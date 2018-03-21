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

from newcomer import Newcomer
from organizations import AZC, City, Hotel, Empty, COA

    


class HumanitarianLogistics(Model):
    """A model with: number of azc
        rate of newcomer arrival
        dimensions width and height"""
    
    
    def __init__(self, shock_period, shock_duration, shock_rate,
                 N_cities,N_a,nc_rate, width, height):
        
        #canvas info
        self.width = width
        self.height = height
        
        
        #sim boilerplate
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True
        
        
        
        self.num_nc = 0 #counts number of applicants
        self.num_azc = N_a #number of AZC in sim
        self.nc_rate = nc_rate #rate of inflow of newcomers
        self.num_cities = N_cities #number of cities in sim
        
        #initialize shock values
        self.shock_period = shock_period       #how often does shock occur
        self.shock_duration = shock_duration   #how long does shock last
        self._shock_duration = shock_duration  #current position in shock
        self.shock_rate = shock_rate           #amt of increase during shock
        self.shock = False                     #shock flag
        self.number_added = 1                  #base rate of influx

        #dict of probabilities of first/second decision success rates by country
        self.specs = {'Syria' : [.97,.96],
                      'Eritrea' : [.96,.89],
                     'Iraq' : [.482,.611],
                     'Afghanistan' : [.518,.52]}
        
        self.country_multinomial = [.50,.30,.10,.10]
        
        
        self.country_list = ['Syria', 'Eritrea', 'Iraq', 'Afghanistan']
        self.country_count = np.zeros(4) #keeps track of how many applicants from each country
        

        
        #records capacitiy of each AZC type
        self.datacollector = DataCollector(
            model_reporters = {'Cap - Extended-AS' : calc_extended_as,
                              'Cap - AS' : calc_as})
        
        #records success rates of each country of origin
        self.sr = DataCollector(
            model_reporters = {'Syria' : sr_syria,
                              'Iraq' : sr_iraq,
                              'Eritrea' : sr_eritrea,
                              'Afghanistan' : sr_afgh})
        
        
        
        for city in range(self.num_cities):
            
            pos = (int(self.width / 2), int(self.height / 2)) #placeholder position
            current_city = City(city, self, pos) #instantiates city
            
            current_coa = COA(city, self, current_city)
            self.schedule.add(current_coa)
            #adds city to schedule n grid
            self.schedule.add(current_city) 
            self.grid.place_agent(current_city, (current_city.pos))
            
        
            # Create AZCs
            for i in range(self.num_azc):
                
                if i == 0:
                    occupant_type = 'edp'   # ter apel 
                    
                elif i < self.num_azc - 2:
                    occupant_type = 'as'    # standard AZC
                elif i == self.num_azc - 2:
                    occupant_type = 'as_ext'# extended procedure AZC
                else:
                    occupant_type = 'tr'    # 'Housing' for those with 
                
                #place evenly
                x = int((self.width / self.num_azc) * (i+.5))  
                y = int(self.height * .5)
                
                a = AZC(i, self, occupant_type, (x,y)) #instantiate
                self.schedule.add(a)                   #add in time          
                self.grid.place_agent(a, (x, y))       #add in spaace
                current_city.buildings.add(a)
                if a.occupant_type != 'tr':
                    current_coa.azcs.add(a)
                    current_coa.capacities[a] = a.occupancy
                if a.occupant_type == 'edp':
                    current_coa.ter_apel = a
                    
                
            #create civilian buildings
            #hotels
            x = np.random.randint(0,self.width, dtype = 'int')
            y = np.random.randint(0,self.height, dtype = 'int')
            hotel = Hotel(i, self, (x,y), 50)
            current_city.buildings.add(hotel)
            self.grid.place_agent(hotel, (x,y))
            self.schedule.add(hotel)
            #empty buildings
            x = np.random.randint(0,self.width, dtype = 'int')
            y = np.random.randint(0,self.height, dtype = 'int')
            empty = Empty(i, self, (x,y), 1000)
            current_city.buildings.add(empty)
            self.grid.place_agent(empty, (x,y))
            self.schedule.add(empty)
            
            
            
            
        
            
            
       
    
    
    
    
    def house(self,newcomer):

        #find building for newcomers legal status
        eligible_buildings = [x for x in
                              self.schedule.agents 
                    if type(x) is AZC and
                    x.occupant_type == newcomer.ls]
        
        
        #take first one, in future, evaluate buildings on some criteria
        destination = eligible_buildings[0] 
        house_loc = destination.pos         #where is it
        
        if newcomer.ls is not 'edp':
            newcomer.loc.occupancy -= 1     #reduce occupance of prev building
        
        
        
        #add noise so agents don't overlap
        x = house_loc[0] + np.random.randint(-20,20)
        y = house_loc[1] + np.random.randint(-20,20)
        
        self.grid.move_agent(newcomer, (x,y)) #place
        
        destination.occupants.add(newcomer) #add agent to building roster
        newcomer.loc = destination #update agent location
        
        destination.occupancy += 1 #update occupancy
        
        
        
    def Remove(self, agent):
        
        agent.loc.occupancy -= 1 #reduce occupancy of building
        
        #remove from time n space
        self.schedule.remove(agent)
        self.grid.remove_agent(agent)
        
    def country_distribution(self):
        #draws a random discrete number from multinomial distribution
        country = np.random.multinomial(1, self.country_multinomial, size = 1)
        
        # turns that distribution into a number
        country = np.where(country == 1)[1][0]
        
        
        # updates country count
        self.country_count[country] += 1
        
        # assigns that number to a country
        country_of_origin = self.country_list[country]
        return country_of_origin
                              
    def addNewcomer(self, shock, country_of_origin):
        
        #increase count
        self.num_nc += 1

        if not shock:
            
            country_of_origin = self.country_distribution()
        
        
            
            
          
        else:
            
            self.country_count[self.country_list.index(country_of_origin)] += 1
            
        
        x = np.random.randint(0,10, dtype = 'int')
        y = np.random.randint(0,10, dtype = 'int')    
        #define newcomer
        r = Newcomer(self.num_nc, self, country_of_origin,(x,y))
        self.schedule.add(r)
        self.grid.place_agent(r, r.pos)
        self.house(r) #place n ter apel

          
           

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self) #collects occupancy data
        self.sr.collect(self)            #collects success rate data
        
        
        
        if self.schedule.steps % self.shock_period == 0:
            self.shock = True
        
        if self.shock:
            
            if self._shock_duration > (self._shock_duration / 2):
                self.number_added += self.shock_rate
            else:
                self.number_added -= self.shock_rate
            
            for i in range(int(self.number_added)):
                
                self.addNewcomer(True, 'Syria')  #should be generalized to have shocks from whereever
                
            self._shock_duration -= 1
            
            if self._shock_duration == 0:
                
                self.shock = False
                self._shock_duration = self.shock_duration
                self.number_added = 1
        else:
        
            #adds newcomers to simuluation at a given rate
            if uniform(0,1) < self.nc_rate:
                self.addNewcomer(False, None)
            
            


    
    
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

def sr_syria(model):
    
    newcomers = [agent for agent in model.schedule.agents if
                 type(agent) is Newcomer]
    
    
    syrians = [agent for agent in newcomers if
               agent.coo == 'Syria']
    
    
    status = [agent for agent in syrians if
              agent.ls == 'tr']
    
      
    return 1.0*len(status) / (model.country_count[0] + 1)

def sr_eritrea(model):
    
    newcomers = [agent for agent in model.schedule.agents if
                 type(agent) is Newcomer]
    
    
    syrians = [agent for agent in newcomers if
               agent.coo == 'Eritrea']
    
    
    status = [agent for agent in syrians if
              agent.ls == 'tr']
    
      
    return 1.0*len(status) / (model.country_count[1] + 1)

def sr_iraq(model):
    
    newcomers = [agent for agent in model.schedule.agents if
                 type(agent) is Newcomer]
    
    
    syrians = [agent for agent in newcomers if
               agent.coo == 'Iraq']
    
    
    status = [agent for agent in syrians if
              agent.ls == 'tr']
    
      
    return 1.0*len(status) / (model.country_count[2] + 1)

def sr_afgh(model):
    
    newcomers = [agent for agent in model.schedule.agents if
                 type(agent) is Newcomer]
    
    
    syrians = [agent for agent in newcomers if
               agent.coo == 'Afghanistan']
    
    
    status = [agent for agent in syrians if
              agent.ls == 'tr']
    
      
    return 1.0*len(status) / (model.country_count[3] + 1)