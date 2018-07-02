from model_explorer import ModelExplorer 

# create model and adjust params
test = ModelExplorer(p_width=200, p_height=200, p_num_pols=2, p_city_size=20, p_number_steps=500, p_shock_flag =False, p_decision_quality=True)

# fill in coa value search space
cse = [25]
cst = [25]
cc =  [25]
cotc = [25]

# fil in ngo value search space        
nse = [25]
nst = [25]
nc =  [25]
notc = [25]


# fill in ind value search space        
ise = [25]
ist = [25]
ic =  [25]
iotc = [25]

# run specified sweep - file name describing sweep is auto-generated.
# exp_all_time_steps True means record values for every time step
# exp_all_time_steps False means only record values for final time step
test.sweep(exp_all_time_steps=True, coa_se=cse, coa_st=cst, coa_c=cc, coa_otc=cotc, 
                                    ngo_se=nse, ngo_st=nst, ngo_c=nc, ngo_otc=notc,
                                    ind_se=ise, ind_st=ist, ind_c=ic, ind_otc=iotc)

