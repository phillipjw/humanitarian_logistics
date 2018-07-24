import numpy as np
import mesa
from model import HumanitarianLogistics, COA, AZC, Newcomer, City, NGO, IND
import activity
from Values import Values
import random
import csv
import traceback

class ModelExplorer():

    def __init__(self, p_width=200, p_height=200, p_num_pols=2, p_city_size=20, p_number_steps=500, p_shock_flag =False, p_decision_quality=True, 
                 p_coa_se=55, p_coa_st=65, p_coa_c=45, p_coa_otc=60, p_ngo_se=45, p_ngo_st=50, p_ngo_c=55, p_ngo_otc=48, p_ind_se=45, p_ind_st=50, p_ind_c=55, p_ind_otc=65,
                 p_cultural_wellbeing=True, p_cw_group='A'):

        self.width = p_width
        self.height = p_height
        self.num_pols = p_num_pols
        self.city_size = p_city_size
        self.number_steps = p_number_steps
        self.shock_flag = p_shock_flag
        self.dq = p_decision_quality
        self.coa_se = p_coa_se
        self.coa_st = p_coa_st
        self.coa_c = p_coa_c
        self.coa_otc = p_coa_otc
        self.ngo_se = p_ngo_se
        self.ngo_st = p_ngo_st
        self.ngo_c = p_ngo_c
        self.ngo_otc = p_ngo_otc
        self.ind_se = p_ind_se
        self.ind_st = p_ind_st
        self.ind_c = p_ind_c
        self.ind_otc = p_ind_otc
        self.cultural_wellbeing = p_cultural_wellbeing
        self.cw_group = p_cw_group
    
    def sweep(self, exp_all_time_steps, coa_se, coa_st, coa_c, coa_otc, ngo_se, ngo_st, ngo_c, ngo_otc, ind_se, ind_st, ind_c, ind_otc):
        
        myData = [["trial", "step", "coa_se_value", "coa_st_value", "coa_c_value", "coa_otc_value", "ngo_se_value", "ngo_st_value", "ngo_c_value", "ngo_otc_value", "ind_se_value", "ind_st_value", "ind_c_value", "ind_otc_value", "ngo_funds", "city_po", "building_health", "newcomer_acculturation", "azc_staff", "city_costs", "city_crime", "coa_costs", "newcomer_health", "newcomer_distress"]]
        
        fileprefix = 'sweep-'
        filesuffix = '.csv'
        
        coa_se_part = "coa_se"+str(coa_se[0])+'-'+str(coa_se[len(coa_se)-1])+'-'
        coa_st_part = "coa_st"+str(coa_st[0])+'-'+str(coa_st[len(coa_st)-1])+'-'
        coa_c_part = "coa_c"+str(coa_c[0])+'-'+str(coa_c[len(coa_c)-1])+'-'
        coa_otc_part = "coa_otc"+str(coa_otc[0])+'-'+str(coa_otc[len(coa_otc)-1])+'-'
        
        ngo_se_part = "ngo_se"+str(ngo_se[0])+'-'+str(ngo_se[len(ngo_se)-1])+'-'
        ngo_st_part = "ngo_st"+str(ngo_st[0])+'-'+str(ngo_st[len(ngo_st)-1])+'-'
        ngo_c_part = "ngo_c"+str(ngo_c[0])+'-'+str(ngo_c[len(ngo_c)-1])+'-'
        ngo_otc_part = "ngo_otc"+str(ngo_otc[0])+'-'+str(ngo_otc[len(ngo_otc)-1])
        
        ind_se_part = "ind_se"+str(ind_se[0])+'-'+str(ind_se[len(ind_se)-1])+'-'
        ind_st_part = "ind_st"+str(ind_st[0])+'-'+str(ind_st[len(ind_st)-1])+'-'
        ind_c_part = "ind_c"+str(ind_c[0])+'-'+str(ind_c[len(ind_c)-1])+'-'
        ind_otc_part = "ind_otc"+str(ind_otc[0])+'-'+str(ind_otc[len(ind_otc)-1])
        
        filename = fileprefix + coa_se_part + coa_st_part + coa_c_part + coa_otc_part 
        filename = filename +   ngo_se_part + ngo_st_part + ngo_c_part + ngo_otc_part 
        filename = filename +  ind_se_part + ind_st_part + ind_c_part + ind_otc_part + filesuffix
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
                                        for ise in ind_se:
                                            for ist in ind_st:
                                                for ic in ind_c:
                                                    for iotc in ind_otc:
                                                        params = [cse, cst, cc, cotc, nse, nst, nc, notc, ise, ist, ic, iotc]
                                                        print("----------------------------------------------------------------------------------------")
                                                        print(params)
                                                        print("----------------------------------------------------------------------------------------")
                                                        sim_values = self.run_sweep_trial(coa_se_value = cse, coa_st_value= cst, coa_c_value = cc, coa_otc_value = cotc,
                                                                                              ngo_se_value = nse, ngo_st_value= nst, ngo_c_value = nc, ngo_otc_value = notc,
                                                                                              ind_se_value = ise, ind_st_value=ist, ind_c_value=ic, ind_otc_value=iotc,
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
                                                        if sim_values is None:
                                                            print("Exception thrown during simulation run with: "+str(params))
    
    def run_sweep_trial(self, coa_se_value, coa_st_value, coa_c_value, coa_otc_value, ngo_se_value, ngo_st_value, ngo_c_value, ngo_otc_value, 
                           ind_se_value, ind_st_value, ind_c_value, ind_otc_value, trial_id, all_time_steps):
        try:
            toReturn = []
            test = HumanitarianLogistics(self.width, self.height, self.num_pols, self.city_size, coa_se_value, coa_st_value, coa_c_value, coa_otc_value)
            test.shock_flag = self.shock_flag
            test.dq = self.dq
            test.include_social_networks = False
            ngo = [x for x in test.schedule.agents if type(x) is NGO]
            for unit in ngo:
                unit.values = Values(10, ngo_se_value,ngo_st_value,ngo_c_value,ngo_otc_value, unit)
            coa_array = [coa for coa in test.schedule.agents if type(coa) is COA and coa.city.modality == 'AZC']
            
            inds = [ind for ind in test.schedule.agents if type(ind) is IND]
            for unit in inds:
                unit.values = Values(10, ind_se_value,ind_st_value,ind_c_value,ind_otc_value, unit)
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
                    for building in coa.city.azcs:
                        if (np.isnan(building.health)==False):
                            buf.append(building.health)
                bh = np.mean(buf)
                #bh = np.nanmean(buf)
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
                values = [trial_id, step, coa_se_value, coa_st_value, coa_c_value, coa_otc_value, ngo_se_value, ngo_st_value, ngo_c_value, ngo_otc_value, ind_se_value, ind_st_value, ind_c_value, ind_otc_value, ng, ct, bh, ac, staff, ct_costs, ct_crime, coa_costs, nc_health, nc_distress]
                if all_time_steps==True:
                    toReturn.append(values)
            if all_time_steps == False:
                toReturn.append(values)
            return (toReturn)
        except Exception:
            return None
    
    def sweep_exp_1(self, coa_type):
        
        ngo_se = [10]
        ngo_st = [35]
        ngo_c =  [40]
        ngo_otc = [60]
        
        ise = 50
        ist = 51
        ic = 49
        
        if coa_type == 1:
            coa_se = [70]
            coa_st = [75]
            coa_c = [35]
            coa_otc = [50]
        if coa_type == 2:
            coa_se = [35]
            coa_st = [70]
            coa_c = [75]
            coa_otc = [50]
        if coa_type == 3:
            coa_se = [35]
            coa_st = [50]
            coa_c = [70]
            coa_otc = [75]
        if coa_type == 4:
            coa_se = [75]
            coa_st = [30]
            coa_c = [50]
            coa_otc = [70]
            
        myData = [["trial", "step", "coa_se_value", "coa_st_value", "coa_c_value", "coa_otc_value", "ngo_se_value", "ngo_st_value", "ngo_c_value", "ngo_otc_value", "ind_se_value", "ind_st_value", "ind_c_value", "ind_otc_value", "budget_freq", "ngo_funds", "ngo_cfr", "ngo_cme", "city_po", "building_health", "newcomer_acculturation", "azc_staff", "city_costs", "city_crime", "coa_costs", "newcomer_health", "newcomer_distress", "ind_staff", "wait_time"]]
        
        fileprefix = 'sweep-exp1-'+str(coa_type)
        filesuffix = '.csv'
        
        filename = fileprefix + filesuffix
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
                                        for k in range(0, 6):
                                            if k==0:
                                                iotc = 70
                                                budgetf = 365
                                            if k==1:
                                                iotc = 70
                                                budgetf = 230
                                            if k==2:
                                                iotc = 70
                                                budgetf = 60
                                            if k==3:
                                                iotc = 30
                                                budgetf = 365
                                            if k==4:
                                               iotc = 30
                                               budgetf = 230
                                            if k==5:
                                               iotc = 30
                                               budgetf = 60
                                            print("----------------------------------------------------------------------------------------")
                                            params = [cse, cst, cc, cotc, nse, nst, nc, notc, ise, ist, ic, iotc]
                                            print(params)
                                            print("----------------------------------------------------------------------------------------")
                                            sim_values = self.run_sweep_trial_exp_1(coa_se_value = cse, coa_st_value= cst, coa_c_value = cc, coa_otc_value = cotc,
                                                                              ngo_se_value = nse, ngo_st_value= nst, ngo_c_value = nc, ngo_otc_value = notc,
                                                                              ind_se_value = ise, ind_st_value=ist, ind_c_value=ic, ind_otc_value=iotc,
                                                                              trial_id = i, all_time_steps = True, budget=budgetf)
                                            i = i + 1
                                            if sim_values is not None:
                                                for x in range(0, len(sim_values)):
                                                    valuesToAdd = sim_values[x]
                                                    if valuesToAdd is not None:
                                                        myFile = open(filename, 'a')
                                                        with myFile:
                                                            writer = csv.writer(myFile)
                                                            writer.writerows([valuesToAdd])
                                            if sim_values is None:
                                                print("Exception thrown during simulation run with: "+str(params))
                    
    def run_sweep_trial_exp_1(self, coa_se_value, coa_st_value, coa_c_value, coa_otc_value, ngo_se_value, ngo_st_value, ngo_c_value, ngo_otc_value, 
                           ind_se_value, ind_st_value, ind_c_value, ind_otc_value, trial_id, all_time_steps, budget):
        try:
            toReturn = []
            test = HumanitarianLogistics(False, self.width, self.height, self.num_pols, self.city_size, coa_se_value, coa_st_value, coa_c_value, coa_otc_value)
            test.shock_flag = self.shock_flag
            test.dq = self.dq
            test.include_social_networks = False
            ngo = [x for x in test.schedule.agents if type(x) is NGO]
            for unit in ngo:
                unit.values = Values(10, ngo_se_value,ngo_st_value,ngo_c_value,ngo_otc_value, unit)
            coa_array = [coa for coa in test.schedule.agents if type(coa) is COA and coa.city.modality == 'AZC']
            
            inds = [ind for ind in test.schedule.agents if type(ind) is IND]
            for unit in inds:
                unit.values = Values(10, ind_se_value,ind_st_value,ind_c_value,ind_otc_value, unit)
                unit.budget_frequency = budget
            cities = []
            for coa in coa_array:
                if coa.city is not None:
                    cities.append(coa.city)
            for step in range(0,self.number_steps):
                test.step()
                buf_coa_cost = []
                buf_ind_staff = []
                for ind_unit in inds:
                    buf_coa_cost.append([ind_unit.city.coa.housing_costs + ind_unit.city.coa.hotel_costs])
                    buf_ind_staff.append(ind_unit.staff)
                coa_costs = np.nansum(buf_coa_cost)
                ind_staff = np.nanmean(buf_ind_staff)
                buf = []
                for coa in coa_array:
                    for building in coa.city.azcs:
                        if (np.isnan(building.health)==False):
                            buf.append(building.health)
                bh = np.mean(buf)
                #bh = np.nanmean(buf)
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
                ngo_cfr = np.nanmean([ngo.cumulative_funds_raised for ngo in ngo])
                ngo_cme = np.nanmean([ngo.cumulative_marketing_expenditures for ngo in ngo])
                ct = np.nanmean([city.public_opinion for city in cities])
                ct_costs = np.nanmean([city.costs for city in cities])
                ct_crime = np.nanmean([city.crime for city in cities])
                staff = np.nanmean([coa.staff for coa in coa_array])
                temp = []
                temp.append(test.wait_times)
                wt = np.nanmean(temp[0])
                values = [trial_id, step, coa_se_value, coa_st_value, coa_c_value, coa_otc_value, ngo_se_value, ngo_st_value, ngo_c_value, ngo_otc_value, ind_se_value, ind_st_value, ind_c_value, ind_otc_value, budget, ng, ngo_cfr, ngo_cme, ct, bh, ac, staff, ct_costs, ct_crime, coa_costs, nc_health, nc_distress, ind_staff, wt]
                if all_time_steps==True:
                    toReturn.append(values)
            if all_time_steps == False:
                toReturn.append(values)
            return (toReturn)
        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return None
            
    def sweep_exp_2(self, org_type):
        
        coa_se = [55]
        coa_st = [65]
        coa_c = [45]
        coa_otc = [60]
        
        ngo_se = [10]
        ngo_st = [35]
        ngo_c =  [40]
        ngo_otc = [60]
        
        ind_se = [52]
        ind_st = [45]
        ind_c = [49]
        ind_otc = [70]
        
        if org_type == 1:
            coa_se = [20, 40, 60, 80]
            coa_st = [20, 40, 60, 80]
            coa_c = [20, 40, 60, 80]
            coa_otc = [20, 40, 60, 80]
        
        if org_type == 2:
            ngo_se = [20, 40, 60, 80]
            ngo_st = [20, 40, 60, 80]
            ngo_c = [20, 40, 60, 80]
            ngo_otc = [20, 40, 60, 80]
        
        if org_type == 3:
            ind_se = [20, 40, 60, 80]
            ind_st = [20, 40, 60, 80]
            ind_c = [20, 40, 60, 80]
            ind_otc =[20, 40, 60, 80]
        
            
        myData = [["trial", "step", "coa_se_value", "coa_st_value", "coa_c_value", "coa_otc_value", "ngo_se_value", "ngo_st_value", "ngo_c_value", "ngo_otc_value", "ind_se_value", "ind_st_value", "ind_c_value", "ind_otc_value", "ind_staff", "ngo_funds", "ngo_acts", "ngo_cfr", "ngo_cme", "city_po", "building_health", "newcomer_acculturation", "azc_staff", "city_costs", "city_crime", "coa_costs", "newcomer_health", "newcomer_distress", "fp", "fn", "wait_time", "prct_segregated", "segregated_acc", "segregated_costs", "segregated_crime", "segregated_health", "segregated_wellbeing", "segregated_buiding_health", "segregated_coa_costs", "non_segregated_coa_costs", "non_seg_ct_crime", "non_seg_building_health", "non_seg_acc", "non_seg_costs","non_seg_health", "non_seg_wellbeing"]]
        
        fileprefix = 'sweep-exp2.demo.-'+str(org_type)
        filesuffix = '.csv'
        
        filename = fileprefix + filesuffix
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
                                        for ise in ind_se:
                                            for ist in ind_st:
                                                for ic in ind_c:
                                                    for iotc in ind_otc:
                                                        params = [cse, cst, cc, cotc, nse, nst, nc, notc, ise, ist, ic, iotc]
                                                        print("----------------------------------------------------------------------------------------")
                                                        print(params)
                                                        print("----------------------------------------------------------------------------------------")
                                                        sim_values = self.run_sweep_trial_exp_2(coa_se_value = cse, coa_st_value= cst, coa_c_value = cc, coa_otc_value = cotc,
                                                                                              ngo_se_value = nse, ngo_st_value= nst, ngo_c_value = nc, ngo_otc_value = notc,
                                                                                              ind_se_value = ise, ind_st_value=ist, ind_c_value=ic, ind_otc_value=iotc,
                                                                                              trial_id = i, all_time_steps = True, org=org_type)
                                                        i = i + 1
                                                        if sim_values is not None:
                                                            for x in range(0, len(sim_values)):
                                                                valuesToAdd = sim_values[x]
                                                                if valuesToAdd is not None:
                                                                    myFile = open(filename, 'a')
                                                                    with myFile:
                                                                        writer = csv.writer(myFile)
                                                                        writer.writerows([valuesToAdd])
                                                        if sim_values is None:
                                                            print("Exception thrown during simulation run with: "+str(params))


    def run_sweep_trial_exp_2(self, coa_se_value, coa_st_value, coa_c_value, coa_otc_value, ngo_se_value, ngo_st_value, ngo_c_value, ngo_otc_value, 
                           ind_se_value, ind_st_value, ind_c_value, ind_otc_value, trial_id, all_time_steps, org):
        try:
            toReturn = []
            test = None
            if org == 1:
                test = HumanitarianLogistics(False, self.width, self.height, self.num_pols, self.city_size, coa_se_value, coa_st_value, coa_c_value, coa_otc_value)
            else:
                test = HumanitarianLogistics(True, self.width, self.height, self.num_pols, self.city_size, coa_se_value, coa_st_value, coa_c_value, coa_otc_value)
            test.shock_flag = self.shock_flag
            test.dq = self.dq
            test.include_social_networks = False
            ngo = [x for x in test.schedule.agents if type(x) is NGO]
            for unit in ngo:
                unit.values = Values(10, ngo_se_value,ngo_st_value,ngo_c_value,ngo_otc_value, unit)
            coa_array = [coa for coa in test.schedule.agents if type(coa) is COA and coa.city.modality == 'AZC']
            
            inds = [ind for ind in test.schedule.agents if type(ind) is IND]
            for unit in inds:
                unit.values = Values(10, ind_se_value,ind_st_value,ind_c_value,ind_otc_value, unit)
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
                    for building in coa.city.azcs:
                        if (np.isnan(building.health)==False):
                                buf.append(building.health)
                bh = np.mean(buf)
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
                ind_staff = np.nanmean([ind.staff for ind in inds])
                fp = test.confusionMatrix['FP']
                fn = test.confusionMatrix['FN']
                wait_times = np.nanmean(test.wait_times)
                pct_segregated = len([nc for nc in newcomers if nc.segregated])/(len(newcomers)+1)
                
                segregated_costs = np.nanmean([nc.loc.city.costs for nc in newcomers if nc.segregated])
                segregated_buiding_health = np.nanmean([nc.loc.health for nc in newcomers if nc.segregated])
                segregated_coa_costs = np.nanmean([nc.loc.coa.net_costs for nc in newcomers if nc.segregated])
                segregated_crime = np.nanmean([nc.loc.city.crime for nc in newcomers if nc.segregated])
                segregated_health = np.nanmean([nc.health for nc in newcomers if nc.segregated])
                segregated_wellbeing = np.nanmean([nc.values.health for nc in newcomers if nc.segregated])
                segregated_acc = np.nanmean([nc.acculturation for nc in newcomers if nc.segregated])
                non_seg_costs = np.nanmean([nc.loc.city.costs for nc in newcomers if not nc.segregated])
                non_seg_crime = np.nanmean([nc.loc.city.crime for nc in newcomers if not nc.segregated])
                non_seg_health = np.nanmean([nc.health for nc in newcomers if not nc.segregated])
                non_seg_wellbeing = np.nanmean([nc.values.health for nc in newcomers if not nc.segregated])
                non_seg_acc = np.nanmean([nc.acculturation for nc in newcomers if not nc.segregated])
                non_seg_building_health = np.nanmean([nc.loc.health for nc in newcomers if not nc.segregated])
                non_seg_coa_costs = np.nanmean([nc.loc.coa.net_costs for nc in newcomers if not nc.segregated])               
                ngo_activities = np.nanmean([ngo.get_num_sessions() for ngo in ngo])
                ngo_cumu_funds = np.nanmean([ngo.cumulative_funds_raised for ngo in ngo])
                ngo_cumu_marketing = np.nanmean([ngo.cumulative_marketing_expenditures for ngo in ngo])
                values = [trial_id, step, coa_se_value, coa_st_value, coa_c_value, coa_otc_value, ngo_se_value, ngo_st_value, ngo_c_value, ngo_otc_value, ind_se_value, ind_st_value, ind_c_value, ind_otc_value, ind_staff, ng,ngo_activities,ngo_cumu_funds,ngo_cumu_marketing, ct, bh, ac, staff, ct_costs, ct_crime, coa_costs, nc_health, nc_distress, fp, fn, wait_times, pct_segregated, segregated_acc, segregated_costs,segregated_crime, segregated_health, segregated_wellbeing, segregated_buiding_health,segregated_coa_costs, non_seg_coa_costs, non_seg_crime, non_seg_building_health, non_seg_acc, non_seg_costs, non_seg_health, non_seg_wellbeing]                
                if all_time_steps==True:
                    toReturn.append(values)
            if all_time_steps == False:
                toReturn.append(values)
            return (toReturn)
        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return None
            
    def sweep_exp_3(self):
        
        cse = 55
        cst = 65
        cc = 45
        cotc = 60
        
        nse = 10
        nst = 35
        nc =  40
        notc = 60
        
        ise = 52
        ist = 45
        ic = 49
        iotc = 70
        
        pos = [-99, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            
        myData = [["trial", "step", "coa_se_value", "coa_st_value", "coa_c_value", "coa_otc_value", "ngo_se_value", "ngo_st_value", "ngo_c_value", "ngo_otc_value", "ind_se_value", "ind_st_value", "ind_c_value", "ind_otc_value", "po_value", "ngo_funds", "ngo_cfr", "ngo_cme", "city_po", "building_health", "newcomer_acculturation", "azc_staff", "city_costs", "city_crime", "coa_costs", "newcomer_health", "newcomer_distress"]]
        
        fileprefix = 'sweep-exp-3'
        filesuffix = '.csv'
        
        filename = fileprefix + filesuffix
        myFile = open(filename, 'w')
        with myFile:
            writer = csv.writer(myFile)
            writer.writerows(myData)
        
        i = 0
        for po in pos:
            print("----------------------------------------------------------------------------------------")
            print(po)
            print("----------------------------------------------------------------------------------------")
            sim_values = self.run_sweep_trial_exp_3(coa_se_value = cse, coa_st_value= cst, coa_c_value = cc, coa_otc_value = cotc,
                                                    ngo_se_value = nse, ngo_st_value= nst, ngo_c_value = nc, ngo_otc_value = notc,
                                                    ind_se_value = ise, ind_st_value=ist, ind_c_value=ic, ind_otc_value=iotc,
                                                    trial_id = i, all_time_steps = True, po_value=po)
            i = i + 1
            if sim_values is not None:
                for x in range(0, len(sim_values)):
                    valuesToAdd = sim_values[x]
                    if valuesToAdd is not None:
                        myFile = open(filename, 'a')
                        with myFile:
                            writer = csv.writer(myFile)
                            writer.writerows([valuesToAdd])
            if sim_values is None:
                print("Exception thrown during simulation run with: "+str(po))
    
    def run_sweep_trial_exp_3(self, coa_se_value, coa_st_value, coa_c_value, coa_otc_value, ngo_se_value, ngo_st_value, ngo_c_value, ngo_otc_value, 
                           ind_se_value, ind_st_value, ind_c_value, ind_otc_value, trial_id, all_time_steps, po_value):
        try:
            toReturn = []
            test = HumanitarianLogistics(False, self.width, self.height, self.num_pols, self.city_size, coa_se_value, coa_st_value, coa_c_value, coa_otc_value)
            test.shock_flag = self.shock_flag
            test.dq = self.dq
            test.include_social_networks = False
            ngo = [x for x in test.schedule.agents if type(x) is NGO]
            for unit in ngo:
                unit.values = Values(10, ngo_se_value,ngo_st_value,ngo_c_value,ngo_otc_value, unit)
            coa_array = [coa for coa in test.schedule.agents if type(coa) is COA and coa.city.modality == 'AZC']
            
            inds = [ind for ind in test.schedule.agents if type(ind) is IND]
            for unit in inds:
                unit.values = Values(10, ind_se_value,ind_st_value,ind_c_value,ind_otc_value, unit)
            azcs = [azc for azc in test.schedule.agents if type(azc) is AZC]
            for b in azcs:
                if po_value == -99:
                    b.city.ngo.funds = 0
                    b.funds = 0
                    b.city.ngo.testing = False
                    copy = set([])
                    for act in b.activity_center.activities_available:
                        if not (act.name == 'Football' or act.name == 'Volunteer'):
                            copy.add(act)
                    b.activity_center.activities_available = copy
            cities = []
            for coa in coa_array:
                if coa.city is not None:
                    if po_value != -99:
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
                    for building in coa.city.azcs:
                        if (np.isnan(building.health)==False):
                            buf.append(building.health)
                bh = np.mean(buf)
                #bh = np.nanmean(buf)
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
                ngo_cfr = np.nanmean([ngo.cumulative_funds_raised for ngo in ngo])
                ngo_cme = np.nanmean([ngo.cumulative_marketing_expenditures for ngo in ngo])
                ct = np.nanmean([city.public_opinion for city in cities])
                ct_costs = np.nanmean([city.costs for city in cities])
                ct_crime = np.nanmean([city.crime for city in cities])
                staff = np.nanmean([coa.staff for coa in coa_array])
                values = [trial_id, step, coa_se_value, coa_st_value, coa_c_value, coa_otc_value, ngo_se_value, ngo_st_value, ngo_c_value, ngo_otc_value, ind_se_value, ind_st_value, ind_c_value, ind_otc_value, po_value, ng, ngo_cfr, ngo_cme, ct, bh, ac, staff, ct_costs, ct_crime, coa_costs, nc_health, nc_distress]
                if all_time_steps==True:
                    toReturn.append(values)
            if all_time_steps == False:
                toReturn.append(values)
            return (toReturn)
        except Exception as e:
            print(str(e))
            return None

    def trace_given_cw(self):
        
        
        myData = [["step", "coa_se_value", "coa_st_value", "coa_c_value", "coa_otc_value", "ngo_se_value", "ngo_st_value", "ngo_c_value", "ngo_otc_value", "ind_se_value", "ind_st_value", "ind_c_value", "ind_otc_value", "ngo_funds", "ngo_cfr", "ngo_cme", "city_po", "building_health", "newcomer_acculturation", "azc_staff", "city_costs", "city_crime", "coa_costs", "newcomer_health", "newcomer_distress", "cw_group"]]
        
        fileprefix = 'trace-of-cw-'
        filesuffix = str(self.cw_group) + '.csv'
        
        filename = fileprefix + filesuffix
        myFile = open(filename, 'w')
        with myFile:
            writer = csv.writer(myFile)
            writer.writerows(myData)
        
        sim_values = self.trace(all_time_steps=True)
        if sim_values is not None:
            for x in range(0, len(sim_values)):
                valuesToAdd = sim_values[x]
                if valuesToAdd is not None:
                    myFile = open(filename, 'a')
                    with myFile:
                        writer = csv.writer(myFile)
                        writer.writerows([valuesToAdd])
        if sim_values is None:
            print("Exception thrown during simulation run.")
    
    def trace(self, all_time_steps):
        toReturn = []
        test = HumanitarianLogistics(False, self.width, self.height, self.num_pols, self.city_size, self.coa_se, self.coa_st, self.coa_c, self.coa_otc,
                                     self.ngo_se, self.ngo_st, self.ngo_c, self.ngo_otc, self.ind_se, self.ind_st, self.ind_c, self.ind_otc)
        test.shock_flag = self.shock_flag
        test.dq = self.dq
        test.include_social_networks = False
        test.cultural_wellbeing = self.cultural_wellbeing
        test.cw_group = self.cw_group
            
        ngo = [x for x in test.schedule.agents if type(x) is NGO]
        coa_array = [coa for coa in test.schedule.agents if type(coa) is COA and coa.city.modality == 'AZC']
            
        inds = [ind for ind in test.schedule.agents if type(ind) is IND]
        azcs = [azc for azc in test.schedule.agents if type(azc) is AZC]
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
                for building in coa.city.azcs:
                    if (np.isnan(building.health)==False):
                        buf.append(building.health)
            bh = np.mean(buf)
            #bh = np.nanmean(buf)
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
            ngo_cfr = np.nanmean([ngo.cumulative_funds_raised for ngo in ngo])
            ngo_cme = np.nanmean([ngo.cumulative_marketing_expenditures for ngo in ngo])
            ct = np.nanmean([city.public_opinion for city in cities])
            ct_costs = np.nanmean([city.costs for city in cities])
            ct_crime = np.nanmean([city.crime for city in cities])
            staff = np.nanmean([coa.staff for coa in coa_array])
            values = [step, self.coa_se, self.coa_st, self.coa_c, self.coa_otc, self.ngo_se, self.ngo_st, self.ngo_c, self.ngo_otc, self.ind_se, self.ind_st, self.ind_c, self.ind_otc, ng, ngo_cfr, ngo_cme, ct, bh, ac, staff, ct_costs, ct_crime, coa_costs, nc_health, nc_distress, self.cw_group]
            if all_time_steps==True:
                toReturn.append(values)
        if all_time_steps == False:
            toReturn.append(values)
        return (toReturn)