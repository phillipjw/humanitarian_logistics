# server.py
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import HumanitarianLogistics, AZC, Newcomer, Hotel, Empty, AZC_Viz, COA, IND
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.ModularVisualization import VisualizationElement
from SimpleContinuousModule import SimpleCanvas
#from mesa.visualization.modules.SimpleContinuousModule import SimpleCanvas
import numpy as np

canvas_width = 400
canvas_height = 600
num_pol = 3

azc_display_size = 20



def agent_portrayal(agent):
    if agent is None:
        return
        
    portrayal = {}
    
    if type(agent) is IND:
        
        portrayal['Shape'] = "circle"
        portrayal['Filled'] = 'False'
        portrayal['Layer'] = 0
        portrayal['Color'] = 'blue'
        portrayal['r'] = azc_display_size
     
    elif type(agent) is AZC:
        
        portrayal['Shape'] = "circle"
        portrayal['Filled'] = 'False'
        portrayal['Layer'] = 1
        portrayal['Color'] = 'red'
        portrayal['r'] = int(agent.occupancy*azc_display_size / agent.capacity)
    
   
        

      
        
    


        
    return portrayal

continuous_canvas = SimpleCanvas(agent_portrayal, canvas_width, canvas_height)

#grid = CanvasGrid(agent_portrayal, grid_width, grid_height,canvas_width, canvas_height)








server = ModularServer(HumanitarianLogistics,
                       [continuous_canvas],
                       "Humanitarian Logistics",
                       {"width": canvas_width, "height": canvas_height, "num_pols": num_pol})

