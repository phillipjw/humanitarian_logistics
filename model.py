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
from organizations import COA, AZC, Hotel, Empty, City, IND, NGO
from viz import AZC_Viz
from socialrelationship import SocialRelationship

    

class HumanitarianLogistics(Model):
    """A model with: number of azc
        rate of newcomer arrival
        dimensions width and height"""
    SOCIAL_ACTIVITIES = set(["Football", "Craft", "LanguageClass", 'Volunteer', 'Socialize', 'Work'])
    
    def __init__(self, po_uniform,width, height, num_pols, city_size,
                 coa_se,coa_st,coa_c,coa_otc,
                 ind_se,ind_st,ind_c,ind_otc,
                 ngo_se,ngo_st,ngo_c,ngo_otc):

        #canvas info
        self.width = width
        self.height = height
        self.number_pols = num_pols
        self.city_size = city_size
        self.po_uniform = po_uniform
        #test health params
        #health param
        self.health_decay = .35
        self.football_increase = 4
        
        ##### Shock
        self.shock_duration = 100
        self.shock_position = 0
        self.shock_period = 200
        self.shock = False
        self.shock_rate = 100
        self.shock_flag = False #flag to run sim without shocks
        self.shock_inverse = False
        self.dq = True #flag for which type of IND decision to make
        
        self.coa_values = {'SE':coa_se,
                           'ST': coa_st,
                           'C': coa_c,
                           'OTC':coa_otc}
        
        self.ind_values = {'SE':ind_se,
                           'ST': ind_st,
                           'C': ind_c,
                           'OTC':ind_otc}
        
        self.ngo_values = {'SE':ngo_se,
                           'ST': ngo_st,
                           'C': ngo_c,
                           'OTC':ngo_otc}
        
        
        

        #sim boilerplate
        self.grid = ContinuousSpace(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True
                
        ####Generate COL
        self.procedure_durations = {'edp':2,
                                    'as':4,
                                    'as_ext':90,
                                    'tr': 35}
        self.pol_to_azc_ratio = 4 
        self.space_per_city = int(self.width / self.number_pols)
        self.num_azc = self.number_pols * self.pol_to_azc_ratio
        self.space_per_azc = int(self.width / self.num_azc)
        self.fraction_ngo = .30
        self.num_nc = 0
        self.wait_times = []

        self.city_count = 1
        
        
            
            
        
        
        ####### Generate COLS
        self.ta = City(self.city_count,self, {'edp'}, 'COL')
        
        self.total_num_facilities = self.number_pols+self.number_pols*self.pol_to_azc_ratio
        

        #### Generate POLS
        for i in range(1,self.number_pols+1):
            city = City(i, self, {'as'}, 'POL')

        ##### Generate AZC
        for i in range(1,self.number_pols*self.pol_to_azc_ratio):
            city = City(i, self, {'as_ext', 'tr'}, 'AZC')
            
        ##### cultural_wellbeing
        self.cultural_wellbeing = False
        self.cw_group = 'A'
            
        

        
            
        ####flow in
        self.in_rate = 10 #int(self.number_pols * pol_op_capacity * pol_size / pol_duration)
        self.nc_count = 0  
        self.var = 5
        self.freq = 60
        
        
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
        
        ### Staff data collector
        self.staff_index = -1
        staff_functions = {}
        po_functions = {}
        self.staff = self.modalities
        for i in range(0, len(self.staff)):
            self.staff_index = i
            staff_functions[self.staff[self.staff_index]] = staff
            po_functions[self.staff[self.staff_index]] = po
        
        self.staff_dc = DataCollector(model_reporters = staff_functions)
        self.po_dc = DataCollector(model_reporters = po_functions)
    
        
        self.ind_statement = 1
        
        self.ls_index = -1
        ls_functions = {}
        self.ls = ['edp', 'as', 'as_ext', 'tr']
        network_functions = {}
        for i in range(0, len(self.ls)):
            self.ls_index = i
            network_functions[self.ls[self.ls_index]] = network_size
            ls_functions[self.ls[self.ls_index]] = distress
        
        self.ls_dc = DataCollector(model_reporters = ls_functions)
        self.network_dc = DataCollector(model_reporters= network_functions)
        
        self.int = ['True','False']
        int_functions = {}
        self.int_index =  -1
        for i in range(0, len(self.int)):
            self.int_index = i
            int_functions[self.int[self.int_index]] = integrated
        
        self.int_dc = DataCollector(model_reporters = int_functions)
        
        
        
        self.action_agents = []
        self.actions = []
        self.include_social_networks = False
       


    def step(self):
        self.schedule.step()
        #self.sr.collect(self)
        #self.azc_health.collect(self)
        #self.modality_occ.collect(self)
        #self.cm_dc.collect(self)
        #self.staff_dc.collect(self)
        self.ls_dc.collect(self)
        #self.network_dc.collect(self)
        #self.po_dc.collect(self)
        #self.int_dc.collect(self)
        
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
    
        if self.include_social_networks:
            self.adjust_social_networks()
            
    def reset_social_network_lists(self):
        self.action_agents=[]
        self.actions=[]
    
    def adjust_social_networks(self):
        for i in range(0, len(self.action_agents)):
            agent_i = self.action_agents[i]
            action_i = self.actions[i][0]
            city_i = self.actions[i][1]
            for j in range(0, len(self.actions)):
               agent_j = self.action_agents[j]
               action_j = self.actions[j][0]
               city_j = self.actions[j][1]
               if i != j:
                   if city_i == city_j:
                       if action_i.name == action_j.name:
                           if action_i.name in HumanitarianLogistics.SOCIAL_ACTIVITIES:
                               similarity = 1-(abs(agent_i.values.v_tau[3]-agent_j.values.v_tau[3])/100)
                               if action_i.name == 'Socialize':
                                   #OTC dependent bias against other culture relationship formation
                                   relationship = SocialRelationship(agent_j, similarity)
                                   if (relationship in agent_i.sn.network) == False:
                                       if agent_i.coo != agent_j.coo:
                                           if np.random.uniform(0,100) < agent_i.values.v_tau[3]:
                                               similarity = 1-(abs(agent_i.values.v_tau[3]-agent_j.values.v_tau[3])/100)
                                               agent_i.sn.bondWithAgent(agent_j, similarity)
                                       else:
                                           if abs(agent_i.political_polarity - agent_j.political_polarity) < (1-(agent_i.values.v_tau[2]/100)):
                                               similarity = 1-(abs(agent_i.values.v_tau[2]-agent_j.values.v_tau[2])/100)
                                               agent_i.sn.bondWithAgent(agent_j, similarity)
    
                                   else: 
                                       agent_i.sn.bondWithAgent(agent_j, similarity)
        self.reset_social_network_lists()

                
            
    
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
        if self.ind_statement != None:
            a = Newcomer(self.nc_count, self, self.country_distribution(), self.ta.coa)
            if a.second == 0 and np.random.uniform(0,1) > self.ind_statement:
                return
            else:
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

def get_staff(model, idx):
    
    staff =  np.mean([building.health for building in
                         model.schedule.agents if
                         type(building) is AZC and
                         building.modality == model.modalities[idx]])
    return staff
def staff(model):
    model.staff_index += 1
    if model.staff_index == len(model.staff):
        model.staff_index = 0
    return get_staff(model, model.staff_index)

def distress(model):
    model.ls_index += 1
    if model.ls_index == len(model.ls):
        model.ls_index = 0
    return get_distress(model, model.ls_index)

def get_distress(model, idx):
    
    ncs = np.mean([nc.values.health for nc in model.schedule.agents if
                   type(nc) is Newcomer and
                   nc.ls == model.ls[idx]])
    return ncs

def po(model):
    model.staff_index += 1
    if model.staff_index == len(model.modalities):
        model.staff_index = 0
    return get_po(model, model.staff_index)

def get_po(model, idx):
    
    ncs = np.mean([ngo.city.public_opinion for ngo in model.schedule.agents if
                   type(ngo) is NGO and
                   ngo.city.modality == model.modalities[idx]])
    return ncs

def integrated(model):
    model.int_index += 1
    if model.int_index == (len(model.int)):
        model.int_index = 0
    return get_integrated(model, model.int_index)

def get_integrated(model, integrated):
    nc = [nc.values.health for nc in model.schedule.agents if type(nc) is
                   Newcomer and nc.loc.modality == 'AZC']
    if len(nc) == 0:
        return 0
    else:
        
    
        if model.int[integrated] == 'True':
            
            #get max distress
            ncs = np.max(nc)
        else:
            ncs = np.min(nc)
        
       # ncs = np.mean([nc.values.health for nc in model.schedule.agents if type(nc) is
       #                Newcomer and str(nc.segregated) == model.int[integrated]])
        print('VARIANCE', np.std(nc))
        
        zr = [z for z  in nc if z == 0.0]
        print('PCT ZEROS', len(zr)/len(nc))
        
        
        if np.isnan(ncs):
            return 0
        return ncs

def network_size(model):
    model.ls_index += 1
    if model.ls_index == len(model.ls):
        model.ls_index = 0
    return get_network_size(model, model.ls_index)

def get_network_size(model, idx):
    # the average size of a newcomer's social network seems pretty stable
    # however, this function gets called four times each time step
    # each time with a different idx
    # edp: is always 0 this is because they can't participate in anything with a sn
    # as: is the largest sn stablizing around 80-90 under default parameters
    # as_ext and tr are about the same size and sit between 30-40
    
    # in the plot it seems like each of these individual numbers are
    # being plotted as if they occur on different time steps. I think we
    # want to plot each type (or just plot them for one type (as, as_ext or tr))
    ncs = np.mean([len(nc.sn.network) for nc in model.schedule.agents if
                   type(nc) is Newcomer and nc.ls == model.ls[idx]])
    print(model.ls[idx],": ",ncs)
    return ncs

        


