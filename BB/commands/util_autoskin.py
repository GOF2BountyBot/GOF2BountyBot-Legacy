from io import BytesIO
from typing import Optional, Tuple, cast
import discord
from datetime import timedelta
import os
from PIL import Image
import asyncio

from ..bbConfig import bbConfig, bbData
from .. import lib, bbGlobals, logging
from ..lib.stringTyping import truncateWithEllipse
from ..reactionMenus import ReactionSkinRegionPicker, ReactionMenu
from ..bbObjects.items import bbShip
from ..shipRenderer import shipRenderer
from ..reactionMenus.ReactionMenu import DummySingleUserReactionMenu

CWD = os.getcwd()
robotIcon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/259/robot_1f916.png"


def checkImageAspectRatio(skinFile: discord.Attachment, skinPath: str) -> bool:
    """Check whether an image is of the correct aspect ratio.
    If it is, it will be scaled to 2048x, and `True` returned.
    If it is not, nothing will happen, and `False` will be returned.
    It is intended that in this case, you follow up with `fixImageAspectRatio`.

    :param skinFile: Attachment referencing the image
    :type skinFile: discord.Attachment
    :param skinPath: Path to the image on disc
    :type skinPath: str
    :return: `True` if the image is now 2048x, `False` if the aspect ratio is incorrect and must be correct some other way
    :rtype: bool
    """
    if skinFile.width != 2048 or skinFile.height != 2048:
        if abs(1 - (skinFile.width / skinFile.height)) < bbConfig.aspectRatioTolerance:
            workingSF = Image.open(skinPath)
            workingSF = workingSF.resize((2048, 2048))
            workingSF.save(skinPath)
            workingSF.close()
            return True
        return False
    return True


async def fixImageAspectRatio(skinPath: str, message: discord.Message, itemName: str, renderReserved: bool,
                                menuMsg: discord.Message = None) -> Tuple[bool, discord.Message]:
    """Given a path to an image that is not square, as the user whether they would like it to be cropped or
    stretched to become square, and perform the correction.
    The user can also cancel the operation entirely. This will result in the image at `skinPath` being removed
    from disc, and the reservation in `bbGlobals.currentRenders` being removed. If cancelled, the function will return `True`.
    Alongside the `bool` result, the `Message` used for reaction menus is also returned for reuse in other menus.

    :param skinFile: Attachment referencing the incorrect image
    :type skinFile: discord.Attachment
    :param skinPath: Path to the image on disc
    :type skinPath: str
    :param message: Message that contained the image
    :type message: discord.Message
    :param itemName: Name of the ship to be skinned
    :type itemName: str
    :param renderReserved: Whether the ship has already been reserved in bbGlobals.currentRenders
    :type renderReserved: bool
    :return: True if the operation was cancelled by the user, False if it succeeded to completion, followed by
            the message used for reaction menus
    :rtype: Tuple[bool, discord.Message]
    """
    if menuMsg is None:
        menuMsg = await message.reply("** **", mention_author=False)

    menuOptions = {
        bbConfig.cropEmoji: "Crop",
        bbConfig.stretchEmoji: "Stretch",
        bbConfig.defaultCancelEmoji: "Cancel"
    }

    actionMenu = DummySingleUserReactionMenu(menuMsg, message.author,
                                                timedelta(**bbConfig.timeouts.selectImageSizeHandling),
                                                menuOptions,
                                                menuOptions.keys(),
                                                desc="Your image is not square, should I crop it or stretch it?"
                                            )
    action = await actionMenu.doMenu()
    if not action or action[0] == bbConfig.defaultCancelEmoji:
        if renderReserved:
            bbGlobals.currentRenders.remove(itemName)
        os.remove(skinPath)
        await message.reply("🛑 Render cancelled.")
        return True, menuMsg

    workingSF = Image.open(skinPath)
    
    if action[0] == bbConfig.cropEmoji:
        workingSF = lib.graphics.cropAndScale(workingSF, 2048, 2048)
    else:
        workingSF = workingSF.resize((2048, 2048))

    workingSF.save(skinPath)
    workingSF.close()
    return False, menuMsg


async def collectAutoskinArgs(message: discord.Message, userShipName: str, res_x : int, res_y : int, numSamples: int,
                                full: bool = False) -> Optional[Tuple[str, shipRenderer.AutoskinArgs]]:
    """Collect a usable AutoskinArgs object to pass to the ship renderer

    :param message: The message that triggered the operation
    :type message: discord.Message
    :param userShipName: The user-provided ship name to look up
    :type userShipName: str
    :param res_x: width of the render
    :type res_x: int
    :param res_y: height of the render
    :type res_y: int
    :param numSamples: Number of samples of the render
    :type numSamples: int
    :param full: Whether to trigger autoskin at all, or just render the given texture (Default False)
    :type full: bool, optional
    :return: The collected parameter values, or None if an error occurred
    :rtype: Optional[shipRenderer.AutoskinArgs]
    """
    prefix = bbConfig.commandPrefix

    # look up the ship data
    try:
        shipData = bbData.findShipDataByAlias(userShipName)
    except KeyError:
        # report unrecognised ship names
        await message.reply(mention_author=False,
                            content=f":x: **{truncateWithEllipse(userShipName, 20, 15)}** is not in my database! :detective:")
        return None

    itemName = shipData["name"]

    if not shipData["skinnable"]:
        await message.reply(mention_author=False, content=":x: That ship is not skinnable!")
        return None

    if len(bbGlobals.currentRenders) >= bbConfig.maxConcurrentRenders:
        await message.reply(mention_author=False,
                            content=":x: My rendering queue is full currently. Please try this command again once someone " \
                                    + "else's render has completed.")
        return None
    if itemName in bbGlobals.currentRenders:
        await message.reply(mention_author=False,
                            content=":x: Someone else is currently rendering this ship! Please use this command again " \
                                    + f"once my other {itemName} render has completed.")
        return None

    if not message.attachments:
        await message.reply(mention_author=False, content=":x: Please attach an image to use as your base texture.")
        return None

    bbGlobals.currentRenders.append(itemName)
    skinPaths = {}

    async def downloadImage(skinPaths, skinFile, key) -> bool:
        if not skinFile.content_type.startswith("image"):
            await message.reply(f":x: Please only attach images! That's a `{skinFile.content_type}`.\n" \
                                + "🛑 Render cancelled.")
            for skinPath in skinPaths.values():
                try:
                    os.remove(skinPath)
                except FileNotFoundError:
                    pass
            bbGlobals.currentRenders.remove(itemName)
            return False
            
        texBytes = BytesIO()

        try:
            await skinFile.save(texBytes)
        except (discord.NotFound, discord.HTTPException):
            await message.reply(mention_author=False,
                                content=":x: I couldn't download your image. Did you delete it?")
            for skinPath in skinPaths.values():
                try:
                    os.remove(skinPath)
                except FileNotFoundError:
                    pass
            bbGlobals.currentRenders.remove(itemName)
            texBytes.close()
            return False

        texBytes.seek(0)
        baseTex = Image.open(texBytes)
        if baseTex.mode == "RGBA":
            ext = "png"
        else:
            baseTex = baseTex.convert("RGB")
            ext = "jpg"
        skinPaths[key] = os.path.join(CWD, bbConfig.tempRendersDir, f"{message.id}_{key}.{ext}")
        baseTex.save(skinPaths[key])
        baseTex.close()
        texBytes.close()
        return True

    skinFile = message.attachments[0]
    result = await downloadImage(skinPaths, skinFile, 0)
    if not result:
        return None

    menuMsg = None

    correctShape = checkImageAspectRatio(skinFile, skinPaths[0])
    if not correctShape:
        cancelled, menuMsg = await fixImageAspectRatio(skinPaths[0], message, itemName, True, menuMsg)
        if cancelled:
            return None

    disabledLayers = []

    if shipData["textureRegions"] > 0 and not full:
        layerIndices = [i for i in range(1, shipData["textureRegions"] + 1)]

        if menuMsg is None:
            menuMsg = await message.reply(mention_author=False, content="** **")
        layersPickerMenu = ReactionSkinRegionPicker.ReactionSkinRegionPicker(menuMsg, message.author,
                                                                                bbConfig.toolUseConfirmTimeoutSeconds,
                                                                                numRegions=shipData["textureRegions"])
        pickedLayers = []
        menuOutput = await layersPickerMenu.doMenu()
        # Menu expired
        if not menuOutput:
            for skinPath in skinPaths.values():
                os.remove(skinPath)
            bbGlobals.currentRenders.remove(itemName)
            return None

        if bbConfig.spiralEmoji in menuOutput:
            pickedLayers = layerIndices
        elif bbConfig.defaultCancelEmoji in menuOutput:
            await menuMsg.edit(mention_author=False, content="🛑 Skin render cancelled.", embed=None)
            for skinPath in skinPaths.values():
                os.remove(skinPath)
            bbGlobals.currentRenders.remove(itemName)
            return None
        else:
            for react in menuOutput:
                try:
                    pickedLayers.append(bbConfig.numberEmojis.index(react))
                except ValueError:
                    pass

        remainingIndices = [i for i in layerIndices if i not in pickedLayers]

        if remainingIndices:
            disableHelpMsg = "Would you like to disable any regions?\n\n" \
                            + "Disabled regions will appear with your provided base texture."
            disabledLayersPickerMenu = ReactionSkinRegionPicker.ReactionSkinRegionPicker(menuMsg, message.author,
                                                                                            bbConfig.toolUseConfirmTimeoutSeconds,
                                                                                            possibleRegions=remainingIndices,
                                                                                            desc=disableHelpMsg)
            menuOutput = await disabledLayersPickerMenu.doMenu()
            # Menu expired
            if not menuOutput:
                for skinPath in skinPaths.values():
                    os.remove(skinPath)
                bbGlobals.currentRenders.remove(itemName)
                return None
                
            if bbConfig.spiralEmoji in menuOutput:
                disabledLayers = remainingIndices
            elif bbConfig.defaultCancelEmoji in menuOutput:
                await menuMsg.reply(mention_author=False, content="🛑 Skin render cancelled.")
                for skinPath in skinPaths.values():
                    os.remove(skinPath)
                bbGlobals.currentRenders.remove(itemName)
                return None
            else:
                for react in menuOutput:
                    try:
                        disabledLayers.append(bbConfig.numberEmojis.index(react))
                    except ValueError:
                        pass

        def showmeAdditionalMessageCheck(newMessage):
            return newMessage.author is message.author and \
                    (newMessage.content.lower().startswith(f"{prefix}cancel") or len(newMessage.attachments) > 0)

        for regionNum in pickedLayers:
            nextLayerMsg = await message.reply(mention_author=False,
                                                content=f"Please send your image for texture region #{regionNum}" \
                                                        + f", or `{prefix}cancel` to cancel the render, within " \
                                                        + f"{bbConfig.toolUseConfirmTimeoutSeconds} seconds.")
            try:
                imgMsg = await bbGlobals.client.wait_for("message", check=showmeAdditionalMessageCheck,
                                                        timeout=bbConfig.toolUseConfirmTimeoutSeconds)
            except asyncio.TimeoutError:
                await nextLayerMsg.edit(content="This menu has now expired. Please try the command again.")
                return None
            else:
                if imgMsg.content.lower().startswith(f"{prefix}cancel"):
                    await nextLayerMsg.edit(mention_author=False, content="🛑 Skin render cancelled.")
                    for skinPath in skinPaths.values():
                        os.remove(skinPath)
                    bbGlobals.currentRenders.remove(itemName)
                    return None

                nextLayer = imgMsg.attachments[0]
                result = await downloadImage(skinPaths, nextLayer, regionNum)
                if not result:
                    return None

                correctShape = checkImageAspectRatio(nextLayer, skinPaths[regionNum])
                if not correctShape:
                    cancelled, _ = await fixImageAspectRatio(skinPaths[regionNum], message, itemName, True)
                    if cancelled:
                        return None
    
    return itemName, shipRenderer.AutoskinArgs(str(message.id), shipData["path"], shipData["model"], skinPaths,
                                                disabledLayers, res_x, res_y, numSamples, full=full)


async def doAutoSkin(message: discord.Message, rendererArgs: shipRenderer.AutoskinArgs, shipName: str,
                    renderIdentifierPrefix: str = ""):
    """Call shipRenderer following a render command.

    :param message: The message that triggered the render
    :type message: discord.Message
    :param rendererArgs: The parameters to pass to the renderer
    :type rendererArgs: shipRenderer.AutoskinArgs
    :param renderIdentifierPrefix: Prefix for the render ID, which will be posted to the renders channel (Default ")
    :type renderIdentifierPrefix: str, optional
    """
    waitMsg = await message.reply(mention_author=False, content="🤖 Render started! I'll ping you when I'm done.")

    renderPath = os.path.join(rendererArgs.shipPath, "skins", f"{message.id}-RENDER.png")
    outSkinPath = os.path.join(rendererArgs.shipPath, "skins", f"{message.id}.jpg")

    guildStr = "DM" if message.guild is None else str(message.guild.id)
    renderIdentifier = f"{renderIdentifierPrefix}{'-' if renderIdentifierPrefix else ''}" \
                        + f"u{message.author.id}g{guildStr}c{message.channel.id}m{message.id}sh{shipName}"

    await lib.discordUtil.startLongProcess(waitMsg)
    try:
        await shipRenderer.renderShip(**rendererArgs)
    except shipRenderer.RenderFailed:
        await message.reply("🥺 Render failed! The error has been logged, please try a different ship.",
                            mention_author=True)
        logging.bbLogger.log("Main", "admin_cmd_showmeHD", f"Ship render failed. Identifer: {renderIdentifier}")
    else:
        rendersChannel = bbGlobals.client.get_channel(bbConfig.showmeSkinRendersChannel)
        
        with open(renderPath, "rb") as f:
            imageEmbedMsg = await rendersChannel.send(renderIdentifier, file=discord.File(f))
            renderEmbed = lib.discordUtil.makeEmbed(col=discord.Colour.random(),
                                                    img=imageEmbedMsg.attachments[0].url,
                                                    authorName="Skin Render Complete!",
                                                    icon=robotIcon,
                                                    footerTxt=f"Custom skinned {shipName.capitalize()}")
            await message.reply(embed=renderEmbed, mention_author=True)

    bbGlobals.currentRenders.remove(shipName)

    try:
        os.remove(renderPath)
    except FileNotFoundError:
        pass

    for skinPath in rendererArgs.textures.values():
        os.remove(skinPath)

    try:
        os.remove(outSkinPath)
    except FileNotFoundError:
        pass

    await lib.discordUtil.endLongProcess(waitMsg)
