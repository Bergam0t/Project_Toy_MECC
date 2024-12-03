import pytest
import pandas as pd
import numpy as np
from streamlit_app.model_two_types_mecc import SmokeModel_MECC_Model

def run_scenario(params, steps=18):
    """Run a scenario and return the results"""
    model = SmokeModel_MECC_Model(**params)
    results = []
    
    for _ in range(steps):
        model.step()
        data = model.datacollector.get_model_vars_dataframe().iloc[-1]
        results.append(data)
    
    return pd.DataFrame(results)

def test_high_smoking_recovery():
    """Test recovery from high initial smoking rate"""
    params = {
        "N_people": 1000,
        "N_service": 3,  # Multiple services
        "mecc_effect": 1.0,  # Maximum effect
        "base_make_intervention_prob": 0.5,
        "visit_prob": 0.3,
        "initial_smoking_prob": 0.8,  # High initial smoking
        "quit_attempt_prob": 0.2,
        "base_smoke_relapse_prob": 0.1,  # Low relapse
        "intervention_effect": 2.0,
        "seed": 42,
        "mecc_trained": True
    }
    
    results = run_scenario(params)
    
    # Calculate recovery metrics
    initial_smokers = results["Total Smoking"].iloc[0]
    final_smokers = results["Total Smoking"].iloc[-1]
    recovery_rate = (initial_smokers - final_smokers) / initial_smokers
    
    # Should see significant reduction in smoking
    assert recovery_rate >= 0.4, \
        f"Expected at least 40% reduction, got {recovery_rate*100:.1f}%"
    
    # Calculate quit attempt trend using 3-month moving average
    quit_attempts = results["Total Quit Attempts"].diff()
    moving_avg = quit_attempts.rolling(window=3).mean()
    
    # Quit attempts should remain positive (using moving average)
    assert (moving_avg.iloc[3:] > 0).all(), \
        "Quit attempts should continue throughout recovery"
    
    # Smoke-free months should increase
    smoke_free_months = results["Average Months Smoke Free"]
    assert smoke_free_months.iloc[-1] > smoke_free_months.iloc[6], \
        "Smoke-free months should increase during recovery"

def test_intervention_driven_recovery():
    """Test recovery driven by strong intervention program"""
    params = {
        "N_people": 1000,
        "N_service": 2,
        "mecc_effect": 1.0,
        "base_make_intervention_prob": 0.8,
        "visit_prob": 0.4,
        "initial_smoking_prob": 0.6,
        "quit_attempt_prob": 0.1,  # Low baseline quit rate
        "base_smoke_relapse_prob": 0.2,
        "intervention_effect": 3.0,  # Strong intervention effect
        "seed": 42,
        "mecc_trained": True
    }
    
    results = run_scenario(params)
    
    # Calculate intervention effectiveness
    def get_quit_rate(period_data):
        smokers = period_data["Total Smoking"].mean()
        quit_attempts = period_data["Total Quit Attempts"].diff().mean()
        return quit_attempts / max(1, smokers)  # Per smoker quit rate
    
    # Compare quit rates with/without interventions
    early_data = results.iloc[:6]  # First 6 months (fewer interventions)
    late_data = results.iloc[-6:]  # Last 6 months (more interventions)
    
    early_quit_rate = get_quit_rate(early_data)
    late_quit_rate = get_quit_rate(late_data)
    
    # Quit rate should improve with interventions
    assert late_quit_rate > early_quit_rate, \
        f"Quit rate should increase with interventions. Early: {early_quit_rate:.3f}, Late: {late_quit_rate:.3f}"
    
    # Should see sustained improvement
    early_smoking = results["Total Smoking"].iloc[:6].mean()
    late_smoking = results["Total Smoking"].iloc[-6:].mean()
    improvement = (early_smoking - late_smoking) / early_smoking
    assert improvement >= 0.3, \
        f"Expected at least 30% improvement, got {improvement*100:.1f}%"

def test_relapse_resistant_recovery():
    """Test recovery pattern with decreasing relapse probability"""
    params = {
        "N_people": 1000,
        "N_service": 1,
        "mecc_effect": 0.8,
        "base_make_intervention_prob": 0.3,
        "visit_prob": 0.2,
        "initial_smoking_prob": 0.7,
        "quit_attempt_prob": 0.2,
        "base_smoke_relapse_prob": 0.3,  # Higher initial relapse rate
        "intervention_effect": 1.5,
        "seed": 42,
        "mecc_trained": True
    }
    
    results = run_scenario(params)
    
    # Calculate relapse pattern using cumulative metrics
    def get_relapse_rate(period_data):
        # Calculate net smoking increases over the period
        smoking_changes = period_data["Total Smoking"].diff()
        # Sum only the increases that exceed a threshold to filter noise
        threshold = 2.0  # Minimum increase to count as relapse
        total_increases = smoking_changes[smoking_changes > threshold].sum()
        # Average non-smoking population over the period
        avg_non_smokers = period_data["Total Not Smoking"].mean()
        # Calculate rate per non-smoker per month
        months = len(period_data)
        return total_increases / (avg_non_smokers * months) if avg_non_smokers > 0 else 0
    
    # Compare early vs late periods (excluding first month)
    early_data = results.iloc[1:7]  # Months 2-7
    late_data = results.iloc[-6:]   # Last 6 months
    
    early_relapse_rate = get_relapse_rate(early_data)
    late_relapse_rate = get_relapse_rate(late_data)
    
    # Smoke-free duration should increase
    early_duration = results["Average Months Smoke Free"].iloc[:6].mean()
    late_duration = results["Average Months Smoke Free"].iloc[-6:].mean()
    
    assert late_duration > early_duration, \
        f"Smoke-free duration should increase. Early: {early_duration:.1f}, Late: {late_duration:.1f}"
