from datetime import datetime

from .events.bountiesEventHub import BountiesEventHub

class ShutDownState:
    restart = 0
    shutdown = 1
    update = 2


# Discord
client = None
botLoggedIn = False


# Databases
usersDB = None
guildsDB = None


# Timed tasks
newBountiesTTDB = None

shopRefreshTT = None
dbSaveTT = None

duelRequestTTDB = None

botOperationsTTDB = None

# Reaction Menus
reactionMenusDB = None
reactionMenusTTDB = None


# Scheduling overrides
newBountyFixedDeltaChanged = False


# Names of ships currently being rendered
currentRenders = []

shutdown = ShutDownState.restart
lastSuccessfulSave = datetime.min

# Events
bountiesEventHub = BountiesEventHub()