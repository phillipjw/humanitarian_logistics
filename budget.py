#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 11:33:12 2018

@author: phillip
"""

import numpy as np
import copy

class Budget():
    
    def __init__(self, accounts, frequency):
        '''
        Keeps track of funds by type
        accounts is a list of types
        frequency is how often funds are replaced. 
        '''
        self.account_types = copy.copy(list(accounts.keys()))
        self.accounts = accounts            #keeps track of how much funding is available
        self.frequency = frequency    #how often funds replenished 
        self.replenish_amounts = copy.deepcopy(self.accounts)
        self.accounts['Savings'] = 0
        
    def spend(self, account, amount):
        #deducts an amount from an account        
        self.accounts[account] -= amount
    
    def __str__(self):
        return str(self.accounts)
    
    def replenish(self):
        
        #tops off accounts to replenish amount
        for account in self.account_types:
            self.accounts[account]  = max(self.replenish_amounts[account], self.accounts[account])