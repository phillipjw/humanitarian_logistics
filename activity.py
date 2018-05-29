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
        self.agent.funds = max(0,self.agent.city.public_opinion - len(self.agent.activities) * self.agent.cost_per_activity)

class marketingCampaign(Action):
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
        
class customActivity(Action):
    '''
    An action to convert public opinion into usable funds
    '''
    
    def __init__(self, name, agent, v_index):
        
        super().__init__(name, agent, v_index)
        self.counter = 0
    def precondition(self):
        return self.agent.funds > self.agent.cost_per_activity
    
    def do(self):
        super().do()
        #find needed activity, add it to set
        need = self.agent.identify_need()
        activity = Activity(self.agent.unique_id, self.agent.model, {1}, need)
        activity.name = 'custom'+str(need)
        self.agent.activites.add(activity)
        self.agent.city.azc.activity_center.activities_available.add(activity)
        self.agent.funds -= self.agent.cost_per_activity
        
class Prioritize(Action):
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
        return True
    def do(self):
        super().do()
        
        self.agent.staff = self.agent.get_total_occupancy()*self.agent.staff_to_resident_ratio
    
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
        for azc in self.agent.city.azcs:
            increase_amount = (azc.max_health - azc.health)*(self.agent.conservatism/100)
            azc.health = max(azc.operational_health, azc.health + increase_amount)
        
    
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
        
        current_ratio = self.agent.staff / np.sum([azc.occupancy for azc in
                                                   self.agent.city.azcs])
        error_probability = current_ratio / self.agent.staff_to_resident_ratio
        #iterate through newcomers
        for newcomer in self.agent.city.azc.occupants:
            #probability of error depends on number of staff
            
            if np.random.uniform(0,1) < error_probability:
                #do checkin
                if newcomer.values.health < self.healthy_threshold:
                    pass
                    #placeholder value satisfaction
                    #newcomer.values.val_t += np.array([50,50,50,50])
        

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
        self.agent.build(need)
        
        

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
        
    def precondition(self):
        
        return self.agent.shock
    
    def do(self):
        
        super().do()
        
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
        

        
    def precondition(self):
        
        ''''
        check if action is feasible in the first place
        by ensuring that azcs's are non-empty
        '''
        
        return self.agent.state != 'Crisis' and sum([azc.occupancy for azc in
                                             self.agent.city.azcs]) > 0
    
    def do(self):
        super().do()
        #this is placeholder and should go outisde the function
        if not self.precondition():
            print('Cannot Consolidate')
            pass
        
        #get all non-empty AZCs
        azcs = [azc for azc in self.agent.model.schedule.agents if
                type(azc) is organizations.AZC and not azc.modality != 'COL' and
                azc.occupancy > 0]

        
        #Order non-empty Azcs by occupancy
        azcs.sort(key = lambda x: x.occupancy)
        
        
        #move occupants to central location
        for current in self.agent.city.azcs:
            
            #take lowest capacity AZC and move its occupants to highest
            #capacity AZC that can fit them
            
            amount = current.occupancy
            
           
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
        
    
        
        between_city_travel = True # we will want to parameterize this somehow
        travel_voucher = self.agent.city.cost_of_bus_within_city 
        if not between_city_travel:
            travel_voucher = self.agent.city.cost_of_bus_to_another_city 
        
        for azc in self.agent.city.azcs:
                 for newcomer in azc.occupants:
                     newcomer.budget = newcomer.budget + travel_voucher
                

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
        for azc in self.agent.city.azcs:
            for newcomer in azc.occupants:
                if newcomer.second == 0:
                    self.unlikely_status_holders.append(newcomer)
        
        
    def precondition(self):
        
        #check if not crisis
        return self.agent.state != 'Crisis' 
        
    
    def do(self):
        super().do()
        cheapest_azc_to_maintain = None
        
        #gets a cost per azc from health + occupancy + activities + proximity
        [azc.get_operational_cost() for azc in 
         self.agent.model.schedule.agents if
         type(azc) is organizations.AZC and
         azc.modality != 'COL']
        
        cheapest_azc_to_maintain = min([azc for azc in self.agent.city.azcs], key = attrgetter('operational_cost'))
        
        if cheapest_azc_to_maintain != None:
            
            
            count = 0
            
            while count < len(self.unlikely_status_holders):
                newcomer = self.agent.newcomers.pop()
                if newcomer.second == 0:
                    self.agent.move(newcomer, cheapest_azc_to_maintain)
                    count += 1
                else:
                    self.agent.newcomers.add(newcomer)
                
           
        
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
        

        
    def precondition(self):
        
        #check if not shock and check if feasible
        return self.agent.state != 'Crisis'
    
    def do(self):
        super().do()
        between_city_travel = True # we will want to parameterize this somehow
        travel_voucher = self.agent.city.cost_of_bus_within_city 
        if not between_city_travel:
            travel_voucher = self.agent.city.cost_of_bus_to_another_city 
        
        for azc in self.agent.city.azcs:
                 for newcomer in azc.occupants:
                     newcomer.budget = newcomer.budget + travel_voucher

class OpenToNGO(Action):
    
    # Value: Openness to change
    # Effect: Allow local NGO to add an activity to AZC schedule.
    # Expected result: Locals interact with newcomers, some Newcomer values get satisfied. 
    
    def __init__(self, name, agent, v_index):
        
        super().__init__(name, agent, v_index)
        
    def precondition(self):
        # test to see if an ngo exits. this is right, correct. A coa would have an NGO
        return self.agent.city.ngo != None
    
    
    def do(self):
        super().do()
        # right now the activity is just a language class but can be changed to randomly pick one of ours
        # or allow the NGO to design an activity for the AZC
        self.agent.city.azc.activity_center.activities_available.add(activity.Language_Class(self.unique_id, 
                                                                     self.model, {1,2,3,4,5}, 0))

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
        self.agent.margin -= self.marginal_decrease
        
class lowerThreshold(Action):
    
    def __init__(self,name, agent, v_index):
        
        '''
        lowering the threshold increases the margin
        '''
        super().__init__(name, agent,v_index)

        self.counter = 0              #for histogramming purposes
        self.marginal_increase = .15
        
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
        Indeed, ind can do this whenever.
        '''
        return True
        
    def do(self):
        
        super().do()
        # Adjust current staff to be in accordance with actual occupancy levels
        # here occupants reside in azc?
        
        
        currentOccupants = len(self.agent.city.azc.occupants)
        currentStaff = self.agent.city.ind.staff+1 # to ensure no divide by zero
        #if (currentOccupants/currentStaff) >= self.LOW_OCCUPANCY_OCC_TO_STAFF_RATIO:
        self.agent.city.ind.staff = len(self.agent.city.azc.occupants) / self.LOW_OCCUPANCY_OCC_TO_STAFF_RATIO
        # this simulates bottle necking highering additional staff when occupancy is high    
        if (currentOccupants/currentStaff) > self.HIGH_OCCUPANCY_OCC_TO_STAFF_RATIO:
            self.agent.city.ind.staff = len(self.agent.city.azc.occupants) / self.HIGH_OCCUPANCY_OCC_TO_STAFF_RATIO 

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
        

        self.effect = None
    
    def satisfaction(self, agent):
        
        agent.values.val_t[self.v_index] += agent.values.val_sat[self.v_index]
        
    def do(self, agent):
        '''
        Do is separate from satisfaction bc there may be
        extra changes in state that are activity specific
        '''
        #change satisfaction 
        self.satisfaction(agent)
        if self.name in agent.current[1].activity_center.counter:
            agent.current[1].activity_center.counter[self.name] += 1
        else:

            agent.current[1].activity_center.counter[self.name] = 1
            
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
        self.HEALTH_INCREASE = 10
        
    def precondition(self, agent):
        '''
        Available to those who need it, ie health below threshold
        '''
        return agent.ls in self.occupant_type and agent.health < self.healthiness_threshold

    
    def do(self, agent):
        super().do(agent)
        agent.health = min(agent.health+self.HEALTH_INCREASE, agent.HEALTH_MAX)
        
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
        self.HEALTH_THRESHOLD = 50.0
        self.HEALTH_INCREASE = 4
        self.name = 'Football'
        
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

        self.v_index = v_index
    
    def precondition(self, agent):
        return  agent.ls in self.occupant_type and agent.health > self.HEALTH_THRESHOLD
        

    
    def do(self, agent):
        super().do(agent)
        agent.acculturation += (agent.max_acc - agent.acculturation) / 10
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
        self.HEALTH_THRESHOLD = 30.0
        self.name = 'Socialize'
    
    def precondition(self, agent):
        
        return agent.health > self.HEALTH_THRESHOLD and np.random.uniform(0,100) < agent.loc.health
    
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
        agent.current[1].coa.city.public_opinion += (po_max - current) / 10
        #possible additions: AGENT.WORK_EXPERIENCE ++ also opportunity to socialize
        
class Work(Activity):
    HEALTH_THRESHOLD = 40.0
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
        agent.coa.budget += .50*earnings
        
            #possible additions: AGENT.WORK_EXPERIENCE ++ also opportunity to socialize

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
        self.local_involvement = agent.current[1].coa.city.public_opinion
        super().do(agent)
        agent.education += (agent.max_education - agent.education) / (100-agent.values.v_tau[0])
        
            #possible additions: AGENT.WORK_EXPERIENCE ++ also opportunity to socialize
            # Also agent.budget++        
        
        
