import mesa
import csv
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


        #sim boilerplate
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True
                
        ####Generate COL
        COL = AZC(0, self, {'edp'})
        COL_coa = COA(0,self, None)
        COL.coa = COL_coa
        COL.modality = 'COL'
        self.coa_ref = COL_coa
        self.ta = COL
        COL.procedure_duration = 2
        self.schedule.add(COL)
        
        #### Generate POLS
        self.number_pols = num_pols
        pol_op_capacity = .75
        pol_size = 400
        pol_duration = 4
        for i in range(self.number_pols):
            city = City(i, self, None)
            POL_COA = COA(i, self, city)
            POL = AZC(i, self, {'as'})
            POL.procedure_duration = pol_duration
            POL.coa = POL_COA
            POL.modality = 'POL'
            POL.operating_capacity = pol_op_capacity
            self.schedule.add(POL)
            ind = IND(i, self, None, POL_COA)
            self.schedule.add(ind)
            POL_COA.ind = ind
    
        
        ##### Generate AZC
        self.pol_to_azc_ratio = int(COL.coa.conservatism/10)
        for i in range(self.number_pols*self.pol_to_azc_ratio):
            city = City(i, self, None)
            AZC_COA = COA(i, self, city)
            azc = AZC(i, self, {'as_ext','tr'})
            azc.modality = 'AZC'
            azc.procedure_duration = 100
            azc.coa = AZC_COA
            self.schedule.add(azc)
            ind = IND(i, self, None, AZC_COA)
            self.schedule.add(ind)
            AZC_COA.ind = ind
            
        ####flow in
        self.in_rate = int(self.number_pols * pol_op_capacity * pol_size / pol_duration)
        self.nc_count = 0      
        
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
        
        
        

       


    def step(self):
        self.schedule.step()
        for i in range(2):
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
        a = Newcomer(self.nc_count, self, self.country_distribution())
        a.coa = self.ta.coa
        self.schedule.add(a)
        #house in COL
        a.loc = self.ta
        self.ta.occupants.add(a)
        self.ta.occupancy += 1
        
        a.current_procedure_time = a.loc.procedure_duration
        
    def Remove(self, agent):
        
        agent.loc.occupancy -= 1 #reduce occupancy of building
        agent.loc.occupants.remove(agent)

        #remove from time n space
        self.schedule.remove(agent)
        


