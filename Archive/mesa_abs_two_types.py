# mesa_abs_two_types.py
import pandas as pd
import numpy as np
import streamlit as st
from model_two_types import Enhanced_Persuasion_Model
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

def run_simulation_step(model):
    """Run one step of the simulation and return current data"""
    model.step()
    data = model.datacollector.get_model_vars_dataframe()
    return data

def create_figure(results, step):
    """Create the figure with data up to the current step"""
    fig = make_subplots(
        rows=2, 
        cols=2,
        subplot_titles=(
            'Population Smoking Status Over Time',
            'Intervention Metrics',
            'Current Population Distribution',
            'Quit Attempt Success Metrics'
        ),
        row_heights=[0.7, 0.3]
    )
    
    # Population changes over time
    fig.add_trace(
        go.Scatter(
            x=results.index[:step+1], 
            y=results['Total Smoking'][:step+1], 
            name="Smoking", 
            line=dict(color="red")
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=results.index[:step+1], 
            y=results['Total Not Smoking'][:step+1], 
            name="Not Smoking", 
            line=dict(color="green")
        ),
        row=1, col=1
    )
    
    # Intervention metrics
    fig.add_trace(
        go.Scatter(
            x=results.index[:step+1],
            y=results['Total Interventions'][:step+1],
            name="Total Interventions",
            line=dict(color="blue")
        ),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(
            x=results.index[:step+1],
            y=results['Average Days Smoke Free'][:step+1],
            name="Avg Days Smoke Free",
            line=dict(color="purple")
        ),
        row=1, col=2
    )
    
    # Current population distribution
    current_smoking = results['Total Smoking'].iloc[step]
    current_not_smoking = results['Total Not Smoking'].iloc[step]
    
    fig.add_trace(
        go.Bar(
            y=['Current Distribution'],
            x=[current_smoking],
            name='Smoking',
            orientation='h',
            marker_color='red'
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(
            y=['Current Distribution'],
            x=[current_not_smoking],
            name='Not Smoking',
            orientation='h',
            marker_color='green'
        ),
        row=2, col=1
    )
    
    # Quit attempt metrics
    current_quit_attempts = results['Total Quit Attempts'].iloc[step]
    success_rate = (current_not_smoking / current_quit_attempts * 100) if current_quit_attempts > 0 else 0
    
    fig.add_trace(
        go.Bar(
            x=['Quit Attempts', 'Successful Quits'],
            y=[current_quit_attempts, current_not_smoking],
            name='Quit Metrics',
            marker_color=['blue', 'green']
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        showlegend=True,
        barmode='group'
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="Time Step", row=1, col=1)
    fig.update_xaxes(title_text="Time Step", row=1, col=2)
    fig.update_xaxes(title_text="Number of Agents", row=2, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=2)
    
    return fig

st.title("Enhanced Smoking Cessation Model with Primary Care")

# Sidebar parameters
with st.sidebar:
    st.markdown("#### Population Parameters")
    num_people = st.slider("Number of People", 5, 100, 50)
    initial_smoking_prob = st.slider("Initial Smoking Probability", 0.0, 1.0, 0.5)
    quit_attempt_prob = st.slider("Base Quit Attempt Probability", 0.0, 0.5, 0.1)
    
    st.markdown("#### Primary Care Parameters")
    num_care = st.slider("Number of Primary Care Providers", 1, 20, 5)
    care_persuasiveness = st.slider("Provider Persuasiveness", 0.0, 1.0, 0.3)
    intervention_radius = st.slider("Intervention Radius", 1, 5, 2)
    
    st.markdown("#### Simulation Parameters")
    num_steps = st.slider("Number of Steps to Simulate", 10, 200, 100)
    animation_speed = st.slider("Animation Speed (seconds)", 0.1, 2.0, 0.5)

# Main content
st.markdown("### Model Description")
st.write("""
This enhanced agent-based model simulates smoking cessation with primary care interventions:
- People move randomly and may attempt to quit smoking
- Primary care providers move and provide interventions within their radius
- Successful quitters may relapse based on time smoke-free
- Interventions increase quit attempt probability
""")

# Initialize placeholder for the chart
chart_placeholder = st.empty()

# Run simulation button
if st.button("Run Simulation"):
    # Initialize model
    model = Enhanced_Persuasion_Model(
        N_people=num_people,
        N_care=num_care,
        initial_smoking_prob=initial_smoking_prob,
        width=10,
        height=10,
        care_persuasiveness=care_persuasiveness,
        intervention_radius=intervention_radius,
        quit_attempt_prob=quit_attempt_prob
    )
    
    # Initialize progress bar
    progress_bar = st.progress(0)
    
    # Run simulation step by step
    for step in range(num_steps):
        progress = (step + 1) / num_steps
        progress_bar.progress(progress)
        
        data = run_simulation_step(model)
        fig = create_figure(data, step)
        
        with chart_placeholder:
            st.plotly_chart(fig, use_container_width=True)
        
        time.sleep(animation_speed)
    
    # Display final statistics
    st.markdown("### Final Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Final Smoking Population", 
                 int(data['Total Smoking'].iloc[-1]))
    with col2:
        st.metric("Total Interventions", 
                 int(data['Total Interventions'].iloc[-1]))
    with col3:
        success_rate = (data['Total Not Smoking'].iloc[-1] / 
                       data['Total Quit Attempts'].iloc[-1] * 100 
                       if data['Total Quit Attempts'].iloc[-1] > 0 else 0)
        st.metric("Quit Success Rate", f"{success_rate:.1f}%")
    
    with st.expander("View Raw Data"):
        st.dataframe(data)
    
    st.success("Simulation completed!")