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
from organizations import AZC, City, Hotel, Empty, COA, IND
from viz import AZC_Viz
from Activities import Activity, Football

    


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
        self.num_buildings = 3
        
        #initialize shock values
        self.shock_period = shock_period       #how often does shock occur
        self.shock_duration = shock_duration   #how long does shock last
        self._shock_duration = shock_duration  #current position in shock
        self.shock_rate = shock_rate           #amt of increase during shock
        self.shock = False                     #shock flag
        self.number_added = 1                  #base rate of influx
        self.number_shocks = 4
        self.shock_growth = 2
        
        #dict of probabilities of first/second decision success rates by country
        self.specs = {'Syria' : [.97,.96],
                      'Eritrea' : [.96,.89],
                     'Iraq' : [.482,.611],
                     'Afghanistan' : [.518,.52]}
        
        self.country_multinomial = [.50,.30,.10,.10]
        
        
        self.country_list = ['Syria', 'Eritrea', 'Iraq', 'Afghanistan']
        self.country_count = np.zeros(len(self.country_list)) #keeps track of how many applicants from each country
        self.country_success = np.zeros(len(self.country_list))

        
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
        
        self.capacity_dc = DataCollector(
                model_reporters = {
                        'Current Capacity' : coa_occ,
                        'Projected Capacity' : coa_proj})
        
        
        #add activities
        self.test_activity = Football(0, self, 4)
        self.schedule.add(self.test_activity)
        
        #generate cities
        for city in range(self.num_cities):
            
            pos = (int(self.width / 2), int(self.height / 2)) #placeholder position
            current_city = City(city, self, pos) #instantiates city
            #add COA
            current_coa = COA(city, self, current_city)
            current_city.coa = current_coa
            self.schedule.add(current_coa)
            self.grid.place_agent(current_coa, (int(self.width / 2), self.height - 10))
            current_ind = IND(city, self, current_city)
            self.schedule.add(current_ind)
            current_coa.IND = current_ind
            current_ind.coa = current_coa
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
                
                a = AZC(i, self, occupant_type, (x,y), current_coa) #instantiate
                self.schedule.add(a)                   #add in time          
                self.grid.place_agent(a, (x, y))       #add in spaace
                current_city.buildings.add(a)
                if a.occupant_type != 'tr':
                    current_coa.azcs.add(a)
                    current_coa.capacities[a] = a.occupancy
                if a.occupant_type == 'edp':
                    current_coa.ter_apel = a
                if a.occupant_type == 'tr':
                    current_city.social_housing = a
                    
                #add viz
                v = AZC_Viz(self,a)
                self.schedule.add(v)
                self.grid.place_agent(v, v.pos)
                
                    
                
            #create civilian buildings
                       
            y = int(self.height / 5)
            
            for bdg in range(self.num_buildings):
                
                x = int((self.width / self.num_buildings) * (bdg+.5))

                if bdg == 0:
                    
                    current = Hotel(bdg, self, (x,y),1000)
                    current_city.buildings.add(current)
                    current.city = current_city
                    self.grid.place_agent(current, (x,y))
                    self.schedule.add(current)
                else:
                    empty = Empty(bdg, self, (x,y), 100*bdg)
                    current_city.buildings.add(empty)
                    empty.city = current_city
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
        
        #find coa
        coa = [x for x in 
               self.schedule.agents if
               type(x) is COA][0]
        
        coa.intake(r) #place n ter apel
        coa.newcomers.add(r) #adds NC to coa's list of residents
        r.coa = coa          #likewise for the newcomer

          
           

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self) #collects occupancy data
        self.sr.collect(self)            #collects success rate data
        self.capacity_dc.collect(self)
        
        
        
        if self.schedule.steps % self.shock_period == 0:
            self.shock = True
            self.shock_counter = 0
        
        if self.shock:
            
            #if self._shock_duration > (self._shock_duration / 2):
            #    self.number_added += self.shock_rate
            #else:
            #    self.number_added -= self.shock_rate
            self.number_added += self.shock_rate
            for i in range(int(self.number_added)):
                
                self.addNewcomer(True, 'Syria')  #should be generalized to have shocks from whereever
                self.shock_counter += 1
            self._shock_duration -= 1
            
            
            if self._shock_duration == 0:
                
                self.shock = False
                self._shock_duration = self.shock_duration
                self.number_added = 1
                
                self.shock_counter = 0
                self.shock_rate = self.shock_rate*self.shock_growth
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
    
    return success_counter(model,'Syria')

def sr_eritrea(model):
    
    return success_counter(model,'Eritrea')

def sr_iraq(model):
    
    return success_counter(model,'Iraq')

def sr_afgh(model):
    
    return success_counter(model,'Afghanistan')

def success_counter(model,country):
    
    '''
    Tabulates how many of a given country get TR
    '''
    country = model.country_list.index(country)
    status = model.country_success[country]
    
    return 1.0*status / (model.country_count[country] + 1)

def coa_occ(model):
    coa = [agent for agent in model.schedule.agents if 
           type(agent) is COA][0]
    return coa.get_occupancy_pct()

def coa_proj(model):
    coa = [agent for agent in model.schedule.agents if 
           type(agent) is COA][0]
    return coa.project_dc()
    
    