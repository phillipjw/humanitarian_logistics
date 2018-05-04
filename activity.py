
import mesa
import numpy as np
from mesa import Agent, Model
import organizations
from operator import attrgetter
import statistics

class Action():
    
    def __init__(self,name, agent, v_index):
        
        '''
        generic action class, similar to activity but not of agent type
        '''
        self.name = name
        self.agent = agent            #tie it to a given agent
        self.v_index = v_index          #index of value to be satisfied
        self.counter = 0              #for histogramming purposes
    
    def do(self):
        
        self.agent.values.val_t[self.v_index] += self.agent.values.val_sat[self.v_index]
        self.counter += 1
         
class RequestFunds(Action):
    
    def __init__(self, name, agent, v_index):
        '''
        Request Funds is a self-enhancement action
        it involves petitioning the government for increased funding
        '''
        super().__init__(name, agent, v_index)
        self.name = name
        self.agent = agent            #tie it to a given agent
        self.v_index = v_index          #index of value to be satisfied
        self.effect = self.do
        self.counter = 0              #for histogramming purposes
        self.request_amount = 10000
        
    def satisfaction(self):
        
        self.agent.values.val_t[self.v_index] += self.agent.values.val_sat[self.v_index]
        self.counter += 1
        
    def precondition(self):
        
        return self.agent.shock
    
    def do(self):
        
        #increase budget
        self.agent.budget += self.request_amount
        
        #satisfy values
        self.satisfaction()
        
        
class Consolidate(Action):
    
    def __init__(self, name, agent, v_index):
        
        '''
        Consolidate is a self-enhancement action
        It involves moving newcomers from multiple dispersed AZCs
        into fewer, centralized AZCs
        It frees up available capital for COA
        '''
        
        super().__init__(name, agent, v_index)
        self.name = name
        self.agent = agent            #tie it to a given agent
        self.v_index = v_index          #index of value to be satisfied
        self.effect = self.do
        self.counter = 0              #for histogramming purposes
        
    def satisfaction(self):
        
        self.agent.values.val_t[self.v_index] += self.agent.values.val_sat[self.v_index]
        self.counter += 1
        
    def precondition(self):
        
        ''''
        check if action is feasible in the first place
        by ensuring that azcs's are non-empty
        '''
        
        return not self.agent.shock and sum([azc.occupancy for azc in
                                             self.agent.azcs]) > 0
    
    def do(self):
        
        #this is placeholder and should go outisde the function
        if not self.precondition():
            print('Cannot Consolidate')
            pass
        
        #get all non-empty AZCs
        azcs = [azc for azc in self.agent.model.schedule.agents if
                type(azc) is organizations.AZC and not azc.coa.ta and
                azc.occupancy > 0]

        
        #Order non-empty Azcs by occupancy
        azcs.sort(key = lambda x: x.occupancy)
        
        
        #move occupants to central location
        for current in self.agent.azcs:
            
            #take lowest capacity AZC and move its occupants to highest
            #capacity AZC that can fit them
            
            amount = current.occupancy
            print('amount:', amount)
            print('test:', len(current.occupants))
           
            if current.occupants:
            
                for other_azc in reversed(azcs):
                    difference = other_azc.capacity - other_azc.occupancy

                    while difference > 0 and amount > 0:
                        try:
                            occupant = current.occupants.pop()
                            current.coa.move(occupant, other_azc)
                            amount -= 1
                            difference -= 1
                        except TypeError:
                            print('Typerror,',len(current.occupants))
                        
        #update values
        self.satisfaction()
        
class FlexibleConstruction(Action):
    
    def __init__(self, name, agent, v_index):
        '''
        Flexible construction is that which can serve multiple purposes. It
        will cost more to build, because it must serve other audiences than 
        only AS, but it can be converted
        into local resident social housing when a shock has passed. otc action during shock
        '''
        super().__init__(name, agent, v_index)
        self.name = name
        self.agent = agent            #tie it to a given agent
        self.v_index = v_index          #index of value to be satisfied
        self.effect = self.do
        self.counter = 0              #for histogramming purposes
        self.additional_cost_to_build = 1000
        
    def satisfaction(self):
        
        self.agent.values.val_t[self.v_index] += self.agent.values.val_sat[self.v_index]
        self.counter += 1
        
    def precondition(self):
        
        return self.agent.shock
    
    def do(self):
        
        # build the flexible construction building
        # FlexConstruction class should be fleshed out more. Still not sure exactly how to position things.
        # Using construct function makes sense to me. Does this seem right?
        flex = FlexConstruction(0, self.agent.model, self.agent.city.pos, self.agent, np.random.uniform(0,1)) #instantiate
        self.agent.construct(flex, self.additional_cost_to_build)
        
        #satisfy values
        self.satisfaction()
        
        
class Invest(Action):
    
    def __init__(self, name, agent, v_index):
        
        '''
        Invest is a self-transcendence action
        It involves constructing activity centers in a AZC to fill the needs of 
        newcomers 
        Money is spent from the COA to accomplish this.
        '''
        
        super().__init__(name, agent, v_index)
        self.name = name
        self.agent = agent            #tie it to a given agent
        self.v_index = v_index          #index of value to be satisfied
        self.effect = self.do
        self.counter = 0              #for histogramming purposes
        
    def satisfaction(self):
        
        self.agent.values.val_t[self.v_index] += self.agent.values.val_sat[self.v_index]
        self.counter += 1
        
    def precondition(self):
        
        #check if Balance enough to invest and not shock
        shock = not self.agent.shock
        finances = None
        
        #if no activity center already
        #check if enough funds to build one
        if self.agent.activity_centers:
            finances = self.agent.activity_budget > self.agent.activity_cost
        
        #otherwise, check if enough funds to add an activity
        else:
            finances = self.agent.budget > self.agent.activity_center_cost
        return shock and finances
    
    def do(self):
        
    #During a non-shock period, COA satisfies ST by investing in the quality of life of its
    #residents by constructing an activity center (AC). The AC has a cost significantly less than an
    #entire building, as it may simply be a room in another building. The AC hosts activities, which
    #are period events satisfying a certain criteria of a newcomer. Currently, we just add an activities
    # to aczs that are less than half full and where the ls == as. However, there is functionality in the
    # code to convert empty buildings to ActivityCenter buildings.
        
        max_num_activity_centers = 2
        max_num_activities_per_center = 2 
        num_activity_centers_added = 0       
        for azc in self.agent.azcs:
       

         if (num_activity_centers_added < max_num_activity_centers):
             activities = set([])
             for j in range(max_num_activities_per_center):
                 # only activities the coa can afford are chosen
                 activity = self.choose_needed_activity(azc.coa)
                 activities.add(activity)
                 azc.coa.activity_budget = azc.coa.activity_budget - activity.cost
                
             azc.activities_available = activities
             num_activity_centers_added = num_activity_centers_added + 1
                
        self.satisfaction()
    
    def choose_needed_activity(self, coa, genereate_needed_activity=False, actCost=1000):
        
        coa_values = coa.values
        if genereate_needed_activity:
            needed_se  = 100-coa_values[0]
            needed_st  = 100-coa_values[1]
            needed_c   = 100-coa_values[2]
            needed_otc = 100-coa_values[3]
            # custom/generic activity that is high in cost due to the fact taht it can be ideal in nature
            activity_to_return = Activity(0, self, 5, se=needed_se, st=needed_st, c=needed_c, otc=needed_otc, cost=actCost)
            return activity_to_return
            
        else:
            possible_activities = []
            working_with_coa_activity = WorkingWithCOA(0, self, 5)
            sports_activity = Sports(0, self, 5)
            pre_integration_workshop_activity = PreIntegrationWorkshop(0, self, 5)
            volunteer_with_ngo_activity = VolunteeringWithNGO(0, self, 5, coa.ngo)
            language_course_activity = LanguageCourse(0, self, 5)
            
            list_of_all_activities = [working_with_coa_activity, sports_activity, volunteer_with_ngo_activity,
                                     pre_integration_workshop_activity, language_course_activity]
            for activity in list_of_all_activities:     
                if coa.activity_budget > activity.cost:
                    if (not activity.ngo_required) or (not coa.ngo is None):
                        possible_activities.append(activity)
                
            priority = coa.values.prioritize()
            #find action that corresponds to priority
            for value in priority:
                possible_effects = []
                for index in range(0, len(possible_activities)):
                    activity = possible_activities[index]
                    possible_effects.append(activity.v_sat[value])
                if max(possible_effects) > 0:
                    break;
            
            # get the max value in possible effects
            index_of_activity = possible_effects.index(max(possible_effects))
            activity_to_return =  possible_activities[index_of_activity]
            return activity_to_return
    

class RobustConstruction(Action):
    
    def __init__(self, name, agent, v_index):
        '''
        Robust Construction Robust construction (RC) is that which allows for redundancy. That
        is, Robustness prioritizes multiple smaller units over one large unit in case of maintenance issues. A
        construction decision is first made by identifying the amount of unmet need. Rather than focusing
        on only the cheapest option, RC identifies, from the set of buildings which meet the projected
        need, the largest subset.
        '''
        super().__init__(name, agent, v_index)
        self.name = name
        self.agent = agent            #tie it to a given agent
        self.v_index = v_index          #index of value to be satisfied
        self.effect = self.do
        self.counter = 0              #for histogramming purposes
        self.construction_budget = 1000
        self.maintenance_budget = 1000
        
    def satisfaction(self):
        
        self.agent.values.val_t[self.v_index] += self.agent.values.val_sat[self.v_index]
        self.counter += 1
        
    def precondition(self):
        
        return self.agent.shock
    
    def do(self):
        
        #order azcs in terms of length_of_occupants apply maintenance to each azc until out of funds
        
        #gets a cost per azc from health + occupancy + activities + proximity
        [azc.get_operational_cost() for azc in self.agent.azcs]
        list_of_azcs = sorted([azc for azc in self.agent.azcs], key = attrgetter('operational_cost'))
        if len(list_of_azcs) > 0:
            index = 0
            cur_azc = list_of_azcs[index]
            while self.maintenance_budget >= (100-cur_azc.health):
                cur_azc.health = 100-cur_azc.health
                self.maintenance_budget = self.maintenance_budget - cur_azc.health
                index = index + 1
                cur_azc = list_of_azcs[index]
                
        #still not sure about how to see which buildings reflect which needs
class Segregate(Action):
        
    def __init__(self, name, agent, v_index):
        
        '''
      Segregate is modeled after Vivien Coulier’s description of COA policies to come.
      Essentially COA identifies those AS which are unlikely to achieve status and separates them from
      those who will. The unlikely to achieve status ones are placed in the cheapest to maintain AZC.
        '''
        
        super().__init__(name, agent, v_index)
        self.name = name
        self.agent = agent            #tie it to a given agent
        self.v_index = v_index          #index of value to be satisfied
        self.effect = self.do
        self.counter = 0              #for histogramming purposes
        
    def satisfaction(self):
        
        self.agent.values.val_t[self.v_index] += self.agent.values.val_sat[self.v_index]
        self.counter += 1
        
    def precondition(self):
        
        #check if not shock and check if feasible
        return not self.agent.shock
        
    
    def do(self):
        cheapest_azc_to_maintain = None
        
        #gets a cost per azc from health + occupancy + activities + proximity
        [azc.get_operational_cost() for azc in 
         self.agent.azcs]
        
        cheapest_azc_to_maintain = min([azc for azc in self.agent.azcs], key = attrgetter('operational_cost'))
        
        if cheapest_azc_to_maintain != None and cheapest_azc_to_maintain.pos != None:
            for newcomer in self.agent.newcomers:
                # defining an unlikely new comer as one with a first value = 0
                # and a legal status of edp
                if newcomer.first == 0:
                    if newcomer.ls == "as_ext" and newcomer.second == 0:
                        if (newcomer.pos != None):
                            cheapest_azc_to_maintain.coa.move(newcomer, cheapest_azc_to_maintain)
                        
        self.satisfaction()
        
class Integrate(Action):
        
    def __init__(self, name, agent, v_index):
        
        '''
        COA integrates by setting activity permissions to setting activity permissions to
        all legal statuses. That way all AS can participate in the same activities. It also obliges transfer
        requests and will subsidize travel to participate in activities for AS that live far from activity
        centers.
        '''
        
        super().__init__(name, agent, v_index)
        self.name = name
        self.agent = agent            #tie it to a given agent
        self.v_index = v_index          #index of value to be satisfied
        self.effect = self.do
        self.counter = 0              #for histogramming purposes
        
    def satisfaction(self):
        
        self.agent.values.val_t[self.v_index] += self.agent.values.val_sat[self.v_index]
        self.counter += 1
        
    def precondition(self):
        
        #check if not shock and check if feasible
        return not self.agent.shock
    
    def do(self):
        between_city_travel = True # we will want to parameterize this somehow
        travel_voucher = self.agent.city.cost_of_bus_within_city 
        if not between_city_travel:
            travel_voucher = self.agent.city.cost_of_bus_to_another_city 
        
        for azc in self.agent.azcs:
                 for newcomer in azc.occupants:
                     newcomer.budget = newcomer.budget + travel_voucher
                    
        self.satisfaction()  
        

        

class Activity(Agent):
    
    def __init__(self, unique_id, model, frequency=1, se=0, st=0, c=0, otc=0, cost=0):
       
    
        '''
        An activity is an event which recurs with a particular weekly 
        frequency and satisfies a particular value for the newcomers.
        '''
        super().__init__(unique_id, model)   
        self.frequency = frequency
	
        # SE corresponds to an activity that provides betterment of one’s 
	     # own attributes through either enhancement
        # of already owned resources, corresponding to achievement, or the enhanced control of resource
        # acquisition, corresponding to power
        # ST satisfaction providing an activity where the betterment of
        # another agent’s attributes, as per its component values, benevolence and universalism
        # C, which is an activity providing tradition, conformity and security.
        # OTC is an activity providing stimulation and hedonism
        
        #putting the above together into one array
        self.v_sat = np.array([se,st,c,otc])
        
        self.effect = None
        self.participants =[]
        self.cost = cost        
        self.ngo_required = False        
        
        
class Sports(Activity):
    
    def __init__(self, unique_id, model, frequency):
        
        super().__init__(unique_id, model, frequency)
        
        self.effect = self.satisfaction
        self.frequency = frequency
        
        #satisfies OTC
        self.v_sat = np.array([10,10,10,70])  #staves off decay for se,st,c
        self.cost = 100
    def satisfaction(self, participant):
        
        participant.values.val_t += self.v_sat

class WorkingWithCOA(Activity):
    
    def __init__(self, unique_id, model, frequency):
        
        super().__init__(unique_id, model, frequency)
        
        self.effect = self.satisfaction
        self.frequency = frequency
        
        #satisfies conservation? (should double check with phillip)
        self.v_sat = np.array([10,10,70,10])  #staves off decay for se,st,otc
        self.financial_payout = 10 # also should double check with phillip
        self.cost = 0
    def satisfaction(self, participant):
        
        participant.values.val_t += self.v_sat

class VolunteeringWithNGO(Activity):
    
    def __init__(self, unique_id, model, frequency, ngo):
        
        super().__init__(unique_id, model, frequency)
        
        self.effect = self.satisfaction
        self.frequency = frequency
        
        #satisfies self-transcendence? (should double check with phillip)
        self.v_sat = np.array([10,70,10,10])  #staves off decay for se,c,otc
        self.ngo = ngo
        self.cost = 0
        self.ngo_required = True
    def satisfaction(self, participant):
        if not self.ngo is None:
            participant.values.val_t += self.v_sat

class PreIntegrationWorkshop(Activity):
    
    def __init__(self, unique_id, model, frequency):
        
        super().__init__(unique_id, model, frequency)
        
        self.effect = self.satisfaction
        self.frequency = frequency
        
        #satisfies OTC and SE? (should double check with phillip)
        self.v_sat = np.array([35,10,10,35])  #staves off decay for st,c
        self.cost = 500
    def satisfaction(self, participant):
        participant.values.val_t += self.v_sat

class LanguageCourse(Activity):
    
    def __init__(self, unique_id, model, frequency):
        
        super().__init__(unique_id, model, frequency)
        
        self.effect = self.satisfaction
        self.frequency = frequency
        self.cost = 500
        #satisfies OTC and SE? (should double check with phillip)
        self.v_sat = np.array([35,10,10,35])  #staves off decay for st,c
        
    def satisfaction(self, participant):
        participant.values.val_t += self.v_sat