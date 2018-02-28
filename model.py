import mesa

# model.py
from mesa.space import MultiGrid
from mesa import Agent, Model
from mesa.time import RandomActivation


from random import randrange

class HumanitarianLogistics(Model):
    """A model with some number of agents."""
    def __init__(self, N_a,N_r, width, height):
        self.num_azc = N_a
        self.num_r = N_r
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True
        
        
        # Create AZCs
        for i in range(self.num_azc):
            a = AZC(i, self)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = randrange(self.grid.width)
            y = randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
            
        # Create Refugees
        for i in range(self.num_r):
            x = randrange(self.grid.width)
            y = randrange(self.grid.height)
            pos = (x,y)
            
            r = Newcomer(i, self, pos)
            self.schedule.add(r)
            
            
            self.grid.place_agent(r, pos)           
            
          
           

    def step(self):
        self.schedule.step()
        
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