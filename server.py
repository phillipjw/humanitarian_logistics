# server.py
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import HumanitarianLogistics, AZC, Newcomer
from mesa.visualization.modules import ChartModule


canvas_width = 500
canvas_height = 300

grid_width = int(canvas_width / 2)
grid_height = int(canvas_height / 2)

num_azc = 4
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
        portrayal['text'] = agent.occupancy


        
    return portrayal

grid = CanvasGrid(agent_portrayal, grid_width, grid_height,canvas_width, canvas_height)

chart = ChartModule([{'Label' : 'Capacities',
                      'Color' : 'Black'}],
                    data_collector_name = 'datacollector')

server = ModularServer(HumanitarianLogistics,
                       [grid,chart],
                       "Humanitarian Logistics",
                       {"N_a": num_azc,"nc_rate" : nc_rate, "width": grid_width, "height": grid_height})

