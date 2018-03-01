# server.py
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import HumanitarianLogistics, AZC, Newcomer

canvas_width = 500
canvas_height = 300

grid_width = int(canvas_width / 4)
grid_height = int(canvas_height / 4)

num_azc = 5
nc_rate = .5


def agent_portrayal(agent):
    
    if agent is None:
        return
        
    portrayal = {}
    
    if type(agent) is Newcomer:

        portrayal['Shape'] = "rect"
        portrayal['Filled'] = 'true'
        portrayal['Layer'] = 2
        portrayal['Color'] = 'red'
        portrayal['w'] = 3
        portrayal['h'] = 3

    
    elif type(agent) is AZC:
        
        portrayal['Shape'] = "rect"
        portrayal['Filled'] = 'true'
        portrayal['Layer'] = 0
        portrayal['Color'] = 'blue'
        portrayal['w'] = 20
        portrayal['h'] = 10        


        
    return portrayal

grid = CanvasGrid(agent_portrayal, grid_width, grid_height,canvas_width, canvas_height)
server = ModularServer(HumanitarianLogistics,
                       [grid],
                       "Humanitarian Logistics",
                       {"N_a": num_azc,"nc_rate" : nc_rate, "width": grid_width, "height": grid_height})

