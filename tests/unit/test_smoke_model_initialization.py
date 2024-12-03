import pytest
from streamlit_app.model_two_types_mecc import SmokeModel_MECC_Model

def test_smoke_model_initialization():
    """Test that the smoke model initializes correctly with given parameters"""
    params = {
        'N_people': 100,
        'N_service': 1,
        'mecc_effect': 0.5,
        'base_make_intervention_prob': 0.5,
        'visit_prob': 0.5,
        'initial_smoking_prob': 0.8,
        'quit_attempt_prob': 0.2,
        'base_smoke_relapse_prob': 0.3,
        'intervention_effect': 1.5,
        'seed': 42,
        'mecc_trained': False
    }
    
    model = SmokeModel_MECC_Model(**params)
    
    # Check that the model has the correct number of agents
    assert len([a for a in model.schedule.agents if hasattr(a, 'smoker')]) == params['N_people']
    assert len([a for a in model.schedule.agents if not hasattr(a, 'smoker')]) == params['N_service']
    
    # Check that the initial smoking population is approximately correct
    smokers = sum(1 for a in model.schedule.agents if hasattr(a, 'smoker') and a.smoker)
    expected_smokers = params['N_people'] * params['initial_smoking_prob']
    assert abs(smokers - expected_smokers) <= 10  # Allow for some random variation

def test_metrics_collection():
    """Test that all metrics are collected and have sensible values"""
    params = {
        'N_people': 100,
        'N_service': 1,
        'mecc_effect': 0.5,
        'base_make_intervention_prob': 0.5,
        'visit_prob': 0.5,
        'initial_smoking_prob': 0.5,
        'quit_attempt_prob': 0.2,
        'base_smoke_relapse_prob': 0.2,
        'intervention_effect': 1.5,
        'seed': 42,
        'mecc_trained': True
    }
    
    model = SmokeModel_MECC_Model(**params)
    model.step()
    
    data = model.datacollector.get_model_vars_dataframe()
    
    # Check that all expected metrics are present
    expected_metrics = [
        "Total Smoking",
        "Total Not Smoking",
        "Total Quit Attempts",
        "Total Quit Smoking",
        "Total Contacts",
        "Total Interventions",
        "Smokers With an Intervention",
        "Average Months Smoke Free"
    ]
    
    for metric in expected_metrics:
        assert metric in data.columns
        
        # Check that values are within sensible ranges
        values = data[metric]
        assert (values >= 0).all()  # All metrics should be non-negative
        
        if metric in ["Total Smoking", "Total Not Smoking"]:
            assert (values <= params['N_people']).all()
        elif metric in ["Total Contacts", "Total Interventions", "Smokers With an Intervention"]:
            assert (values <= params['N_people'] * 10).all()  # Allow for multiple contacts/interventions
