from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import List
from ..baseClasses.bbSerializable import bbSerializable

@dataclass
class StatRaceReward(bbSerializable):
    item: dict
    fixedPlace: int

    def toDict(self, **kwargs) -> dict:
        return {
            "item": json.dumps(self.item),
            "fixedPlace": self.fixedPlace
        }


    @classmethod
    def fromDict(cls, data : dict, **kwargs) -> "StatRaceReward":
        return StatRaceReward(
            item=data["item"], 
            fixedPlace=data["fixedPlace"])

@dataclass
class StatRace(bbSerializable):
    rewards: List[StatRaceReward]
    startDate: datetime
    endDate: datetime
    deltaMode: bool
    orderAsc: bool
    statName: str

    def toDict(self, **kwargs) -> dict:
        return {
            "rewards": [r.toDict() for r in self.rewards],
            "startDate": self.startDate.timestamp(),
            "endDate": self.endDate.timestamp(),
            "deltaMode": self.deltaMode,
            "orderAsc": self.orderAsc,
            "statName": self.statName
        }


    @classmethod
    def fromDict(cls, data : dict, **kwargs) -> "StatRace":
        return StatRace(
            rewards=[StatRaceReward.fromDict(r) for r in data["rewards"]],
            startDate=datetime.fromtimestamp(data["startDate"], timezone.utc),
            endDate=datetime.fromtimestamp(data["endDate"], timezone.utc),
            deltaMode=data["deltaMode"],
            orderAsc=data["orderAsc"],
            statName=data["statName"])