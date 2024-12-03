import pytest
from streamlit_app.model_two_types_mecc import SmokeModel_MECC_Model

def test_population_dynamics():
    """Test that population dynamics behave correctly"""
    params = {
        'N_people': 100,
        'N_service': 1,
        'mecc_effect': 0.9,
        'base_make_intervention_prob': 0.1,
        'visit_prob': 0.1,
        'initial_smoking_prob': 0.5,
        'quit_attempt_prob': 0.2,  # High quit rate for visible changes
        'base_smoke_relapse_prob': 0.1,
        'intervention_effect': 1.1,
        'seed': 42,
        'mecc_trained': False
    }
    
    model = SmokeModel_MECC_Model(**params)
    
    # Track population changes over time
    smokers = []
    non_smokers = []
    
    # Run for several steps
    for _ in range(5):
        model.step()
        data = model.datacollector.get_model_vars_dataframe()
        smokers.append(data["Total Smoking"].iloc[-1])
        non_smokers.append(data["Total Not Smoking"].iloc[-1])
    
    # Population should be conserved
    for step in range(len(smokers)):
        total = smokers[step] + non_smokers[step]
        assert total == params['N_people'], \
            f"Population not conserved at step {step}. Got {total}, expected {params['N_people']}"
    
    # Should see some population changes
    assert len(set(smokers)) > 1, \
        "Smoking population should change over time"
    assert len(set(non_smokers)) > 1, \
        "Non-smoking population should change over time"

def test_state_transitions():
    """Test that agent state transitions work correctly"""
    params = {
        'N_people': 100,
        'N_service': 1,
        'mecc_effect': 0.9,
        'base_make_intervention_prob': 0.1,
        'visit_prob': 1.0,  # High visit rate
        'initial_smoking_prob': 1.0,  # All start as smokers
        'quit_attempt_prob': 1.0,  # Everyone tries to quit
        'base_smoke_relapse_prob': 0.0,  # No relapses
        'intervention_effect': 2.0,  # Strong intervention effect
        'seed': 42,
        'mecc_trained': True  # Enable MECC
    }
    
    model = SmokeModel_MECC_Model(**params)
    
    # Get initial state
    model.step()  # Need to run step to collect initial data
    data = model.datacollector.get_model_vars_dataframe()
    initial_smokers = data["Total Smoking"].iloc[-1]
    assert initial_smokers == params['N_people'], \
        "All agents should start as smokers"
    
    # Run one step - should see quit attempts
    model.step()
    data = model.datacollector.get_model_vars_dataframe()
    quit_attempts = data["Total Quit Attempts"].iloc[-1]
    assert quit_attempts > 0, \
        "Should see quit attempts with quit_attempt_prob=1.0"
    
    # Run another step - should see successful quits
    model.step()
    data = model.datacollector.get_model_vars_dataframe()
    successful_quits = data["Total Quit Smoking"].iloc[-1]
    assert successful_quits > 0, \
        "Should see successful quits"

def test_time_progression():
    """Test that time-dependent behaviors work correctly"""
    params = {
        'N_people': 100,
        'N_service': 1,
        'mecc_effect': 0.9,
        'base_make_intervention_prob': 0.1,
        'visit_prob': 0.1,
        'initial_smoking_prob': 1.0,  # All start as smokers
        'quit_attempt_prob': 1.0,  # Everyone tries to quit
        'base_smoke_relapse_prob': 0.2,
        'intervention_effect': 1.1,
        'seed': 42,
        'mecc_trained': False
    }
    
    model = SmokeModel_MECC_Model(**params)
    
    # Track smoke-free months and relapse rates
    smoke_free_months = []
    relapse_counts = []
    previous_smokers = params['N_people']
    
    # Run for several steps
    for _ in range(5):
        model.step()
        data = model.datacollector.get_model_vars_dataframe()
        smoke_free_months.append(data["Average Months Smoke Free"].iloc[-1])
        current_smokers = data["Total Smoking"].iloc[-1]
        relapse_count = max(0, current_smokers - previous_smokers)  # Only count increases
        relapse_counts.append(relapse_count)
        previous_smokers = current_smokers
    
    # Smoke-free months should increase monotonically for those who stay quit
    assert all(b >= a for a, b in zip(smoke_free_months[:-1], smoke_free_months[1:])), \
        "Smoke-free months should not decrease"
    
    # Relapse rate should decrease over time
    non_zero_relapses = [r for r in relapse_counts if r > 0]
    if len(non_zero_relapses) > 1:
        assert non_zero_relapses[-1] <= non_zero_relapses[0], \
            "Relapse rate should decrease over time"

def test_agent_interactions():
    """Test that agents interact correctly"""
    params = {
        'N_people': 100,
        'N_service': 1,
        'mecc_effect': 1.0,  # Always intervene when trained
        'base_make_intervention_prob': 0.0,  # Never intervene when not trained
        'visit_prob': 1.0,  # Always visit
        'initial_smoking_prob': 1.0,  # All start as smokers
        'quit_attempt_prob': 0.2,  # Base quit rate
        'base_smoke_relapse_prob': 0.0,  # No relapses
        'intervention_effect': 2.0,  # Strong intervention effect
        'seed': 42,
        'mecc_trained': True
    }
    
    model = SmokeModel_MECC_Model(**params)
    
    # Run for several steps
    contacts = []
    interventions = []
    quit_attempts = []
    
    for _ in range(3):
        model.step()
        data = model.datacollector.get_model_vars_dataframe()
        contacts.append(data["Total Contacts"].iloc[-1])
        interventions.append(data["Total Interventions"].iloc[-1])
        quit_attempts.append(data["Total Quit Attempts"].iloc[-1])
    
    # Should see increasing contacts
    assert contacts[-1] > contacts[0], \
        f"Contacts should increase over time. Got {contacts}"
    
    # Should see interventions due to MECC training
    assert interventions[-1] > 0, \
        f"Should see interventions with MECC training. Got {interventions}"
    
    # Should see more quit attempts with interventions
    assert quit_attempts[-1] > 0, \
        f"Should see quit attempts from interventions. Got {quit_attempts}"
    
    # Verify relationships
    assert interventions[-1] <= contacts[-1], \
        f"Cannot have more interventions than contacts. Got {interventions[-1]} interventions vs {contacts[-1]} contacts"

def test_intervention_effects():
    """Test that interventions have their intended effects"""
    params = {
        'N_people': 100,
        'N_service': 1,
        'mecc_effect': 1.0,  # Always intervene
        'base_make_intervention_prob': 1.0,  # Always intervene
        'visit_prob': 1.0,  # Always visit
        'initial_smoking_prob': 1.0,  # All start as smokers
        'quit_attempt_prob': 0.2,  # Base quit rate
        'base_smoke_relapse_prob': 0.0,  # No relapses
        'intervention_effect': 2.0,  # Double quit probability
        'seed': 42,
        'mecc_trained': True
    }
    
    model = SmokeModel_MECC_Model(**params)
    
    # Track intervention chain
    base_quit_attempts = []  # Without interventions
    intervention_quit_attempts = []  # With interventions
    
    # First run without interventions
    model_no_intervention = SmokeModel_MECC_Model(**{**params, 'intervention_effect': 1.0})
    for _ in range(3):
        model_no_intervention.step()
        data = model_no_intervention.datacollector.get_model_vars_dataframe()
        base_quit_attempts.append(data["Total Quit Attempts"].iloc[-1])
    
    # Then run with interventions
    for _ in range(3):
        model.step()
        data = model.datacollector.get_model_vars_dataframe()
        intervention_quit_attempts.append(data["Total Quit Attempts"].iloc[-1])
    
    # Should see more quit attempts with interventions
    assert intervention_quit_attempts[-1] > base_quit_attempts[-1], \
        f"Interventions should increase quit attempts. Got {intervention_quit_attempts[-1]} with vs {base_quit_attempts[-1]} without"
    
    # Verify intervention multiplier
    quit_ratio = intervention_quit_attempts[-1] / max(1, base_quit_attempts[-1])
    assert quit_ratio > 1.0, \
        f"Intervention effect should increase quit attempts. Got ratio {quit_ratio}"
