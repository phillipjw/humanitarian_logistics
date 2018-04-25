import mesa
import numpy as np
from mesa import Agent, Model
from organizations import AZC

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
        
        return sum([azc.occupancy for azc in
                    self.agent.azcs]) > 0
    
    def do(self):
        
        #this is placeholder and should go outisde the function
        if not self.precondition():
            print('Cannot Consolidate')
            pass
        
        #get all non-empty AZCs
        azcs = [azc for azc in self.agent.model.schedule.agents if
                type(azc) is AZC and not azc.ta and
                azc.occupancy > 0]
        print('a')
        print('num opties', len(azcs))
        
        #Order non-empty Azcs by occupancy
        azcs.sort(key = lambda x: x.occupancy)
        
        
        #move occupants to central location
        for current in self.agent.azcs:
            
            #take lowest capacity AZC and move its occupants to highest
            #capacity AZC that can fit them
            
            amount = current.occupancy
            
            if amount > 0:
                print('init')
            
                for other_azc in reversed(azcs):
                    
                    if other_azc.capacity - other_azc.occupancy > amount:
                        #move occupants
                        print('enough room!')
                        for occupant in current:
                            current.coa.move(occupant, other_azc)
                        
                        break
        
        #update values
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