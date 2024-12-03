import pytest
import pandas as pd
import numpy as np
from streamlit_app.model_two_types_mecc import (
    MECC_Model,
    SmokeModel_MECC_Model,
    SmokeModel_PersonAgent,
    SmokeModel_ServiceAgent,
    ServiceAgent,
    PersonAgent
)

def test_intervention_effect_scaling():
    """Test that intervention load is properly distributed among services"""
    def get_service_stats(n_services):
        params = {
            "N_people": 1000,
            "N_service": n_services,
            "mecc_effect": 0.8,
            "base_make_intervention_prob": 0.3,
            "visit_prob": 0.2,
            "initial_smoking_prob": 1.0,
            "quit_attempt_prob": 0.1,
            "base_smoke_relapse_prob": 0.0,
            "intervention_effect": 1.5,
            "seed": 42,
            "mecc_trained": True
        }

        model = SmokeModel_MECC_Model(**params)
        
        # Run for several steps to accumulate more data
        for _ in range(5):
            model.step()
        
        # Get service-specific stats
        services = [a for a in model.schedule.agents if isinstance(a, ServiceAgent)]
        contacts_per_service = [s.contacts_made for s in services]
        interventions_per_service = [s.interventions_made for s in services]
        
        return {
            'contacts_std': np.std(contacts_per_service),
            'interventions_std': np.std(interventions_per_service),
            'total_contacts': sum(contacts_per_service),
            'total_interventions': sum(interventions_per_service),
            'max_contacts': max(contacts_per_service),
            'min_contacts': min(contacts_per_service)
        }

    # Compare results with different numbers of services
    stats_1 = get_service_stats(1)
    stats_5 = get_service_stats(5)

    # With multiple services:
    # 1. The maximum load on any single service should be less
    assert stats_5['max_contacts'] < stats_1['total_contacts']
    
    # 2. Each service should handle a reasonable share of the load
    # For 5 services, each should handle roughly 1/5 of the total contacts
    expected_contacts_per_service = stats_5['total_contacts'] / 5
    assert abs(stats_5['max_contacts'] - expected_contacts_per_service) < expected_contacts_per_service
    assert abs(stats_5['min_contacts'] - expected_contacts_per_service) < expected_contacts_per_service

def test_person_service_interaction_chain():
    """Test the complete chain of interactions between people and services"""
    params = {
        "N_people": 100,
        "N_service": 1,
        "mecc_effect": 1.0,  # Always intervene when trained
        "base_make_intervention_prob": 0.0,  # Never intervene when not trained
        "visit_prob": 1.0,  # Always visit
        "initial_smoking_prob": 1.0,  # All start as smokers
        "quit_attempt_prob": 0.2,  # Base quit rate
        "base_smoke_relapse_prob": 0.0,  # No relapses
        "intervention_effect": 2.0,  # Strong intervention effect
        "seed": 42,
        "mecc_trained": True
    }
    
    model = SmokeModel_MECC_Model(**params)
    
    # Track the interaction chain
    history = []
    for _ in range(5):
        model.step()
        data = model.datacollector.get_model_vars_dataframe()
        history.append({
            'contacts': data["Total Contacts"].iloc[-1],
            'interventions': data["Total Interventions"].iloc[-1],
            'quit_attempts': data["Total Quit Attempts"].iloc[-1],
            'quit_smoking': data["Total Quit Smoking"].iloc[-1]
        })
    
    # Verify the interaction chain
    for step in range(1, len(history)):
        # Contacts should lead to interventions
        assert history[step]['contacts'] > 0, \
            f"Step {step}: Should see contacts with visit_prob=1.0"
        
        # Interventions should occur with contacts
        assert history[step]['interventions'] > 0, \
            f"Step {step}: Contacts ({history[step]['contacts']}) should lead to interventions"
        
        # Quit attempts should increase with interventions
        assert history[step]['quit_attempts'] > history[0]['quit_attempts'], \
            f"Step {step}: Interventions should increase quit attempts over baseline"
        
        # Some quit attempts should succeed
        assert history[step]['quit_smoking'] > 0, \
            f"Step {step}: Should see some successful quits"
        
        # Chain should be properly ordered
        assert history[step]['contacts'] >= history[step]['interventions'], \
            "Cannot have more interventions than contacts"

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
    for _ in range(5):
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
            f"Smoking metric ({smokers_metric}) doesn't match direct count ({smokers_direct})"
        assert non_smokers_direct == non_smokers_metric, \
            f"Non-smoking metric ({non_smokers_metric}) doesn't match direct count ({non_smokers_direct})"
        
        # Population should be conserved
        assert smokers_metric + non_smokers_metric == params['N_people'], \
            "Total population should remain constant"

def test_model_state_integration():
    """Test that model state remains consistent across components"""
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
    
    # Run model and check state consistency
    for step in range(5):
        # Get service states
        services = [a for a in model.schedule.agents if isinstance(a, ServiceAgent)]
        service_interventions = sum(s.interventions_made for s in services)
        
        # Get person states
        people = [a for a in model.schedule.agents if isinstance(a, PersonAgent)]
        
        # Get metrics
        data = model.datacollector.get_model_vars_dataframe()
        if len(data) > 0:
            metric_interventions = data["Total Interventions"].iloc[-1]
            
            # Service interventions should match metrics
            assert abs(service_interventions - metric_interventions) <= step + 1, \
                f"Step {step}: Service interventions ({service_interventions}) should match metrics ({metric_interventions})"
        
        model.step()
        
        # Check agent consistency
        for person in people:
            # Smoker status should be boolean
            assert isinstance(person.smoker, bool), \
                f"Smoker status should be boolean, got {type(person.smoker)}"
            
            # Never-smoked status should be consistent
            if person.never_smoked:
                assert not person.smoker, \
                    "Never-smoked agents cannot be current smokers"
            
            # Smoke-free months should be non-negative
            assert person.months_smoke_free >= 0, \
                f"Smoke-free months should be non-negative, got {person.months_smoke_free}"
