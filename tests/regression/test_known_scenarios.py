import pytest
import pandas as pd
import numpy as np
from streamlit_app.model_two_types_mecc import SmokeModel_MECC_Model

@pytest.fixture
def baseline_scenario():
    """Baseline scenario with typical parameter values"""
    return {
        "N_people": 1000,
        "N_service": 1,
        "mecc_effect": 0.8,
        "base_make_intervention_prob": 0.3,
        "visit_prob": 0.2,
        "initial_smoking_prob": 0.3,
        "quit_attempt_prob": 0.1,
        "base_smoke_relapse_prob": 0.2,
        "intervention_effect": 1.5,
        "seed": 42,
        "mecc_trained": True
    }

def run_scenario(params, steps=12):
    """Run a scenario and return the results"""
    model = SmokeModel_MECC_Model(**params)
    results = []
    
    for _ in range(steps):
        model.step()
        data = model.datacollector.get_model_vars_dataframe().iloc[-1]
        results.append(data)
    
    return pd.DataFrame(results)

def test_baseline_scenario(baseline_scenario):
    """Test that baseline scenario behaves as expected"""
    results = run_scenario(baseline_scenario)
    
    # Known good values from baseline scenario
    # Adjusted ranges based on observed behavior
    expected_ranges = {
        "Total Smoking": (100, 200),  # Expect significant reduction from initial ~300
        "Total Quit Attempts": (200, 600),  # Cumulative range
        "Total Interventions": (1000, 2000),  # Cumulative range
        "Average Months Smoke Free": (0.5, 2)  # Expected range
    }
    
    final_values = results.iloc[-1]
    
    for metric, (min_val, max_val) in expected_ranges.items():
        assert min_val <= final_values[metric] <= max_val, \
            f"{metric} value {final_values[metric]} outside expected range [{min_val}, {max_val}]"

def test_high_intervention_scenario():
    """Test scenario with high intervention rates"""
    params = {
        "N_people": 1000,
        "N_service": 1,
        "mecc_effect": 1.0,  # Maximum intervention rate
        "base_make_intervention_prob": 0.8,
        "visit_prob": 0.5,
        "initial_smoking_prob": 0.3,
        "quit_attempt_prob": 0.2,
        "base_smoke_relapse_prob": 0.1,
        "intervention_effect": 2.0,
        "seed": 42,
        "mecc_trained": True
    }
    
    results = run_scenario(params)
    final_values = results.iloc[-1]
    
    # High intervention scenario should show:
    # 1. Higher intervention rate
    assert final_values["Total Interventions"] >= 1000
    # 2. More quit attempts
    assert final_values["Total Quit Attempts"] >= 400
    # 3. Lower final smoking population
    assert final_values["Total Smoking"] <= 200

def test_high_relapse_scenario():
    """Test scenario with high relapse rates"""
    params = {
        "N_people": 1000,
        "N_service": 1,
        "mecc_effect": 0.8,
        "base_make_intervention_prob": 0.3,
        "visit_prob": 0.2,
        "initial_smoking_prob": 0.3,
        "quit_attempt_prob": 0.2,
        "base_smoke_relapse_prob": 0.8,  # High relapse rate
        "intervention_effect": 1.5,
        "seed": 42,
        "mecc_trained": True
    }
    
    results = run_scenario(params)
    
    # High relapse scenario should show:
    # 1. More fluctuation in smoking population
    smoking_std = results["Total Smoking"].std()
    assert smoking_std >= 5
    # 2. Lower average smoke-free months
    assert results["Average Months Smoke Free"].mean() <= 1.0

def test_low_visit_scenario():
    """Test scenario with low visit rates"""
    params = {
        "N_people": 1000,
        "N_service": 1,
        "mecc_effect": 0.8,
        "base_make_intervention_prob": 0.3,
        "visit_prob": 0.05,  # Very low visit rate
        "initial_smoking_prob": 0.3,
        "quit_attempt_prob": 0.1,
        "base_smoke_relapse_prob": 0.2,
        "intervention_effect": 1.5,
        "seed": 42,
        "mecc_trained": True
    }
    
    results = run_scenario(params)
    final_values = results.iloc[-1]
    
    # Low visit scenario should show:
    # 1. Fewer total contacts
    assert final_values["Total Contacts"] <= 800
    # 2. Fewer interventions
    assert final_values["Total Interventions"] <= 600
    # 3. Less change in smoking population
    initial_smoking = results["Total Smoking"].iloc[0]
    final_smoking = results["Total Smoking"].iloc[-1]
    assert abs(final_smoking - initial_smoking) <= 150

def test_multiple_services_scenario():
    """Test scenario with multiple services"""
    params = {
        "N_people": 1000,
        "N_service": 5,  # Multiple services
        "mecc_effect": 0.8,
        "base_make_intervention_prob": 0.3,
        "visit_prob": 0.2,
        "initial_smoking_prob": 0.3,
        "quit_attempt_prob": 0.1,
        "base_smoke_relapse_prob": 0.2,
        "intervention_effect": 1.5,
        "seed": 42,
        "mecc_trained": True
    }
    
    results = run_scenario(params)
    final_values = results.iloc[-1]
    
    # Multiple services scenario should show:
    # 1. More total contacts
    assert final_values["Total Contacts"] >= 800
    # 2. More interventions
    assert final_values["Total Interventions"] >= 500
    # 3. Greater reduction in smoking population
    initial_smoking = results["Total Smoking"].iloc[0]
    final_smoking = results["Total Smoking"].iloc[-1]
    assert (initial_smoking - final_smoking) >= 100

def test_intervention_effectiveness_scenario():
    """Test scenario focusing on intervention effectiveness"""
    params = {
        "N_people": 1000,
        "N_service": 1,
        "mecc_effect": 0.8,
        "base_make_intervention_prob": 0.3,
        "visit_prob": 0.2,
        "initial_smoking_prob": 0.3,
        "quit_attempt_prob": 0.1,
        "base_smoke_relapse_prob": 0.2,
        "intervention_effect": 3.0,  # Very effective interventions
        "seed": 42,
        "mecc_trained": True
    }
    
    results = run_scenario(params)
    
    # Calculate intervention success rate
    quit_attempts_per_intervention = (
        results["Total Quit Attempts"] / 
        results["Total Interventions"].replace(0, 1)  # Avoid division by zero
    )
    
    # High intervention effectiveness should show:
    # 1. Higher quit attempts per intervention
    assert quit_attempts_per_intervention.mean() >= 0.2
    # 2. Larger reduction in smoking population
    smoking_reduction = results["Total Smoking"].iloc[0] - results["Total Smoking"].iloc[-1]
    assert smoking_reduction >= 150

def test_long_term_behavior():
    """Test model behavior over a longer time period"""
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
    
    # Run for longer period
    results = run_scenario(params, steps=24)
    
    # Calculate rates of change
    smoking_changes = results["Total Smoking"].diff()
    late_changes = smoking_changes.iloc[-6:]  # Last 6 months
    
    # Population should stabilize
    assert abs(late_changes.mean()) < abs(smoking_changes.iloc[:6].mean()), \
        "Rate of change should decrease over time"
    
    # Smoke-free months should increase
    smoke_free_progression = results["Average Months Smoke Free"].diff()
    assert (smoke_free_progression >= 0).all(), \
        "Smoke-free months should not decrease"
    
    # Intervention effectiveness should persist
    early_quit_rate = results["Total Quit Attempts"].iloc[6] / 6  # First 6 months
    late_quit_rate = (results["Total Quit Attempts"].iloc[-1] - results["Total Quit Attempts"].iloc[-7]) / 6  # Last 6 months
    assert late_quit_rate > 0, \
        "Quit attempts should continue even in long term"

def test_no_intervention_scenario():
    """Test edge case with no interventions"""
    params = {
        "N_people": 1000,
        "N_service": 1,
        "mecc_effect": 0.0,  # No MECC effect
        "base_make_intervention_prob": 0.0,  # No base interventions
        "visit_prob": 0.2,
        "initial_smoking_prob": 0.3,
        "quit_attempt_prob": 0.1,
        "base_smoke_relapse_prob": 0.2,
        "intervention_effect": 1.5,
        "seed": 42,
        "mecc_trained": False
    }
    
    results = run_scenario(params)
    
    # Should see:
    # 1. No interventions
    assert results["Total Interventions"].iloc[-1] == 0
    # 2. Only baseline quit attempts
    expected_attempts = params["quit_attempt_prob"] * params["N_people"] * 12  # rough estimate
    assert abs(results["Total Quit Attempts"].iloc[-1] - expected_attempts) < expected_attempts * 0.5
    # 3. Less reduction in smoking
    smoking_reduction = results["Total Smoking"].iloc[0] - results["Total Smoking"].iloc[-1]
    assert smoking_reduction < 100  # Lower than baseline scenario

def test_recovery_scenario():
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
    
    results = run_scenario(params, steps=18)  # Longer run
    
    # Calculate recovery metrics
    initial_smokers = results["Total Smoking"].iloc[0]
    final_smokers = results["Total Smoking"].iloc[-1]
    recovery_rate = (initial_smokers - final_smokers) / initial_smokers
    
    # Should see:
    # 1. Significant reduction in smoking
    assert recovery_rate >= 0.4, \
        f"Expected at least 40% reduction, got {recovery_rate*100:.1f}%"
    
    # 2. Sustained quit attempts
    quit_attempts = results["Total Quit Attempts"].diff()
    assert (quit_attempts > 0).all(), \
        "Quit attempts should continue throughout recovery"
    
    # 3. Increasing smoke-free duration
    smoke_free_months = results["Average Months Smoke Free"]
    assert smoke_free_months.iloc[-1] > smoke_free_months.iloc[6], \
        "Smoke-free months should increase during recovery"
