# server.py
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import HumanitarianLogistics, AZC, Newcomer, Hotel, Empty, AZC_Viz, COA, IND
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.ModularVisualization import VisualizationElement
from SimpleContinuousModule import SimpleCanvas
import numpy as np

canvas_width = 400
canvas_height = 600
num_pol = 2

azc_display_size = 20

st = UserSettableParameter('slider', 'Self-Transcendence', 45,0,100,5)
se = UserSettableParameter('slider', 'Self-Enhancement', 65,0,100, 5)
c = UserSettableParameter('slider', 'Conservatism', 46, 0, 100, 5)
otc = UserSettableParameter('slider', 'Openness-to-Change',64,0,100, 5)


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
        if agent.under_construction:
            portrayal['Color'] = 'green'
        else:
            portrayal['Color'] = 'red'
        
        portrayal['r'] = int(agent.occupancy*azc_display_size / agent.capacity)
        
        
    elif type(agent) is Hotel:
        pass
        '''
        portrayal['Shape'] = "circle"
        portrayal['Filled'] = 'false'
        portrayal['Layer'] = 0
        portrayal['Color'] = 'green'
        portrayal['r'] = azc_display#int(agent.city.public_opinion * azc_display_size)
        portrayal['text'] = agent.occupancy
        portrayal['text_color'] = 'black'
        '''
    return portrayal

chart_suces = ChartModule([{'Label' : 'Syria',
                            'Color' : 'blue'},
                          {'Label' : 'Iraq',
                            'Color' : 'red'},
                          {'Label' : 'Eritrea',
                            'Color' : 'black'},
                          {'Label' : 'Afghanistan',
                            'Color' : 'yellow'},],
                            data_collector_name = 'sr')

chart_azc = ChartModule([{'Label': 'AZC',
                          'Color': 'black'},
                          {'Label': 'AZC',
                          'Color': 'black'},
                           {'Label': 'AZC',
                          'Color': 'black'},
                            {'Label': 'AZC',
                          'Color': 'black'},
                            {'Label': 'AZC',
                          'Color': 'black'},
                            {'Label': 'AZC',
                          'Color': 'black'},],data_collector_name = 'azc_health')

continuous_canvas = SimpleCanvas(agent_portrayal, canvas_width, canvas_height)

chart_modality_occupancy = ChartModule([{'Label': 'AZC',
                                         'Color': 'black'},
                                         {'Label': 'POL',
                                         'Color': 'blue'},
                                         {'Label': 'COL',
                                         'Color': 'red'}], data_collector_name = 'modality_occ')

chart_modality_staff = ChartModule([{'Label': 'AZC',
                                 'Color': 'black'},
                                 {'Label': 'POL',
                                 'Color': 'blue'},
                                 {'Label': 'COL',
                                 'Color': 'red'}], data_collector_name = 'staff_dc')

chart_modality_po = ChartModule([{'Label': 'AZC',
                                 'Color': 'black'},
                                 {'Label': 'POL',
                                 'Color': 'blue'},
                                 {'Label': 'COL',
                                 'Color': 'red'}], data_collector_name = 'po_dc')

chart_cm = ChartModule([{'Label': 'TP',
                         'Color': 'black'},
                        {'Label': 'TN',
                         'Color': 'blue'},
                        {'Label': 'FP',
                         'Color': 'red'},
                         {'Label': 'FN',
                         'Color': 'yellow'}], data_collector_name = 'cm_dc')
                          



chart_ls = ChartModule([{'Label': 'edp',
                                 'Color': 'black'},
                                 {'Label': 'as',
                                 'Color': 'blue'},
                                 {'Label': 'as_ext',
                                 'Color': 'red'},
                                  {'Label': 'tr',
                                   'Color': 'yellow'}], data_collector_name = 'ls_dc')

chart_network = ChartModule([{'Label': 'edp',
                                 'Color': 'black'},
                                 {'Label': 'as',
                                 'Color': 'blue'},
                                 {'Label': 'as_ext',
                                 'Color': 'red'},
                                  {'Label': 'tr',
                                   'Color': 'yellow'}], data_collector_name = 'network_dc')

test = [se,st,c,otc]


server = ModularServer(HumanitarianLogistics,
                       [continuous_canvas,  chart_modality_occupancy, chart_modality_staff],
                       "Humanitarian Logistics",
                       {"width": canvas_width, "height": canvas_height, "num_pols": num_pol, 
                        "city_size": azc_display_size, 'se': se,'st': st,'c': c,'otc': otc})

