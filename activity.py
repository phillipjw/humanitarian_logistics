import mesa
import numpy as np
from mesa import Agent, Model
import organizations

class Action():
    
    def __init__(self,name, agent, v_index):
        
        '''
        generic action class, similar to activity but not of agent type
        '''
        self.name = name
        self.agent = agent            #tie it to a given agent
        self.v_index = v_index          #index of value to be satisfied
        self.counter = 0              #for histogramming purposes
        
    def do(self):
        
        self.agent.values.val_t[self.v_index] += self.agent.values.val_sat[self.v_index]
        self.counter += 1
        
class Consolidate(Action):
    
    def __init__(self, name, agent, v_index):
        
        '''
        Consolidate is a self-enhancement action
        It involves moving newcomers from multiple dispersed AZCs
        into fewer, centralized AZCs
        It frees up available capital for COA
        '''
        
        super().__init__(name, agent, v_index)
        self.name = name
        self.agent = agent            #tie it to a given agent
        self.v_index = v_index          #index of value to be satisfied
        self.effect = self.do
        self.counter = 0              #for histogramming purposes
        
    def satisfaction(self):
        
        self.agent.values.val_t[self.v_index] += self.agent.values.val_sat[self.v_index]
        self.counter += 1
        
    def precondition(self):
        
        ''''
        check if action is feasible in the first place
        by ensuring that azcs's are non-empty
        '''
        
        return not self.agent.shock and sum([azc.occupancy for azc in
                                             self.agent.azcs]) > 0
    
    def do(self):
        
        #this is placeholder and should go outisde the function
        if not self.precondition():
            print('Cannot Consolidate')
            pass
        
        #get all non-empty AZCs
        azcs = [azc for azc in self.agent.model.schedule.agents if
                type(azc) is organizations.AZC and not azc.ta and
                azc.occupancy > 0]

        
        #Order non-empty Azcs by occupancy
        azcs.sort(key = lambda x: x.occupancy)
        
        
        #move occupants to central location
        for current in self.agent.azcs:
            
            #take lowest capacity AZC and move its occupants to highest
            #capacity AZC that can fit them
            
            amount = current.occupancy
            print('amount:', amount)
            print('test:', len(current.occupants))
           
            if current.occupants:
            
                for other_azc in reversed(azcs):
                    difference = other_azc.capacity - other_azc.occupancy

                    while difference > 0 and amount > 0:
                        try:
                            occupant = current.occupants.pop()
                            current.coa.move(occupant, other_azc)
                            amount -= 1
                            difference -= 1
                        except TypeError:
                            print('Typerror,',len(current.occupants))
                        
        #update values
        self.satisfaction()
        
class Invest(Action):
    
    def __init__(self, name, agent, v_index):
        
        '''
        Consolidate is a self-enhancement action
        It involves moving newcomers from multiple dispersed AZCs
        into fewer, centralized AZCs
        It frees up available capital for COA
        '''
        
        super().__init__(name, agent, v_index)
        self.name = name
        self.agent = agent            #tie it to a given agent
        self.v_index = v_index          #index of value to be satisfied
        self.effect = self.do
        self.counter = 0              #for histogramming purposes
        
    def satisfaction(self):
        
        self.agent.values.val_t[self.v_index] += self.agent.values.val_sat[self.v_index]
        self.counter += 1
        
    def precondition(self):
        
        #check if Balance enough to invest and not shock
        return not self.agent.shock
    
    def do(self):
        
    #During a non-shock period, COA satisfies ST by investing in the quality of life of its
    #residents by constructing an activity center (AC). The AC has a cost significantly less than an
    #entire building, as it may simply be a room in another building. The AC hosts activities, which
    #are period events satisfying a certain criteria of a newcomer. Currently, we just add an activities
    # to aczs that are less than half full and where the ls == as. However, there is functionality in the
    # code to convert empty buildings to ActivityCenter buildings.
        
        max_num_activity_centers = 2
        max_num_activities_per_center = 2 
        num_activity_centers_added = 0       
        for azc in self.agent.azcs:
       
         if (len(azc.occupants)/azc.capacity) < 0.5:
             if (num_activity_centers_added < max_num_activity_centers):
                 activities = set([])
                 for j in range(max_num_activities_per_center):
                     generated_activity = Football(num_activity_centers_added, self, 1)
                     activities.add(generated_activity)
                        
                 azc.activities_available = activities
                 num_activity_centers_added = num_activity_centers_added + 1
        '''
        unsure about this bit of code below:
        Is this satisfaction to the newcomer whose doing the action?
        
        
        for azc in self.agent.azcs:
             if len(azc.activities_available)>0:
                 for newcomer in azc.occupants:
                     if newcomer.ls == "as":
                         action_to_take.satisfaction(newcomer)
        '''
                
        self.satisfaction()

class Segregate(Action):
        
    def __init__(self, name, agent, v_index):
        
        '''
        Consolidate is a self-enhancement action
        It involves moving newcomers from multiple dispersed AZCs
        into fewer, centralized AZCs
        It frees up available capital for COA
        '''
        
        super().__init__(name, agent, v_index)
        self.name = name
        self.agent = agent            #tie it to a given agent
        self.v_index = v_index          #index of value to be satisfied
        self.effect = self.do
        self.counter = 0              #for histogramming purposes
        
    def satisfaction(self):
        
        self.agent.values.val_t[self.v_index] += self.agent.values.val_sat[self.v_index]
        self.counter += 1
        
    def precondition(self):
        
        #check if not shock and check if feasible
        return not self.agent.shock
        
    
    def segregate(self, action_to_take):
        cheapest_azc_to_maintain = None
        cost_to_maintain = 100
        for azc in self.agent.azcs:
            if (100-azc.health) < cost_to_maintain:
                cheapest_azc_to_maintain = azc
                cost_to_maintain = 100-azc.health
        if cheapest_azc_to_maintain != None:
            for newcomer in self.agent.newcomers:
                # defining an unlikely new comer as one with a first value = 0
                # and a legal status of edp
                if newcomer.first == 0:
                    if newcomer.ls == "edp":
                        self.move(newcomer, cheapest_azc_to_maintain)
                        action_to_take.satisfaction(newcomer)
        
        self.satisfaction()
        
class Integrate(Action):
        
    def __init__(self, name, agent, v_index):
        
        '''
        Consolidate is a self-enhancement action
        It involves moving newcomers from multiple dispersed AZCs
        into fewer, centralized AZCs
        It frees up available capital for COA
        '''
        
        super().__init__(name, agent, v_index)
        self.name = name
        self.agent = agent            #tie it to a given agent
        self.v_index = v_index          #index of value to be satisfied
        self.effect = self.do
        self.counter = 0              #for histogramming purposes
        
    def satisfaction(self):
        
        self.agent.values.val_t[self.v_index] += self.agent.values.val_sat[self.v_index]
        self.counter += 1
        
    def precondition(self):
        
        #check if not shock and check if feasible
        return not self.agent.shock
    
    def do(self):
        '''
        Not yet sold on this one
        for azc in self.agent.azcs:
             if len(azc.activities_available)>1:
                 for newcomer in azc.occupants:
                    action_to_take.satisfaction(newcomer)
        '''
                    
        self.satisfaction()  
        

        

class Activity(Agent):
    
    def __init__(self, unique_id, model, frequency=1, se=0, st=0, c=0, otc=0):
       
    
        '''
        An activity is an event which recurs with a particular weekly 
        frequency and satisfies a particular value for the newcomers.
        '''
        super().__init__(unique_id, model)   
        self.frequency = frequency
	
        # SE corresponds to an activity that provides betterment of one’s 
	     # own attributes through either enhancement
        # of already owned resources, corresponding to achievement, or the enhanced control of resource
        # acquisition, corresponding to power
        # ST satisfaction providing an activity where the betterment of
        # another agent’s attributes, as per its component values, benevolence and universalism
        # C, which is an activity providing tradition, conformity and security.
        # OTC is an activity providing stimulation and hedonism
        
        #putting the above together into one array
        self.v_sat = np.array([se,st,c,otc])
        
        
        self.effect = None
    
        

        
class Football(Activity):
    
    def __init__(self, unique_id, model, frequency):
        
        super().__init__(unique_id, model, frequency)
        
        self.effect = self.satisfaction
        self.frequency == frequency
        
        #satisfies OTC
        self.v_sat = np.array([10,10,10,70])  #staves off decay for se,st,c
        
        
        
    def satisfaction(self, participant):
        
        participant.values.val_t += self.v_sat