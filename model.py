import mesa

# model.py
from mesa.space import MultiGrid
from mesa import Agent, Model
from mesa.time import RandomActivation


from random import randrange
from random import uniform

class HumanitarianLogistics(Model):
    """A model with some number of agents."""
    def __init__(self, N_a,nc_rate, width, height):
        self.num_azc = N_a #number of AZC in sim
        self.nc_rate = nc_rate #rate of inflow of newcomers
        
        self.width = width
        self.height = height
        
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True
        self.num_nc = 0
        
        self.dq_min = .5
        
        # Create AZCs
        for i in range(self.num_azc):
            
            if i == 0:
                occupant_type = 'edp'
            elif i < self.num_azc - 1:
                occupant_type = 'as'
            else:
                occupant_type = 'tr'
            
            a = AZC(i, self, occupant_type)
            
            self.schedule.add(a)
            # Add the agent to a random grid cell
            
            x = int((self.width / self.num_azc) * (i+.5))  
            
            y = int(self.height * .5)
            
            self.grid.place_agent(a, (x, y))
                              
            
          
           

    def step(self):
        self.schedule.step()
        
        
        #adds newcomers to simuluation at a given rate
        if uniform(0,1) < self.nc_rate:
            
            self.num_nc += 1
            
            
            ter_apel = self.schedule.agents
            
            
            x = int((self.width / self.num_azc)
                    * .5) + int(uniform(0,30))
            y = int(self.height * .5) + int(uniform(0,30))
            
            pos = (x,y)
            
            r = Newcomer(self.num_nc, self, pos, self.dq_min)
            self.schedule.add(r)
            
            
            self.grid.place_agent(r, pos) 
            
        
class Newcomer(Agent):
    
    def __init__(self, unique_id, model, pos, dq_min):
        
        '''
        
        Initializes Newcomer Class (NC)
        DQ - documentation quality
        pos - position in x,y space
        dq_min - refers to the IND standard
        decision time - time until IND must make a decision. 
       
        
        '''
        super().__init__(unique_id, model)
        self.pos = pos
        
        self.ls = 'edp'
        
        self.decision_time = 28
        
        
        self.dq = uniform(0,1)
            
    def step(self):
        self.decision_time -= 1
        
        if self.decision_time == 0:
            
            if self.dq < self.model.dq_min:
                self.model.grid.remove_agent(self)
            else:
                self.ls = 'tr'
                
class Building(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
         
        self.capacity = 0
        self.occupants = set([])
        
        self.occupancy = len(self.occupants)
                          
                
                

        

class AZC(Building):
    def __init__(self, unique_id, model,occupant_type):
        super().__init__(unique_id, model)
        
        self.capacity = 0
        self.occupants = set([])
        self.occupant_type = occupant_type


    def step(self):
        pass