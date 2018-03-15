from mesa import Agent, Model
from random import randrange
from random import uniform
import numpy as np

class City(Agent):
    '''
    A city contains buildings
    '''
    
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        
        self.buildings = set([])
        self.pos = pos
        



class Organization(Agent):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
        """
        Generic Starter class for Organizations,
        to be adapted to Gov and NGO and the like
        """
        self.unique_id = unique_id
        self.model = model
        

        
class NGO(Organization):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
        '''
        Basic NGO class
        
        '''

        
        
class IND(Organization):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
        self.processing_rate = None
                           
                    
                    
                
class Building(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
         
        self.capacity = 0
        self.occupants = set([])
        
        self.occupancy = 0
        


class AZC(Building):
    def __init__(self, unique_id, model,occupant_type, pos):
        super().__init__(unique_id, model)
        
        self.capacity = 0
        self.occupants = set([])
        self.occupant_type = occupant_type
        self.pos = pos


    def step(self):
        pass