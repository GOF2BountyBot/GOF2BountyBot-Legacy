import discord

from . import commandsDB as bbCommands
from .. import lib, bbGlobals
from ..bbConfig import bbConfig
from ..reactionMenus import ReactionMenu, DataPrivacyReactionMenu
from ..scheduling import TimedTask


bbCommands.addHelpSection(0, "data privacy")


async def cmd_dataPrivacy(message : discord.Message, args : str, isDM : bool):
    if message.author.dm_channel is None:
        await message.author.create_dm()
    if message.author.dm_channel is None:
        sendChannel = message.channel
    else:
        sendChannel = message.author.dm_channel

    try:
        menuMsg = await sendChannel.send("‎")
    except discord.Forbidden:
        await message.channel.send(":x: I can't DM you, " + message.author.display_name + "! Please enable DMs from users who are not friends.")
        return

    helpTT = TimedTask.TimedTask(expiryDelta=lib.timeUtil.timeDeltaFromDict(bbConfig.helpEmbedTimeout), expiryFunction=ReactionMenu.markExpiredMenuAndRemoveOptions, expiryFunctionArgs=menuMsg.id)
    bbGlobals.reactionMenusTTDB.scheduleTask(helpTT)
    helpMenu = DataPrivacyReactionMenu.DataPrivacyReactionMenu(
        menuMsg,
        message.author.id,
        timeout=helpTT,
        titleTxt="Export User Data",
        desc="This menu will export all data that is currently stored about you, to a machine-readable format.",
        thumb=bbGlobals.client.user.avatar_url_as(size=64),
        footerTxt="This menu will expire in " + lib.timeUtil.td_format_noYM(helpTT.expiryDelta) + ".")
    await helpMenu.updateMessage()
    bbGlobals.reactionMenusDB[menuMsg.id] = helpMenu

bbCommands.register("my-data", cmd_dataPrivacy, 0, allowDM=True, helpSection="data privacy",
                    signatureStr="**my-data**",
                    shortHelp="Export all data stored about you, in a machine readable format.",
                    longHelp="Exports all data currently stored about you.\n" +
                        "The data export only contains your data, any data relating to other users is anonymized.\n" +
                        "This is the real save data stored by bountybot, and can be read and analysed as the classes " +
                        "found in the BountyBot source code (see `$COMMANDPREFIX$source`).")