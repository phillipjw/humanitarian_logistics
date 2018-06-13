import numpy as np
import mesa
from model import HumanitarianLogistics, COA, AZC, Newcomer, City, NGO
import activity
from Values import Values
import numpy as np

#initial config
width = 200
height = 200
num_pols = 2
city_size = 20
number_steps = 100

se_min = 1
se_max = 100

st_min = 1
st_max = 100

c_min=1
c_max = 100

otc_min = 1
otc_max = 100

num_random_sample_params_to_do = 10

for iter in range(0,num_random_sample_params_to_do):
    se_value = np.random.randint(low=se_min, high=se_max)
    st_value = np.random.randint(low=st_min, high=st_max)
    c_value = np.random.randint(low=c_min, high=c_max)
    otc_value = np.random.randint(low=otc_min, high=otc_max)
    try:
        test = HumanitarianLogistics(width, height, num_pols, city_size, se_value, st_value, c_value, otc_value)
    except Exception:
        continue
    test.include_social_networks = True
    cities = [x for x in test.schedule.agents if type(x) is City]
    NGO = [x for x in test.schedule.agents if type(x) is NGO]
    coa_array = [coa for coa in test.schedule.agents if type(coa) is COA and coa.city.modality == 'AZC']
    azc_array = [azc for azc in test.schedule.agents if type(azc) is AZC and azc.modality == 'AZC' and azc.city.ngo == None]
    for step in range(0,number_steps):
        buf = []
        for coa in coa_array:
            buf.append([building.health for building in coa.city.azcs])
        bh = np.mean(buf)
        buf = []
        for x in azc_array:
                [buf.append(nc.acculturation) for nc in x.occupants if
                           nc.ls == 'as_ext']
        ac = np.mean(buf)
        ng = np.mean([x.funds for x in NGO])
        ct = np.mean([x.public_opinion for x in cities])
        staff = np.mean([coa.staff for coa in coa_array])
        test.step()
    values = [se_value, st_value, c_value, otc_value, ng, ct, bh, ac, staff]
    print(values)    
