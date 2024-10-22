# model_two_types_mecc.py
import mesa
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random

class PersonAgent(Agent):
    def __init__(self, unique_id, model, initial_smoking_prob, quit_attempt_prob):
        super().__init__(unique_id, model)
        self.smoker = random.uniform(0, 1) < initial_smoking_prob
        self.quit_attempts = 0
        self.days_smoke_free = 0
        self.quit_attempt_prob = quit_attempt_prob
        
    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False)
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
    
    def attempt_quit(self):
        if self.smoker and random.uniform(0, 1) < self.quit_attempt_prob:
            self.smoker = False
            self.quit_attempts += 1
            self.days_smoke_free = 0
    
    def update_smoking_status(self):
        if not self.smoker:
            self.days_smoke_free += 1
            recidivism_prob = 0.1 * (0.95 ** self.days_smoke_free)
            if random.uniform(0, 1) < recidivism_prob:
                self.smoker = True
                self.days_smoke_free = 0

    def step(self):
        self.move()
        self.attempt_quit()
        self.update_smoking_status()

class PrimaryCareAgent(Agent):
    def __init__(self, unique_id, model, base_persuasiveness, intervention_radius, mecc_trained=False):
        super().__init__(unique_id, model)
        self.base_persuasiveness = base_persuasiveness
        self.mecc_trained = mecc_trained
        self.intervention_radius = intervention_radius
        self.interventions_made = 0
        
    @property
    def persuasiveness(self):
        return self.base_persuasiveness * (1.3 if self.mecc_trained else 1.0)
        
    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False)
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
    
    def provide_intervention(self):
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, radius=self.intervention_radius)
        
        for neighbor in neighbors:
            if isinstance(neighbor, PersonAgent) and neighbor.smoker:
                if random.uniform(0, 1) < self.persuasiveness:
                    neighbor.quit_attempt_prob *= 1.5
                    self.interventions_made += 1
    
    def step(self):
        self.move()
        self.provide_intervention()

class MECC_Model(Model):  # Renamed from Enhanced_Persuasion_Model
    def __init__(self, N_people, N_care, initial_smoking_prob, width, height, 
                 care_persuasiveness, intervention_radius, quit_attempt_prob, mecc_trained=False):
        super().__init__()  # Properly initialize the Model class
        # Convert dictionary values if they're dictionaries
        self.num_people = N_people['value'] if isinstance(N_people, dict) else N_people
        self.num_care = N_care['value'] if isinstance(N_care, dict) else N_care
        self.initial_smoking_prob = initial_smoking_prob['value'] if isinstance(initial_smoking_prob, dict) else initial_smoking_prob
        self.width = width
        self.height = height
        self.care_persuasiveness = care_persuasiveness['value'] if isinstance(care_persuasiveness, dict) else care_persuasiveness
        self.intervention_radius = intervention_radius['value'] if isinstance(intervention_radius, dict) else intervention_radius
        self.quit_attempt_prob = quit_attempt_prob['value'] if isinstance(quit_attempt_prob, dict) else quit_attempt_prob
        self.mecc_trained = mecc_trained
        
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(self.width, self.height, True)
        
        self.datacollector = DataCollector(
            model_reporters={
                "Total Smoking": calculate_number_smoking,
                "Total Not Smoking": calculate_number_not_smoking,
                "Total Quit Attempts": calculate_total_quit_attempts,
                "Total Interventions": calculate_total_interventions,
                "Average Days Smoke Free": calculate_average_days_smoke_free
            },
            agent_reporters={}
        )
        
        # Create person agents
        for i in range(self.num_people):
            a = PersonAgent(i, self, self.initial_smoking_prob, self.quit_attempt_prob)
            self.schedule.add(a)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
            
        # Create primary care agents
        for i in range(self.num_care):
            a = PrimaryCareAgent(i + self.num_people, self, 
                               self.care_persuasiveness, 
                               self.intervention_radius,
                               self.mecc_trained)
            self.schedule.add(a)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

def calculate_number_smoking(model):
    return sum(1 for agent in model.schedule.agents 
              if isinstance(agent, PersonAgent) and agent.smoker)

def calculate_number_not_smoking(model):
    return sum(1 for agent in model.schedule.agents 
              if isinstance(agent, PersonAgent) and not agent.smoker)

def calculate_total_quit_attempts(model):
    return sum(agent.quit_attempts for agent in model.schedule.agents 
              if isinstance(agent, PersonAgent))

def calculate_total_interventions(model):
    return sum(agent.interventions_made for agent in model.schedule.agents 
              if isinstance(agent, PrimaryCareAgent))

def calculate_average_days_smoke_free(model):
    smoke_free_days = [agent.days_smoke_free for agent in model.schedule.agents 
                      if isinstance(agent, PersonAgent) and not agent.smoker]
    return sum(smoke_free_days) / len(smoke_free_days) if smoke_free_days else 0