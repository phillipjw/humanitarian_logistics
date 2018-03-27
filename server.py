# server.py
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import HumanitarianLogistics, AZC, Newcomer, Hotel, Empty, AZC_Viz
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.ModularVisualization import VisualizationElement
import numpy as np

canvas_width = 500
canvas_height = 300

grid_width = int(canvas_width / 3)
grid_height = int(canvas_height / 3)

num_azc = 4
num_cities = 1

shock_duration = UserSettableParameter('slider', "Shock Duration", 100, 0, 600, 20)
shock_period = UserSettableParameter('slider', "Shock Period", 200, 0, 600, 20)
shock_rate = UserSettableParameter('slider', "Shock Growth", .025, 0, 1, .001)


nc_rate = UserSettableParameter('slider', "In-Flow", .8, 0, 1, .1)

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
        '''
        portrayal['Shape'] = "rect"
        portrayal['Filled'] = 'true'
        portrayal['Layer'] = 2
        portrayal['Color'] = 'red'
        portrayal['w'] = 10
        portrayal['h'] = 1
        ''' 
    elif type(agent) is AZC_Viz:
        
        portrayal['Shape'] = "rect"
        portrayal['Filled'] = 'False'
        portrayal['Layer'] = 1
        portrayal['Color'] = 'red'
        portrayal['w'] = 10
        portrayal['h'] = agent.value
    

    
    elif type(agent) is AZC:
        
        portrayal['Shape'] = "rect"
        portrayal['Filled'] = 'False'
        portrayal['Layer'] = 0
        portrayal['Color'] = 'blue'
        portrayal['w'] = 10
        portrayal['h'] = 20
        
    elif type(agent) is Hotel:
        
        portrayal['Shape'] = "circle"
        portrayal['Filled'] = 'true'
        portrayal['Layer'] = 0
        portrayal['Color'] = 'green'
        portrayal['r'] = 10
        
    elif type(agent) is Empty:
        
        portrayal['Shape'] = "circle"
        portrayal['Filled'] = 'true'
        portrayal['Layer'] = 0
        portrayal['Color'] = 'Black'
        portrayal['r'] = 10
        
        
    


        
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
                       {"shock_period" : shock_period, "shock_duration" : shock_duration,
                        "shock_rate" : shock_rate, "N_cities": num_cities, "N_a": num_azc,
                        "nc_rate" : nc_rate, "width": grid_width, "height": grid_height})

