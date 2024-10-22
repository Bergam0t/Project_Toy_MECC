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
    """Create the figure for single model visualization"""
    fig = make_subplots(
        rows=2, 
        cols=2,
        subplot_titles=(
            'Population Changes Over Time',
            'Interventions and Quit Attempts',
            'Current Population Distribution',
            'Success Metrics'
        ),
        specs=[[{}, {}], [{}, {}]],
        row_heights=[0.6, 0.4]
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
    
    # Interventions and Quit Attempts over time
    fig.add_trace(
        go.Scatter(
            x=results.index[:step+1], 
            y=results['Total Interventions'][:step+1], 
            name="Interventions", 
            line=dict(color="blue")
        ),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(
            x=results.index[:step+1], 
            y=results['Total Quit Attempts'][:step+1], 
            name="Quit Attempts", 
            line=dict(color="purple")
        ),
        row=1, col=2
    )
    
    # Current Population Distribution (Bar Chart)
    current_smoking = results['Total Smoking'].iloc[step]
    current_not_smoking = results['Total Not Smoking'].iloc[step]
    
    fig.add_trace(
        go.Bar(
            x=['Current Distribution'],
            y=[current_smoking],
            name='Smoking',
            marker_color='red'
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(
            x=['Current Distribution'],
            y=[current_not_smoking],
            name='Not Smoking',
            marker_color='green'
        ),
        row=2, col=1
    )
    
    # Success Metrics
    current_quit_attempts = results['Total Quit Attempts'].iloc[step]
    current_interventions = results['Total Interventions'].iloc[step]
    avg_days_smoke_free = results['Average Days Smoke Free'].iloc[step]
    
    fig.add_trace(
        go.Bar(
            x=['Quit Attempts', 'Interventions', 'Avg Days Smoke Free'],
            y=[current_quit_attempts, current_interventions, avg_days_smoke_free],
            marker_color=['purple', 'blue', 'orange']
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
    fig.update_yaxes(title_text="Number of Agents", row=1, col=1)
    fig.update_yaxes(title_text="Number of Events", row=1, col=2)
    fig.update_yaxes(title_text="Number of Agents", row=2, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=2)
    
    return fig

def create_comparison_figure(results_no_mecc, results_mecc, step):
    """Create side-by-side comparison figures"""
    fig = make_subplots(
        rows=2, 
        cols=2,
        subplot_titles=(
            'Without MECC Training',
            'With MECC Training',
            'Intervention Effectiveness',
            'Quit Success Comparison'
        ),
        specs=[[{}, {}], [{"colspan": 2}, None]],
        row_heights=[0.6, 0.4]
    )
    
    # Population changes over time - Without MECC
    fig.add_trace(
        go.Scatter(
            x=results_no_mecc.index[:step+1], 
            y=results_no_mecc['Total Smoking'][:step+1], 
            name="Smoking (No MECC)", 
            line=dict(color="red", dash='solid')
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=results_no_mecc.index[:step+1], 
            y=results_no_mecc['Total Not Smoking'][:step+1], 
            name="Not Smoking (No MECC)", 
            line=dict(color="green", dash='solid')
        ),
        row=1, col=1
    )
    
    # Population changes over time - With MECC
    fig.add_trace(
        go.Scatter(
            x=results_mecc.index[:step+1], 
            y=results_mecc['Total Smoking'][:step+1], 
            name="Smoking (MECC)", 
            line=dict(color="red", dash='dot')
        ),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(
            x=results_mecc.index[:step+1], 
            y=results_mecc['Total Not Smoking'][:step+1], 
            name="Not Smoking (MECC)", 
            line=dict(color="green", dash='dot')
        ),
        row=1, col=2
    )
    
    # Comparative metrics
    current_interventions_no_mecc = results_no_mecc['Total Interventions'].iloc[step]
    current_interventions_mecc = results_mecc['Total Interventions'].iloc[step]
    current_quit_attempts_no_mecc = results_no_mecc['Total Quit Attempts'].iloc[step]
    current_quit_attempts_mecc = results_mecc['Total Quit Attempts'].iloc[step]
    
    success_rate_no_mecc = (results_no_mecc['Total Not Smoking'].iloc[step] / 
                           current_quit_attempts_no_mecc * 100 if current_quit_attempts_no_mecc > 0 else 0)
    success_rate_mecc = (results_mecc['Total Not Smoking'].iloc[step] / 
                        current_quit_attempts_mecc * 100 if current_quit_attempts_mecc > 0 else 0)
    
    comparison_data = {
        'Metric': ['Total Interventions', 'Quit Attempts', 'Success Rate (%)'],
        'No MECC': [current_interventions_no_mecc, current_quit_attempts_no_mecc, success_rate_no_mecc],
        'With MECC': [current_interventions_mecc, current_quit_attempts_mecc, success_rate_mecc]
    }
    
    for i, metric in enumerate(['Total Interventions', 'Quit Attempts', 'Success Rate (%)']):
        fig.add_trace(
            go.Bar(
                name='No MECC',
                x=[metric],
                y=[comparison_data['No MECC'][i]],
                marker_color='lightblue'
            ),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(
                name='With MECC',
                x=[metric],
                y=[comparison_data['With MECC'][i]],
                marker_color='darkblue'
            ),
            row=2, col=1
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
    fig.update_xaxes(title_text="Metrics", row=2, col=1)
    
    return fig

st.title("Enhanced Smoking Cessation Model with MECC Training")

# Sidebar parameters
with st.sidebar:
    st.markdown("#### Population Parameters")
    num_people = st.slider("Number of People", 5, 100, 50)
    initial_smoking_prob = st.slider("Initial Smoking Probability", 0.0, 1.0, 0.5)
    quit_attempt_prob = st.slider("Base Quit Attempt Probability", 0.0, 0.5, 0.1)
    
    st.markdown("#### Primary Care Parameters")
    num_care = st.slider("Number of Primary Care Providers", 1, 20, 5)
    care_persuasiveness = st.slider("Base Provider Persuasiveness", 0.0, 1.0, 0.3)
    intervention_radius = st.slider("Intervention Radius", 1, 5, 2)
    
    st.markdown("#### Simulation Parameters")
    num_steps = st.slider("Number of Steps to Simulate", 10, 200, 100)
    animation_speed = st.slider("Animation Speed (seconds)", 0.1, 2.0, 0.5)

    mecc_training = st.checkbox("Enable MECC Training Comparison", value=False)

# Initialize placeholder for the chart
chart_placeholder = st.empty()

# Run simulation button
if st.button("Run Simulation"):
    if mecc_training:
        # Initialize both models
        model_no_mecc =  Enhanced_Persuasion_Model(  
            N_people=num_people,
            N_care=num_care,
            initial_smoking_prob=initial_smoking_prob,
            width=10,
            height=10,
            care_persuasiveness=care_persuasiveness,
            intervention_radius=intervention_radius,
            quit_attempt_prob=quit_attempt_prob,
            mecc_trained=False
        )
        
        model_mecc =  Enhanced_Persuasion_Model(  
            N_people=num_people,
            N_care=num_care,
            initial_smoking_prob=initial_smoking_prob,
            width=10,
            height=10,
            care_persuasiveness=care_persuasiveness,
            intervention_radius=intervention_radius,
            quit_attempt_prob=quit_attempt_prob,
            mecc_trained=True
        )

        
        # Initialize progress bar
        progress_bar = st.progress(0)
        
        # Initialize data storage
        data_no_mecc = pd.DataFrame()
        data_mecc = pd.DataFrame()
        
        # Run simulation step by step
        for step in range(num_steps):
            progress = (step + 1) / num_steps
            progress_bar.progress(progress)
            
            # Run both models
            data_no_mecc = run_simulation_step(model_no_mecc)
            data_mecc = run_simulation_step(model_mecc)
            
            # Create comparison figure
            fig = create_comparison_figure(data_no_mecc, data_mecc, step)
            
            with chart_placeholder:
                st.plotly_chart(fig, use_container_width=True)
            
            time.sleep(animation_speed)
        
        # Display final statistics
        st.markdown("### Final Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Smoking Reduction (No MECC)", 
                f"{(data_no_mecc['Total Not Smoking'].iloc[-1] / num_people * 100):.1f}%",
                f"{(data_no_mecc['Total Not Smoking'].iloc[-1] - data_no_mecc['Total Not Smoking'].iloc[0]):.0f}"
            )
        
        with col2:
            st.metric(
                "Smoking Reduction (With MECC)", 
                f"{(data_mecc['Total Not Smoking'].iloc[-1] / num_people * 100):.1f}%",
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
                f"{(mecc_improvement / num_people * 100):.1f}%"
            )

        # Display detailed data
        with st.expander("View Raw Data"):
            tab1, tab2 = st.tabs(["Without MECC", "With MECC"])
            with tab1:
                st.dataframe(data_no_mecc)
            with tab2:
                st.dataframe(data_mecc)
    
    else:
        # Single model simulation (without comparison)
        model = Enhanced_Persuasion_Model(
            N_people=num_people,
            N_care=num_care,
            initial_smoking_prob=initial_smoking_prob,
            width=10,
            height=10,
            care_persuasiveness=care_persuasiveness,
            intervention_radius=intervention_radius,
            quit_attempt_prob=quit_attempt_prob,
            mecc_trained=False
        )
        
        # Initialize progress bar
        progress_bar = st.progress(0)
        
        # Run simulation step by step
        for step in range(num_steps):
            progress = (step + 1) / num_steps
            progress_bar.progress(progress)
            
            data = run_simulation_step(model)
            
            # Create and update the figure
            fig = create_figure(data, step)  # You'll need to implement this for single model view
            
            with chart_placeholder:
                st.plotly_chart(fig, use_container_width=True)
            
            time.sleep(animation_speed)
        
        # Display final statistics
        st.markdown("### Final Statistics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Final Smoking Rate", 
                f"{(data['Total Smoking'].iloc[-1] / num_people * 100):.1f}%",
                f"{(data['Total Smoking'].iloc[-1] - data['Total Smoking'].iloc[0]):.0f}"
            )
        
        with col2:
            st.metric(
                "Quit Attempts",
                f"{data['Total Quit Attempts'].iloc[-1]:.0f}",
                f"{data['Total Interventions'].iloc[-1]:.0f} interventions"
            )
        
        # Display raw data
        with st.expander("View Raw Data"):
            st.dataframe(data)

    # Success message
    st.success("Simulation completed!")
