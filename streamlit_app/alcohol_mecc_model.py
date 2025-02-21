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

######################################################

N_people = 10
seed = 1
steps = 5

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

for step in range(steps):
    print(f"\n**Step {step}**")
    if step == steps - 1:
        print("**Simulation Completed!**")
    else:
        pass
    data_model = run_simulation_step(model)

data_model

######################################################

st.title("Simulate - Alcohol Advice Model with MECC Training")

# initialise simulation_completed session state
if 'simulation_completed' not in st.session_state:
    st.session_state.simulation_completed = False

if "download_clicked" not in st.session_state:
    st.session_state.download_clicked = False

def disable_download():
    st.session_state.download_clicked = True
    st.session_state.simulation_completed = False
    report_message.empty()


model_parameters = {
    "model_seed": st.session_state.model_seed,
    "num_steps" : st.session_state.num_steps,
    "animation_speed" : st.session_state.animation_speed,    
    "N_people": st.session_state.N_people,
    "change_prob_contemplation": st.session_state.alcohol_change_prob_contemplation,
    "change_prob_preparation":st.session_state.alcohol_change_prob_preparation,
    "change_prob_action": st.session_state.alcohol_change_prob_action,
    "lapse_prob_precontemplation": st.session_state.alcohol_lapse_prob_precontemplation,
    "lapse_prob_contemplation": st.session_state.alcohol_lapse_prob_contemplation,
    "lapse_prob_preparation": st.session_state.alcohol_lapse_prob_preparation,
    "visit_prob": st.session_state.alcohol_visit_prob,
    "base_make_intervention_prob": st.session_state.alcohol_base_make_intervention_prob,
    "mecc_trained": st.session_state.alcohol_mecc_trained,
    "mecc_effect": st.session_state.alcohol_mecc_effect,
    "contemplation_intervention": st.session_state.alcohol_contemplation_intervention,
    "preparation_intervention": st.session_state.alcohol_preparation_intervention,
    "action_intervention": st.session_state.alcohol_action_intervention,
}


tab1, tab2 = st.tabs(['Model','Parameters'])

with tab2:
    colA, colB = st.columns(2)

    with colA:
        st.markdown("#### Population Parameters")
        st.write(f" - Number of People: :blue-background[{st.session_state.N_people}]")
        st.write(f" - Base Pre-Contemplation to Contemplation chance: :blue-background[{st.session_state.alcohol_change_prob_contemplation}]")
        st.write(f" - Base Contemplation to Preparation chance: :blue-background[{st.session_state.alcohol_change_prob_preparation}]")
        st.write(f" - Base Preparation to Action chance: :blue-background[{st.session_state.alcohol_change_prob_action}]")
        st.write(f" - Base Contemplation to Pre-Contemplation lapse chance: :blue-background[{st.session_state.alcohol_lapse_prob_precontemplation}]")
        st.write(f" - Base Preparation to Contemplation lapse chance: :blue-background[{st.session_state.alcohol_lapse_prob_contemplation}]")
        st.write(f" - Base Action to Preparation lapse chance: :blue-background[{st.session_state.alcohol_lapse_prob_preparation}]")

    with colB:
        st.markdown("#### Simulation Parameters")
        st.write(f" - Random Seed: :blue-background[{st.session_state.model_seed}]")
        st.write(f" - Number of Months to Simulate: :blue-background[{st.session_state.num_steps}]")
        st.write(f" - Animation Speed (seconds): :blue-background[{st.session_state.animation_speed}]")

    st.markdown("#### Service Parameters")
    col1, col2, col3, col4 = st.columns(4)
    column_dict = { 'Job Centre': col1
                    ,'Benefits Office': col2
                    ,'Housing Officer': col3
                    ,'Community Hub': col4}
    
    for service in column_dict:
        st.write(f"{service}")
        st.write(f" - Chance of a Person Visiting per Month: :blue-background[{st.session_state.alcohol_visit_prob[service]}]")
        st.write(f" - Chance a Brief Intervention Made Without MECC Training: :blue-background[{st.session_state.alcohol_base_make_intervention_prob[service]}]")
        st.write(f" - Service has had MECC Training: :blue-background[{st.session_state.alcohol_mecc_trained[service] }]")
        if st.session_state.alcohol_mecc_trained[service]:
            st.write(f" - Chance Making a Brief Intervention After MECC Training: :blue-background[{st.session_state.alcohol_mecc_effect[service] }]")
        else:
            pass
        st.write(f" - Chance Making a Brief Intervention After MECC Training: :blue-background[{st.session_state.alcohol_mecc_effect[service] }]")
        st.write(f" - Post Intervention Pre-Contemplation to Contemplation chance: :blue-background[{st.session_state.alcohol_contemplation_intervention[service]}]")
        st.write(f" - Post Intervention Contemplation to Preparation chance: :blue-background[{st.session_state.alcohol_preparation_intervention[service]}]")
        st.write(f" - Post Intervention Preparation to Action chance: :blue-background[{st.session_state.alcohol_action_intervention[service]}]")
