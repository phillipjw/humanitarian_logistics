import numpy as np

class SocialRelationship():
    
    INITIAL_CONNECTION_WEIGHT_MIN = 0.10
    INITIAL_CONNECTION_WEIGHT_MAX = 0.40
    ACTIVITY_INCREMENT = 0.10
    DECAY_DECREMENT = 0.05
    MAX_WEIGHT = 1.0
    MIN_WEIGHT = 0.0
      
    def __init__(self, agent, similarity):
    # initializes an empty social network  
        self.connection = agent
        diff_between_min_and_max = SocialRelationship.INITIAL_CONNECTION_WEIGHT_MAX - SocialRelationship.INITIAL_CONNECTION_WEIGHT_MIN
        new_min_value = SocialRelationship.INITIAL_CONNECTION_WEIGHT_MAX - (diff_between_min_and_max*(1.0-similarity))
        weight = np.random.uniform(low=new_min_value, 
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
          