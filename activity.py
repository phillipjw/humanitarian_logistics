import mesa
import numpy as np
from mesa import Agent, Model
import organizations
from operator import attrgetter


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
        
class Prioritize(Action):
    '''
    An action to re-allocate resources to best meet the needs of Newcomers
    Value: OTCDO
    '''
    
    def __init__(self, name, agent, v_index):
        
        super().__init__(name, agent, v_index)
        self.counter = 0
    def precondition(self):
        '''
        There's a minimum number of sessions for this to be feasible        
        '''
        return self.agent.get_num_sessions() > 2
    
    def do(self):
        
        '''
        Function removes sessions where funding is over allocated
        adding them to either NGO funds or activities where funding is under allocated        
        '''
        super().do()
        
        
        #gather data re: how NGO allocates its funds        
        funding_allocation = np.zeros(4)
        #distribution of values p activities
        for act in self.agent.activities:
            for day in act.frequency:
                funding_allocation[act.v_index] += 1
            
        f_sum = np.sum(funding_allocation)
        funding_allocation /= f_sum
        
        freed_up_capital = 0
        non_empty_funds = np.where(funding_allocation> 0)[0]
        
        health = np.zeros(4)
        #Gather data regarding distress of those addressed values
        for nc in self.agent.city.coa.get_residents(False):
            nc_lack = nc.values.v_tau - nc.values.val_t
            for nef in non_empty_funds:
                health[nef] += nc_lack[nef]
        health /= sum(health)
                
        #first remove sessions where funding is over allocated
        diff = np.zeros(4)
        for nef in non_empty_funds:
            
            diff[nef] = health[nef] - funding_allocation[nef]

            if diff[nef] > 1/f_sum:
                
                #translates difference into number of session terms
                ALOT = 1e6
                try:
                	diff_in_sessions = int(np.floor(diff[nef]*f_sum))
                except Exception:
                	diff_in_sessions = ALOT
                act = self.agent.get_activity(nef)
                #only remove if more than 2 sessions in act frequency
                if diff_in_sessions >= 2 and len(act.frequency) >= 2:
                    for session in range(min(len(act.frequency)-1,
                                             diff_in_sessions-1)):
                        freed_up_capital += 1
                        self.agent.remove_session(act)
        
        #translate freed up capital into cost of session terms
        freed_up_capital /= self.agent.cost_per_activity
        
        #isolate under allocation of funding
        diff[diff <0] = 0
        #transforms into distribution of under allocation
        diff /= sum(diff)

        #adds sessions where funding is under allocated
        for value in diff:
            if value*freed_up_capital >= 1:
                act = self.agent.get_activity(np.where(diff == value)[0][0])
                for i in range(int(np.floor(value*freed_up_capital))):
                    if self.agent.session_possible(act):
                        self.agent.add_session(act)
                    else:
                        self.agent.funds += self.agent.cost_per_activity
            else:
                self.agent.funds += value*freed_up_capital
                        
                    
                
            
            
        
        
        
        
        
        
      
        
        
    
        
class Fundraise(Action):
    '''
    An action to convert public opinion into usable funds
    '''
    
    def __init__(self, name, agent, v_index):
        
        super().__init__(name, agent, v_index)
        self.counter = 0
    def precondition(self):
        return True
    
    def do(self):
        super().do()
        
        campaign_cost = self.agent.campaign
        activity_cost = 0
        capital = self.agent.funds + campaign_cost + activity_cost
        
        
        if self.agent.activities:
            for activity in self.agent.activities:
                for day in activity.frequency:
                    activity_cost += self.agent.cost_per_activity
                    
                    
        if capital < self.agent.city.public_opinion:
            self.agent.cumulative_funds_raised += (1 - self.agent.funds) * self.agent.city.public_opinion
            self.agent.funds += (1 - self.agent.funds) * self.agent.city.public_opinion
            
        else: 
            
            #if have existing activities, shed them
            if self.agent.activities:
                difference = self.agent.city.public_opinion - capital
            
                while difference > 0:
                    self.agent.get_avg_attendance()
                    mini = np.inf
                
                    for activity in self.agent.activities:
                        for day in activity.frequency:
                            if self.agent.activity_attendance[activity.name][day] < mini:
                                mini = self.agent.activity_attendance[activity.name][day]
                                worst, when = activity, day
                    
                    #remove min
                    try:
                        if len(worst.frequency) == 1:
                            #if only one session p week, remove the whole activity
                            self.agent.activities.remove(worst)
                            self.agent.activity_attendance.pop(worst.name)
                            self.agent.activity_records.pop(worst.name)
                        else:
                            #otherwise just remove one session. 
                            self.agent.activity_attendance[worst.name].pop(when)
                            self.agent.activity_records[worst.name].pop(when)
                            #increase funds
                    except Exception:
                        print("UnboundLocalError: local variable worst referenced before assignment")
                        
                    self.agent.funds += self.agent.cost_per_activity
                    difference -= self.agent.cost_per_activity
            #Otherwise, cancel the marketing campaign
            else: 
                self.agent.funds += self.agent.campaign
                self.agent.city.public_opinion -= self.agent.campaign
                self.agent.campaign = 0
            
            

class marketingCampaign(Action):
    '''
    An action to convert public opinion into usable funds
    '''
    
    def __init__(self, name, agent, v_index):
        
        super().__init__(name, agent, v_index)
        self.counter = 0
    def precondition(self):
        return self.agent.funds > self.agent.overhead
    
    def do(self):
        super().do()
        expendable_funds = self.agent.funds - self.agent.overhead
        self.agent.campaign = min(expendable_funds,(self.agent.city.po_max - self.agent.city.public_opinion) / (100 - self.agent.values.v_tau[0]))
        self.agent.city.public_opinion += self.agent.campaign
        self.agent.cumulative_marketing_expenditures += self.agent.campaign
        self.agent.funds -= self.agent.campaign

        
class customActivity(Action):
    '''
    An action to convert public opinion into usable funds
    '''
    
    def __init__(self, name, agent, v_index):
        
        super().__init__(name, agent, v_index)
        self.possible_days = set([0,1,2,3,4,5,6])
        self.counter = 0
    def precondition(self):
        return self.agent.funds > self.agent.overhead
    
    def do(self):
        super().do()
        #find needed activity, add it to set
        need = self.agent.identify_need()
        
        #if activity already meets  that need, add another session to it
        additional_session = None
        for act in self.agent.activities:
            if need == act.v_index:
                additional_session = act
                break
        #add session to existing activity
        if additional_session != None and self.possible_days.difference(act.frequency):
            new_day = self.possible_days.difference(act.frequency).pop()
            act.frequency.add(new_day)
            act.attendance[new_day] = 0
            self.agent.activity_records[act.name][new_day] = 1
            self.agent.activity_attendance[act.name][new_day] = 0
            self.agent.funds -= self.agent.cost_per_activity

        
        #otherwise create new activity
        else:
            day = np.random.randint(0,6)
            activity = Activity(self.agent.unique_id, self.agent.model, {day}, need)
            activity.name = 'custom'+str(need)
            activity.basic = 0
            self.agent.activities.add(activity)
            self.agent.activity_records[activity.name] = {day:1}
            self.agent.activity_attendance[activity.name] = {day:0}
            self.agent.city.azc.activity_center.activities_available.add(activity)
            self.agent.funds -= self.agent.cost_per_activity
        
    
class adjustStaff_COA(Action):
    '''
    An action that calibrates current staff to current number of occupants
    Value: Openness to change
    Improves Flexibility
    '''
    def __init__(self,name, agent, v_index):
        super().__init__(name, agent, v_index)
        self.counter = 0
        
    def precondition(self):
        '''
        COA can do this theoretically whenever, but we could also put a budget constraint
        '''
        self.required_staff = int(self.agent.get_total_occupancy()*self.agent.staff_to_resident_ratio)
        self.adjustment = self.required_staff - self.agent.staff

        return self.adjustment < 0 or self.agent.budget.accounts['Staff'] > 0
    def do(self):
        super().do()
        working_conditions = self.agent.get_working_conditions()
        required_staff = int(self.agent.get_total_occupancy()*self.agent.staff_to_resident_ratio)
        adjustment = required_staff - self.agent.staff
        if adjustment > 0:
            while self.agent.budget.accounts['Staff'] > 0 and adjustment > 0:
                
                if np.random.uniform(0,1) < working_conditions:
                    self.agent.staff += 1
                    self.agent.budget.accounts['Staff'] -= 1
                adjustment -= 1
        else: 

            while adjustment < 0:
                self.agent.staff -= 1
                self.agent.budget.accounts['Staff'] += 1
                adjustment += 1
            
class improveFacilities(Action):
    '''
    Value: Self-Enhancement
    Improves building health
    '''
    def __init__(self,name, agent, v_index):
        super().__init__(name, agent, v_index)
        self.counter = 0
    def precondition(self):
        '''
        COA can do this theoretically whenever, but we could also put a budget constraint
        '''
        return True
    def do(self):
        super().do()
        total_spent = 0
        for azc in self.agent.city.azcs:
            increase_amount = (azc.max_health - azc.health)*(self.agent.conservatism/100)
            new_health = max(azc.operational_health, azc.health + increase_amount)
            delta_health = new_health - azc.health
            if delta_health > self.agent.budget.accounts['Housing']:
                azc.health += self.agent.budget.accounts['Housing']
                total_spent += delta_health
                self.agent.budget.spend('Housing',self.agent.budget.accounts['Housing'])
            else:
                
                while self.agent.budget.accounts['Housing'] > 0 and delta_health > 0:
                    azc.health += 1
                    delta_health -= 1
                    self.agent.budget.accounts['Housing'] -= 1
                    total_spent += 1
                
                
 
        self.agent.housing_costs += total_spent
    
class Checkin(Action):
    
    def __init__(self, name, agent, v_index):
        super().__init__(name, agent, v_index)
        
        self.healthy_threshold = .5
        self.satisfaction = np.array([])
        
    def precondition(self):
        '''
        That coa has some staff at all
        '''
        return self.agent.staff > 0
    
    def do(self):
        '''
        checks health of residents, if below threshold satisfy conservatism (ie security)
        '''
        super().do()
        
        total_occ = np.sum([azc.occupancy for azc in self.agent.city.azcs]) + self.agent.city.hotel.occupancy
        staff_fitness = self.agent.staff / (total_occ*self.agent.staff_to_resident_ratio)
        #iterate through newcomers
        for newcomer in self.agent.city.azc.occupants:
            #probability of error depends on number of staff
            
            if not newcomer.invested and newcomer.values.health < .5 and np.random.uniform(0,1) < staff_fitness:
                #do checkin
                
                #identify need
                lack = newcomer.values.v_tau - newcomer.values.val_t
                need = np.where(lack == max(lack))[0][0]
                
                #option is a placeholder for the other location needed
                option = None
                #search through other cities
                cities = [coa.city for coa in self.agent.model.schedule.agents if 
                      type(coa) is organizations.COA and coa.city != self.agent.city]
                for city in cities:
                    #check AZC Activity Center for Matching activity
                    for azc in city.azcs:
                        for activity in azc.activity_center.activities_available:
                            
                            if activity.v_index == need:
                                option = activity
                                break
                        if option != None:
                            break
                   

                if option != None and newcomer not in self.agent.voucher_requests:
                    self.agent.voucher_requests.add(newcomer)
                                        
                
        

class BuildCentral(Action):
    
    def __init__(self, name, agent, v_index):
        
        super().__init__(name, agent, v_index)
        
    def precondition(self):
        '''
        check if agent in crisis
        '''        
        
        return self.agent.city.azc.state == 'Crisis' and self.agent.city.azc.modality != 'COL'
    
    
    def do(self):
        super().do()
        
        #how long until run out of space
        time = self.agent.city.azc.estimate_time(max(3, self.agent.city.azc.shock_position))
        
        #how much space is required in six months
        need = self.agent.city.azc.estimate(int(180/self.agent.assessment_frequency))
        
        #build for that amount
        self.agent.build(need, max(30, time))
        
        

class BuildFlex(Action):
    
    def __init__(self, name, agent, v_index):
        
        super().__init__(name, agent, v_index)
        
    def precondition(self):
        '''
        check if agent in crisis
        '''        
        
        return self.agent.crisis and not self.agent.ta
    
    def evaluate_options(self):
        
        average_duration = 50
        
        ####Gather Buildings####
        empties = [building for building in self.agent.city.buildings
                   if type(building) is organizations.Empty and
                   self.agent.budget > building.convert_cost]
        
        #gather candidates
        candidates = [building for building in 
                      empties if
                      building.capacity > self.agent.need]
        
        hotel = [x for x in self.agent.city.buildings
                 if type(x) is organizations.Hotel][0]
        
        candidates.append(hotel)
                      
        for building in candidates:
            building.calc_cost(self.agent.need, average_duration)
        
        #find max value, need:cost ratio
        best = max(candidates, key = attrgetter('calculated_value'))
        
        #increase supply of available housing
        self.agent.city.aux_supply += .25

        #return policy
        return best
    
    def do(self):
        super().do()
        
        decision = self.evaluate_options()
        
        if type(decision) is not organizations.Hotel:
            
            self.agent.construct(decision)
            
class BuildRobust(Action):
    
    def __init__(self, name, agent, v_index):
        
        super().__init__(name, agent, v_index)
        
    def precondition(self):
        '''
        check if agent in crisis
        '''        
        
        return self.agent.crisis and not self.agent.ta
    
    def evaluate_options(self):
        average_duration = 50
        
        ####Gather Buildings####
        empties = [building for building in self.agent.city.buildings
                   if type(building) is organizations.Empty and
                   self.agent.budget > building.convert_cost]
        
        #gather candidates
        candidates = [building for building in 
                      empties if
                      building.capacity > self.agent.need]
        
        hotel = [x for x in self.agent.city.buildings
                 if type(x) is organizations.Hotel][0]
        
        candidates.append(hotel)
        
        adjusted_need = int(self.agent.need + .25*self.agent.need)
                      
        for building in candidates:
            building.calc_cost(adjusted_need, average_duration)
        
        #find max value, need:cost ratio
        best = max(candidates, key = attrgetter('calculated_value'))

        #return policy
        return best
    
    def do(self):
        super().do()
        
        decision = self.evaluate_options()
        
        if type(decision) is not organizations.Hotel:
            
            self.agent.construct(decision)
        
        
                     

        
class Invest(Action):
    
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
        

        
    def precondition(self):
        
        #add finances
        
        return self.agent.state != 'Crisis'
    
    def do(self):
        
        super().do()
        gravity = 1-self.agent.gravity
        counter = 0
        voucher_budget = int(gravity*(self.agent.self_transcendence/100)*len(self.agent.voucher_requests))
        while self.agent.voucher_requests and voucher_budget > 0:
            current = self.agent.voucher_requests.pop()
            current.allowance += self.agent.city.cost_of_bus_to_another_city
            current.invested = True
            counter += 1
            self.agent.net_investment += 1
            self.agent.net_costs += 1
            voucher_budget -= 1
       

class Segregate(Action):
        
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
        self.unlikely_status_holders = []
        
        
        
    def precondition(self):
        
        #check if not crisis
        for azc in self.agent.city.azcs:
            for newcomer in azc.occupants:
                if newcomer.second == 0:
                    self.unlikely_status_holders.append(newcomer)
        return self.agent.state != 'Crisis' 
        
    
    def do(self):
        super().do()
        
        #gets a cost per azc from health + occupancy + activities + proximity
        candidates = [azc for azc in 
         self.agent.model.schedule.agents if
         type(azc) is organizations.AZC and
         azc.modality != 'COL']
        
        [azc.get_operational_cost() for azc in candidates]
        
        candidates.sort(key = lambda x: x.operational_cost)
        count = 0
        candidate_idx = 0
        cheapest_azc_to_maintain = candidates[candidate_idx]
        
        while count < len(self.unlikely_status_holders) and candidate_idx < len(candidates):
            cheapest_azc_to_maintain = candidates[candidate_idx]
            if cheapest_azc_to_maintain.occupancy/cheapest_azc_to_maintain.capacity < .9:
                
                newcomer = self.unlikely_status_holders.pop()
                if newcomer.second == 0:
                    
                        
                        self.agent.move(newcomer, cheapest_azc_to_maintain)
                        newcomer.segregated = True
                        count += 1
                else:
                    self.agent.newcomers.add(newcomer)
            else:
                candidate_idx += 1
                
                
           
 

class raiseThreshold(Action):
    
    def __init__(self,name, agent, v_index):
        
        '''
        raises threshold, shrinks the margin, essentially tightens border security
        '''
        super().__init__(name, agent,v_index)

        self.counter = 0              #for histogramming purposes
        self.marginal_decrease = .05
        
    def precondition(self):
        '''
        IND can do this whenever
        '''
        return True
        
    def do(self):
        
        super().do()
        
        #decrease margin by .05
        self.agent.margin = max(-.1,self.agent.margin - self.marginal_decrease)
        
class lowerThreshold(Action):
    
    def __init__(self,name, agent, v_index):
        
        '''
        lowering the threshold increases the margin
        '''
        super().__init__(name, agent,v_index)

        self.counter = 0              #for histogramming purposes
        self.marginal_increase = .05
        
    def precondition(self):
        '''
        IND can do this whenever
        '''
        return True
        
    def do(self):
        
        super().do()
        
        #increase margin by .05
        self.agent.margin += self.marginal_increase
    
class adjustStaff(Action):
    
    
    def __init__(self,name, agent, v_index):
        
        '''
        
        '''
        super().__init__(name, agent,v_index)
        self.counter = 0              #for histogramming purposes #used in the test ipynb
        self.LOW_OCCUPANCY_OCC_TO_STAFF_RATIO = 4
        self.HIGH_OCCUPANCY_OCC_TO_STAFF_RATIO = 2
        
    def precondition(self):
        '''
        IND can do this when it has the funds or when laying staff off
        '''
        if self.agent.city.azc.shock_state != 'Problematic':
            ratio = self.agent.staff_to_resident_ratio
        else:
            ratio = self.agent.staff_to_resident_ratio/2
        
        required_staff = int(self.agent.city.coa.get_total_occupancy()/ratio)
        adjustment = required_staff - self.agent.staff
        occupied = self.agent.city.coa.get_total_occupancy() > 0
        return (adjustment < 0 or self.agent.budget.accounts['Staff'] > 0) and occupied
        
    def do(self):
        
        super().do()
        # Adjust current staff to be in accordance with actual occupancy levels
        # here occupants reside in azc?
        
        if self.agent.city.azc.shock_state != 'Problematic': 
            ratio = self.agent.staff_to_resident_ratio
        else:
            ratio = self.agent.staff_to_resident_ratio/2
        
        required_staff = int(self.agent.city.coa.get_total_occupancy()/ratio)
        adjustment = required_staff - self.agent.staff
        if adjustment > 0:
            if adjustment > self.agent.budget.accounts['Staff']:
                self.agent.staff += self.agent.budget.accounts['Staff']
                self.agent.budget.accounts['Staff'] =  0
            else:
                self.agent.staff += adjustment
                self.agent.budget.accounts['Staff'] -= adjustment

        else: 

    
            self.agent.staff += adjustment
            self.agent.budget.accounts['Staff'] -= adjustment
        
class issueStatement(Action):

    def __init__(self, name, agent, v_index):
        
        super().__init__(name, agent,v_index)
        self.counter = 0
        
    def precondition(self):
        
        return True
    
    def do(self):
        super().do()
        
        occupancy = np.sum([azc.occupancy for azc in self.agent.model.schedule.agents if
                           type(azc) is organizations.AZC and azc.modality == 'AZC'])
        capacity = np.sum([azc.capacity for azc in self.agent.model.schedule.agents if
                           type(azc) is organizations.AZC and azc.modality == 'AZC'])
        self.agent.model.ind_statement = 1 - (occupancy / capacity)
class Activity(Agent):
    
    def __init__(self, unique_id, model, frequency, v_index):
       
    
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
        self.v_index = v_index
        self.name = None

        self.local_involvement = 0  #number between 0 and 1 indicating what percent of participants are locals
        self.obligatory = False
        self.critical = False
        self.effect = None
        self.attendance = {}
        self.basic = 1
        for day in frequency:
            self.attendance[day] = 0
    
    def satisfaction(self, agent):
        
        agent.values.val_t[self.v_index] += agent.values.val_sat[self.v_index]
    
    def precondition(self, agent):
        
        return agent.health > .2
        
    def do(self, agent):
        '''
        Do is separate from satisfaction bc there may be
        extra changes in state that are activity specific
        '''
        day = self.model.schedule.steps % 7
        
            
        #change satisfaction 
        self.satisfaction(agent)
        
        
        #keeping track of attendances for NGO
        self.attendance[day] += 1
        
        #keeping track for activity center
        if self.name in agent.current[1].activity_center.counter:
            agent.current[1].activity_center.counter[self.name] += 1
        else:

            agent.current[1].activity_center.counter[self.name] = 1
        
        #add finances for out of town activities
        # if same city but diff location, charge intra city costs
        # if same city same location charge nothing
        # if diff city charge intercity costs
        if agent.loc != agent.current[1] and agent.coa.city == agent.current[1].city:
            agent.budget -= 4
        elif agent.coa.city != agent.current[1].city:
            agent.budget -= 20
            
        agent.acculturation += self.local_involvement*((agent.max_acc - agent.acculturation)/50)
            

class Doctor(Activity):
    
    def __init__(self, unique_id, model, frequency,v_index):
    
            
    #Value: Conservatism (security)
    #Effect: Increase health of NC
    #Expected Result: Health increases, more willing to engage in other activities. 
            
        super().__init__(unique_id, model, frequency, v_index)
        
        self.effect = self.satisfaction
        self.frequency = frequency
        
        # could everyone do this or just as_ext?
        self.occupant_type = {'tr', 'as', 'as_ext'}
        self.v_index = v_index
        self.healthiness_threshold = 30
        self.name = 'Doctor'
        self.HEALTH_INCREASE = 20
        self.obligatory = True
        self.critical = True
        
    def precondition(self, agent):
        '''
        Available to those who need it, ie health below threshold
        '''
        if type(agent.loc) is organizations.Hotel:
            budget = agent.budget > 1.5*agent.coa.city.cost_of_bus_within_city
        else:
            budget = agent.budget > agent.coa.city.cost_of_bus_within_city
        return agent.ls in self.occupant_type and agent.health < self.healthiness_threshold and budget

    
    def do(self, agent):
        super().do(agent)
        agent.health = min(agent.health+self.HEALTH_INCREASE, self.healthiness_threshold)
        agent.budget -= agent.coa.city.cost_of_bus_within_city
        agent.loc.city.costs += 1
        
class Football(Activity):
    
    def __init__(self, unique_id, model, frequency,v_index):
        
        '''
        more male oriented, 
        should be male specific pre-conditions re 
        Vivien's comments on men's tendency to cross cultural boundaries
        though football
        '''
        
        super().__init__(unique_id, model, frequency, v_index)
        
        self.effect = self.satisfaction
        self.frequency = frequency
        self.occupant_type = {'as', 'as_ext', 'tr'}
        self.HEALTH_THRESHOLD = 60
        self.HEALTH_INCREASE = 4
        
        self.v_index = v_index
    
    def precondition(self, agent):
        return  agent.ls in self.occupant_type and agent.health > self.HEALTH_THRESHOLD
        

    def do(self, agent):
        self.local_involvement = agent.current[1].city.public_opinion
        super().do(agent)
        agent.health = min(agent.health+self.HEALTH_INCREASE, agent.HEALTH_MAX)
        
        #possible additions: SOCIALIZE or HEALTH++
        
   
        
class Craft(Activity):
    HEALTH_THRESHOLD = 10.0
    def __init__(self, unique_id, model, frequency,v_index):
        
        '''
        More female oriented re Vivien Coulier's comments on
        women participating in women's only activities
        and guaging willingness to participate based on
        ethnic homogenaeity. 
        '''
        
        super().__init__(unique_id, model, frequency, v_index)
        
        self.effect = self.satisfaction
        self.frequency = frequency
        self.name = 'Craft'
        
        self.v_index = v_index
        
    def precondition(self, agent):
        return  agent.ls in self.occupant_type and agent.health > Craft.HEALTH_THRESHOLD
         
    
    def do(self, agent):
        super().do(agent)
        #possible additions: SOCIALIZE or HEALTH++

class Language_Class(Activity):
    def __init__(self, unique_id, model, frequency,v_index):
        
        super().__init__(unique_id, model, frequency, v_index)
        
        self.effect = self.satisfaction
        self.frequency = frequency
        self.occupant_type = {'tr'}
        self.HEALTH_THRESHOLD = 30.0
        self.name = 'languageClass'
        self.obligatory = False

        self.v_index = v_index
    
    def precondition(self, agent):
        return  agent.ls in self.occupant_type and agent.health > self.HEALTH_THRESHOLD
        

    
    def do(self, agent):

        super().do(agent)
        self.local_involvement = agent.current[1].coa.city.public_opinion

        agent.acculturation += agent.values.health*self.local_involvement*(agent.max_acc - agent.acculturation) / 10
        #possible additions: AGENT.INTEGRATION ++ also opportunity to socialize
    
class Socialize(Activity):
    
    def __init__(self, unique_id, model, frequency, v_index):
        super().__init__(unique_id, model, frequency, v_index)
        
        '''
        Value: Conservatism (Tradition and Security)
        General idea: Essentially Hanging-Out, Socializing for its own sake.
            Socialize builds community. Agents connect with those of the same
        culture. As Acculturation increases, so does the likelihood of connecting
        with somemone of a different culture
        '''
        
        self.effect = self.satisfaction
        self.frequency = frequency
        self.occupant_type = {'edp','as','as_ext','tr'}
        self.HEALTH_THRESHOLD = 40.0
        self.name = 'Socialize'
    
    def precondition(self, agent):
        
        return agent.values.health > .4 and agent.health > self.HEALTH_THRESHOLD and np.random.uniform(0,100) < agent.loc.health
    
    def do(self, agent):
        '''
        What if, agents share information re activities
        so that agents aren't so omnicient.
        '''
        
        super().do(agent)
        

class Volunteer(Activity):
    
    def __init__(self, unique_id, model, frequency,v_index):
        
        super().__init__(unique_id, model, frequency, v_index)
        
        self.effect = self.satisfaction
        self.frequency = frequency
        self.occupant_type = {'tr', 'as', 'as_ext'}
        self.HEALTH_THRESHOLD = 40.0
        self.v_index = v_index
        self.name = 'Volunteer'
    
    def precondition(self, agent):
        return  agent.ls in self.occupant_type and agent.health > self.HEALTH_THRESHOLD
             

    
    def do(self, agent):
        self.local_involvement = agent.current[1].coa.city.public_opinion
        super().do(agent)
        po_max = agent.current[1].coa.city.po_max
        current = agent.current[1].coa.city.public_opinion

        agent.current[1].coa.city.public_opinion += (po_max - current) / 100#1000 * (1-agent.coa.gravity)
        #ossible additions: AGENT.WORK_EXPERIENCE ++ also opportunity to socialize
        
class Work(Activity):
    HEALTH_THRESHOLD = 70.0
    def __init__(self, unique_id, model, frequency,v_index):
        
        super().__init__(unique_id, model, frequency, v_index)
        
        self.effect = self.satisfaction
        self.frequency = frequency
        self.name = 'Work'
        self.occupant_type = {'tr', 'as', 'as_ext'}
        
        self.v_index = v_index
        
    def precondition(self, agent):
        return  agent.ls in self.occupant_type and agent.health > Work.HEALTH_THRESHOLD and agent.age > 18
      


    
    def do(self, agent):
        super().do(agent)
        earnings = 10
        agent.budget += .50*earnings
        agent.coa.budget.accounts['Savings'] += .50*earnings
        
            #possible additions: AGENT.WORK_EXPERIENCE ++ also opportunity to socialize

class Crime(Activity):
    
    def __init__(self,unique_id, model, frequency, v_index):
        
        super().__init__(unique_id, model, frequency, v_index)
        self.frequency = frequency
        self.name = 'Crime'
        self.occupant_type = {'tr', 'as', 'as_ext'}
        self.v_index = v_index
        self.basic = 0
    
    def precondition(self, agent):
        val_hel = agent.values.health < .05
        intent = agent.values.v_tau[0] > 58.9
        conditions = agent.loc.health < 50
        #bumps crime up to the the top of the activity stack
        if np.random.randint(0,100)/2 > agent.qol:
            self.basic = 1

        return val_hel and conditions and intent #np.random.uniform(0,1) < .001 #
    
    def do(self, agent):
        super().do(agent)
        agent.loc.city.public_opinion -= (agent.loc.city.public_opinion - agent.loc.city.po_min) / 2
        agent.coa.city.public_opinion = max(0, agent.coa.city.public_opinion)
        agent.coa.city.crime += 1

class Study(Activity):
    HEALTH_THRESHOLD = 40.0
    def __init__(self, unique_id, model, frequency,v_index):
        
        super().__init__(unique_id, model, frequency, v_index)
        
        self.effect = self.satisfaction
        self.frequency = frequency
        self.name = 'Study'
        self.occupant_type = {'tr', 'as', 'as_ext'}
        
        self.v_index = v_index
        
    def precondition(self, agent):
        return  agent.ls in self.occupant_type and agent.health > Work.HEALTH_THRESHOLD and agent.age < 18

    def do(self, agent):
        self.local_involvement = agent.values.health*agent.current[1].coa.city.public_opinion
        super().do(agent)
        agent.education += (agent.max_education - agent.education) / (100-agent.values.v_tau[0])
        
            #possible additions: AGENT.WORK_EXPERIENCE ++ also opportunity to socialize
            # Also agent.budget++        
        
        
