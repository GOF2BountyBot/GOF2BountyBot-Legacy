import sys
import json
from BB.bbConfig import bbPRIVATE

if len(sys.argv) != 2:
    raise ValueError("config file is required as single commandline argument")

fp = sys.argv[1]
with open(fp, "r") as cfgFile:
    cfg = json.load(cfgFile)

if "botToken" in cfg:
    bbPRIVATE.botToken = cfg["botToken"]

if "userDBPath" in cfg:
    bbPRIVATE.userDBPath = cfg["userDBPath"]

if "guildDBPath" in cfg:
    bbPRIVATE.guildDBPath = cfg["guildDBPath"]

if "bountyDBPath" in cfg:
    bbPRIVATE.bountyDBPath = cfg["bountyDBPath"]

if "reactionMenusDBPath" in cfg:
    bbPRIVATE.reactionMenusDBPath = cfg["reactionMenusDBPath"]

if "loggingFolderPath" in cfg:
    bbPRIVATE.loggingFolderPath = cfg["loggingFolderPath"]

if "developers" in cfg:
    bbPRIVATE.developers = [int(i.strip()) for i in cfg["developers"].split(",")]

if "shipsDir" in cfg:
    bbPRIVATE.shipsDir = cfg["shipsDir"]

if "skinsDir" in cfg:
    bbPRIVATE.skinsDir = cfg["skinsDir"]
    
import BB.bountybot
