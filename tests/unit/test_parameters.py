import pytest
from hypothesis import given, settings, strategies as st
from streamlit_app.model_two_types_mecc import SmokeModel_MECC_Model

# Test strategies for different parameter types
prob_strategy = st.floats(min_value=0.0, max_value=1.0, allow_infinity=False, allow_nan=False)
population_strategy = st.integers(min_value=5, max_value=100)
steps_strategy = st.integers(min_value=1, max_value=120)
seed_strategy = st.integers(min_value=0)
intervention_effect_strategy = st.floats(min_value=0.0, max_value=10.0, allow_infinity=False, allow_nan=False)

def test_parameter_behavior():
    """Test model behavior with edge case parameters"""
    # Test valid parameters
    valid_params = {
        'N_people': 50,
        'N_service': 1,
        'mecc_effect': 0.9,
        'base_make_intervention_prob': 0.1,
        'visit_prob': 0.1,
        'initial_smoking_prob': 0.5,
        'quit_attempt_prob': 0.01,
        'base_smoke_relapse_prob': 0.01,
        'intervention_effect': 1.1,
        'seed': 42,
        'mecc_trained': False
    }
    
    # Model should initialize with valid parameters
    model = SmokeModel_MECC_Model(**valid_params)
    assert model is not None
    
    # Test edge case parameters
    edge_cases = [
        # Zero population
        {**valid_params, 'N_people': 0},
        # Zero service
        {**valid_params, 'N_service': 0},
        # Zero probabilities
        {**valid_params, 'visit_prob': 0.0},
        {**valid_params, 'quit_attempt_prob': 0.0},
        {**valid_params, 'base_smoke_relapse_prob': 0.0},
        # Maximum probabilities
        {**valid_params, 'visit_prob': 1.0},
        {**valid_params, 'quit_attempt_prob': 1.0},
        {**valid_params, 'base_smoke_relapse_prob': 1.0},
        # No intervention effect
        {**valid_params, 'intervention_effect': 0.0},
    ]
    
    for params in edge_cases:
        model = SmokeModel_MECC_Model(**params)
        # Model should initialize
        assert model is not None
        # Run one step to ensure it doesn't crash
        model.step()
        # Get data to verify it collected something
        data = model.datacollector.get_model_vars_dataframe()
        assert len(data) > 0

@given(
    N_people=population_strategy,
    visit_prob=prob_strategy,
    base_make_intervention_prob=prob_strategy,
    mecc_effect=prob_strategy,
    seed=seed_strategy
)
def test_generic_parameters(N_people, visit_prob, base_make_intervention_prob, mecc_effect, seed):
    """Test generic parameter validation using property-based testing"""
    params = {
        'N_people': N_people,
        'N_service': 1,
        'mecc_effect': mecc_effect,
        'base_make_intervention_prob': base_make_intervention_prob,
        'visit_prob': visit_prob,
        'initial_smoking_prob': 0.5,
        'quit_attempt_prob': 0.01,
        'base_smoke_relapse_prob': 0.01,
        'intervention_effect': 1.1,
        'seed': seed,
        'mecc_trained': False
    }
    
    model = SmokeModel_MECC_Model(**params)
    assert model is not None
    # Run one step to ensure parameters work in practice
    model.step()

@given(
    initial_smoking_prob=prob_strategy,
    quit_attempt_prob=prob_strategy,
    base_smoke_relapse_prob=prob_strategy,
    intervention_effect=intervention_effect_strategy
)
def test_smoking_parameters(initial_smoking_prob, quit_attempt_prob, base_smoke_relapse_prob, intervention_effect):
    """Test smoking-specific parameter validation using property-based testing"""
    params = {
        'N_people': 50,
        'N_service': 1,
        'mecc_effect': 0.9,
        'base_make_intervention_prob': 0.1,
        'visit_prob': 0.1,
        'initial_smoking_prob': initial_smoking_prob,
        'quit_attempt_prob': quit_attempt_prob,
        'base_smoke_relapse_prob': base_smoke_relapse_prob,
        'intervention_effect': intervention_effect,
        'seed': 42,
        'mecc_trained': False
    }
    
    model = SmokeModel_MECC_Model(**params)
    assert model is not None
    # Run one step to ensure parameters work in practice
    model.step()

def test_parameter_relationships():
    """Test relationships between parameters"""
    params = {
        'N_people': 50,
        'N_service': 1,
        'mecc_effect': 0.9,
        'base_make_intervention_prob': 0.1,
        'visit_prob': 0.1,
        'initial_smoking_prob': 0.5,
        'quit_attempt_prob': 0.01,
        'base_smoke_relapse_prob': 0.01,
        'intervention_effect': 1.1,
        'seed': 42,
        'mecc_trained': False
    }
    
    model = SmokeModel_MECC_Model(**params)
    
    # MECC effect should be higher than base intervention probability
    assert model.mecc_effect >= model.base_make_intervention_prob, \
        "MECC training should improve intervention probability"
    
    # Intervention effect should be positive
    assert model.intervention_effect > 0, \
        "Intervention effect must be positive"
    
    # Service count should be reasonable relative to population
    assert model.N_service <= model.N_people / 10, \
        "Too many services relative to population"

def test_parameter_dependencies():
    """Test dependencies between parameters"""
    base_params = {
        'N_people': 50,
        'N_service': 1,
        'mecc_effect': 0.9,
        'base_make_intervention_prob': 0.1,
        'visit_prob': 0.1,
        'initial_smoking_prob': 0.5,
        'quit_attempt_prob': 0.01,
        'base_smoke_relapse_prob': 0.01,
        'intervention_effect': 1.1,
        'seed': 42,
        'mecc_trained': False
    }
    
    # Test MECC training dependency
    model_untrained = SmokeModel_MECC_Model(**base_params)
    model_trained = SmokeModel_MECC_Model(**{**base_params, 'mecc_trained': True})
    
    # Get service agents
    untrained_service = [a for a in model_untrained.schedule.agents if not hasattr(a, 'smoker')][0]
    trained_service = [a for a in model_trained.schedule.agents if not hasattr(a, 'smoker')][0]
    
    # Verify MECC training affects intervention probability
    assert untrained_service.make_intervention_prob == base_params['base_make_intervention_prob']
    assert trained_service.make_intervention_prob == base_params['mecc_effect']
    
    # Test intervention effect dependency
    high_effect_params = {**base_params, 'intervention_effect': 2.0}
    low_effect_params = {**base_params, 'intervention_effect': 1.1}
    
    model_high = SmokeModel_MECC_Model(**high_effect_params)
    model_low = SmokeModel_MECC_Model(**low_effect_params)
    
    # Run both models
    model_high.step()
    model_low.step()
    
    # Higher intervention effect should lead to more quit attempts
    high_data = model_high.datacollector.get_model_vars_dataframe()
    low_data = model_low.datacollector.get_model_vars_dataframe()
    
    assert high_data["Total Quit Attempts"].iloc[-1] >= low_data["Total Quit Attempts"].iloc[-1], \
        "Higher intervention effect should lead to more quit attempts"

def test_parameter_effects():
    """Test that parameters have their intended effects"""
    base_params = {
        'N_people': 50,
        'N_service': 1,
        'mecc_effect': 0.9,
        'base_make_intervention_prob': 0.1,
        'visit_prob': 0.1,
        'initial_smoking_prob': 0.5,
        'quit_attempt_prob': 0.01,
        'base_smoke_relapse_prob': 0.01,
        'intervention_effect': 1.1,
        'seed': 42,
        'mecc_trained': False
    }
    
    # Test visit probability effect
    high_visit = SmokeModel_MECC_Model(**{**base_params, 'visit_prob': 1.0})
    low_visit = SmokeModel_MECC_Model(**{**base_params, 'visit_prob': 0.1})
    
    # Run multiple steps to accumulate contacts
    for _ in range(3):
        high_visit.step()
        low_visit.step()
    
    high_data = high_visit.datacollector.get_model_vars_dataframe()
    low_data = low_visit.datacollector.get_model_vars_dataframe()
    
    assert high_data["Total Contacts"].iloc[-1] > low_data["Total Contacts"].iloc[-1], \
        f"Higher visit probability should lead to more contacts. Got {high_data['Total Contacts'].iloc[-1]} vs {low_data['Total Contacts'].iloc[-1]}"
    
    # Test initial smoking probability effect
    high_smoking = SmokeModel_MECC_Model(**{**base_params, 'initial_smoking_prob': 1.0})
    low_smoking = SmokeModel_MECC_Model(**{**base_params, 'initial_smoking_prob': 0.0})
    
    # Check initial state
    high_smokers = sum(1 for a in high_smoking.schedule.agents if hasattr(a, 'smoker') and a.smoker)
    low_smokers = sum(1 for a in low_smoking.schedule.agents if hasattr(a, 'smoker') and a.smoker)
    
    assert high_smokers > low_smokers, \
        f"Higher initial smoking probability should lead to more smokers. Got {high_smokers} vs {low_smokers}"
    
    # Test quit attempt probability effect
    high_quit = SmokeModel_MECC_Model(**{**base_params, 'quit_attempt_prob': 0.5})
    low_quit = SmokeModel_MECC_Model(**{**base_params, 'quit_attempt_prob': 0.1})
    
    # Run multiple steps to accumulate quit attempts
    for _ in range(3):
        high_quit.step()
        low_quit.step()
    
    high_data = high_quit.datacollector.get_model_vars_dataframe()
    low_data = low_quit.datacollector.get_model_vars_dataframe()
    
    assert high_data["Total Quit Attempts"].iloc[-1] > low_data["Total Quit Attempts"].iloc[-1], \
        f"Higher quit probability should lead to more quit attempts. Got {high_data['Total Quit Attempts'].iloc[-1]} vs {low_data['Total Quit Attempts'].iloc[-1]}"

def test_simulation_parameters():
    """Test simulation-specific parameters"""
    base_params = {
        'N_people': 50,
        'N_service': 1,
        'mecc_effect': 0.9,
        'base_make_intervention_prob': 0.1,
        'visit_prob': 0.1,
        'initial_smoking_prob': 0.5,
        'quit_attempt_prob': 0.01,
        'base_smoke_relapse_prob': 0.01,
        'intervention_effect': 1.1,
        'seed': 42,
        'mecc_trained': False
    }
    
    # Test different step counts
    model_short = SmokeModel_MECC_Model(**base_params)
    model_long = SmokeModel_MECC_Model(**base_params)
    
    # Run for different numbers of steps
    for _ in range(3):  # Short run
        model_short.step()
    
    for _ in range(10):  # Long run
        model_long.step()
    
    short_data = model_short.datacollector.get_model_vars_dataframe()
    long_data = model_long.datacollector.get_model_vars_dataframe()
    
    # More steps should lead to more accumulated events
    assert len(long_data) > len(short_data), \
        f"Longer simulation should have more data points. Got {len(long_data)} vs {len(short_data)}"
    
    assert long_data["Total Contacts"].iloc[-1] > short_data["Total Contacts"].iloc[-1], \
        "Longer simulation should accumulate more contacts"
    
    assert long_data["Total Quit Attempts"].iloc[-1] > short_data["Total Quit Attempts"].iloc[-1], \
        "Longer simulation should accumulate more quit attempts"

def test_parameter_combinations():
    """Test combinations of related parameters"""
    base_params = {
        'N_people': 50,
        'N_service': 1,
        'mecc_effect': 0.9,
        'base_make_intervention_prob': 0.1,
        'visit_prob': 0.1,
        'initial_smoking_prob': 0.5,
        'quit_attempt_prob': 0.01,
        'base_smoke_relapse_prob': 0.01,
        'intervention_effect': 1.1,
        'seed': 42,
        'mecc_trained': False
    }
    
    # Test high visit + high intervention probability
    high_interaction_params = {
        **base_params,
        'visit_prob': 1.0,
        'base_make_intervention_prob': 1.0
    }
    model_high_interaction = SmokeModel_MECC_Model(**high_interaction_params)
    
    # Test high quit + high relapse probability
    high_turnover_params = {
        **base_params,
        'quit_attempt_prob': 0.5,
        'base_smoke_relapse_prob': 0.5
    }
    model_high_turnover = SmokeModel_MECC_Model(**high_turnover_params)
    
    # Run both models
    for _ in range(3):
        model_high_interaction.step()
        model_high_turnover.step()
    
    high_interaction_data = model_high_interaction.datacollector.get_model_vars_dataframe()
    high_turnover_data = model_high_turnover.datacollector.get_model_vars_dataframe()
    
    # High interaction should lead to more contacts and interventions
    assert high_interaction_data["Total Contacts"].iloc[-1] > 0, \
        "High visit + intervention probability should result in contacts"
    assert high_interaction_data["Total Interventions"].iloc[-1] > 0, \
        "High visit + intervention probability should result in interventions"
    
    # High turnover should show both quit attempts and relapses
    assert high_turnover_data["Total Quit Attempts"].iloc[-1] > 0, \
        "High quit probability should result in quit attempts"
    
    # Check that smoking population changes over time with high turnover
    smoking_changes = high_turnover_data["Total Smoking"].diff().abs()
    assert smoking_changes.mean() > 0, \
        "High quit + relapse probability should result in population changes"
