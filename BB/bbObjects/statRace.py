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


MAX_RACE_PLACES = 10


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
            "item": self.item,
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
    scoreMode: str
    orderAsc: bool
    statName: str

    def toDict(self, **kwargs) -> dict:
        return {
            "rewards": [r.toDict() for r in self.rewards],
            "startDate": self.startDate.timestamp(),
            "endDate": self.endDate.timestamp(),
            "scoreMode": self.scoreMode,
            "orderAsc": self.orderAsc,
            "statName": self.statName
        }


    @classmethod
    def fromDict(cls, data : dict, **kwargs) -> "StatRace":
        return StatRace(
            rewards=[StatRaceReward.fromDict(r) for r in data["rewards"]],
            startDate=datetime.fromtimestamp(data["startDate"], timezone.utc),
            endDate=datetime.fromtimestamp(data["endDate"], timezone.utc),
            scoreMode=data["scoreMode"],
            orderAsc=data["orderAsc"],
            statName=data["statName"])
    

    def calculateRewards(
        self,
        startSaveData: "bbUserDB.bbUserDB", 
        endSaveData: "bbUserDB.bbUserDB", 
        guild: "bbGuild.bbGuild"
    ) -> Dict[int, Union[StatRaceResultsEntry, UnclaimedStatRaceResultsEntry]]:
        defaultUser = bbUser.bbUser.fromDict(bbUser.defaultUserDict, id=0)

        # get the requested stats and sort users by the stat and the last updated timestamp
        # when orderAsc is false, the timestamp is negative
        inputDict: Dict[int, Tuple[Union[int, float], float]] = {}
        user: bbUser.bbUser
          
        average = 0.0
        users = endSaveData.getUsers()

        if self.statName == "checkAccuracy" and self.scoreMode == "periodonly":
            reference = startSaveData.getUser(user.id) if startSaveData.userIDExists(user.id) else defaultUser
            total = sum(
                user.getPeriodOnlyStatByName("systemsChecked", reference)
                for user in users
            )
            count = len(users)
            average = total / count if count else 0.0

        for user in users:
            if self.scoreMode == "periodonly":
                reference = startSaveData.getUser(user.id) if startSaveData.userIDExists(user.id) else defaultUser
                lastUpdated = user.getStatUpdatedTime(self.statName)
                lastUpdatedStamp = 0 if lastUpdated == datetime.min else lastUpdated.timestamp()      
                inputDict[user.id] = (user.getPeriodOnlyStatByName(self.statName, reference, average), (1 if self.orderAsc else -1) * lastUpdatedStamp)
            elif self.scoreMode == "delta":
                reference = startSaveData.getUser(user.id) if startSaveData.userIDExists(user.id) else defaultUser
                lastUpdated = user.getStatUpdatedTime(self.statName)
                lastUpdatedStamp = 0 if lastUpdated == datetime.min else lastUpdated.timestamp()
                inputDict[user.id] = (user.getDeltaStatByName(self.statName, reference), (1 if self.orderAsc else -1) * lastUpdatedStamp)
            elif self.scoreMode == "lifetime":
                lastUpdated = user.getStatUpdatedTime(self.statName)
                lastUpdatedStamp = 0 if lastUpdated == datetime.min else lastUpdated.timestamp()
                inputDict[user.id] = (user.getStatByName(self.statName), (1 if self.orderAsc else -1) * lastUpdatedStamp)
            else:
                raise ValueError(f"invalid scoreMode: {self.scoreMode}")

        sortedUsers = sorted(inputDict.items(), key=operator.itemgetter(1), reverse=not self.orderAsc)[:MAX_RACE_PLACES]
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
                    + f"Race: {debugFmtDt(self.startDate)} - {debugFmtDt(self.endDate)} {self.statName} {self.scoreMode} {'asc' if self.orderAsc else 'desc'}\n"
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
                    entry[1][0],
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
        elif self.statName == "incorrectChecks":
            return "number of incorrect systems checked"
        elif self.statName == "checkAccuracy":
            return f"Ratio of correct to incorrect system `{bbConfig.commandPrefix}check`s: `(correct {bbConfig.commandPrefix}checks / incorrect " + bbConfig.commandPrefix + "checks) * 100`"
        elif self.statName == "bountyWins":
            return "number of bounties won"
        elif self.statName == "lifetimeCredits":
            return "lifetime credits earned"
        elif self.statName == "loadoutTotalDps":
            return "loadout DPS"
        elif self.statName == "loadoutTotalHp":
            return "loadout total HP"
        elif self.statName == "loadoutTotalCargo":
            return "loadout cargo capacity"
        elif self.statName == "loadoutTotalHandling":
            return "loadout handling"
        elif self.statName == "ownedItemsCount":
            return "number of owned items"
        elif self.statName == "equippedItemsCount":
            return "number of equipped items"
        elif self.statName == "duelWins":
            return "number of duels won"
        elif self.statName == "duelLosses":
            return "number of duels lost"
        elif self.statName == "duelCreditsWins":
            return "credits won from duels"
        elif self.statName == "duelLosses":
            return "credits lost in duels"
        elif self.statName == "bountyWinsToday":
            return "number of bounties won today"
        elif self.statName == "value":
            return "total value"
        elif self.statName == "averageCheckCountWeightedCheckAccuracy":
            return "check accuracy (weighted by the global average checks)"
        else:
            raise ValueError(f"unrecognised stat: {self.statName}") 
        

    def getFormattedScoreModeExt(self) -> str:
        if self.scoreMode == "delta":
            return "increase"
        if self.scoreMode == "periodonly" or self.scoreMode == "relativeperiodonly":
            return "during the race"
        return ""
    

    def makeLeaderboardEmbed(
        self,
        onlyShowRewards: bool,
        raceIsOver: bool,
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
        elif self.statName == "incorrectChecks":
            boardTitle = "Incorrect $checks"
            boardUnit = "System"
            boardUnits = "Systems"
            boardDesc = "*Total number of systems `" + bbConfig.commandPrefix + "check`ed that were on a route, but not the answer"
        elif self.statName == "checkAccuracy":
            boardTitle = "Check Accuracy"
            boardUnit = "%"
            boardUnits = "%"
            boardDesc = "Ratio of correct to incorrect system `" + bbConfig.commandPrefix + "check`s: `(correct " + bbConfig.commandPrefix + "checks / incorrect " + bbConfig.commandPrefix + "checks) * 100`"
        elif self.statName == "bountyWins":
            boardTitle = "Bounties Won"
            boardUnit = "Bounty"
            boardUnits = "Bounties"
            boardDesc = "*Total number of bounties won"
        elif self.statName == "lifetimeCredits":
            boardTitle = "Credits Earned From Bounties"
            boardUnit = "Credit"
            boardUnits = "Credits"
            boardDesc = "*Total credits earned from bounties"
        elif self.statName == "loadoutTotalDps":
            boardTitle = "Loadout DPS"
            boardUnit = "dps"
            boardUnits = "dps"
            boardDesc = "*Total DPS of your equipped items"
        elif self.statName == "loadoutTotalHp":
            boardTitle = "Loadout Total HP"
            boardUnit = "Bounty"
            boardUnits = "Bounties"
            boardDesc = "*Total HP of your equipped items, for example your hull, armour, and shield"
        elif self.statName == "loadoutTotalCargo":
            boardTitle = "Loadout Cargo Capacity"
            boardUnit = "Bounty"
            boardUnits = "Bounties"
            boardDesc = "*Total loadout cargo capacity"
        elif self.statName == "loadoutTotalHandling":
            boardTitle = "Loadout Handling"
            boardUnit = "Bounty"
            boardUnits = "Bounties"
            boardDesc = "*Total loadout handling"
        elif self.statName == "ownedItemsCount":
            boardTitle = "Owned Items Count"
            boardUnit = "Bounty"
            boardUnits = "Bounties"
            boardDesc = "*Total number of owned items, including hangar and loadout"
        elif self.statName == "equippedItemsCount":
            boardTitle = "Equipped Items Count"
            boardUnit = "Bounty"
            boardUnits = "Bounties"
            boardDesc = "*Total number of equipped items"
        elif self.statName == "duelWins":
            boardTitle = "Duels Won"
            boardUnit = "Bounty"
            boardUnits = "Bounties"
            boardDesc = "*Total number of duels won"
        elif self.statName == "duelLosses":
            boardTitle = "Duels Lost"
            boardUnit = "Bounty"
            boardUnits = "Bounties"
            boardDesc = "*Total number of duels lost"
        elif self.statName == "duelCreditsWins":
            boardTitle = "Credits Won In Duels"
            boardUnit = "Bounty"
            boardUnits = "Bounties"
            boardDesc = "*Total amount of credits won in duels"
        elif self.statName == "duelLosses":
            boardTitle = "Credits Lost In Duels"
            boardUnit = "Bounty"
            boardUnits = "Bounties"
            boardDesc = "*Total amount of credits lost in duels"
        elif self.statName == "bountyWinsToday":
            boardTitle = "Bounty Wins Today"
            boardUnit = "Bounty"
            boardUnits = "Bounties"
            boardDesc = "*Total number of bounties won, today only"
        elif self.statName == "value":
            boardTitle = "Total Value"
            boardUnit = "Credit"
            boardUnits = "Credits"
            boardDesc = "*The total value of player inventory, loadout and credits balance"
        elif self.statName == "averageCheckCountWeightedCheckAccuracy":
            boardTitle = "Check Accuracy (Weighted by Global Average Checks)"
            boardUnit = "%"
            boardUnits = "%"
            boardDesc = f"Ratio of correct to incorrect system `{bbConfig.commandPrefix}check`s, relative to the global average number of system checks: `(correct {bbConfig.commandPrefix}checks / total {bbConfig.commandPrefix}checks) / (sqrt(total {bbConfig.commandPrefix}checks) / sqrt(global average {bbConfig.commandPrefix}checks))`"
        else:
            err = f"unrecognised stat: {self.statName}"
            logging.bbLogger.log(StatRace.__name__, StatRace.makeLeaderboardEmbed.__name__, err)
            raise ValueError(err)

        boardDesc += ".*"
        if self.orderAsc:
            boardTitle = f"Lowest {boardTitle}"
        if self.scoreMode == "delta":
            boardTitle = f"{boardTitle} Delta"
        elif self.scoreMode == "periodonly" or self.scoreMode == "periodonlyrelative":
            boardTitle = f"{boardTitle} During the Race"

        boardTitle = f"{self.startDate.strftime('%d/%m/%Y')} {lib.timeUtil.td_format(self.startDate, self.endDate).title()} Stat Race: {boardTitle}"

        # build the leaderboard embed
        leaderboardEmbed = lib.discordUtil.makeEmbed(titleTxt=boardTitle, icon=bbData.winIcon, col=bbData.factionColours["neutral"], desc=boardDesc)

        doStar = set() if not raceIsOver or len(self.rewards) == MAX_RACE_PLACES else {x.fixedPlace - 1 for x in self.rewards}
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
            placeStr = f"**{entry.place}{lib.stringTyping.getNumExtension(entry.place)} Place**" if onlyShowRewards else f"**{entry.place}. **"
            if isinstance(entry, StatRaceResultsEntry) and not onlyShowRewards:
                if raceIsOver:
                    rewardStr = (f"\nYou won a: {f'{entry.reward.emoji.sendable} ' if entry.reward.hasEmoji else ''}**{entry.reward.name}**!" if entry.reward is not None else
                        "\nReward creation failed - please contact a developer!" if entry.rewardDeserializationFailed
                        else "")
                else:
                    rewardStr = (f"\n{f'{entry.reward.emoji.sendable} ' if entry.reward.hasEmoji else ''}{entry.reward.name}" if entry.reward is not None else
                        "\nReward creation failed - please contact a developer!" if entry.rewardDeserializationFailed
                        else "")
                leaderboardEmbed.add_field(
                    value=placeStr + f"<@{entry.userId}>{rewardStr}",
                    name=("⭐ " if place in doStar else "") + str(entry.statValue) + " " + (boardUnit if entry.statValue == 1 else boardUnits), inline=False)
            else:
                rewardStr = (f"\n{f'{entry.reward.emoji.sendable} ' if entry.reward.hasEmoji else ''}{entry.reward.name}\n{entry.reward.statsStringShort()}" if entry.reward is not None else
                    "\nReward creation failed - please contact a developer!" if entry.rewardDeserializationFailed
                    else "")
                leaderboardEmbed.add_field(
                    value=placeStr + rewardStr,
                    name="⭐ " if place in doStar else "", inline=False)
            
        return leaderboardEmbed
    

    def getStartingSaveData(self) -> Optional["bbUserDB.bbUserDB"]:
        if self.scoreMode == "lifetime":
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
                    + f"Race: {debugFmtDt(self.startDate)} - {debugFmtDt(self.endDate)} {self.statName} {self.scoreMode} {'asc' if self.orderAsc else 'desc'}\n"
                    + f"Serialized item: {json.dumps(item.toDict())}",
                    trace=traceback.format_exc())