import pytest
from hypothesis import given, settings, strategies as st
import numpy as np
from streamlit_app.model_two_types_mecc import (
    MECC_Model, SmokeModel_MECC_Model,
    SmokeModel_PersonAgent, SmokeModel_ServiceAgent,
    PersonAgent, ServiceAgent
)

# Strategy for probability values between 0 and 1
prob_strategy = st.floats(min_value=0.0, max_value=1.0, allow_infinity=False, allow_nan=False)

# Strategy for small positive integers (to keep tests manageable)
pos_int_strategy = st.integers(min_value=10, max_value=50)  # Reduced range for faster tests

# Strategy for positive floats greater than 1 (for intervention effects)
pos_float_strategy = st.floats(min_value=1.0, max_value=3.0, allow_infinity=False, allow_nan=False)

@settings(deadline=500, max_examples=20)  # Increased deadline, reduced examples
@given(
    N_people=pos_int_strategy,
    N_service=st.integers(min_value=1, max_value=3),  # Limit number of services
    mecc_effect=prob_strategy,
    base_make_intervention_prob=prob_strategy,
    visit_prob=prob_strategy
)
def test_base_model_invariants(N_people, N_service, mecc_effect, base_make_intervention_prob, visit_prob):
    """Test that the base model maintains its invariants across different parameter values"""
    model = MECC_Model(
        N_people=N_people,
        N_service=N_service,
        mecc_effect=mecc_effect,
        base_make_intervention_prob=base_make_intervention_prob,
        visit_prob=visit_prob,
        seed=42
    )
    
    # Run for a few steps
    for _ in range(2):  # Reduced number of steps for faster testing
        # Check agent counts before step
        person_agents = [a for a in model.schedule.agents if isinstance(a, PersonAgent)]
        service_agents = [a for a in model.schedule.agents if isinstance(a, ServiceAgent)]
        assert len(person_agents) == N_people
        assert len(service_agents) == N_service
        
        # Run step and check data
        model.step()
        data = model.datacollector.get_model_vars_dataframe()
        
        # Check invariants
        assert (data["Total Contacts"] >= 0).all()
        assert (data["Total Interventions"] >= 0).all()
        assert (data["Total Interventions"] <= data["Total Contacts"]).all()

@settings(deadline=500, max_examples=20)  # Increased deadline, reduced examples
@given(
    N_people=pos_int_strategy,
    N_service=st.integers(min_value=1, max_value=3),
    mecc_effect=prob_strategy,
    base_make_intervention_prob=prob_strategy,
    visit_prob=prob_strategy,
    initial_smoking_prob=prob_strategy,
    quit_attempt_prob=prob_strategy,
    base_smoke_relapse_prob=prob_strategy,
    intervention_effect=pos_float_strategy
)
def test_smoke_model_invariants(
    N_people, N_service, mecc_effect, base_make_intervention_prob, visit_prob,
    initial_smoking_prob, quit_attempt_prob, base_smoke_relapse_prob, intervention_effect
):
    """Test that the smoking model maintains its invariants across different parameter values"""
    model = SmokeModel_MECC_Model(
        N_people=N_people,
        N_service=N_service,
        mecc_effect=mecc_effect,
        base_make_intervention_prob=base_make_intervention_prob,
        visit_prob=visit_prob,
        initial_smoking_prob=initial_smoking_prob,
        quit_attempt_prob=quit_attempt_prob,
        base_smoke_relapse_prob=base_smoke_relapse_prob,
        intervention_effect=intervention_effect,
        seed=42,
        mecc_trained=False
    )
    
    # Check initial state
    person_agents = [a for a in model.schedule.agents if isinstance(a, SmokeModel_PersonAgent)]
    initial_smokers = sum(1 for a in person_agents if a.smoker)
    assert 0 <= initial_smokers <= N_people
    
    # Run for a few steps
    for step in range(2):  # Reduced number of steps for faster testing
        model.step()
        data = model.datacollector.get_model_vars_dataframe()
        
        # Basic invariants that must always hold
        assert (data["Total Smoking"] >= 0).all()
        assert (data["Total Not Smoking"] >= 0).all()
        assert (data["Total Smoking"] + data["Total Not Smoking"] == N_people).all()
        
        # Event invariants
        assert (data["Total Quit Attempts"] >= 0).all()
        assert (data["Total Quit Smoking"] >= 0).all()
        assert (data["Total Quit Smoking"] <= data["Total Quit Attempts"]).all()
        
        # Contact and intervention invariants
        assert (data["Total Contacts"] >= 0).all()
        assert (data["Total Interventions"] >= 0).all()
        assert (data["Total Interventions"] <= data["Total Contacts"]).all()
        assert (data["Smokers With an Intervention"] >= 0).all()
        assert (data["Smokers With an Intervention"] <= N_people).all()
        
        # Smoke-free months invariant (if there are non-smokers)
        if data["Total Not Smoking"].iloc[-1] > 0:
            assert (data["Average Months Smoke Free"] >= 0).all()
            # Months smoke free should not exceed simulation steps
            assert (data["Average Months Smoke Free"] <= step + 1).all()

@settings(deadline=500, max_examples=20)
@given(
    visit_prob=prob_strategy,
    base_make_intervention_prob=prob_strategy,
    # Ensure MECC effect is higher than base intervention probability
    mecc_effect=st.floats(min_value=0.5, max_value=1.0)
)
def test_mecc_training_effect(visit_prob, base_make_intervention_prob, mecc_effect):
    """Test that MECC training consistently improves intervention rates"""
    # Adjust base_make_intervention_prob to be less than mecc_effect
    base_make_intervention_prob = min(base_make_intervention_prob, mecc_effect * 0.8)
    
    def run_model(mecc_trained):
        model = MECC_Model(
            N_people=20,  # Fixed smaller population for faster testing
            N_service=1,
            mecc_effect=mecc_effect,
            base_make_intervention_prob=base_make_intervention_prob,
            visit_prob=visit_prob,
            mecc_trained=mecc_trained,
            seed=42
        )
        
        # Check initial state
        service_agents = [a for a in model.schedule.agents if isinstance(a, ServiceAgent)]
        assert len(service_agents) == 1
        service = service_agents[0]
        
        # Verify intervention probability based on MECC training
        if mecc_trained:
            assert service.make_intervention_prob == mecc_effect
        else:
            assert service.make_intervention_prob == base_make_intervention_prob
        
        # Run for multiple steps to get more stable results
        for _ in range(3):
            model.step()
        
        data = model.datacollector.get_model_vars_dataframe()
        return data["Total Interventions"].iloc[-1]
    
    interventions_no_mecc = run_model(False)
    interventions_with_mecc = run_model(True)
    
    # MECC training should increase intervention rate
    assert interventions_with_mecc >= interventions_no_mecc

@settings(deadline=500, max_examples=10)  # Reduced examples for faster testing
@given(
    # Use discrete values for more predictable behavior
    quit_attempt_prob=st.sampled_from([0.2, 0.3, 0.4]),
    intervention_effect=st.sampled_from([1.5, 2.0, 2.5])
)
def test_intervention_quit_relationship(quit_attempt_prob, intervention_effect):
    """Test that interventions consistently affect quit attempts as expected"""
    def run_model(with_interventions):
        model = SmokeModel_MECC_Model(
            N_people=20,  # Smaller population for faster testing
            N_service=1,
            mecc_effect=1.0,  # Always intervene when trained
            base_make_intervention_prob=0.0,  # Never intervene without MECC
            visit_prob=1.0,  # Always visit
            initial_smoking_prob=1.0,  # All start as smokers
            quit_attempt_prob=quit_attempt_prob,
            base_smoke_relapse_prob=0.0,  # No relapse
            intervention_effect=intervention_effect,
            seed=42,
            mecc_trained=with_interventions
        )
        
        # Check initial quit probability before any steps
        person_agents = [a for a in model.schedule.agents if isinstance(a, SmokeModel_PersonAgent)]
        initial_quit_prob = sum(a.quit_attempt_prob for a in person_agents) / len(person_agents)
        
        # First step: apply interventions
        model.step()
        
        # Check quit probabilities after interventions but before next step
        post_intervention_quit_prob = sum(a.quit_attempt_prob for a in person_agents) / len(person_agents)
        
        # Second step: see the effect of modified quit probabilities
        model.step()
        data = model.datacollector.get_model_vars_dataframe()
        
        return {
            'quit_attempts': data["Total Quit Attempts"].iloc[-1],
            'initial_quit_prob': initial_quit_prob,
            'post_intervention_quit_prob': post_intervention_quit_prob,
            'interventions': data["Total Interventions"].iloc[-1]
        }
    
    # Run both scenarios
    result_without = run_model(False)
    result_with = run_model(True)
    
    # Initial quit probability should match the input parameter in both cases
    assert abs(result_without['initial_quit_prob'] - quit_attempt_prob) < 0.01
    assert abs(result_with['initial_quit_prob'] - quit_attempt_prob) < 0.01
    
    # Without interventions, quit probability should remain unchanged
    assert abs(result_without['post_intervention_quit_prob'] - quit_attempt_prob) < 0.01
    
    # With interventions, quit probability should increase by intervention_effect
    expected_with_prob = quit_attempt_prob * intervention_effect
    assert abs(result_with['post_intervention_quit_prob'] - expected_with_prob) < 0.01
    
    # Verify interventions only occurred in the "with" case
    assert result_without['interventions'] == 0
    assert result_with['interventions'] > 0
    
    # Over multiple runs, this should lead to more quit attempts
    total_attempts_without = 0
    total_attempts_with = 0
    
    # Run multiple times to account for randomness
    for _ in range(5):
        total_attempts_without += run_model(False)['quit_attempts']
        total_attempts_with += run_model(True)['quit_attempts']
    
    assert total_attempts_with > total_attempts_without

@settings(deadline=500, max_examples=10)
@given(
    initial_smoking_prob=prob_strategy,
    quit_attempt_prob=prob_strategy,
    base_smoke_relapse_prob=prob_strategy
)
def test_population_conservation(initial_smoking_prob, quit_attempt_prob, base_smoke_relapse_prob):
    """Test that population is conserved and state transitions are valid"""
    model = SmokeModel_MECC_Model(
        N_people=20,
        N_service=1,
        mecc_effect=0.8,
        base_make_intervention_prob=0.3,
        visit_prob=0.2,
        initial_smoking_prob=initial_smoking_prob,
        quit_attempt_prob=quit_attempt_prob,
        base_smoke_relapse_prob=base_smoke_relapse_prob,
        intervention_effect=1.5,
        seed=42,
        mecc_trained=True
    )
    
    # Run for several steps
    for _ in range(5):
        # Check population conservation
        person_agents = [a for a in model.schedule.agents if isinstance(a, SmokeModel_PersonAgent)]
        assert len(person_agents) == 20, "Population size should remain constant"
        
        # Check state consistency
        for agent in person_agents:
            # Can't be both never-smoked and smoker
            assert not (agent.never_smoked and agent.smoker), \
                "Agent cannot be never-smoked and current smoker"
            
            # If smoke-free months > 0, must not be smoking
            if agent.months_smoke_free > 0:
                assert not agent.smoker, \
                    "Agent with smoke-free months cannot be smoking"
        
        model.step()
        
        # Check data consistency
        data = model.datacollector.get_model_vars_dataframe()
        total = data["Total Smoking"].iloc[-1] + data["Total Not Smoking"].iloc[-1]
        assert total == 20, "Total population in metrics should remain constant"

@settings(deadline=500, max_examples=10)
@given(
    base_smoke_relapse_prob=prob_strategy,
    quit_attempt_prob=prob_strategy
)
def test_time_based_properties(base_smoke_relapse_prob, quit_attempt_prob):
    """Test properties that depend on time progression"""
    model = SmokeModel_MECC_Model(
        N_people=20,
        N_service=1,
        mecc_effect=0.8,
        base_make_intervention_prob=0.3,
        visit_prob=0.2,
        initial_smoking_prob=1.0,  # Start all as smokers
        quit_attempt_prob=quit_attempt_prob,
        base_smoke_relapse_prob=base_smoke_relapse_prob,
        intervention_effect=1.5,
        seed=42,
        mecc_trained=True
    )
    
    # Track smoke-free months and relapse rates
    smoke_free_months = []
    relapse_rates = []
    
    for step in range(5):
        model.step()
        data = model.datacollector.get_model_vars_dataframe()
        
        # Get current smoke-free months
        if data["Total Not Smoking"].iloc[-1] > 0:
            smoke_free_months.append(data["Average Months Smoke Free"].iloc[-1])
        
        # Calculate effective relapse rate
        person_agents = [a for a in model.schedule.agents if isinstance(a, SmokeModel_PersonAgent)]
        ex_smokers = [a for a in person_agents if not a.smoker and not a.never_smoked]
        if ex_smokers:
            avg_months_free = sum(a.months_smoke_free for a in ex_smokers) / len(ex_smokers)
            expected_rate = base_smoke_relapse_prob * (0.95 ** avg_months_free)
            relapse_rates.append(expected_rate)
    
    # Smoke-free months should increase monotonically
    if len(smoke_free_months) > 1:
        assert all(b >= a for a, b in zip(smoke_free_months[:-1], smoke_free_months[1:])), \
            "Smoke-free months should not decrease"
    
    # Relapse rates should decrease over time
    if len(relapse_rates) > 1:
        assert all(b <= a for a, b in zip(relapse_rates[:-1], relapse_rates[1:])), \
            "Relapse rates should decrease over time"
