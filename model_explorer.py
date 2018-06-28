import numpy as np
import mesa
from model import HumanitarianLogistics, COA, AZC, Newcomer, City, NGO, IND
import activity
from Values import Values
import random
import csv


class ModelExplorer():

    def __init__(self, p_width=200, p_height=200, p_num_pols=2, p_city_size=20, p_number_steps=200,
                 p_se_min=1, p_se_max=100, p_st_min=1, p_st_max=100, p_c_min=1, p_c_max=100, p_otc_min=1, p_otc_max=100,
                 p_num_random_sample_params_to_do=100):

        self.width = p_width
        self.height = p_height
        self.num_pols = p_num_pols
        self.city_size = p_city_size
        self.number_steps = 500

        self.se_min = p_se_min
        self.se_max = p_se_max

        self.st_min = p_st_min
        self.st_max = p_st_max

        self.c_min= p_c_min
        self.c_max = p_c_max

        self.otc_min = p_otc_min
        self.otc_max = p_otc_max

        self.num_random_sample_params_to_do = p_num_random_sample_params_to_do

    def explore_summary(self, filename = 'summary-exploration.csv', exp_all_time_steps=False):
        myData = [["trial", "step", "social_networks", "se_value", "st_value", "c_value", "otc_value", "ng", "ct", "bh", "ac", "staff"]]
        for iter in range(0, self.num_random_sample_params_to_do):
            print(iter)
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
            
            
    def sweep_po(self, filename = 'sweep-po-exploration.csv', exp_all_time_steps=True):
        myData = [["trial", "step", "po_value", "ngo_funds", "city_po", "building_health", "newcomer_acculturation", "azc_staff", "city_costs", "city_crime", "coa_costs", "newcomer_health", "newcomer_distress"]]
        
        po_val = [0.01, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.99]

        i = 1
        for val in po_val:
            print("----------------------------------------------------------------------------------------")
            print(val)
            print("----------------------------------------------------------------------------------------")
            sim_values = self.run_po_sweep_trial(po_value=val, trial_id = i, all_time_steps = exp_all_time_steps)
            if sim_values is not None:
                for i in range(0, len(sim_values)):
                    valuesToAdd = sim_values[i]
                    if valuesToAdd is not None:
                        myData.append(valuesToAdd)
        myFile = open(filename, 'w')
        with myFile:
            writer = csv.writer(myFile)
            writer.writerows(myData)
    
    def sweep_ngo(self, filename = 'sweep-ngo-exploration.csv', exp_all_time_steps=True):
        myData = [["trial", "step", "se_value", "st_value", "c_value", "otc_value", "ngo_funds", "city_po", "building_health", "newcomer_acculturation", "azc_staff", "city_costs", "city_crime", "coa_costs", "newcomer_health", "newcomer_distress"]]
        
        ngo_se = [20, 40, 60, 80]
        ngo_st = [20, 40, 60, 80]
        ngo_c =  [20, 40, 60, 80]
        ngo_otc = [20, 40, 60, 80]
        
        i = 1
        for se in ngo_se:
            for st in ngo_st:
                for c in ngo_c:
                    for otc in ngo_otc:
                         i = i + 1
                         params = [se, st, c, otc]
                         print("----------------------------------------------------------------------------------------")
                         print(params)
                         print("----------------------------------------------------------------------------------------")
                         sim_values = self.run_ngo_sweep_trial(se_value = se, st_value= st, c_value = c, otc_value = otc, trial_id = i, all_time_steps = exp_all_time_steps)
                         if sim_values is not None:
                             for i in range(0, len(sim_values)):
                                 valuesToAdd = sim_values[i]
                                 if valuesToAdd is not None:
                                     myData.append(valuesToAdd)
        myFile = open(filename, 'w')
        with myFile:
            writer = csv.writer(myFile)
            writer.writerows(myData)
    
    
    def sweep_coa(self, filename = 'sweep-coa-exploration.csv', exp_all_time_steps=True):
        myData = [["trial", "step", "se_value", "st_value", "c_value", "otc_value", "ngo_funds", "city_po", "building_health", "newcomer_acculturation", "azc_staff", "city_costs", "city_crime", "coa_costs", "newcomer_health", "newcomer_distress"]]
        
        coa_se = [20, 40, 60, 80]
        coa_st = [20, 40, 60, 80]
        coa_c =  [20, 40, 60, 80]
        coa_otc = [20, 40, 60, 80]
        
        i = 1
        for se in coa_se:
            for st in coa_st:
                for c in coa_c:
                    for otc in coa_otc:
                         i = i + 1
                         params = [se, st, c, otc]
                         print("----------------------------------------------------------------------------------------")
                         print(params)
                         print("----------------------------------------------------------------------------------------")
                         sim_values = self.run_coa_sweep_trial(se_value = se, st_value= st, c_value = c, otc_value = otc, trial_id = i, all_time_steps = exp_all_time_steps)
                         if sim_values is not None:
                             for i in range(0, len(sim_values)):
                                 valuesToAdd = sim_values[i]
                                 if valuesToAdd is not None:
                                     myData.append(valuesToAdd)
        myFile = open(filename, 'w')
        with myFile:
            writer = csv.writer(myFile)
            writer.writerows(myData)
    
    def sweep_all(self, exp_all_time_steps, coa_se, coa_st, coa_c, coa_otc, ngo_se, ngo_st, ngo_c, ngo_otc):
        
        myData = [["trial", "step", "coa_se_value", "coa_st_value", "coa_c_value", "coa_otc_value", "ngo_se_value", "ngo_st_value", "ngo_c_value", "ngo_otc_value", "ngo_funds", "city_po", "building_health", "newcomer_acculturation", "azc_staff", "city_costs", "city_crime", "coa_costs", "newcomer_health", "newcomer_distress"]]
        
        fileprefix = 'sweep-all-exploration-'
        filesuffix = '.csv'
        
        coa_se_part = "coa_se"+str(coa_se[0])+'-'+str(coa_se[len(coa_se)-1])+'-'
        coa_st_part = "coa_st"+str(coa_st[0])+'-'+str(coa_st[len(coa_st)-1])+'-'
        coa_c_part = "coa_c"+str(coa_c[0])+'-'+str(coa_c[len(coa_c)-1])+'-'
        coa_otc_part = "coa_otc"+str(coa_otc[0])+'-'+str(coa_otc[len(coa_otc)-1])+'-'
        
        ngo_se_part = "ngo_se"+str(coa_se[0])+'-'+str(ngo_se[len(ngo_se)-1])+'-'
        ngo_st_part = "ngo_st"+str(coa_st[0])+'-'+str(ngo_st[len(ngo_st)-1])+'-'
        ngo_c_part = "ngo_c"+str(coa_c[0])+'-'+str(ngo_c[len(ngo_c)-1])+'-'
        ngo_otc_part = "ngo_otc"+str(coa_otc[0])+'-'+str(ngo_otc[len(ngo_otc)-1])
        
        filename = fileprefix + coa_se_part + coa_st_part + coa_c_part + coa_otc_part + ngo_se_part + ngo_st_part + ngo_c_part + ngo_otc_part + filesuffix
        myFile = open(filename, 'w')
        with myFile:
            writer = csv.writer(myFile)
            writer.writerows(myData)
        
        i = 0
        for cse in coa_se:
            for cst in coa_st:
                for cc in coa_c:
                    for cotc in coa_otc:
                        for nse in ngo_se:
                            for nst in ngo_st:
                                for nc in ngo_c:
                                    for notc in ngo_otc:
                                        params = [cse, cst, cc, cotc, nse, nst, nc, notc]
                                        print("----------------------------------------------------------------------------------------")
                                        print(params)
                                        print("----------------------------------------------------------------------------------------")
                                        sim_values = self.run_all_sweep_trial(coa_se_value = cse, coa_st_value= cst, coa_c_value = cc, coa_otc_value = cotc,
                                                                              ngo_se_value = nse, ngo_st_value= nst, ngo_c_value = nc, ngo_otc_value = notc, 
                                                                              trial_id = i, all_time_steps = exp_all_time_steps)
                                        i = i + 1
                                        if sim_values is not None:
                                            for x in range(0, len(sim_values)):
                                                valuesToAdd = sim_values[x]
                                                if valuesToAdd is not None:
                                                    myFile = open(filename, 'a')
                                                    with myFile:
                                                        writer = csv.writer(myFile)
                                                        writer.writerows([valuesToAdd])
    
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
    
    def run_all_sweep_trial(self, coa_se_value, coa_st_value, coa_c_value, coa_otc_value, ngo_se_value, ngo_st_value, ngo_c_value, ngo_otc_value, 
                           trial_id, all_time_steps):
        toReturn = []
        try:
            test = HumanitarianLogistics(self.width, self.height, self.num_pols, self.city_size, coa_se_value, coa_st_value, coa_c_value, coa_otc_value)
            test.include_social_networks = False
            ngo = [x for x in test.schedule.agents if type(x) is NGO]
            for unit in ngo:
                unit.values = Values(10, ngo_se_value,ngo_st_value,ngo_c_value,ngo_otc_value, unit)
            coa_array = [coa for coa in test.schedule.agents if type(coa) is COA and coa.city.modality == 'AZC']
            
            inds = [ind for ind in test.schedule.agents if type(ind) is IND]
            cities = []
            for coa in coa_array:
                if coa.city is not None:
                    cities.append(coa.city)
            for step in range(0,self.number_steps):
                test.step()
                buf_coa_cost = []
                for ind_unit in inds:
                    buf_coa_cost.append([ind_unit.city.coa.housing_costs + ind_unit.city.coa.hotel_costs])
                coa_costs = np.nansum(buf_coa_cost)
                buf = []
                for coa in coa_array:
                    buf.append([building.health for building in coa.city.azcs])
                bh = np.nanmean(buf)
                buf_ac = []
                buf_health = []
                buf_distress = []
                newcomers = [nc for nc in test.schedule.agents if type(nc) is Newcomer and nc.ls == 'as_ext']
                for nc in newcomers:
                    buf_ac.append(nc.acculturation)
                    buf_health.append(nc.health)
                    buf_distress.append(nc.values.health)
                ac = np.nanmean(buf_ac)
                nc_health = np.nanmean(buf_health)
                nc_distress = np.nanmean(buf_distress)
                ng = np.nanmean([ngo.funds for ngo in ngo])
                ct = np.nanmean([city.public_opinion for city in cities])
                ct_costs = np.nanmean([city.costs for city in cities])
                ct_crime = np.nanmean([city.crime for city in cities])
                staff = np.nanmean([coa.staff for coa in coa_array])
                values = [trial_id, step, coa_se_value, coa_st_value, coa_c_value, coa_otc_value, ngo_se_value, ngo_st_value, ngo_c_value, ngo_otc_value, ng, ct, bh, ac, staff, ct_costs, ct_crime, coa_costs, nc_health, nc_distress]
                if all_time_steps==True:
                    toReturn.append(values)
            if all_time_steps == False:
                toReturn.append(values)
            return (toReturn)
        except Exception:
            return None
            
    def run_coa_sweep_trial(self, se_value, st_value, c_value, otc_value, trial_id, all_time_steps=True):
        toReturn = []
        try:
            test = HumanitarianLogistics(self.width, self.height, self.num_pols, self.city_size, se_value, st_value, c_value, otc_value)
            test.include_social_networks = False
            ngo = [x for x in test.schedule.agents if type(x) is NGO]
            coa_array = [coa for coa in test.schedule.agents if type(coa) is COA and coa.city.modality == 'AZC']
            inds = [ind for ind in test.schedule.agents if type(ind) is IND]
            cities = []
            for coa in coa_array:
                if coa.city is not None:
                    cities.append(coa.city)
            for step in range(0,self.number_steps):
                test.step()
                buf_coa_cost = []
                for ind_unit in inds:
                    buf_coa_cost.append([ind_unit.city.coa.housing_costs + ind_unit.city.coa.hotel_costs])
                coa_costs = np.nansum(buf_coa_cost)
                buf = []
                for coa in coa_array:
                    buf.append([building.health for building in coa.city.azcs])
                bh = np.nanmean(buf)
                buf_ac = []
                buf_health = []
                buf_distress = []
                newcomers = [nc for nc in test.schedule.agents if type(nc) is Newcomer and nc.ls == 'as_ext']
                for nc in newcomers:
                    buf_ac.append(nc.acculturation)
                    buf_health.append(nc.health)
                    buf_distress.append(nc.values.health)
                ac = np.nanmean(buf_ac)
                nc_health = np.nanmean(buf_health)
                nc_distress = np.nanmean(buf_distress)
                ng = np.nanmean([ngo.funds for ngo in ngo])
                ct = np.nanmean([city.public_opinion for city in cities])
                ct_costs = np.nanmean([city.costs for city in cities])
                ct_crime = np.nanmean([city.crime for city in cities])
                staff = np.nanmean([coa.staff for coa in coa_array])
                values = [trial_id, step, se_value, st_value, c_value, otc_value, ng, ct, bh, ac, staff, ct_costs, ct_crime, coa_costs, nc_health, nc_distress]
                if all_time_steps==True:
                    toReturn.append(values)
            if all_time_steps == False:
                toReturn.append(values)
            return (toReturn)
        except Exception:
            return None
    
    def run_ngo_sweep_trial(self, se_value, st_value, c_value, otc_value, trial_id, all_time_steps=True):
        toReturn = []
        try:
            test = HumanitarianLogistics(self.width, self.height, self.num_pols, self.city_size, 55, 65, 45, 60)
            test.include_social_networks = False
            ngo = [x for x in test.schedule.agents if type(x) is NGO]
            for unit in ngo:
                unit.values = Values(10, se_value,st_value,c_value,otc_value, unit)
                
            coa_array = [coa for coa in test.schedule.agents if type(coa) is COA and coa.city.modality == 'AZC']
            inds = [ind for ind in test.schedule.agents if type(ind) is IND]
            cities = []
            for coa in coa_array:
                if coa.city is not None:
                    cities.append(coa.city)
            for step in range(0,self.number_steps):
                test.step()
                buf_coa_cost = []
                for ind_unit in inds:
                    buf_coa_cost.append([ind_unit.city.coa.housing_costs + ind_unit.city.coa.hotel_costs])
                coa_costs = np.nansum(buf_coa_cost)
                buf = []
                for coa in coa_array:
                    buf.append([building.health for building in coa.city.azcs])
                bh = np.nanmean(buf)
                buf_ac = []
                buf_health = []
                buf_distress = []
                newcomers = [nc for nc in test.schedule.agents if type(nc) is Newcomer and nc.ls == 'as_ext']
                for nc in newcomers:
                    buf_ac.append(nc.acculturation)
                    buf_health.append(nc.health)
                    buf_distress.append(nc.values.health)
                ac = np.nanmean(buf_ac)
                nc_health = np.nanmean(buf_health)
                nc_distress = np.nanmean(buf_distress)
                ng = np.nanmean([ngo.funds for ngo in ngo])
                ct = np.nanmean([city.public_opinion for city in cities])
                ct_costs = np.nanmean([city.costs for city in cities])
                ct_crime = np.nanmean([city.crime for city in cities])
                staff = np.nanmean([coa.staff for coa in coa_array])
                values = [trial_id, step, se_value, st_value, c_value, otc_value, ng, ct, bh, ac, staff, ct_costs, ct_crime, coa_costs, nc_health, nc_distress]
                if all_time_steps==True:
                    toReturn.append(values)
            if all_time_steps == False:
                toReturn.append(values)
            return (toReturn)
        except Exception:
            return None
    
    def run_po_sweep_trial(self, po_value, trial_id, all_time_steps=True):
        toReturn = []
        try:
            test = HumanitarianLogistics(self.width, self.height, self.num_pols, self.city_size, 55, 65, 45, 60)
            test.include_social_networks = False
            ngo = [x for x in test.schedule.agents if type(x) is NGO]
            coa_array = [coa for coa in test.schedule.agents if type(coa) is COA and coa.city.modality == 'AZC']
            inds = [ind for ind in test.schedule.agents if type(ind) is IND]
            cities = []
            for coa in coa_array:
                if coa.city is not None:
                    coa.city.public_opinion = po_value
                    cities.append(coa.city)
            for step in range(0,self.number_steps):
                test.step()
                buf_coa_cost = []
                for ind_unit in inds:
                    buf_coa_cost.append([ind_unit.city.coa.housing_costs + ind_unit.city.coa.hotel_costs])
                coa_costs = np.nansum(buf_coa_cost)
                buf = []
                for coa in coa_array:
                    buf.append([building.health for building in coa.city.azcs])
                bh = np.nanmean(buf)
                buf_ac = []
                buf_health = []
                buf_distress = []
                newcomers = [nc for nc in test.schedule.agents if type(nc) is Newcomer and nc.ls == 'as_ext']
                for nc in newcomers:
                    buf_ac.append(nc.acculturation)
                    buf_health.append(nc.health)
                    buf_distress.append(nc.values.health)
                ac = np.nanmean(buf_ac)
                nc_health = np.nanmean(buf_health)
                nc_distress = np.nanmean(buf_distress)
                ng = np.nanmean([ngo.funds for ngo in ngo])
                ct = np.nanmean([city.public_opinion for city in cities])
                ct_costs = np.nanmean([city.costs for city in cities])
                ct_crime = np.nanmean([city.crime for city in cities])
                staff = np.nanmean([coa.staff for coa in coa_array])
                values = [trial_id, step, po_value, ng, ct, bh, ac, staff, ct_costs, ct_crime, coa_costs, nc_health, nc_distress]
                if all_time_steps==True:
                    toReturn.append(values)
            if all_time_steps == False:
                toReturn.append(values)
            return (toReturn)
        except Exception:
            return None
            
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
            bh = np.nanmean(buf)
            buf = []
            newcomers = [nc for nc in test.schedule.agents if type(nc) is Newcomer and nc.ls == 'as_ext']
            for nc in newcomers:
                buf.append(nc.acculturation)
            ac = np.nanmean(buf)
            ng = np.nanmean([ngo.funds for ngo in ngo])
            ct = np.nanmean([city.public_opinion for city in cities])
            staff = np.nanmean([coa.staff for coa in coa_array])
            values = [trial_number, step, test.include_social_networks, se_value, st_value, c_value, otc_value, ng, ct, bh, ac, staff]
            if all_time_steps==True:
                toReturn.append(values)
        if all_time_steps == False:
            toReturn.append(values)
        return (toReturn)
        
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
            bh = np.nanmean(buf)
            buf = []
            newcomers = [nc for nc in test.schedule.agents if type(nc) is Newcomer and nc.ls == 'as_ext']
            for nc in newcomers:
                buf.append(nc.acculturation)
            ac = np.nanmean(buf)
            ng = np.nanmean([ngo.funds for ngo in ngo])
            ct = np.nanmean([city.public_opinion for city in cities])
            staff = np.nanmean([coa.staff for coa in coa_array])
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


