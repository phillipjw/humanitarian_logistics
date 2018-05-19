import mesa 
from mesa import Agent, Model
from scipy.stats import bernoulli
import numpy as np
from Values import Values
from organizations import AZC



class Newcomer(Agent):
    
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
        self.values = Values(10, 70, 30, 70, 50, self)
        self.testing_activities = False
        self.budget = 0
        
        #measure of quality o
        self.doc_quality = 0
        self.case_quality = 0
        
          
    

    def COA_Interaction(self):
        
        
        #decision procedure for interacting with COA
        
        #EDP to AZ
        
        if self.ls == 'edp':
            self.current_procedure_time -= 1
            
            if self.current_procedure_time == 0:

                self.ls = 'as'
                self.coa.house(self)
                self.coa.city.ind.set_time(self)
                self.current_procedure_time = self.loc.procedure_duration
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
                
            
                
        
                 

        
    def step(self):
        
        #value decay
        self.values.decay_val()
        
        
        
        #update procedings 
        self.COA_Interaction()
        

