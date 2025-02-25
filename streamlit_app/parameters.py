## mesa_abs_two_types_mecc.py
import pandas as pd
import numpy as np
import streamlit as st
#import plotly.graph_objects as go
#from plotly.subplots import make_subplots
import time
from logic_diagram import create_logic_diagram, create_logic_diagram_SmokeModel
#from model_two_types_mecc import MECC_Model 
#from streamlit_model_functions import run_simulation_step, create_comparison_figure, create_MECC_model #, create_figure
#import random

st.title("Parameters")

tab1, tab2, tab3, tab4  = st.tabs(['Generic','Alcohol Advice','Smoking Cessation','Generic Monte Carlo'])

with tab1:
    st.markdown("### Generic Parameters")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Population")

        if 'N_people' not in st.session_state:
            st.session_state.N_people = 50
        st.session_state.N_people = st.slider("Number of People", 5, 100, st.session_state.N_people)

        if 'visit_prob' not in st.session_state:
            st.session_state.visit_prob = 0.1
        st.session_state.visit_prob = st.slider("Chance of Visiting a Service per Month", 0.0, 1.0, st.session_state.visit_prob)

    with col2:
        st.markdown("#### Service")

        if 'base_make_intervention_prob' not in st.session_state:
            st.session_state.base_make_intervention_prob = 0.1
        st.session_state.base_make_intervention_prob = st.slider("Chance a Brief Intervention Made Without MECC Training", 0.0, 1.0, st.session_state.base_make_intervention_prob)

        st.write("-----") #divider

        st.markdown("#### MECC Training")

        if 'mecc_effect' not in st.session_state:
            st.session_state.mecc_effect = 0.9
        st.session_state.mecc_effect = st.slider("Chance Making a Brief Intervention After MECC Training", 0.0, 1.0, st.session_state.mecc_effect)

    with col3:
        st.markdown("#### Simulation")

        if 'model_seed' not in st.session_state:
            st.session_state.model_seed = 42
        st.session_state.model_seed = st.number_input("Random Seed", min_value=0, max_value=None, value=st.session_state.model_seed, step=1)

        if 'num_steps' not in st.session_state:
            st.session_state.num_steps = 24
        st.session_state.num_steps = st.slider("Number of Months to Simulate", 1, 120, st.session_state.num_steps)

        if 'animation_speed' not in st.session_state:
            st.session_state.animation_speed = 0.1
        st.session_state.animation_speed = st.slider("Animation Speed (seconds)", 0)

    ## Logic Diagram
    with st.expander("Click here to view the logic diagram"):
        #col1a, col2a, col3a = st.columns(3)
        #with col2a:
        st.image(create_logic_diagram(number_labels = True)
            , caption="Diagram of Agent Model Logic"
            , use_column_width=False)

with tab2:
    st.markdown("### Alcohol Advice Parameters")


    colA, colB = st.columns(2)
    with colA:
        st.markdown("#### Population")

        st.write(f"Number of People: :blue-background[{st.session_state.N_people}]") 
        st.markdown("**Base Positive Change Chance**")
        if 'alcohol_change_prob_contemplation' not in st.session_state: 
            st.session_state.alcohol_change_prob_contemplation = 0.01
        st.session_state.alcohol_change_prob_contemplation =  st.slider(
                                                "Base Pre-Contemplation to Contemplation chance"
                                                , 0.0, 1.0
                                                , st.session_state.alcohol_change_prob_contemplation
                                                ,key='alcohol Contemplation')

        if 'alcohol_change_prob_preparation' not in st.session_state: 
            st.session_state.alcohol_change_prob_preparation = 0.01
        st.session_state.alcohol_change_prob_preparation =  st.slider(
                                                "Base Contemplation to Preparation chance"
                                                , 0.0, 1.0
                                                , st.session_state.alcohol_change_prob_preparation
                                                ,key='alcohol Preparation')

        if 'alcohol_change_prob_action' not in st.session_state: 
            st.session_state.alcohol_change_prob_action = 0.01
        st.session_state.alcohol_change_prob_action =  st.slider(
                                                "Base Preparation to Action chance"
                                                , 0.0, 1.0
                                                , st.session_state.alcohol_change_prob_action
                                                ,key='alcohol Action')
        
        st.markdown("**Lapse Chance**")
        if 'alcohol_lapse_prob_precontemplation' not in st.session_state: 
            st.session_state.alcohol_lapse_prob_precontemplation = 0.01
        st.session_state.alcohol_lapse_prob_precontemplation =  st.slider(
                                                "Base Contemplation to Pre-Contemplation lapse chance"
                                                , 0.0, 1.0
                                                , st.session_state.alcohol_lapse_prob_precontemplation
                                                ,key='alcohol lapse Pre-Contemplation')

        if 'alcohol_lapse_prob_contemplation' not in st.session_state: 
            st.session_state.alcohol_lapse_prob_contemplation = 0.01
        st.session_state.alcohol_lapse_prob_contemplation =  st.slider(
                                                "Base Preparation to Contemplation lapse chance"
                                                , 0.0, 1.0
                                                , st.session_state.alcohol_lapse_prob_contemplation
                                                ,key='alcohol lapse Contemplation')
        
        if 'alcohol_lapse_prob_preparation' not in st.session_state: 
            st.session_state.alcohol_lapse_prob_preparation = 0.01
        st.session_state.alcohol_lapse_prob_preparation =  st.slider(
                                                "Base Action to Preparation lapse chance"
                                                , 0.0, 1.0
                                                , st.session_state.alcohol_lapse_prob_preparation
                                                ,key='alcohol lapse Preparation')

    with colB:        
        st.markdown("#### Simulation")

        st.write(f"Random Seed: :blue-background[{st.session_state.model_seed}]")

        st.write(f"Number of Months to Simulate: :blue-background[{st.session_state.num_steps}]")

        st.write(f"Animation Speed (seconds): :blue-background[{st.session_state.animation_speed}]")

        
    st.markdown("#### Service")
    ## sets up one column for each service type

    alcohol_services = pd.DataFrame(
             {'Service': ['Job Centre','Benefits Office','Housing Officer','Community Hub']
            ,'Person Visit Probability': [0.0,0.0,0.0,0.0]
            ,'Chance a Brief Intervention Made Without MECC Training': [0.0,0.0,0.0,0.0]
            ,'MECC Trained': [True,True,True,True]
            ,'Chance Making a Brief Intervention After MECC Training': [0.0,0.0,0.0,0.0]
            ,'Post Intervention Pre-Contemplation to Contemplation chance': [0.0,0.0,0.0,0.0]
            ,'Post Intervention Contemplation to Preparation chance': [0.0,0.0,0.0,0.0]
            ,'Post Intervention Preparation to Action chance': [0.0,0.0,0.0,0.0]}
    )    

    alcohol_services = alcohol_services.set_index('Service')

    if 'alcohol_services_table' not in st.session_state:
        st.session_state.alcohol_services_table = alcohol_services

#    if 'alcohol_visit_prob' not in st.session_state:
#        st.session_state.alcohol_visit_prob = {
#                                'Job Centre': 0.0
#                            ,'Benefits Office': 0.0
#                            ,'Housing Officer': 0.0
#                            ,'Community Hub': 0.0}
#    if 'alcohol_base_make_intervention_prob' not in st.session_state:
#        st.session_state.alcohol_base_make_intervention_prob = {
#                                'Job Centre': 0.0
#                            ,'Benefits Office': 0.0
#                            ,'Housing Officer': 0.0
#                            ,'Community Hub': 0.0}
#    if 'alcohol_contemplation_intervention' not in st.session_state:
#        st.session_state.alcohol_contemplation_intervention = {
#                                'Job Centre': 0.0
#                            ,'Benefits Office': 0.0
#                            ,'Housing Officer': 0.0
#                            ,'Community Hub': 0.0}
#    if 'alcohol_preparation_intervention' not in st.session_state:
#        st.session_state.alcohol_preparation_intervention = {
#                                'Job Centre': 0.0
#                            ,'Benefits Office': 0.0
#                            ,'Housing Officer': 0.0
#                            ,'Community Hub': 0.0}
#    if 'alcohol_action_intervention' not in st.session_state:
#        st.session_state.alcohol_action_intervention = {
#                                'Job Centre': 0.0
#                            ,'Benefits Office': 0.0
#                            ,'Housing Officer': 0.0
#                            ,'Community Hub': 0.0}
#    if 'alcohol_mecc_trained' not in st.session_state:
#        st.session_state.alcohol_mecc_trained =  {
#                                                'Job Centre': True
#                                                ,'Benefits Office': True
#                                                ,'Housing Officer': True
#                                                ,'Community Hub': True}
#    if 'alcohol_mecc_effect' not in st.session_state:
#        st.session_state.alcohol_mecc_effect = {
#                                'Job Centre': 0.0
#                            ,'Benefits Office': 0.0
#                            ,'Housing Officer': 0.0
#                            ,'Community Hub': 0.0}
#
#    def update_alcohol_service_params():
#        alcohol_services_list = [ 'Job Centre'
#                                    ,'Benefits Office'
#                                    ,'Housing Officer'
#                                    ,'Community Hub']
#        print('Update alcohol service parameters')
#        for service in alcohol_services_list:
#            st.session_state.alcohol_visit_prob[service] = (
#                alcohol_services_edit.loc[service]['Person Visit Probability'])
#            print(f"{alcohol_services_edit.loc[service]['Person Visit Probability']}")
#        for service in alcohol_services_list:          
#            st.session_state.alcohol_base_make_intervention_prob[service] = (
#                alcohol_services_edit.loc[service]['Chance a Brief Intervention Made Without MECC Training'])        
#            #st.session_state.alcohol_mecc_trained[service] = (
#            #    alcohol_services_edit.loc[service]['MECC Trained'])
#            #st.session_state.alcohol_mecc_effect[service] = (
#            #    alcohol_services_edit.loc[service]['Chance Making a Brief Intervention After MECC Training'])
#            #st.session_state.alcohol_contemplation_intervention[service] = (
#            #    alcohol_services_edit.loc[service]['Post Intervention Pre-Contemplation to Contemplation chance'])
#            #st.session_state.alcohol_preparation_intervention[service] = (
#            #    alcohol_services_edit.loc[service]['Post Intervention Contemplation to Preparation chance'])
#            #st.session_state.alcohol_action_intervention[service] = (
#            #    alcohol_services_edit.loc[service]['Post Intervention Preparation to Action chance'])

    st.session_state.alcohol_services_table = st.data_editor(
        alcohol_services,
        disabled=["Service"],
        #on_change = update_alcohol_service_params,
        column_config={
            "Service": "Service",
            "Person Visit Probability": st.column_config.NumberColumn(
                "Person Visit Probability",
                width='medium',
                help="How likely is someone to visit in a month (0.0-1.0)?",
                min_value=0.0,
                max_value=1.0,
                step=0.01,),
            "Chance a Brief Intervention Made Without MECC Training": st.column_config.NumberColumn(
                "Chance a Brief Intervention Made Without MECC Training",
                width='medium',
                help="How likely is an intervention before MECC training (0.0-1.0)?",
                min_value=0.0,
                max_value=1.0,
                step=0.01,),                
            "MECC Trained":"MECC Trained",
            "Chance Making a Brief Intervention After MECC Training": st.column_config.NumberColumn(
                "Chance Making a Brief Intervention After MECC Training",
                width='medium',                
                help="How likely is an intervention after MECC training (0.0-1.0)?",
                min_value=0.0,
                max_value=1.0,
                step=0.01,),
            "Post Intervention Pre-Contemplation to Contemplation chance": st.column_config.NumberColumn(
                "Post Intervention Pre-Contemplation to Contemplation chance",
                width='medium',
                help="What does a person's chance of changing from" +
                        "Pre-Contemplation to Contemplation become" + 
                        "post-intervention (0.0-1.0)?",
                min_value=0.0,
                max_value=1.0,
                step=0.01,), 
            "Post Intervention Contemplation to Preparation chance": st.column_config.NumberColumn(
                "Post Intervention Contemplation to Preparation chance",
                width='medium',
                help="What does a person's chance of changing from" +
                        "Contemplation to Preparation become" + 
                        "post-intervention (0.0-1.0)?",
                min_value=0.0,
                max_value=1.0,
                step=0.01,),            
            "Post Intervention Preparation to Action chance": st.column_config.NumberColumn(
                "Post Intervention Preparation to Action chance",
                width='medium',           
                help="What does a person's chance of changing from" +
                        "Preparation to Action become" + 
                        "post-intervention (0.0-1.0)?",
                min_value=0.0,
                max_value=1.0,
                step=0.01,),                                                                    
                },
        )

    #update_alcohol_service_params()
    st.write(f"{st.session_state.alcohol_services_table.loc['Job Centre']['Person Visit Probability']}")
    
    for service in st.session_state.alcohol_services_table.index:
        st.write(f"{service}  visti prob = {st.session_state.alcohol_services_table.loc[service]['Person Visit Probability']}")
    
    #st.write(f'Job Centre Visit probability = {st.session_state.alcohol_visit_prob}')
    #st.write(f'Chance a Brief Intervention = {st.session_state.alcohol_base_make_intervention_prob}')

    #col1, col2, col3, col4 = st.columns(4)
    #column_dict = { 'Job Centre': col1
    #                ,'Benefits Office': col2
    #                ,'Housing Officer': col3
    #                ,'Community Hub': col4}

    ## makes sure service values exist in session state
    ## Most service values default to zero


    
    ### Creates each columnn based on the dictionary
    #for service in column_dict:
    #    with column_dict[service]:
    #        st.write(f'**{service}**')
    #        st.session_state.alcohol_visit_prob[service] = st.slider(
    #            'Person Visit Probability', 0.0, 1.0
    #            , st.session_state.alcohol_visit_prob[service]
    #            ,key = f'Visit Probability {service}')            
    #        st.session_state.alcohol_base_make_intervention_prob[service] = st.slider(
    #            'Chance a Brief Intervention Made Without MECC Training', 0.0, 1.0
    #            , st.session_state.alcohol_base_make_intervention_prob[service]
    #            , key = f'Base Intervetion {service}')
    #        st.session_state.alcohol_mecc_trained[service] = st.checkbox(
    #            'MECC Trained'
    #            ,key= f'MECC Trained {service}')
    #        st.session_state.alcohol_mecc_effect[service] = st.slider(
    #            "Training Effect on Intervention Chance", 0.0, 1.0
    #            , st.session_state.alcohol_mecc_effect[service]
    #            , key = f'Training Effect {service}'
    #            ,disabled = False)            
    #        ## only enable MECC training if true
    #        #if st.session_state.alcohol_mecc_trained[service]:
    #        #    st.session_state.alcohol_mecc_effect[service] = st.slider(
    #        #        "Training Effect on Intervention Chance", 0.0, 1.0
    #        #        , st.session_state.alcohol_mecc_effect[service]
    #        #        , key = f'Training Effect {service}'
    #        #        ,disabled = False)
    #        #else:               
    #        #    st.session_state.alcohol_mecc_effect[service] = 0.0
    #        #    st.session_state.alcohol_mecc_effect[service] = st.slider(
    #        #        "Training Effect on Intervention Chance", 0.0, 1.0
    #        #        , st.session_state.alcohol_mecc_effect[service]                  
    #        #        , key = f'Training Effect {service}'
    #        #        , disabled = True)                                  
    #        st.session_state.alcohol_contemplation_intervention[service] = st.slider(
    #            'Post Intervention Pre-Contemplation to Contemplation chance', 0.0, 1.0
    #            , st.session_state.alcohol_contemplation_intervention[service]
    #            , key = f'Contemplation {service}')
    #        st.session_state.alcohol_preparation_intervention[service] = st.slider(
    #            'Post Intervention Contemplation to Preparation chance', 0.0, 1.0
    #            , st.session_state.alcohol_preparation_intervention[service]
    #            , key = f'Preparation {service}')
    #        st.session_state.alcohol_action_intervention[service] = st.slider(
    #            'Post Intervention Preparation to Action chance', 0.0, 1.0
    #            , st.session_state.alcohol_action_intervention[service]
    #            , key = f'Action {service}') 
    

    ## Logic Diagram
    #with st.expander("Click here to view the logic diagram"):
        #col1a, col2a, col3a = st.columns(3)
        #with col2a:
        #st.image(create_logic_diagram(number_labels = True)
        #    , caption="Diagram of Agent Model Logic"
        #    , use_column_width=False)

with tab3:
    st.markdown("### Smoking Cessation Parameters")

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("#### Population")

        st.write(f"Number of People: :blue-background[{st.session_state.N_people}]") 

        st.write(f"Chance of Visiting a Service per Month: :blue-background[{st.session_state.visit_prob}]")

        if 'initial_smoking_prob' not in st.session_state:
            st.session_state.initial_smoking_prob = 0.5
        st.session_state.initial_smoking_prob = st.slider("Initial Smoking Probability", 0.0, 1.0, st.session_state.initial_smoking_prob)

        if 'quit_attempt_prob' not in st.session_state:
            st.session_state.quit_attempt_prob = 0.01
        st.session_state.quit_attempt_prob = st.slider("Base Quit Attempt Probability per Month", 0.00, 1.00, st.session_state.quit_attempt_prob)

        if 'base_smoke_relapse_prob' not in st.session_state:
            st.session_state.base_smoke_relapse_prob = 0.01
        st.session_state.base_smoke_relapse_prob = st.slider("Base Smoking Relapse per Month", 0.00, 1.00, st.session_state.base_smoke_relapse_prob)
        st.markdown("*Relapse chance decreases over time of not smoking*")

    with col5:
        st.markdown("#### Service")

        st.write(f"Chance a Brief Intervention Made Without MECC Training: :blue-background[{st.session_state.base_make_intervention_prob}]")

        if 'intervention_effect' not in st.session_state:
            st.session_state.intervention_effect = 1.1
        st.session_state.intervention_effect = st.slider("Effect of a Brief Intervention on Chance Making a Quit Attempt", 0.0, 10.0, st.session_state.intervention_effect)
        st.markdown("*Numbers less than 1 will decrease the probability*")

        st.write("-----") #divider

        st.markdown("#### MECC Training")
        st.write(f"Chance Making a Brief Intervention After MECC Training: :blue-background[{st.session_state.mecc_effect}]")

    with col6:
        st.markdown("#### Simulation")

        st.write(f"Random Seed: :blue-background[{st.session_state.model_seed}]")

        st.write(f"Number of Months to Simulate: :blue-background[{st.session_state.num_steps}]")

        st.write(f"Animation Speed (seconds): :blue-background[{st.session_state.animation_speed}]")

    ## Logic Diagram
    with st.expander("Click here to view the logic diagram"):
       #col4a, col5a, col6a = st.columns(3)
       #with col5a:
        st.image(create_logic_diagram_SmokeModel(number_labels = True)
            , caption="Diagram of Agent Model Logic"
            , use_column_width=False)

with tab4:
    st.markdown("### Monte Carlo Parameters")

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("#### Population")

        st.write(f"Number of People: :blue-background[{st.session_state.N_people}]") 

        st.write(f"Chance of Visiting a Service per Month: :blue-background[{st.session_state.visit_prob}]")

    with col5:
        st.markdown("#### Service")

        st.write(f"Chance a Brief Intervention Made Without MECC Training: :blue-background[{st.session_state.base_make_intervention_prob}]")

        st.write("-----") #divider

        st.markdown("#### MECC Training")

        st.write(f"Chance Making a Brief Intervention After MECC Training: :blue-background[{st.session_state.mecc_effect}]")

    with col6:
        st.markdown("#### Simulation")

        if 'iterations' not in st.session_state:
            st.session_state.iterations = 100
        st.session_state.iterations = st.slider("Number of Reruns"
                                                , 100, 1000
                                                , st.session_state.iterations
                                                , step=100)

        st.write(f"Number of Months to Simulate: :blue-background[{st.session_state.num_steps}]")

        st.write(f"Animation Speed (seconds): :blue-background[{st.session_state.animation_speed}]")

    ## Logic Diagram
    with st.expander("Click here to view the logic diagram"):
        #col1a, col2a, col3a = st.columns(3)
        #with col2a:
        st.image(create_logic_diagram(number_labels = True)
            , caption="Diagram of Agent Model Logic"
            , use_column_width=False)
