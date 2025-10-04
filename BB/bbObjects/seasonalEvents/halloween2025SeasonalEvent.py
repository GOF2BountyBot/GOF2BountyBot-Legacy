from datetime import date
import random

from ... import bbGlobals, lib
from ..bounties import bbBounty, bbBountyConfig
from ..bounties.bountyRoutes.bountyRouteConfig import PathOfLengthRouteConfig
from .. import bbGuild
from ...scheduling import TimedTask

SPECIAL_ENEMY_ROUTE_LENGTH_MIN = 7
SPECIAL_ENEMY_ROUTE_LENGTH_MAX = 13

SPECIAL_ENEMY_RESURRECTION_TIME_SECONDS_MIN = 5 * 60
SPECIAL_ENEMY_RESURRECTION_TIME_SECONDS_MAX = 10 * 60

GHOST_QUIRK_IDENTIFIER = "Halloween2025SeasonalEvent_GhostBounty"
SKELETON_QUIRK_IDENTIFIER = "Halloween2025SeasonalEvent_SkeletonBounty"
ZOMBIE_QUIRK_IDENTIFIER = "Halloween2025SeasonalEvent_ZombieBounty"

SPECIAL_ENEMY_QUIRK_IDENTIFIERS = [GHOST_QUIRK_IDENTIFIER, SKELETON_QUIRK_IDENTIFIER, ZOMBIE_QUIRK_IDENTIFIER]

class Halloween2025SeasonalEvent:
    def __init__(self) -> None:
        self.startOnDate = date(2025, 10, 1)
        self.endAfterDate = date(2025, 10, 31)
        self.bountyResurrectAsSpecialEnemyChancePercent = 10

    def activate(self):
        bbGlobals.bountiesEventHub.subscribeBountyDefeated(self.onBountyDefeated)

    def deactivate(self):
        bbGlobals.bountiesEventHub.unsubscribeBountyDefeated(self.onBountyDefeated)

    def __del__(self):
        self.deactivate()

    async def onBountyDefeated(self, bounty: "bbBounty.Bounty", guild: "bbGuild.bbGuild"):
        if not self.bountyCanResurrectAsEvent(bounty):
            return
        
        if random.random() > self.bountyResurrectAsSpecialEnemyChancePercent / 100:
            return
        
        specialEnemyType = random.choice(SPECIAL_ENEMY_QUIRK_IDENTIFIERS)
        
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
        return not any(i in bounty.quirkIdentifiers for i in SPECIAL_ENEMY_QUIRK_IDENTIFIERS)