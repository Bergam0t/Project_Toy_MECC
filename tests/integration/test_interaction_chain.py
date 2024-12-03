import pytest
from streamlit_app.model_two_types_mecc import SmokeModel_MECC_Model

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
            'quit_smoking': data["Total Quit Smoking"].iloc[-1],
            'total_smoking': data["Total Smoking"].iloc[-1]
        })
    
    # Verify each step of the chain
    for step in range(1, len(history)):
        # 1. Contacts should occur with high visit probability
        assert history[step]['contacts'] > history[step-1]['contacts'], \
            f"Step {step}: Contacts should increase. Got {history[step]['contacts']} vs {history[step-1]['contacts']}"
        
        # 2. Interventions should follow contacts
        assert history[step]['interventions'] > history[step-1]['interventions'], \
            f"Step {step}: Interventions should increase. Got {history[step]['interventions']} vs {history[step-1]['interventions']}"
        
        # 3. Quit attempts should increase until population saturates
        if history[step-1]['total_smoking'] > 0:  # Only expect more quit attempts if there are smokers left
            assert history[step]['quit_attempts'] >= history[step-1]['quit_attempts'], \
                f"Step {step}: Quit attempts should not decrease while smokers remain. Got {history[step]['quit_attempts']} vs {history[step-1]['quit_attempts']}"
        
        # 4. Some quit attempts should succeed
        assert history[step]['quit_smoking'] > 0, \
            f"Step {step}: Should see successful quits. Got {history[step]['quit_smoking']}"
        
        # 5. Chain should be properly ordered
        assert history[step]['contacts'] >= history[step]['interventions'], \
            f"Step {step}: Cannot have more interventions than contacts"
        assert history[step]['quit_smoking'] <= history[step]['quit_attempts'], \
            f"Step {step}: Cannot have more successful quits than attempts"

def test_intervention_effectiveness():
    """Test that interventions effectively increase quit attempts"""
    base_params = {
        "N_people": 100,
        "N_service": 1,
        "mecc_effect": 1.0,
        "base_make_intervention_prob": 1.0,
        "visit_prob": 1.0,
        "initial_smoking_prob": 1.0,
        "quit_attempt_prob": 0.2,
        "base_smoke_relapse_prob": 0.0,
        "seed": 42,
        "mecc_trained": True
    }
    
    # Run with strong intervention effect
    strong_model = SmokeModel_MECC_Model(**{**base_params, "intervention_effect": 2.0})
    
    # Run with weak intervention effect
    weak_model = SmokeModel_MECC_Model(**{**base_params, "intervention_effect": 1.1})
    
    # Track quit attempts for both models
    strong_attempts = []
    weak_attempts = []
    
    for _ in range(5):
        strong_model.step()
        weak_model.step()
        
        strong_data = strong_model.datacollector.get_model_vars_dataframe()
        weak_data = weak_model.datacollector.get_model_vars_dataframe()
        
        strong_attempts.append(strong_data["Total Quit Attempts"].iloc[-1])
        weak_attempts.append(weak_data["Total Quit Attempts"].iloc[-1])
    
    # Strong interventions should lead to more quit attempts
    assert strong_attempts[-1] > weak_attempts[-1], \
        f"Strong interventions should lead to more quit attempts. Got {strong_attempts[-1]} vs {weak_attempts[-1]}"
    
    # Calculate early quit attempt rates (before saturation)
    early_strong_rate = strong_attempts[1] / base_params['N_people']
    early_weak_rate = weak_attempts[1] / base_params['N_people']
    
    # Strong intervention rate should be higher than weak rate
    assert early_strong_rate > early_weak_rate, \
        f"Strong intervention rate ({early_strong_rate:.2f}) should exceed weak rate ({early_weak_rate:.2f})"
    
    # Rate increase should be proportional to intervention effect difference
    rate_increase = early_strong_rate / early_weak_rate
    effect_ratio = 2.0 / 1.1  # Strong effect / weak effect
    
    assert abs(rate_increase - effect_ratio) < 0.5, \
        f"Rate increase ({rate_increase:.2f}) should be close to effect ratio ({effect_ratio:.2f})"
