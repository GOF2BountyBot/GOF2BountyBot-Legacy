from abc import ABC
from datetime import date
import random
from typing import Dict, Iterable, Optional, Set, Type, TypeVar

from ... import bbGlobals, lib
from ..bounties import bbBounty, bbBountyConfig
from ..bounties.bountyRoutes.bountyRouteConfig import PathOfLengthRouteConfig
from .. import bbGuild
from ...scheduling import TimedTask
from . import seasonalEvent, bountyMessageFormatter

SPECIAL_ENEMY_ROUTE_LENGTH_MIN = 7
SPECIAL_ENEMY_ROUTE_LENGTH_MAX = 13

SPECIAL_ENEMY_RESURRECTION_TIME_SECONDS_MIN = 5 * 60
SPECIAL_ENEMY_RESURRECTION_TIME_SECONDS_MAX = 10 * 60

class Halloween2025SpecialEnemy(ABC):
    QuirkIdentifier: str
    FriendlyName: str

halloweenEnemiesByQuirkIdentifier: Dict[str, Type[Halloween2025SpecialEnemy]] = {}

TSpecialEnemyType = TypeVar("TSpecialEnemyType", bound=Type[Halloween2025SpecialEnemy])

def halloweenSpecialEnemy(t: TSpecialEnemyType) -> TSpecialEnemyType:
    halloweenEnemiesByQuirkIdentifier[t.QuirkIdentifier] = t
    return t

@halloweenSpecialEnemy
class GhostSpecialEnemy(Halloween2025SpecialEnemy):
    QuirkIdentifier = "Halloween2025SeasonalEvent_GhostBounty"
    FriendlyName = "Ghost"

@halloweenSpecialEnemy
class SkeletonSpecialEnemy(Halloween2025SpecialEnemy):
    QuirkIdentifier = "Halloween2025SeasonalEvent_SkeletonBounty"
    FriendlyName = "Skeleton"

@halloweenSpecialEnemy
class ZombieSpecialEnemy(Halloween2025SpecialEnemy):
    QuirkIdentifier = "Halloween2025SeasonalEvent_ZombieBounty"
    FriendlyName = "Zombie"

SPECIAL_ENEMY_QUIRK_IDENTIFIERS_SET = set(halloweenEnemiesByQuirkIdentifier.keys())
SPECIAL_ENEMY_QUIRK_IDENTIFIERS_LIST = list(halloweenEnemiesByQuirkIdentifier.keys())

def randomSpecialEnemyQuirkIdentifier():
    return random.choice(SPECIAL_ENEMY_QUIRK_IDENTIFIERS_LIST)

def findSpecialEnemyQuirkIdentifiers(quirks: Iterable[str]) -> Set[str]:
    return SPECIAL_ENEMY_QUIRK_IDENTIFIERS_SET.intersection(quirks)

def firstSpecialEnemyQuirkIdentifier(quirks: Iterable[str]) -> Optional[str]:
    for q in findSpecialEnemyQuirkIdentifiers(quirks):
        return q
    return None

def firstSpecialEnemyType(quirks: Iterable[str]) -> Optional[Type[Halloween2025SpecialEnemy]]:
    quirk = firstSpecialEnemyQuirkIdentifier(quirks)
    return None if quirk is None else halloweenEnemiesByQuirkIdentifier.get(quirk, None)

class Halloween2025SeasonalEvent(seasonalEvent.SeasonalEvent):
    def __init__(self) -> None:
        self.startOnDate = date(2025, 10, 1)
        self.endAfterDate = date(2025, 10, 31)
        self.bountyResurrectAsSpecialEnemyChancePercent = 10
        self.bountyFormatIntercept = Halloween2025BountyFormatIntercept()

    def activate(self):
        bbGlobals.bountiesEventHub.subscribeBountyDefeated(self.onBountyDefeated)

    def deactivate(self):
        bbGlobals.bountiesEventHub.unsubscribeBountyDefeated(self.onBountyDefeated)

    async def onBountyDefeated(self, bounty: "bbBounty.Bounty", guild: "bbGuild.bbGuild"):
        if not self.bountyCanResurrectAsEvent(bounty):
            return
        
        if random.random() > self.bountyResurrectAsSpecialEnemyChancePercent / 100:
            return
        
        specialEnemyType = randomSpecialEnemyQuirkIdentifier()
        
        routeLength = random.randint(SPECIAL_ENEMY_ROUTE_LENGTH_MIN, SPECIAL_ENEMY_ROUTE_LENGTH_MAX)
        newRouteConfig = PathOfLengthRouteConfig(
            None, # answer
            None, # start node
            (None, routeLength)) # first segment (next node, segment length)
        
        config = bbBountyConfig.BountyConfig(
            faction=bounty.faction, 
            route=newRouteConfig, 
            checked=bounty.checked, 
            reward=bounty.reward, 
            issueTime=bounty.issueTime, 
            endTime=bounty.endTime,
            quirkIdentifiers=set((specialEnemyType,)))
        
        resurrectDelay = lib.timeUtil.getRandomDelaySeconds({
            "min": SPECIAL_ENEMY_RESURRECTION_TIME_SECONDS_MIN,
            "max": SPECIAL_ENEMY_RESURRECTION_TIME_SECONDS_MAX
        })

        resurrectTask = TimedTask.TimedTask(
            expiryDelta=resurrectDelay,
            autoReschedule=False,
            expiryFunction=guild.spawnAndAnnounceNewBounty,
            expiryFunctionArgs=config)
        
        bbGlobals.newBountiesTTDB.scheduleTask(resurrectTask)

    def bountyCanResurrectAsEvent(self, bounty: "bbBounty.Bounty"):
        return firstSpecialEnemyQuirkIdentifier(bounty.quirkIdentifiers) is not None
    

class Halloween2025BountyFormatIntercept(bountyMessageFormatter.BountyMessageFormatIntercept):
    def formatCriminalName(self, bounty: bbBounty.Bounty) -> str:
        specialEnemyType = firstSpecialEnemyType(bounty.quirkIdentifiers)
        base = self.defaultFormat.formatCriminalName(bounty)

        return base if specialEnemyType is None else f"{base} ({specialEnemyType.FriendlyName})"
    
    def formatBountyBoardListingDescription(self, bounty: bbBounty.Bounty) -> str:
        base = self.defaultFormat.formatBountyBoardListingDescription(bounty)

        return base if firstSpecialEnemyQuirkIdentifier(bounty.quirkIdentifiers) is None else \
            f"{base}\n:jack_o_lantern: This is a halloween special enemy!"
    