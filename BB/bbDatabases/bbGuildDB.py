from __future__ import annotations

from ..bbObjects import bbGuild
from typing import List
from . import bbBountyDB
from ..bbConfig import bbData
from .. import bbGlobals
from ..logging import bbLogger
from ..baseClasses import bbSerializable


class bbGuildDB(bbSerializable.bbSerializable):
    """A database of bbGuilds.
    
    :var guilds: Dictionary of guild.id to guild, where guild is a bbGuild
    :vartype guilds: dict[int, bbGuild]
    """

    def __init__(self):
        # Store guilds as a dict of guild.id: guild
        self.guilds = {}

    
    def getIDs(self) -> List[int]:
        """Get a list of all guild IDs in the database.

        :return: A list containing all guild IDs (ints) stored in the database.
        :rtype: list
        """
        return list(self.guilds.keys())

    
    def getGuilds(self) -> List[bbGuild.bbGuild]:
        """Get a list of all bbGuilds in the database.

        :return: A list containing all bbGuild objects stored in the database
        :rtype: list
        """
        return list(self.guilds.values())


    def getGuild(self, id : int) -> bbGuild.bbGuild:
        """Get the bbGuild object with the specified ID.

        :param str id: integer discord ID for the requested guild
        :return: bbGuild having the requested ID
        :rtype: bbGuild
        """
        return self.guilds[id]

    
    def guildIdExists(self, id : int) -> bool:
        """Check whether a bbGuild with a given ID exists in the database.
        
        :param int id: integer discord ID to check for existence
        :return: True if a bbGuild is stored in the database with the requested ID, False otherwise
        :rtype: bool
        """
        # Search the DB for the requested ID
        try:
            self.getGuild(id)
        # No bbGuild found, return False
        except KeyError:
            return False
        # Return True otherwise
        return True

    
    def guildObjExists(self, guild : bbGuild.bbGuild) -> bool:
        """Check whether a bbGuild object exists in the database.
        Existence checking is currently handled by checking if a guild with the requested ID is stored.

        :param bbGuild guild: bbGuild object to check for existence

        :return: True if the exact bbGuild exists in the DB, False otherwise
        :rtype: bool
        """
        return self.guildIdExists(guild.id)

    
    def addGuildObj(self, guild : bbGuild.bbGuild):
        """Add a given bbGuild object to the database.

        :param bbGuild guild: the bbGuild object to store
        :raise KeyError: If the the guild is already in the database
        """
        # Ensure guild is not yet in the database
        if self.guildObjExists(guild):
            raise KeyError(f"Attempted to add a guild that already exists: {guild.id}")
        self.guilds[guild.id] = guild

    
    def addGuildID(self, id: int) -> bbGuild.bbGuild:
        """Add a bbGuild object with the requested ID to the database

        :param int id: integer discord ID to create and store a bbGuild for
        :raise KeyError: If a bbGuild is already stored for the requested ID
        
        :return: the new bbGuild object
        :rtype: bbGuild
        """
        # Ensure the requested ID does not yet exist in the database
        if self.guildIdExists(id):
            raise KeyError(f"Attempted to add a guild that already exists: {id}")
        # Create and return a bbGuild for the requested ID
        self.guilds[id] = bbGuild.bbGuild(id, bbBountyDB.bbBountyDB(bbData.bountyFactions), bbGlobals.client.get_guild(id))
        return self.guilds[id]
    

    def getOrAddGuildID(self, id: int) -> bbGuild.bbGuild:
        """Get the existing, or add a new, bbGuild object with the requested ID to the database

        :param int id: integer discord ID to get or create a bbGuild for
        
        :return: the existing bbGuild object if one exists, or a new one
        :rtype: bbGuild
        """
        if existing := self.guilds.get(id, None):
            return existing
        
        return self.addGuildID(id)
    
    
    def removeGuildId(self, id : int):
        """Remove the bbGuild with the requested ID from the database.
        
        :param int id: integer discord ID to remove from the database
        """
        self.guilds.pop(id)

    
    def removeGuildObj(self, guild : bbGuild.bbGuild):
        """Remove the given bbGuild object from the database
        Currently removes any bbGuild sharing the given guild's ID, even if it is a different object.

        :param bbGuild guild: the guild object to remove from the database
        """
        self.removeGuildId(guild.id)

    
    def refreshAllShopStocks(self):
        """Generate new stock for all shops belonging to the stored bbGuilds
        """
        for guild in self.guilds.values():
            if not guild.shopDisabled:
                guild.shop.refreshStock()
    
    
    def toDict(self, **kwargs) -> dict:
        """Serialise this bbGuildDB into dictionary format

        :return: A dictionary containing all data needed to recreate this bbGuildDB
        :rtype: dict
        """
        data = {}
        # Iterate over all stored guilds
        for guild in self.getGuilds():
            # Serialise and then store each guild
            # JSON stores properties as strings, so ids must be converted to str first.
            data[str(guild.id)] = guild.toDict(**kwargs)
        return data

    
    def __str__(self) -> str:
        """Fetch summarising information about the database, as a string
        Currently only the number of guilds stored

        :return: A string summarising this db
        :rtype: str
        """
        return "<bbGuildDB: " + str(len(self.guilds)) + " guilds>"


    @classmethod
    def fromDict(cls, guildsDBDict : dict, **kwargs) -> bbGuildDB:
        """Construct a bbGuildDB object from dictionary-serialised format; the reverse of bbGuildDB.todict()

        :param dict bountyDBDict: The dictionary representation of the bbGuildDB to create
        :param bool dbReload: Whether or not this DB is being created during the initial database loading phase of bountybot. This is used to toggle name checking in bbBounty contruction.
        :return: The new bbGuildDB
        :rtype: bbGuildDB
        """
        dbReload = kwargs["dbReload"] if "dbReload" in kwargs else False
        
        # Instance the new bbGuildDB
        newDB = bbGuildDB()
        # Iterate over all IDs to add to the DB
        for id in guildsDBDict.keys():
            # Instance new bbGuilds for each ID, with the provided data
            # JSON stores properties as strings, so ids must be converted to int first.
            try:
                newDB.addGuildObj(bbGuild.bbGuild.fromDict(guildsDBDict[id], id=int(id), dbReload=dbReload))
            # Ignore guilds that don't have a corresponding dcGuild
            except bbGuild.NoneDCGuildObj:
                bbLogger.log("bbGuildDB", "fromDict", f"no corresponding discord guild found for ID {id}, guild removed from database",
                    category="guildsDB", eventType="NULL_GLD")
        return newDB
