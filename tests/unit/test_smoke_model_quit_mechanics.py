import pytest
from streamlit_app.model_two_types_mecc import SmokeModel_MECC_Model

def test_quit_attempt_mechanics():
    """Test that quit attempts occur at expected rates"""
    params = {
        'N_people': 1000,
        'N_service': 1,
        'mecc_effect': 0.5,
        'base_make_intervention_prob': 0.5,
        'visit_prob': 0.5,
        'initial_smoking_prob': 1.0,  # Start all as smokers
        'quit_attempt_prob': 0.2,
        'base_smoke_relapse_prob': 0.0,  # No relapses
        'intervention_effect': 1.0,  # No intervention boost
        'seed': 42,
        'mecc_trained': False
    }
    
    model = SmokeModel_MECC_Model(**params)
    
    # Track quit attempts after each step
    quit_attempts_by_step = []
    for _ in range(3):  # Run for 3 steps
        model.step()
        data = model.datacollector.get_model_vars_dataframe()
        quit_attempts_by_step.append(data["Total Quit Attempts"].iloc[-1])
    
    # Check that quit attempts increase over time
    assert quit_attempts_by_step[-1] > quit_attempts_by_step[0], \
        f"Quit attempts should increase over time. Got {quit_attempts_by_step}"
    
    # With 1000 people, quit_attempt_prob=0.2, over 3 steps
    # Each step: remaining_smokers * quit_attempt_prob
    # Step 1: 1000 * 0.2 = 200
    # Step 2: 800 * 0.2 = 160
    # Step 3: 640 * 0.2 = 128
    # Total ≈ 488
    expected_min = 350  # Allow for some random variation below mean
    expected_max = 600  # Allow for some random variation above mean
    
    assert expected_min <= quit_attempts_by_step[-1] <= expected_max, \
        f"Got {quit_attempts_by_step[-1]} total quit attempts, expected between {expected_min} and {expected_max}"

def test_intervention_effect():
    """Test that interventions properly affect quit attempt probability"""
    params = {
        'N_people': 100,
        'N_service': 1,
        'mecc_effect': 1.0,  # Always intervene when trained
        'base_make_intervention_prob': 0.0,  # Never intervene when not trained
        'visit_prob': 1.0,  # Always visit
        'initial_smoking_prob': 1.0,  # All start as smokers
        'quit_attempt_prob': 0.2,
        'base_smoke_relapse_prob': 0.0,  # No relapses
        'intervention_effect': 2.0,  # Double quit probability
        'seed': 42
    }
    
    # Run without MECC training
    model_without = SmokeModel_MECC_Model(**params, mecc_trained=False)
    model_without.step()
    model_without.step()
    data_without = model_without.datacollector.get_model_vars_dataframe()
    
    # Run with MECC training
    model_with = SmokeModel_MECC_Model(**params, mecc_trained=True)
    model_with.step()
    model_with.step()
    data_with = model_with.datacollector.get_model_vars_dataframe()
    
    # Should see more quit attempts with interventions
    assert data_with["Total Quit Attempts"].iloc[-1] > data_without["Total Quit Attempts"].iloc[-1], \
        f"Expected more quit attempts with interventions. Got {data_with['Total Quit Attempts'].iloc[-1]} with vs {data_without['Total Quit Attempts'].iloc[-1]} without"

def test_quit_success_tracking():
    """Test that successful quits are tracked correctly"""
    params = {
        'N_people': 100,
        'N_service': 1,
        'mecc_effect': 0.5,
        'base_make_intervention_prob': 0.0,
        'visit_prob': 0.0,
        'initial_smoking_prob': 1.0,  # Start all as smokers
        'quit_attempt_prob': 1.0,  # Everyone tries to quit
        'base_smoke_relapse_prob': 0.0,  # No relapses
        'intervention_effect': 1.0,
        'seed': 42,
        'mecc_trained': False
    }
    
    model = SmokeModel_MECC_Model(**params)
    
    # First step: get initial state
    model.step()
    data = model.datacollector.get_model_vars_dataframe()
    initial_quit_attempts = data["Total Quit Attempts"].iloc[-1]
    initial_quit_success = data["Total Quit Smoking"].iloc[-1]
    
    # Second step: everyone tries to quit
    model.step()
    data = model.datacollector.get_model_vars_dataframe()
    final_quit_attempts = data["Total Quit Attempts"].iloc[-1]
    final_quit_success = data["Total Quit Smoking"].iloc[-1]
    
    # Should see quit attempts increase
    assert final_quit_attempts > initial_quit_attempts, \
        f"Expected quit attempts to increase. Got {initial_quit_attempts} -> {final_quit_attempts}"
    
    # Successful quits should be tracked
    assert final_quit_success > initial_quit_success, \
        f"Expected successful quits to increase. Got {initial_quit_success} -> {final_quit_success}"
    
    # Successful quits should not exceed attempts
    assert final_quit_success <= final_quit_attempts, \
        f"Successful quits ({final_quit_success}) should not exceed attempts ({final_quit_attempts})"
