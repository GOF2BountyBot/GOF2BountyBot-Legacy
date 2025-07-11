from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import List, Tuple, Union, Dict, Optional
from ..baseClasses.bbSerializable import bbSerializable
import discord
from . import bbGuild, bbUser
from ..bbDatabases import bbUserDB
from ..bbConfig import bbConfig, bbData
from .. import logging, lib
from ..bbObjects.items import bbItem
import traceback
import operator
import os


def debugFmtDt(d: datetime) -> str:
    return f"{d} ({d.timestamp()})"


@dataclass
class StatRaceResultsEntry:
    userId: int
    statValue: Union[int, float]
    place: int
    reward: Optional["bbItem.bbItem"]
    rewardDeserializationFailed: bool


@dataclass
class UnclaimedStatRaceResultsEntry:
    place: int
    reward: Optional["bbItem.bbItem"]
    rewardDeserializationFailed: bool


@dataclass
class StatRaceReward(bbSerializable):
    item: dict
    fixedPlace: int

    def toDict(self, **kwargs) -> dict:
        return {
            "item": json.dumps(self.item),
            "fixedPlace": self.fixedPlace
        }


    @classmethod
    def fromDict(cls, data : dict, **kwargs) -> "StatRaceReward":
        return StatRaceReward(
            item=data["item"], 
            fixedPlace=data["fixedPlace"])

@dataclass
class StatRace(bbSerializable):
    rewards: List[StatRaceReward]
    startDate: datetime
    endDate: datetime
    deltaMode: bool
    orderAsc: bool
    statName: str

    def toDict(self, **kwargs) -> dict:
        return {
            "rewards": [r.toDict() for r in self.rewards],
            "startDate": self.startDate.timestamp(),
            "endDate": self.endDate.timestamp(),
            "deltaMode": self.deltaMode,
            "orderAsc": self.orderAsc,
            "statName": self.statName
        }


    @classmethod
    def fromDict(cls, data : dict, **kwargs) -> "StatRace":
        return StatRace(
            rewards=[StatRaceReward.fromDict(r) for r in data["rewards"]],
            startDate=datetime.fromtimestamp(data["startDate"], timezone.utc),
            endDate=datetime.fromtimestamp(data["endDate"], timezone.utc),
            deltaMode=data["deltaMode"],
            orderAsc=data["orderAsc"],
            statName=data["statName"])
    

    def calculateRewards(
        self,
        startSaveData: "bbUserDB.bbUserDB", 
        endSaveData: "bbUserDB.bbUserDB", 
        guild: "bbGuild.bbGuild"
    ) -> Dict[int, Union[StatRaceResultsEntry, UnclaimedStatRaceResultsEntry]]:
        defaultUser = bbUser.bbUser.fromDict(bbUser.defaultUserDict, id=0)

        # get the requested stats and sort users by the stat
        inputDict: Dict[int, Union[int, float]] = {}
        user: bbUser.bbUser
        for user in endSaveData.getUsers():
            newValue = user.getStatByName(self.statName)
            if self.deltaMode:
                oldValue = startSaveData.getUser(user.id).getStatByName(self.statName) if startSaveData.userIDExists(user.id) else defaultUser.getStatByName(self.statName)
                inputDict[user.id] = newValue - oldValue
            else:
                inputDict[user.id] = newValue

        sortedUsers = sorted(inputDict.items(), key=operator.itemgetter(1), reverse=not self.orderAsc)
        results: Dict[int, Union[StatRaceResultsEntry, UnclaimedStatRaceResultsEntry]] = {}

        for reward in self.rewards:
            try:
                item = bbItem.spawnItem(reward.item)
                itemFailed = False
            except Exception as ex:
                logging.bbLogger.log(
                    StatRace.__name__,
                    StatRace.makeLeaderboardEmbed.__name__,
                    f"Failed to deserialize reward with {type(ex).__name__}: {ex}\n"
                    + f"Guild: {guild.id}\n"
                    + f"Race: {debugFmtDt(self.startDate)} - {debugFmtDt(self.endDate)} {self.statName} {'delta' if self.deltaMode else 'non-delta'} {'asc' if self.orderAsc else 'desc'}\n"
                    + f"Serialized item: {json.dumps(reward.item)}",
                    trace=traceback.format_exc())
                item = None
                itemFailed = True
            
            if reward.fixedPlace > len(sortedUsers):
                results[reward.fixedPlace] = UnclaimedStatRaceResultsEntry(
                    reward.fixedPlace,
                    item,
                    itemFailed
                )
            else:
                entry = sortedUsers[reward.fixedPlace - 1]
                results[reward.fixedPlace] = StatRaceResultsEntry(
                    entry[0],
                    entry[1],
                    reward.fixedPlace,
                    item,
                    itemFailed
                )

        return results


    def getFormattedStatName(self) -> str:
        if self.statName == "credits":
            return "credits balance"
        elif self.statName == "systemsChecked":
            return "number of systems checked"
        elif self.statName == "bountyWins":
            return "number of bounties won"
        elif self.statName == "lifetimeCredits":
            return "lifetime credits earned"
        elif self.statName == "value":
            return "total value"
        else:
            raise ValueError(f"unrecognised stat: {self.statName}") 
    

    def makeLeaderboardEmbed(
        self,
        onlyShowRewards: bool,
        showWinnerStars: bool,
        results: Dict[int, Union[StatRaceResultsEntry, UnclaimedStatRaceResultsEntry]]
    ) -> discord.Embed:
        if self.statName == "credits":
            boardTitle = "Credits Balance"
            boardUnit = "Credit"
            boardUnits = "Credits"
            boardDesc = "*Player credits balance"
        elif self.statName == "systemsChecked":
            boardTitle = "Systems Checked"
            boardUnit = "System"
            boardUnits = "Systems"
            boardDesc = "*Total number of systems `" + bbConfig.commandPrefix + "check`ed"
        elif self.statName == "bountyWins":
            boardTitle = "Bounties Won"
            boardUnit = "Bounty"
            boardUnits = "Bounties"
            boardDesc = "*Total number of bounties won"
        elif self.statName == "lifetimeCredits":
            boardTitle = "Lifetime Credits Earned"
            boardUnit = "Credit"
            boardUnits = "Credits"
            boardDesc = "*Total credits earned from bounties"
        elif self.statName == "value":
            boardTitle = "Total Value"
            boardUnit = "Credit"
            boardUnits = "Credits"
            boardDesc = "*The total value of player inventory, loadout and credits balance"
        else:
            err = f"unrecognised stat: {self.statName}"
            logging.bbLogger.log(StatRace.__name__, StatRace.makeLeaderboardEmbed.__name__, err)
            raise ValueError(err)

        boardDesc += ".*"
        if self.orderAsc:
            boardTitle = f"Lowest {boardTitle}"
        if self.deltaMode:
            boardTitle = f"{boardTitle} Delta"

        boardTitle = f"{self.startDate.strftime('%d/%m/%Y')} {lib.timeUtil.td_format(self.startDate, self.endDate)} Stat Race: {boardTitle}"

        # build the leaderboard embed
        leaderboardEmbed = lib.discordUtil.makeEmbed(titleTxt=boardTitle, icon=bbData.winIcon, col=bbData.factionColours["neutral"], desc=boardDesc)

        doStar = set() if not showWinnerStars or len(self.rewards) == 10 else {x.fixedPlace - 1 for x in self.rewards}
        topPlaces = sorted(results.items(), key=lambda pair: pair[0])
        noRewards = False
        if onlyShowRewards:
            try:
                lastIndexWithReward = next(i for i, p in list(enumerate(topPlaces))[::-1] if p[1].reward is not None or p[1].rewardDeserializationFailed)
            except StopIteration:
                noRewards = True
            else:
                topPlaces = topPlaces[:lastIndexWithReward + 1]

        if noRewards:
            leaderboardEmbed.description += "\n\nThere are no rewards for this race."
            return leaderboardEmbed

        for place, entry in topPlaces:
            if isinstance(entry, StatRaceResultsEntry) and not onlyShowRewards:
                rewardStr = (f"\nYou won a: {entry.reward.name}" if entry.reward is not None else
                    "\nReward creation failed - please contact a developer!" if entry.rewardDeserializationFailed
                    else "")
                leaderboardEmbed.add_field(
                    value=f"{entry.place}. <@{entry.userId}>{rewardStr}",
                    name=("⭐ " if place in doStar else "") + str(entry.statValue) + " " + (boardUnit if entry.statValue == 1 else boardUnits), inline=False)
            else:
                rewardStr = (f"\n{entry.reward.name}" if entry.reward is not None else
                    "\nReward creation failed - please contact a developer!" if entry.rewardDeserializationFailed
                    else "")
                leaderboardEmbed.add_field(
                    value=f"{entry.place}. {rewardStr}",
                    name="⭐ " if place in doStar else "", inline=False)
            
        return leaderboardEmbed
    

    def getStartingSaveData(self) -> Optional["bbUserDB.bbUserDB"]:
        if not self.deltaMode:
            return bbUserDB.bbUserDB()
        
        dirPath = os.path.join(bbConfig.userDBBackupPath, str(self.startDate.month))
        fpath = os.path.join(dirPath, self.startDate.strftime("%d-%m-%Y.json"))
        try:
            rawStartSaveData = lib.jsonHandler.readJSON(fpath)
        except FileNotFoundError:
            logging.bbLogger.log(StatRace.__name__, StatRace.getStartingSaveData.__name__, f"file not found: {fpath}")
            return None
        
        return bbUserDB.bbUserDB.fromDict(rawStartSaveData)
        

    def distributeRewards(
        self, 
        endSaveData: "bbUserDB.bbUserDB", 
        guild: "bbGuild.bbGuild",
        userRewards: Dict[int, bbItem.bbItem]
    ):
        for userId, item in userRewards.items():
            try:
                u: bbUser.bbUser = endSaveData.getOrAddID(userId)
                u.getInventoryForItem(item).addItem(item)
            except Exception as ex:
                logging.bbLogger.log(
                    StatRace.__name__,
                    StatRace.distributeRewards.__name__,
                    f"Failed to give reward to user {userId} with {type(ex).__name__}: {ex}\n"
                    + f"Guild: {guild.id}\n"
                    + f"Race: {debugFmtDt(self.startDate)} - {debugFmtDt(self.endDate)} {self.statName} {'delta' if self.deltaMode else 'non-delta'} {'asc' if self.orderAsc else 'desc'}\n"
                    + f"Serialized item: {json.dumps(item.toDict())}",
                    trace=traceback.format_exc())