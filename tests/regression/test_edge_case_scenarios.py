import pytest
import pandas as pd
import numpy as np
from streamlit_app.model_two_types_mecc import SmokeModel_MECC_Model

def run_scenario(params, steps=12):
    """Run a scenario and return the results"""
    model = SmokeModel_MECC_Model(**params)
    results = []
    
    for _ in range(steps):
        model.step()
        data = model.datacollector.get_model_vars_dataframe().iloc[-1]
        results.append(data)
    
    return pd.DataFrame(results)

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
    
    # Should see no interventions
    assert results["Total Interventions"].iloc[-1] == 0, \
        f"Expected no interventions, got {results['Total Interventions'].iloc[-1]}"
    
    # Calculate expected quit attempts accounting for decreasing smoker population
    smokers_by_month = results["Total Smoking"]
    expected_attempts = sum(smokers * params["quit_attempt_prob"] for smokers in smokers_by_month)
    actual_attempts = results["Total Quit Attempts"].iloc[-1]
    
    # Allow for 50% variation from expected
    assert abs(actual_attempts - expected_attempts) < expected_attempts * 0.5, \
        f"Expected around {expected_attempts:.1f} quit attempts, got {actual_attempts}"

def test_maximum_intervention_scenario():
    """Test edge case with maximum possible interventions"""
    params = {
        "N_people": 1000,
        "N_service": 1,
        "mecc_effect": 1.0,  # Always intervene
        "base_make_intervention_prob": 1.0,  # Always intervene
        "visit_prob": 1.0,  # Always visit
        "initial_smoking_prob": 1.0,  # All smokers
        "quit_attempt_prob": 0.1,  # Base quit rate needed
        "base_smoke_relapse_prob": 0.0,  # No relapses
        "intervention_effect": 2.0,
        "seed": 42,
        "mecc_trained": True
    }
    
    results = run_scenario(params)
    
    # Should see interventions for every contact
    assert (results["Total Interventions"] == results["Total Contacts"]).all(), \
        "Every contact should result in an intervention"
    
    # Should see significant smoking reduction
    initial_smoking = results["Total Smoking"].iloc[0]
    final_smoking = results["Total Smoking"].iloc[-1]
    reduction = (initial_smoking - final_smoking) / initial_smoking
    assert reduction >= 0.3, \
        f"Expected at least 30% reduction in smoking, got {reduction*100:.1f}%"

def test_minimal_population_scenario():
    """Test edge case with minimal population"""
    params = {
        "N_people": 10,  # Minimal population
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
    
    # Population should remain constant
    for col in ["Total Smoking", "Total Not Smoking"]:
        assert (results[col] >= 0).all(), f"Found negative values in {col}"
        assert (results[col] <= params["N_people"]).all(), \
            f"Found values exceeding population in {col}"
    
    # Total population should be constant
    total = results["Total Smoking"] + results["Total Not Smoking"]
    assert (total == params["N_people"]).all(), \
        "Total population should remain constant"

def test_all_smokers_scenario():
    """Test edge case with all smokers and high quit rate"""
    params = {
        "N_people": 1000,
        "N_service": 1,
        "mecc_effect": 1.0,
        "base_make_intervention_prob": 1.0,
        "visit_prob": 1.0,
        "initial_smoking_prob": 1.0,  # All smokers
        "quit_attempt_prob": 0.5,  # High quit rate
        "base_smoke_relapse_prob": 0.0,  # No relapses
        "intervention_effect": 2.0,
        "seed": 42,
        "mecc_trained": True
    }
    
    results = run_scenario(params)
    
    # Should see rapid decrease in smoking
    smoking_changes = results["Total Smoking"].diff().iloc[1:]  # Skip first NaN
    assert (smoking_changes <= 0).all(), \
        "Smoking population should only decrease"
    
    # Should see substantial reduction
    final_smoking = results["Total Smoking"].iloc[-1]
    assert final_smoking < params["N_people"] * 0.2, \
        f"Expected reduction to <20% smoking, got {final_smoking/params['N_people']*100:.1f}%"
