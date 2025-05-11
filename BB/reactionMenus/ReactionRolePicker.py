from __future__ import annotations
from discord.member import Member
from . import ReactionMenu
from ..bbConfig import bbConfig
from .. import bbGlobals, lib
from discord import Colour, NotFound, HTTPException, Forbidden, Guild, Role, Message, User
from datetime import datetime
from ..scheduling import TimedTask
from typing import List, Union, Dict


async def giveRole(args : List[Union[Guild, Role, int]], reactingUser : Union[User, Member] = None) -> bool:
    """Grant the given user the role described in args.
    if reactingUser already has the requested role, do nothing.

    :param dict args: A list containing the guild to grant the role in, the role to grant, and finally the message ID that triggered the role addition.
    :param discord.User reactingUser: The user to grant the role to (Default None)
    :return: The new state of role ownership; always True
    :rtype: bool
    """
    dcGuild = args[0]
    dcMember = dcGuild.get_member(reactingUser.id)
    role = args[1]
    msgID = args[2]

    if role not in dcMember.roles:
        await dcMember.add_roles(role, reason="User requested role toggle via BB reaction menu " + str(msgID))
    return True


async def removeRole(args : List[Union[Guild, Role, int]], reactingUser : Union[User, Member] = None) -> bool:
    """remove the role described in args from the given user.
    if reactingUser already lacks the requested role, do nothing.

    :param dict args: A list containing the guild to remove the role in, the role to grant, and finally the message ID that triggered the role addition.
    :param discord.User reactingUser: The user to remove the role from (Default None)
    :return: The new state of role ownership; always False
    :rtype: bool
    """
    dcGuild = args[0]
    dcMember = dcGuild.get_member(reactingUser.id)
    role = args[1]
    msgID = args[2]

    if role in dcMember.roles:
        await dcMember.remove_roles(role, reason="User requested role toggle via BB reaction menu " + str(msgID))
    return False


async def markExpiredRoleMenu(menuID : int):
    """Decrement the owning bbGuild's role menus counter, and call ReactionMenu.markExpiredMenu.

    :param int menuID: The message ID of the menu to expire
    """
    menu = bbGlobals.reactionMenusDB[menuID]
    if bbGlobals.guildsDB.guildIdExists(menu.msg.guild.id):
        bbGlobals.guildsDB.getGuild(menu.msg.guild.id).ownedRoleMenus -= 1
    await ReactionMenu.markExpiredMenu(menuID)


class ReactionRolePickerOption(ReactionMenu.ReactionMenuOption):
    """A reaction menu option that stores a role, granting the reacting user the role when added, and removing the role when the reaction is removed.

    :var role: The role to toggle on reactions
    :vartype role: discord.Role 
    """

    def __init__(self, emoji : lib.emojis.dumbEmoji, role : Role, menu : ReactionMenu.ReactionMenu):
        self.role = role
        super(ReactionRolePickerOption, self).__init__(self.role.name, emoji, addFunc=giveRole, addArgs=(menu.dcGuild, self.role, menu.msg.id), removeFunc=removeRole, removeArgs=(menu.dcGuild, self.role, menu.msg.id))


    def toDict(self, **kwargs) -> dict:
        """Serialize the option into dictionary format for saving.
        Since reaction menu options are saved alongside their emojis, this dictionary need not contain the option emoji.

        :return: A dictionary containing all information needed to reconstruct this menu option
        :rtype: dict
        """
        # baseDict = super(ReactionRolePickerOption, self).toDict(**kwargs)
        # baseDict["role"] = self.role.id
        
        # return baseDict

        return {"role": self.role.id}


class ReactionRolePicker(ReactionMenu.ReactionMenu):
    """A reaction menu that grants and removes roles when interacted with.
    TODO: replace dcGuild param with extracting msg.guild
    """

    def __init__(self, msg : Message, reactionRoles : Dict[lib.emojis.dumbEmoji, Role], dcGuild : Guild,
            titleTxt : str = "", desc : str = "", col : Colour = Colour.blue(), timeout : TimedTask.TimedTask = None,
            footerTxt : str = "", img : str = "", thumb : str = "", icon : str = "", authorName : str = "",
            targetMember : Member = None, targetRole : Role = None):
        # TODO: Stop taking dcGuild, and instead extract dcGuild from msg.guild
        """
        :param discord.Message msg: the message where this menu is embedded
        :param reactionRoles: A dictionary where keys are emojis and values are the roles to grant/remove when adding/removing the emoji 
        :type reactionRoles: dict[lib.emojis.dumbEmoji, discord.Role]
        :param discord.Guild dcGuild: The guild where this menu is contained TODO: Remove and replace with extracting msg.guild
        :param str titleTxt: The content of the embed title (Default "**Role Menu**")
        :param str desc: he content of the embed description; appears at the top below the title (Default "React for your desired role!")
        :param discord.Colour col: The colour of the embed's side strip (Default None)
        :param str footerTxt: Secondary description appearing in darker font at the bottom of the embed (Default time until menu expiry if timeout is not None, "" otherwise)
        :param str img: URL to a large icon appearing as the content of the embed, left aligned like a field (Default "")
        :param str thumb: URL to a larger image appearing to the right of the title (Default "")
        :param str icon: URL to a smaller image to the left of authorName. AuthorName is required for this to be displayed. (Default "")
        :param str authorName: Secondary, smaller title for the embed (Default "")
        :param TimedTask timeout: The TimedTask responsible for expiring this menu (Default None)
        :param discord.Member targetMember: The only discord.Member that is able to interact with this menu. All other reactions are ignored (Default None)
        :param discord.Role targetRole: In order to interact with this menu, users must possess this role. All other reactions are ignored (Default None)
        """
        self.dcGuild = dcGuild
        self.msg = msg
        roleOptions = {}
        for reaction in reactionRoles:
            roleOptions[reaction] = ReactionRolePickerOption(reaction, reactionRoles[reaction], self)

        if titleTxt == "":
            titleTxt = "**Role Menu**"
        if desc == "":
            desc = "React for your desired role!"

        super(ReactionRolePicker, self).__init__(msg, options=roleOptions, titleTxt=titleTxt, desc=desc, col=col, footerTxt=footerTxt, img=img, thumb=thumb, icon=icon, authorName=authorName, timeout=timeout, targetMember=targetMember, targetRole=targetRole)
        self.saveable = True


    def toDict(self, **kwargs) -> dict:
        """Serialize this menu to dictionary format for saving to file.

        :return: A dictionary containing all information needed to reconstruct this menu object
        :rtype: dict
        """
        # TODO: Remove this method. The guild is already saved in ReactionMenu.toDict
        baseDict = super(ReactionRolePicker, self).toDict(**kwargs)
        baseDict["guild"] = self.dcGuild.id
        return baseDict


    @classmethod
    def fromDict(cls, rmDict : dict, **kwargs) -> ReactionRolePicker:
        """Reconstruct a ReactionRolePicker from its dictionary-serialized representation.

        :param dict rmDict: A dictionary containing all information needed to construct the desired ReactionRolePicker
        :return: A new ReactionRolePicker object as described in rmDict
        :rtype: ReactionRolePicker
        """
        if "msg" in kwargs:
            raise NameError("Required kwarg not given: msg")
        msg = kwargs["msg"]

        dcGuild = msg.guild

        reactionRoles = {}
        for reaction in rmDict["options"]:
            reactionRoles[lib.emojis.dumbEmojiFromStr(reaction)] = dcGuild.get_role(rmDict["options"][reaction]["role"])

        timeoutTT = None
        if "timeout" in rmDict:
            expiryTime = datetime.fromtimestamp(rmDict["timeout"], timezone.utc)
            bbGlobals.reactionMenusTTDB.scheduleTask(TimedTask.TimedTask(expiryTime=expiryTime, expiryFunction=ReactionMenu.markExpiredMenu, expiryFunctionArgs=msg.id))


        return ReactionRolePicker(msg, reactionRoles, dcGuild,
                                    titleTxt=rmDict["titleTxt"] if "titleTxt" in rmDict else "",
                                    desc=rmDict["desc"] if "desc" in rmDict else "",
                                    col=Colour.from_rgb(rmDict["col"][0], rmDict["col"][1], rmDict["col"][2]) if "col" in rmDict else Colour.blue(),
                                    footerTxt=rmDict["footerTxt"] if "footerTxt" in rmDict else "",
                                    img=rmDict["img"] if "img" in rmDict else "",
                                    thumb=rmDict["thumb"] if "thumb" in rmDict else "",
                                    icon=rmDict["icon"] if "icon" in rmDict else "",
                                    authorName=rmDict["authorName"] if "authorName" in rmDict else "",
                                    timeout=timeoutTT,
                                    targetMember=dcGuild.get_member(rmDict["targetMember"]) if "targetMember" in rmDict else None,
                                    targetRole=dcGuild.get_role(rmDict["targetRole"]) if "targetRole" in rmDict else None)
