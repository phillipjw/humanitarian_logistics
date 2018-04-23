#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 10:57:53 2018

@author: phillip
"""

import operator
import numpy as np

class Values():
    
    def __init__(self, decay, se=0, st=0, c=0, otc=0):
        
        # SE corresponds to an activity that provides betterment of one’s 
	     # own attributes through either enhancement
        # of already owned resources, corresponding to achievement, or the enhanced control of resource
        # acquisition, corresponding to power
        # ST satisfaction providing an activity where the betterment of
        # another agent’s attributes, as per its component values, benevolence and universalism
        # C, which is an activity providing tradition, conformity and security.
        # OTC is an activity providing stimulation and hedonism
        
        #putting the above together into one array
        
        self.v_tau = np.array([se,st,c,otc])
        
        #Value satisfaction
        self.val_sat = np.repeat(100, 4) - self.v_tau
        
        #current value satisfaction level at time t
        self.val_t = np.repeat(60, 4)
        
        #val_decay
        self.val_decay = np.repeat(decay, 4)
        
        #list of available actions
        self.actions = []
        
    def decay_val(self):
        
        self.val_t -= self.val_decay
        
    def prioritize(self):
        '''
        find difference between current val_sats and thresholds
        identify max value
        '''
        
        #get difference between thresholds and current satisfaction
        priorities = self.v_tau - self.val_t
        
        #get index of value w highest priority
        priority = max(enumerate(priorities), key = operator.itemgetter(1))
        
        return priority
        