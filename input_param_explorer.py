from model_explorer import ModelExplorer 

test = ModelExplorer()
#test.explore_all() # to get a complete trace with all time steps for each entity

# to get a trace with all time steps for mean values for each entity
#test.explore_summary(exp_all_time_steps=True, filename="summary-exploration-all-time-steps.csv") 

# to get a single line output reflectin the state at the final time step with mean values for each entity
cse = [25]
cst = [25]
cc =  [25]
cotc = [25]
        
nse = [25]
nst = [25]
nc =  [25]
notc = [25]
test.sweep_all(exp_all_time_steps=True, coa_se=cse, coa_st=cst, coa_c=cc, coa_otc=cotc, ngo_se=nse, ngo_st=nst, ngo_c=nc, ngo_otc=notc)

