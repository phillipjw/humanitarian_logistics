#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 10:57:53 2018

@author: phillip
"""

from mesa import Agent, Model
import operator
import numpy

class Values():
    
    def __init__(self, decay, se=0, st=0, c=0, otc=0):
        
        self.v_tau = np.array([se,st,c,otc])
        
        #Value satisfaction
        self.val_sat = np.repeat(100, 4) - self.val_tau
        
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
        