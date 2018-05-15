from mesa import Agent, Model
from random import randrange
from random import uniform
from operator import attrgetter
import numpy as np
from viz import AZC_Viz
from mesa.datacollection import DataCollector
from Values import Values

import activity





class City(Agent):
    '''
    A city contains buildings
    '''
    
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.auxiliary_housing = 0

        
        

    def step(self):
        pass
        
        



class Organization(Agent):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
        """
        Generic Starter class for Organizations,
        to be adapted to Gov and NGO and the like
        """
        self.unique_id = unique_id
        self.model = model
        
class COA(Organization):
    
    def __init__(self, unique_id, model, city):
        super().__init__(unique_id, model)
        
        self.azcs = set([])
        self.ind = None
        self.pos = None
        
        self.newcomer_payday = 0
        self.self_enhancement = 20
        self.self_transcendence = 70     
        self.conservatism = 30
        self.openness_to_change = 20
        self.values = Values(10, self.self_enhancement, self.self_transcendence,
                             self.conservatism, self.openness_to_change)
        
    def find_house(self, newcomer):
        '''finds min occupancy building for a given legal status
        '''
        candidates = [building for building in self.model.schedule.agents if
                    type(building) is AZC and
                    newcomer.ls in building.occupant_type]
        min_type = min(candidates, key = attrgetter('occupancy'))
        return min_type
    
    def get_total_cap(self):
        '''total available room'''
        
        return sum([azc.capacity for azc in self.azcs])
    
    def get_total_occupancy(self):
        '''total occupied space'''
        
        return sum([azc.occupancy for azc in self.azcs])
    
    def get_occupancy_pct(self):
        '''room to space ratio'''
        
        return self.get_total_occupancy() / (self.get_total_cap() + 1)
    
    def intake(self, newcomer, destination):
        destination.occupants.add(newcomer)

        destination.occupancy += 1 #update occupancy 
        
        newcomer.loc = destination
        
         
    def house(self, newcomer):
        
            
        newcomer.loc.occupants.remove(newcomer)
        newcomer.loc.occupancy -= 1
        destination = self.find_house(newcomer)
        destination.occupants.add(newcomer)

        destination.occupancy += 1 #update occupancy 
        
        newcomer.loc = destination
        newcomer.coa = destination.coa
        
        
        
        
            
      
    
    def step(self):
        print(self.occupancy / self.capacity)
        
        

        

        
            
        
class NGO(Organization):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
        '''
        Basic NGO class
        
        '''

        
        
class IND(Organization):
    
    def __init__(self, unique_id, model, city, coa):
        super().__init__(unique_id, model)
        
        self.processing_rate = None
        self.max_time = 270
        self.min_time = 8
        self.coa = coa
        self.city = city
        self.pos = self.coa.pos
        
    def set_time(self, newcomer):
        if newcomer.ls == 'as':
            capacity = self.coa.get_occupancy_pct()
            time = 90*capacity + 8
            newcomer.current_decision_time = int(time)
        elif newcomer.ls == 'as_ext':
            newcomer.decision_time = 90
        elif newcomer.ls == 'tr':
            newcomer.decision_time = 100
    
    def decide(self, first, newcomer):
        
        
        if first:
            return newcomer.first == 1
        else:
            return newcomer.second == 1
        
    
                           
                    
                    
                
class Building(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
         
        self.capacity = 0
        self.occupants = set([])
        
        self.occupancy = 0
    
    def step(self):
        pass


class AZC(Building):
    def __init__(self, unique_id, model, occupant_type,coa, modality):
        super().__init__(unique_id, model)
        
        self.capacity = 400
        self.occupants = set([])
        self.occupant_type = occupant_type
        self.procedure_duration = None
        self.coa = coa
        self.operating_capacity = None
        self.occupancy = 0
        self.modality = modality
       

        if self.modality == 'POL':
            

            self.pos = (unique_id*self.model.space_per_city + .25*(self.model.space_per_city), int(self.model.height / 3))
            
            
        elif self.modality == 'AZC':
            
            orientation_x = int(self.model.space_per_azc * unique_id + self.model.space_per_azc)

            self.pos = (orientation_x, int(self.model.height / 2))
        elif self.modality == 'COL':
            
            self.pos = (self.model.width / 2, self.model.height - 10)

            
            
        self.coa.pos = self.pos    
        self.model.schedule.add(self)
        self.model.grid.place_agent(self,self.pos)
    def step(self):
        
        super().step()
        pass


         

class Hotel(Building):
    '''
    Hotels are commerical buildings
    they have a cost p room p person
    '''
    
    def __init__(self, unique_id, model,
                 pos, cost_pp):
        super().__init__(unique_id, model)
        
        self.capacity = 1000
        self.occupants = set([])
        self.pos = pos
        self.cost_pp = cost_pp
        self.available = True
        self.calculated_value = None
        self.city = None
        self.activity_center = None
    
 
        
        
        
    
class Empty(Building):
    '''
    Empty buildings have a refurbishing cost
    and can be converted into AZCs
    '''
    def __init__(self, unique_id, model,
                 pos, capacity, proximity):
        super().__init__(unique_id, model)
        
        self.proximity = proximity
        self.capacity = capacity
        self.occupants = set([])

    def step(self):
        super().step()

            
        
