# Typing imports
from __future__ import annotations

import math, random
from ..lib.emojis import dumbEmoji, UninitializedDumbEmoji
from . import bbPRIVATE

##### UTIL #####


# Number of decimal places to calculate itemTLSpawnChanceForShopTL values to
tl_resolution = 3


def truncToRes(num : float) -> float:
    """Truncate the passed float to tl_resolution decimal places.

    :param float num: Float number to truncate
    :return: num, truncated to tl_resolution decimal places
    :rtype: float
    """
    return math.trunc(num * math.pow(10, tl_resolution)) / math.pow(10, tl_resolution)



##### COMMANDS #####

# List of module names from BB.commands to import
includedCommandModules = (  "usr_misc", "usr_homeguilds", "usr_gof2-info", "usr_bounties", "usr_loadout", "usr_economy",
                            "admn_channels", "admn_misc",
                            "dev_misc", "dev_channels", "dev_bounties", "dev_items", "dev_skins")

maxCommandsPerHelpPage = 5
helpEmbedTimeout = {"minutes": 5}



##### DUELS #####

# Amount of time before a duel request expires
duelReqExpiryTime = {"days":1}
# duelReqExpiryTime as a user-friendly string for printing
duelReqExpiryTimeStr = "1 day"
# The amount to vary ship stats (+-) by before executing a duel
duelVariancePercent = 0.05

# Max number of entries that can be printed for a duel log
duelLogMaxLength = 10

# Percentage probability of a user envoking a cloak module in a given timeStep, should they have one equipped
duelCloakChance = 20



##### SHOPS #####

# Amount of time to wait between refreshing stock of all shops
shopRefreshStockPeriod = {"days":0, "hours":6, "minutes":0, "seconds":0}

# The number of ranks to use when randomly picking shop stock
numShipRanks = 10
numWeaponRanks = 10
numModuleRanks = 7
numTurretRanks = 3

# The default number of items shops should generate every shopRefreshStockPeriod
shopDefaultShipsNum = 5
shopDefaultWeaponsNum = 5
shopDefaultModulesNum = 5
shopDefaultTurretsNum = 2

# bbTurret is the only item that has a probability not to be spawned. This metric indicates the percentage chance of turrets being stocked on a given day
turretSpawnProbability = 45

# The range of valid tech levels a shop may spawn at
minTechLevel = 1
maxTechLevel = 10

# The probability of a shop spawning with a given tech level. Tech level = index + 1
cumulativeShopTLChance = [0 for tl in range(minTechLevel, maxTechLevel + 1)]
shopTLChance = [0 for tl in range(minTechLevel, maxTechLevel + 1)]

# itemChanceSum = 0

# # Calculate spawn chance for each shop TL
# for shopTL in range(minTechLevel, maxTechLevel + 1):
#     itemChance = truncToRes(0.2 * math.pow(shopTL, 2) + 20)
#     cumulativeShopTLChance[shopTL - 1] = itemChance
#     itemChanceSum += itemChance

# looks like I can't remember maths from school, so I'm hand picking weights for now
cumulativeShopTLChance = [8, 10, 12, 12, 11, 10, 9, 8, 6, 5]
itemChanceSum = sum(cumulativeShopTLChance)

# Scale shop TL probabilities so that they add up to 1
for shopTL in range(minTechLevel, maxTechLevel + 1):
    currentChance = cumulativeShopTLChance[shopTL - 1]
    if currentChance != 0:
        cumulativeShopTLChance[shopTL - 1] = truncToRes(currentChance / itemChanceSum)

# Save non-cumulative probabilities
for i in range(len(cumulativeShopTLChance)):
    shopTLChance[i] = cumulativeShopTLChance

# Sum probabilities to give cumulative scale
currentSum = 0
for shopTL in range(minTechLevel, maxTechLevel + 1):
    currentChance = cumulativeShopTLChance[shopTL - 1]
    if currentChance != 0:
        cumulativeShopTLChance[shopTL - 1] = truncToRes(currentSum + currentChance)
        currentSum += currentChance


def pickRandomShopTL() -> int:
    """Pick a random shop techlevel, with probabilities calculated previously in bbConfig.

    :return: An integer between 1 and 10 representing a shop tech level
    :rtype: int    
    """
    tlChance = random.randint(1, 10 ** tl_resolution) / 10 ** tl_resolution
    for shopTL in range(len(cumulativeShopTLChance)):
        if cumulativeShopTLChance[shopTL] >= tlChance:
            return shopTL + 1
    return maxTechLevel


# Price ranges by which ships should be ranked into tech levels. 0th index = tech level 1
shipMaxPriceTechLevels = [50000, 100000, 200000, 500000, 1000000, 2000000, 5000000, 7000000, 7500000, 999999999]

# CUMULATIVE probabilities of items of a given tech level spawning in a shop of a given tech level
# Outer dimension is shop tech level
# Inner dimension is item tech level
itemTLSpawnChanceForShopTL = [[0 for i in range(minTechLevel, maxTechLevel + 1)] for i in range(minTechLevel, maxTechLevel + 1)]
cumulativeItemTLSpawnChanceForShopTL = [[0 for i in range(minTechLevel, maxTechLevel + 1)] for i in range(minTechLevel, maxTechLevel + 1)]

# Parameters for itemTLSpawnChanceForShopTL values, using quadratic function: https://www.desmos.com/calculator/n2xfxf8taj
# Original u function by Novahkiin22: https://www.desmos.com/calculator/tnldodey5u
# Original function by Novahkiin22: https://www.desmos.com/calculator/nrshikfmxc
tl_s = 7
tl_o = 2.3

"""def tl_u(x, t):
    h = t - tl_s
    tl_n = (x - tl_o - h) / tl_s
    mid = tl_n * (1 - math.pow(tl_n, 4))
    outer = tl_s * mid - (h / 2)
    return truncToRes(outer if outer > 0 else 0)"""

def tl_u(x : int, t : int) -> float:
    """mathematical function used when calculating item spawn probabilities.

    :param int x: int representing the item's tech level
    :param int t: int representing the owning shop's tech level
    :return: A partial probability for use in probability generation
    :rtype: float
    """
    chance = truncToRes(1 - math.pow((x - t)/1.4,2))
    return chance if chance > 0 else 0


# Loop through shop TLs
for shopTL in range(minTechLevel, maxTechLevel + 1):
    tl_h = shopTL - tl_s
    itemChanceSum = 0

    # Calculate spawn chance for each item TL in this shop TL
    for itemTL in range(minTechLevel, maxTechLevel + 1):
        itemChance = tl_u(itemTL, shopTL)
        cumulativeItemTLSpawnChanceForShopTL[shopTL - 1][itemTL - 1] = itemChance
        itemChanceSum += itemChance
    
    # Scale item TLs so that they add up to 1
    for itemTL in range(minTechLevel, maxTechLevel + 1):
        currentChance = cumulativeItemTLSpawnChanceForShopTL[shopTL - 1][itemTL - 1]
        if currentChance != 0:
            cumulativeItemTLSpawnChanceForShopTL[shopTL - 1][itemTL - 1] = truncToRes(currentChance / itemChanceSum)

    # Save non-cumulative probabilities
    for i in range(len(cumulativeItemTLSpawnChanceForShopTL[shopTL - 1])):
        itemTLSpawnChanceForShopTL[shopTL - 1][i] = cumulativeItemTLSpawnChanceForShopTL[shopTL - 1][i]

    # Sum probabilities to give cumulative scale
    currentSum = 0
    for itemTL in range(minTechLevel, maxTechLevel + 1):
        currentChance = cumulativeItemTLSpawnChanceForShopTL[shopTL - 1][itemTL - 1]
        if currentChance != 0:
            cumulativeItemTLSpawnChanceForShopTL[shopTL - 1][itemTL - 1] = truncToRes(currentSum + currentChance)
            currentSum += currentChance

print("[bbConfig] Item rarities generated:")
for shopTL in range(len(itemTLSpawnChanceForShopTL)):
    print("\t• shop TL" + str(shopTL+1) + ": itemTL",end="")
    for itemTL in range(len((itemTLSpawnChanceForShopTL[shopTL]))):
        if itemTLSpawnChanceForShopTL[shopTL][itemTL] != 0:
            print(" " + str(itemTL + 1) + "=" + str(truncToRes(itemTLSpawnChanceForShopTL[shopTL][itemTL]*100)),end="% ")
    print()


def pickRandomItemTL(shopTL : int) -> int:
    """Pick a random item techlevel, with probabilities calculated previously in bbConfig.

    :param int shopTL: int representing the tech level of the shop owning the item
    :return: An integer between 1 and 10 representing a item tech level
    :rtype: int
    """
    tlChance = random.randint(1, 10 ** tl_resolution) / 10 ** tl_resolution
    for itemTL in range(len(cumulativeItemTLSpawnChanceForShopTL[shopTL - 1])):
        if cumulativeItemTLSpawnChanceForShopTL[shopTL - 1][itemTL] >= tlChance:
            return itemTL + 1
    return maxTechLevel



##### BOUNTIES #####

newBountyWarningTimeSeconds = 20

maxBountiesPerFaction = 5

# The maximum number of bounties a player is allowed to win each day
maxDailyBountyWins = 10

# can be "fixed" or "random"
newBountyDelayType = "random-routeScale"

### fixed delay config
# only spawn bounties at this time
newBountyFixedDailyTime = {"hours":18, "minutes":40, "seconds":0}
# use the above, or just spawn after every newBountyFixedDelta
newBountyFixedUseDailyTime = False

# time to wait inbetween spawning bounties
# when using fixed-routeScale generation, use this for bounties of route length 1
newBountyFixedDelta = {"days":0, "hours":0, "minutes":1, "seconds":0}

### random delay config
# when using random delay generation, use these min and max points
# when using random-routeScale generation, use these min and max points for bounties of route length 1
newBountyDelayRandomRange = {"min": 5 * 60, "max": 7 * 60}

### routeScale config
newBountyDelayRouteScaleCoefficient = 0.85
fallbackRouteScale = 5


# The number of credits to award for each bPoint (each system in a criminal route)
bPointsToCreditsRatio = 1000

# time to put users on cooldown between using !bb check
checkCooldown = {"minutes":3}

# number of bounties ahead of a checked system in a route to report a recent criminal spotting (+1)
closeBountyThreshold = 4

# Text to send to a BountyBoardChannel when no bounties are currently active
bbcNoBountiesMsg = "```css\n[ NO ACTIVE BOUNTIES ]\n\nThere are currently no active bounty listings.\nPlease check back later, or use [ $notify bounties ] to be pinged when new ones become available!\n```"

# The number of times to retry BBC listing updates when HTTP exceptions are thrown
bbcHTTPErrRetries = 3

# The number of seconds to wait between BBC listing update retries upon HTTP exception catching
bbcHTTPErrRetryDelaySeconds = 1


##### SAVING #####

# The time to wait inbetween database autosaves.
savePeriod = {"hours":1}

# path to JSON files for database saves
userDBPath = bbPRIVATE.userDBPath
userDBBackupPath = bbPRIVATE.userDBBackupPath
guildDBPath = bbPRIVATE.guildDBPath
bountyDBPath = bbPRIVATE.bountyDBPath
reactionMenusDBPath = bbPRIVATE.reactionMenusDBPath
botGlobalSavePath = bbPRIVATE.botGlobalSavePath

# path to folder to save log txts to
loggingFolderPath = bbPRIVATE.loggingFolderPath

# Discord server containing the skinRendersChannel
mediaServer = 699744305274945650
# Channel to send ship skin renders to and link from
skinRendersChannel = 770036783026667540
# Channel to send showme-prompted ship skin renders to and link from
showmeSkinRendersChannel = 771368555019108352
# Resolution of skin render icons
skinRenderIconResolution = [800, 600]
skinRenderIconSamples = 8
# Resolution of skin render emojis (currently unused)
skinRenderEmojiResolution = [400, 400]
skinRenderEmojiSamples = 8
# Resolution of skin renders from cmd_showme_ship calls
skinRenderShowmeResolution = [800, 600]
skinRenderShowmeSamples = 6
# Resolution of skin renders from admin_cmd_showmeHD calls
skinRenderShowmeHDResolution = [1920, 1080]
skinRenderShowmeHDSamples = 4

# Percentage tolerance to give when deciding whether an image is of the correct aspect ratio
aspectRatioTolerance = 0.1



##### SCHEDULING #####

# Whether to execute timedtask checks every timedTaskLatenessThresholdSeconds ("fixed"), or to calculate the delay to wait until the next TimedTask is schedule to expire ("dynamic")
timedTaskCheckingType = "fixed"

# How late a timed task may acceptably be in seconds.
# I.e a scheduled task may expire up to timedTaskLatenessThresholdSeconds seconds after their intended expiration time.
# replaces the depracated 'delayFactor' variable
timedTaskLatenessThresholdSeconds = 10



##### MISC #####

# prefix for bot commands. dont forget a space if you want one!
commandPrefix = "$"

# When a user message prompts a DM to be sent, this emoji will be added to the message reactions.
dmSentEmoji = dumbEmoji(unicode="📬")

# When a message prompts a process that will take a long time (e.g rendering), this will be added to the message reactions. It will be removed when the long process is finished.
longProcessEmoji = dumbEmoji(unicode="⏳")

# max number of characters accepted by nameShip
maxShipNickLength = 30

# max number of characters accepted by nameShip, when called by a developer
maxDevShipNickLength = 100

# The default emojis to list in a reaction menu
numberEmojis = [dumbEmoji(unicode="0️⃣"), dumbEmoji(unicode="1️⃣"), dumbEmoji(unicode="2️⃣"), dumbEmoji(unicode="3️⃣"), dumbEmoji(unicode="4️⃣"), dumbEmoji(unicode="5️⃣"), dumbEmoji(unicode="6️⃣"), dumbEmoji(unicode="7️⃣"), dumbEmoji(unicode="8️⃣"), dumbEmoji(unicode="9️⃣"), dumbEmoji(unicode="🔟")]
defaultMenuEmojis = numberEmojis
defaultCancelEmoji = dumbEmoji(unicode="🇽")
defaultSubmitEmoji = dumbEmoji(unicode="✅")
spiralEmoji = dumbEmoji(unicode="🌀")
defaultErrEmoji = dumbEmoji(unicode="❓")
defaultAcceptEmoji = dumbEmoji(unicode="👍")
defaultRejectEmoji = dumbEmoji(unicode="👎")
defaultNextEmoji = dumbEmoji(unicode='⏩')
defaultPreviousEmoji = dumbEmoji(unicode='⏪')

# Path to the directory to use when temporarily saving textures downloaded from showme commands.
tempRendersDir = "rendering-temp"

# Default graphics to use for ship skin application tool items
defaultShipSkinToolIcon = "https://cdn.discordapp.com/attachments/700683544103747594/723472334362771536/documents.png"
defaultShipSkinToolEmoji = UninitializedDumbEmoji(777166858516299786)

defaultShipUpgradeToolIcon = "https://em-content.zobj.net/source/twitter/408/wrench_1f527.png"
defaultShipUpgradeToolEmoji = dumbEmoji(unicode="🔧")

cropEmoji = dumbEmoji(unicode="✂")
stretchEmoji = dumbEmoji(unicode="↔")

def shipSkinValueForTL(averageTL : int) -> int:
    """Calculate how skins are valued with respect to their average compatible ship techlevel.

    :param int averageTL: The average techLevel of the ships that this skin is compatible with
    :return: The value to assign to the ship skin
    :rtype: int
    """
    return averageTL * 10000

# The maximum number of rendering threads that may be dispatched simultaneously
maxConcurrentRenders = 1



##### ADMINISTRATION #####

# discord user IDs of all developers
developers = bbPRIVATE.developers

# Names to assign to each access level
accessLevelNames = ["User", "Administrator", "Developer"]

# The number of registerable command access levels.
# E.g I use 3 to represent 0=user, 1=admin, 2=dev
# TODO: Add a fourth, mod commands, with an admin-assignable role
numCommandAccessLevels = len(accessLevelNames)

# titles to give each type of user when reporting error messages etc
accessLevelTitles = ["pilot", "commander", "officer"]



##### HANGARS #####

# The maximum number of items that will be displayed per page of a user's hangar, when all item types are requested
maxItemsPerHangarPageAll = 3
# The maximum number of items that will be displayed per page of a user's hangar, when a single item type is requested
maxItemsPerHangarPageIndividual = 10

# Names to be used when checking input to !bb hangar and bbUser.numInventoryPages
validItemNames = ["ship", "weapon", "module", "turret", "all", "tool"]

# the max number of each module type that can be equipped on a ship.
maxModuleTypeEquips = {     "bbArmourModule": 1,
                            "bbBoosterModule": 1,
                            "bbCabinModule": -1,
                            "bbCloakModule": 1,
                            "bbCompressorModule": -1,
                            "bbGammaShieldModule": 1,
                            "bbMiningDrillModule": 1,
                            "bbRepairBeamModule": 1,
                            "bbRepairBotModule": 1,
                            "bbScannerModule": 1,
                            "bbShieldModule": 1,
                            "bbSpectralFilterModule": 1,
                            "bbThrusterModule": 1,
                            "bbTractorBeamModule": 1,
                            "bbTransfusionBeamModule": 1,
                            "bbWeaponModModule": 1,
                            "bbJumpDriveModule": 0,
                            "bbEmergencySystemModule": 1,
                            "bbSignatureModule": 1,
                            "bbShieldInjectorModule": 1,
                            "bbTimeExtenderModule": 1}



##### USERS #####

userAlertsIDsDefaults = {   "bounties_new": False,
    
                            "shop_refresh": False,

                            "duels_challenge_incoming_new": True,
                            "duels_challenge_incoming_cancel": False,
                            
                            "system_updates_major": False,
                            "system_updates_minor": False,
                            "system_misc": False}

homeGuildTransferCooldown = {"weeks":1}



##### REACTION MENUS #####

roleMenuDefaultTimeout = {"days": 1}
duelChallengeMenuDefaultTimeout = {"hours": 2}
pollMenuDefaultTimeout = {"minutes": 5}
expiredMenuMsg = "😴 This role menu has now expired."
pollMenuResultsBarLength = 10
maxRoleMenusPerGuild = 10
toolUseConfirmTimeoutSeconds = 60
homeGuildTransferConfirmTimeoutSeconds = 60



##### SKINS #####

defaultSkinCrateEmoji = UninitializedDumbEmoji(723709178736017419)
