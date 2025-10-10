from typing import Callable, Set, Type, Union
from ..bounties import bbBounty

class NoIntercept: pass
    
class DefaultBountyMessageFormatIntercept:
    def formatCriminalName(self, bounty: bbBounty.Bounty) -> str:
        return bounty.criminal.name.title()
    
    def formatBountyBoardListingDescription(self, bounty: bbBounty.Bounty) -> str:
        return ""


class BountyMessageFormatIntercept:
    defaultFormat = DefaultBountyMessageFormatIntercept()

    def formatCriminalName(self, bounty: bbBounty.Bounty) -> Union[str, Type[NoIntercept]]:
        return NoIntercept
    
    def formatBountyBoardListingDescription(self, bounty: bbBounty.Bounty) -> Union[str, Type[NoIntercept]]:
        return NoIntercept


class BountyMessageFormatter:
    def __init__(self) -> None:
        self._activeInterceptors: Set[BountyMessageFormatIntercept] = {BountyMessageFormatIntercept()}

    def activateInterceptor(self, interceptor: BountyMessageFormatIntercept):
        if type(interceptor) is BountyMessageFormatIntercept:
            raise ValueError("The default format interceptor is always active.")
        
        self._activeInterceptors.add(interceptor)

    def deactivateInterceptor(self, interceptor: BountyMessageFormatIntercept):
        if type(interceptor) is BountyMessageFormatIntercept:
            raise ValueError("The default format interceptor is always active.")
        
        if interceptor in self._activeInterceptors:
            self._activeInterceptors.remove(interceptor)

    def _format(self, callInterceptor: Callable[[Union[BountyMessageFormatIntercept, DefaultBountyMessageFormatIntercept]], Union[str, Type[NoIntercept]]]) -> str:
        for formatter in self._activeInterceptors:
            intercepted = callInterceptor(formatter)
            if isinstance(intercepted, str):
                return intercepted
            
        default = callInterceptor(BountyMessageFormatIntercept.defaultFormat)
        if not isinstance(default, str):
            raise RuntimeError("No default format")
        
        return default
    
    def formatCriminalName(self, bounty: bbBounty.Bounty) -> str:
        return self._format(lambda f: f.formatCriminalName(bounty))
    
    def formatBountyBoardListingDescription(self, bounty: bbBounty.Bounty) -> str:
        return self._format(lambda f: f.formatBountyBoardListingDescription(bounty))