# Discord Global Chat
## Description
A Discord bot that allows for global chat between Discord servers in certain channels. Used for the Unnamed Discord community brand.

## Requirements
The Discord.py [package](https://pypi.org/project/discord.py/) is required in order to use this bot. You may install this via the following command.

```
python3 -m pip install -U discord.py
```

## Command Line Usage
You may specify the settings JSON (used for the bot token, etc) and the SQLite DB location within the command line. The default settings location is `/etc/dgc/settings.json` and the default SQLite DB location is `/etc/dgc/dgc.db`.

The following are examples of how to set these in the program.

```
python3 src/main.py cfg=/home/cdeacon/settings.json sqlite=/home/cdeacon/dgc.db
```

## Config
The config file is in JSON format and the following keys are supported.

* **BotToken** - The Discord bot token. Please retrieve this from the Discord Developers page for your bot.
* **BotMsgStayTime** - When the bot replies to a command in a text channel, delete the bot message this many seconds after (default - **10.0** seconds).
* **UpdateTime** - How often to update the channel and web hook URL cache in seconds (default - **60.0** seconds).

## Bot Commands
The command prefix is `!`. You must execute these commands inside of a text channel of the guild you want to modify. You must also be an administrator in order to use these commands.

### dgc_linkchannel
```
!dgc_linkchannel <channel ID>
```

Adds a channel to the linked global chat. If the channel ID is left blank, it will choose the channel the message was sent in.

### dgc_unlinkchannel
```
!dgc_unlinkchannel <channel ID>
```

Unlinks a channel to the linked global chat.

### dgc_updatehook
```
!dgc_updatehook <webhook URL>
```

Updates the web hook that messages send to within the current guild. This must be pointed towards the correct channel ID set with `dgc_linkchannel`.

## Installing
You may use `make install` within this directory to create the `/etc/dgc/` directory and copy `settings.json.example` to `/etc/dgc/settings.json`. Please configure the `settings.json` file to your needs.

Other than that, the needed SQLite tables are created if they don't exist when the Python program is started. However, if need to be, here is the current table structure.

```SQL
CREATE TABLE IF NOT EXISTS `channels` (guildid integer PRIMARY KEY, channelid integer, webhookurl text)
```

## Starting
As of right now, you'll want to use `python3` against the `src/main.py` file. Something like the following should work.

```bash
python3 src/main.py
```

If there's a better way to handle this, please let me know.

## Credits
* [Christian Deacon](https://github.com/gamemann)