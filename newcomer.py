import mesa 
from mesa import Agent, Model
from scipy.stats import bernoulli
import numpy as np
from Values import Values
from organizations import AZC
from scipy.stats import truncnorm
from socialnetwork import SocialNetwork

class Newcomer(Agent):
    
    
    
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
        
        self.coa = coa
        self.pos = self.coa.pos
        
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
        self.values = Values(10, 40, 30, 60, 70, self)
        self.testing_activities = False
        self.budget = 0
        self.acculturation = np.random.uniform(0,.2)
        self.max_acc = 1.
        
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

    def COA_Interaction(self):
        
        
        #decision procedure for interacting with COA
        
        #EDP to AZ
        
        if self.ls == 'edp':
            self.current_procedure_time -= 1
            
            if self.current_procedure_time == 0:

                self.ls = 'as'
                self.coa.house(self)
                self.coa.city.ind.set_time(self)
                #self.current_procedure_time = self.coa.city.ind.set_time(self)
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
                        self.coa.city.public_opinion -= 1000
                else:
                    self.ls = 'as_ext'
                self.coa.house(self)
                self.current_procedure_time = self.model.procedure_durations[self.ls]
        elif self.ls == 'as_ext':
            self.current_procedure_time -= 1
            if self.current_procedure_time == 0:
                self.coa.city.ind.interview(self)
                
                #if positive decision
                if self.coa.city.ind.decide(False, self, self.model.dq):
                    self.ls = 'tr'
                    self.model.country_success[self.model.country_list.index(self.coo)] += 1
                    self.current_procedure_time = self.loc.procedure_duration
                    if self.second == 1:
                        self.model.confusionMatrix['TP'] += 1
                    else:
                        self.model.confusionMatrix['FP'] += 1
                        self.coa.city.public_opinion -= (self.coa.city.po_min - self.coa.city.public_opinion) / 2
                
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
                 

        
    def step(self):
        
        day = self.model.schedule.steps % 7
        
        #value decay
        self.values.decay_val()
        
        possible_activities = self.get_activities(day = self.model.schedule.steps % 7)
        
        #do activity
        priority = self.values.prioritize()
        
        #find action that corresponds to priority
        self.current = None
        for value in priority:
            for action in possible_activities:
                if value == action[0].v_index:
                    self.current = action
                    break
            if self.current != None:
                    break
        
        #update v_sat

        if self.current != None:
            self.current[0].do(self)
            self.model.action_agents.append(self)
            self.model.actions.append(self.current[0])

        
        #update procedings 
        self.COA_Interaction()
        
        self.health -= self.health_decay
        
        if self.model.include_social_networks:
            self.sn.decayRelationships()
            self.sn.maintainNetwork()
