from model_explorer import ModelExplorer 

test = ModelExplorer(p_num_random_sample_params_to_do=2)
test.explore_all() # to get a complete trace with all time steps for each entity

# to get a trace with all time steps for mean values for each entity
test.explore_summary(exp_all_time_steps=True, filename="summary-exploration-all-time-steps.csv") 

# to get a single line output reflectin the state at the final time step with mean values for each entity
test.explore_summary(exp_all_time_steps=False, filename="summary-exploration-just-final-time-step.csv")

