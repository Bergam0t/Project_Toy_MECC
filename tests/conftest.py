import pytest
from streamlit_app.model_two_types_mecc import MECC_Model, SmokeModel_MECC_Model

@pytest.fixture
def base_model_params():
    return {
        "N_people": 100,
        "N_service": 1,
        "mecc_effect": 0.8,
        "base_make_intervention_prob": 0.3,
        "visit_prob": 0.5,
        "mecc_trained": False,
        "seed": 42
    }

@pytest.fixture
def smoke_model_params(base_model_params):
    return {
        **base_model_params,
        "initial_smoking_prob": 0.2,
        "quit_attempt_prob": 0.1,
        "base_smoke_relapse_prob": 0.3,
        "intervention_effect": 1.5
    }

@pytest.fixture
def base_model(base_model_params):
    return MECC_Model(**base_model_params)

@pytest.fixture
def smoke_model(smoke_model_params):
    return SmokeModel_MECC_Model(**smoke_model_params)
