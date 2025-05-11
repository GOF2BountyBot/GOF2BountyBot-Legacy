# TODO: Move items etc into JSON files

# Shame, but i'd rather this than keep factionColours in bountybot.py
from discord import Colour
# Used for importing items
import os
import json
from . import bbPRIVATE

shipsDir = bbPRIVATE.shipsDir
skinsDir = bbPRIVATE.skinsDir
CWD = os.getcwd()


# all factions recognised by BB
factions = ["terran", "vossk", "midorian", "nivelian", "neutral"]
# all factions useable in bounties
bountyFactions = ["terran", "vossk", "midorian", "nivelian"]

# names of criminals in builtIn bounties
bountyNames = {"terran": ["Pal Tyyrt", "Kehnor", "Gendol Ethor", "Korr Bekkt", "Hongar Meton"],
                "vossk": ["Mrrkt Nimkk", "Alvar Julen", "Vortt Baskk", "Oluchi Erland", "Orp Tsam"],
                "midorian": ["Toma Prakupy", "Nombur Telénah", "Bartholomeu Drew", "Doni Trillyx", "Mashon Redal"],
                "nivelian": ["Borsul Tarand", "Vilhelm Lindon", "Tamir Prakupy", "Merson Surr", "Ganfor Kant"]}

# icons for builtIn criminals
bountyIcons = { # Terran
                "Pal Tyyrt": "https://cdn.discordapp.com/attachments/700683544103747594/711226618919780359/pal_tyyrt.png",
                "Kehnor": "https://cdn.discordapp.com/attachments/700683544103747594/711226614767419432/kehnor.png",
                "Gendol Ethor": "https://cdn.discordapp.com/attachments/700683544103747594/711226611608977490/gendol_ethor.png",
                "Korr Bekkt": "https://cdn.discordapp.com/attachments/700683544103747594/711226617254510602/korr_bekkt.png",
                "Hongar Meton": "https://cdn.discordapp.com/attachments/700683544103747594/711226613278441543/hongar_meton.png",
                "Trent Jameson": "https://cdn.discordapp.com/attachments/700683544103747594/711226622195269632/trent_jameson.png",
                "Qyrr Myfft": "https://cdn.discordapp.com/attachments/700683544103747594/711226620786114590/qyrr_myfft.png",

                # Midorian
                "Toma Prakupy": "https://cdn.discordapp.com/attachments/700683544103747594/711226704953344060/toma_prakupy.png",
                "Nombur Telénah": "https://cdn.discordapp.com/attachments/700683544103747594/711226703703310397/nombur_talenah.png",
                "Bartholomeu Drew": "https://cdn.discordapp.com/attachments/700683544103747594/711226697974022204/bartholomeu_drew.png",
                "Doni Trillyx": "https://cdn.discordapp.com/attachments/700683544103747594/711226699119067217/doni_trillyx.png",
                "Heinrich Wickel": "https://cdn.discordapp.com/attachments/700683544103747594/711226700305793085/heinrich_wickel.png",
                "Mashon Redal": "https://cdn.discordapp.com/attachments/700683544103747594/711226702122057768/mashon_redal.png",

                # Vossk
                "Mrrkt Nimkk": "https://cdn.discordapp.com/attachments/700683544103747594/711226820854284368/mrrkt_minkk.png",
                "Alvar Julen": "https://cdn.discordapp.com/attachments/700683544103747594/711226819461775360/alvar_julen.png",
                "Vortt Baskk": "https://cdn.discordapp.com/attachments/700683544103747594/711226826831298710/vortt_baskk.png",
                "Oluchi Erland": "https://cdn.discordapp.com/attachments/700683544103747594/711226822540394546/oluchi_erland.png",
                "Orp Tsam": "https://cdn.discordapp.com/attachments/700683544103747594/711226823966720041/orp_tsam.png",
                "Urr Sekant": "https://cdn.discordapp.com/attachments/700683544103747594/711226825488990258/urr_sakant.png",

                # Nivelian
                "Borsul Tarand": "https://cdn.discordapp.com/attachments/700683544103747594/711226764948537374/borsul_tarand.png",
                "Malon Sentendar": "https://cdn.discordapp.com/attachments/700683544103747594/711226767939207178/malon_sentendar.png",
                "Vilhelm Lindon": "https://cdn.discordapp.com/attachments/700683544103747594/711226772812726302/vilhelm_lindon.png",
                "Tamir Prakupy": "https://cdn.discordapp.com/attachments/700683544103747594/711226770707185664/tamir_prakupy.png",
                "Merson Surr": "https://cdn.discordapp.com/attachments/700683544103747594/711226769327521872/merson_surr.png",
                "Ganfor Kant": "https://cdn.discordapp.com/attachments/700683544103747594/711226766630584370/ganfor_kant.png"}

# find the length of the longest criminal name, to be used in padding during cmd_bounties
longestBountyNameLength = 0
for fac in bountyNames:
    for name in bountyNames[fac]:
        if len(name) > longestBountyNameLength:
            longestBountyNameLength = len(name)

# levels of security in bbSystems (bbSystem security is stored as an index in this list)
securityLevels = ["secure", "average", "risky", "dangerous"]

# map image URLS for cmd_map
mapImageWithGraphLink = "https://cdn.discordapp.com/attachments/700683544103747594/700683693215318076/gof2_coords.png"
mapImageNoGraphLink = 'https://i.imgur.com/TmPgPd3.png'

# intro for help commands
helpIntro = "**[Square brackets]** indicate *optional* arguments, **<angled brackets>** indicate *required* arguments.\n"

# icons for factions
terranIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013574331596850/terran.png"
vosskIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013681621893130/vossk.png"
midorianIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013601019691038/midorian.png"
nivelianIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013623257890857/nivelian.png"
neutralIcon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/248/rocket_1f680.png"
voidIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013699841687602/void.png"
errorIcon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/248/exclamation-mark_2757.png"
winIcon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/248/trophy_1f3c6.png"
rocketIcon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/248/rocket_1f680.png"

# list associating faction names with icons
factionIcons = {"terran":terranIcon, "vossk":vosskIcon, "midorian":midorianIcon, "nivelian":nivelianIcon, "neutral":neutralIcon}

# colours to use in faction-related embed strips
factionColours = {"terran":Colour.gold(), "vossk":Colour.dark_green(), "midorian":Colour.dark_red(), "nivelian":Colour.dark_blue(), "neutral":Colour.purple()}

# Data representing all ship items in the game. These are used to create bbShip objects, which are stored in builtInShipObjs in a similar dict format.
# Ships to not have tech levels in GOF2, so tech levels will be automaticaly generated for the sake of the bot during bbConfig package init.
builtInShipData = {}

for subdir, dirs, files in os.walk(shipsDir):
    for dirname in dirs:
        dirpath = subdir + os.sep + dirname

        if dirname.lower().endswith(".bbship"):
            with open(dirpath + os.sep + "META.json", "r") as f:
                currentShipData = json.loads(f.read())
                currentShipData["path"] = CWD + os.sep + dirpath
                if "skinnable" not in currentShipData or "model" not in currentShipData:
                    currentShipData["skinnable"] = False
                builtInShipData[currentShipData["name"]] = currentShipData

                if "compatibleSkins" not in currentShipData:
                    currentShipData["compatibleSkins"] = []


# Objects representing all ship skins in the game.
builtInShipSkins = {}




# Old Hardcoded version
"""builtInShipData = {# Terran
                    "Inflict": {"name": "Inflict", "manufacturer": "terran", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 4, "armour": 150, "cargo": 45, "numSecondaries": 1, "handling": 125, "value": 30900, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Inflict", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694046057824296/inflict.png", "emoji":"<:inflict:723705238091202650>"},
                    "Furious": {"name": "Furious", "manufacturer": "terran", "maxPrimaries": 1, "maxTurrets": 1, "maxModules": 6, "armour": 176, "cargo": 108, "numSecondaries": 2, "handling": 112, "value": 75800, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Furious", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694028752126162/furious.png", "emoji":"<:furious:723705236958609520>"},
                    "Taipan": {"name": "Taipan", "manufacturer": "terran", "maxPrimaries": 3, "maxTurrets": 0, "maxModules": 5, "armour": 176, "cargo": 50, "numSecondaries": 2, "handling": 113, "value": 100100, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Taipan", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694066626691082/taipan.png", "emoji":"<:taipan:723705237088501781>"},
                    "Hera": {"name": "Hera", "manufacturer": "terran", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 7, "armour": 152, "cargo": 64, "numSecondaries": 2, "handling": 108, "value": 107000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Hera", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694040021958749/hera.png", "emoji":"<:hera:723705237285896222>"},
                    "Teneta": {"name": "Teneta", "manufacturer": "terran", "maxPrimaries": 2, "maxTurrets": 1, "maxModules": 7, "armour": 192, "cargo": 65, "numSecondaries": 4, "handling": 105, "value": 125400, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Teneta", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694071647141968/teneta.png", "emoji":"<:teneta:723705237281439744>"},
                    "Cormorant": {"name": "Cormorant", "manufacturer": "terran", "maxPrimaries": 0, "maxTurrets": 1, "maxModules": 8, "armour": 200, "cargo": 350, "numSecondaries": 4, "handling": 45, "value": 168900, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Cormorant", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694018580938812/cormorant.png", "emoji":"<:cormorant:723705236241514557>"},
                    "Anaan": {"name": "Anaan", "manufacturer": "terran", "maxPrimaries": 2, "maxTurrets": 1, "maxModules": 7, "armour": 220, "cargo": 240, "numSecondaries": 1, "handling": 65, "value": 176900, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Anaan", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694009571573820/anaan.png", "emoji":"<:anaan:723705236304166922>"},
                    "Groza": {"name": "Groza", "manufacturer": "terran", "maxPrimaries": 3, "maxTurrets": 0, "maxModules": 8, "armour": 160, "cargo": 130, "numSecondaries": 3, "handling": 117, "value": 251600, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Groza", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694034305253447/groza.png", "emoji":"<:groza:723705237038432258>"},
                    "Razor 6": {"name": "Razor 6", "manufacturer": "terran", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 6, "armour": 135, "cargo": 60, "numSecondaries": 1, "handling": 130, "value": 294900, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Razor_6", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694059517345985/razor_6.png", "emoji":"<:razor6:723705237340160071>"},
                    "Phantom": {"name": "Phantom", "manufacturer": "terran", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 9, "armour": 200, "cargo": 52, "numSecondaries": 1, "handling": 150, "value": 1450000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Phantom", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694051963142215/phantom.png", "emoji":"<:phantom:723705237281701968>"},
                    "Ward": {"name": "Ward", "manufacturer": "terran", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 10, "armour": 145, "cargo": 65, "numSecondaries": 2, "handling": 95, "value": 1654800, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Ward", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694086897500220/ward.png", "emoji":"<:ward:723705236845232141>"},
                    "Gryphon": {"name": "Gryphon", "manufacturer": "terran", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 10, "armour": 220, "cargo": 90, "numSecondaries": 2, "handling": 130, "value": 2100000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Gryphon", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720783815328399399/gryphon.png", "emoji":"<:gryphon:723705237264924713>"},
                    "Veteran": {"name": "Veteran", "manufacturer": "terran", "maxPrimaries": 3, "maxTurrets": 1, "maxModules": 12, "armour": 200, "cargo": 110, "numSecondaries": 4, "handling": 92, "value": 2488400, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Veteran", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694081897889793/veteran.png", "emoji":"<:veteran:723705237231239219>"},
                    "Dark Angel": {"name": "Dark Angel", "manufacturer": "terran", "maxPrimaries": 4, "maxTurrets": 1, "maxModules": 14, "armour": 350, "cargo": 85, "numSecondaries": 2, "handling": 125, "value": 7227000, "aliases": ["Dark", "Angel", "DarkAngel"], "wiki": "https://galaxyonfire.fandom.com/wiki/Dark_Angel", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720783955455901775/dark_angel.png", "emoji":"<:darkangel:723705236492910723>"},
                    "Rhino": {"name": "Rhino", "manufacturer": "terran", "maxPrimaries": 0, "maxTurrets": 1, "maxModules": 9, "armour": 1200, "cargo": 480, "numSecondaries": 2, "handling": 30, "value": 700000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Rhino", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720784079750168615/rhino.png", "emoji":"<:rhino:723705236937506828>"},
                    
                    # Vossk
                    "H'Soc": {"name": "H'Soc", "manufacturer": "vossk", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 7, "armour": 210, "cargo": 45, "numSecondaries": 2, "handling": 140, "value": 150000, "aliases": ["Soc", "HSoc"], "wiki": "https://galaxyonfire.fandom.com/wiki/H%27Soc", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694188659966022/hsoc.png", "emoji":"<:hsoc:723705306684588043>"},
                    "N'Tirrk": {"name": "N'Tirrk", "manufacturer": "vossk", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 8, "armour": 280, "cargo": 80, "numSecondaries": 4, "handling": 128, "value": 250000, "aliases": ["Tirrk", "NTirrk"], "wiki": "https://galaxyonfire.fandom.com/wiki/N%27Tirrk", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720784330632200322/ntirrk.png", "emoji":"<:ntirrk:723705307078983700>"},
                    "K'Suuk": {"name": "K'Suuk", "manufacturer": "vossk", "maxPrimaries": 3, "maxTurrets": 0, "maxModules": 12, "armour": 255, "cargo": 55, "numSecondaries": 2, "handling": 125, "value": 1950000, "aliases": ["Suuk", "KSuuk"], "wiki": "https://galaxyonfire.fandom.com/wiki/K%27Suukk", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694205990568055/ksuukk.png", "emoji":"<:ksuukk:723705306827194449>"},
                    "S'Kanarr": {"name": "S'Kanarr", "manufacturer": "vossk", "maxPrimaries": 4, "maxTurrets": 1, "maxModules": 11, "armour": 315, "cargo": 150, "numSecondaries": 2, "handling": 70, "value": 7250000, "aliases": ["Kanarr", "SKanarr"], "wiki": "https://galaxyonfire.fandom.com/wiki/S%27Kanarr", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694223308980314/skanarr.png", "emoji":"<:skanarr:723705306722467852>"},
                    "Na'Srrk": {"name": "Na'Srrk", "manufacturer": "vossk", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 12, "armour": 280, "cargo": 70, "numSecondaries": 4, "handling": 145, "value": 5400000, "aliases": ["srrk", "Nasrrk"], "wiki": "https://galaxyonfire.fandom.com/wiki/Na%27srrk", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720785069672890408/nasrrk.png", "emoji":"<:nasrrk:723705306894565407>"},
                    
                    # Nivelian
                    "Night Owl": {"name": "Night Owl", "manufacturer": "nivelian", "maxPrimaries": 1, "maxTurrets": 0, "maxModules": 4, "armour": 125, "cargo": 40, "numSecondaries": 2, "handling": 150, "value": 26500, "aliases": ["Night", "Owl", "NightOwl"], "wiki": "https://galaxyonfire.fandom.com/wiki/Night_Owl", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693855728697445/night_owl.png", "emoji":"<:nightowl:723705339639365662>"},
                    "Type 43": {"name": "Type 43", "manufacturer": "nivelian", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 6, "armour": 175, "cargo": 30, "numSecondaries": 3, "handling": 132, "value": 72500, "aliases": ["Type", "43", "Type43"], "wiki": "https://galaxyonfire.fandom.com/wiki/Type_43", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693873512546404/type_43.png", "emoji":"<:type43:723705339345764433>"},
                    "Salvéhn": {"name": "Salvéhn", "manufacturer": "nivelian", "maxPrimaries": 2, "maxTurrets": 1, "maxModules": 6, "armour": 156, "cargo": 110, "numSecondaries": 1, "handling": 102, "value": 94500, "aliases": ["Salvehn"], "wiki": "https://galaxyonfire.fandom.com/wiki/Salvéhn", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693866533093526/salvehn.png", "emoji":"<:salvehn:723705339547090964>"},
                    "Hatsuyuki": {"name": "Hatsuyuki", "manufacturer": "nivelian", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 8, "armour": 115, "cargo": 28, "numSecondaries": 2, "handling": 145, "value": 171900, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Hatsuyuki", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693848577409145/hatsuyuki.png", "emoji":"<:hatsuyuki:723705339521925210>"},
                    "Dace": {"name": "Dace", "manufacturer": "nivelian", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 5, "armour": 170, "cargo": 38, "numSecondaries": 1, "handling": 162, "value": 235600, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Dace", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693815752523796/dace.png", "emoji":"<:dace:723705338968277038>"},
                    "Wraith": {"name": "Wraith", "manufacturer": "nivelian", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 9, "armour": 180, "cargo": 65, "numSecondaries": 2, "handling": 140, "value": 1750000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Wraith", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693879891951636/wraith.png", "emoji":"<:wraith:723705339706474576>"},
                    "Kinzer": {"name": "Kinzer", "manufacturer": "nivelian", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 10, "armour": 180, "cargo": 45, "numSecondaries": 4, "handling": 120, "value": 2128000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Kinzer", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720785556925317140/kinzer.png", "emoji":"<:kinzer:723705339522056342>"},
                    "Aegir": {"name": "Aegir", "manufacturer": "nivelian", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 11, "armour": 190, "cargo": 70, "numSecondaries": 4, "handling": 100, "value": 2712900, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Aegir", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693803932975135/aegir.png", "emoji":"<:aegir:723705338683195463>"},
                    "Ghost": {"name": "Ghost", "manufacturer": "nivelian", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 14, "armour": 530, "cargo": 50, "numSecondaries": 2, "handling": 135, "value": 6000000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Ghost", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720785665402601522/ghost.png", "emoji":"<:ghost:723705339282718792>"},
                    "Scimitar": {"name": "Scimitar", "manufacturer": "nivelian", "maxPrimaries": 3, "maxTurrets": 0, "maxModules": 15, "armour": 400, "cargo": 40, "numSecondaries": 2, "handling": 104, "value": 5800000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Scimitar", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720785793337262180/scimitar.png", "emoji":"<:scimitar:723705339262009355>"},
                    "Specter": {"name": "Specter", "manufacturer": "nivelian", "maxPrimaries": 4, "maxTurrets": 0, "modules": [{"name":"U'tool", "builtIn":True}],"maxModules": 16, "armour": 800, "cargo": 65, "numSecondaries": 2, "handling": 138, "value": 30000000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Specter", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720785904540581989/specter.png", "emoji":"<:specter:723705339563868160>"},
                    
                    # Midorian
                    "Betty": {"name": "Betty", "manufacturer": "midorian", "maxPrimaries": 1, "maxTurrets": 0, "maxModules": 3, "armour": 95, "cargo": 25, "numSecondaries": 1, "handling": 120, "value": 16038, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Betty", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693735158972476/betty.png", "emoji":"<:betty:723705372606726155>"},
                    "Hector": {"name": "Hector", "manufacturer": "midorian", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 5, "armour": 105, "cargo": 42, "numSecondaries": 1, "handling": 148, "value": 38016, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Hector", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693749134655528/hector.png", "emoji":"<:hector:723705373017767976>"},
                    "Badger": {"name": "Badger", "manufacturer": "midorian", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 5, "armour": 135, "cargo": 55, "numSecondaries": 2, "handling": 112, "value": 38709, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Badger", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693707795595284/badger.png", "emoji":"<:badger:723705372786950174>"},
                    "Cicero": {"name": "Cicero", "manufacturer": "midorian", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 6, "armour": 125, "cargo": 25, "numSecondaries": 1, "handling": 155, "value": 51975, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Cicero", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693741052231821/cicero.png", "emoji":"<:cicero:723705373109780530>"},
                    "Berger CrossXT": {"name": "Berger CrossXT", "manufacturer": "midorian", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 6, "armour": 165, "cargo": 45, "numSecondaries": 2, "handling": 128, "value": 87318, "aliases": ["CrossXT", "Cross XT", "Berger XT", "BergerCrossXT", "Berger Cross XT", "BergerCross XT", "🍔"], "wiki": "https://galaxyonfire.fandom.com/wiki/Berger_CrossXT", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693724694184136/berger_crossxt.png", "emoji":"<:bergercrossxt:723705372657057815>"},
                    "Nuyang II": {"name": "Nuyang II", "manufacturer": "midorian", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 9, "armour": 225, "cargo": 105, "numSecondaries": 2, "handling": 90, "value": 930303, "aliases": ["Nuyang", "NuyangII", "Nuyang2", "Nuyang 2"], "wiki": "https://galaxyonfire.fandom.com/wiki/Nuyang_II", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693758605393980/nuyang_ii.png", "emoji":"<:nuyangii:723705373063774338>"},
                    
                    # Pirate
                    "Wasp": {"name": "Wasp", "manufacturer": "pirate", "maxPrimaries": 1, "maxTurrets": 0, "maxModules": 3, "armour": 100, "cargo": 30, "numSecondaries": 1, "handling": 160, "value": 19500, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Wasp", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693960422719558/wasp.png", "emoji":"<:wasp:723706166450061493>"},
                    "Hiro": {"name": "Hiro", "manufacturer": "pirate", "maxPrimaries": 1, "maxTurrets": 0, "maxModules": 4, "armour": 160, "cargo": 52, "numSecondaries": 2, "handling": 150, "value": 32600, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Hiro", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693933042303046/hiro.png", "emoji":"<:hiro:723706166231957504>"},
                    "Azov": {"name": "Azov", "manufacturer": "pirate", "maxPrimaries": 2, "maxTurrets": 1, "maxModules": 5, "armour": 150, "cargo": 55, "numSecondaries": 2, "handling": 128, "value": 61900, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Azov", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693920509460531/azov.png", "emoji":"<:azov:723706166059728936>"},
                    "Tyrion": {"name": "Tyrion", "manufacturer": "pirate", "maxPrimaries": 1, "maxTurrets": 0, "maxModules": 9, "armour": 155, "cargo": 52, "numSecondaries": 4, "handling": 145, "value": 316400, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Tyrion", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693949009887392/tyrion.png", "emoji":"<:tyrion:723706166038888460>"},
                    "Hernstein": {"name": "Hernstein", "manufacturer": "pirate", "maxPrimaries": 2, "maxTurrets": 1, "maxModules": 8, "armour": 210, "cargo": 180, "numSecondaries": 2, "handling": 75, "value": 327800, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Hernstein", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693928273117294/hernstein.png", "emoji":"<:hernstein:723706166148071486>"},
                    "Velasco": {"name": "Velasco", "manufacturer": "pirate", "maxPrimaries": 3, "maxTurrets": 1, "maxModules": 8, "armour": 170, "cargo": 95, "numSecondaries": 2, "handling": 125, "value": 684300, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Velasco", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693956186210304/velasco.png", "emoji":"<:velasco:723706166428958730>"},
                    "Mantis": {"name": "Mantis", "manufacturer": "pirate", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 12, "armour": 240, "cargo": 75, "numSecondaries": 4, "handling": 117, "value": 4136800, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Mantis", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693938536841247/mantis.png", "emoji":"<:mantis:723706166307192892>"},
                    
                    # Grey
                    "Vol Noor": {"name": "Vol Noor", "manufacturer": "grey", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 7, "armour": 165, "cargo": 75, "numSecondaries": 2, "handling": 110, "value": 105000, "aliases": ["Vol", "Noor", "VolNoor"], "wiki": "https://galaxyonfire.fandom.com/wiki/Vol_Noor", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693658877165598/vol_noor.png", "emoji":"<:volnoor:723705970529796157>"},
                    
                    # Void
                    "VoidX": {"name": "VoidX", "manufacturer": "void", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 15, "armour": 450, "cargo": 30, "numSecondaries": 4, "handling": 155, "value": 8115900, "aliases": ["Void", "X", "Void X"], "wiki": "https://galaxyonfire.fandom.com/wiki/VoidX", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694144158138418/voidx.png", "emoji":"<:voidx:723706193096212510>"},
                    
                    # Deep Science
                    "Cronus": {"name": "Cronus", "manufacturer": "deep science", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 7, "armour": 190, "cargo": 95, "numSecondaries": 2, "handling": 120, "value": 1200000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Cronus", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693576509554818/cronus.png", "emoji":"<:cronus:723705945074434200>"},
                    "Typhon": {"name": "Typhon", "manufacturer": "deep science", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 12, "armour": 175, "cargo": 40, "numSecondaries": 0, "handling": 145, "value": 2500000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Typhon", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693603428728862/typhon.png", "emoji":"<:typhon:723705945305382983>"},
                    "Nemesis": {"name": "Nemesis", "manufacturer": "deep science", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 14, "armour": 235, "cargo": 105, "numSecondaries": 1, "handling": 95, "value": 6800000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Nemesis_(ship)", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693589973270603/nemesis.png", "emoji":"<:nemesis:723705945192005643>"},
                    
                    # Most Wanted
                    "Blue Fyre": {"name": "Blue Fyre", "manufacturer": "most wanted", "maxPrimaries": 3, "maxTurrets": 0, "maxModules": 13, "armour": 270, "cargo": 125, "numSecondaries": 3, "handling": 116, "value": 4455000, "aliases": ["Blue", "Fyre", "BlueFyre", "Blue Fire", "BlueFire"], "wiki": "https://galaxyonfire.fandom.com/wiki/Blue_Fyre", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720787143596834816/blue_fyre.png", "emoji":"<:bluefyre:723706134430744577>"},
                    "Gator Custom": {"name": "Gator Custom", "manufacturer": "most wanted", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 12, "armour": 335, "cargo": 320, "numSecondaries": 2, "handling": 95, "value": 5148000, "aliases": ["Gator", "Custom", "GatorCustom"], "wiki": "https://galaxyonfire.fandom.com/wiki/Gator_Custom", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720787254632644608/gator_custom.png", "emoji":"<:gatorcustom:723706134401384498>"},
                    "Amboss": {"name": "Amboss", "manufacturer": "most wanted", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 14, "armour": 305, "cargo": 80, "numSecondaries": 4, "handling": 110, "value": 6732000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Amboss", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720786108773826640/amboss.png", "emoji":"<:amboss:723706134271098881>"},
                    "Bloodstar": {"name": "Bloodstar", "manufacturer": "most wanted", "maxPrimaries": 4, "maxTurrets": 1, "maxModules": 14, "armour": 460, "cargo": 180, "numSecondaries": 4, "handling": 88, "value": 13365000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Bloodstar", "builtIn":False, "icon": "https://cdn.discordapp.com/attachments/700683544103747594/720786243725688832/bloodstar.png", "emoji":"<:bloodstar:723706134032023553>"},
                    
                    # Kaamo Club
                    "Groza Mk II": {"name": "Groza Mk II", "manufacturer": "kaamo club", "maxPrimaries": 5, "maxTurrets": 0, "maxModules": 11, "armour": 450, "cargo": 90, "numSecondaries": 1, "handling": 122, "value": 7130000, "aliases": ["Groza Mk 2", "Groza Mark 2", "Groza Mark II", "Groza MkII", "Groza Mk2", "Groza Mk.2", "Groza Mk. II"], "wiki": "https://galaxyonfire.fandom.com/wiki/Groza_Mk_II", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720787464901361670/groza_mk_ii.png", "emoji":"<:grozamkii:723705998954594356>"},
                    "Darkzov": {"name": "Darkzov", "manufacturer": "kaamo club", "maxPrimaries": 4, "maxTurrets": 1, "maxModules": 14, "armour": 420, "cargo": 70, "numSecondaries": 1, "handling": 130, "value": 7236000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Darkzov", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720786415679569950/darkzov.png", "emoji":"<:darkzov:723705999030091816>"},
                    "Berger Cross Special": {"name": "Berger Cross Special", "manufacturer": "kaamo club", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 14, "armour": 410, "cargo": 55, "numSecondaries": 4, "handling": 130, "value": 7335900, "aliases": ["Berger Cross Special", "Berger Special", "Cross Special"], "wiki": "https://galaxyonfire.fandom.com/wiki/Berger_Cross_Special", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720787569541120010/berger_cross_special.png", "emoji":"<:bergercrossspecial:723705998665056287>"},
                    "Phantom XT": {"name": "Phantom XT", "manufacturer": "kaamo club", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 14, "armour": 425, "cargo": 60, "numSecondaries": 1, "handling": 150, "value": 7430000, "aliases": ["PhantomXT"], "wiki": "https://galaxyonfire.fandom.com/wiki/Phantom_XT", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720787685035212830/phantom_xt.png", "emoji":"<:phantomxt:723705998660862064>"},
                    "Teneta R.E.D.": {"name": "Teneta R.E.D.", "manufacturer": "kaamo club", "maxPrimaries": 4, "maxTurrets": 1, "maxModules": 13, "armour": 545, "cargo": 70, "numSecondaries": 2, "handling": 117, "value": 7610000, "aliases": ["Teneta RED", "Teneta R.E.D"], "wiki": "https://galaxyonfire.fandom.com/wiki/Teneta_R.E.D.", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720787774328012840/teneta_r.e.d..png", "emoji":"<:tenetared:723705999277686814>"},
                    "Kinzer RS": {"name": "Kinzer RS", "manufacturer": "kaamo club", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 15, "armour": 420, "cargo": 65, "numSecondaries": 4, "handling": 125, "value": 8930000, "aliases": ["KinzerRS"], "wiki": "https://galaxyonfire.fandom.com/wiki/Kinzer_RS", "builtIn":False, "icon": "https://cdn.discordapp.com/attachments/700683544103747594/720787863171629056/kinzer_rs.png", "emoji":"<:kinzerrs:723705998723907615>"}}
"""

# Data representing all module items in the game. These are used to create bbModule objects, which are stored in builtInModuleObjs in a similar dict format.
builtInModuleData = {   # armour
                        "E2 Exoclad": {"type": "armour", "name": "E2 Exoclad", "aliases": ["E2", "Exoclad", "Exoclad E2"], "techLevel": 1, "armour": 40, "value": 1070, "wiki": "https://galaxyonfire.fandom.com/wiki/E2_Exoclad", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474328687214612/e2_exoclad.png", "emoji": "<:e2exoclad:723706394716536842>"},
                        "E4 Ultra Lamina": {"type": "armour", "name": "E4 Ultra Lamina", "aliases": ["E4", "Lamina", "E4 Ultra", "E4 Lamina", "Ultra Lamina"], "techLevel": 3, "armour": 80, "value": 4705, "wiki": "https://galaxyonfire.fandom.com/wiki/E4_Ultra_Lamina", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474339860840468/e4_ultra_lamina.png", "emoji": "<:e4ultralamina:723706394485719121>"},
                        "E6 D-X Plating": {"type": "armour", "name": "E6 D-X Plating", "aliases": ["E6", "D-X Plating", "E6 Plating", "E6 D-X"], "techLevel": 5, "armour": 110, "value": 20171, "wiki": "https://galaxyonfire.fandom.com/wiki/E6_D-X_Plating", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474351587983360/e6_d-x_plating.png", "emoji": "<:e6dxplating:723706394775257168>"},
                        "D'iol": {"type": "armour", "name": "D'iol", "aliases": ["Diol"], "techLevel": 7, "armour": 160, "value": 51449, "wiki": "https://galaxyonfire.fandom.com/wiki/D%27iol", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474213247385610/diol.png", "emoji": "<:diol:723706394687307803>"},
                        "T'yol": {"type": "armour", "name": "T'yol", "aliases": ["Tyol"], "techLevel": 10, "armour": 250, "value": 117922, "wiki": "https://galaxyonfire.fandom.com/wiki/T%27yol", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474361549324389/tyol.png", "emoji": "<:tyol:723706394821525595>"},
                        
                        # boosters
                        "Linear Boost": {"type": "booster", "name": "Linear Boost", "aliases": ["Linear"], "techLevel": 4, "effect": 1.6, "duration": 3, "value": 5704, "wiki": "https://galaxyonfire.fandom.com/wiki/Linear_Boost", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474553577406504/linear_boost.png", "emoji": "<:linearboost:723706427381907526>"},
                        "Cyclotron Boost": {"type": "booster", "name": "Cyclotron Boost", "aliases": ["Cyclotron"], "techLevel": 5, "effect": 1.8, "duration": 4.4, "value": 11553, "wiki": "https://galaxyonfire.fandom.com/wiki/Cyclotron_Boost", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474544479698965/cyclotron_boost.png", "emoji": "<:cyclotronboost:723706427448754178>"},
                        "Synchrotron Boost": {"type": "booster", "name": "Synchrotron Boost", "aliases": ["Synchrotron"], "techLevel": 7, "effect": 2.6, "duration": 5.6, "value": 22373, "wiki": "https://galaxyonfire.fandom.com/wiki/Synchrotron_Boost", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474582463578112/synchrotron_boost.png", "emoji": "<:synchrotronboost:723706427390033942>"},
                        "Me'al": {"type": "booster", "name": "Me'al", "aliases": ["Meal"], "techLevel": 7, "effect": 3, "duration": 7, "value": 46897, "wiki": "https://galaxyonfire.fandom.com/wiki/Me%27al", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474564637655040/meal.png", "emoji": "<:meal:723706427260141629>"},
                        "Polytron Boost": {"type": "booster", "name": "Polytron Boost", "aliases": ["Polytron"], "techLevel": 8, "effect": 4, "duration": 6, "value": 86815, "wiki": "https://galaxyonfire.fandom.com/wiki/Polytron_Boost", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474574234222642/polytron_boost.png", "emoji": "<:polytronboost:723706427251752991>"},
                        
                        # cabins
                        "Small Cabin": {"type": "cabin", "name": "Small Cabin", "aliases": [], "techLevel": 3, "cabinSize": 3, "value": 3170, "wiki": "https://galaxyonfire.fandom.com/wiki/Small_Cabin", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474647152328774/small_cabin.png", "emoji": "<:smallcabin:723706495426101268>"},
                        "Medium Cabin": {"type": "cabin", "name": "Medium Cabin", "aliases": [], "techLevel": 6, "cabinSize": 5, "value": 6347, "wiki": "https://galaxyonfire.fandom.com/wiki/Medium_Cabin", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474636641140736/medium_cabin.png", "emoji": "<:mediumcabin:723706494918590475>"},
                        "Large Cabin": {"type": "cabin", "name": "Large Cabin", "aliases": [], "techLevel": 7, "cabinSize": 10, "value": 14190, "wiki": "https://galaxyonfire.fandom.com/wiki/Large_Cabin", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474628512579664/large_cabin.png", "emoji": "<:largecabin:723706494801149973>"},

                        # cloaks
                        "U'tool": {"type": "cloak", "name": "U'tool", "aliases": ["Utool"], "techLevel": 6, "duration":10, "value": 47367, "wiki": "https://galaxyonfire.fandom.com/wiki/U%27tool", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474706182832139/utool.png", "emoji": "<:utool:723706519379509249>"},
                        "Sight Suppressor II": {"type": "cloak", "name": "Sight Suppressor II", "aliases": ["Sight Suppressor 2", "Sight 2", "Suppressor II", "Suppressor II"], "techLevel": 4, "duration":20, "value": 29599, "wiki": "https://galaxyonfire.fandom.com/wiki/Sight_Suppressor_II", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474695336493136/sight_suppressor_ii.png", "emoji": "<:sightsuppressorii:723706519383703662>"},
                        "Yin Co. Shadow Ninja": {"type": "cloak", "name": "Yin Co. Shadow Ninja", "aliases": ["Shadow Ninja", "Yin", "Yin Co Shadow Ninja"], "techLevel": 10, "duration":40, "value": 69183, "wiki": "https://galaxyonfire.fandom.com/wiki/Yin_Co._Shadow_Ninja", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474714982613052/yin_co._shadow_ninja.png", "emoji": "<:yinco:723706519484497931>"},

                        # compressors
                        "ZMI Optistore": {"type": "compressor", "name": "ZMI Optistore", "aliases": ["Optistore"], "techLevel": 1, "cargoMultiplier":1.15, "value": 2576, "wiki": "https://galaxyonfire.fandom.com/wiki/ZMI_Optistore", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474790828212254/zmi_optistore.png", "emoji": "<:zmioptistore:723706540975980628>"},
                        "Autopacker 2": {"type": "compressor", "name": "Autopacker 2", "aliases": ["Autopacker"], "techLevel": 3, "cargoMultiplier":1.25, "value": 5747, "wiki": "https://galaxyonfire.fandom.com/wiki/Autopacker_2", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474748327198731/autopacker_2.png", "emoji": "<:autopacker2:723706540825116743>"},
                        "Ultracompact": {"type": "compressor", "name": "Ultracompact", "aliases": [], "techLevel": 5, "cargoMultiplier":1.4, "value": 14992, "wiki": "https://galaxyonfire.fandom.com/wiki/Ultracompact", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474776039096350/ultracompact.png", "emoji": "<:ultracompact:723706540971786272>"},
                        "Shrinker BT": {"type": "compressor", "name": "Shrinker BT", "aliases": ["Shrinker", "BT"], "techLevel": 7, "cargoMultiplier":1.75, "value": 28571, "wiki": "https://galaxyonfire.fandom.com/wiki/Shrinker_BT", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474766161379360/shrinker_bt.png", "emoji": "<:shrinkerbt:723706541236158505>"},
                        "Rhoda Blackhole": {"type": "compressor", "name": "Rhoda Blackhole", "aliases": ["Blackhole", "Black Hole", "Rhoda Black Hole"], "techLevel": 9, "cargoMultiplier":2, "value": 66305, "wiki": "https://galaxyonfire.fandom.com/wiki/Rhoda_Blackhole", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723474756875190342/rhoda_blackhole.png", "emoji": "<:rhodablackhole:723706541160792184>"},
                        
                        # gamma shields
                        "Gamma Shield I": {"type": "gamma shield", "name": "Gamma Shield I", "aliases": ["Gamma Shield 1", "Gamma I", "Gamma 1"], "techLevel": 8, "value": 27526, "wiki": "https://galaxyonfire.fandom.com/wiki/Gamma_Shield_I", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475048848949249/gamma_shield_i.png", "emoji": "<:gammashieldi:723706563096871004>"},
                        "Gamma Shield II": {"type": "gamma shield", "name": "Gamma Shield II", "aliases": ["Gamma Shield 2", "Gamma 2", "Gamma II"], "techLevel": 8, "value": 43202, "wiki": "https://galaxyonfire.fandom.com/wiki/Gamma_Shield_II", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475058739380244/gamma_shield_ii.png", "emoji": "<:gammashieldii:723706563558113392>"},

                        # mining drills
                        "IMT Extract 1.3": {"type": "mining drill", "name": "IMT Extract 1.3", "aliases": ["IMT 1.3", "Extract 1.3"], "techLevel": 2, "oreYield": 0.6, "handling": 0.3, "value": 4347, "wiki": "https://galaxyonfire.fandom.com/wiki/IMT_Extract_1.3", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475162808188948/imt_extract_1.3.png", "emoji": "<:imtextract1:723706605258145934>"},
                        "IMT Extract 2.7": {"type": "mining drill", "name": "IMT Extract 2.7", "aliases": ["IMT 2.7", "Extract 2.7"], "techLevel": 4, "oreYield": 0.5, "handling": 0.5, "value": 17297, "wiki": "https://galaxyonfire.fandom.com/wiki/IMT_Extract_2.7", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475171607969822/imt_extract_2.7.png", "emoji": "<:imtextract2:723706605887291413>"},
                        "K'yuul": {"type": "mining drill", "name": "K'yuul", "aliases": ["Kyuul"], "techLevel": 5, "oreYield": 0.4, "handling": 0.8, "value": 37743, "wiki": "https://galaxyonfire.fandom.com/wiki/K%27yuul", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475197159538698/kyuul.png", "emoji": "<:kyuul:723706605660667967>"},
                        "IMT Extract 4.0X": {"type": "mining drill", "name": "IMT Extract 4.0X", "aliases": ["IMT Extract 4", "IMT 4.0X", "IMT 4", "Extract 4.0X", "Extract 4"], "techLevel": 7, "oreYield": 0.8, "handling": 0.7, "value": 73093, "wiki": "https://galaxyonfire.fandom.com/wiki/IMT_Extract_4.0X", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475184203464714/imt_extract_4.0x.png", "emoji": "<:imtextract4:723706605970915339>"},
                        "Gunant's Drill": {"type": "mining drill", "name": "Gunant's Drill", "aliases": ["Gunant's", "Gunants", "Gunants Drill"], "techLevel": 10, "oreYield": 10, "handling": 1, "value": 209353, "wiki": "https://galaxyonfire.fandom.com/wiki/Gunant%27s_Drill", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475153631182909/gunants_drill.png", "emoji": "<:gunantsdrill:723706605572718612>"},

                        # repair beams
                        "Nirai SPP-C1": {"type": "repair beam", "name": "Nirai SPP-C1", "aliases": ["SPP-C1", "Nirai C1"], "techLevel": 8, "value": 68336, "wiki": "https://galaxyonfire.fandom.com/wiki/Nirai_SPP-C1", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475264281247774/nirai_spp-c1.png", "emoji": "<:niraisppc1:723706682605043723>"},
                        "Nirai SPP-M50": {"type": "repair beam", "name": "Nirai SPP-M50", "aliases": ["SPP-M50", "Nirai M50"], "techLevel": 8, "value": 365681, "wiki": "https://galaxyonfire.fandom.com/wiki/Nirai_SPP-M50", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475273772826654/nirai_spp-m50.png", "emoji": "<:niraisppm50:723706682278150340>"},

                        # repair bots
                        "Ketar Repair Bot": {"type": "repair bot", "name": "Ketar Repair Bot", "aliases": ["Repair Bot", "Ketar Bot"], "techLevel": 4, "HPps": 7, "value": 15285, "wiki": "https://galaxyonfire.fandom.com/wiki/Ketar_Repair_Bot", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475310175322132/ketar_repair_bot.png", "emoji": "<:ketarrepairbot:723706704373481543>"},
                        "Ketar Repair Bot II": {"type": "repair bot", "name": "Ketar Repair Bot II", "aliases": ["Ketar Repair Bot 2", "Repair Bot 2", "Repair Bot II", "Ketar Bot 2", "Ketar Bot II"], "techLevel": 7, "HPps": 15, "value": 141949, "wiki": "https://galaxyonfire.fandom.com/wiki/Ketar_Repair_Bot_II", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475300582686800/ketar_repair_bot_ii.png", "emoji": "<:ketarrepairbotii:723706703975284737>"},

                        # scanners
                        "Telta Quickscan": {"type": "scanner", "name": "Telta Quickscan", "aliases": ["Quickscan"], "techLevel": 2, "timeToLock": 4, "showClassAAsteroids": False, "showCargo": False, "value": 2438, "wiki": "https://galaxyonfire.fandom.com/wiki/Telta_Quickscan", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475379397984267/telta_quickscan.png", "emoji": "<:teltaquickscan:723706726079135764>"},
                        "Telta Ecoscan": {"type": "scanner", "name": "Telta Ecoscan", "aliases": ["Ecoscan"], "techLevel": 3, "timeToLock": 3, "showClassAAsteroids": False, "showCargo": True, "value": 8647, "wiki": "https://galaxyonfire.fandom.com/wiki/Telta_Ecoscan", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475370585751593/telta_ecoscan.png", "emoji": "<:teltaecoscan:723706725953306704>"},
                        "Hiroto Proscan": {"type": "scanner", "name": "Hiroto Proscan", "aliases": ["Proscan"], "techLevel": 6, "timeToLock": 1.8, "showClassAAsteroids": False, "showCargo": True, "value": 38955, "wiki": "https://galaxyonfire.fandom.com/wiki/Hiroto_Proscan", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475350603956284/hiroto_proscan.png", "emoji": "<:hirotoproscan:723706725592596542>"},
                        "Hiroto Ultrascan": {"type": "scanner", "name": "Hiroto Ultrascan", "aliases": ["Ultrascan"], "techLevel": 7, "timeToLock": 1.8, "showClassAAsteroids": True, "showCargo": True, "value": 95309, "wiki": "https://galaxyonfire.fandom.com/wiki/Hiroto_Ultrascan", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475359579766814/hiroto_ultrascan.png", "emoji": "<:hirotoultrascan:723706725915689020>"},

                        # shields
                        "Targe Shield": {"type": "shield", "name": "Targe Shield", "aliases": ["Targe"], "techLevel": 1, "shield": 50, "value": 1620, "wiki": "https://galaxyonfire.fandom.com/wiki/Targe_Shield", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475473392205844/targe_shield.png", "emoji": "<:targeshield:723706780156297298>"},
                        "Riot Shield": {"type": "shield", "name": "Riot Shield", "aliases": ["Riot"], "techLevel": 3, "shield": 80, "value": 5306, "wiki": "https://galaxyonfire.fandom.com/wiki/Riot_Shield", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475462873153546/riot_shield.png", "emoji": "<:riotshield:723706780508749964>"},
                        "H'Belam": {"type": "shield", "name": "H'Belam", "aliases": ["HBelam"], "techLevel": 5, "shield": 120, "value": 13043, "wiki": "https://galaxyonfire.fandom.com/wiki/H%27Belam", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475429159206912/hbelam.png", "emoji": "<:hbelam:723706780139520019>"},
                        "Beamshield II": {"type": "shield", "name": "Beamshield II", "aliases": ["Beamshield 2", "Beamshield"], "techLevel": 7, "shield": 150, "value": 39331, "wiki": "https://galaxyonfire.fandom.com/wiki/Beamshield_II", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475410679234650/beamshield_ii.png", "emoji": "<:beamshield:723706780202303676>"},
                        "Fluxed Matter Shield": {"type": "shield", "name": "Fluxed Matter Shield", "aliases": ["Fluxed", "Matter Shield", "Fluxed Shield"], "techLevel": 10, "shield": 220, "value": 101914, "wiki": "https://galaxyonfire.fandom.com/wiki/Fluxed_Matter_Shield", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475420300967946/fluxed_matter_shield.png", "emoji": "<:fluxedmattershield:723706780445835274>"},
                        "Particle Shield": {"type": "shield", "name": "Particle Shield", "aliases": ["Particle"], "techLevel": 10, "shield": 380, "value": 189194, "wiki": "https://galaxyonfire.fandom.com/wiki/Particle_Shield", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475438919483432/particle_shield.png", "emoji": "<:particleshield:723706780441640982>"},

                        # spectral filters
                        "Spectral Filter SA-1": {"type": "spectral filter", "name": "Spectral Filter SA-1", "aliases": ["Spectral SA-1", "Spectral Filter SA-1", "Filter SA-1", "Spectral SA1", "Filter SA1"], "techLevel": 9, "showInfo": False, "showOnRadar": False, "value": 43856, "wiki": "https://galaxyonfire.fandom.com/wiki/Spectral_Filter_SA-1", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475524814635019/spectral_filter_sa-1.png", "emoji": "<:spectralfiltersa1:723707076899242004>"},
                        "Spectral Filter ST-X": {"type": "spectral filter", "name": "Spectral Filter ST-X", "aliases": ["Spectral SA-X", "Spectral Filter SA-X", "Filter SA-X", "Spectral SAX", "Filter SAX"], "techLevel": 9, "showInfo": True, "showOnRadar": False, "value": 154662, "wiki": "https://galaxyonfire.fandom.com/wiki/Spectral_Filter_ST-X", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475538647449630/spectral_filter_st-x.png", "emoji": "<:spectralfilterstx:723707076731469878>"},
                        "Spectral Filter Omega": {"type": "spectral filter", "name": "Spectral Filter Omega", "aliases": ["Spectral Omega", "Filter Omega", "Omega"], "techLevel": 9, "showInfo": True, "showOnRadar": True, "value": 485406, "wiki": "https://galaxyonfire.fandom.com/wiki/Spectral_Filter_Omega", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475501661945887/spectral_filter_omega.png", "emoji": "<:spectralfilteromega:723707076869881896>"},

                        # thrusters
                        "Static Thrust": {"type": "thruster", "name": "Static Thrust", "aliases": [], "techLevel": 1, "handlingMultiplier":1.2, "value": 1398, "wiki": "https://galaxyonfire.fandom.com/wiki/Static_Thrust", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475634247958538/static_thrust.png", "emoji": "<:staticthrust:723707097652658178>"},
                        "Pendular Thrust": {"type": "thruster", "name": "Pendular Thrust", "aliases": [], "techLevel": 3, "handlingMultiplier":1.4, "value": 2957, "wiki": "https://galaxyonfire.fandom.com/wiki/Pendular_Thrust", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475613381558362/pendular_thrust.png", "emoji": "<:pendularthrust:723707097853722654>"},
                        "D'ozzt Thrust": {"type": "thruster", "name": "D'ozzt Thrust", "aliases": [], "techLevel": 5, "handlingMultiplier":1.7, "value": 5762, "wiki": "https://galaxyonfire.fandom.com/wiki/D%27ozzt_Thrust", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475582788304936/dozzt_thrust.png", "emoji": "<:dozztthrust:723707097765642351>"},
                        "Mp'zzzm Thrust": {"type": "thruster", "name": "Mp'zzzm Thrust", "aliases": [], "techLevel": 7, "handlingMultiplier":2, "value": 18731, "wiki": "https://galaxyonfire.fandom.com/wiki/Mp%27zzzm_Thrust", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475592443461642/mpzzzm.png", "emoji": "<:mpzzzm:723707097778225214>"},
                        "Pulsed Plasma Thrust": {"type": "thruster", "name": "Pulsed Plasma Thrust", "aliases": [], "techLevel": 8, "handlingMultiplier":2.3, "value": 31015, "wiki": "https://galaxyonfire.fandom.com/wiki/Pulsed_Plasma_Thrust", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475621694668820/pulsed_plasma_thrust.png", "emoji": "<:pulsedplasmathrust:723707097690144801>"},

                        # tractor beams
                        'AB-1 "Retractor"': {"type": "tractor beam", "name": 'AB-1 "Retractor"', "aliases": ["Retractor", '"Retractor"', "AB-1 Retractor"], "techLevel": 4, "timeToLock": 4, "value": 8962, "wiki": 'https://galaxyonfire.fandom.com/wiki/AB-1_"Retractor"', "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475674492436510/ab-1_retractor.png", "emoji": "<:ab1retractor:723707140610719787>"},
                        'AB-2 "Glue Gun"': {"type": "tractor beam", "name": 'AB-2 "Glue Gun"', "aliases": ["Glue Gun", '"Glue Gun"', "AB-2 Glue Gun"], "techLevel": 5, "timeToLock": 1.8, "value": 27464, "wiki": 'https://galaxyonfire.fandom.com/wiki/AB-2_"Glue Gun"', "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475682893627392/ab-2_glue_gun.png", "emoji": "<:ab2gluegun:723707141105516604>"},
                        'AB-3 "Kingfisher"': {"type": "tractor beam", "name": 'AB-3 "Kingfisher"', "aliases": ["Kingfisher", '"Kingfisher"', "AB-3 Kingfisher"], "techLevel": 7, "timeToLock": 0, "value": 61448, "wiki": 'https://galaxyonfire.fandom.com/wiki/AB-3_"Kingfisher"', "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475692074827856/ab-3_kingfisher.png", "emoji": "<:ab3kingfisher:723707140942069832>"},
                        'AB-4 "Octopus"': {"type": "tractor beam", "name": 'AB-4 "Octopus"', "aliases": ["Octopus", '"Octopus"', "AB-4 Octopus"], "techLevel": 8, "timeToLock": 0, "value": 199026, "wiki": 'https://galaxyonfire.fandom.com/wiki/AB-4_"Octopus"', "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475713847590942/ab-4_octopus.png", "emoji": "<:ab4octopus:723707140967235697>"},

                        # transfusion beams
                        "Crimson Drain": {"type": "transfusion beam", "name": "Crimson Drain", "aliases": ["Crimson", "Drain"], "techLevel": 8, "HPps": 7, "count": 1, "value": 8735, "wiki": "https://galaxyonfire.fandom.com/wiki/Crimson_Drain", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475747825647656/crimson_drain.png", "emoji": "<:crimsondrain:723707161146032209>"},
                        "Pandora Leech": {"type": "transfusion beam", "name": "Pandora Leech", "aliases": ["Pandora", "Leech"], "techLevel": 8, "HPps": 15, "count": 3, "value": 80537, "wiki": "https://galaxyonfire.fandom.com/wiki/Pandora_Leech", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475759028633630/pandora_leech.png", "emoji": "<:pandoraleech:723707161380913182>"},
                        
                        # weapon mods
                        "Nirai Overcharge": {"type": "weapon mod", "name": "Nirai Overcharge", "aliases": ["Overcharge"], "techLevel": 5, "dpsMultiplier":1.1, "value": 29224, "wiki": "https://galaxyonfire.fandom.com/wiki/Nirai_Overcharge", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475785935224952/nirai_overcharge.png", "emoji": "<:niraiovercharge:723707184478945302>"},
                        "Nirai Overdrive": {"type": "weapon mod", "name": "Nirai Overdrive", "aliases": ["Overdrive"], "techLevel": 5, "dpsMultiplier":1.1, "value": 30143, "wiki": "https://galaxyonfire.fandom.com/wiki/Nirai_Overdrive", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475794646532126/nirai_overdrive.png", "emoji": "<:niraioverdrive:723707184667689023>"},

                        # jump drives
                        "Khador Drive": {"type": "jump drive", "name": "Khador Drive", "aliases": ["Khador"], "techLevel": 10, "value": 310037, "wiki": "https://galaxyonfire.fandom.com/wiki/Khador_Drive", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723475113751871548/khador_drive.png", "emoji": "<:khadordrive:723706582075965511>"},
                        
                        # other
                        "Emergency System": {"type": "emergency system", "name": "Emergency System", "aliases": ["Emergency"], "techLevel": 6, "duration": 10, "value": 6860, "wiki": "https://galaxyonfire.fandom.com/wiki/Emergency_System", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723481915528839178/emergency_system.png", "emoji": "<:emergencysystem:723706633888464926>"},
                        
                        # signatures
                        # TODO: Estimated techLevel. find actual in game.
                        "Signature Midorian": {"type": "signature", "name": "Signature Midorian", "aliases": ["Midorian Signature"], "techLevel": 8, "value": 7500, "manufacturer": "midorian", "wiki": "https://galaxyonfire.fandom.com/wiki/Signature", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723481827783999508/signature_midorian.png", "emoji": "<:signaturemidorian:723706652716695582>"},
                        "Signature Nivelian": {"type": "signature", "name": "Signature Nivelian", "aliases": ["Nivelian Signature"], "techLevel": 8, "value": 7500, "manufacturer": "nivelian", "wiki": "https://galaxyonfire.fandom.com/wiki/Signature", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723481835748982804/signature_nivelian.png", "emoji": "<:signaturenivelian:723706652817227897>"},
                        "Signature Terran": {"type": "signature", "name": "Signature Terran", "aliases": ["Terran Signature"], "techLevel": 8, "value": 7500, "manufacturer": "terran", "wiki": "https://galaxyonfire.fandom.com/wiki/Signature", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723481847585046528/signature_terran.png", "emoji": "<:signatureterran:723706652527689800>"},
                        "Signature Vossk": {"type": "signature", "name": "Signature Vossk", "aliases": ["Vossk Signature"], "techLevel": 8, "value": 7500, "manufacturer": "vossk", "wiki": "https://galaxyonfire.fandom.com/wiki/Signature", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723481857051590657/signature_vossk.png", "emoji": "<:signaturevossk:723706653488185404>"},
                        
                        # shield injectors
                        "Phoenix SIS": {"type": "shield injector", "name": "Phoenix SIS", "aliases": ["SIS"], "techLevel": 9, "plasmaConsumption": 30, "value": 535304, "wiki": "https://galaxyonfire.fandom.com/wiki/Phoenix_SIS", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723481950744084540/phoenix_sis.png", "emoji": "<:phoenixsis:723706755216834641>"},
                        
                        # time extenders
                        "Rhoda Vortex": {"type": "time extender", "name": "Rhoda Vortex", "aliases": ["Vortex"], "techLevel": 9, "effect": 0.5, "duration": 15, "value": 370064, "wiki": "https://galaxyonfire.fandom.com/wiki/Rhoda_Vortex", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723482042918109204/rhoda_vortex.png", "emoji": "<:rhodavortex:723707119328690196>"}}
                        
# Data representing all primary weapon items in the game. These are used to create bbWeapon objects, which are stored in builtInWeaponObjs in a similar dict format.
builtInWeaponData = {   # Lasers
                        "Nirai Impulse EX 1": {"name": "Nirai Impulse EX 1", "aliases": ["Impulse EX 1", "Nirai EX 1", "EX 1", "Impulse 1", "Impulse EX1", "EX1", "Nirai Impulse EX1", "Nirai Impulse EX I", "Impulse EX I", "Nirai EX I", "EX I", "Impulse I", "Impulse EXI", "EXI", "Nirai Impulse EXI"], "techLevel": 1, "dps":7.5, "value":2500, "wiki": "https://galaxyonfire.fandom.com/wiki/Nirai_Impulse_EX_1", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476980837777408/nirai_impulse_ex_1.png", "emoji": "<:niraiimpulseex1:723709564217982997>"},
                        "Nirai Impulse EX 2": {"name": "Nirai Impulse EX 2", "aliases": ["Impulse EX 2", "Nirai EX 2", "EX 2", "Impulse 2", "Impulse EX2", "EX2", "Nirai Impulse EX2", "Nirai Impulse EX II", "Impulse EX II", "Nirai EX II", "EX II", "Impulse II", "Impulse EXII", "EXII", "Nirai Impulse EXII"], "techLevel": 2, "dps":12.5, "value":6727, "wiki": "https://galaxyonfire.fandom.com/wiki/Nirai_Impulse_EX_2", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476989083910194/nirai_impulse_ex_2.png", "emoji": "<:niraiimpulseex2:723709564217851974>"},
                        "Nirai Charged Pulse": {"name": "Nirai Charged Pulse", "aliases": ["Charged Pulse", "Pulse", "Nirai Pulse"], "techLevel": 3, "dps":15.78, "value":11465, "wiki": "https://galaxyonfire.fandom.com/wiki/Nirai_Charged_Pulse", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723486991533998110/nirai_charged_pulse.png", "emoji": "<:niraichargedpulse:723709563848622111>"},
                        "V'skorr": {"name": "V'skorr", "aliases": ["vskorr"], "techLevel": 6, "dps":14, "value":9528, "wiki": "https://galaxyonfire.fandom.com/wiki/V%27skorr", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723477007060566037/vskorr.png", "emoji": "<:vskorr:723709563823718402>"},
                        "Sh'koom": {"name": "Sh'koom", "aliases": ["shkoom"], "techLevel": 6, "dps":16.66, "value":14195, "wiki": "https://galaxyonfire.fandom.com/wiki/Sh%27koom", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723477000441823283/shkoom.png", "emoji": "<:shkoom:723709563840495622>"},
                        "Berger Focus I": {"name": "Berger Focus I", "aliases": ["berger focus" "berger focus 1" "focus 1" "focus I"], "techLevel": 5, "dps":17.77, "value":22816, "wiki": "https://galaxyonfire.fandom.com/wiki/Berger_Focus_I", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476909098270720/berger_focus_i.png", "emoji": "<:bergerfocusi:723709563265876051>"},
                        "Berger Focus II A1": {"name": "Berger Focus II A1", "aliases": ["berger focus 2 A1", "berger focus 2", "berger focus II", "berger focus A1", "focus 2", "focus 2 A1"], "techLevel": 6, "dps":20, "value":31946, "wiki": "https://galaxyonfire.fandom.com/wiki/Berger_Focus_II_A1", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476920133484574/berger_focus_ii_a1.png", "emoji": "<:bergerfocusiia1:723709563915730985>"},
                        "Berger Retribution": {"name": "Berger Retribution", "aliases": ["retribution"], "techLevel": 7, "dps":24, "value":37744, "wiki": "https://galaxyonfire.fandom.com/wiki/Berger_Retribution", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476927603802132/berger_retribution.png", "emoji": "<:bergerretribution:723709564150611999>"},
                        "Berger Converge IV": {"name": "Berger Converge IV", "aliases": ["converge IV", "berger converge 4", "converge 4", "berger converge", "converge"], "techLevel": 8, "dps":32.94, "value":88969, "wiki": "https://galaxyonfire.fandom.com/wiki/Berger_Converge_IV", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476901250727963/berger_converge_iv.png", "emoji": "<:bergerconvergeiv:723709563420803103>"},
                        "Disruptor Laser": {"name": "Disruptor Laser", "aliases": ["disruptor"], "techLevel": 9, "dps":60, "value":387090, "wiki": "https://galaxyonfire.fandom.com/wiki/Disruptor_Laser", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476944926277642/disruptor_laser.png", "emoji": "<:disruptorlaser:723709563936702526>"},
                        "Dark Matter Laser": {"name": "Dark Matter Laser", "aliases": ["dark matter", "dark laser", "matter laser"], "techLevel": 9, "dps":88.23, "value":523757, "wiki": "https://galaxyonfire.fandom.com/wiki/Dark_Matter_Laser", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476935740620831/dark_matter_laser.png", "emoji": "<:darkmatterlaser:723709564347744456>"},
                        
                        'M6 A1 "Wolf"': {"name": 'M6 A1 "Wolf"', "aliases": ["M6 A1", "Wolf", "M6 Wolf", "A1 Wolf", "M6 A1 Wolf", '"Wolf"', 'M6 "Wolf"', 'A1 "Wolf"'], "techLevel": 7, "dps":22.5, "value":38838, "wiki": 'https://galaxyonfire.fandom.com/wiki/M6_A1_"Wolf"', "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723486903952998430/m6_a1_wolf.png", "emoji": "<:m6a1wolf:723709564167651348>"},
                        'M6 A2 "Cougar"': {"name": 'M6 A2 "Cougar"', "aliases": ["M6 A2", "Cougar", "M6 Cougar", "A2 Cougar", "M6 A2 Cougar", '"Cougar"', 'M6 "Cougar"', 'A2 "Cougar"'], "techLevel": 8, "dps":24.28, "value":46160, "wiki": 'https://galaxyonfire.fandom.com/wiki/M6_A2_"Cougar"', "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723486960663920680/m6_a2_cougar.png", "emoji": "<:m6a2cougar:723709564289286185>"},
                        'M6 A3 "Wolverine"': {"name": 'M6 A3 "Wolverine"', "aliases": ["M6 A3", "Wolverine", "M6 Wolverine", "A3 Wolverine", "M6 A3 Wolverine", '"Wolverine"', 'M6 "Wolverine"', 'A3 "Wolverine"'], "techLevel": 9, "dps":34, "value":68725, "wiki": 'https://galaxyonfire.fandom.com/wiki/M6_A3_"Wolverine"', "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723486973750149151/m6_a3_wolverine.png", "emoji": "<:m6a3wolverine:723709564255600690>"},
                        'M6 A4 "Raccoon"': {"name": 'M6 A4 "Raccoon"', "aliases": ["M6 A4", "Raccoon", "M6 Raccoon", "A4 Raccoon", "M6 A4 Raccoon", '"Raccoon"', 'M6 "Raccoon"', 'A4 "Raccoon"'], "techLevel": 9, "dps":92.3, "value":552747, "wiki": 'https://galaxyonfire.fandom.com/wiki/M6_A4_"Raccoon"', "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476953960808478/m6_a4_raccoon.png", "emoji": "<:m6a4raccoon:723709564280897577>"},
                        
                        # Blasters
                        "N'saan": {"name": "N'saan", "aliases": ["Nsaan"], "techLevel": 1, "dps":13.33, "value":12894, "wiki": "https://galaxyonfire.fandom.com/wiki/N%27saan", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476802340782100/nsaan.png", "emoji": "<:nsaan:723709620476182579>"},
                        "K'booskk": {"name": "K'booskk", "aliases": ["Kbooskk"], "techLevel": 2, "dps":15.90, "value":16743, "wiki": "https://galaxyonfire.fandom.com/wiki/K%27booskk", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476784338829392/kbooskk.png", "emoji": "<:kbooskk:723709619968671765>"},
                        "Sh'gaal": {"name": "Sh'gaal", "aliases": ["Shgaal"], "techLevel": 4, "dps":20.93, "value":24527, "wiki": "https://galaxyonfire.fandom.com/wiki/Sh%27gaal", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476826600505354/shgaal.png", "emoji": "<:shgaal:723709620518125620>"},
                        "H'nookk": {"name": "H'nookk", "aliases": ["Hnookk"], "techLevel": 5, "dps":27.27, "value":47478, "wiki": "https://galaxyonfire.fandom.com/wiki/H%27nookk", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476771533750332/hnookk.png", "emoji": "<:hnookk:723709619989512302>"},
                        "Gram Blaster": {"name": "Gram Blaster", "aliases": ["Gram"], "techLevel": 7, "dps":40, "value":41703, "wiki": "https://galaxyonfire.fandom.com/wiki/Gram_Blaster", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476763291680779/gram_blaster.png", "emoji": "<:gramblaster:723709619624476795>"},
                        "Ridil Blaster": {"name": "Ridil Blaster", "aliases": ["Ridil"], "techLevel": 8, "dps":48, "value":67535, "wiki": "https://galaxyonfire.fandom.com/wiki/Ridil_Blaster", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476812814090300/ridil_blaster.png", "emoji": "<:ridilblaster:723709620446822420>"},
                        "Tyrfing Blaster": {"name": "Tyrfing Blaster", "aliases": ["Tyrfing"], "techLevel": 9, "dps":59.09, "value":97683, "wiki": "https://galaxyonfire.fandom.com/wiki/Tyrfing_Blaster", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723484968055079002/tyrfing_blaster.png", "emoji": "<:tyrfingblaster:723709620220198974>"},
                        "Mimung Blaster": {"name": "Mimung Blaster", "aliases": ["Mimung"], "techLevel": 9, "dps":69.56, "value":369763, "wiki": "https://galaxyonfire.fandom.com/wiki/Mimung_Blaster", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476793658572800/mimung_blaster.png", "emoji": "<:mimungblaster:723709620169736204>"},
                        
                        # EMP Blasters
                        "Luna EMP Mk I": {"name": "Luna EMP Mk I", "aliases": ["Luna Mk I", "Luna EMP", "Luna", "EMP Mk I", "EMP I"], "techLevel": 4, "dps":8.57, "value":5942, "wiki": "https://galaxyonfire.fandom.com/wiki/Luna_EMP_Mk_I", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476864126943232/luna_emp_mk_i.png", "emoji": "<:lunaempmki:723709689149390888>"},
                        "Sol EMP Mk II": {"name": "Sol EMP Mk II", "aliases": ["Sol Mk II", "Sol EMP", "Sol", "EMP Mk II", "EMP II"], "techLevel": 5, "dps":11.11, "value":12517, "wiki": "https://galaxyonfire.fandom.com/wiki/Sol_EMP_Mk_II", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476876915638310/sol_emp_mk_ii.png", "emoji": "<:solempmkii:723709689212436560>"},
                        "Dia EMP Mk III": {"name": "Dia EMP Mk III", "aliases": ["Dia Mk III", "Dia EMP", "Dia", "EMP Mk III", "EMP III"], "techLevel": 6, "dps":17.77, "value":40736, "wiki": "https://galaxyonfire.fandom.com/wiki/Dia_EMP_Mk_III", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476855465705482/dia_emp_mk_iii.png", "emoji": "<:diaempmkiii:723709689044402228>"},
                        
                        # Auto Cannons
                        "Micro Gun MK I": {"name": "Micro Gun MK I", "aliases": ["Micro MK I", "Micro I", "Micro Gun Mk 1", "Micro MK 1", "Micro 1"], "techLevel": 1, "dps":9.09, "value":2577, "wiki": "https://galaxyonfire.fandom.com/wiki/Micro_Gun_MK_I", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476716516802617/micro_gun_mki.png", "emoji": "<:microgunmki:723709599269519400>"},
                        "Micro Gun MK II": {"name": "Micro Gun MK II", "aliases": ["Micro MK II", "Micro II", "Micro Gun Mk 2", "Micro MK 2", "Micro 2"], "techLevel": 2, "dps":11.76, "value":5538, "wiki": "https://galaxyonfire.fandom.com/wiki/Micro_Gun_MK_II", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476726222684210/micro_gun_mkii.png", "emoji": "<:microgunmkii:723709599244353606>"},
                        "64MJ Railgun": {"name": "64MJ Railgun", "aliases": ["64MJ", "64MJ Railgun", "64 Rail"], "techLevel": 3, "dps":14.28, "value":15343, "wiki": "https://galaxyonfire.fandom.com/wiki/64MJ_Railgun", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476666151600138/64mj_railgun.png", "emoji": "<:64mjrailgun:723709599051677756>"},
                        "Scram Cannon": {"name": "Scram Cannon", "aliases": ["scram", "scam cannon"], "techLevel": 6, "dps":20.00, "value":47203, "wiki": "https://galaxyonfire.fandom.com/wiki/Scram_Cannon", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476735357616199/scram_cannon.png", "emoji": "<:scramcannon:723709599223382046>"},
                        "128MJ Railgun": {"name": "128MJ Railgun", "aliases": ["128MJ", "128MJ Railgun", "128 Rail"], "techLevel": 5, "dps":25.00, "value":24675, "wiki": "https://galaxyonfire.fandom.com/wiki/128MJ_Railgun", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476675119153162/128mj_railgun.png", "emoji": "<:128mjrailgun:723709598938300496>"},
                        "Mass Driver MD 10": {"name": "Mass Driver MD 10", "aliases": ["MD 10", "MD10", "Mass Driver 10", "Mass Driver MD10"], "techLevel": 8, "dps":44.44, "value":114314, "wiki": "https://galaxyonfire.fandom.com/wiki/Mass_Driver_MD_10", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476698498203678/mass_driver_md_10.png", "emoji": "<:massdrivermd10:723709599101747231>"},
                        "Mass Driver MD 12": {"name": "Mass Driver MD 12", "aliases": ["MD 12", "MD12", "Mass Driver 12", "Mass Driver MD12"], "techLevel": 9, "dps":70.00, "value":423181, "wiki": "https://galaxyonfire.fandom.com/wiki/Mass_Driver_MD_12", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476708367269969/mass_driver_md_12.png", "emoji": "<:massdrivermd12:723709599278170123>"},
                        
                        # Thermal Fusion Cannons
                        "Thermic o5": {"name": "Thermic o5", "aliases": ["o5", "Thermic"], "techLevel": 7, "dps":10.00, "value":9959, "wiki": "https://galaxyonfire.fandom.com/wiki/Thermic_o5", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723477150879186944/thermic_o5.png", "emoji": "<:thermico5:723709644899352576>"},
                        "ReHeat o10": {"name": "ReHeat o10", "aliases": ["o10", "ReHeat"], "techLevel": 8, "dps":23.52, "value":35724, "wiki": "https://galaxyonfire.fandom.com/wiki/ReHeat_o10", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723477129689432124/reheat_o10.png", "emoji": "<:reheato10:723709644786237490>"},
                        "MaxHeat o20": {"name": "MaxHeat o20", "aliases": ["o20", "MaxHeat"], "techLevel": 9, "dps":33.33, "value":86204, "wiki": "https://galaxyonfire.fandom.com/wiki/MaxHeat_o20", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723477122110455868/maxheat_o20.png", "emoji": "<:maxheato20:723709644568002562>"},
                        "SunFire o50": {"name": "SunFire o50", "aliases": ["o50", "SunFire"], "techLevel": 9, "dps":41.66, "value":183413, "wiki": "https://galaxyonfire.fandom.com/wiki/SunFire_o50", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723477138422104114/sunfire_o50.png", "emoji": "<:sunfireo50:723709644823986187>"},
                        
                        # Scatter Guns
                        "Nirai .50AS": {"name": "Nirai .50AS", "aliases": [".50AS", "50AS", "Nirai 50AS"], "techLevel": 5, "dps":18.57, "value":44092, "wiki": "https://galaxyonfire.fandom.com/wiki/Nirai_.50AS", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723477087637340193/nirai_.50as.png", "emoji": "<:nirai:723709663753011221>"},
                        "Berger FlaK 9-9": {"name": "Berger FlaK 9-9", "aliases": ["Berger FlaK 9-9", "Berger FlaK", "Berger 9-9", "Flak 9-9", "9-9"], "techLevel": 7, "dps":25.33, "value":135058, "wiki": "https://galaxyonfire.fandom.com/wiki/Berger_FlaK_9-9", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723477061800427560/berger_flak_9-9.png", "emoji": "<:bergerflak99:723709663610273843>"},
                        "Icarus Heavy AS": {"name": "Icarus Heavy AS", "aliases": ["Icarus Heavy AS", "Icarus Heavy", "Icarus AS", "Heavy AS", "Icarus"], "techLevel": 9, "dps":33.33, "value":356787, "wiki": "https://galaxyonfire.fandom.com/wiki/Icarus_Heavy_AS", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723477069610352681/icarus_heavy_as.png", "emoji": "<:icarusheavyas:723709663723388949>"}}

# Data representing all ship upgrades in the game. These are used to create bbShipUpgrade objects, which are stored in builtInUpgradeObjs in a similar dict format.
builtInUpgradeData = {  "+30 Cargo Space": {"name": "+30 Cargo Space", "shipToUpgradeValueMult":0.3, "cargo": 30, "builtIn":False, "wiki":"https://galaxyonfire.fandom.com/wiki/Kaamo_Club#Ship_Upgrades"},
                        "+20 Handling": {"name": "+20 Handling", "shipToUpgradeValueMult":0.2, "handling": 20, "builtIn":False, "wiki":"https://galaxyonfire.fandom.com/wiki/Kaamo_Club#Ship_Upgrades"},
                        "Extra Equipment Slot": {"name": "Extra Equipment Slot", "shipToUpgradeValueMult":0.4, "maxModules": 1, "builtIn":False, "wiki":"https://galaxyonfire.fandom.com/wiki/Kaamo_Club#Ship_Upgrades"},
                        "+40 Armor": {"name": "+40 Armor", "shipToUpgradeValueMult":0.2, "armour": 40, "builtIn":False, "wiki":"https://galaxyonfire.fandom.com/wiki/Kaamo_Club#Ship_Upgrades"}}

# data for builtIn criminals to be used in bbCriminal.fromDict
# criminals marked as not builtIn to allow for dictionary init. The criminal object is then marked as builtIn during package __init__.py
builtInCriminalData = {"Pal Tyyrt": {"name":"Pal Tyyrt", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226618919780359/pal_tyyrt.png", "aliases":["pal", "tyyrt"], "wiki":"https://galaxyonfire.fandom.com/wiki/Pal_Tyyrt", "builtIn":False, "isPlayer":False},
                "Kehnor": {"name":"Kehnor", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226614767419432/kehnor.png", "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Kehnor", "builtIn":False, "isPlayer":False},
                "Gendol Ethor": {"name":"Gendol Ethor", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226611608977490/gendol_ethor.png", "aliases":["gendol","ethor"], "wiki":"https://galaxyonfire.fandom.com/wiki/Gendol_Ethor", "builtIn":False, "isPlayer":False},
                "Korr Bekkt": {"name":"Korr Bekkt", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226617254510602/korr_bekkt.png", "aliases":["korr", "bekkt"], "wiki":"https://galaxyonfire.fandom.com/wiki/Korr_Bekkt", "builtIn":False, "isPlayer":False},
                "Hongar Meton": {"name":"Hongar Meton", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226613278441543/hongar_meton.png", "aliases":["hongar", "meton"], "wiki":"https://galaxyonfire.fandom.com/wiki/Hongar_Meton", "builtIn":False, "isPlayer":False},
                "Trent Jameson": {"name":"Trent Jameson", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226622195269632/trent_jameson.png", "aliases":["trent", "jameson"], "wiki":"https://galaxyonfire.fandom.com/wiki/Trent_Jameson", "builtIn":False, "isPlayer":False},
                "Qyrr Myfft": {"name":"Qyrr Myfft", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226620786114590/qyrr_myfft.png", "aliases":["qyrr","myfft"], "wiki":"https://galaxyonfire.fandom.com/wiki/Qyrr_Myfft", "builtIn":False, "isPlayer":False},

                # Midorian
                "Toma Prakupy": {"name":"Toma Prakupy", "faction":"midorian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226704953344060/toma_prakupy.png", "aliases":["toma"], "wiki":"https://galaxyonfire.fandom.com/wiki/Toma_Prakupy", "builtIn":False, "isPlayer":False},
                "Nombur Telénah": {"name":"Nombur Telénah", "faction":"midorian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226703703310397/nombur_talenah.png", "aliases":["nombur","telenah","telénah"], "wiki":"https://galaxyonfire.fandom.com/wiki/Nombur_Telénah", "builtIn":False, "isPlayer":False},
                "Bartholomeu Drew": {"name":"Bartholomeu Drew", "faction":"midorian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226697974022204/bartholomeu_drew.png", "aliases":["bart","bartholomeu","drew"], "wiki":"https://galaxyonfire.fandom.com/wiki/Bartholomeu_Drew", "builtIn":False, "isPlayer":False},
                "Doni Trillyx": {"name":"Doni Trillyx", "faction":"midorian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226699119067217/doni_trillyx.png", "aliases":["doni","trillyx"], "wiki":"https://galaxyonfire.fandom.com/wiki/Doni_Trillyx", "builtIn":False, "isPlayer":False},
                "Heinrich Wickel": {"name":"Heinrich Wickel", "faction":"midorian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226700305793085/heinrich_wickel.png", "aliases":["heinrich","wickel"], "wiki":"https://galaxyonfire.fandom.com/wiki/Heinrich_Wickel", "builtIn":False, "isPlayer":False},
                "Mashon Redal": {"name":"Mashon Redal", "faction":"midorian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226702122057768/mashon_redal.png", "aliases":["mashon","redal"], "wiki":"https://galaxyonfire.fandom.com/wiki/Mashon_Redal", "builtIn":False, "isPlayer":False},

                # Vossk
                "Mrrkt Nimkk": {"name":"Mrrkt Nimkk", "faction":"vossk", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226820854284368/mrrkt_minkk.png", "aliases":["mrrkt","nimkk"], "wiki":"https://galaxyonfire.fandom.com/wiki/Mrrkt_Nimkk", "builtIn":False, "isPlayer":False},
                "Alvar Julen": {"name":"Alvar Julen", "faction":"vossk", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226819461775360/alvar_julen.png", "aliases":["alvar","julen"], "wiki":"https://galaxyonfire.fandom.com/wiki/Alvar_Julen", "builtIn":False, "isPlayer":False},
                "Vortt Baskk": {"name":"Vortt Baskk", "faction":"vossk", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226826831298710/vortt_baskk.png", "aliases":["vortt","baskk"], "wiki":"https://galaxyonfire.fandom.com/wiki/Vortt_Baskk", "builtIn":False, "isPlayer":False},
                "Oluchi Erland": {"name":"Oluchi Erland", "faction":"vossk", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226822540394546/oluchi_erland.png", "aliases":["oluchi","erland"], "wiki":"https://galaxyonfire.fandom.com/wiki/Oluchi_Erland", "builtIn":False, "isPlayer":False},
                "Orp Tsam": {"name":"Orp Tsam", "faction":"vossk", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226823966720041/orp_tsam.png", "aliases":["orp", "tsam"], "wiki":"https://galaxyonfire.fandom.com/wiki/Orp_Tsam", "builtIn":False, "isPlayer":False},
                "Urr Sekant": {"name":"Urr Sekant", "faction":"vossk", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226825488990258/urr_sakant.png", "aliases":["urr", "sekant"], "wiki":"https://galaxyonfire.fandom.com/wiki/Urr_Sakant", "builtIn":False, "isPlayer":False},

                # Nivelian
                "Borsul Tarand": {"name":"Borsul Tarand", "faction":"nivelian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226764948537374/borsul_tarand.png", "aliases":["borsul","tarand"], "wiki":"https://galaxyonfire.fandom.com/wiki/Borsul_Tarand", "builtIn":False, "isPlayer":False},
                "Malon Sentendar": {"name":"Malon Sentendar", "faction":"nivelian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226767939207178/malon_sentendar.png", "aliases":["malon","sendendar"], "wiki":"https://galaxyonfire.fandom.com/wiki/Malon_Sentendar", "builtIn":False, "isPlayer":False},
                "Vilhelm Lindon": {"name":"Vilhelm Lindon", "faction":"nivelian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226772812726302/vilhelm_lindon.png", "aliases":["vilhelm","lindon"], "wiki":"https://galaxyonfire.fandom.com/wiki/Vilhelm_lindon", "builtIn":False, "isPlayer":False},
                "Tamir Prakupy": {"name":"Tamir Prakupy", "faction":"nivelian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226770707185664/tamir_prakupy.png", "aliases":["tamir"], "wiki":"https://galaxyonfire.fandom.com/wiki/Tamir_Prakupy", "builtIn":False, "isPlayer":False},
                "Merson Surr": {"name":"Merson Surr", "faction":"nivelian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226769327521872/merson_surr.png", "aliases":["merson","surr"], "wiki":"https://galaxyonfire.fandom.com/wiki/Merson_Surr", "builtIn":False, "isPlayer":False},
                "Ganfor Kant": {"name":"Ganfor Kant", "faction":"nivelian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226766630584370/ganfor_kant.png", "aliases":["ganfor","kant"], "wiki":"https://galaxyonfire.fandom.com/wiki/Ganfor_Kant", "builtIn":False, "isPlayer":False}}

# data for builtIn systems to be used in bbSystem.fromDict
builtInSystemData = { #Terran
            "Aquila": {"name":"Aquila", "faction":"terran", "neighbours":["Wolf-Reiser", "Loma", "Union"], "security":2, "coordinates":(9, 2), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Aquila_system"},
            "Augmenta": {"name":"Augmenta", "faction":"terran", "neighbours":["Weymire", "Magnetar", "V'Ikka", "Buntta"], "security":0, "coordinates":(6, 6), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Augmenta_system"},
            "Beidan": {"name":"Beidan", "faction":"terran", "neighbours":[], "security":0, "coordinates":(12, 6), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Beidan"},
            "Buntta": {"name":"Buntta", "faction":"terran", "neighbours":["Suteo", "Behén", "Augmenta", "V'Ikka", "Pescal Inartu", "Pan"], "security":1, "coordinates":(5, 9), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Buntta"},
            "Magnetar": {"name":"Magnetar", "faction":"terran", "neighbours":["Union", "Oom'Bak", "V'Ikka", "Augmenta"], "security":0, "coordinates":(6, 8), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Magnetar_system"},
            "Pan": {"name":"Pan", "faction":"terran", "neighbours":["Buntta", "Pescal Inartu"], "security":2, "coordinates":(3, 11), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Pan"},
            "Pescal Inartu": {"name":"Pescal Inartu", "faction":"terran", "neighbours":["Pan", "Buntta"], "security":2, "coordinates":(6, 12), "aliases":["pescal","inartu"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Pescal_Inartu"},
            "Prospero": {"name":"Prospero", "faction":"terran", "neighbours":["Union", "Vulpes"], "security":2, "coordinates":(5, 10), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Prospero"},
            "Union": {"name":"Union", "faction":"terran", "neighbours":["Loma", "Aquila", "Prospero", "Magnetar", "Weymire"], "security":1, "coordinates":(7, 4), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Union_system"},
            "Vulpes": {"name":"Vulpes", "faction":"terran", "neighbours":["Prospero", "Oom'Bak"], "security":2, "coordinates":(10, 7), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Vulpes"},
            "Wolf-Reiser": {"name":"Wolf-Reiser", "faction":"terran", "neighbours":["Aquila"], "security":0, "coordinates":(10, 3), "aliases":["wolfreiser","wolf","reiser"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Wolf-Reiser"},
            
            #Vossk
            "K'Ontrr": {"name":"K'Ontrr", "faction":"vossk", "neighbours":["S'Kolptorr", "Ni'Mrrod", "Me'Enkk", "Wah'Norr"], "security":3, "coordinates":(10, 11), "aliases":["kontrr"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:K'Ontrr"},
            "Me'Enkk": {"name":"Me'Enkk", "faction":"vossk", "neighbours":["Ni'Mrrod", "K'Ontrr"], "security":3, "coordinates":(11, 12), "aliases":["meenkk"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Me'Enkk"},
            "Ni'Mrrod": {"name":"Ni'Mrrod", "faction":"vossk", "neighbours":["K'Ontrr", "Me'Enkk", "Wah'Norr"], "security":3, "coordinates":(12, 12), "aliases":["nimrrod"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Ni'Mrrod"},
            "Oom'Bak": {"name":"Oom'Bak", "faction":"vossk", "neighbours":["Magnetar", "Vulpes", "S'Kolptorr", "V'Ikka"], "security":1, "coordinates":(9, 8), "aliases":["oombak"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Oom'Bak"},
            "S'Kolptorr": {"name":"S'Kolptorr", "faction":"vossk", "neighbours":["K'Ontrr", "Oom'Bak", "V'Ikka"], "security":2, "coordinates":(9, 9), "aliases":["skolptorr"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:S'Kolptorr"},
            "V'Ikka": {"name":"V'Ikka", "faction":"vossk", "neighbours":["Augmenta", "Buntta", "Magnetar", "Oom'Bak", "S'Kolptorr"], "security":1, "coordinates":(7, 8), "aliases":["vikka"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:V'Ikka"},
            "Wah'Norr": {"name":"Wah'Norr", "faction":"vossk", "neighbours":["K'Ontrr", "Ni'Mrrod"], "security":3, "coordinates":(12, 8), "aliases":["wahnorr"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Wah'Norr"},
            "Y'Mirr": {"name":"Y'Mirr", "faction":"vossk", "neighbours":[], "security":3, "coordinates":(11, 9), "aliases":["ymirr"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Y'Mirr"},
            
            #Nivelian
            "Behén": {"name":"Behén", "faction":"nivelian", "neighbours":["Nesla", "Suteo", "Weymire", "Buntta"], "security":2, "coordinates":(3, 6), "aliases":["behen"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Behén"},
            "Paréah": {"name":"Paréah", "faction":"nivelian", "neighbours":["Nesla"], "security":1, "coordinates":(2, 5), "aliases":["pareah"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Paréah"},
            "Nesla": {"name":"Nesla", "faction":"nivelian", "neighbours":["Behén", "Paréah", "Weymire", "Shima", "Eanya"], "security":2, "coordinates":(4, 3), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Nesla"},
            "Suteo": {"name":"Suteo", "faction":"nivelian", "neighbours":["Behén", "Buntta"], "security":2, "coordinates":(3, 8), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Suteo"},
            "Weymire": {"name":"Weymire", "faction":"nivelian", "neighbours":["Augmenta", "Behén", "Union", "Nesla", "Shima"], "security":1, "coordinates":(6, 4), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Weymire"},
            
            #Midorian
            "Eanya": {"name":"Eanya", "faction":"midorian", "neighbours":["Nesla", "Ginoya"], "security":3, "coordinates":(2, 3), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Eanya"},
            "Ginoya": {"name":"Ginoya", "faction":"midorian", "neighbours":["Talidor", "Eanya"], "security":3, "coordinates":(2, 2), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Ginoya"},
            "Loma": {"name":"Loma", "faction":"midorian", "neighbours":["Shima", "Union", "Aquila"], "security":3, "coordinates":(5, 1), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Loma"},
            "Mido": {"name":"Mido", "faction":"midorian", "neighbours":[], "security":3, "coordinates":(4, 2), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Mido"},
            "Talidor": {"name":"Talidor", "faction":"midorian", "neighbours":["Ginoya"], "security":3, "coordinates":(3, 1), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Talidor"},
            
            #Neutral
            "Alda": {"name":"Alda", "faction":"neutral", "neighbours":[], "security":3, "coordinates":(8, 13), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Alda"},
            "Her Jaza": {"name":"Her Jaza", "faction":"neutral", "neighbours":[], "security":3, "coordinates":(8, 12), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Her_Jaza"},
            "Shima": {"name":"Shima", "faction":"neutral", "neighbours":["Loma", "Weymire", "Nesla"], "security":0, "coordinates":(5, 3), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Shima"},
            "Skavac": {"name":"Skavac", "faction":"neutral", "neighbours":[], "security":3, "coordinates":(10, 1), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Skavac"},
            "Skor Terpa": {"name":"Skor Terpa", "faction":"neutral", "neighbours":[], "security":3, "coordinates":(7, 1), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Skor_Terpa"}
        }

# data for builtIn Turrets to be used in bbTurret.fromDict
builtInTurretData = { # Manual
                        "Hammerhead D1": {"name": "Hammerhead D1", "aliases": ["D1"], "techLevel": 5, "dps": 20, "value": 24174, "wiki": "https://galaxyonfire.fandom.com/wiki/Hammerhead_D1", "builtIn":False, "emoji": "<:hammerheadd1:723707422065033277>", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476535276863508/hammerhead_d1.png"},
                        "Hammerhead D2A2": {"name": "Hammerhead D2A2", "aliases": ["D2A2", "D2", "Hammerhead D2"], "techLevel": 6, "dps": 35.71, "value": 77097, "wiki": "https://galaxyonfire.fandom.com/wiki/Hammerhead_D2A2", "builtIn":False, "emoji": "<:hammerheadd2a2:723707422136598568>", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476545703772210/hammerhead_d2a2.png"},
                        "L'ksaar": {"name": "L'ksaar", "aliases": ["Lksaar"], "techLevel": 6, "dps": 48, "value": 149317, "wiki": "https://galaxyonfire.fandom.com/wiki/L%27ksaar", "builtIn":False, "emoji": "<:lksaar:723707422367154180>", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476553748447242/lksaar.png"},
                        "Matador TS": {"name": "Matador TS", "aliases": ["Matador", "TS"], "techLevel": 9, "dps": 90, "value": 485350, "wiki": "https://galaxyonfire.fandom.com/wiki/Matador_TS", "builtIn":False, "emoji": "<:matadorts:723707422455103488>", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476561931665418/matador_ts.png"},

                        # Auto
                        "Berger AGT 20mm": {"name": "Berger AGT 20mm", "aliases": ["Berger AGT", "Berger 20mm", "20mm", "AGT", "AGT 20mm"], "techLevel": 5, "dps": 40, "value": 227040, "wiki": "https://galaxyonfire.fandom.com/wiki/Berger_AGT_20mm", "builtIn":False, "emoji": "<:bergeragt20mm:723707369552347216>", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476483074686976/berger_agt_20mm.png"},
                        "Skuld AT XR": {"name": "Skuld AT XR", "aliases": ["Skuld XR", "Skuld", "AT XR", "Skuld AT", "XR"], "techLevel": 6, "dps": 47.36, "value": 407793, "wiki": "https://galaxyonfire.fandom.com/wiki/Skuld_AT_XR", "builtIn":False, "emoji": "<:skuldatxr:723707369573449809>", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476499625279508/skuld_at_xr.png"},
                        'HH-AT "Archimedes"': {"name": 'HH-AT "Archimedes"', "aliases": ["HH-AT", "HHAT Archimedes", "Archimedes", '"Archimedes"'], "techLevel": 6, "dps": 53.33, "value": 586176, "wiki": 'https://galaxyonfire.fandom.com/wiki/HH-AT_"Archimedes"', "builtIn":False, "emoji": "<:archimedes:723707369275523094>", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476492050235442/hh_at_archimedes.png"},

                        # plasma collectors
                        "PE Proton": {"name": "PE Proton", "aliases": ["Proton"], "techLevel": 9, "dps":0, "value": 43856, "wiki": "https://galaxyonfire.fandom.com/wiki/PE_Proton", "builtIn":False, "emoji": "<:peproton:723707456768704533>", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476617846063134/pe_proton.png"},
                        "PE Ambipolar-5": {"name": "PE Ambipolar-5", "aliases": ["Ambipolar", "PE Ambipolar 5", "PE Ambipolar"], "techLevel": 9, "dps":0, "value": 115169, "wiki": "https://galaxyonfire.fandom.com/wiki/PE_Ambipolar-5", "builtIn":False, "emoji": "<:peambipolar5:723707457146454123>", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476601333088276/pe_ambipolar-5.png"},
                        "PE Fusion H2": {"name": "PE Fusion H2", "aliases": ["Fusion", "PE Fusion"], "techLevel": 9, "dps":0, "value": 631720, "wiki": "https://galaxyonfire.fandom.com/wiki/PE_Fusion_H2", "builtIn":False, "emoji": "<:pefusionh2:723707456991133757>", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/723476609860108318/pe_fusion_h2.png"}}

# TO BE COMPLETED
builtInCommodityData = {
            # 
}

builtInToolData = {}
builtInToolObjs = {}

# TO BE COMPLETED
builtInSecondariesData = {
            # rockets
            "G'liissk": {"type": "rocket", "name": "G'liissk", "aliases": ["G'liissk"], "damage": 60, "loading speed": 1.2, "value": 23, "wiki": "", "builtIn": False, "icon": ""},
            "Jet Rocket": {"type": "rocket", "name": "Jet Rocket", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "Armour Rocket": {"type": "rocket", "name": "Armour Rocket", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "EMP Rocket Mk I": {"type": "rocket", "name": "EMP Rocket Mk I", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "EMP Rocket Mk II": {"type": "rocket", "name": "EMP Rocket Mk II", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},

            # missiles
            "Edo": {"type": "missile", "name": "Edo", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "S'koon": {"type": "missile", "name": "S'koon", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "Intelli Jet": {"type": "missile", "name": "Intelli Jet", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "Mamba EMP": {"type": "missile", "name": "Mamba EMP", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "Dephase EMP": {"type": "missile", "name": "Dephase EMP", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},

            # cluster missiles
            "Sheesha": {"type": "cluster missile", "name": "Sheesha", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "Garuda-IV": {"type": "cluster missile", "name": "Garuda-IV", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "Patala": {"type": "cluster missile", "name": "Patala", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},

            # emp bombs
            "EMP GL I": {"type": "emp bomb", "name": "EMP GL I", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "EMP GL II": {"type": "emp bomb", "name": "EMP GL II", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "EMP GL DX": {"type": "emp bomb", "name": "EMP GL DX", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},

            # nukes
            "AMR Tormentor": {"type": "nuke", "name": "AMR Tormentor", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "AMR Oppressor": {"type": "nuke", "name": "AMR Oppressor", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "AMR Extinctor": {"type": "nuke", "name": "AMR Extinctor", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "Liberator": {"type": "nuke", "name": "Liberator", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "Fireworks": {"type": "nuke", "name": "Fireworks", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},

            # mines
            "AMR Saber": {"type": "mine", "name": "AMR Saber", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "Ksann'k": {"type": "mine", "name": "Ksann'k", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "Neétha EMP": {"type": "mine", "name": "Neétha EMP", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},

            # sentry guns
            "Berger SG-100": {"type": "sentry gun", "name": "Berger SG-100", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "Berger SG-400": {"type": "sentry gun", "name": "Berger SG-400", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "T'Suum": {"type": "sentry gun", "name": "T'Suum", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},

            # ionizing missiles
            "Ion Lambda MK1": {"type": "ionizing missile", "name": "Ion Lambda MK1", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},
            "Ion Lambda MK2": {"type": "ionizing missile", "name": "Ion Lambda MK2", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""},

            # shock blast
            "Shock Blast": {"type": "shock blast", "name": "Shock Blast", "aliases": [], "damage": 0, "loading speed": 0, "value": 0, "wiki": "", "builtIn": False, "icon": ""}
}

# To be populated during package init
# These dicts contain item name: item object for the object described in the variable name.
# This is primarily for use in their relevent fromDict functions.
builtInSystemObjs = {}
builtInCriminalObjs = {}
# Ships are now stored as keys (names) rather than objects, as ships are no longer shared - every user has a unique ship object to allow for customisation
# builtInShipObjs = {}
builtInModuleObjs = {}
builtInWeaponObjs = {}
builtInUpgradeObjs = {}
builtInTurretObjs = {}

# References to the above item objects, sorted by techLevel.
shipKeysByTL = []
moduleObjsByTL = []
weaponObjsByTL = []
turretObjsByTL = []
