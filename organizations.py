from mesa import Agent, Model
from random import randrange
from random import uniform
from operator import attrgetter
import numpy as np
from viz import AZC_Viz

class City(Agent):
    '''
    A city contains buildings
    '''
    
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        
        self.buildings = set([])
        self.pos = pos
        self.social_housing = None
        self.coa = None
        
        
        



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
        self.assessment_frequency = 15      #monthly checks
        self.projection_time = 180          #6 month conditions, given 5 month construction time
        self.budget = 10000                 #arbitrary and to be replaced
        self.city = city
        self.newcomers = set([])
        self.shock_assessment_frequency = 10
        self.shock_threshold = 5
        self.capacity_threshold = .75
        self.buildings_under_construction = set([])
        

        self.shock = False                 # is current influx an anomoly 
        self.crisis = False                # is there sufficient housing 
                                           # for current influx
        self.problematic = False           # is change in policy required
        
        #ter apel shock check
        self.sum_ta = 0 
        self.squared_ta =  0 
        self.counter_ta = 1
        self.variance_ta = None
        self.var_copy_ta = None
        self.ter_apel = None
        
        #policies
        self.policy = self.house
    
    def decide(self, first, newcomer):
        
        if first:
            return newcomer.first == 1
        else:
            return newcomer.second == 1
        
    def house(self, newcomer):
        
        destination = [azc for azc in self.azcs if
                       azc.occupant_type == newcomer.ls][0]
        
        
        self.move(newcomer, destination)
          
        
    def social_house(self, newcomer):
        
        
        destination = self.city.social_housing
        
        
        self.move(newcomer, destination)
    
    def move(self, newcomer, destination):
        
        newcomer.loc.occupancy -= 1 
        destination.occupancy += 1 #update occupancy 

        #take first one, in future, evaluate buildings on some criteria
        house_loc = destination.pos         #where is it
        
        #add noise so agents don't overlap
        x = house_loc[0] #+ np.random.randint(-20,20)
        y = house_loc[1] - 10 + int(20*((1+ destination.occupancy) / destination.capacity))
        
        
        self.model.grid.move_agent(newcomer, (x,y)) #place
        
        destination.occupants.add(newcomer) #add agent to building roster
        newcomer.loc = destination #update agent location
        
        
        
        
    def min_house(self, newcomer):
        
        destination = min(self.azcs, key = attrgetter('occupancy'))
        
        self.move(newcomer, destination)
        
    
    def get_total_cap(self):
        
        return sum([azc.capacity for azc in self.azcs])
    
    def get_total_occupancy(self):
        
        return sum([azc.occupancy for azc in self.azcs])
        
    def hotel_house(self, newcomer):
        '''
        min-house till near max, then send to hotel
        '''
        #until there's no room, house in azc
        if self.get_total_occupancy() / self.get_total_cap() < .90:
            self.min_house(newcomer)
        #then house in hotel
        else:
            
            destination = [x for x in self.city.buildings if
                           type(x) is Hotel][0]
            
            self.move(newcomer, destination)
            
            
                
        
        
        
        
    def evaluate_need(self,building, projection):
        '''
        How many newcomers need housing
        '''
        
        return projection - building.capacity
    
    def project(self, building):
        
        difference = building.occupancy - self.capacities[building]
        
        delta = difference / self.assessment_frequency #assuming monthly assessment
        
        return self.capacities[building] + delta*self.projection_time, delta
    
    def evaluate_cost(self, need, building):
        
        if type(building) is Empty:
            return building.convert_cost
        elif type(building) is Hotel:
            return need*building.cost_pp
          
    
        
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
        
     
    def shock_check(self,variance_ta):
        return self.ter_apel.occupancy / variance_ta > self.shock_threshold
    
    def update_capacities(self):
        #update monthly rate of change 
        for k,v in self.capacities.items():
            
            self.capacities[k] = k.occupancy
            
    def problematic_check(self):
        
        problematic = False 
        #look at rate of change for each building
        for building, occupancy in self.capacities.items():
            
            #project rate of growth
            project = self.project(building)
            
            #update capacities    
            self.capacities[building] = building.occupancy
            
            if project[0] > building.capacity*self.capacity_threshold:
                print('Problematic')
                problematic = True
                break                         
            else:
                print('Manageable')
                #all must be manageable for normal housing policies
        return problematic
    
    def crisis_check(self):
        
        '''
        Checks if the projected amount of inflow is 
        greater than the capacity in the city
        '''

        
        total_need = 0
        
        #takes into account future capacities if building under construction
        if self.buildings_under_construction:
            total_need -= sum([x.capacity for x in
                               self.buildings_under_construction])
        
        for building, occupancy in self.capacities.items():
            
            #how many in 6 months
            project = self.project(building)
            
            #difference between that and occupancy
            total_need += self.evaluate_need(building, project[0])
            
        return (total_need > 0, total_need)
        
        
            
    def evaluate_options(self, need):
        
        '''
        if in crisis, check cost of each
        hotel v empty building conversion
        need = amount of people over capacity
        '''
        #placeholder
        average_duration = 50
        
        #gather candidates
        hotel = [x for x in self.city.buildings
                 if type(x) is Hotel][0]
        candidates = [x for x in self.city.buildings if
                   type(x) is Empty]
        
        candidates.append(hotel)
        
        #calculate values
        for candidate in candidates:
            candidate.calc_cost(need, average_duration)
        
        #find max value, need:cost ratio
        best = max(candidates, key = attrgetter('calculated_value'))

        #return policy
        return best
     
        
    def convert(self, building):
        
        #remove
        new_azc = AZC(building.unique_id,building.model,
                      'as_ext', building.pos, self)
        azc_viz = AZC_Viz(self.model, new_azc)
        self.model.schedule.add(azc_viz)
        self.model.grid.place_agent(azc_viz, azc_viz.pos)
        self.model.schedule.add(new_azc)
        self.model.grid.place_agent(new_azc, building.pos)
        self.city.buildings.add(new_azc)
        self.azcs.add(new_azc)
        self.city.buildings.remove(building)
        self.buildings_under_construction.remove(building)
        self.model.schedule.remove(building)
        self.model.grid.remove_agent(building)
        
        
    def construct(self, building):
        
        building.under_construction = True
        self.buildings_under_construction.add(building)
             
                
        
    def step(self):
        
        '''
        COA is essentially checking for anomalies in the 'Ter Apel'
        If detected, inspects the gravity of the anomoly and acts
        accordingly
        '''
        
        
        #gives the model time to build of a distribution of normal flow
        if self.model.schedule.steps < self.model.shock_period / 2:
            
            # start calculting variances
            self.variance_ta, self.squared_ta, self.sum_ta = self.online_variance_ta(self.ter_apel)
        
        #starts checking for anamolies
        else:
            
            #only with a certain frequency so as not to slow it down
            if self.model.schedule.steps % self.assessment_frequency == 0:
                #check variance of current point
                
                variance_ta, squared_ta, sum_ta = self.online_variance_ta(self.ter_apel)
                if self.shock_check(variance_ta):
                    print('shock')
                    self.shock = True
                    
                    
                #if no anomoly add to normal flow distribution    
                else:
                    print('no shock')
                    self.variance_ta, self.squared_ta, self.sum_ta = variance_ta, squared_ta, sum_ta
                    self.shock = False
                    self.policy = self.house
                    
                    self.update_capacities()
        
        #only during shock periods project
        if self.shock:
            
            if self.model.schedule.steps % self.assessment_frequency == 0:
                
                if self.problematic:
                    cc = self.crisis_check()
                    if cc[0]:
                        self.crisis = True
                        print('Crisis')
                        
                        decision = self.evaluate_options(cc[1])
                        if type(decision) is Hotel:
                            self.policy = self.hotel_house
                        else:
                            self.policy = self.hotel_house
                            #convert decision
                            
                            self.construct(decision)
                         
                    else:
                        self.crisis = False
                        self.problematic = False #forcing reevaluation.
                
                else:

                    #check for problematic
                    if self.problematic_check():
                        self.problematic = True
                        self.policy = self.min_house
                    else:
                        self.policy = self.house
                        self.problematic = False
            
                
                        
                        

            
   

    def intake(self,newcomer):       
        
        #take first one, in future, evaluate buildings on some criteria
        house_loc = self.ter_apel.pos         #where is it
        

        
        self.ter_apel.occupancy += 1
        
        #add noise so agents don't overlap
        x = house_loc[0] #+ np.random.randint(-20,20)
        y = house_loc[1] - 10 + int(20*((1+self.ter_apel.occupancy) / self.ter_apel.capacity))
        
        self.model.grid.move_agent(newcomer, (x,y)) #place
        
        self.ter_apel.occupants.add(newcomer) #add agent to building roster
        newcomer.loc = self.ter_apel #update agent location
        
         #update occupancy           
            
        
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
    def __init__(self, unique_id, model, occupant_type, pos, coa):
        super().__init__(unique_id, model)
        
        self.capacity = 400
        self.occupants = set([])
        self.occupant_type = occupant_type
        self.pos = pos
        self.available = False
        
        self.coa = coa
        


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
        self.calculated_value = None
        self.city = None
    
    def calc_cost(self, need, average_duration):
        
        hotel_cost = need*average_duration*self.cost_pp/30
        self.calculated_value = need / hotel_cost
        
        
        
        
    
class Empty(Building):
    '''
    Empty buildings have a refurbishing cost
    and can be converted into AZCs
    '''
    def __init__(self, unique_id, model,
                 pos, capacity):
        super().__init__(unique_id, model)
        
        self.capacity = capacity
        self.occupants = set([])
        self.pos = pos
        self.convert_cost = self.capacity * 1000 * .80
        self.available = True
        self.calculated_value = None
        self.under_construction = False
        self.construction_time = 180
        self.city = None
        
    def calc_cost(self, need, average_duration):
        
        self.calculated_value = need / self.convert_cost
    def step(self):
        
        if self.under_construction == True:
            self.construction_time -= 1
        if self.construction_time == 0:
            self.under_construction = False
            self.city.coa.convert(self)
            
        