import streamlit as st
from logic_diagram import create_logic_diagram
import json
import os

# st.logo("resources/MECC.jpg")

st.title("Toy MECC - Making Every Contact Count")

# st.image("./resources/MECC.jpg", width=250)

st.write("https://github.com/DomRowney/Project_Toy_MECC.git")

st.write("""
A (toy) model for showing the benefit of Making Every Contact Count (MECC) Training.
         
Build a Streamlit app for an Agent Based Simulation.
The pop culture 80's references will all be in the form of toy robots.
There is an initial group of people and an initial group of government services.
People can have lifestyle factors: smoking/drinking/no exercise.
People may have a probability of making a quit attempt (smoking/drinking/no exercise) with a probability of success.
People have contact with government services at random.
Services can have MECC training, and therefore a probability that any contact will lead to a Very Brief Intervention.
Services with MECC training increase over time with a training rate.
A Very Brief Intervention increases the probability that a patient will make a quit attempt.
Outputs will be MECC training numbers, number of quit attempts, and number of successful quits over time.
""")

st.write("## Diagram of Agent Model Logic")
st.write("This diagram shows how a a person agent moves through the system")

st.image(create_logic_diagram()
         , caption="Diagram of Agent Model Logic"
         , use_column_width=False)

# initailise parameter variables for simulation - defaults
if 'N_people' not in st.session_state:
    st.session_state.N_people = 50

if 'initial_smoking_prob' not in st.session_state:
    st.session_state.initial_smoking_prob = 0.5

if 'visit_prob' not in st.session_state:
    st.session_state.visit_prob = 0.1

if 'quit_attempt_prob' not in st.session_state:
    st.session_state.quit_attempt_prob = 0.01

if 'base_smoke_relapse_prob' not in st.session_state:
    st.session_state.base_smoke_relapse_prob = 0.01

if 'base_make_intervention_prob' not in st.session_state:
    st.session_state.base_make_intervention_prob = 0.1

if 'mecc_effect' not in st.session_state:
    st.session_state.mecc_effect = 1.0

if 'intervention_effect' not in st.session_state:
    st.session_state.intervention_effect = 1.1

if 'model_seed' not in st.session_state:
    st.session_state.model_seed = 42

if 'num_steps' not in st.session_state:
    st.session_state.num_steps = 24

if 'animation_speed' not in st.session_state:
    st.session_state.animation_speed = 0.1

model_parameters = {
    "model_seed": st.session_state.model_seed,
    "N_people": st.session_state.N_people,
    "N_service": 1,
    "initial_smoking_prob": st.session_state.initial_smoking_prob,
    "visit_prob": st.session_state.visit_prob,
    "quit_attempt_prob": st.session_state.quit_attempt_prob,
    "base_smoke_relapse_prob": st.session_state.base_smoke_relapse_prob,
    "base_make_intervention_prob": st.session_state.base_make_intervention_prob,
    "mecc_effect": st.session_state.mecc_effect,
    "intervention_effect": st.session_state.intervention_effect,
    "num_steps" : st.session_state.num_steps,
    "animation_speed" : st.session_state.animation_speed
}

# save to json file to be used later for the quarto report
output_path = os.path.join(os.getcwd(),'streamlit_app','outputs')
json_path = os.path.join(output_path,'session_data.json')

with open(json_path, "w") as f:
    json.dump(model_parameters, f, indent=4)
