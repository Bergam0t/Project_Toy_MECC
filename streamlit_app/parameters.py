## mesa_abs_two_types_mecc.py
import pandas as pd
import numpy as np
import streamlit as st
#import plotly.graph_objects as go
#from plotly.subplots import make_subplots
import time
from logic_diagram import create_logic_diagram, create_logic_diagram_SmokeModel
#from model_two_types_mecc import MECC_Model 
#from streamlit_model_functions import run_simulation_step, create_comparison_figure, create_MECC_model #, create_figure
#import random

st.title("Parameters")

tab1, tab2 = st.tabs(['Generic','Smoking Cessation'])

with tab1:
    st.markdown("### Generic Parameters")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Population")

        if 'N_people' not in st.session_state:
            st.session_state.N_people = 50
        st.session_state.N_people = st.slider("Number of People", 5, 100, st.session_state.N_people)

        if 'visit_prob' not in st.session_state:
            st.session_state.visit_prob = 0.1
        st.session_state.visit_prob = st.slider("Chance of Visiting a Service per Month", 0.0, 1.0, st.session_state.visit_prob)

    with col2:
        st.markdown("#### Service")

        if 'base_make_intervention_prob' not in st.session_state:
            st.session_state.base_make_intervention_prob = 0.1
        st.session_state.base_make_intervention_prob = st.slider("Chance a Brief Intervention Made Without MECC", 0.0, 1.0, st.session_state.base_make_intervention_prob)

        st.write("-----") #divider

        st.markdown("#### MECC")

        if 'mecc_effect' not in st.session_state:
            st.session_state.mecc_effect = 0.9
        st.session_state.mecc_effect = st.slider("Chance Making a Brief Intervention After MECC Training", 0.0, 1.0, st.session_state.mecc_effect)

    with col3:
        st.markdown("#### Simulation")

        if 'model_seed' not in st.session_state:
            st.session_state.model_seed = 42
        st.session_state.model_seed = st.number_input("Random Seed", min_value=0, max_value=None, value=st.session_state.model_seed, step=1)

        if 'num_steps' not in st.session_state:
            st.session_state.num_steps = 24
        st.session_state.num_steps = st.slider("Number of Months to Simulate", 1, 120, st.session_state.num_steps)

        if 'animation_speed' not in st.session_state:
            st.session_state.animation_speed = 0.1
        st.session_state.animation_speed = st.slider("Animation Speed (seconds)", 0)

    ## Logic Diagram
    with st.expander("Click here to view the logic diagram"):
        col1a, col2a, col3a = st.columns(3)
        with col2a:
            st.image(create_logic_diagram()
                , caption="Diagram of Agent Model Logic"
                , use_column_width=False)

with tab2:
    st.markdown("### Smoking Cessation Parameters")

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("#### Population")

        st.write(f"Number of People: :blue-background[{st.session_state.N_people}]") 

        st.write(f"Chance of Visiting a Service per Month: :blue-background[{st.session_state.visit_prob}]")

        if 'initial_smoking_prob' not in st.session_state:
            st.session_state.initial_smoking_prob = 0.5
        st.session_state.initial_smoking_prob = st.slider("Initial Smoking Probability", 0.0, 1.0, st.session_state.initial_smoking_prob)

        if 'quit_attempt_prob' not in st.session_state:
            st.session_state.quit_attempt_prob = 0.01
        st.session_state.quit_attempt_prob = st.slider("Base Quit Attempt Probability per Month", 0.00, 1.00, st.session_state.quit_attempt_prob)

        if 'base_smoke_relapse_prob' not in st.session_state:
            st.session_state.base_smoke_relapse_prob = 0.01
        st.session_state.base_smoke_relapse_prob = st.slider("Base Smoking Relapse per Month", 0.00, 1.00, st.session_state.base_smoke_relapse_prob)
        st.markdown("*Relapse chance decreases over time of not smoking*")

    with col5:
        st.markdown("#### Service")

        st.write(f"Chance a Brief Intervention Made Without MECC: :blue-background[{st.session_state.base_make_intervention_prob}]")

        if 'intervention_effect' not in st.session_state:
            st.session_state.intervention_effect = 1.1
        st.session_state.intervention_effect = st.slider("Effect of a Brief Intervention on Chance Making a Quit Attempt", 0.0, 10.0, st.session_state.intervention_effect)
        st.markdown("*Numbers less than 1 will decrease the probability*")

        st.write("-----") #divider

        st.markdown("#### MECC")
        st.write(f"Chance Making a Brief Intervention After MECC Training: :blue-background[{st.session_state.mecc_effect}]")

    with col6:
        st.markdown("#### Simulation")

        st.write(f"Random Seed: :blue-background[{st.session_state.model_seed}]")

        st.write(f"Number of Months to Simulate: :blue-background[{st.session_state.num_steps}]")

        st.write(f"Animation Speed (seconds): :blue-background[{st.session_state.animation_speed}]")

    ## Logic Diagram
    with st.expander("Click here to view the logic diagram"):
        col4a, col5a, col6a = st.columns(3)
        with col5a:
            st.image(create_logic_diagram_SmokeModel()
                , caption="Diagram of Agent Model Logic"
                , use_column_width=False)
