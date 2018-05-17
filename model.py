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


    def __init__(self, width, height, num_pols):

        #canvas info
        self.width = width
        self.height = height
        self.number_pols = num_pols
        
        ##### Shock
        self.shock_duration = 100
        self.shock_position = 0
        self.shock_period = 200
        self.shock = False
        self.shock_rate = 100
        self.shock_flag = False #flag to run sim without shocks
        



        #sim boilerplate
        self.grid = ContinuousSpace(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True
                
        ####Generate COL
        
        COL_coa = COA(0,self, None)
        COL = AZC(0, self, {'edp'}, COL_coa, 'COL')
        COL.modality = 'COL'
        self.coa_ref = COL_coa
        self.ta = COL
        COL.procedure_duration = 2
        
        self.space_per_city = int(self.width / self.number_pols)
        self.pol_to_azc_ratio = int(COL.coa.conservatism/10)
        self.num_azc = self.number_pols * self.pol_to_azc_ratio
        self.space_per_azc = int(self.width / self.num_azc)
        
        
        #### Generate POLS
        pol_op_capacity = .75
        pol_size = 400
        pol_duration = 4
        for i in range(1,self.number_pols+1):
            city = City(i, self, None)
            POL_COA = COA(i, self, city)
            POL = AZC(i, self, {'as'}, POL_COA, 'POL')
            POL.procedure_duration = pol_duration
            POL.operating_capacity = pol_op_capacity
            self.schedule.add(POL)
            ind = IND(i, self, None, POL_COA)
            self.schedule.add(ind)
            POL_COA.ind = ind
    
        
        ##### Generate AZC
        for i in range(1,self.number_pols*self.pol_to_azc_ratio+1):
            city = City(i, self, None)
            AZC_COA = COA(i, self, city)
            azc = AZC(i, self, {'as_ext','tr'}, AZC_COA,'AZC')
            azc.procedure_duration = 100
            self.schedule.add(azc)
            ind = IND(i, self, None, AZC_COA)
            self.schedule.add(ind)
            AZC_COA.ind = ind
            
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
        
        self.confusionMatrix = {'TP': 0,
                                'TN': 0,
                                'FP': 0,
                                'FN': 0}
        
        
        

       


    def step(self):
        self.schedule.step()
        self.sr.collect(self)
        
        if self.shock_flag and self.shock:
            print('shock')
            shock_in = int(self.shock_rate*np.sin((np.pi/self.shock_duration)*self.schedule.steps) + self.current)
            #add increasing amount of newcomers
            for i in range(shock_in):
                self.addNewcomer()

            self.shock_position += 1
            #reset shock conditions
            if self.shock_position == self.shock_duration:
                self.shock = False
                self.shock_position = 0
                print('shock_over')
            
            
            
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
        a.loc = self.ta
        self.ta.occupants.add(a)
        self.ta.occupancy += 1
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
        


