import mesa
from mesa import Agent, Model

class Activity(Agent):
    
    def __init__(self, unique_id, model, frequency=1, se=0, st=0, c=0, otc=0):
       
    
        '''
        An activity is an event which recurs with a particular weekly 
        frequency and satisfies a particular value for the newcomers.
        '''
        super().__init__(unique_id, model)   
        self.frequency = frequency
	
        # SE corresponds to an activity that provides betterment of one’s 
	    # own attributes through either enhancement
        # of already owned resources, corresponding to achievement, or the enhanced control of resource
        # acquisition, corresponding to power
        self.se = se
    
        # ST satisfaction providing an activity where the betterment of
        # another agent’s attributes, as per its component values, benevolence and universalism
        self.st=st
    
        # C, which is an activity providing tradition, conformity and security.
        self.c =c
    
        # OTC is an activity providing stimulation and hedonism
        self.otc =otc
    
    
    def step(self):
        print(self.weekly_frequency)