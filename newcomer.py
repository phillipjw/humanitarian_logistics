import mesa 
from mesa import Agent, Model
from scipy.stats import bernoulli
import numpy as np
from Values import Values
import math
from organizations import City
from random import randrange

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
        self.budget = 0

        
        
    def step(self):
        
        day = self.model.schedule.steps % 7
        
        #Allowance payment
        if day == self.coa.newcomer_payday:
            self.budget += self.coa.newcomer_allowance
      
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
        
        else:
            #decay
            self.values.decay_val()
            
            # get the day of the week
            day = self.model.schedule.steps % 7
            
            my_possible_activities = []
            activity_travel_costs  = []
            
            if self.budget > self.coa.city.cost_of_bus_within_city:
                # other within city azcs
                for azc in self.coa.azcs:
                    for activity in azc.activities_available:
                        my_possible_activities.append(activity)
                        activity_travel_costs.append(self.coa.city.cost_of_bus_within_city)
            
            if self.budget > self.coa.city.cost_of_bus_to_another_city:
                # other city azcs
                cities = set ([city for city in self.model.schedule.agents if type(city) is City])
                cities = cities - set([self.coa.city])
                for city in cities:
                    for azc in city.coa.azcs:
                        for activity in azc.activities_available:
                             my_possible_activities.append(activity)
                             activity_travel_costs.append(self.coa.city.cost_of_bus_to_another_city)
        
            # add logic to identify the activity that provides the best value payoff that the agent can afford
            # for now just pick one at random
            if (len(my_possible_activities) > 0):
                
                #prioritize my most important values and then find an activity that satisfies them
                priority = self.values.prioritize()
                possible_effects = []
                for value in priority:
                    possible_effects = []
                    for index in range(0, len(my_possible_activities)):
                        activity = my_possible_activities[index]
                        possible_effects.append(activity.v_sat[value])
                    if max(possible_effects) > 0:
                        break;
                
                # get the max value in possible effects
                index_of_activity = possible_effects.index(max(possible_effects))
                activity_to_do = my_possible_activities[index_of_activity]
                activity_to_do.effect(self)
                self.budget = self.budget - activity_travel_costs[index_of_activity]
            
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