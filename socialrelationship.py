import numpy as np

class SocialRelationship():
    
    INITIAL_CONNECTION_WEIGHT_MIN = 0.10
    INITIAL_CONNECTION_WEIGHT_MAX = 0.50
    ACTIVITY_INCREMENT = 0.10
    DECAY_DECREMENT = 0.05
    MAX_WEIGHT = 1.0
    MIN_WEIGHT = 0.0
      
    def __init__(self, agent):
    # initializes an empty social network  
        self.connection = agent
        weight = np.random.uniform(low=SocialRelationship.INITIAL_CONNECTION_WEIGHT_MIN, 
                                   high=SocialRelationship.INITIAL_CONNECTION_WEIGHT_MAX)
        self.weight = weight
    
    def __eq__(self, other): 
        return self.connection.unique_id == other.connection.unique_id
    
    def incrementWeight(self):
        self.weight = self.weight + SocialRelationship.ACTIVITY_INCREMENT
        self.weight = min(self.weight, SocialRelationship.MAX_WEIGHT)

    def decrementWeight(self):
        self.weight = self.weight - SocialRelationship.DECAY_DECREMENT
        self.weight = max(self.weight, SocialRelationship.MIN_WEIGHT)
          