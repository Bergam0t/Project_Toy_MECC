## alcohol_mecc_model.py
import subprocess
import pandas as pd
import numpy as np
import streamlit as st
import time
from streamlit_model_functions import run_simulation_step, create_MECC_model,create_population_figure,create_intervention_figure,create_metrics_figure
import os
import shutil
import json
from alcohol_agents import Alcohol_MECC_Model

N_people = 10
seed = 0

contemplation_intervention =  { 'Job Centre': 0.2
                    ,'Benefits Office': 0.1
                    ,'Housing Officer': 0.1
                    ,'Community Hub': 0.1}

preparation_intervention =  { 'Job Centre': 0.2
                    ,'Benefits Office': 0.1
                    ,'Housing Officer': 0.1
                    ,'Community Hub': 0.2}

action_intervention =  { 'Job Centre': 0.1
                    ,'Benefits Office': 0.1
                    ,'Housing Officer': 0.1
                    ,'Community Hub': 0.2 }

mecc_effect =  { 'Job Centre': 0.2
                    ,'Benefits Office': 0.2
                    ,'Housing Officer': 0.5
                    ,'Community Hub': 0.9 }

base_make_intervention_prob =  { 'Job Centre': 0.0
                    ,'Benefits Office': 0.0
                    ,'Housing Officer': 0.0
                    ,'Community Hub': 0.0 }

mecc_trained =  { 'Job Centre': True
                    ,'Benefits Office': False
                    ,'Housing Officer': True
                    ,'Community Hub': True}

change_prob_contemplation = 0.1
change_prob_preparation = 0.1
change_prob_action = 0.1

lapse_prob_precontemplation = 0.1
lapse_prob_contemplation = 0.1
lapse_prob_preparation = 0.5

visit_prob  =    { 'Job Centre': 0.8
                    ,'Benefits Office': 0.2
                    ,'Housing Officer': 0.2
                    ,'Community Hub': 0.1}

model = Alcohol_MECC_Model(
                 N_people 
                #, N_service
                , seed

                ## dictionaries of intervention chance
                 , contemplation_intervention
                 , preparation_intervention
                 , action_intervention

                 ## change state probability
                 , change_prob_contemplation
                 , change_prob_preparation
                 , change_prob_action

                 , lapse_prob_precontemplation
                 , lapse_prob_contemplation
                 , lapse_prob_preparation

                ## visit probability
                 , visit_prob

                ## site properties
                , mecc_effect
                , base_make_intervention_prob
                , mecc_trained
)

for step in range(20):
    if step == 20 - 1:
        print("Simulation Completed!")
    else:
        progress = (step + 1) / 20
        print(f"{progress*100}%")
    data_model = run_simulation_step(model)