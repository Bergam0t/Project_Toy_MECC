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

st.title("Enhanced Smoking Cessation Model with MECC Training")

## Sidebar parameters
with st.sidebar:
    #mecc_training = st.checkbox("Enable MECC Training Comparison", value=False)
    
    st.markdown("#### Population Parameters")
    N_people = st.slider("Number of People", 5, 100, 50)
    initial_smoking_prob = st.slider("Initial Smoking Probability", 0.0, 1.0, 0.5)
    visit_prob = st.slider("Chance of Visiting a Service per Month", 0.0, 1.0, 0.1)
    quit_attempt_prob = st.slider("Base Quit Attempt Probability per Month", 0.00, 1.00, 0.01)
    base_smoke_relapse_prob = st.slider("Base Smoking Relapse per Month", 0.00, 1.00, 0.01)
    st.markdown("*Replase chance decreases over time of not smoking*")

    st.markdown("#### Service Parameters")
    #N_service = st.slider("Number of Services", 1, 20, 5) ##not used
    base_make_intervention_prob = st.slider("Chance a Brief Intervention Made Without MECC", 0.0, 1.0, 0.1)
    #intervention_radius = st.slider("Intervention Radius", 1, 5, 2)

    st.markdown("#### MECC Parameters")
    mecc_effect = st.slider("Chance Making a Brief Intervention After MECC Training", 0.0, 1.0, 1.0)
    intervention_effect = st.slider("Effect of a Brief Intervention on Chance Making a Quit Attempt", 0.0, 10.0, 1.1)
    st.markdown("*Numbers less than 1 will decrease the probability*")

    st.markdown("#### Simulation Parameters")
    model_seed = st.number_input("Random Seed",min_value=0,max_value=None,value=42,step=1) 
    num_steps = st.slider("Number of Months to Simulate", 1, 120, 24)
    animation_speed = st.slider("Animation Speed (seconds)", 0.1, 2.0, 0.1)

## Dictionary to store all parameter values
model_parameters = {
    "model_seed": model_seed,
    "N_people": N_people,
    "N_service": 1, ## set to 1 as currently not used
    "initial_smoking_prob": initial_smoking_prob,
    "visit_prob": visit_prob,
    "quit_attempt_prob": quit_attempt_prob,
    "base_smoke_relapse_prob": base_smoke_relapse_prob,
    #"N_service": 1,
    "base_make_intervention_prob": base_make_intervention_prob,
    "mecc_effect": mecc_effect,
    "intervention_effect": intervention_effect,
    }

   


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
    for step in range(num_steps):
        if step == num_steps-1:
            model_message.success("Simulation completed!")
            progress_bar.empty()
        else:
            progress = (step + 1) / num_steps
            progress_bar.progress(progress)
        
        ## Run both models
        data_no_mecc = run_simulation_step(model_no_mecc)
        data_mecc = run_simulation_step(model_mecc)
        
        ## Create comparison figure
        fig = create_comparison_figure(data_no_mecc, data_mecc, step)

        with chart_placeholder:
            st.plotly_chart(fig, use_container_width=True)
        
        time.sleep(animation_speed)
    
    ## Display final statistics
    st.markdown("### Final Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Smoking Reduction (No MECC)", 
            f"{(data_no_mecc['Total Not Smoking'].iloc[-1] / N_people * 100):.1f}%",
            f"{(data_no_mecc['Total Not Smoking'].iloc[-1] - data_no_mecc['Total Not Smoking'].iloc[0]):.0f}"
        )
    
    with col2:
        st.metric(
            "Smoking Reduction (With MECC)", 
            f"{(data_mecc['Total Not Smoking'].iloc[-1] / N_people * 100):.1f}%",
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
            f"{(mecc_improvement / N_people * 100):.1f}%"
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