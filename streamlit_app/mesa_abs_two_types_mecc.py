## mesa_abs_two_types_mecc.py
import pandas as pd
import numpy as np
import streamlit as st
#import plotly.graph_objects as go
#from plotly.subplots import make_subplots
import time
#from model_two_types_mecc import MECC_Model 
from streamlit_model_functions import run_simulation_step, create_comparison_figure, create_MECC_model #, create_figure
#import random
import parameters


st.title("Simulate - Enhanced Smoking Cessation Model with MECC Training")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Population Parameters")
    
    st.write(f"Number of People: {st.session_state.N_people}")
    st.write(f"Initial Smoking Probability: {st.session_state.initial_smoking_prob}")
    st.write(f"Chance of Visiting a Service per Month: {st.session_state.visit_prob}")
    st.write(f"Base Quit Attempt Probability per Month: {st.session_state.quit_attempt_prob}")
    st.write(f"Base Smoking Relapse per Month: {st.session_state.base_smoke_relapse_prob}")
    st.markdown("*Relapse chance decreases over time of not smoking*")

with col2: 
    st.markdown("#### Service Parameters")
    st.write(f"Chance a Brief Intervention Made Without MECC: {st.session_state.base_make_intervention_prob}")

col3, col4 = st.columns(2)

with col3:
    st.markdown("#### MECC Parameters")
    st.write(f"Chance Making a Brief Intervention After MECC Training: {st.session_state.mecc_effect}")
    st.write(f"Effect of a Brief Intervention on Chance Making a Quit Attempt: {st.session_state.intervention_effect}")
    st.markdown("*Numbers less than 1 will decrease the probability*")

with col4:
    st.markdown("#### Simulation Parameters")
    st.write(f"Random Seed: {st.session_state.model_seed}")
    st.write(f"Number of Months to Simulate: {st.session_state.num_steps}")
    st.write(f"Animation Speed (seconds): {st.session_state.animation_speed}")

## Sidebar parameters
# with st.sidebar:
#     #mecc_training = st.checkbox("Enable MECC Training Comparison", value=False)
    
#     st.markdown("#### Population Parameters")
#     st.session_state.N_people = st.slider("Number of People", 5, 100, 50)
#     st.session_state.initial_smoking_prob = st.slider("Initial Smoking Probability", 0.0, 1.0, 0.5)
#     st.session_state.visit_prob = st.slider("Chance of Visiting a Service per Month", 0.0, 1.0, 0.1)
#     st.session_state.quit_attempt_prob = st.slider("Base Quit Attempt Probability per Month", 0.00, 1.00, 0.01)
#     st.session_state.base_smoke_relapse_prob = st.slider("Base Smoking Relapse per Month", 0.00, 1.00, 0.01)
#     st.markdown("*Replase chance decreases over time of not smoking*")

#     st.markdown("#### Service Parameters")
#     #N_service = st.slider("Number of Services", 1, 20, 5) ##not used
#     st.session_state.base_make_intervention_prob = st.slider("Chance a Brief Intervention Made Without MECC", 0.0, 1.0, 0.1)
#     #intervention_radius = st.slider("Intervention Radius", 1, 5, 2)

#     st.markdown("#### MECC Parameters")
#     st.session_state.mecc_effect = st.slider("Chance Making a Brief Intervention After MECC Training", 0.0, 1.0, 1.0)
#     st.session_state.intervention_effect = st.slider("Effect of a Brief Intervention on Chance Making a Quit Attempt", 0.0, 10.0, 1.1)
#     st.markdown("*Numbers less than 1 will decrease the probability*")

#     st.markdown("#### Simulation Parameters")
#     st.session_state.model_seed = st.number_input("Random Seed",min_value=0,max_value=None,value=42,step=1) 
#     st.session_state.num_steps = st.slider("Number of Months to Simulate", 1, 120, 24)
#     st.session_state.animation_speed = st.slider("Animation Speed (seconds)", 0.1, 2.0, 0.1)

## Dictionary to store all parameter values
model_parameters = {
    "model_seed": st.session_state.model_seed,
    "N_people": st.session_state.N_people,
    "N_service": 1, ## set to 1 as currently not used
    "initial_smoking_prob": st.session_state.initial_smoking_prob,
    "visit_prob": st.session_state.visit_prob,
    "quit_attempt_prob": st.session_state.quit_attempt_prob,
    "base_smoke_relapse_prob": st.session_state.base_smoke_relapse_prob,
    #"N_service": 1,
    "base_make_intervention_prob": st.session_state.base_make_intervention_prob,
    "mecc_effect": st.session_state.mecc_effect,
    "intervention_effect": st.session_state.intervention_effect,
    }

st.write("----") #divider


## Run simulation button
if st.button("Run Simulation"):
    #if mecc_training:
    ## Initialize both models
    model_no_mecc =  create_MECC_model(
        model_parameters = model_parameters     
        , mecc_trained=False
        )
    
    model_mecc =  create_MECC_model(
        model_parameters = model_parameters     
        , mecc_trained=True
        )

    
    ## Initialize placeholder for the success
    model_message = st.info("Simulation Running")
    #model_message
    #    st.info("Simulation Running")

    ## Initialize progress bar
    progress_bar = st.progress(0)

    ## Initialize placeholder for the chart
    chart_placeholder = st.empty()

    ## Initialize data storage
    data_no_mecc = pd.DataFrame()
    data_mecc = pd.DataFrame()
    
    ## Run simulation step by step
    for step in range(st.session_state.num_steps):
        if step == st.session_state.num_steps-1:
            model_message.success("Simulation completed!")
            progress_bar.empty()
        else:
            progress = (step + 1) / st.session_state.num_steps
            progress_bar.progress(progress)
        
        ## Run both models
        data_no_mecc = run_simulation_step(model_no_mecc)
        data_mecc = run_simulation_step(model_mecc)
        
        ## Create comparison figure
        fig = create_comparison_figure(data_no_mecc, data_mecc, step)

        with chart_placeholder:
            st.plotly_chart(fig, use_container_width=True)
        
        time.sleep(st.session_state.animation_speed)
    
    ## Display final statistics
    st.markdown("### Final Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Smoking Reduction (No MECC)", 
            f"{(data_no_mecc['Total Not Smoking'].iloc[-1] / st.session_state.N_people * 100):.1f}%",
            f"{(data_no_mecc['Total Not Smoking'].iloc[-1] - data_no_mecc['Total Not Smoking'].iloc[0]):.0f}"
        )
    
    with col2:
        st.metric(
            "Smoking Reduction (With MECC)", 
            f"{(data_mecc['Total Not Smoking'].iloc[-1] / st.session_state.N_people * 100):.1f}%",
            f"{(data_mecc['Total Not Smoking'].iloc[-1] - data_mecc['Total Not Smoking'].iloc[0]):.0f}"
        )
    
    with col3:
        mecc_improvement = (
            data_mecc['Total Not Smoking'].iloc[-1] - 
            data_no_mecc['Total Not Smoking'].iloc[-1]
        )
        st.metric(
            "MECC Impact",
            f"{mecc_improvement:.0f} additional quits",
            f"{(mecc_improvement / st.session_state.N_people * 100):.1f}%"
        )

    ## Display detailed data
    with st.expander("View Raw Data"):
        tab1, tab2 = st.tabs(["Without MECC", "With MECC"])
        with tab1:
            st.dataframe(data_no_mecc)
        with tab2:
            st.dataframe(data_mecc)
    
    # else:
    #     ## Single model simulation (without comparison)
    #     model = create_MECC_model(
    #         model_parameters = model_parameters     
    #         , mecc_trained=False
    #         )
        
    #     ## Initialize progress bar
    #     progress_bar = st.progress(0)
        
    #     ## Run simulation step by step
    #     for step in range(num_steps):
    #         progress = (step + 1) / num_steps
    #         progress_bar.progress(progress)
            
    #         data = run_simulation_step(model)
            
    #         # Create and update the figure
    #         fig = create_figure(data, step)  # You'll need to implement this for single model view
            
    #         with chart_placeholder:
    #             st.plotly_chart(fig, use_container_width=True)
            
    #         time.sleep(animation_speed)
        
    #     ## Display final statistics
    #     st.markdown("### Final Statistics")
    #     col1, col2 = st.columns(2)
        
    #     with col1:
    #         st.metric(
    #             "Final Smoking Rate", 
    #             f"{(data['Total Smoking'].iloc[-1] / N_people * 100):.1f}%",
    #             f"{(data['Total Smoking'].iloc[-1] - data['Total Smoking'].iloc[0]):.0f}"
    #         )
        
    #     with col2:
    #         st.metric(
    #             "Quit Attempts",
    #             f"{data['Total Quit Attempts'].iloc[-1]:.0f}",
    #             f"{data['Total Interventions'].iloc[-1]:.0f} interventions"
    #         )
        
    #    ## Display raw data
    #    with st.expander("View Raw Data"):
    #        st.dataframe(data)

    ## Success message
    st.success("Simulation completed!")