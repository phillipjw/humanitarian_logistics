from model_explorer import ModelExplorer 

# create model and adjust param
test = ModelExplorer(p_po_uniform=False, p_width=200, p_height=200, p_num_pols=2, p_city_size=20, p_number_steps=500, p_shock_flag =False, p_decision_quality=True, 
                 p_coa_se=55, p_coa_st=65, p_coa_c=45, p_coa_otc=60, p_ngo_se=50, p_ngo_st=55, p_ngo_c=60, p_ngo_otc=60, p_ind_se=50, p_ind_st=55, p_ind_c=60, p_ind_otc=60,
                 p_cultural_wellbeing=True, p_cw_group='A')

test.trace_given_cw()

