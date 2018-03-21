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
        self.var_copy = None
        self.shock = False
        
        #ter apel shock check
        self.sum_ta = 0 
        self.squared_ta =  0 
        self.counter_ta = 1
        self.variance_ta = None
        self.var_copy_ta = None
        self.ter_apel = None
        
        
        
        
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
                
                
                

        
        
      '''  

      
        
        
        

        
        
        
    
    def online_variance(self):
        
        self.var_copy = self.variance
        
        if self.shock:
            shock_ = False
            for building,occupancy in self.capacities.items():
                if building.occupancy / self.variance[building] > 3:
                    print('shock')
                    shock_ = True
                if not shock_:
                    self.shock = False
                    print('Shock Over')
        else:
                    
                    
                
        
        
            for building,occupancy in self.capacities.items():
                
                self.sum_capacities[building] += building.occupancy
                
                self.squared_capacities[building] += np.square(building.occupancy)
                
                self.variance[building] = np.sqrt((self.occupancy_counter *
                             self.squared_capacities[building] -
                             self.sum_capacities[building]**2) / 
                             (self.occupancy_counter*(self.occupancy_counter-1)))
        
                if building.occupancy / self.variance[building] > 3:  #if current occupancy is an outlier
                    print('shock')
                    self.shock = True
                    self.variance = self.var_copy
                    break
 
        

            
            
     ''' 
        
        
    def shock_check(self):
        
        #how many currently entering
        
        
        #current variance of ter apel
        test = self.online_variance_ta(ter_apel)
        
        if ter_apel.occupancy / test[0] > 3:
            print('shock')
        else:
            print('no shock')
            self.variance_ta, self.squared_ta, self.sum_ta = test
    
    def online_variance_ta(self, building):
        
        '''
        Calculates online variance for anomoly detection
        '''
        
        self.counter_ta += 1
        
        sum_ta = self.sum_ta
        squared_ta = self.squared_ta
        variance_ta = self.variance_ta
        
        sum_ta += building.occupancy
        squared_ta += building.occupancy**2
        variance_ta = np.sqrt((self.counter_ta * 
                                    self.squared_ta - 
                                    self.sum_ta**2) / 
                                    (self.counter_ta*(self.counter_ta - 1)))
        
        return (variance_ta, squared_ta, sum_ta)            
        
        
        
    def step(self):
        
        '''
        COA is essentially checking for anomalies in the 'Ter Apel'
        If detected, inspects the gravity of the anomoly and acts
        accordingly
        '''
    
        if self.model.schedule.steps < self.model.shock_period / 2:
            
            # start calculting variances
            self.variance_ta, self.squared_ta, self.sum_ta = self.online_variance_ta(self.ter_apel)
        else:
            
            if self.model.schedule.steps % self.assessment_frequency == 0:
                #check variance of current point
                variance_ta, squared_ta, sum_ta = self.online_variance_ta(self.ter_apel)
                if self.ter_apel.occupancy / variance_ta > 3:
                    print('shock')
                    self.shock = True
                else:
                    print('no shock')
                    self.variance_ta, self.squared_ta, self.sum_ta = variance_ta, squared_ta, sum_ta
        if shock:
            
            #project error
            
            
            
    
        
'''
            
            
        
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
        '''
                
                
        

        
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