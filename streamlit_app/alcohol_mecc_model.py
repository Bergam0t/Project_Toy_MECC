## alcohol_mecc_model.py
import subprocess
import pandas as pd
import numpy as np
import streamlit as st
import time
from streamlit_model_functions import run_simulation_step, create_MECC_model,create_metrics_figure
from alcohol_outputs import create_population_figure,create_intervention_figure
import os
import shutil
import json
from alcohol_agents import Alcohol_MECC_Model

######################################################

st.title("Simulate - Alcohol Advice Model with MECC Training")

# initialise simulation_completed session state
if 'simulation_completed' not in st.session_state:
    st.session_state.simulation_completed = False

if "download_clicked" not in st.session_state:
    st.session_state.download_clicked = False

def disable_download():
    st.session_state.download_clicked = True
    st.session_state.simulation_completed = False
    report_message.empty()


tab1, tab2 = st.tabs(['Model','Parameters'])

######################################################

##################################
### Parameters 
##################################

with tab2:
    colA, colB = st.columns(2)

    with colA:
        st.markdown("#### Population Parameters")
        st.write(f" - Number of People: :blue-background[{st.session_state.N_people}]")
        st.write(f" - Base Pre-Contemplation to Contemplation chance: :blue-background[{st.session_state.alcohol_change_prob_contemplation}]")
        st.write(f" - Base Contemplation to Preparation chance: :blue-background[{st.session_state.alcohol_change_prob_preparation}]")
        st.write(f" - Base Preparation to Action chance: :blue-background[{st.session_state.alcohol_change_prob_action}]")
        st.write(f" - Base Contemplation to Pre-Contemplation lapse chance: :blue-background[{st.session_state.alcohol_lapse_prob_precontemplation}]")
        st.write(f" - Base Preparation to Contemplation lapse chance: :blue-background[{st.session_state.alcohol_lapse_prob_contemplation}]")
        st.write(f" - Base Action to Preparation lapse chance: :blue-background[{st.session_state.alcohol_lapse_prob_preparation}]")

    with colB:
        st.markdown("#### Simulation Parameters")
        st.write(f" - Random Seed: :blue-background[{st.session_state.model_seed}]")
        st.write(f" - Number of Months to Simulate: :blue-background[{st.session_state.num_steps}]")
        st.write(f" - Animation Speed (seconds): :blue-background[{st.session_state.animation_speed}]")

    st.markdown("#### Service Parameters")
    col1, col2, col3, col4 = st.columns(4)
    column_dict = { 'Job Centre': col1
                    ,'Benefits Office': col2
                    ,'Housing Officer': col3
                    ,'Community Hub': col4}
    
    for service in column_dict:
        with column_dict[service]:
            st.write(f"**{service}**")
            st.write(f" - Chance of a Person Visiting per Month: :blue-background[{st.session_state.alcohol_services_table.loc[service]['Person Visit Probability']}]")
            st.write(f" - Chance a Brief Intervention Made Without MECC Training: :blue-background[{st.session_state.alcohol_services_table.loc[service]['Chance a Brief Intervention Made Without MECC Training']}]")
            st.write(f" - Service has had MECC Training: :blue-background[{st.session_state.alcohol_services_table.loc[service]['MECC Trained']}]")
            if st.session_state.alcohol_services_table.loc[service]['MECC Trained']:
                st.write(f" - Chance Making a Brief Intervention After MECC Training: :blue-background[{st.session_state.alcohol_services_table.loc[service]['Chance Making a Brief Intervention After MECC Training']}]")
            else:
                pass
            #st.write(f" - Chance Making a Brief Intervention After MECC Training: :blue-background[{st.session_state.alcohol_services_table.loc[service]['Person Visit Probability']}]")
            st.write(f" - Post Intervention Pre-Contemplation to Contemplation chance: :blue-background[{st.session_state.alcohol_services_table.loc[service]['Post Intervention Pre-Contemplation to Contemplation chance']}]")
            st.write(f" - Post Intervention Contemplation to Preparation chance: :blue-background[{st.session_state.alcohol_services_table.loc[service]['Post Intervention Contemplation to Preparation chance']}]")
            st.write(f" - Post Intervention Preparation to Action chance: :blue-background[{st.session_state.alcohol_services_table.loc[service]['Post Intervention Preparation to Action chance']}]")

######################################################

##################################
### Model 
##################################

with tab1:

    model_parameters = {
        "model_seed": st.session_state.model_seed,
        "num_steps" : st.session_state.num_steps,
        "animation_speed" : st.session_state.animation_speed,    
        "N_people": st.session_state.N_people,
        "change_prob_contemplation": st.session_state.alcohol_change_prob_contemplation,
        "change_prob_preparation":st.session_state.alcohol_change_prob_preparation,
        "change_prob_action": st.session_state.alcohol_change_prob_action,
        "lapse_prob_precontemplation": st.session_state.alcohol_lapse_prob_precontemplation,
        "lapse_prob_contemplation": st.session_state.alcohol_lapse_prob_contemplation,
        "lapse_prob_preparation": st.session_state.alcohol_lapse_prob_preparation,
        "visit_prob": st.session_state.alcohol_services_table['Person Visit Probability'].to_dict(),
        "base_make_intervention_prob": st.session_state.alcohol_services_table['Chance a Brief Intervention Made Without MECC Training'].to_dict(),
        "mecc_trained": st.session_state.alcohol_services_table['MECC Trained'].to_dict(),
        "mecc_effect": st.session_state.alcohol_services_table['Chance Making a Brief Intervention After MECC Training'].to_dict(),
        "contemplation_intervention": st.session_state.alcohol_services_table['Post Intervention Pre-Contemplation to Contemplation chance'].to_dict(),
        "preparation_intervention": st.session_state.alcohol_services_table['Post Intervention Contemplation to Preparation chance'].to_dict(),
        "action_intervention": st.session_state.alcohol_services_table['Post Intervention Preparation to Action chance'].to_dict(),
    }

    # save to json file to be used later for the quarto report
    output_path = os.path.join(os.getcwd(),'streamlit_app','outputs')
    json_path = os.path.join(output_path,'session_data.json')

    with open(json_path, "w") as f:
        json.dump(model_parameters, f, indent=4)

    if "simulation_completed" not in st.session_state:
        st.session_state.simulation_completed = False

    if st.button("Run Simulation"):
        # set simulation_completed to False before starting - to control the download report button
        st.session_state.simulation_completed = False
        st.session_state.download_clicked = False

        model_no_mecc = create_MECC_model(
            model_parameters=model_parameters,
            model_type='Alcohol',
            mecc_trained=False
        )
        model_mecc = create_MECC_model(
            model_parameters=model_parameters,
            model_type='Alcohol',
            mecc_trained=True
        )

        model_message = st.info("Simulation Running")
        progress_bar = st.progress(0)
        chart_placeholder1 = st.empty()
        chart_placeholder2 = st.empty()
        chart_placeholder3 = st.empty()
          
        for step in range(st.session_state.num_steps):
            if step == st.session_state.num_steps - 1:
                model_message.success("Simulation Completed!")
                progress_bar.empty()
            else:
                progress = (step + 1) / st.session_state.num_steps
                progress_bar.progress(progress)

            data_no_mecc = run_simulation_step(model_no_mecc)
            data_mecc = run_simulation_step(model_mecc)

            fig1 = create_population_figure(data_no_mecc, data_mecc, step)
            with chart_placeholder1:
                st.plotly_chart(fig1, use_container_width=True)
            
            fig2 = create_intervention_figure(data_no_mecc, data_mecc, step)
            with chart_placeholder2:
                st.plotly_chart(fig2, use_container_width=True)
            
            time.sleep(st.session_state.animation_speed)
                

        st.session_state.simulation_completed = True  # set to True after completion

        ## save csv files for use in quarto
        data_no_mecc_file = os.path.join(output_path,'data_no_mecc.csv')
        data_mecc_file = os.path.join(output_path,'data_mecc.csv')

        data_no_mecc.to_csv(data_no_mecc_file, index=False)
        data_mecc.to_csv(data_mecc_file, index=False)

######################################################

        st.markdown("### Final Statistics")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.empty()
    #       st.metric(
    #           "Smoking Reduction\n\n(No MECC Training)",
    #           f"{(data_no_mecc['Total Not Smoking'].iloc[-1] / st.session_state.N_people * 100):.1f}%",
    #           f"{(data_no_mecc['Total Not Smoking'].iloc[-1] - data_no_mecc['Total Not Smoking'].iloc[0]):.0f}"
    #       )

        with col2:
            st.empty()
    #        st.metric(
    #            "Smoking Reduction\n\n(MECC Trained)",
    #            f"{(data_mecc['Total Not Smoking'].iloc[-1] / st.session_state.N_people * 100):.1f}%",
    #            f"{(data_mecc['Total Not Smoking'].iloc[-1] - data_mecc['Total Not Smoking'].iloc[0]):.0f}"
    #        )

        with col3:
            st.empty()
    #        mecc_improvement = (
    #            data_mecc['Total Not Smoking'].iloc[-1] -
    #            data_no_mecc['Total Not Smoking'].iloc[-1]
    #        )
    #        st.metric(
    #            "MECC Training\n\nImpact",
    #            f"{mecc_improvement:.0f} additional quits",
    #            f"{(mecc_improvement / st.session_state.N_people * 100):.1f}%"
    #        )

        with st.expander("View Raw Data"):
            tab1, tab2 = st.tabs(["No MECC Training", "MECC Trained"])
            with tab1:
                st.dataframe(data_no_mecc)
            with tab2:
                st.dataframe(data_mecc)

######################################################

# empty location for report message
report_message = st.empty()