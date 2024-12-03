import pytest
import pandas as pd
import numpy as np
from streamlit_app.model_two_types_mecc import SmokeModel_MECC_Model

def run_scenario(params, steps=24):
    """Run a scenario and return the results"""
    model = SmokeModel_MECC_Model(**params)
    results = []
    
    for _ in range(steps):
        model.step()
        data = model.datacollector.get_model_vars_dataframe().iloc[-1]
        results.append(data)
    
    return pd.DataFrame(results)

def test_long_term_population_stabilization():
    """Test that population changes stabilize over time"""
    params = {
        "N_people": 1000,
        "N_service": 1,
        "mecc_effect": 0.8,
        "base_make_intervention_prob": 0.3,
        "visit_prob": 0.2,
        "initial_smoking_prob": 0.5,  # Start with 50% smokers
        "quit_attempt_prob": 0.1,
        "base_smoke_relapse_prob": 0.2,
        "intervention_effect": 1.5,
        "seed": 42,
        "mecc_trained": True
    }
    
    results = run_scenario(params)
    
    # Calculate rates of change
    smoking_changes = results["Total Smoking"].diff()
    early_changes = smoking_changes.iloc[1:7]  # First 6 months (excluding initial NaN)
    late_changes = smoking_changes.iloc[-6:]  # Last 6 months
    
    # Population changes should slow down
    assert abs(late_changes.mean()) < abs(early_changes.mean()), \
        f"Rate of change should decrease. Early: {early_changes.mean():.1f}, Late: {late_changes.mean():.1f}"

def test_long_term_smoke_free_progression():
    """Test that smoke-free months generally increase"""
    params = {
        "N_people": 1000,
        "N_service": 1,
        "mecc_effect": 0.8,
        "base_make_intervention_prob": 0.3,
        "visit_prob": 0.2,
        "initial_smoking_prob": 0.5,
        "quit_attempt_prob": 0.1,
        "base_smoke_relapse_prob": 0.2,
        "intervention_effect": 1.5,
        "seed": 42,
        "mecc_trained": True
    }
    
    results = run_scenario(params)
    smoke_free_months = results["Average Months Smoke Free"]
    
    # Calculate trend using 3-month moving average
    window_size = 3
    moving_avg = smoke_free_months.rolling(window=window_size).mean()
    
    # Trend should be generally increasing
    early_avg = moving_avg.iloc[window_size:window_size+3].mean()
    late_avg = moving_avg.iloc[-3:].mean()
    assert late_avg > early_avg, \
        f"Smoke-free months should trend upward. Early avg: {early_avg:.1f}, Late avg: {late_avg:.1f}"

def test_long_term_intervention_persistence():
    """Test that interventions remain effective over time"""
    params = {
        "N_people": 1000,
        "N_service": 1,
        "mecc_effect": 0.8,
        "base_make_intervention_prob": 0.3,
        "visit_prob": 0.2,
        "initial_smoking_prob": 0.5,
        "quit_attempt_prob": 0.1,
        "base_smoke_relapse_prob": 0.2,
        "intervention_effect": 1.5,
        "seed": 42,
        "mecc_trained": True
    }
    
    results = run_scenario(params)
    
    # Calculate intervention effectiveness over time
    def get_effectiveness(start_idx, end_idx):
        period_data = results.iloc[start_idx:end_idx]
        interventions = period_data["Total Interventions"].iloc[-1] - period_data["Total Interventions"].iloc[0]
        quit_attempts = period_data["Total Quit Attempts"].iloc[-1] - period_data["Total Quit Attempts"].iloc[0]
        return quit_attempts / max(1, interventions)  # Avoid division by zero
    
    # Compare early vs late effectiveness
    early_effectiveness = get_effectiveness(0, 6)  # First 6 months
    late_effectiveness = get_effectiveness(-6, -1)  # Last 6 months
    
    # Late effectiveness should be at least 50% of early effectiveness
    assert late_effectiveness >= 0.5 * early_effectiveness, \
        f"Intervention effectiveness should persist. Early: {early_effectiveness:.2f}, Late: {late_effectiveness:.2f}"
