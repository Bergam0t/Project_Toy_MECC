import pytest
from streamlit_app.model_two_types_mecc import SmokeModel_MECC_Model

def test_relapse_mechanics():
    """Test that relapses occur at expected rates"""
    params = {
        'N_people': 1000,
        'N_service': 1,
        'mecc_effect': 0.5,
        'base_make_intervention_prob': 0.0,  # No interventions
        'visit_prob': 0.0,  # No visits
        'initial_smoking_prob': 1.0,  # Start all as smokers
        'quit_attempt_prob': 1.0,  # Everyone tries to quit first step
        'base_smoke_relapse_prob': 0.2,  # 20% base relapse chance
        'intervention_effect': 1.0,
        'seed': 42,
        'mecc_trained': False
    }
    
    model = SmokeModel_MECC_Model(**params)
    
    # Run first step to get initial state
    model.step()
    data = model.datacollector.get_model_vars_dataframe()
    initial_smokers = data["Total Smoking"].iloc[-1]
    assert initial_smokers == params['N_people'], \
        f"Expected to start with {params['N_people']} smokers, got {initial_smokers}"
    
    # Second step: everyone tries to quit
    model.step()
    data = model.datacollector.get_model_vars_dataframe()
    smokers_after_quit = data["Total Smoking"].iloc[-1]
    
    # Third step: some ex-smokers relapse
    model.step()
    data = model.datacollector.get_model_vars_dataframe()
    smokers_after_relapse = data["Total Smoking"].iloc[-1]
    
    # With quit_attempt_prob=1.0, most people should quit in second step
    assert smokers_after_quit < params['N_people'] * 0.5, \
        f"Expected most people to quit, got {smokers_after_quit} smokers"
    
    # Verify that some relapses occur
    assert smokers_after_relapse > smokers_after_quit, \
        f"Expected some relapses to occur. Got {smokers_after_quit} -> {smokers_after_relapse} smokers"
    
    # Verify relapse rate is reasonable (not too high)
    non_smokers = params['N_people'] - smokers_after_quit
    relapse_rate = (smokers_after_relapse - smokers_after_quit) / non_smokers
    assert relapse_rate <= params['base_smoke_relapse_prob'], \
        f"Relapse rate {relapse_rate:.2f} should not exceed base rate {params['base_smoke_relapse_prob']}"

def test_smoke_free_tracking():
    """Test that smoke-free months are tracked correctly"""
    params = {
        'N_people': 100,
        'N_service': 1,
        'mecc_effect': 0.5,
        'base_make_intervention_prob': 0.0,
        'visit_prob': 0.0,
        'initial_smoking_prob': 1.0,  # Start all as smokers
        'quit_attempt_prob': 1.0,  # Everyone quits first step
        'base_smoke_relapse_prob': 0.0,  # No relapses
        'intervention_effect': 1.0,
        'seed': 42,
        'mecc_trained': False
    }
    
    model = SmokeModel_MECC_Model(**params)
    
    # First step: everyone quits
    model.step()
    data = model.datacollector.get_model_vars_dataframe()
    initial_smoke_free = data["Average Months Smoke Free"].iloc[-1]
    
    # Track smoke-free months over next steps
    smoke_free_months = [initial_smoke_free]
    for _ in range(3):
        model.step()
        data = model.datacollector.get_model_vars_dataframe()
        smoke_free_months.append(data["Average Months Smoke Free"].iloc[-1])
    
    # Check that smoke-free months increase monotonically
    assert all(b > a for a, b in zip(smoke_free_months[:-1], smoke_free_months[1:])), \
        f"Smoke-free months should increase over time. Got {smoke_free_months}"
    
    # Check final value is approximately correct
    # After 3 steps, should be around 3 months smoke free
    assert abs(smoke_free_months[-1] - 3) < 0.1, \
        f"Expected about 3 months smoke free, got {smoke_free_months[-1]}"

def test_relapse_probability_bounds():
    """Test that relapse probability stays within expected bounds"""
    params = {
        'N_people': 1000,
        'N_service': 1,
        'mecc_effect': 0.5,
        'base_make_intervention_prob': 0.0,
        'visit_prob': 0.0,
        'initial_smoking_prob': 1.0,  # Start all as smokers
        'quit_attempt_prob': 1.0,  # Everyone quits first step
        'base_smoke_relapse_prob': 0.2,
        'intervention_effect': 1.0,
        'seed': 42,
        'mecc_trained': False
    }
    
    model = SmokeModel_MECC_Model(**params)
    
    # Track smoker counts over time
    smokers_by_step = []
    
    # First step: get initial state
    model.step()
    data = model.datacollector.get_model_vars_dataframe()
    smokers_by_step.append(data["Total Smoking"].iloc[-1])
    
    # Second step: mass quit attempt
    model.step()
    data = model.datacollector.get_model_vars_dataframe()
    smokers_by_step.append(data["Total Smoking"].iloc[-1])
    
    # Run for several more steps to observe relapses
    for _ in range(5):
        model.step()
        data = model.datacollector.get_model_vars_dataframe()
        smokers_by_step.append(data["Total Smoking"].iloc[-1])
    
    # Calculate changes after the mass quit
    post_quit_changes = [b - a for a, b in zip(smokers_by_step[1:-1], smokers_by_step[2:])]
    
    # For each step:
    # - Positive changes (relapses) should be bounded by base_smoke_relapse_prob
    # - Negative changes (quits) should be bounded by quit_attempt_prob
    max_relapse_change = (params['N_people'] - min(smokers_by_step)) * params['base_smoke_relapse_prob']
    max_quit_change = max(smokers_by_step) * params['quit_attempt_prob']
    
    for change in post_quit_changes:
        if change > 0:  # Relapse
            assert change <= max_relapse_change, \
                f"Relapse change {change} exceeds maximum possible {max_relapse_change}"
        else:  # Quit
            assert abs(change) <= max_quit_change, \
                f"Quit change {change} exceeds maximum possible {max_quit_change}"
