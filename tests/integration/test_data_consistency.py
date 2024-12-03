import pytest
from streamlit_app.model_two_types_mecc import (
    SmokeModel_MECC_Model,
    ServiceAgent,
    PersonAgent
)

def test_data_collection_integration():
    """Test that data collection accurately reflects model state"""
    params = {
        "N_people": 100,
        "N_service": 1,
        "mecc_effect": 0.8,
        "base_make_intervention_prob": 0.3,
        "visit_prob": 0.2,
        "initial_smoking_prob": 1.0,
        "quit_attempt_prob": 0.1,
        "base_smoke_relapse_prob": 0.1,
        "intervention_effect": 1.5,
        "seed": 42,
        "mecc_trained": True
    }
    
    model = SmokeModel_MECC_Model(**params)
    
    # Run model and collect both agent states and metrics
    for step in range(5):
        # Get direct agent counts before step
        smokers_direct = sum(1 for a in model.schedule.agents if hasattr(a, 'smoker') and a.smoker)
        non_smokers_direct = sum(1 for a in model.schedule.agents if hasattr(a, 'smoker') and not a.smoker)
        
        model.step()
        
        # Get metrics after step
        data = model.datacollector.get_model_vars_dataframe()
        smokers_metric = data["Total Smoking"].iloc[-1]
        non_smokers_metric = data["Total Not Smoking"].iloc[-1]
        
        # Metrics should match direct counts
        assert smokers_direct == smokers_metric, \
            f"Step {step}: Smoking metric ({smokers_metric}) doesn't match direct count ({smokers_direct})"
        assert non_smokers_direct == non_smokers_metric, \
            f"Step {step}: Non-smoking metric ({non_smokers_metric}) doesn't match direct count ({non_smokers_direct})"
        
        # Population should be conserved
        assert smokers_metric + non_smokers_metric == params['N_people'], \
            f"Step {step}: Population not conserved. Got {smokers_metric + non_smokers_metric}, expected {params['N_people']}"

def test_metric_consistency():
    """Test that metrics remain consistent with each other"""
    params = {
        "N_people": 100,
        "N_service": 1,
        "mecc_effect": 0.8,
        "base_make_intervention_prob": 0.3,
        "visit_prob": 0.2,
        "initial_smoking_prob": 1.0,
        "quit_attempt_prob": 0.1,
        "base_smoke_relapse_prob": 0.1,
        "intervention_effect": 1.5,
        "seed": 42,
        "mecc_trained": True
    }
    
    model = SmokeModel_MECC_Model(**params)
    
    # Run model and check metric relationships
    for step in range(5):
        model.step()
        data = model.datacollector.get_model_vars_dataframe()
        
        # Get current metrics
        total_smoking = data["Total Smoking"].iloc[-1]
        total_not_smoking = data["Total Not Smoking"].iloc[-1]
        total_quit_attempts = data["Total Quit Attempts"].iloc[-1]
        total_quit_smoking = data["Total Quit Smoking"].iloc[-1]
        total_contacts = data["Total Contacts"].iloc[-1]
        total_interventions = data["Total Interventions"].iloc[-1]
        
        # Check metric relationships
        assert total_smoking + total_not_smoking == params['N_people'], \
            f"Step {step}: Population not conserved"
        
        assert total_interventions <= total_contacts, \
            f"Step {step}: Cannot have more interventions ({total_interventions}) than contacts ({total_contacts})"
        
        assert total_quit_smoking <= total_quit_attempts, \
            f"Step {step}: Cannot have more successful quits ({total_quit_smoking}) than attempts ({total_quit_attempts})"

def test_agent_state_consistency():
    """Test that agent states remain consistent"""
    params = {
        "N_people": 100,
        "N_service": 2,
        "mecc_effect": 0.8,
        "base_make_intervention_prob": 0.3,
        "visit_prob": 0.2,
        "initial_smoking_prob": 1.0,
        "quit_attempt_prob": 0.1,
        "base_smoke_relapse_prob": 0.1,
        "intervention_effect": 1.5,
        "seed": 42,
        "mecc_trained": True
    }
    
    model = SmokeModel_MECC_Model(**params)
    
    # Run model and check agent states
    for step in range(5):
        model.step()
        
        # Check person agents
        people = [a for a in model.schedule.agents if isinstance(a, PersonAgent)]
        for person in people:
            # Basic state checks
            assert isinstance(person.smoker, bool), \
                f"Step {step}: Smoker status should be boolean, got {type(person.smoker)}"
            
            assert isinstance(person.never_smoked, bool), \
                f"Step {step}: Never-smoked status should be boolean, got {type(person.never_smoked)}"
            
            assert person.months_smoke_free >= 0, \
                f"Step {step}: Smoke-free months should be non-negative, got {person.months_smoke_free}"
            
            # Logical state checks
            if person.never_smoked:
                assert not person.smoker, \
                    f"Step {step}: Never-smoked agents cannot be current smokers"
            
            if person.months_smoke_free > 0:
                assert not person.smoker, \
                    f"Step {step}: Agents with smoke-free months cannot be current smokers"
        
        # Check service agents
        services = [a for a in model.schedule.agents if isinstance(a, ServiceAgent)]
        for service in services:
            assert service.contacts_made >= 0, \
                f"Step {step}: Contacts should be non-negative, got {service.contacts_made}"
            
            assert service.interventions_made >= 0, \
                f"Step {step}: Interventions should be non-negative, got {service.interventions_made}"
            
            assert service.interventions_made <= service.contacts_made, \
                f"Step {step}: Cannot have more interventions ({service.interventions_made}) than contacts ({service.contacts_made})"
