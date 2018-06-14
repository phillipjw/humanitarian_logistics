import numpy as np
import mesa
from model import HumanitarianLogistics, COA, AZC, Newcomer, City, NGO
import activity
from Values import Values
import random
import csv


class ModelExplorer():

    def __init__(self):
        # initializes an empty social network
          
        #initial config
        self.width = 200
        self.height = 200
        self.num_pols = 2
        self.city_size = 20
        self.number_steps = 100

        self.se_min = 1
        self.se_max = 100

        self.st_min = 1
        self.st_max = 100

        self.c_min=1
        self.c_max = 100

        self.otc_min = 1
        self.otc_max = 100

        self.num_random_sample_params_to_do = 2

    def explore_summary(self, filename = 'summary-exploration.csv', exp_all_time_steps=False):
        myData = [["trial", "step", "social_networks", "se_value", "st_value", "c_value", "otc_value", "ng", "ct", "bh", "ac", "staff"]]
        for iter in range(0, self.num_random_sample_params_to_do):
            sim_values = self.run_trial_summary(trial_number = iter, all_time_steps=exp_all_time_steps)
            if sim_values is not None:
                for i in range(0, len(sim_values)):
                    valuesToAdd = sim_values[i]
                    if valuesToAdd is not None:
                        myData.append(valuesToAdd)
        myFile = open(filename, 'w')
        with myFile:
            writer = csv.writer(myFile)
            writer.writerows(myData)
    
    def explore_all(self, filename = 'all-exploration.csv'):
        myData = [["trial", "step", "social_networks", "se_value", "st_value", "c_value", "otc_value", "entity_id", "entity_name", "entity_attribute", "entity_value"]]
        for iter in range(0, self.num_random_sample_params_to_do):
            sim_values = self.run_trial_all(trial_number = iter, all_time_steps=True)
            if sim_values is not None:
                for i in range(0, len(sim_values)):
                    valuesToAdd = sim_values[i]
                    if valuesToAdd is not None:
                        myData.append(valuesToAdd)
        myFile = open(filename, 'w')
        with myFile:
            writer = csv.writer(myFile)
            writer.writerows(myData)
        
    def run_trial_summary(self,  trial_number, all_time_steps=False):
        toReturn = []
        se_value = np.random.randint(low=self.se_min, high=self.se_max)
        st_value = np.random.randint(low=self.st_min, high=self.st_max)
        c_value = np.random.randint(low=self.c_min, high=self.c_max)
        otc_value = np.random.randint(low=self.otc_min, high=self.otc_max)
        try:
            test = HumanitarianLogistics(self.width, self.height, self.num_pols, self.city_size, se_value, st_value, c_value, otc_value)
        except Exception:
            return None
        test.include_social_networks = random.choice([True, False])
        ngo = [x for x in test.schedule.agents if type(x) is NGO]
        coa_array = [coa for coa in test.schedule.agents if type(coa) is COA and coa.city.modality == 'AZC']
        cities = []
        for coa in coa_array:
            if coa.city is not None:
                cities.append(coa.city)
        for step in range(0,self.number_steps):
            test.step()
            buf = []
            for coa in coa_array:
                buf.append([building.health for building in coa.city.azcs])
            bh = np.mean(buf)
            buf = []
            newcomers = [nc for nc in test.schedule.agents if type(nc) is Newcomer and nc.ls == 'as_ext']
            for nc in newcomers:
                buf.append(nc.acculturation)
            ac = np.mean(buf)
            ng = np.mean([ngo.funds for ngo in ngo])
            ct = np.mean([city.public_opinion for city in cities])
            staff = np.mean([coa.staff for coa in coa_array])
            values = [trial_number, step, test.include_social_networks, se_value, st_value, c_value, otc_value, ng, ct, bh, ac, staff]
            if all_time_steps==True:
                toReturn.append(values)
        if all_time_steps == False:
            toReturn.append(values)
        return (toReturn)

    def run_trial_all(self,  trial_number, all_time_steps=False):
        toReturn = []
        se_value = np.random.randint(low=self.se_min, high=self.se_max)
        st_value = np.random.randint(low=self.st_min, high=self.st_max)
        c_value = np.random.randint(low=self.c_min, high=self.c_max)
        otc_value = np.random.randint(low=self.otc_min, high=self.otc_max)
        try:
            test = HumanitarianLogistics(self.width, self.height, self.num_pols, self.city_size, se_value, st_value, c_value, otc_value)
        except Exception:
            return None
        test.include_social_networks = random.choice([True, False])
        ngo = [x for x in test.schedule.agents if type(x) is NGO]
        coa_array = [coa for coa in test.schedule.agents if type(coa) is COA and coa.city.modality == 'AZC']
        cities = []
        for coa in coa_array:
            if coa.city is not None:
                cities.append(coa.city)
                
        for step in range(0,self.number_steps):
            test.step()
            count =0
            for coa in coa_array:
                for building in coa.city.azcs:
                    count = count + 1
                    values = [trial_number, step, test.include_social_networks, 
                          se_value, st_value, c_value, otc_value, count, "Building", "Health", building.health]
                    toReturn.append(values)
            newcomers = [nc for nc in test.schedule.agents if type(nc) is Newcomer and nc.ls == 'as_ext']
            for nc in newcomers:
                values = [trial_number, step, test.include_social_networks, 
                      se_value, st_value, c_value, otc_value, nc.UID, "Newcomer", "Acculturation", nc.acculturation]
                toReturn.append(values)
            count =0
            for x in ngo:
                count = count + 1
                values = [trial_number, step, test.include_social_networks, 
                      se_value, st_value, c_value, otc_value, count, "NGO", "Funds", x.funds]
                toReturn.append(values)
            count =0
            for ct in cities:
                count = count + 1
                values = [trial_number, step, test.include_social_networks, 
                      se_value, st_value, c_value, otc_value, count, "City", "Public Opinion", ct.public_opinion]
                toReturn.append(values)
            count =0
            for coa in coa_array:
                count = count + 1
                values = [trial_number, step, test.include_social_networks, 
                      se_value, st_value, c_value, otc_value, count, "COA", "Staff", coa.staff]
                toReturn.append(values)
        return (toReturn)


