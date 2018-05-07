import mesa 
from mesa import Agent, Model
from scipy.stats import bernoulli
import numpy as np
from Values import Values
from organizations import AZC



class Newcomer(Agent):
    
    def __init__(self, unique_id, model,country_of_origin, pos):
        
        '''
        
        Initializes Newcomer Class (NC)
        DQ - documentation quality
        pos - position in x,y space
        dq_min - refers to the IND standard
        decision time - time until IND must make a decision. 
        current_step - refers to what position the agent is in the sequence of actions
       
        
        '''
        super().__init__(unique_id, model)
        
        self.pos = pos
        self.coa = None
        
        #ls is Legal Status
        self.ls = 'edp' #externally displaced person
                
        self.decision_time = 8 #28 days is the length of the general asylum procedure
        self.intake_time = 4 #time until transfer out of ter apel
              
        self.coo = country_of_origin
        self.specs = self.model.specs[self.coo] #specs contains bournoulli distribution params
        self.ext_time = 90 #duration of extended procedure
        self.tr_time = None
        
        #draw first decision outcome
        self.first = bernoulli.rvs(self.specs[0], size = 1)[0] 
        #second decision outcome not drawn unless necessary
        self.second = None   
                                  
        # new comer values
        self.values = Values(10, 70, 30, 70, 50)
             
        self.testing_activities = False
        self.budget = 0
        
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
                    type(azc) is AZC and not azc.ta and
                    azc.activity_center != None and
                    azc.activity_center.activities_available != None]
            
            
        
        #check if enough for intracity
        elif self.budget > self.coa.city.cost_of_bus_within_city:
            
            
            azcs = [azc for azc in self.coa.azcs if
                    not azc.ta and azc.activity_center != None and
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
                    
                        possible_activities.append(activity)
        
        return possible_activities

    def COA_Interaction(self):
        
        #decision procedure for interacting with COA
        
        #EDP to AZ
        
        if self.ls == 'edp':
            self.intake_time -= 1
            
            if self.intake_time == 0:

                self.ls = 'as'
                self.coa.policy(self)
                self.coa.IND.set_time(self)
        #AZ to TR
        elif self.ls == 'as':
        
            self.decision_time -= 1

            if self.decision_time == 0:
                if self.coa.IND.decide(True, self):
                    self.ls = 'tr'
                    self.coa.social_house(self)
                    country = self.model.country_list.index(self.coo)
                    self.model.country_success[country] += 1
                    self.model.Remove(self)
                else:

                    self.ls = 'as_ext'
                    self.coa.policy(self)
                    self.coa.IND.set_time(self)

                    #draws decision outcome from bernoulli distribution based on attributes
                    self.second = bernoulli.rvs(self.specs[1], size = 1)[0]
                    

                        
        # Extended Procedure to TR or Repatriation
        
        elif self.ls == 'as_ext':
            self.decision_time -= 1
            
            if self.decision_time == 0:
            
                if self.second == 0:
                    self.model.Remove(self)
                else:
                    self.ls = 'tr'
                    wait_time = int(self.coa.city.social_housing.occupancy / self.coa.city.social_housing.capacity)
                    self.tr_time = 7 + wait_time
                    self.coa.social_house(self)
                    country = self.model.country_list.index(self.coo)
                    self.model.country_success[country] += 1
       
        # Agent Temporary Resident            

        elif self.ls == 'tr':
             self.tr_time -= 1
             
             if self.tr_time == 0:
                 
                 #add function to calculte QOL outcome
                 
                 self.model.Remove(self) 
                 

        
    def step(self):
        
        day = self.model.schedule.steps % 7
        
        #Allowance payment
        if day == self.coa.newcomer_payday:
            self.budget += self.coa.newcomer_allowance
            
        #select actions
        possible_actions = self.get_activities(day)
        
        #prioritize values
        priority = self.values.prioritize()
        
        #find action that corresponds to priority
        current = None
        for value in priority:
            for action in possible_actions:
                if value == action.v_index:
                    current = action
                    break
            if current != None:
                break
        
        #update v_sat
        if current != None:
            current.do(self)
        

        #COA interaction
        self.COA_Interaction()
