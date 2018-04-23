import mesa 
from mesa import Agent, Model
from scipy.stats import bernoulli
import numpy as np
from Values import Values



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
        
        #draw first decision outcome
        self.first = bernoulli.rvs(self.specs[0], size = 1)[0] 
        #second decision outcome not drawn unless necessary
        self.second = None   
                                  
        # new comer values
        self.values = Values(10, 70, 30, 70, 50)
             
        self.testing_activities = False
        

        
        
    def step(self):
        
        if self.testing_activities:
            #decay
            self.values.decay_val()
            
            #check if test activity is occuring today
            day = self.model.schedule.steps % 7
            if self.model.test_activity.frequency == day:
                print('partaking!')
                print(self.values.val_t)
                self.model.test_activity.effect(self)
                print(self.values.val_t)
        
        
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
                    self.coa.social_house(self)
                    country = self.model.country_list.index(self.coo)
                    self.model.country_success[country] += 1
                    self.model.Remove(self)      #temporary just to speed things up
         
       
        # Agent Temporary Resident            
        elif self.ls == 'tr':
            pass