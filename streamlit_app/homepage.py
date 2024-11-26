import streamlit as st
from logic_diagram import create_logic_diagram
import json
import os

# st.logo("resources/MECC.jpg")

st.title("Toy MECC :material/smart_toy:")
st.write("## _Making Every Contact Count_")
# st.image("./resources/MECC.jpg", width=250)

st.write("""
A (toy) model for showing the benefit of Making Every Contact Count (MECC) Training.
        
This app was built as part of the [HSMA](https://hsma-programme.github.io/hsma_site/) 6 Hackday 2024 and 
the source code is available on [GitHub](https://github.com/DomRowney/Project_Toy_MECC.git)
""")

st.write("#### Explanation")
st.write("""
The model is an Agent based simulation:

+ There is an initial group of people (agents) and an initial group of services.
+ A certain proportion of people have lifestyle factors: smoking.
        People cannot start smoking if they never had to start with.
+ People may have a probability of making a smoking quit attempt each month
+ People have a chance of restarting smoking,
          this chance decreases the longer a person is smoke free.
+ People have contact with government services at random with a certain probability
+ People in contact with services have a chance of having a Very Brief Intervention.        
+ A Very Brief Intervention increases the probability that a person will make a quit attempt.
         It does not effect the chance that a person will stay smoke free.
+ Services can have MECC training, which increases the a probability that
          any contact will lead to a Very Brief Intervention.
+ The model compares results for the same simultion with and without MECC training.
                           
You can change all these probabilites on the:""") 
st.page_link('./parameters.py',label='Parameters for Simulation')

st.write("#### Diagram of Agent Model Logic")
st.write("This diagram shows how a a person agent moves through the system")

st.image(create_logic_diagram()
         , caption="Diagram of Agent Model Logic"
         , use_column_width=False)

################################################################################

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
    st.session_state.mecc_effect = 0.9

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
