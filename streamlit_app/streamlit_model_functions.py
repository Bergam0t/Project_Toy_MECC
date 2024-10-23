## streamlit_model_functions.py
#import pandas as pd
#import numpy as np
#import streamlit as st
from model_two_types_mecc import MECC_Model 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
#import time

##################################
### Model Functions
##################################

## Function to create a model
def create_MECC_model(model_parameters
                      ,mecc_trained = False):
        model = MECC_Model(
            N_people=model_parameters["N_people"],
            N_service=model_parameters["N_service"],
            initial_smoking_prob=model_parameters["initial_smoking_prob"],
            base_make_intervention_prob=model_parameters["base_make_intervention_prob"],
            quit_attempt_prob=model_parameters["quit_attempt_prob"],
            visit_prob=model_parameters["visit_prob"],
            base_smoke_relapse_prob = model_parameters["base_smoke_relapse_prob"],
            intervention_effect=model_parameters["intervention_effect"],  
            mecc_effect=model_parameters["mecc_effect"],            
            mecc_trained=mecc_trained)
        return model

## Function to run simulation steps
def run_simulation_step(model):
    """Run one step of the simulation and return current data"""
    model.step()
    data = model.datacollector.get_model_vars_dataframe()
    return data



##################################
### Output Functions
##################################

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
    avg_months_smoke_free = results['Average Months Smoke Free'].iloc[step]
    
    fig.add_trace(
        go.Bar(
            x=['Quit Attempts', 'Interventions', 'Avg Months Smoke Free'],
            y=[current_quit_attempts, current_interventions, avg_months_smoke_free],
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
        rows=3, 
        cols=2,
        subplot_titles=(
            'Without MECC Training',
            'With MECC Training',
            'Interventions & Quit Attempts (No MECC)',
            'Interventions & Quit Attempts (With MECC)',
            'Success Metrics Comparison',
            'Performance Improvement'
        ),
        specs=[[{}, {}], [{}, {}], [{}, {}]],
        row_heights=[0.4, 0.4, 0.2]
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
    
    # Interventions and Quit Attempts - Without MECC
    fig.add_trace(
        go.Scatter(
            x=results_no_mecc.index[:step+1],
            y=results_no_mecc['Total Interventions'][:step+1],
            name="Interventions (No MECC)",
            line=dict(color="blue", dash='solid')
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=results_no_mecc.index[:step+1],
            y=results_no_mecc['Total Quit Attempts'][:step+1],
            name="Quit Attempts (No MECC)",
            line=dict(color="purple", dash='solid')
        ),
        row=2, col=1
    )
    
    # Interventions and Quit Attempts - With MECC
    fig.add_trace(
        go.Scatter(
            x=results_mecc.index[:step+1],
            y=results_mecc['Total Interventions'][:step+1],
            name="Interventions (MECC)",
            line=dict(color="blue", dash='dot')
        ),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(
            x=results_mecc.index[:step+1],
            y=results_mecc['Total Quit Attempts'][:step+1],
            name="Quit Attempts (MECC)",
            line=dict(color="purple", dash='dot')
        ),
        row=2, col=2
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
    
    # Success metrics comparison
    fig.add_trace(
        go.Bar(
            x=['Interventions', 'Quit Attempts', 'Success Rate (%)'],
            y=[current_interventions_no_mecc, current_quit_attempts_no_mecc, success_rate_no_mecc],
            name='No MECC',
            marker_color='rgba(135, 206, 250, 0.8)'
        ),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=['Interventions', 'Quit Attempts', 'Success Rate (%)'],
            y=[current_interventions_mecc, current_quit_attempts_mecc, success_rate_mecc],
            name='With MECC',
            marker_color='rgba(0, 0, 139, 0.8)'
        ),
        row=3, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=1000,  # Increased height to accommodate new row
        showlegend=True,
        barmode='group'
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="Time Step", row=1, col=1)
    fig.update_xaxes(title_text="Time Step", row=1, col=2)
    fig.update_xaxes(title_text="Time Step", row=2, col=1)
    fig.update_xaxes(title_text="Time Step", row=2, col=2)
    fig.update_xaxes(title_text="Metrics", row=3, col=1)
    fig.update_xaxes(title_text="Metrics", row=3, col=2)
    
    # Update y-axes labels
    fig.update_yaxes(title_text="Number of Agents", row=1, col=1)
    fig.update_yaxes(title_text="Number of Agents", row=1, col=2)
    fig.update_yaxes(title_text="Count", row=2, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=2)
    fig.update_yaxes(title_text="Value", row=3, col=1)
    fig.update_yaxes(title_text="Value", row=3, col=2)
    
    return fig