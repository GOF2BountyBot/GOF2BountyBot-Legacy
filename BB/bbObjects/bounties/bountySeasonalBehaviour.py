from . import bbBountyConfig, bbBounty

class BountyBehaviourModifier:
    def configWillGenerate(self, config: "bbBountyConfig.BountyConfig"):
        pass

    def bountyWasDefeated(self, bounty: "bbBounty.Bounty"):
        pass

class BountyBehaviourSpecification:
    