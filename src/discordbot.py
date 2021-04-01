import os
import base64
import time

import discord
from discord.ext import commands, tasks

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

    @bot.command()
    @has_permissions(administrator=True)  
    async def dgc_linkchannel(ctx, id=None):
        chnlid = 0
        chnl = 0

        if id is not None:
            chnlid = id
        else:
            chnlid = ctx.channel.id

        try:
            chnl await bot.fetch_channel(chnlid)
        except NotFound:
            await ctx.channel.send("**Error** - Could not find channel with ID **" + chnlid + "** in current Discord guild.", delete_after=cfg['BotMsgStayTime'])
            return

        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO `channels` (`guildid`, `channelid`) VALUES (?, ?)", (ctx.guild.id, chnlid))
        cur.commit()

        await update_channels()

        await ctx.channel.send("Successfully linked channel!", delete_after=cfg['BotMsgStayTime'])

    @bot.command()
    @has_permissions(administrator=True) 
    async def dcr_unlinkchannel(ctx, name=None):
        chnlid = 0
        chnl = 0

        if id is not None:
            chnlid = id
        else:
            chnlid = ctx.channel.id

        try:
            chnl await bot.fetch_channel(chnlid)
        except NotFound:
            await ctx.channel.send("**Warning** - Could not find channel with ID **" + chnlid + "** in current Discord guild. However, will attempt to delete anyways.", delete_after=cfg['BotMsgStayTime'])

        cur = conn.cursor()
        cur.execute("DELETE FROM `channels` WHERE `guildid`=? AND `channelid`=?", (ctx.guild.id, chnlid))
        cur.commit()

        await update_channels()

        await ctx.channel.send("Successfully unlinked channel!", delete_after=cfg['BotMsgStayTime'])

    @bot.event
    async def on_message(msg):
        if pl.user_id == bot.user.id:
            return

    @tasks.loop(minutes=cfg['UpdateTime'])
    async def update_channels():
        print("Updating channels...")
        cur = conn.cursor()

        for guild in bot.guilds:
            # Perform SQL query to retrieve all channels for this specific guild.
            cur.execute("SELECT `channelid` FROM `channels` WHERE `guildid`=?", [guild.id])
            cur.commit()

            # Reset channels list.
            channels[guild.id] = []

            rows = cur.fetchall()

            for row in rows:
                channels[guild.id].append(row['channelid'])
            
    bot.run(cfg['BotToken'])