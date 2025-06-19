# Typing imports
from types import FunctionType
from discord import Message, Embed, Colour
from typing import List
from ..bbConfig import bbConfig, bbData
from .. import logging


class IncorrectCommandCallContext(Exception):
    """Exception used to indicate when a non-DMable command is called from DMs.
    May be used in the future to indicate the opposite; a command that can only be called from DMs is called from outside of DMs.
    """
    pass


class CommandRegistry:
    """Represents a registration of a command in a HeirarchicalCommandsDB.
    TODO: Make allowDM so we dont have to make two HeirarchicalCommandsDBs to handle DM commands

    :var ident: The string command name by which this command is identified and called
    :vartype ident: str
    :var func: A reference to the function to call upon calling this CommandRegistry
    :vartype func: FunctionType
    :var forceKeepArgsCasing: Whether to pass arguments to the function with their original casing. If False, arguments will be transformed to lower case before passing.
    :vartype forceKeepArgsCasing: bool
    :var forceKeepCommandCasing: Whether the command must be called with exactly the correct casing
    :vartype forceKeepCommandCasing: bool
    :var allowDM: Allow calling of this command from DMs.
    :vartype allowDM: bool
    :var signatureStr: A short string naming each parameter in the command signature
    :vartype signatureStr: str
    :var shortHelp: A short string describing the command
    :vartype shortHelp: str
    :var longHelp: A longer help string describing in full parameters and command usage
    :vartype longHelp: str
    """
    def __init__(self, ident : str, func: FunctionType, accessLevel: int, forceKeepArgsCasing : bool, forceKeepCommandCasing : bool, allowDM : bool, allowHelp : bool, aliases : List[str] = [], signatureStr : str = "", shortHelp : str = "", longHelp : str = "", helpSection : str = "miscellaneous"):
        """
        :param str ident: The string command name by which this command is identified and called
        :param FunctionType func: A reference to the function to call upon calling this CommandRegistry
        :param bool forceKeepArgsCasing: Whether to pass arguments to the function with their original casing. If False, arguments will be transformed to lower case before passing.
        :param bool forceKeepCommandCasing: Whether the command must be called with exactly the correct casing
        :param bool allowDM: Allow calling of this command from DMs
        :param bool allowHelp: If False, do not display this command in help listings.
        :param List[str] aliases: List of alternative names for this command (Default [])
        :param str signatureStr: A short string naming each parameter in the command signature (Default "")
        :param str shortHelp: A short string describing the command (Default "")
        :param str longHelp: A longer help string describing in full parameters and command usage (Default "")
        :param str helpSection: The name of the help section containing this command (Default "miscellaneous")
        """
        self.ident = ident
        self.func = func
        self.forceKeepArgsCasing = forceKeepArgsCasing
        self.forceKeepCommandCasing = forceKeepCommandCasing
        self.allowDM = allowDM
        self.allowHelp = allowHelp
        self.aliases = aliases
        self.signatureStr = signatureStr
        self.shortHelp = shortHelp
        self.longHelp = longHelp
        self.helpSection = helpSection
        self.accessLevel = accessLevel


    async def call(self, message : Message, args : str, isDM : bool):
        """Call this command.

        :param discord.message message: the discord message calling the command. This is required for referencing the author and sending responses
        :param str args: string containing arguments to pass to the command
        :param bool isDM: Whether the command was called from DMs or not
        :raise IncorrectCommandCallContext: When attempting to call a non-DMable command from DMs
        """
        if self.accessLevel == 2:
            callerStr = f"{message.author.display_name}#{message.author.id}" if message.author is not None else 'UNKNOWN'
            channelStr = (f"{message.guild.name}#{message.guild.id}/{message.channel.id}"
                          if message.guild is not None else f"{message.channel.id} (DM)")
            logging.bbLogger.log(
                CommandRegistry.__name__,
                CommandRegistry.call.__name__,
                "DEVCMD",
                "devCommands",
                "CMD_CALL",
                f"{callerStr} called dev command {self.ident} with args {args} in channel {channelStr}")
        
        if isDM and not self.allowDM:
            raise IncorrectCommandCallContext("Attempted to call command '" + self.ident + "' from DMs, but command is not allowed in DMs.")
        await self.func(message, args if self.forceKeepArgsCasing else args.lower(), isDM)


class HeirarchicalCommandsDB:
    """Class that stores, categorises, and calls commands based on a text name and caller permissions.
    
    :vartype numAccessLevels: The number of command access levels registerable and callable in this database
    :type numAccessLevels: int
    :var commands: A list, where the index in the list corresponds to the access level requirement. Each index in the list is a dictionary mapping a command identifier string to a command registry.
    :vartype commands: List[Dict[str, CommandRegistry]]
    :var helpSections: A list, where indices correspond to access levels, and elements are dictionaries mapping help section names to lists of CommandRegistrys
    :vartype helpSections: List[Dict[str, List[CommandRegistry]]]
    :var helpSectionEmbeds:  A list, where indices correspond to access levels, and elements are dictionaries mapping help section names to a list of discord.Embeds describing each command in the section by their shortHelp strings
    :vartype helpSectionEmbeds: List[Dict[str, List[Embed]]]
    """

    def __init__(self, numAccessLevels : int):
        if numAccessLevels < 1:
            raise ValueError("Cannot create a HeirarchicalCommandsDB with less than one access level")
        self.numAccessLevels = numAccessLevels
        self.clear()
        self.helpSections = [{"miscellaneous" : []} for accessLevel in range(self.numAccessLevels)]
        self.helpSectionEmbeds = [{"miscellaneous" : [Embed(title="BB " + bbConfig.accessLevelNames[accessLevel] + " Commands", description=bbData.helpIntro + "\n__Miscellaneous__", colour=Colour.blue())]} for accessLevel in range(self.numAccessLevels)]
        self.helpSectionEmbeds[0]["miscellaneous"][0].set_footer(text="Page 1 of 1")
        self.totalEmbeds = [1 for level in range(numAccessLevels)]
        
    
    def register(self, command : str, function : FunctionType, accessLevel : int, aliases : List[str] = [],
            forceKeepArgsCasing : bool = False, forceKeepCommandCasing : bool = False, allowDM : bool = True, noHelp : bool = False,
            signatureStr : str = "", shortHelp : str = "", longHelp : str = "", useDoc : bool = False, helpSection : str = "miscellaneous"):
        """Register a command in the database.

        :param str command: the text name users should call the function by. Commands are case sensitive.
        :param FunctionType function: reference to the function that should be called
        :param int accessLevel: The level of access required to call this command
        :param List[str] aliases: List of alternative commands which may be used to call this one. The same accessLevel will be required for all aliases. (Default []) 
        :param bool forceKeepArgsCasing: Whether to pass arguments to the function with their original casing. If False, arguments will be transformed to lower case before passing. (Default False)
        :param bool forceKeepCommandCasing: Whether the command must be called with exactly the correct casing (Default False)
        :param bool allowDM: Allow calling of this command from DMs. (Default True)
        :param bool noHelp: If true, do not add this command to the help registry (Default False)
        :param str signatureStr: A short string naming each parameter in the command signature. (Default function.__name__)
        :param str shortHelp: A short string describing the command (Default "")
        :param str longHelp: A longer help string describing in full parameters and command usage (Default "")
        :param bool useDoc: If no help strings are given, fall back on the docstring of function. (Default False)
        :param str helpSection: The name of the help section that this command should be displayed under (Default "miscellaneous")
        :raise IndexError: When attempting to register at an unsupported access level
        :raise NameError: When attempting to register a command identifier or alias that already exists at the requested access level
        :raise ValueError: When an unknown help section name is requested
        """
        # Validate accessLevel
        if accessLevel < 0 or accessLevel > self.numAccessLevels - 1:
            raise IndexError("Access level out of range. Minimum: 0, maximum: " + str(self.numAccessLevels - 1) + ", given: " + str(accessLevel))
        
        # Generate a list of all command identifiers with respect to forceKeepCommandCasing
        cmdIdent = command if forceKeepCommandCasing else command.lower()
        allIdents = [cmdIdent]
        for alias in aliases:
            allIdents.append(alias if forceKeepCommandCasing else alias.lower())
        
        # Validate command identifiers for existence at the given accessLevel
        for currentIdent in allIdents:
            if currentIdent in self.commands[accessLevel]:
                raise NameError("A command at access level " + str(accessLevel) + " already exists with the name " + currentIdent)
        
        if not noHelp:
            helpSection = helpSection.lower()

            # Infer help strings from the function docstrings, if instructed to
            if useDoc:
                longHelp = function.__doc__
            
            if longHelp and not shortHelp:
                # max out shortHelp string lengths at 200 characters here to keep things short. Not a limit anywhere else, just for docstring inferring.
                if len(longHelp) <= 200:
                    shortHelp = longHelp
                # if longhelp > 200 characters, first attempt the first line of longHelp
                elif len(longHelp.split("\n")[0]) <= 200:
                    shortHelp = longHelp.split("\n")[0]
                # next try the first sentence of the first line...
                elif len(longHelp.split("\n")[0].split(".")[0]) < 200:
                    shortHelp = longHelp.split("\n")[0].split(".")[0] + "."
                # As a last resort, just cut it off.
                else:
                    shortHelp = longHelp[:201]
            
            elif not shortHelp and not longHelp:
                shortHelp = "*No help string available for this command*"
            
            # if missing longHelp but not shortHelp, copy over shortHelp to long
            elif not longHelp:
                longHelp = shortHelp

            # if missing signatureStr, use the function name
            if not signatureStr:
                signatureStr = function.__name__

            # Ensure helpSection is valid in the DB
            if helpSection not in self.helpSections[accessLevel]:
                raise ValueError("Unrecognised help section name '" + helpSection + "'")

        # Register all identifiers for this command to the same command registry
        newRegistry = CommandRegistry(cmdIdent, function, accessLevel, forceKeepArgsCasing, forceKeepCommandCasing, allowDM, not noHelp, aliases=aliases, signatureStr=signatureStr, shortHelp=shortHelp, longHelp=longHelp, helpSection=helpSection)
        for currentIdent in allIdents:
            self.commands[accessLevel][currentIdent] = newRegistry

        if not noHelp:
            # Add the command to help
            self.helpSections[accessLevel][helpSection].append(newRegistry)
            self.helpSectionEmbeds[accessLevel][helpSection][-1].add_field(name=signatureStr, value=newRegistry.shortHelp.replace("$COMMANDPREFIX$", bbConfig.commandPrefix), inline=False)

            if len(self.helpSectionEmbeds[accessLevel][helpSection][-1]) > 6000 or len(self.helpSectionEmbeds[accessLevel][helpSection][-1].fields) > bbConfig.maxCommandsPerHelpPage:
                self.helpSectionEmbeds[accessLevel][helpSection][-1].remove_field(-1)
                self.helpSectionEmbeds[accessLevel][helpSection].append(Embed(title="BB " + bbConfig.accessLevelNames[accessLevel] + " Commands", description=bbData.helpIntro + "\n__" + helpSection.title() + "__", colour=Colour.blue()))
                self.helpSectionEmbeds[accessLevel][helpSection][-1].add_field(name=signatureStr, value=newRegistry.shortHelp.replace("$COMMANDPREFIX$", bbConfig.commandPrefix), inline=False)
                for pageNum in range(len(self.helpSectionEmbeds[accessLevel][helpSection])):
                    self.helpSectionEmbeds[accessLevel][helpSection][pageNum].set_footer(text="Page " + str(pageNum+1) + " of " + str(len(self.helpSectionEmbeds[accessLevel][helpSection])))
                self.totalEmbeds[accessLevel] += 1

    
    async def call(self, command : str, message : Message, args : str, accessLevel : int, isDM : bool = False):
        """Call a command or send an error message.

        :param str command: the text name of the command to attempt to call. Commands may be case sensitive, depending on their forceKeepCommandCasing option
        :param discord.message message: the discord message calling the command. This is required for referencing the author and sending responses
        :param str args: string containing arguments to pass to the command. May be transformed to lower case before passing, depending on the commands forceKeepArgsCasing option
        :param bool isDM: Whether the command was called from DMs or not (Default False)
        :return: True if the command call was successful, False otherwise
        :rtype: bool
        """
        commandLower = command.lower()
        # Search upper access levels first
        for requiredAccess in range(accessLevel, -1, -1):
            # Search casing matches (forceKeepCommandCasing) first
            if command in self.commands[requiredAccess]:
                await self.commands[requiredAccess][command].call(message, args, isDM)
                # Return true if a command was found
                return True
            elif commandLower in self.commands[requiredAccess]:
                await self.commands[requiredAccess][commandLower].call(message, args, isDM)
                return True
        # Return false if no command could be matched
        return False


    def clear(self):
        """Remove all command registrations from the database.
        """
        self.commands = [{} for i in range(self.numAccessLevels)]

    
    def addHelpSection(self, accessLevel : int, sectionName : str):
        """Add a help section to the DB.

        :param int accessLevel: The access level which commands in the new section require
        :param str sectionName: The name of the new section
        :raise ValueError: If a section with this name already exists
        :raise IndexError: If attemping to use an out of range access level
        """
        if accessLevel < 0 or accessLevel > self.numAccessLevels - 1:
            raise IndexError("accessLevel must be at least 0, and less than " + str(self.numAccessLevels))
        if sectionName in self.helpSections:
            raise ValueError("The given section name already exists in this DB '" + sectionName + "'")

        self.helpSections[accessLevel][sectionName] = []
        self.helpSectionEmbeds[accessLevel][sectionName] = [Embed(title="BB " + bbConfig.accessLevelNames[accessLevel] + " Commands", description=bbData.helpIntro + "\n__" + sectionName.title() + "__")]
        self.helpSectionEmbeds[accessLevel][sectionName][0].set_footer(text="Page 1 of 1")
        self.totalEmbeds[accessLevel] += 1

