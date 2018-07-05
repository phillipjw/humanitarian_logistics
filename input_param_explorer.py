from model_explorer import ModelExplorer 

# create model and adjust params
test = ModelExplorer(p_po_uniform = True, p_width=200, p_height=200, p_num_pols=2, p_city_size=20, p_number_steps=400, p_shock_flag =False, p_decision_quality=True)

# fill in coa value search space
cse = range(20,100,15)
cst = range(20,100,15)
cc =  range(20,100,15)
cotc = range(20,100,15)

# fil in ngo value search space        
nse = [45]
nst = [50]
nc =  [55]
notc = [48]


# fill in ind value search space        
ise = [45]
ist = [50]
ic =  [55]
iotc = [65]

# run specified sweep - file name describing sweep is auto-generated.
# exp_all_time_steps True means record values for every time step
# exp_all_time_steps False means only record values for final time step
test.sweep(exp_all_time_steps=True, coa_se=cse, coa_st=cst, coa_c=cc, coa_otc=cotc, 
                                    ngo_se=nse, ngo_st=nst, ngo_c=nc, ngo_otc=notc,
                                    ind_se=ise, ind_st=ist, ind_c=ic, ind_otc=iotc)

