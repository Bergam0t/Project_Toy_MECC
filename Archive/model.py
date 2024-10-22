# model.py
import mesa
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random

class PersuasionAgent(Agent):
    def __init__(self, unique_id, model, initial_smoking_prob, persuasiveness_max):
        super().__init__(unique_id, model)
        
        if random.uniform(0, 1) < initial_smoking_prob:
            self.smoker = True
        else:
            self.smoker = False
            
        self.persuasiveness = random.uniform(0.0, persuasiveness_max)
        
    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False)
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def talk(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            for inhabitant in cellmates:
                if inhabitant.smoker != self.smoker:
                    if random.uniform(0, 1) < self.persuasiveness:
                        inhabitant.smoker = self.smoker

    def step(self):
        if random.choice([True, False]):
            self.move()
        self.talk()

class Persuasion_Model(Model):
    def __init__(self, N, initial_smoking_prob, width, height, persuasiveness_max):
        # Extract values from parameter dictionaries if they are dictionaries
        self.num_agents = N['value'] if isinstance(N, dict) else N
        self.initial_smoking_prob = initial_smoking_prob['value'] if isinstance(initial_smoking_prob, dict) else initial_smoking_prob
        self.width = width
        self.height = height
        self.persuasiveness_max = persuasiveness_max['value'] if isinstance(persuasiveness_max, dict) else persuasiveness_max
        
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(self.width, self.height, True)
        
        self.datacollector = DataCollector(
            model_reporters={
                "Total Smoking": calculate_number_smoking,
                "Total Not Smoking": calculate_number_not_smoking
            },
            agent_reporters={}
        )
        
        # Create agents
        for i in range(self.num_agents):
            a = PersuasionAgent(i, self, self.initial_smoking_prob, self.persuasiveness_max)
            self.schedule.add(a)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

def calculate_number_smoking(model):
    return sum(1 for agent in model.schedule.agents if agent.smoker)

def calculate_number_not_smoking(model):
    return sum(1 for agent in model.schedule.agents if not agent.smoker)