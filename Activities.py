#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 14:14:30 2018

@author: phillip
"""

import mesa 
from mesa import Agent, Model
from scipy.stats import bernoulli
import numpy as np

class Activity(Agent):
    
    def __init__(self,unique_id, model, day):
        
        self.id = unique_id
        self.model = model
        self.day = day
        self.effect = None
        
class Football(Activity):
    
    def __init__(self, unique_id, model, day):
        
        super().__init__(unique_id, model, day)
        
        self.effect = self.satisfaction
        self.v_sat_amt = 10
        
        
    def satisfaction(self, participant):
        
        participant.v_sat += self.v_sat_amt
        
        