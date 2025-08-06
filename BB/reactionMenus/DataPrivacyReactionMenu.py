from __future__ import annotations
import json
from discord.member import Member
from . import ReactionMenu
from ..bbConfig import bbConfig
from .. import bbGlobals, lib
from discord import Colour, NotFound, HTTPException, Forbidden, Guild, Role, Message, User, Client, DiscordException, File
from discord.http import Forbidden
from datetime import datetime
from ..scheduling import TimedTask
from ..bbObjects import bbUser
from ..bbDatabases import bbUserDB
from ..logging import bbLogger
from typing import List, Optional, Union, Dict, cast
from io import BytesIO
from zipfile import ZipFile, ZIP_LZMA
import os
import traceback
from datetime import datetime, timezone


def getSanitizedJson(user: bbUser.bbUser) -> str:
    return json.dumps(user, indent=4, sort_keys=True)


class DataPrivacyReactionMenu(ReactionMenu.ReactionMenu):
    """This is only non-serializable because of the timeout task"""
    def __init__(self, msg : Message, userId: int, timeout : Optional[TimedTask.TimedTask] = None,
            titleTxt : str = "", desc : str = "", col : Colour = Colour.blue(),
            footerTxt : str = "", img : str = "", thumb : str = "", icon : str = "", authorName : str = ""):
        exportDataOption = ReactionMenu.NonSaveableReactionMenuOption("Export All User Data", bbConfig.defaultDownloadEmoji, self.exportUserData, None)
        cancelOption = ReactionMenu.NonSaveableReactionMenuOption("Close Menu", bbConfig.defaultCancelEmoji, self.delete, None)
        menuOptions = {
            bbConfig.defaultDownloadEmoji: exportDataOption,
            bbConfig.defaultCancelEmoji: cancelOption
        }
        super().__init__(msg, options=menuOptions, titleTxt=titleTxt, desc=desc, col=col, footerTxt=footerTxt, img=img, thumb=thumb, icon=icon, authorName=authorName, timeout=timeout)
        self.saveable = False
        self.userId = userId


    async def exportUserData(self):
        if not bbGlobals.usersDB.userIDExists(self.userId):
            await self.msg.channel.send("User data export failed: No data is currently stored for you.")
            await self.delete()
            return
        
        client = cast(Client, bbGlobals.client)
        try:
            dcUser = client.get_user(self.userId) or await client.fetch_user(self.userId)
        except DiscordException:
            dcUser = None
            
        if dcUser is None:
            bbLogger.log(
                DataPrivacyReactionMenu.__name__, 
                DataPrivacyReactionMenu.exportUserData.__name__,
                f"Failed to find discord user for id {self.userId}")
            await self.delete()
        
        bUser = cast("bbUser.bbUser", bbGlobals.usersDB.getUser(self.userId))
        endReached = False
        with BytesIO() as zipBuffer, ZipFile(zipBuffer, "w", compression=ZIP_LZMA) as zipFile:
            zipFile.writestr("current.json", getSanitizedJson(bUser))
            failedDates: List[str] = []
            for subdir, _, files in os.walk(bbConfig.userDBBackupPath):
                if endReached:
                    break
                for fileName in (fname for fname in files if fname.lower().endswith(".json")):
                    filePath = os.path.join(bbConfig.userDBBackupPath, subdir, fileName)
                    try:
                        raw = lib.jsonHandler.readJSON(filePath)
                        userDb = bbUserDB.bbUserDB.fromDict(raw)
                    except json.JSONDecodeError:
                        bbLogger.log(
                            DataPrivacyReactionMenu.__name__, 
                            DataPrivacyReactionMenu.exportUserData.__name__,
                            f"Failed to deserialize backup {filePath}",
                            trace=traceback.format_exc())
                        failedDates.append(fileName[:-5])
                        continue
                    if not userDb.userIDExists(self.userId):
                        endReached = True
                        break
                    userBackup = userDb.getUser(self.userId)
                    zipFile.writestr(f"{fileName[:-5]}.json", getSanitizedJson(userBackup))
        
            if dcUser.dm_channel is None:
                await dcUser.create_dm()
            if dcUser.dm_channel is None:
                sendChannel = dcUser
            else:
                sendChannel = dcUser.dm_channel

            zipBuffer.seek(0)
            nowStr = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(":", ".")
            dcFile = File(zipBuffer, filename=f"BB_BatchUserDataExport_{self.userId}_{nowStr}.zip")
            try:
                await sendChannel.send("Here is all user data currently stored about you:", file=)dcFile
            except Forbidden:
                await self.msg.channel.send(":x: I can't DM you, " + dcUser.mention + "! Please enable DMs from users who are not friends.")


    def toDict(self, **kwargs) -> dict:
        """Serialize this menu to dictionary format for saving to file.

        :return: A dictionary containing all information needed to reconstruct this menu object
        :rtype: dict
        """
        # TODO: Remove this method. The guild is already saved in ReactionMenu.toDict
        baseDict = super().toDict(**kwargs)
        baseDict["userId"] = self.userId
        return baseDict


    @classmethod
    def fromDict(cls, rmDict : dict, **kwargs) -> "DataPrivacyReactionMenu":
        if "msg" in kwargs:
            raise NameError("Required kwarg not given: msg")
        msg = kwargs["msg"]

        return DataPrivacyReactionMenu(msg, rmDict["userId"],
                                    titleTxt=rmDict["titleTxt"] if "titleTxt" in rmDict else "",
                                    desc=rmDict["desc"] if "desc" in rmDict else "",
                                    col=Colour.from_rgb(rmDict["col"][0], rmDict["col"][1], rmDict["col"][2]) if "col" in rmDict else Colour.blue(),
                                    footerTxt=rmDict["footerTxt"] if "footerTxt" in rmDict else "",
                                    img=rmDict["img"] if "img" in rmDict else "",
                                    thumb=rmDict["thumb"] if "thumb" in rmDict else "",
                                    icon=rmDict["icon"] if "icon" in rmDict else "",
                                    authorName=rmDict["authorName"] if "authorName" in rmDict else "")