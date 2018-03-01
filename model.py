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
        
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True
        self.num_nc = 0
        
        # Create AZCs
        for i in range(self.num_azc):
            a = AZC(i, self)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            
            x = int(self.grid.width / self.num_azc) * (i)  
            
            y = int(self.grid.height / 2)
            self.grid.place_agent(a, (x, y))
                              
            
          
           

    def step(self):
        self.schedule.step()
        
        
        #adds newcomers to simuluation at a given rate
        if uniform(0,1) < self.nc_rate:
            
            self.num_nc += 1
            
            x = randrange(self.grid.width)
            y = randrange(self.grid.height)
            pos = (x,y)
            
            r = Newcomer(self.num_nc, self, pos)
            self.schedule.add(r)
            
            
            self.grid.place_agent(r, pos) 
            
        
class Newcomer(Agent):
    
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
        
        self.decision_time = 28
            
    def step(self):
        self.decision_time -= 1
        print(self.decision_time)
        if self.decision_time == 0:
            self.model.grid.remove_agent(self)
            print('out')
        

class AZC(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


    def step(self):
        pass