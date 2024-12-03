import pytest
import numpy as np
from streamlit_app.model_two_types_mecc import (
    SmokeModel_MECC_Model,
    ServiceAgent
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
    assert stats_5['max_contacts'] < stats_1['total_contacts'], \
        f"Max contacts per service ({stats_5['max_contacts']}) should be less than total contacts with one service ({stats_1['total_contacts']})"
    
    # 2. Each service should handle a reasonable share of the load
    # For 5 services, each should handle roughly 1/5 of the total contacts
    expected_contacts_per_service = stats_5['total_contacts'] / 5
    assert abs(stats_5['max_contacts'] - expected_contacts_per_service) < expected_contacts_per_service, \
        f"Max contacts ({stats_5['max_contacts']}) should be close to expected ({expected_contacts_per_service})"
    assert abs(stats_5['min_contacts'] - expected_contacts_per_service) < expected_contacts_per_service, \
        f"Min contacts ({stats_5['min_contacts']}) should be close to expected ({expected_contacts_per_service})"
