import mesa
import csv
# model.py
from mesa.space import ContinuousSpace
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from scipy.stats import bernoulli


from random import randrange
from random import uniform
import numpy as np

from newcomer import Newcomer
from organizations import COA, AZC, Hotel, Empty, City, IND
from viz import AZC_Viz
#from Activities import Activity, Football




class HumanitarianLogistics(Model):
    """A model with: number of azc
        rate of newcomer arrival
        dimensions width and height"""


    def __init__(self, width, height, num_pols, city_size):

        #canvas info
        self.width = width
        self.height = height
        self.number_pols = num_pols
        self.city_size = city_size
        
        ##### Shock
        self.shock_duration = 100
        self.shock_position = 0
        self.shock_period = 200
        self.shock = False
        self.shock_rate = 100
        self.shock_flag = False #flag to run sim without shocks
        self.shock_inverse = False
        
        self.coa_values = {'SE':20,
                           'ST': 70,
                           'C': 30,
                           'OTC':20}
        
        
        

        #sim boilerplate
        self.grid = ContinuousSpace(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True
                
        ####Generate COL
        self.procedure_durations = {'edp':2,
                                    'as':4,
                                    'as_ext':90,
                                    'tr': 35}
        self.pol_to_azc_ratio = int(self.coa_values['C']/10)
        self.space_per_city = int(self.width / self.number_pols)
        self.num_azc = self.number_pols * self.pol_to_azc_ratio
        self.space_per_azc = int(self.width / self.num_azc)
        
        

        self.city_count = 1
        
        
        ####### Generate COLS
        self.ta = City(self.city_count,self, {'edp'}, 'COL')

        #### Generate POLS
        for i in range(1,self.number_pols+1):
            city = City(i, self, {'as'}, 'POL')

        ##### Generate AZC
        for i in range(1,self.number_pols*self.pol_to_azc_ratio+1):
            city = City(i, self, {'as_ext', 'tr'}, 'AZC')
            
            

        
            
        ####flow in
        self.in_rate = 30 #int(self.number_pols * pol_op_capacity * pol_size / pol_duration)
        self.nc_count = 0  
        self.var = 10
        self.freq = 60
        self.dq = False #flag for which type of IND decision to make
        
        #dict of probabilities of first/second decision success rates by country
        self.specs = {}
         # list of multinomial probabilities for countries
        self.country_multinomial = []
        # list of shock distributions for countries related to adding newcomers
        self.country_shock_dist = []
        #list of country ids
        self.country_list = []
        self.country_count = np.zeros(len(self.country_list))
        ###NC Attributes
        with open("country-input.csv") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                decisionList = []
                decisionList.append(float(row['DecisionA']))
                decisionList.append(float(row['DecisionB']))
                self.specs[row['Country']] = decisionList
                self.country_shock_dist.append(row['ShockDist'])
                self.country_list.append(row['Country'])
                self.country_multinomial.append(row['Multinomial'])
                
        self.country_count = np.zeros(len(self.country_list)) #keeps track of how many applicants from each country
        self.country_success = np.zeros(len(self.country_list))
        self.current_country_index = -1
        
        #records success rates of each country of origin using current_country_index
        #which is manipulated in sr_country
        sr_functions = {}
        for i in range(0, len(self.country_list)):
            self.current_country_index = i
            sr_functions[self.country_list[self.current_country_index]] = sr_country

        self.sr = DataCollector(model_reporters = sr_functions)
        
        #records the health of newcomers in each facility, POL v AZC
        self.azcs = [azc for azc in self.schedule.agents if
                     type(azc) is AZC and azc.modality == 'AZC']
        azc_health_functions = {}
        self.azc_index = -1
        for i in range(0,len(self.azcs)):
            self.azc_index = i
            azc_health_functions[self.azcs[self.azc_index]] = azc_health
        self.azc_health = DataCollector(model_reporters = azc_health_functions)
        
        ###records occupancies per modality
        self.modalities = ['COL', 'POL', 'AZC']
        modality_functions = {}
        self.modality_index = -1
        for i in range(0,len(self.modalities)):
            self.modality_index = i
            modality_functions[self.modalities[self.modality_index]] = modality_occupancy
        
        self.modality_occ = DataCollector(model_reporters = modality_functions)
        
        self.confusionMatrix = {'TP': 0,
                                'TN': 0,
                                'FP': 0,
                                'FN': 0}
        
        #### Confusion matrix Data Collector
        self.cm_index = -1
        cm_functions = {}
        self.cm = list(self.confusionMatrix.keys())
        for i in range(0, len(self.cm)):
            self.cm_index = i
            cm_functions[self.cm[self.cm_index]] = cm
            
        self.cm_dc = DataCollector(model_reporters = cm_functions)
        
        
        

       


    def step(self):
        self.schedule.step()
        self.sr.collect(self)
        self.azc_health.collect(self)
        self.modality_occ.collect(self)
        self.cm_dc.collect(self)
        
        if self.shock_flag and self.shock:
            if self.shock_inverse:
                shock_in = int(-1*self.shock_rate*np.sin((np.pi/self.shock_duration)*self.schedule.steps) + self.current)
                #add increasing amount of newcomers
            else:
                shock_in = int(self.shock_rate*np.sin((np.pi/self.shock_duration)*self.schedule.steps) + self.current)
                
            for i in range(shock_in):
                self.addNewcomer()

            self.shock_position += 1
            #reset shock conditions
            if self.shock_position == self.shock_duration:
                self.shock = False
                self.shock_position = 0
                
            
            
            
        else: 
            
            #check for shock
            if self.schedule.steps % self.shock_period == 0:
                self.shock = True
            
            #if no shock, do normal
            self.current = int(self.var*(np.sin((1/self.freq)*self.schedule.steps)) + self.in_rate)
            for i in range(self.current):
                self.addNewcomer()
    
        
            
    
    def country_distribution(self):
        #draws a random discrete number from multinomial distribution
        country = np.random.multinomial(1, self.country_multinomial, size = 1)

        # turns that distribution into a number
        country = np.where(country == 1)[1][0]


        # updates country count
        #self.country_count[country] += 1

        # assigns that number to a country
        country_of_origin = self.country_list[country]
        return country_of_origin
    
    def addNewcomer(self):
        
        #gen NC attributes
        self.nc_count += 1
        a = Newcomer(self.nc_count, self, self.country_distribution(), self.ta.coa)
        self.schedule.add(a)
        #house in COL
        a.loc = self.ta.azc
        self.ta.azc.occupants.add(a)
        self.ta.azc.occupancy += 1
        self.country_count[self.country_list.index(a.coo)] += 1
        
        a.current_procedure_time = a.loc.procedure_duration
        
    def Remove(self, agent):
        
        agent.loc.occupancy -= 1 #reduce occupancy of building
        agent.loc.occupants.remove(agent)

        #remove from time n space
        self.schedule.remove(agent)
    
def sr_country(model):

    model.current_country_index = model.current_country_index+1
    if model.current_country_index >= len(model.country_list):
        model.current_country_index = 0
    
    return success_counter(model,model.country_list[model.current_country_index])

def success_counter(model,country):

    '''
    Tabulates how many of a given country get TR
    '''
    country = model.country_list.index(country)
    status = model.country_success[country]

    return 1.0*status / (model.country_count[country] + 1)

def azc_health(model):
    '''
    calcs average health of a newcomer in a particular facility modality
    '''
    
    model.azc_index += 1
    if model.azc_index == len(model.azcs):
        model.azc_index = 0
    return get_health(model, model.azc_index)

def get_health(model, index):
    
    building = model.azcs[index]
    health = np.mean([newcomer.values.health for newcomer in building.occupants])
    return health
def modality_occupancy(model):
    
    model.modality_index += 1
    
    if model.modality_index  == len(model.modalities):
        model.modality_index = 0
    return get_modality(model,model.modalities[model.modality_index])

def get_modality(model, modality):
    
    occupancy = np.mean([building.city.coa.get_occupancy_pct() for building in
                         model.schedule.agents if
                         type(building) is AZC and
                         building.modality == modality])
    
    return occupancy

def get_cm(model, idx):
    return 1.*model.confusionMatrix[model.cm[idx]] / (sum(list(model.confusionMatrix.values()))+1)
    
def cm(model):
    model.cm_index += 1
    if model.cm_index == len(model.cm):
        model.cm_index = 0
    return get_cm(model, model.cm_index)
        


