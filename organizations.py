from mesa import Agent, Model
from random import randrange
from random import uniform
from operator import attrgetter
import numpy as np
from viz import AZC_Viz
from mesa.datacollection import DataCollector
from Values import Values
from fractions import Fraction
import activity
import newcomer





class City(Agent):
    '''
    A city contains buildings and institutions
    '''
    
    def __init__(self, unique_id, model, occupant_type,modality):
        super().__init__(unique_id, model)
        self.ngo = None
        self.modality = modality
        if self.modality == 'POL':
            y = int(self.model.height - 5*self.model.height/8)
            procedure_time = 4
            po = .05
        elif self.modality == 'COL':
            y = int(self.model.height - 7*self.model.height/8)
            procedure_time = 2
            po = .05
        elif self.modality == 'AZC':
            y = int(self.model.height - 3*self.model.height/8)
            procedure_time = 180
            if np.random.uniform(0,1) < .2:
                po = .05
                
            else:
                po = .05
                
        self.pos = (unique_id*(self.model.space_per_azc),y)
        self.coa = COA(self.unique_id, model, self)
        self.model.schedule.add(self.coa)
        self.ind = IND(self.unique_id, model, self)
        self.model.schedule.add(self.ind)
        self.hotel = Hotel(self.unique_id, self.model, 1000,self ) 
        self.model.schedule.add(self.coa)
        self.azc = AZC(unique_id, model, occupant_type, modality, self)
        self.azc.procedure_duration = procedure_time
        self.azcs = set([self.azc])
        self.model.schedule.add(self.azc)
        
        
        self.auxiliary_housing = 0
        self.model.city_count += 1
        self.cost_of_bus_within_city = 5
        self.cost_of_bus_to_another_city = 20
        self.public_opinion = po           #cities start out neutral regarding PO of NC.
        self.ngo = NGO(self.unique_id, self.model, self)

        self.po_max = 1.
        self.po_min = 0
        action_testing = True
        if action_testing:
            #add actions to action set
            for action in range(len(self.coa.action_names)):
                
                #make action w a name, actor, and index of value to be satisfied
        
                
                if action == 1:
                    current_action = activity.Invest(self.coa.action_names[action], self.coa,action)
                    self.coa.actions.add(current_action)
                    current_action = activity.BuildCentral(self.coa.action_names[action], self.coa,action)
                    self.coa.actions.add(current_action)
                elif action == 2:
                    current_action = activity.Segregate(self.coa.action_names[action], self.coa,action)
                    self.coa.actions.add(current_action)
                
                elif action == 0:
                    
                    current_action = activity.improveFacilities(self.coa.action_names[action], self.coa,action)
                    self.coa.actions.add(current_action)
                
                elif action == 3:
                    current_action = activity.adjustStaff_COA(self.coa.action_names[action], self.coa,action)
                    self.coa.actions.add(current_action)
                
        
    def __eq__(self, other): 
        return self.unique_id == other.unique_id    

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
        
        
        self.model.schedule.add(self)
        self.city = city
        self.pos = self.city.pos
        
        
        self.self_enhancement = self.model.coa_values['SE']
        self.self_transcendence = self.model.coa_values['ST']
        self.conservatism = self.model.coa_values['C']
        self.openness_to_change = self.model.coa_values['OTC']
        self.values = Values(10, self.self_enhancement, self.self_transcendence,
                             self.conservatism, self.openness_to_change,self)
        
        
        self.newcomer_payday = 0
        self.assessment_frequency = int(365/(self.openness_to_change*52/100))
        self.action_frequency = self.assessment_frequency
        self.checkin_frequency =  int(365/(self.self_transcendence*52/100))
        self.state = 'Normal'
        self.staff_to_resident_ratio = .15
        
        self.staff = 15
        self.checkin = activity.Checkin('Checkin', self, 3)
        self.current_policy = self.find_house
        
        #####ACTIONS######
        self.actions = set([])
        self.action_names = ['improveFacilities', 'Invest', 'Segregate', 'adjustStaff']
        
        self.budget = 0
        
                    

    
    def build(self, size):
        '''
        Build adds a building of a given size to the simulation
        '''
        
        
        new = AZC(self.model.city_count, self.model, {'as', 'as_ext', 'tr'}, 'AZC', self.city)
        new.capacity = size
        new.pos = new.city.hotel.pos
        new.city.azcs.add(new)
        new.procedure_duration = 35
        self.model.schedule.add(new)
        self.model.grid.place_agent(new, new.pos)
    
    def min_house(self, newcomer):
        '''finds min occupancy building regardless of legal status
        '''
        candidates = [building for building in self.model.schedule.agents if
                    type(building) is AZC and building.modality != 'COL' and
                    building.occupancy < building.max_capacity*building.capacity]
        
        if not candidates:
            #hotel house
            min_type = self.city.hotel
            #min_type.procedure_duration = self.model.procedures_duration[newcomer.ls]
        else:
            
            min_type = min(candidates, key = attrgetter('occupancy'))
        
        return min_type
        
    
        
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
        
        return sum([azc.capacity for azc in self.city.azcs])
    
    def get_total_occupancy(self):
        '''total occupied space'''
        
        return sum([azc.occupancy for azc in self.city.azcs])
    
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
        destination = self.current_policy(newcomer)
        destination.occupants.add(newcomer)

        destination.occupancy += 1 #update occupancy 
        
        
        newcomer.loc = destination
        newcomer.coa = destination.city.coa
        
        
        
    def move(self, newcomer, destination):
        
        if newcomer in newcomer.loc.occupants:
            
            newcomer.loc.occupants.remove(newcomer)
        
        newcomer.loc.occupancy -= 1
        destination.occupants.add(newcomer)

        destination.occupancy += 1 #update occupancy 
        
        
        newcomer.loc = destination
        newcomer.coa = destination.coa
        

    def step(self):
                
        day = self.model.schedule.steps
        
        #Obligations - Checkins
        if day % self.checkin_frequency == 0:
            self.checkin.do()
        
        #decay
        self.values.decay_val()
        
        #prioritize
        priority = self.values.prioritize()
        
        if day % self.action_frequency == 0:
            #act
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
                #print(current.name)
                current.do()
        

        
class NGO(Organization):
    
    def __init__(self, unique_id, model,city):
        super().__init__(unique_id, model)
        
        super().__init__(unique_id, model)
        self.model.schedule.add(self)
        self.city = city
        self.pos = self.city.pos
        self.values = Values(10,55,50,40,45, self)
        self.funds = 0
        self.cost_per_activity = .05
        self.activities = set([])
        self.activity_records = {}
        self.activity_attendance = {}
        self.action_frequency = int(365/(self.values.v_tau[3]*52/100))
        self.campaign = 0
        self.overhead = .2
        

        #actions
        self.action_names = ['marketingCampaign', 'customActivity', 'Fundraise','Prioritize']
        self.actions = set([])
        
        for i in range(0, len(self.action_names)):
            
            if i == 9:
                self.actions.add(activity.Prioritize(self.action_names[i], self, i))
            elif i == 9:
                self.actions.add(activity.customActivity(self.action_names[i], self, i))
            elif i == 9:
                self.actions.add(activity.marketingCampaign(self.action_names[i], self, i))
            elif i == 2:
                self.actions.add(activity.Fundraise(self.action_names[i], self, i))

    def identify_need(self):
        
        '''
        Surveys residents of an AZC
        identifies the chief unmet need
        '''
        
        totals = np.array([0,0,0,0])
        
        for nc in self.city.azc.occupants:
            totals += nc.values.v_tau - nc.values.val_t
        
        return np.where(totals == max(totals))[0][0]
        
    def get_avg_attendance(self):
        
        '''
        gets avg attendance p day of each activity. 
        '''
        if self.activity_attendance:
            for act in self.activities:
                for day in act.frequency:
                    
                    self.activity_attendance[act.name][day] = act.attendance[day] / self.activity_records[act.name][day]
        
    
    def step(self):
        
        day = self.model.schedule.steps % 7
        
        self.values.decay_val()
        
        #update attendance records
        if self.activities:
            for act in self.activities:
                if day in act.frequency:
                    if act.name in self.activity_records.keys():
                        self.activity_records[act.name][day] += 1

        
        
            

        
        #the action of marketing gives PO a big boost, but than wanes over time
        if self.campaign > 0:
            self.campaign -= .1
            self.city.public_opinion -= self.campaign
        
        #prioritize
        priority = self.values.prioritize()
        
        if day % self.action_frequency == 0:
            #act
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
        
        

        
        
class IND(Organization):
    
    def __init__(self, unique_id, model, city):
        super().__init__(unique_id, model)
        
        self.processing_rate = None
        self.max_time = 270
        self.min_time = 8
        self.city = city
        self.pos = self.city.pos
        self.threshold_first = 1
        self.margin = .25
        self.threshold_second = 1.5
        self.number_asylum_interviews = 2
        self.case_error_rate = .05
        self.conservatism = 52
        self.self_enhancement = 45
        self.self_transcendence = 49
        self.openness_to_change = 60
        self.values = Values(10, self.self_enhancement, self.self_transcendence,
                             self.conservatism, self.openness_to_change,self)
        self.staff = 50
        self.action_frequency = int(365/(self.openness_to_change*52/100))

        
        #####ACTIONS######
        self.actions = set([])
        self.action_names = ['issueStatement', 'lowerThreshold', 'raiseThreshold', 'adjustStaff']
        
        for action in range(len(self.action_names)):

            if action == 1:
                current_action = activity.lowerThreshold(self.action_names[action], self,action)
                self.actions.add(current_action)
            elif action == 2:
                current_action = activity.raiseThreshold(self.action_names[action], self,action)
                self.actions.add(current_action)
            elif action == 3:
                current_action = activity.adjustStaff(self.action_names[action], self,action)
                self.actions.add(current_action)
            elif action == 0:
                current_action = activity.issueStatement(self.action_names[action], self,action)
                self.actions.add(current_action)
        
        
    def set_time(self, newcomer):
        capacity = self.city.coa.get_occupancy_pct()
        staff_adjustment = 1 - (self.staff)/100
        if newcomer.ls == 'as':
            time = staff_adjustment*27*capacity + 8
            newcomer.current_procedure_time = int(time)
        elif newcomer.ls == 'as_ext':
            newcomer.current_procedure_time = staff_adjustment*int(180*capacity + 90)
        elif newcomer.ls == 'tr':
            newcomer.current_procedure_time = 100
    
    def decide(self, first, newcomer, dq):
        
        if dq:
            if first:
                return newcomer.doc_quality > self.threshold_first - self.margin
            else:
                return newcomer.doc_quality > self.threshold_second - self.margin
        else:
            if first:
                return newcomer.first == 1
            else:
                return newcomer.second == 1
    
    def interview(self, newcomer):
        '''
        increase newcomer DQ by some amount
        '''
        newcomer.doc_quality += np.random.normal(newcomer.second, 1-newcomer.specs[0]) / self.number_asylum_interviews
    
    def step(self):
        
        day = self.model.schedule.steps % 7
        
        self.values.decay_val()
        
        #prioritize
        priority = self.values.prioritize()
        
        if day % self.action_frequency == 0:
            #act
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
                #print(current.name)
                current.do()
    
                           
                    
                    
                
class Building(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
         
        self.capacity = 0
        self.occupants = set([])
        
        self.occupancy = 0
        self.health = 100
        self.max_health = 100
    
    def step(self):
        self.health = self.health - (1*self.occupancy/self.capacity)


class AZC(Building):
    def __init__(self, unique_id, model, occupant_type, modality, city):
        super().__init__(unique_id, model)
        
        self.capacity = 400
        self.occupants = set([])
        self.occupant_type = occupant_type
        self.procedure_duration = None
        self.city = city
        self.coa = self.city.coa
        self.operating_capacity = None
        self.health = 60
        self.max_health = 100
        self.operational_health = 50
        self.operational_cost = self.occupancy/self.capacity + self.health/self.max_health
        self.occupancy = 0
        self.health = 100
        self.max_health = 100
        self.modality = modality
        self.state = 'Normal'
        self.shock_state = None
        self.max_capacity = .75
        self.need = 0
        self.pos = self.city.pos
        #location setting, currently buggy          
        self.model.schedule.add(self)
        self.model.grid.place_agent(self,self.pos)
        self.activity_center = ActivityCenter(self.unique_id, self.model,self)
        
        
        #ter apel shock check
        self.sum_ta = 0 
        self.squared_ta =  0 
        self.counter_ta = 1
        self.variance_ta = None
        self.var_copy_ta = None
        self.shock_threshold = 6
        
        #non-TA shock check
        self.occupancies = []
        self.period = 3
        self.shock_position = 0
        self.problematic_threshold = .60
        
        
        
            
            
        
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
        return self.occupancy / variance_ta > self.shock_threshold
    
    def estimate(self, period):
        '''
        given a length of time period, looks at occupanices from one period ago
        to calculate occupanices one period in the future
        '''
        
        if len(self.occupancies) < period:
            return self.occupancy
        else:
            current = self.occupancies[-1]
            last = self.occupancies[- period]
            rate = (current - last) / period
            estimation = rate*period + current
            return estimation
    
    def estimate_time(self, period):
        
        current = self.occupancies[-1]
        last = self.occupancies[- period]
        rate =  (current - last) / period
        occupancy_exceeded = False
        counter = 1
        if rate > 0:
            while not occupancy_exceeded:
                estimation = rate*counter + current
                if estimation > self.capacity:
                    occupancy_exceeded = True
                    return counter
                else:
                    counter += 1
        else: 
            return 0
        
        
        
    
    def set_state(self, state):
        for azc in self.model.schedule.agents:
            if type(azc) is AZC:
                azc.state = state 
                self.city.coa.state = state
            
    def set_policy(self):
        for azc in self.model.schedule.agents:
            if type(azc) is AZC:
                if azc.shock_state == 'Problematic':
                    azc.city.coa.current_policy = azc.coa.min_house
                elif azc.shock_state == 'Manageable':
                    azc.city.coa.current_policy = azc.coa.find_house
                
    def get_state(self):
        #just gathe variance data for the first 100 steps
        if self.modality == 'COL':
            if self.model.schedule.steps < 100:
                self.variance_ta, self.squared_ta, self.sum_ta = self.online_variance_ta(self)             
            else:
                if self.model.schedule.steps % self.city.coa.assessment_frequency == 0:
                    
                    #check for anomalies in amount of incoming newcomer
                    self.shock_check_procedure()
            
                    
        ###If not COL Just report for estimation purposes.
        else:
            
            if self.model.schedule.steps % self.city.coa.assessment_frequency == 0:
                self.occupancies.append(self.occupancy)
            #problematic check
            if self.state == 'Shock':
                self.problematic_check()
            #Crisis check
            if self.shock_state == 'Problematic':
                self.crisis_check()
            
                
                
    def shock_check_procedure(self):
        #Check for Shock
        variance_ta, squared_ta, sum_ta = self.online_variance_ta(self)
        if self.shock_check(variance_ta):
            print('shock')
            self.set_state('Shock')
            self.shock_position += 1
        #if no anomoly add to normal flow distribution 
        else:
            self.variance_ta, self.squared_ta, self.sum_ta = variance_ta, squared_ta, sum_ta
            self.set_state('Normal')
            self.shock_position = 0
            self.set_policy()
            #print('shock-over')                    
    
    def problematic_check(self):
        estimation = self.estimate(max(3, self.shock_position))                       
                        
        if estimation > self.capacity*self.problematic_threshold:
            self.shock_state = 'Problematic'
            #change policy   
            self.set_policy()
        else: 
            self.shock_state = 'Manageable'
            #change policy
            self.set_policy()
                    
    def crisis_check(self):
        
        total_capacity = sum([azc.capacity for azc in self.model.schedule.agents
                          if type(azc) is AZC and azc.modality != 'COL'])
            
        total_estimated_occupancies = sum([azc.estimate(max(3, self.shock_position)) for
                                       azc in self.model.schedule.agents if
                                       type(azc) is AZC and azc.modality != 'COL'])
        need = total_estimated_occupancies - total_capacity
        
        if need > 0:
            self.state = 'Crisis'
            self.need = need
        else:
            self.problematic_check()
            
    def get_operational_cost(self):
        occupancy = self.occupancy / self.capacity
        health = self.health/ self.max_health
        
        self.operational_cost = health + occupancy
            
    
    def step(self):
        
        super().step()
        
        #update state
        self.get_state()
        
        

        
        
        
        
        
                    


         

class Hotel(Building):
    '''
    Hotels are commerical buildings
    they have a cost p room p person
    '''
    
    def __init__(self, unique_id, model, cost_pp, city):
        super().__init__(unique_id, model)
        
        self.capacity = 100000
        self.occupants = set([])
        self.cost_pp = cost_pp
        self.available = True
        self.city = city
        self.pos = (self.city.pos[0], self.city.pos[1] - 2*self.model.city_size - 5)
        self.calculated_value = None
        self.activity_center = None
        self.model.schedule.add(self)
        self.model.grid.place_agent(self, self.pos)
        self.ind = city.ind
        self.procedure_duration = None
        
    
 
        
        
        
    
class Empty(Building):
    '''
    Empty buildings have a refurbishing cost
    and can be converted into AZCs
    '''
    def __init__(self, unique_id, model, capacity, city):
        super().__init__(unique_id, model)
        
        self.capacity = capacity
        self.occupants = set([])
        self.city = city

    def step(self):
        super().step()
        
class ActivityCenter(Building):
    def __init__(self, unique_id, model, azc):
        super().__init__(unique_id, model)
        
        self.participants = set([])
        self.available = False
        self.occupancy = 0
        self.azc = azc
        self.activities_available = set([
                activity.Language_Class(self.unique_id, self.model, {1,2,3,4,5}, 0),
                activity.Work(self.unique_id, self.model, {1,2,3,4,5}, 0),
                activity.Doctor(self.unique_id, self.model, {1,2,3,4,5,6,7}, 2),
                activity.Socialize(self.unique_id, self.model, {1,2,6,7},2),
                activity.Study(self.unique_id, self.model, {1,2,3,4,5}, 0)])
        
        #NGO activities if available
        if self.azc.city.ngo != None:
            self.activities_available.add(activity.Football(self.unique_id, self.model, {1,3,5}, 3))
            self.activities_available.add(activity.Volunteer(self.unique_id, self.model, {2,3}, 1))

        self.counter = {}
        
        self.active_participants = set([])
        
    def step(self):
        pass        

            
        
