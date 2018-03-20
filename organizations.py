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
        
class COA(Organization):
    
    def __init__(self, unique_id, model, city):
        super().__init__(unique_id, model)
        
        self.azcs = set([])
        self.capacities = dict()
        self.average_capacities = self.capacities
        self.model = model
        self.assessment_frequency = 30      #monthly checks
        self.projection_time = 180          #6 month conditions, given 5 month construction time
        self.budget = 10000                 #arbitrary and to be replaced
        self.city = city
        
        #online variance calculations
        self.occupancy_frequency = 15
        self.occupancy_counter = 1
        self.sum_capacities = self.capacities
        self.squared_capacities = dict()
        self.variance = dict()
        
        
        
        
    def evaluate_need(self,building, projection):
        '''
        How many newcomers need housing
        '''
        
        return projection - building.capacity
    
    def project(self, building):
        
        difference = building.occupancy - self.capacities[building]
        
        delta = difference / self.assessment_frequency #assuming monthly assessment
        
        return self.capacities[building] + delta*self.projection_time
    
    def evaluate_cost(self, need, building):
        
        if type(building) is Empty:
            return building.convert_cost
        elif type(building) is Hotel:
            return need*building.cost_pp
        
    def get_buildings(self, available):
        
        '''
        help function to get a list of buildings of a given type
        '''
        
        if available == False:
            
            return self.city.buildings
        else:
            return [building for building in self.city.buildings
                    if building.available]
            
    def online_mean(self):
        
        for building,occupancy in self.capacities.items():
                
                self.average_capacities[building] += self.capacities[building] / self.occupancy_counter
                
                
                
    def online_variance(self):
        
        
        for building,occupancy in self.capacities.items():
            
            self.sum_capacities[building] += building.occupancy
            
            self.squared_capacities[building] += np.square(building.occupancy)
            
            self.variance[building] = np.sqrt((self.occupancy_counter *
                         self.squared_capacities[building] -
                         self.sum_capacities[building]**2) / 
                         (self.occupancy_counter*(self.occupancy_counter-1)))
            
            

        
        
            
        
        
        
    def step(self):
        
        if self.model.schedule.steps > 2:
            if self.model.schedule.steps % self.occupancy_frequency == 0:
                
                
                self.occupancy_counter += 1
                
                self.online_mean()
                self.online_variance()
                
                print('avg cap',self.average_capacities)
                print('var',self.variance)
        else:
            self.squared_capacities = {k:self.capacities[k]**2 for
                                       k in self.capacities.keys()}
            
            
        
        if self.model.schedule.steps % 30 == 0:
                        
            for k,v in self.capacities.items():
                
                #project growth rate onto 6 months
                projection = self.project(k)
                

                #update capacities
                self.capacities[k] = k.occupancy
                
                #check if problematic
                if projection > k.capacity:
                    
                    print('PROBLEMATIC')
                    
                    need = self.evaluate_need(k, projection)
                    
                    #get list of candiate buildings
                    candidates = self.get_buildings(True)
                    
                    #get cost per candidate
                    for candidate in candidates:
                        costs = self.evaluate_cost(need, candidate)
                           
                    #asdf
                    pass
                
                
        

        
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
        
        self.capacity = 400
        self.occupants = set([])
        self.occupant_type = occupant_type
        self.pos = pos
        self.available = False
        


    def step(self):
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
    
class Empty(Building):
    '''
    Empty buildings have a refurbishing cost
    and can be converted into AZCs
    '''
    def __init__(self, unique_id, model,
                 pos, convert_cost):
        super().__init__(unique_id, model)
        
        self.capacity = 1000
        self.occupants = set([])
        self.pos = pos
        self.convert_cost = convert_cost
        self.available = True