from .bbConfig import bbConfig
from os import path, makedirs
from datetime import datetime, timezone
import traceback
from typing import Tuple


class logger:
    """A general event logging object.
    Takes strings describing events, categorises them, sorts them by time added,
    and saves them to separate text files by category. Upon saving to file, the logger clears its logs.
    TODO: Add option to save to tsv or similar instead of txt

    :var logs: A dictionary associating category names with dictionaries, associating datetime.datetimes with event strings
    :vartype logs: dict[str, dict[datetime.datetime, str]]
    """

    def __init__(self):
        self.clearLogs()


    def clearLogs(self):
        """Clears all logs from the database.
        """
        self.logs = {
            "usersDB":{}, "guildsDB":{}, "bountiesDB":{},
            "shop":{}, "escapedBounties": {}, "bountyConfig": {},
            "duels": {}, "hangar": {}, "misc": {},
            "bountyBoards": {}, "newBounties": {},
            "reactionMenus": {}, "userAlerts": {}
        }


    def isEmpty(self) -> bool:
        """Decide whether or not any logs are currently stored, waiting to be saved to file.

        :return: False if any of the logger's categories currently contains any logs. True otherwise.
        :rtype: bool
        """
        for cat in self.logs:
            if bool(self.logs[cat]):
                return False
        return True


    def peekHeadTimeAndCategory(self) -> Tuple[datetime, str]:
        """Get the log time of the earliest-logged event currently stored in the logger, as well as the category of the event.
        If the logger is currently empty, None is returned as the log time, and "" as the category.

        :return: If the logger is not empty, a tuple whose first element is the time that the earliest-logged event was added to the logger, and whose second element is the earliest-logged event's category. (None, "") otherwise.
        :rtype: tuple[datetime.datetime or None, str]
        """
        head, headCat = None, ""
        for cat in self.logs:
            if bool(self.logs[cat]):
                currHead = list(self.logs[cat].keys())[0]
                if head is None or currHead < head:
                    head, headCat = currHead, cat

        return head, headCat


    def popHeadLogAndCategory(self) -> Tuple[str, str]:
        """Pop the earliest-logged event and its category. This also removes the returned log from the logger.
        If the logger is currently empty, ("", "") is returned.

        :return: If the logger is not empty, a tuple whose first element is the event string of the earliest-logged event, and whose second element is that log's category. ("", "") otherwise.
        :rtype: tuple[str, str]
        """
        head, headCat = self.peekHeadTimeAndCategory()

        if head is None:
            log = ""
        else:
            log = self.logs[headCat][head]
            del self.logs[headCat][head]

        return log, headCat


    def save(self):
        """Save all currently stored logs to separate text files, named after categories.
        Log files are saved to the directory specified in bbConfig.loggingFolderPath.
        Logs are sorted by the time they were added to the logger prior to saving.
        After saving, the logger is cleared of logs.
        If category-named text files or their parent directory do not exist, they are created.
        """
        if self.isEmpty():
            return

        logsSaved = ""
        files = {}
        nowStr = datetime.now(timezone.utc).strftime("(%d/%m/%H:%M)")

        # 1) Ensure the logging folder exists:
        base_dir = bbConfig.loggingFolderPath
        if not path.exists(base_dir):
            try:
                makedirs(base_dir, exist_ok=True)
                logsSaved += f"[DIR_CREATED:{base_dir}] "
            except OSError as e:
                print(f"{nowStr}-[LOG::SAVE]>DIR_IOERR: ERROR CREATING DIRECTORY: {base_dir}: {e.__class__.__name__}\n{traceback.format_exc()}")

        # 2) Iterate over each category that has logs. For each, open (or create) its .txt file in 'ab' mode.
        for category in self.logs:
            if bool(self.logs[category]):
                # Build full path, ensuring there's exactly one slash between folder and filename
                currentFName = base_dir.rstrip("/") + "/" + category + ".txt"
                logsSaved += category + ".txt, "

                try:
                    # Opening in 'ab' will create the file if it doesn't already exist (provided the directory exists).
                    files[category] = open(currentFName, 'ab')
                except IOError as e:
                    print(f"{nowStr}-[LOG::SAVE]>F_OPN_IOERR: ERROR OPENING/CREATING LOG FILE: {currentFName}: {e.__class__.__name__}\n{traceback.format_exc()}")
                    files[category] = None

        # 3) Write out all queued logs in chronological order, then close each file.
        while not self.isEmpty():
            log, category = self.popHeadLogAndCategory()
            if files.get(category) is not None:
                try:
                    files[category].write(log.encode("utf-8"))
                except IOError as e:
                    print(f"{nowStr}-[LOG::SAVE]>F_WRT_IOERR: ERROR WRITING TO LOG FILE: {files[category].name}: {e.__class__.__name__}\n{traceback.format_exc()}")
                except UnicodeEncodeError as e:
                    print(f"{nowStr}-[LOG::SAVE]>UNICODE_ERR: ERROR ENCODING LOG: {e}\n{traceback.format_exc()}")

        for f in files.values():
            if f is not None:
                f.close()

        if logsSaved:
            # Trim trailing comma+space
            print(f"{nowStr}-[LOG::SAVE]>SAVE_DONE: Logs saved: {logsSaved.rstrip(', ')}")

        self.clearLogs()


    def log(self, classStr: str, funcStr: str, event: str,
            category: str = "misc", eventType: str = "MISC_ERR",
            trace: str = "", noPrintEvent: bool = False, noPrint: bool = False):
        """Log an event, queueing the log to be saved to a file.

        :param str classStr: The class in which the event occurred
        :param str funcStr: The function in which the event occurred
        :param str event: The event string - a string describing the event that occurred.
        :param str category: The category of the event, corresponding to the name of the log file where this event will be saved.
                            Must match one of the keys in the logger’s logs dictionary. (Default 'misc')
        :param str eventType: The type of event, analogous to an exception type name. (Default 'MISC_ERR')
        :param str trace: If the logged event is an exception, you may wish to provide a stack trace here with traceback.format_exc(). (Default "")
        :param bool noPrintEvent: Give True to print this log to console without the event string. Useful in cases where the event string is very long. (Default False)
        :param bool noPrint: Skip printing this log to console entirely. Useful in cases where the log occurs frequently and helps little with debugging or similar. (Default False)
        """
        if category not in self.logs:
            # If an unknown category was passed, redirect to 'misc' and log that incident too
            self.log("misc", "log", f"Attempted to log to unknown category '{category}'; redirected to 'misc'.", eventType="UNKNOWN_CATEGORY")
            category = "misc"

        now = datetime.now(timezone.utc)
        timestamp = now.strftime("(%d/%m/%H:%M)")

        if noPrintEvent:
            eventStr = f"{timestamp}-[{classStr.upper()}::{funcStr.upper()}]{eventType}"
            if not noPrint:
                print(eventStr)
            self.logs[category][now] = eventStr + f": {event}\n{trace}" + "\n\n" if trace else "\n\n"
        else:
            eventStr = f"{timestamp}-[{classStr.upper()}::{funcStr.upper()}]{eventType}: {event}"
            if not noPrint:
                print(eventStr)
            self.logs[category][now] = eventStr + ("\n" + trace if trace else "") + "\n\n"


# The logger instance used throughout BountyBot. TODO: To be moved to bbGlobals.
bbLogger = logger()
