# server.py
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import HumanitarianLogistics, AZC, Newcomer, Hotel, Empty, AZC_Viz, COA
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.ModularVisualization import VisualizationElement
import numpy as np

canvas_width = 600
canvas_height = 400
num_pol = 2

grid_width = int(canvas_width / 4)
grid_height = int(canvas_height / 4)



def agent_portrayal(agent):
    
    if agent is None:
        return
        
    portrayal = {}

        
        
    


        
    return portrayal

grid = CanvasGrid(agent_portrayal, grid_width, grid_height,canvas_width, canvas_height)








server = ModularServer(HumanitarianLogistics,
                       [grid],
                       "Humanitarian Logistics",
                       {"width": grid_width, "height": grid_height, "num_pols": num_pol})

