import mesa

# model.py
from mesa.space import MultiGrid
from mesa import Agent, Model
from mesa.time import RandomActivation


from random import randrange
from random import uniform
import numpy as np

class HumanitarianLogistics(Model):
    """A model with: number of azc
        rate of newcomer arrival
        dimensions width and height"""
    
    
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
        
        
        # create RVR
        RVR_ = RVR(0, self)
        self.schedule.add(RVR_)
        self.rvr = RVR_
        # create IND
        IND_ = IND(0, self)
        self.schedule.add(IND_)
        self.ind = IND_
        
        
        
        
        # Create AZCs
        for i in range(self.num_azc):
            
            if i == 0:
                occupant_type = 'edp'
            elif i < self.num_azc - 1:
                occupant_type = 'as'
            else:
                occupant_type = 'tr'
                
            x = int((self.width / self.num_azc) * (i+.5))  
            
            y = int(self.height * .5)
            
            a = AZC(i, self, occupant_type, (x,y))
            
            self.schedule.add(a)
            # Add the agent to a random grid cell
            
            
            
            self.grid.place_agent(a, (x, y))
            
            
       
    
    
    
    
    def house(self,newcomer):

        
        eligible_buildings = [x for x in self.schedule.agents 
                    if type(x) is AZC and
                    x.occupant_type == newcomer.ls]
        
        
        destination = eligible_buildings[0]
        
        house_loc = destination.pos
        
        print(house_loc)
        
        #add noise
        x = house_loc[0] + np.random.randint(1,10)
        y = house_loc[1] + np.random.randint(1,10)
        
        self.grid.place_agent(newcomer, (x,y))
        
        destination.occupants.add(newcomer)
        
        
                              
            
          
           

    def step(self):
        self.schedule.step()
        
        
        #adds newcomers to simuluation at a given rate
        if uniform(0,1) < self.nc_rate:
            
            self.num_nc += 1
            
            
            
            
            x = int((self.width / self.num_azc)
                    * .5) + int(uniform(0,30))
            y = int(self.height * .5) + int(uniform(0,30))
            
            pos = (x,y)
            
            r = Newcomer(self.num_nc, self, pos, self.dq_min)
            self.schedule.add(r)
            
            self.house(r)
            
            
class Organization(Agent):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
        """
        Generic Starter class for Organizations,
        to be adapted to Gov and NGO and the like
        """
        self.unique_id = unique_id
        self.model = model

        
class NGO(Organization):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
        '''
        Basic NGO class
        
        '''
class RVR(NGO):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
        self.actions = []
        self.dq_rate = .2
    
    def counsel(self, agt):
        """
        Help agent gather documentation
        """
        agt.dq += self.dq_rate
        print('Meeting w RVR')
        
        
class IND(Organization):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
        self.processing_rate = None
        self.likelihood_misinterpretation = uniform(0,1)
        
    def interview(self,agt):
        """
        Judge case of refugee
        via interpreter, some
        possibility of misinterpretation
        """
        agt.case -= self.likelihood_misinterpretation
        print('meeting w IND')
        
        
        
        
class Newcomer(Agent):
    
    def __init__(self, unique_id, model, pos, dq_min):
        
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
        
        self.case = 1 #quality of case made to IND
        
        self.ls = 'edp' #externally displaced person
        
        self.decision_time = 28 #28 days is the length of the general asylum procedure
        
        self.intake_time = 4
        
        self.dq = uniform(0,1) #initially random documentation quality, to be changed later
        
        self.asylum_procedure = [self.model.rvr.counsel(self),
                                 self.model.ind.interview(self),
                                 self.model.rvr.counsel(self),
                                 self.model.ind.interview(self)]
        
        self.current_step = 0
        
        
        
        
            
    def step(self):
        
        #EDP to AZ
        
        if self.ls == 'edp':
            self.intake_time -= 1
            
            if self.intake_time == 0:
                
                self.ls = 'as'
                self.model.house(self)
        
        
        
        #AZ to TR
        
        elif self.ls == 'as':
        
            self.decision_time -= 1
            
                        
            try:
                self.asylum_procedure[self.current_step]
                self.current_step += 1
            except IndexError:
                print(self.ls)
                print(self.current_step)


            if self.current_step == len(self.asylum_procedure):

                if self.dq < self.model.dq_min:
                    self.model.grid.remove_agent(self)
                    self.model.schedule.remove(self)
                else:
                    self.ls = 'tr'
                    self.model.house(self)
        elif self.ls == 'tr':
            print('made it!')
                    
 
                    
                    
                    
                
class Building(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
         
        self.capacity = 0
        self.occupants = set([])
        
        self.occupancy = len(self.occupants)
        

                          
                
                

        

class AZC(Building):
    def __init__(self, unique_id, model,occupant_type, pos):
        super().__init__(unique_id, model)
        
        self.capacity = 0
        self.occupants = set([])
        self.occupant_type = occupant_type
        self.pos = pos


    def step(self):
        pass