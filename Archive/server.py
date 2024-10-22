# server.py
from model import Persuasion_Model
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule

def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "r": 0.5,
        "Layer": 0,
    }
    
    if agent.smoker:
        portrayal["Color"] = "green"
    else:
        portrayal["Color"] = "red"
        
    return portrayal

# Create a grid of 10x10 cells, and display it as 500x500 pixels
grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)

# Create a chart for showing the number of smokers vs non-smokers
chart = ChartModule([
    {"Label": "Total Smoking", "Color": "Red"},
    {"Label": "Total Not Smoking", "Color": "Green"}
],
    data_collector_name='datacollector'
)

# Define the model parameters with simpler structure
model_params = {
    "N": 20,
    "initial_smoking_prob": 0.5,
    "width": 10,
    "height": 10,
    "persuasiveness_max": 1.0
}

server = ModularServer(
    Persuasion_Model,
    [grid, chart],
    "Smoking Persuasion Model",
    model_params
)

server.port = 8521
server.launch()