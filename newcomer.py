import mesa
import math
from mesa import Agent, Model
from scipy.stats import bernoulli
import numpy as np
from Values import Values
from organizations import AZC, Hotel
from scipy.stats import truncnorm
from socialnetwork import SocialNetwork

class Newcomer(Agent):
    
    
    UID=1
    PUBLIC_OPINION_DROP_BASED_ON_CRIME = 0.15
    def get_truncated_normal(mean=50, sd=10, low=0, upp=100):
        return truncnorm(
            (low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd).rvs()
    
    
    def __init__(self, unique_id, model,country_of_origin,coa):
        
        '''
        
        Initializes Newcomer Class (NC)
        DQ - documentation quality
        pos - position in x,y space
        dq_min - refers to the IND standard
        decision time - time until IND must make a decision. 
        current_step - refers to what position the agent is in the sequence of actions
       
        
        '''
        super().__init__(unique_id, model)
        self.unique_id = Newcomer.UID
        Newcomer.UID = Newcomer.UID + 1
        
        self.coa = coa
        self.pos = self.coa.pos
        self.active = True
        #ls is Legal Status
        self.ls = 'edp' #externally displaced person
        self.current_procedure_time = None
        
        self.decision_time = 8 #28 days is the length of the general asylum procedure
        self.intake_time = 4 #time until transfer out of ter apel
              
        self.coo = country_of_origin
        self.specs = self.model.specs[self.coo] #specs contains bournoulli distribution params
        self.ext_time = 90 #duration of extended procedure
        self.tr_time = None
        
        #draw first decision outcome
        self.first = bernoulli.rvs(self.specs[0], size = 1)[0] 
        #second decision outcome not drawn unless necessary
        if self.first == 0:
            self.second = bernoulli.rvs(self.specs[1], size = 1)[0] 
        else:
            self.second = 1
                                  
        # new comer values
        self.values = Values(10, 56, 30, 50, 55, self)
        self.testing_activities = False
        self.budget = 0
        self.allowance = 50
        self.cost_of_food = 30
        self.acculturation = .2
        self.max_acc = 1.0
        
        
        self.invested = False
        self.integrated = False
        #measure of quality o
        self.doc_quality = 0
        self.case_quality = 0
        
        # adding a health measure (what would it mean if health was 1 - just incapable of acting) 
        # that would mean that the health bonus given by exercises is insufficient to counteract health decay.
        self.HEALTH_MAX = 100.0
        self.HEALTH_MIN = 1.0
        self.HEALTH_SD = 20.0
        self.HEALTH_MEAN = 66.0
        
        self.health = Newcomer.get_truncated_normal(mean=self.HEALTH_MEAN, 
                                                    sd=self.HEALTH_SD, low=self.HEALTH_MIN, upp=self.HEALTH_MAX)
        self.health_decay = self.model.health_decay
        self.sn = SocialNetwork()
        self.model.nc_count += 1
        
        #demographics
        probability_male = .7
        probability_minor = .25
        self.political_polarity = np.random.uniform(0,1)
        if np.random.uniform(0,1) < probability_male:
            self.sex = 'Male'
        else:
            self.sex = 'Female'
        if np.random.uniform(0,1) < probability_minor:
            self.age = 15
        else:
            self.age = 35
            
        #Education
        self.education = .5
        self.max_education = 1
        
        self.has_family_here = self.check_for_family()

    def COA_Interaction(self):
        
        
        #decision procedure for interacting with COA
        
        #EDP to AZ
        
        if self.ls == 'edp':
            self.current_procedure_time -= 1
            
            if self.current_procedure_time == 0:

                self.ls = 'as'
                self.coa.house(self)
                self.coa.city.ind.set_time(self)
        #AZ to TR
        elif self.ls == 'as':
            
            self.current_procedure_time -= 1
            
            #increase DQ
            
            
            if self.current_procedure_time == 0:
                self.coa.city.ind.interview(self)
                self.coa.city.ind.interview(self)
                if self.coa.city.ind.decide(True, self, self.model.dq):
                    self.ls = 'tr'
                    self.model.country_success[self.model.country_list.index(self.coo)] += 1
                    if self.first == 1:
                        self.model.confusionMatrix['TP'] += 1
                    else:
                        self.model.confusionMatrix['FP'] += 1
                        self.coa.city.public_opinion -= (self.coa.city.public_opinion - self.coa.city.po_min) / 2
                        self.coa.city.public_opinion = max(0, self.coa.city.public_opinion)
                
                else:
                    self.ls = 'as_ext'
                self.coa.house(self)
                self.coa.city.ind.set_time(self)
        elif self.ls == 'as_ext':
            self.current_procedure_time -= 1
            if self.current_procedure_time == 0:
                self.coa.city.ind.interview(self)
                
                #if positive decision
                if self.coa.city.ind.decide(False, self, self.model.dq):
                    self.ls = 'tr'
                    self.model.country_success[self.model.country_list.index(self.coo)] += 1
                    self.coa.city.ind.set_time(self)
                    if self.second == 1:
                        self.model.confusionMatrix['TP'] += 1
                    else:
                        self.model.confusionMatrix['FP'] += 1
                        self.coa.city.public_opinion -= (self.coa.city.public_opinion - self.coa.city.po_min) / 2
                        self.coa.city.public_opinion = max(0, self.coa.city.public_opinion)
                #if negative decision
                else:
                    if self.second == 0:
                        self.model.confusionMatrix['TN'] += 1
                    else:
    
                        self.model.confusionMatrix['FN'] += 1
                    self.model.Remove(self)
        elif self.ls == 'tr':
            self.current_procedure_time -= 1
            if self.current_procedure_time == 0:
                self.model.Remove(self)
                
            
                
    def get_activities(self, day):
        
        '''
        Given budget of newcomer, searches through reachable AZCs
        and returns the activities doable there.
        '''
        
        #Add default activities such as work once written
        possible_activities = []
        azcs = []
        if type(self.loc) is Hotel:
            
            '''
            If nc lives in a hotel, must pay to travel to do activities
            '''
                
            if self.budget > self.coa.city.cost_of_bus_to_another_city:
            
            
                azcs = [azc for azc in self.model.schedule.agents if
                        type(azc) is AZC and azc.modality != 'COL' and
                        azc.activity_center != None and
                        azc.activity_center.activities_available != None]

                
        else:
            
            #check if enough for intercity
            if self.budget > self.coa.city.cost_of_bus_to_another_city:
                
                
                azcs = [azc for azc in self.model.schedule.agents if
                        type(azc) is AZC and azc.modality != 'COL' and
                        azc.activity_center != None and
                        azc.activity_center.activities_available != None]
            
            #check if enough for intracity
            elif self.budget > self.coa.city.cost_of_bus_within_city:
                
                azcs = [azc for azc in self.coa.city.azcs if
                        azc.modality != 'COL' and azc.activity_center != None and
                        azc.activity_center.activities_available != None]
                
            #local
            else:
                azcs = [self.loc]
        
        if len(azcs) > 0 and azcs[0].activity_center != None:
            
            #add activities in selected AZCs to possible activity list
            for azc in azcs:
                
                for activity in azc.activity_center.activities_available:
                    #if occuring today
                    if day in activity.frequency:
                        
                        if activity.precondition(self):
                            possible_activities.append((activity,azc))
        
        return possible_activities    
    
    def outcome(self):
        
        distress = self.values.health
        physical_health = self.health
        local_interaction = self.acculturation
        social_health = np.mean([relationship.weight for relationship in
                                 self.sn.network])
        return (distress, physical_health, local_interaction, social_health)
                 

        
    def step(self):
        
        day = self.model.schedule.steps % 7
        if self.active:
            # qol is Quality of life, depends on staff:occupants and building health
            self.current = day
            self.qol = self.coa.get_qol()
            #value decay
            
            self.values.decay_val()
            
            possible_activities = self.get_activities(day = self.model.schedule.steps % 7)
            
            #eat
            #deduct for food
            if day == 0:
                self.budget += self.allowance
                self.budget -= self.cost_of_food
            
            
            #do activity
            priority = self.values.prioritize()
            
            #find action that corresponds to priority
            self.current = None
            if possible_activities:
                for value in priority:
                    for action in possible_activities:
                        if value == action[0].v_index and np.random.uniform(0,1) < self.qol:
                            self.current = action
                            break
                    if self.current != None:
                            break
            
            
            
           
            #update v_sat
            if self.current != None:
                self.current[0].do(self)
    
                self.model.action_agents.append(self)
                self.model.actions.append(self.current)
                
    
            
            #update procedings 
            self.COA_Interaction()
            self.health -= self.health_decay*self.qol
            
            if self.model.include_social_networks:
                self.sn.decayRelationships()
                self.sn.maintainNetwork()
             
            #if self.check_for_crime():
                #self.coa.city.public_opinion -= Newcomer.PUBLIC_OPINION_DROP_BASED_ON_CRIME
                #self.coa.city.public_opinion = min(0, self.coa.city.public_opinion)
                # offending agent is quarintined but currently this causes errors: self.model.Remove(self)
            self.active = False
        else:
            if self.current != day:
                self.active = True
        
    def check_for_family(self):
        family_educuation_threshold = 0.66
        chance_with_education = 0.3
        chance_without_education = 0.1
        random_draw = np.random.uniform(low=0, high=1)
        if self.education > family_educuation_threshold:
            return chance_with_education < random_draw
        else:
            return chance_without_education < random_draw
    
    def is_desperate(self):
        stablizing_number_of_steps = 50
        poor_health_threshold = 0.2
        low_budget_threshold = 1
        # wait for model to stabilize
        if self.model.schedule.steps > stablizing_number_of_steps:
            nc_outcome = self.outcome()
            # remove any nans
            nc_outcome = [0 if math.isnan(x) else x for x in nc_outcome]
            # normalize everything to 0-1
            nc_outcome = [(x/100) if x > 1 else x for x in nc_outcome]
            # no family
            if self.has_family_here == False:
                # if in bad shape for all outcome measures
                if all(i < poor_health_threshold for i in nc_outcome):
                    # budget
                    if self.budget < low_budget_threshold:
                        return True
        
        return False
    
    def check_for_crime(self):
        chance_for_crime = 0.01
        if self.is_desperate():
            random_draw = np.random.uniform(low=0, high=1)
            if random_draw < chance_for_crime:
                return True
        
        return False