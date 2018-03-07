# server.py
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import HumanitarianLogistics, AZC, Newcomer
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.ModularVisualization import VisualizationElement
import numpy as np

canvas_width = 500
canvas_height = 300

grid_width = int(canvas_width / 2)
grid_height = int(canvas_height / 2)

num_azc = 4
#nc_rate = .5

nc_rate = UserSettableParameter('slider', "In-Flow", .25, 0, 1, .1)

class HistogramModule(VisualizationElement):
    package_includes = ["Chart.min.js"]
    local_includes = ["HistogramModule.js"]

    def __init__(self, bins, canvas_height, canvas_width):
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.bins = bins
        new_element = "new HistogramModule({}, {}, {})"
        new_element = new_element.format(bins,
                                         canvas_width,
                                         canvas_height)
        self.js_code = "elements.push(" + new_element + ");"
        
    def render(self, model):
        
        newcomers = [agent for agent in model.schedule.agents if
                     type(agent) is Newcomer]
        
        statuses = [agent.first for agent in newcomers]
        
        hist = np.histogram(statuses, bins=self.bins)[0]
        return [int(x) for x in hist]



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
        
        portrayal['Shape'] = "circle"
        portrayal['Filled'] = 'true'
        portrayal['Layer'] = 0
        portrayal['Color'] = 'blue'
        portrayal['r'] = 10
        portrayal['text'] = agent.occupancy


        
    return portrayal

grid = CanvasGrid(agent_portrayal, grid_width, grid_height,canvas_width, canvas_height)

histogram = HistogramModule(list(range(10)), 200, 500)

chart = ChartModule([{'Label' : 'Cap - Extended-AS',
                      'Color' : 'Black'},
                    {'Label' : 'Cap - AS',
                      'Color' : 'Blue'}],
                      data_collector_name = 'datacollector')

chart_suces = ChartModule([{'Label' : 'Syria',
                            'Color' : 'blue'},
                          {'Label' : 'Iraq',
                            'Color' : 'red'},
                          {'Label' : 'Eritrea',
                            'Color' : 'black'},
                          {'Label' : 'Afghanistan',
                            'Color' : 'yellow'},],
                          data_collector_name = 'sr')





server = ModularServer(HumanitarianLogistics,
                       [grid,chart, chart_suces],
                       "Humanitarian Logistics",
                       {"N_a": num_azc,"nc_rate" : nc_rate, "width": grid_width, "height": grid_height})

