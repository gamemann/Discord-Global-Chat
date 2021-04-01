import os
import base64
import time

import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions

import db

bot = commands.Bot(command_prefix='!')
channels = {}

def connect(cfg, conn):
    # Enable intents.
    intents = discord.Intents.default()
    intents.members = True 
    
    # Get connection cursor.
    cur = conn.cursor()

    @bot.event
    async def on_ready():
        print("Successfully connected to Discord.")
        await update_channels()

    @bot.command(name="dgc_linkchannel")
    @has_permissions(administrator=True)  
    async def dgc_linkchannel(ctx, id=None):
        chnlid = 0
        chnl = 0

        if id is not None:
            chnlid = id
        else:
            chnlid = ctx.channel.id

        try:
            chnl = await bot.fetch_channel(chnlid)
        except NotFound:
            await ctx.channel.send("**Error** - Could not find channel with ID **" + chnlid + "** in current Discord guild.", delete_after=cfg['BotMsgStayTime'])
            return

        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO `channels` (`guildid`, `channelid`) VALUES (?, ?)", (ctx.guild.id, chnlid))
        conn.commit()

        await update_channels()

        await ctx.channel.send("Successfully linked channel!", delete_after=cfg['BotMsgStayTime'])

    @dgc_linkchannel.error
    async def dgc_linkchannel_error(ctx, error):
        await ctx.send("Error with cmd => " + error, delete_after=cfg['BotMsgStayTime'])

    @bot.command(name="dgc_unlinkchannel")
    @has_permissions(administrator=True) 
    async def dgc_unlinkchannel(ctx, name=None):
        chnlid = 0
        chnl = 0

        if id is not None:
            chnlid = id
        else:
            chnlid = ctx.channel.id

        try:
            chnl = await bot.fetch_channel(chnlid)
        except NotFound:
            await ctx.channel.send("**Warning** - Could not find channel with ID **" + chnlid + "** in current Discord guild. However, will attempt to delete anyways.", delete_after=cfg['BotMsgStayTime'])

        cur = conn.cursor()
        cur.execute("DELETE FROM `channels` WHERE `guildid`=? AND `channelid`=?", (ctx.guild.id, chnlid))
        conn.commit()

        await update_channels()

        await ctx.channel.send("Successfully unlinked channel!", delete_after=cfg['BotMsgStayTime'])

    @bot.event
    async def on_message(msg):
        # Make sure the user isn't the bot.
        if msg.author.id == bot.user.id:
            return

        chnlid = msg.channel.id

        # Check to see if this is a global channel.
        if channels is None or msg.guild.id not in channels or chnlid not in channels[msg.guild.id]:
            await bot.process_commands(msg)
            return

        # Loop through all cached channels.
        for guild, channellist in channels.items():
            for chnl in channellist:
                # Ignore if this is the current channel.
                if msg.guild.id == guild and chnl == chnlid:
                    continue

                # Try to fetch the channel by ID.
                try:
                    chnlobj = await bot.fetch_channel(chnl)
                except NotFound:
                    print("Channel #" + chnl + " under guild #" + guild + " not found. Removing from list.\n")
                    channels[guild].remove(chnl)
                    continue

                # Now send to the Discord channel.
                await chnlobj.send(content=msg.content)

        await bot.process_commands(msg)

    @tasks.loop(minutes=cfg['UpdateTime'])
    async def update_channels():
        print("Updating channels...")
        cur = conn.cursor()

        for guild in bot.guilds:
            # Perform SQL query to retrieve all channels for this specific guild.
            cur.execute("SELECT `channelid` FROM `channels` WHERE `guildid`=?", [guild.id])
            conn.commit()

            # Reset channels list.
            channels[guild.id] = []

            rows = cur.fetchall()

            for row in rows:
                channels[guild.id].append(row['channelid'])
            
    bot.run(cfg['BotToken'])