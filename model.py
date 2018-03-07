import mesa

# model.py
from mesa.space import MultiGrid
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from scipy.stats import bernoulli


from random import randrange
from random import uniform
import numpy as np

def calc_extended_as(model):
    
    azcs = np.array([x.occupancy for x in
            model.schedule.agents if
            type(x) is AZC and
                    x.occupant_type == 'as_ext'])
    
    
    
    return np.mean(azcs)

def calc_as(model):
    
    azcs = np.array([x.occupancy for x in
            model.schedule.agents if
            type(x) is AZC and
                    x.occupant_type == 'as'])
    
    
    
    return np.mean(azcs)

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
        
        self.dq_min = .85
        
        self.dq_ext = .6
        
        self.specs = {'Syria' : [.97,.96],
                      'Eritrea' : [.96,.89],
                     'Iraq' : [.482,.611],
                     'Afghanistan' : [.518,.52]}
        
        self.country_list = ['Syria', 'Eritrea', 'Iraq', 'Afghanistan']
        
        
        # create RVR
        RVR_ = RVR(0, self)
        self.schedule.add(RVR_)
        self.rvr = RVR_
        # create IND
        IND_ = IND(0, self)
        self.schedule.add(IND_)
        self.ind = IND_
        
        #agent specs
        
        
        self.datacollector = DataCollector(
            model_reporters = {'Cap - Extended-AS' : calc_extended_as,
                              'Cap - AS' : calc_as})
        
        
        
        # Create AZCs
        for i in range(self.num_azc):
            
            if i == 0:
                occupant_type = 'edp'
            elif i < self.num_azc - 2:
                occupant_type = 'as'
            elif i == self.num_azc - 2:
                occupant_type = 'as_ext'
                print('test')
            else:
                occupant_type = 'tr'
                
            x = int((self.width / self.num_azc) * (i+.5))  
            
            y = int(self.height * .5)
            
            a = AZC(i, self, occupant_type, (x,y))
            
            self.schedule.add(a)
            # Add the agent to a random grid cell
            
            
            
            self.grid.place_agent(a, (x, y))
            
            
       
    
    
    
    
    def house(self,newcomer):

        #find building for newcomers legal status
        eligible_buildings = [x for x in self.schedule.agents 
                    if type(x) is AZC and
                    x.occupant_type == newcomer.ls]
        destination = eligible_buildings[0] #take first one, in future, evaluate buildings on some criteria
        house_loc = destination.pos #where is it
        
        if newcomer.ls is not 'edp':
            newcomer.loc.occupancy -= 1
        
        
        
        #add noise
        x = house_loc[0] + np.random.randint(-20,20)
        y = house_loc[1] + np.random.randint(-20,20)
        
        self.grid.place_agent(newcomer, (x,y)) #place
        
        destination.occupants.add(newcomer) #add agent to building roster
        newcomer.loc = destination #update agent loca
        
        destination.occupancy += 1 #update occupancy
        
        
        
    def Remove(self, agent):
        
        agent.loc.occupancy -= 1
        
        self.schedule.remove(agent)
        self.grid.remove_agent(agent)
        
                              
    def addNewcomer(self):
        self.num_nc += 1
        country_of_origin = None
        
       
            
            
        
        
        country_list = ['Syria', 'Eritrea', 'Iraq', 'Afghanistan']
        country = np.random.multinomial(1, [.50,.30,.10,.10], size = 1)
        country_of_origin = country_list[np.where(country == 1)[1][0]]
            
        
            
            
        x = int((self.width / self.num_azc)
                    * .5) + int(uniform(0,30))
        y = int(self.height * .5) + int(uniform(0,30))

        pos = (x,y)

        r = Newcomer(self.num_nc, self, pos, uniform(0,1),
                     country_of_origin, self.specs[country_of_origin])
        self.schedule.add(r)

        self.house(r)
          
           

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        
        
        #adds newcomers to simuluation at a given rate
        if uniform(0,1) < self.nc_rate:
            self.addNewcomer()
            
            
            
            
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
        
        
        
        
class Newcomer(Agent):
    
    def __init__(self, unique_id, model, pos, dq, country_of_origin, specs):
        
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
        
        self.loc = None
        
        self.decision_time = 28 #28 days is the length of the general asylum procedure
        
        self.intake_time = 4 #time until transfer out of ter apel
        
        self.dq = dq #quality of documentation #REMOVE
        
        
        #series of actions undergone during asylum procedure #REMOVE
        self.asylum_procedure = [self.model.rvr.counsel(self),
                                 self.model.ind.interview(self),
                                 self.model.rvr.counsel(self),
                                 self.model.ind.interview(self)]
        
        self.current_step = 0
        
        self.coo = country_of_origin
        
        self.ext_time = 90 #duration of extended procedure
        
        self.specs = specs
        
        self.first = bernoulli.rvs(self.specs[0], size = 1)[0]
        self.second = None
        
        
        
        
            
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
            
            if self.decision_time == 0:
                if self.first == 0:
                    self.ls = 'as_ext'
                    self.model.house(self)
                    
                    self.second = bernoulli.rvs(self.specs[1], size = 1)[0]
                    
                else:
                    self.ls = 'tr'
                    self.model.house(self)
                        
            #try:
            #    self.asylum_procedure[self.current_step]
            #    self.current_step += 1
            #except IndexError:
            #    print(self.ls)
            #  print(self.current_step)


            #if self.current_step == len(self.asylum_procedure):
                
                

            #    if self.dq < self.model.dq_min:
            #        
            #        if self.dq > self.model.dq_ext:
            #            self.ls = 'as_ext'
            #            self.model.house(self)
            #        else:
                        
            #            self.model.Remove(self)
            #    else:
            #        self.ls = 'tr'
            #        self.model.house(self)
                    
        elif self.ls == 'as_ext':
            self.ext_time -= 1
            
            if self.ext_time == 0:
            
                if self.second == 0:
                    self.model.Remove(self)
                else:
                    self.ls = 'tr'
                    self.model.house(self)
                    
                    
        elif self.ls == 'tr':
            pass
 
                    
                    
                    
                
class Building(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
         
        self.capacity = 0
        self.occupants = set([])
        
        self.occupancy = 0
        

                          
                
                

        

class AZC(Building):
    def __init__(self, unique_id, model,occupant_type, pos):
        super().__init__(unique_id, model)
        
        self.capacity = 0
        self.occupants = set([])
        self.occupant_type = occupant_type
        self.pos = pos


    def step(self):
        pass