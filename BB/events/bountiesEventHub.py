import asyncio
from typing import Any, Awaitable, Set, Protocol

from ..bbObjects.bounties import bbBounty

class BountyDefeatEventHandler(Protocol):
    def __call__(self, bounty: "bbBounty.Bounty") -> Awaitable[Any]: ...

class BountiesEventHub:
    def __init__(self) -> None:
        self.listeners: Set[BountyDefeatEventHandler] = set()

    def onBountyDefeated(self, bounty: "bbBounty.Bounty") -> asyncio.Task:
        return asyncio.create_task(asyncio.wait(l(bounty) for l in self.listeners))
    
    def subscribeBountyDefeated(self, handler: BountyDefeatEventHandler):
        self.listeners.add(handler)
    
    def unsubscribeBountyDefeated(self, handler: BountyDefeatEventHandler):
        if handler in self.listeners:
            self.listeners.remove(handler)
