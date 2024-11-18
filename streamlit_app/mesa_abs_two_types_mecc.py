## mesa_abs_two_types_mecc.py
import subprocess
import pandas as pd
import numpy as np
import streamlit as st
import time
from streamlit_model_functions import run_simulation_step, create_MECC_model,create_population_figure,create_intervention_figure,create_metrics_figure
import os
import shutil
import json

st.title("Simulate - Enhanced Smoking Cessation Model with MECC Training")

# initialise simulation_completed session state
if 'simulation_completed' not in st.session_state:
    st.session_state.simulation_completed = False

if "download_clicked" not in st.session_state:
    st.session_state.download_clicked = False

def disable_download():
    st.session_state.download_clicked = True
    st.session_state.simulation_completed = False
    report_message.empty()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Population Parameters")
    st.write(f" - Number of People: :blue-background[{st.session_state.N_people}]") 
    st.write(f" - Initial Smoking Probability: :blue-background[{st.session_state.initial_smoking_prob}]")
    st.write(f" - Chance of Visiting a Service per Month: :blue-background[{st.session_state.visit_prob}]")
    st.write(f" - Base Quit Attempt Probability per Month: :blue-background[{st.session_state.quit_attempt_prob}]")
    st.write(f" - Base Smoking Relapse per Month: :blue-background[{st.session_state.base_smoke_relapse_prob}]  \n  *(Relapse chance decreases over time of not smoking)*")

with col2: 
    st.markdown("#### Service Parameters")
    st.write(f" - Chance a Brief Intervention Made Without MECC: :blue-background[{st.session_state.base_make_intervention_prob}]")

    st.write("-----") #divider

    st.markdown("#### MECC Parameters")
    st.write(f" - Chance Making a Brief Intervention After MECC Training: :blue-background[{st.session_state.mecc_effect}]")
    st.write(f" - Effect of a Brief Intervention on Chance Making a Quit Attempt: :blue-background[{st.session_state.intervention_effect}]  \n  *(Numbers less than 1 will decrease the probability)*")


with col3:
    st.markdown("#### Simulation Parameters")
    st.write(f" - Random Seed: :blue-background[{st.session_state.model_seed}]")
    st.write(f" - Number of Months to Simulate: :blue-background[{st.session_state.num_steps}]")
    st.write(f" - Animation Speed (seconds): :blue-background[{st.session_state.animation_speed}]")

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


st.write("----")  # divider
if "simulation_completed" not in st.session_state:
    st.session_state.simulation_completed = False

if st.button("Run Simulation"):
    # set simulation_completed to False before starting - to control the download report button
    st.session_state.simulation_completed = False
    st.session_state.download_clicked = False
    
    model_no_mecc = create_MECC_model(
        model_parameters=model_parameters,
        mecc_trained=False
    )
    model_mecc = create_MECC_model(
        model_parameters=model_parameters,
        mecc_trained=True
    )

    model_message = st.info("Simulation Running")
    progress_bar = st.progress(0)
    chart_placeholder1 = st.empty()
    chart_placeholder2 = st.empty()
    chart_placeholder3 = st.empty()

    data_no_mecc = pd.DataFrame()
    data_mecc = pd.DataFrame()

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

        fig3 = create_metrics_figure(data_no_mecc, data_mecc, step)
        with chart_placeholder3:
            st.plotly_chart(fig3, use_container_width=True)

        time.sleep(st.session_state.animation_speed)

    st.session_state.simulation_completed = True  # set to True after completion

    # save csv files for use in quarto
    data_no_mecc_file = os.path.join(output_path,'data_no_mecc.csv')
    data_mecc_file = os.path.join(output_path,'data_mecc.csv')

    data_no_mecc.to_csv(data_no_mecc_file, index=False)
    data_mecc.to_csv(data_mecc_file, index=False)

######################################################

    st.markdown("### Final Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Smoking Reduction (No MECC)", 
            f"{(data_no_mecc['Total Not Smoking'].iloc[-1] / st.session_state.N_people * 100):.1f}%",
            f"{(data_no_mecc['Total Not Smoking'].iloc[-1] - data_no_mecc['Total Not Smoking'].iloc[0]):.0f}"
        )
    
    with col2:
        st.metric(
            "Smoking Reduction (With MECC)",
            f"{(data_mecc['Total Not Smoking'].iloc[-1] / st.session_state.N_people * 100):.1f}%",
            f"{(data_mecc['Total Not Smoking'].iloc[-1] - data_mecc['Total Not Smoking'].iloc[0]):.0f}"
        )
    
    with col3:
        mecc_improvement = (
            data_mecc['Total Not Smoking'].iloc[-1] - 
            data_no_mecc['Total Not Smoking'].iloc[-1]
        )
        st.metric(
            "MECC Impact",
            f"{mecc_improvement:.0f} additional quits",
            f"{(mecc_improvement / st.session_state.N_people * 100):.1f}%"
        )

    with st.expander("View Raw Data"):
        tab1, tab2 = st.tabs(["Without MECC", "With MECC"])
        with tab1:
            st.dataframe(data_no_mecc)
        with tab2:
            st.dataframe(data_mecc)


######################################################

## empty location for report message
report_message = st.empty()

if st.session_state.simulation_completed:
    
    report_message.info("Generating Report...")

    ## filepaths for 
    output_dir = os.path.join(os.getcwd(),'streamlit_app','downloads')
    qmd_filename = 'mecc_simulation_report.qmd'
    qmd_path = os.path.join(os.getcwd(),'streamlit_app',qmd_filename)
    html_filename = os.path.basename(qmd_filename).replace('.qmd', '.html')
    dest_html_path = os.path.join(output_dir,html_filename)

    try:
        ## forces result to be html
        result = subprocess.run(["quarto"
                                , "render"
                                , qmd_path
                                , "--to"
                                , "html"
                                , "--output-dir"
                                , output_dir]
                                , capture_output=True
                                , text=True)
    except:
        ## error message
        report_message.error(f"Report cannot be generated")
    
    if os.path.exists(dest_html_path):
        with open(dest_html_path, "r") as f:
            html_data = f.read()

        report_message.success("Report Available for Download")

        if not st.session_state.download_clicked:
            st.download_button(
                label="Download MECC Simulation Report and Clear Simulation Results",
                data=html_data,
                file_name=html_filename,
                mime="text/html",
                # disabled=not st.session_state.simulation_completed,
                on_click=disable_download
            )
    else:
        ## error message
        report_message.error(f"Report failed to generate\n\n_{result}_")

else:
    ## empty location for report message
    report_message = st.empty()