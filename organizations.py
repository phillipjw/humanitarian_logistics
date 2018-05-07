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
    
    def __init__(self, unique_id, model, pos, is_big=False):
        super().__init__(unique_id, model)
        
        self.buildings = set([])
        self.pos = pos
        self.social_housing = None
        self.social_housing_supply = None
        self.cost_of_bus_within_city = 4
        self.cost_of_bus_to_another_city = 18.50
        self.coa = None
        self.big_city = is_big
        if self.big_city == True:
            self.resources = 100
        else:
            self.resources = 50      

    def step(self):
        for i in self.buildings:
            if i.health < 100:
                if self.resources > 0:
                    i.health = i.health+1
                    self.resources = self.resources -1
        
        



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
        self.activity_centers = set([])
        self.activity_cost = 5000
        self.activity_budget = 30000
        self.activity_center_cost = 20000 #abitrary and to be replaced
        self.capacities = dict()
        self.average_capacities = self.capacities
        self.model = model
        self.assessment_frequency = 30      #monthly checks
        self.projection_time = 180          #6 month construction time
        self.budget = 300000                 #arbitrary and to be replaced
        self.city = city
        self.newcomers = set([])
        self.shock_assessment_frequency = 10
        self.shock_threshold = 5
        self.capacity_threshold = .75
        self.buildings_under_construction = set([])
        
        #newcomer pay params
        self.newcomer_allowance = 50
        self.newcomer_payday = 0

        self.shock = False                 # is current influx an anomoly 
        self.crisis = False                # is there sufficient housing 
        self.need = None                   # for current influx
        self.problematic = False           # is change in policy required
        self.shock_reference = None
        self.delta = None                  #rate of change
        
        #ter apel shock check
        self.sum_ta = 0 
        self.squared_ta =  0 
        self.counter_ta = 1
        self.variance_ta = None
        self.var_copy_ta = None
        
        
        #policies
        self.policy = self.house
        self.collection_fee = 194
        self.IND = None
        
        self.ta = False
        
        # coa values
        
        # self_enhancement actions actions increase available capital, 
        # such as consolidation which involves transferring newcomers
        # from low capacity AZCs into a few high capacity AZC. Empty AZCs can either be sold off or
        # operated at minimal cost until required. During shock periods, 
        # COA can satisfy SE by requesting additional government funding.
        self.self_enhancement = 20
        
        # COA satisfies ST by investing its available capital to improve living
        # conditions for its residents. Available capital is invested facilities, 
        # which are a generic building which can host activities, aimed at satisfying 
        # newcomer values. During shock periods, providing housing to newcomers over 
        # the current capacity satisfies ST.
        self.self_transcendence = 70
        
        # COA satisfies C by employing "safe but segregated" policies. That is,
        # separating newcomers by legal status and targeting service delivery on 
        # those who will likely receive status. During shock-periods, C is satisfied 
        # by building robust facilities. That is, favoring AZC developments with a 
        # degree of redundancy; two 100 capacity AZCs instead of one 200, for example.
        self.conservatism = 30
        
        # COA satisfies OTC by employing integration policies which are available
        # to all AS newcomers, regardless of the likelihood of their final status. 
        # During shock periods periods, OTC is satisfied by the construction of 
        # flexible housing. Flexibility, here, means ability to serve multiple functions. 
        # Such housing could serve local populations post shock.
        self.openness_to_change = 20
        
        self.values = Values(10, self.self_enhancement, self.self_transcendence,
                             self.conservatism, self.openness_to_change)
        
        
        #####ACTIONS######
        self.actions = set([])
        self.action_names = ['Consolidate', 'Invest', 'Segregate', 'Integrate']
        self.crisis_names = ['RequestFunds', 'BuildClose', 'BuildRobust', 'BuildFlex']
        
        #add actions to action set
        for action in range(len(self.action_names)):
            
            #make action w a name, actor, and index of value to be satisfied

            if action == 0:
                current_action = activity.Consolidate(self.action_names[action], self,action)
                self.actions.add(current_action)
                current_action = activity.RequestFunds(self.crisis_names[action], self,action)
                self.actions.add(current_action)
            elif action == 1:
                current_action = activity.Invest(self.action_names[action], self,action)
                self.actions.add(current_action)
                current_action = activity.BuildCentral(self.crisis_names[action], self,action)
                self.actions.add(current_action)
            elif action == 2:
                current_action = activity.Segregate(self.action_names[action], self,action)
                self.actions.add(current_action)
                current_action = activity.BuildRobust(self.crisis_names[action], self,action)
                self.actions.add(current_action)
            elif action == 3:
                current_action = activity.Integrate(self.action_names[action], self,action)
                self.actions.add(current_action)
                current_action = activity.BuildCentral(self.crisis_names[action], self,action)
                self.actions.add(current_action)
                
            
            
            

        
    def house(self, newcomer):
        
        #candidates
        candidates = []
        
        #find all coas
        coas = [coa for coa in self.model.schedule.agents if
                type(coa) is COA]
        
        #not ter appel 
        coas = [coa for coa in
                coas if
                not coa.ta]
        
        #only relevant azcs
        for coa in coas:
            for azc in coa.azcs:
                if azc.occupant_type == newcomer.ls:
                    candidates.append(azc)
     
        destination = min(candidates, key = attrgetter('occupancy'))
        
        

        self.move(newcomer, destination)
    
    def pay_allowance(self, newcomer):
        
        newcomer.budget += self.newcomer_allowance
          
        
    def social_house(self, newcomer):
        '''
        Add newcomer to TR housing
        '''        
        
        destination = self.city.social_housing
        
        self.move(newcomer, destination)
    
    def move(self, newcomer, destination):
        '''
        moves newcomer to a destination
        updates occupancies of previous and new destinations
        '''

        newcomer.loc.occupancy -= 1 
        if newcomer in newcomer.loc.occupants:
            newcomer.loc.occupants.remove(newcomer)
        destination.occupancy += 1 #update occupancy 
        
        
        #take first one, in future, evaluate buildings on some criteria
        house_loc = destination.pos         #where is it
    
        self.model.grid.move_agent(newcomer, house_loc) #place

        destination.occupants.add(newcomer) #add agent to building roster

        newcomer.loc = destination #update agent location
        
        if type(destination) is Hotel:
            newcomer.coa = destination.city.coa
        else:
            newcomer.coa = destination.coa
        
        
        
        
    def min_house(self, newcomer):
        '''COA policy houses newcomer
        in the most empty AZC
        '''
        
        #candidates
        candidates = []
        
        #find all coas
        coas = [coa for coa in self.model.schedule.agents if
                type(coa) is COA]
        
        #not ter appel 
        coas = [coa for coa in
                coas if
                not coa.ta]
        
        #only relevant azcs
        for coa in coas:
            for azc in coa.azcs:
                candidates.append(azc)
     
        destination = min(candidates, key = attrgetter('occupancy'))
        
  
        self.move(newcomer, destination)
                
    
    def get_total_cap(self):
        '''total available room'''
        
        return sum([azc.capacity for azc in self.azcs])
    
    def get_total_occupancy(self):
        '''total occupied space'''
        
        return sum([azc.occupancy for azc in self.azcs])
    
    def get_occupancy_pct(self):
        '''room to space ratio'''
        
        return self.get_total_occupancy() / (self.get_total_cap() + 1)
        
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
            self.budget -= destination.cost_pp
        
    def evaluate_need(self,building, projection):
        '''
        How many newcomers need housing
        '''
        
        return projection - building.capacity
    
    def project_dc(self):
        
        total = 0
        
        #delta begins as null bc it requires a shock to be activated
        if not self.delta:
            total = self.get_total_occupancy()
        else:
            
            for azc in self.azcs:

                total += self.delta*180
                
                '''
                if self.shock:
                    total += self.project_2(azc)[0]
                else:
                    total += self.project(azc)[0]
                '''
        return max(0,total / self.get_total_cap())
    
    def project_2(self, building):
        '''
        variation on project function
        '''
        
        difference = building.occupancy - self.capacities[building]
        time_diff = self.model.schedule.steps - self.shock_reference
        delta = difference / self.assessment_frequency #assuming monthly assessment
        
        return self.capacities[building] + delta*(time_diff + 50), delta
    
    
    
    def project(self, building):
        
        '''
        Calculates difference between current and previous occupancies
        to get a rate of change, delta, uses that to estimate, project,
        occupancy in 180 days time if the rate of change were to continue
        '''
        
        difference = building.occupancy - self.capacities[building]
        
        delta = difference / self.assessment_frequency #assuming monthly assessment
        
        self.delta = delta
        
        return self.capacities[building] + delta*self.projection_time, delta
    
    def evaluate_cost(self, need, building):
        
        '''
        returns hotel cost, per person per month
        or conversion cost of an empty building
        '''
        
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
        '''checks if current amount of arrivals is abnormal
        '''
        return self.model.ter_apel.occupancy / variance_ta > self.shock_threshold
    
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
                problematic = True
                break                         
            else:
                self.project(building)
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
        
        self.need = total_need
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
        candidates = [x for x in candidates if
                      self.budget > x.convert_cost]
        
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
                      'as_ext', building.pos, self, building.proximity)
        azc_viz = AZC_Viz(self.model, new_azc)
        self.model.schedule.add(azc_viz)
        self.model.grid.place_agent(azc_viz, azc_viz.pos)
        self.model.schedule.add(new_azc)
        self.model.grid.place_agent(new_azc, building.pos)
        self.city.buildings.add(new_azc)
        self.azcs.add(new_azc)
        self.capacities[new_azc] = new_azc.occupancy
        self.city.buildings.remove(building)
        self.buildings_under_construction.remove(building)
        self.model.schedule.remove(building)
        self.model.grid.remove_agent(building)


# I set this up so we'd have a framework to convert empty buildings into activity centers 
# but currently it is not being used.      
    def convertToActivityCenter(self, building):
        #remove
        new_activity_center = ActivityCenter(building.unique_id,building.model,
                      'as', building.pos, self)
        activity_center_viz = ActivityCenter_Viz(self.model, new_activity_center)
        self.model.schedule.add(activity_center_viz)
        self.model.grid.place_agent(activity_center_viz, activity_center_viz.pos)
        self.model.schedule.add(new_activity_center)
        self.model.grid.place_agent(new_activity_center, building.pos)
        self.city.buildings.add(new_activity_center)
        self.activity_centers.add(new_activity_center)
        self.capacities[new_activity_center] = new_activity_center.participants
        self.city.buildings.remove(building)
        self.buildings_under_construction.remove(building)
        self.model.schedule.remove(building)
        self.model.grid.remove_agent(building)

        
        
    def construct(self, building):
        
        building.under_construction = True
        self.buildings_under_construction.add(building)
        self.budget -= building.convert_cost
    
    def collect(self):
        
        self.budget += self.collection_fee*self.get_total_occupancy()
        
        
    def get_state(self):
        '''
        Checks current state and sets policy accordingly
        '''
        
        #gives the model time to build of a distribution of normal flow
        if self.model.schedule.steps < self.model.shock_period / 2:
            
            if self.model.schedule.steps % self.assessment_frequency == 0:
                self.collect()
            
            # start calculting variances
            self.variance_ta, self.squared_ta, self.sum_ta = self.online_variance_ta(self.model.ter_apel)
        
        #starts checking for anamolies
        else:
            
            #only with a certain frequency so as not to slow it down
            if self.model.schedule.steps % self.assessment_frequency == 0:
                
                #also collects from residents
                self.collect()
                
                #check variance of current point
                variance_ta, squared_ta, sum_ta = self.online_variance_ta(self.model.ter_apel)
                if self.shock_check(variance_ta):
                    self.shock = True
                    self.shock_reference = self.model.schedule.steps
                       
                #if no anomoly add to normal flow distribution    
                else:
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
                        if self.ta:
                            pass
                        else:
                            self.policy = self.hotel_house
                         
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
                
        
    def step(self):
        
        
        '''
        COA is essentially checking for anomalies in the 'Ter Apel'
        If detected, inspects the gravity of the anomoly and acts
        accordingly
        '''
        
        #####Current State########
        #Check State and Set Policy
        self.get_state()
        
        ########Actions###########
        if self.model.schedule.steps % self.assessment_frequency == 0:
            #decay
            self.values.decay_val()
            
            #prioritize
            priority = self.values.prioritize()
            
            #find action that corresponds to priority
            current = None
            possible_actions = set(filter(lambda x: x.precondition(), self.actions))
            for value in priority:
                for action in possible_actions:
                    if value == action.v_index:
                        current = action
                        break
                if current != None:
                    break
            
            
            #update v_sat
            if current != None:
                print(current.name)
                current.do()

    def intake(self,newcomer):     
        '''Adds a newcomer to Ter Apel
        '''
        
        #take first one, in future, evaluate buildings on some criteria
        house_loc = self.model.ter_apel.pos         #where is it
        

        #update occupancy
        self.model.ter_apel.occupancy += 1
        
        #add noise so agents don't overlap
        x = house_loc[0] #+ np.random.randint(-20,20)
        y = house_loc[1] - 10 + int(20*((1+self.model.ter_apel.occupancy) / self.model.ter_apel.capacity))
        self.model.grid.move_agent(newcomer, (x,y)) #place
        self.model.ter_apel.occupants.add(newcomer) #add agent to building roster
        newcomer.loc = self.model.ter_apel #update agent location
        
            
        
class NGO(Organization):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
        '''
        Basic NGO class
        
        '''

        
        
class IND(Organization):
    
    def __init__(self, unique_id, model, city):
        super().__init__(unique_id, model)
        
        self.processing_rate = None
        self.max_time = 270
        self.min_time = 8
        self.coa = None
        self.city = city
        
    def set_time(self, newcomer):
        if newcomer.ls == 'as':
            capacity = self.coa.get_occupancy_pct()
            time = 90*capacity + 8
            newcomer.decision_time = int(time)
        elif newcomer.ls == 'as_ext':
            newcomer.decision_time = 90
    
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
        self.health = 0
        self.activities_available = set([])
        
        def step(self):
            self.health = self.health - 1

class AZC(Building):
    def __init__(self, unique_id, model, occupant_type, pos, coa, proximity):
        super().__init__(unique_id, model)
        
        self.capacity = 400
        self.occupants = set([])
        self.occupant_type = occupant_type
        self.pos = pos
        self.available = False
        self.occupancy = 0
        self.proximity = proximity
        self.operational_cost = None
        self.activity_center = None
        self.health = 0 
        self.ta = False
        self.coa = coa
    
    def get_operational_cost(self):
        
        #should combine capacity, activities and proximity
        #is an evaluation, not a specific monetary amount
        occupancy = self.occupancy / self.capacity
        activity = 0
        if self.activity_center != None:
            if self.activity_center.activities_available:
                activity += len(self.activity_center.activities_available)
                    
        activity = activity / 6 #6 possible activities. should be un-hardcoded as activitys change.
        health = (100 - self.health) / 100
        
        self.operational_cost = health + occupancy + activity + self.proximity


    def step(self):
        
        super().step()
        pass

# I set this up so we'd have a framework to have buildings that were
# solely activity centers but currently it is not being used.              
class ActivityCenter(Building):
    def __init__(self, unique_id, model, occupant_type, pos, azc):
        super().__init__(unique_id, model)
        
        self.capacity = 400
        self.participants = set([])
        self.participant_type = occupant_type
        self.pos = pos
        self.available = False
        self.occupancy = 0
        
        #switched from self.coa to self.azc, bc you can get the coa from the azc
        # Also we're trying to calculte cost per Azc not cost p COA
        self.azc = azc
        self.azc.activity_center = self
        self.activities_available = set([])
        
        self.ta = False
        
    def identify_need(self):
        
        '''
        Surveys residents of an AZC
        identifies the chief unmet need
        '''
        
        totals = np.array([0,0,0,0])
        
        for newcomer in self.azc.occupants:
            totals += newcomer.values.v_tau - newcomer.values.val_t
        
        return np.where(totals == max(totals))[0][0]
        
        



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
    
    def calc_cost(self, need, average_duration):
        
        hotel_cost = need*average_duration*self.cost_pp/30
        self.calculated_value = need / hotel_cost
        
        
        
        
    
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
        self.pos = pos
        
        #cost now depends on proximity and capacity
        self.convert_cost = self.capacity * 1000 * self.proximity
        self.available = True
        self.calculated_value = None
        self.under_construction = False
        self.construction_time = 180
        self.city = None
        
        
    def calc_cost(self, need, average_duration):
        
        self.calculated_value = need / self.convert_cost
    def step(self):
        super().step()
        if self.under_construction == True:
            self.construction_time -= 1
        if self.construction_time == 0:
            self.under_construction = False
            self.city.coa.convert(self)
            
        
