#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 11:45:31 2018

@author: phillip
"""

from mesa import Agent, Model

class AZC_Viz(Agent):
    
    def __init__(self,model,azc):
        
        self.model = model
        self.azc = azc
        
        self.value = 1
        self.display_height = 20
        self.height_adjust = int(.5*self.display_height)
        self.pos = (self.azc.pos[0], self.azc.pos[1] - self.height_adjust)
    
    def step(self):
        self.update_value()
        self.model.grid.place_agent(self, self.pos)
    
    def update_value(self):
        raw_value = self.azc.occupancy / self.azc.capacity
        value = int(self.display_height * raw_value)
        self.value = value
        
        height = int(-10*raw_value + 10)
        self.height_adjust = height 
        self.pos = (self.azc.pos[0], self.azc.pos[1] - self.height_adjust)
        
