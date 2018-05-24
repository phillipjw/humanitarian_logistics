from socialrelationship import SocialRelationship
class SocialNetwork():
    
    # based on this paper https://www.sciencedirect.com/science/article/pii/S0140366412002642
    # which shows average social network size people can maintain is ~ 150ish
    # in future version we can set this up to vary based on the individual
    MAX_SIZE = 150.0
    
    def __init__(self):
        # initializes an empty social network
          
        self.max_size = SocialNetwork.MAX_SIZE
        self.network = []
    
    def addRelationship(self, relationship):
        if len(self.network) < self.max_size:
            self.network.append(relationship)

    def bondWithAgent(self, agent):
        relationship = SocialRelationship(agent)
        if (relationship in self.network) == False:
            self.addRelationship(relationship)
        else:
            indexOfRelationship = self.network.index(relationship)
            self.network[indexOfRelationship].incrementWeight
    
    def decayRelationships(self):
        for relationship in self.network:
            relationship.decrementWeight()
              
    def maintainNetwork(self):
        networkcopy = []
        for relationship in self.network:
            if relationship.weight > 0:
                networkcopy.append(relationship)
        self.network = networkcopy