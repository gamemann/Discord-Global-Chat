import os
import base64
import time
import aiohttp
import aiohttp

import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from discord import Webhook, AsyncWebhookAdapter
from discord.errors import NotFound

import db

bot = commands.Bot(command_prefix='!')
channels = {}
webhooks = {}

def connect(cfg, conn):
    # Enable intents.
    intents = discord.Intents.default()
    intents.members = True 
    
    # Get connection cursor.
    cur = conn.cursor()
    
    @bot.event
    async def on_ready():
        print("Successfully connected to Discord.")
        await updateinfo()

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

        newchannels = [chnlid]
        cur = conn.cursor()

        # Retrieve current channel list if any.
        cur.execute("SELECT `channelid` FROM `channels` WHERE `guildid`=?", [ctx.guild.id])
        conn.commit()

        exist = cur.fetchone()

        if exist is not None and len(exist) > 0:
            cur.execute("UPDATE `channels` SET `channelid`=? WHERE `guildid`=?", (chnlid, ctx.guild.id))
            conn.commit()
        else:
            cur.execute("INSERT INTO `channels` (`guildid`, `channelid`, `webhookurl`) VALUES (?, ?, '')", (ctx.guild.id, chnlid))
            conn.commit()

        await updateinfo()

        await ctx.channel.send("Successfully linked channel!", delete_after=cfg['BotMsgStayTime'])

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
            await ctx.channel.send("**Error** - Could not find channel with ID **" + chnlid + "** in current Discord guild. However, deleting from database anyways.", delete_after=cfg['BotMsgStayTime'])

        cur = conn.cursor()

        # Retrieve current channel list if any.
        cur.execute("SELECT `channelid` FROM `channels` WHERE `guildid`=?", [ctx.guild.id])
        conn.commit()

        exist = cur.fetchone()

        if exist is None or len(exist) < 1:
            await ctx.channel.send("No results came back for specific guild. Channel must not exist.", delete_after=cfg['BotMsgStayTime'])

            return

        cur.execute("UPDATE `channels` SET `channelid`=0 WHERE `guildid`=?", [ctx.guild.id])
        conn.commit()

        await updateinfo()

        await ctx.channel.send("Successfully unlinked channel!", delete_after=cfg['BotMsgStayTime'])

    @bot.command(name="dgc_updatehook")
    @has_permissions(administrator=True) 
    async def dgc_updatehook(ctx, url=None):
        if url is None:
            ctx.channel.send("**Error** - You're missing the URL argument.", delete_after=cfg['BotMsgStayTime'])
            return
        
        cur = conn.cursor()

        cur.execute("SELECT `webhookurl` FROM `channels` WHERE `guildid`=?", [ctx.guild.id])
        conn.commit()

        row = cur.fetchone()

        if row is None or len(row) < 1:
            # Insert.
            cur.execute("INSERT INTO `channels` (`guildid`, `channelid`, `webhookurl`) VALUES (?, 0, ?)", (ctx.guild.id, url))
            conn.commit()
        else:
            # Update.
            cur.execute("UPDATE `channels` SET `webhookurl`=? WHERE `guildid`=?", (url, ctx.guild.id))
            conn.commit()

        await updateinfo()
        await ctx.channel.send("Successfully updated Web Hook URL if row existed.", delete_after=cfg['BotMsgStayTime'])

    @bot.command(name="dgc_gethook")
    @has_permissions(administrator=True) 
    async def dgc_gethook(ctx):
        cur = conn.cursor()

        cur.execute("SELECT `webhookurl` FROM `channels` WHERE `guildid`=?", [ctx.guild.id])
        conn.commit()

        row = cur.fetchone()

        if row is None or len(row) < 1:
            await ctx.channel.send("Could not retrieve hook.", delete_after=cfg['BotMsgStayTime'])

        await ctx.channel.send("Web hook URL => " + str(row['webhookurl']))

    @bot.event
    async def on_message(msg):
        # Make sure the user isn't the bot or a bot.
        if msg.author.id == bot.user.id or msg.author.bot == True:
            return

        # If this is a webhook, ignore.
        if msg.webhook_id != None:
            return

        chnlid = msg.channel.id

        # Check to see if this is a global channel.
        if channels is None or msg.guild.id not in channels or msg.channel.id != channels[msg.guild.id]:
            await bot.process_commands(msg)

            return

        # Loop through all cached channels.
        for guild, chnl in channels.items():
                # Ignore if this is the current channel.
                if chnl is None or (msg.guild.id == guild and chnl == chnlid):
                    continue

                # Try to fetch the channel by ID.
                try:
                    chnlobj = await bot.fetch_channel(chnl)
                except NotFound:
                    channels[guild].remove(chnl)

                    continue

                # Get guild name.
                guildname = False

                try:
                    guildobj = await bot.fetch_guild(msg.guild.id)
                    guildname = guildobj.name
                except (Forbidden, HTTPException) as e:
                    guildname = False

                msgtosend = msg.content

                ## Append guild name to message.
                if guildname != False and cfg['AppendGuildName']:
                    msgtosend = msgtosend + "\n\n*From " + guildname + "*"

                # Now send to the Discord channel.
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(webhooks[guild], adapter=AsyncWebhookAdapter(session))

                    # Check for mentions.
                    mentions = discord.AllowedMentions(everyone=False, users=False, roles=False, replied_user=False)

                    if cfg['AllowMentions']:
                        mentions = discord.AllowedMentions(everyone=False, users=True, roles=False, replied_user=False)

                    await webhook.send(msgtosend, username=msg.author.display_name, avatar_url=msg.author.avatar_url, allowed_mentions=mentions)

        await bot.process_commands(msg)

    @tasks.loop(seconds=cfg['UpdateTime'])
    async def updateinfo():
        print("Updating channels and web hook URLs...")
        cur = conn.cursor()

        for guild in bot.guilds:
            # Perform SQL query to retrieve all channels for this specific guild.
            cur.execute("SELECT `channelid`, `webhookurl` FROM `channels` WHERE `guildid`=?", [guild.id])
            conn.commit()

            # Reset channels list and web hook URL.
            channels[guild.id] = None
            webhooks[guild.id] = None

            row = cur.fetchone()

            if row is None or len(row) < 1:
                #print("Couldn't fetch guild #" + str(guild.id))
                continue

            # Assign web hook.
            webhooks[guild.id] = row['webhookurl']

            # Assign channel ID.
            channels[guild.id] = row['channelid']

            #print("Updated #" + str(guild.id) + " to:\n\nWeb hook => " + str(webhooks[guild.id]) + "\nChannel ID => " + str(channels[guild.id]) + "\n\n")
            
    bot.run(cfg['BotToken'])