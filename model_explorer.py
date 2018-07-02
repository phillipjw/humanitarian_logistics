import numpy as np
import mesa
from model import HumanitarianLogistics, COA, AZC, Newcomer, City, NGO, IND
import activity
from Values import Values
import random
import csv


class ModelExplorer():

    def __init__(self, p_width=200, p_height=200, p_num_pols=2, p_city_size=20, p_number_steps=500, p_shock_flag =False, p_decision_quality=True):

        self.width = p_width
        self.height = p_height
        self.num_pols = p_num_pols
        self.city_size = p_city_size
        self.number_steps = p_number_steps
        self.shock_flag = p_shock_flag
        self.dq = p_decision_quality
            
            
    def sweep(self, exp_all_time_steps, coa_se, coa_st, coa_c, coa_otc, ngo_se, ngo_st, ngo_c, ngo_otc, ind_se, ind_st, ind_c, ind_otc):
        
        myData = [["trial", "step", "coa_se_value", "coa_st_value", "coa_c_value", "coa_otc_value", "ngo_se_value", "ngo_st_value", "ngo_c_value", "ngo_otc_value", "ind_se_value", "ind_st_value", "ind_c_value", "ind_otc_value", "ngo_funds", "city_po", "building_health", "newcomer_acculturation", "azc_staff", "city_costs", "city_crime", "coa_costs", "newcomer_health", "newcomer_distress"]]
        
        fileprefix = 'sweep-'
        filesuffix = '.csv'
        
        coa_se_part = "coa_se"+str(coa_se[0])+'-'+str(coa_se[len(coa_se)-1])+'-'
        coa_st_part = "coa_st"+str(coa_st[0])+'-'+str(coa_st[len(coa_st)-1])+'-'
        coa_c_part = "coa_c"+str(coa_c[0])+'-'+str(coa_c[len(coa_c)-1])+'-'
        coa_otc_part = "coa_otc"+str(coa_otc[0])+'-'+str(coa_otc[len(coa_otc)-1])+'-'
        
        ngo_se_part = "ngo_se"+str(coa_se[0])+'-'+str(ngo_se[len(ngo_se)-1])+'-'
        ngo_st_part = "ngo_st"+str(coa_st[0])+'-'+str(ngo_st[len(ngo_st)-1])+'-'
        ngo_c_part = "ngo_c"+str(coa_c[0])+'-'+str(ngo_c[len(ngo_c)-1])+'-'
        ngo_otc_part = "ngo_otc"+str(coa_otc[0])+'-'+str(ngo_otc[len(ngo_otc)-1])
        
        ind_se_part = "ind_se"+str(coa_se[0])+'-'+str(ind_se[len(ind_se)-1])+'-'
        ind_st_part = "ind_st"+str(coa_st[0])+'-'+str(ind_st[len(ind_st)-1])+'-'
        ind_c_part = "ind_c"+str(coa_c[0])+'-'+str(ind_c[len(ind_c)-1])+'-'
        ind_otc_part = "ind_otc"+str(coa_otc[0])+'-'+str(ind_otc[len(ind_otc)-1])
        
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
        toReturn = []
        test = HumanitarianLogistics(self.width, self.height, self.num_pols, self.city_size, coa_se_value, coa_st_value, coa_c_value, coa_otc_value)
        test.shock_flag = self.shock_flag
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


