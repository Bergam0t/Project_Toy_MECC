import pandas as pd
import numpy as np
import streamlit as st
from model import Persuasion_Model
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
        cols=1,
        subplot_titles=(
            'Population Changes Over Time',
            'Current Population Distribution'
        ),
        row_heights=[0.7, 0.3]
    )
    
    # Line plot for population over time
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
    
    # Get current values for the bar chart
    current_smoking = results['Total Smoking'].iloc[step]
    current_not_smoking = results['Total Not Smoking'].iloc[step]
    
    # Horizontal stacked bar chart for current distribution
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
    
    # Update layout
    fig.update_layout(
        height=800,
        showlegend=True,
        barmode='stack',
        yaxis2=dict(showticklabels=False)
    )
    
    # Update x-axes labels
    fig.update_xaxes(title_text="Time Step", row=1, col=1)
    fig.update_xaxes(title_text="Number of Agents", row=2, col=1)
    
    return fig

st.title("Smoking Persuasion Model Simulation")

# Sidebar parameters
with st.sidebar:
    st.markdown("#### Simulation Parameters")
    num_agents = st.slider("Number of Agents", 5, 50, 20)
    initial_smoking_prob = st.slider("Initial Smoking Probability", 0.0, 1.0, 0.5)
    persuasiveness_max = st.slider("Maximum Persuasiveness", 0.0, 1.0, 1.0)
    num_steps = st.slider("Number of Steps to Simulate", 10, 100, 50)
    animation_speed = st.slider("Animation Speed (seconds per step)", 0.1, 2.0, 0.5)

# Main content
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Model Description")
    st.write("""
    This agent-based model simulates the spread of smoking behavior through social interaction. 
    Agents move randomly on a grid and can influence others based on their persuasiveness level.
    """)

# Initialize placeholder for the chart
chart_placeholder = st.empty()

# Run simulation button
if st.button("Run Simulation"):
    # Initialize the model
    model = Persuasion_Model(
        N=num_agents,
        initial_smoking_prob=initial_smoking_prob,
        width=10,
        height=10,
        persuasiveness_max=persuasiveness_max
    )
    
    # Initialize progress bar
    progress_bar = st.progress(0)
    
    # Run simulation step by step
    for step in range(num_steps):
        # Update progress bar
        progress = (step + 1) / num_steps
        progress_bar.progress(progress)
        
        # Run one step and get data
        data = run_simulation_step(model)
        
        # Create and update the figure
        fig = create_figure(data, step)
        
        # Update the chart
        with chart_placeholder:
            st.plotly_chart(fig, use_container_width=True)
        
        # Add delay for animation
        time.sleep(animation_speed)
    
    # Display final raw data
    with st.expander("View Raw Data"):
        st.dataframe(data)
    
    # Success message
    st.success("Simulation completed!")