import pytest
from streamlit_app.model_two_types_mecc import MECC_Model, PersonAgent, ServiceAgent

def test_model_initialization(base_model):
    """Test that the model initializes with correct number of agents and parameters"""
    # Check total number of agents
    assert len(base_model.schedule.agents) == 101  # 100 people + 1 service

    # Count each type of agent
    person_agents = [a for a in base_model.schedule.agents if isinstance(a, PersonAgent)]
    service_agents = [a for a in base_model.schedule.agents if isinstance(a, ServiceAgent)]
    
    assert len(person_agents) == 100
    assert len(service_agents) == 1

    # Check service agent parameters
    service = service_agents[0]
    assert service.base_make_intervention_prob == 0.3
    assert service.mecc_effect == 0.8
    assert not service.mecc_trained

def test_service_intervention_probability():
    """Test that service intervention probability changes correctly with MECC training"""
    params = {
        "N_people": 1,
        "N_service": 1,
        "mecc_effect": 0.8,
        "base_make_intervention_prob": 0.3,
        "visit_prob": 0.5,
        "seed": 42
    }
    
    # Test without MECC training
    model_no_mecc = MECC_Model(**params, mecc_trained=False)
    service_no_mecc = [a for a in model_no_mecc.schedule.agents if isinstance(a, ServiceAgent)][0]
    assert service_no_mecc.make_intervention_prob == 0.3

    # Test with MECC training
    model_with_mecc = MECC_Model(**params, mecc_trained=True)
    service_with_mecc = [a for a in model_with_mecc.schedule.agents if isinstance(a, ServiceAgent)][0]
    assert service_with_mecc.make_intervention_prob == 0.8

def test_contact_and_intervention_tracking():
    """Test that contacts and interventions are properly tracked"""
    params = {
        "N_people": 1,
        "N_service": 1,
        "mecc_effect": 1.0,  # Always intervene when trained
        "base_make_intervention_prob": 0.0,  # Never intervene when untrained
        "visit_prob": 1.0,  # Always visit
        "seed": 42
    }

    # Test without MECC training
    model_no_mecc = MECC_Model(**params, mecc_trained=False)
    model_no_mecc.step()
    
    service_no_mecc = [a for a in model_no_mecc.schedule.agents if isinstance(a, ServiceAgent)][0]
    assert service_no_mecc.contacts_made == 1
    assert service_no_mecc.interventions_made == 0

    # Test with MECC training
    model_with_mecc = MECC_Model(**params, mecc_trained=True)
    model_with_mecc.step()
    
    service_with_mecc = [a for a in model_with_mecc.schedule.agents if isinstance(a, ServiceAgent)][0]
    assert service_with_mecc.contacts_made == 1
    assert service_with_mecc.interventions_made == 1

def test_data_collection():
    """Test that the model correctly collects data"""
    params = {
        "N_people": 10,
        "N_service": 1,
        "mecc_effect": 1.0,
        "base_make_intervention_prob": 0.0,
        "visit_prob": 1.0,
        "seed": 42
    }

    # Run model for a few steps
    model = MECC_Model(**params, mecc_trained=True)
    for _ in range(3):
        model.step()

    # Get collected data
    data = model.datacollector.get_model_vars_dataframe()

    # Check that we have the expected metrics
    assert "Total Contacts" in data.columns
    assert "Total Interventions" in data.columns

    # Check that values are non-negative and contacts >= interventions
    assert (data["Total Contacts"] >= 0).all()
    assert (data["Total Interventions"] >= 0).all()
    assert (data["Total Contacts"] >= data["Total Interventions"]).all()

def test_visit_probability():
    """Test that visit probability affects contact rate"""
    def run_model_with_visit_prob(visit_prob):
        params = {
            "N_people": 1000,  # Large number for stable statistics
            "N_service": 1,
            "mecc_effect": 0.5,
            "base_make_intervention_prob": 0.5,
            "visit_prob": visit_prob,
            "seed": 42
        }
        model = MECC_Model(**params)
        
        # Run for multiple steps to get more stable statistics
        for _ in range(5):
            model.step()
            
        return model.datacollector.get_model_vars_dataframe()["Total Contacts"].iloc[-1]

    # Test with different visit probabilities
    contacts_low = run_model_with_visit_prob(0.1)
    contacts_high = run_model_with_visit_prob(0.9)

    # Higher visit probability should result in more contacts
    # With 1000 people, 5 steps:
    # Low prob (0.1): expect ~500 contacts (1000 * 0.1 * 5)
    # High prob (0.9): expect ~4500 contacts (1000 * 0.9 * 5)
    assert contacts_high > 3 * contacts_low  # High should be significantly more than low

def test_intervention_tracking():
    """Test that interventions are properly tracked for each person"""
    params = {
        "N_people": 100,
        "N_service": 1,
        "mecc_effect": 1.0,  # Always intervene
        "base_make_intervention_prob": 1.0,
        "visit_prob": 1.0,  # Always visit
        "seed": 42
    }
    
    model = MECC_Model(**params)
    model.step()
    
    # After one step, all people should have received an intervention
    person_agents = [a for a in model.schedule.agents if isinstance(a, PersonAgent)]
    assert all(p.interventions_received == 1 for p in person_agents)

def test_multiple_services():
    """Test that multiple services function correctly"""
    params = {
        "N_people": 100,
        "N_service": 3,  # Multiple services
        "mecc_effect": 0.8,
        "base_make_intervention_prob": 0.3,
        "visit_prob": 1.0,
        "seed": 42
    }
    
    model = MECC_Model(**params)
    model.step()
    
    # Check that all services are being used
    service_agents = [a for a in model.schedule.agents if isinstance(a, ServiceAgent)]
    assert all(s.contacts_made > 0 for s in service_agents)
