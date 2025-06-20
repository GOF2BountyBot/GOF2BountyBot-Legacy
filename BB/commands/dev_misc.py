import discord
import traceback
from datetime import datetime, timezone

from . import commandsDB as bbCommands
from .. import bbGlobals, lib

from . import util_help

# used in nested f-strings
NL = "\n"

async def dev_cmd_dev_help(message : discord.Message, args : str, isDM : bool):
    """dev command printing help strings for dev commands as defined in bbData

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    await util_help.util_autohelp(message, args, isDM, 2)

bbCommands.register("dev-help", dev_cmd_dev_help, 2, signatureStr="**dev-help** *[page number, section or command]*", shortHelp="Display information about developer-only commands.\nGive a specific command for detailed info about it, or give a page number or give a section name for brief info.", longHelp="Display information about developer-only commands.\nGive a specific command for detailed info about it, or give a page number or give a section name for brief info about a set of commands. These are the currently valid section names:\n- Bounties\n- Miscellaneous\n- Items\n- Channels\n- Skins")


async def trySave(message : discord.Message) -> bool:
    """Try to save dbs, and send an error to the caller's DMs if it fails.
    Returns `True` on success, `False` on failure."""
    try:
        bbGlobals.client.bb_saveAllDBs()
        print(datetime.now(timezone.utc).strftime("%H:%M:%S: Data saved manually!"))
        return True
    except Exception as e:
        print("SAVING ERROR", e.__class__.__name__)
        print(traceback.format_exc())
        if message.author.dm_channel is None:
            await message.author.create_dm()
        if message.author.dm_channel is None:
            sendChannel = message.channel
        else:
            sendChannel = message.author.dm_channel

        try:
            await sendChannel.send(f"failed to save with {type(e).__name__}: {e}\n{traceback.format_exc()}")
        except discord.Forbidden:
            await message.channel.send(":x: I can't DM you, " + message.author.display_name + "! Please enable DMs from users who are not friends.")
    return False


async def getShutdownWarnings(message : discord.Message) -> str:
    warnings = []

    saved = await trySave(message)
    if not saved:
        warnings.append(f"failed to save (last successful save <t:{int(bbGlobals.lastSuccessfulSave.timestamp())}:f>)")

    if len(bbGlobals.currentRenders) > 0:
        warnings.append("a render is currently in progress")
    
    return "" if len(warnings) == 0 else warnings[0] if len(warnings) == 1 else (" - " + "\n - ".join(warnings))


async def dev_cmd_sleep(message : discord.Message, args : str, isDM : bool):
    """developer command saving all data to JSON and then shutting down the bot

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    warn = await getShutdownWarnings(message)
    if warn and "-f" not in args:
        await message.channel.send(f":x: {f'{NL}{warn}' if NL in warn else warn}. Give `-f` to force.")	
    else:
        bbGlobals.shutdown = bbGlobals.ShutDownState.shutdown
        await message.channel.send(f"{warn}. `-f` given, shutting down anyway.\nzzzz....")
        await bbGlobals.client.bb_shutdown()

bbCommands.register("bot-sleep", dev_cmd_sleep, 2, allowDM=True, useDoc=True)


async def dev_cmd_save(message : discord.Message, args : str, isDM : bool):
    """developer command saving all databases to JSON

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if await trySave(message):
        await message.channel.send("saved!")

bbCommands.register("save", dev_cmd_save, 2, allowDM=True, useDoc=True)


async def dev_cmd_restart(message: discord.Message, args: str, isDM: bool):
    """developer command saving all data to JSON and then restarting the bot

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    warn = await getShutdownWarnings(message)
    if warn and "-f" not in args:
        await message.channel.send(f":x: {f'{NL}{warn}' if NL in warn else warn}. Give `-f` to force.")	
    else:
        bbGlobals.shutdown = bbGlobals.ShutDownState.restart
        await message.channel.send(f"{warn}. `-f` given, restarting anyway.\nzzzz....")
        await bbGlobals.client.bb_shutdown()

bbCommands.register("bot-restart", dev_cmd_restart, 2, allowDM=True, useDoc=True)


async def dev_cmd_bot_update(message : discord.Message, args : str, isDM : bool):
    """developer command that gracefully shuts down the bot, performs git pull, and then reboots the bot.

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    warn = await getShutdownWarnings(message)
    if warn and "-f" not in args:
        await message.channel.send(f":x: {f'{NL}{warn}' if NL in warn else warn}. Give `-f` to force.")	
    else:
        bbGlobals.shutdown = bbGlobals.ShutDownState.update
        await message.channel.send(f"{warn}. `-f` given, updating and restarting anyway.\nzzzz....")
        await bbGlobals.client.bb_shutdown()

bbCommands.register("bot-update", dev_cmd_bot_update, 2, allowDM=True, useDoc=True)


async def dev_cmd_reset_has_poll(message : discord.Message, args : str, isDM : bool):
    """developer command resetting the poll ownership of the calling user, or the specified user if one is given.

    :param discord.Message message: the discord message calling the command
    :param str args: string, can be empty or contain a user mention
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # reset the calling user's cooldown if no user is specified
    if args == "":
        bbGlobals.usersDB.getUser(
            message.author.id).pollOwned = False
        # otherwise get the specified user's discord object and reset their cooldown.
        # [!] no validation is done.
    else:
        bbGlobals.usersDB.getUser(int(args.lstrip("<@!").rstrip(">"))).pollOwned = False
    await message.channel.send("Done!")

bbCommands.register("reset-has-poll", dev_cmd_reset_has_poll, 2, allowDM=True, useDoc=True)


async def dev_cmd_broadcast(message : discord.Message, args : str, isDM : bool):
    """developer command sending a message to the playChannel of all guilds that have one

    :param discord.Message message: the discord message calling the command
    :param str args: string containing the message to broadcast
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if args == "":
        await message.channel.send("provide a message!")
    else:
        useAnnounceChannel = False
        broadcastEmbed = None
        msg = args
        if args.split(" ")[0].lower() == "announce-channel":
            useAnnounceChannel = True
            msg = args[17:]

        try:
            embedIndex = msg.index("embed=")
        except ValueError:
            embedIndex = -1

        if embedIndex != -1:
            msgText = msg[:embedIndex]
        else:
            msgText = msg

        if embedIndex != -1:
            msg = msg[embedIndex+len("embed="):]
            titleTxt = ""
            desc = ""
            footerTxt = ""
            thumb = ""
            img = ""
            authorName = ""
            icon = ""

            try:
                startIndex = msg.index("titleTxt='")+len("titleTxt=")+1
                endIndex = startIndex + \
                    msg[msg.index("titleTxt='")+len("titleTxt='"):].index("'")
                titleTxt = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("desc='")+len("desc=")+1
                endIndex = startIndex + \
                    msg[msg.index("desc='")+len("desc='"):].index("'")
                desc = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("footerTxt='")+len("footerTxt=")+1
                endIndex = startIndex + \
                    msg[msg.index("footerTxt='") +
                        len("footerTxt='"):].index("'")
                footerTxt = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("thumb='")+len("thumb=")+1
                endIndex = startIndex + \
                    msg[msg.index("thumb='")+len("thumb='"):].index("'")
                thumb = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("img='")+len("img=")+1
                endIndex = startIndex + \
                    msg[msg.index("img='")+len("img='"):].index("'")
                img = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("authorName='")+len("authorName=")+1
                endIndex = startIndex + \
                    msg[msg.index("authorName='") +
                        len("authorName='"):].index("'")
                authorName = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("icon='")+len("icon=")+1
                endIndex = startIndex + \
                    msg[msg.index("icon='")+len("icon='"):].index("'")
                icon = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            broadcastEmbed = lib.discordUtil.makeEmbed(titleTxt=titleTxt, desc=desc, footerTxt=footerTxt,
                                       thumb=thumb, img=img, authorName=authorName, icon=icon)

            try:
                msg.index('\n')
                fieldsExist = True
            except ValueError:
                fieldsExist = False
            while fieldsExist:
                nextNL = msg.index('\n')
                try:
                    closingNL = nextNL + msg[nextNL+1:].index('\n')
                except ValueError:
                    fieldsExist = False
                else:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace(
                        "{NL}", "\n"), value=msg[nextNL+1:closingNL+1].replace("{NL}", "\n"), inline=False)
                    msg = msg[closingNL+2:]

                if not fieldsExist:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace(
                        "{NL}", "\n"), value=msg[nextNL+1:].replace("{NL}", "\n"), inline=False)

        if useAnnounceChannel:
            for guild in bbGlobals.guildsDB.guilds.values():
                if guild.hasAnnounceChannel():
                    await guild.getAnnounceChannel().send(msgText, embed=broadcastEmbed)
        else:
            for guild in bbGlobals.guildsDB.guilds.values():
                if guild.hasPlayChannel():
                    await guild.getPlayChannel().send(msgText, embed=broadcastEmbed)

bbCommands.register("broadcast", dev_cmd_broadcast, 2, forceKeepArgsCasing=True, allowDM=True, useDoc=True)


async def dev_cmd_say(message : discord.Message, args : str, isDM : bool):
    """developer command sending a message to the same channel as the command is called in

    :param discord.Message message: the discord message calling the command
    :param str args: string containing the message to broadcast
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if args == "":
        await message.channel.send("provide a message!")
    else:
        useAnnounceChannel = False
        broadcastEmbed = None
        msg = args
        if args.split(" ")[0].lower() == "announce-channel":
            useAnnounceChannel = True
            msg = args[17:]

        try:
            embedIndex = msg.index("embed=")
        except ValueError:
            embedIndex = -1

        if embedIndex != -1:
            msgText = msg[:embedIndex]
        else:
            msgText = msg

        if embedIndex != -1:
            msg = msg[embedIndex+len("embed="):]
            titleTxt = ""
            desc = ""
            footerTxt = ""
            thumb = ""
            img = ""
            authorName = ""
            icon = ""

            try:
                startIndex = msg.index("titleTxt='")+len("titleTxt=")+1
                endIndex = startIndex + \
                    msg[msg.index("titleTxt='")+len("titleTxt='"):].index("'")
                titleTxt = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("desc='")+len("desc=")+1
                endIndex = startIndex + \
                    msg[msg.index("desc='")+len("desc='"):].index("'")
                desc = msg[startIndex:endIndex].replace("{NL}", "\n")
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("footerTxt='")+len("footerTxt=")+1
                endIndex = startIndex + \
                    msg[msg.index("footerTxt='") +
                        len("footerTxt='"):].index("'")
                footerTxt = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("thumb='")+len("thumb=")+1
                endIndex = startIndex + \
                    msg[msg.index("thumb='")+len("thumb='"):].index("'")
                thumb = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("img='")+len("img=")+1
                endIndex = startIndex + \
                    msg[msg.index("img='")+len("img='"):].index("'")
                img = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("authorName='")+len("authorName=")+1
                endIndex = startIndex + \
                    msg[msg.index("authorName='") +
                        len("authorName='"):].index("'")
                authorName = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("icon='")+len("icon=")+1
                endIndex = startIndex + \
                    msg[msg.index("icon='")+len("icon='"):].index("'")
                icon = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            broadcastEmbed = lib.discordUtil.makeEmbed(titleTxt=titleTxt, desc=desc, footerTxt=footerTxt,
                                       thumb=thumb, img=img, authorName=authorName, icon=icon)

            try:
                msg.index('\n')
                fieldsExist = True
            except ValueError:
                fieldsExist = False
            while fieldsExist:
                nextNL = msg.index('\n')
                try:
                    closingNL = nextNL + msg[nextNL+1:].index('\n')
                except ValueError:
                    fieldsExist = False
                else:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace(
                        "{NL}", "\n"), value=msg[nextNL+1:closingNL+1].replace("{NL}", "\n"), inline=False)
                    msg = msg[closingNL+2:]
                
                if not fieldsExist:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace(
                        "{NL}", "\n"), value=msg[nextNL+1:].replace("{NL}", "\n"), inline=False)

        await message.channel.send(msgText, embed=broadcastEmbed)

bbCommands.register("say", dev_cmd_say, 2, forceKeepArgsCasing=True, allowDM=True, useDoc=True)


async def dev_cmd_setbalance(message : discord.Message, args : str, isDM : bool):
    """developer command setting the requested user's balance.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a user mention and an integer number of credits
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    # verify both a user and a balance were given
    if len(argsSplit) < 2:
        await message.channel.send(":x: Please give a user mention followed by the new balance!")
        return
    # verify the requested balance is an integer
    if not lib.stringTyping.isInt(argsSplit[1]):
        await message.channel.send(":x: that's not a number!")
        return
    # verify the requested user
    requestedUser = bbGlobals.client.get_user(
        int(argsSplit[0].lstrip("<@!").rstrip(">")))
    if requestedUser is None:
        await message.channel.send(":x: invalid user!!")
        return
    if not bbGlobals.usersDB.userIDExists(requestedUser.id):
        requestedBBUser = bbGlobals.usersDB.addUser(requestedUser.id)
    else:
        requestedBBUser = bbGlobals.usersDB.getUser(requestedUser.id)
    # update the balance
    requestedBBUser.credits = int(argsSplit[1])
    await message.channel.send("Done!")

bbCommands.register("setbalance", dev_cmd_setbalance, 2, allowDM=True, useDoc=True)


async def dev_cmd_reset_transfer_cool(message : discord.Message, args : str, isDM : bool):
    """developer command resetting a user's home guild transfer cooldown.

    :param discord.Message message: the discord message calling the command
    :param str args: either empty string or string containing a user mention or ID
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # reset the calling user's cooldown if no user is specified
    if args == "":
        bbGlobals.usersDB.getUser(
            message.author.id).guildTransferCooldownEnd = datetime.now(timezone.utc)
    # otherwise get the specified user's discord object and reset their cooldown.
    # [!] no validation is done.
    else:
        bbGlobals.usersDB.getUser(int(args.lstrip("<@!").rstrip(">"))
                        ).guildTransferCooldownEnd = datetime.now(timezone.utc)
    await message.channel.send("Done!")
    

bbCommands.register("reset-transfer-cool", dev_cmd_reset_transfer_cool, 2, allowDM=True, useDoc=True)