## mesa_abs_two_types_mecc.py
import subprocess
import pandas as pd
import numpy as np
import streamlit as st
import time
from streamlit_model_functions import run_simulation_step, create_comparison_figure, create_MECC_model
import os
import shutil
import json
from quarto_render_func import render_quarto

st.title("Simulate - Enhanced Smoking Cessation Model with MECC Training")

# initialise simulation_completed session state
if 'simulation_completed' not in st.session_state:
    st.session_state.simulation_completed = False

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Population Parameters")
    st.write(f"Number of People: {st.session_state.N_people}")
    st.write(f"Initial Smoking Probability: {st.session_state.initial_smoking_prob}")
    st.write(f"Chance of Visiting a Service per Month: {st.session_state.visit_prob}")
    st.write(f"Base Quit Attempt Probability per Month: {st.session_state.quit_attempt_prob}")
    st.write(f"Base Smoking Relapse per Month: {st.session_state.base_smoke_relapse_prob}")
    st.markdown("*Relapse chance decreases over time of not smoking*")

with col2:
    st.markdown("#### Service Parameters")
    st.write(f"Chance a Brief Intervention Made Without MECC: {st.session_state.base_make_intervention_prob}")

col3, col4 = st.columns(2)

with col3:
    st.markdown("#### MECC Parameters")
    st.write(f"Chance Making a Brief Intervention After MECC Training: {st.session_state.mecc_effect}")
    st.write(f"Effect of a Brief Intervention on Chance Making a Quit Attempt: {st.session_state.intervention_effect}")
    st.markdown("*Numbers less than 1 will decrease the probability*")

with col4:
    st.markdown("#### Simulation Parameters")
    st.write(f"Random Seed: {st.session_state.model_seed}")
    st.write(f"Number of Months to Simulate: {st.session_state.num_steps}")
    st.write(f"Animation Speed (seconds): {st.session_state.animation_speed}")

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
with open("./streamlit_app/outputs/session_data.json", "w") as f:
    json.dump(model_parameters, f)

st.write("----")  # divider
if "simulation_completed" not in st.session_state:
    st.session_state.simulation_completed = False

if st.button("Run Simulation"):
    # set simulation_completed to False before starting - to control the download report button
    st.session_state.simulation_completed = False

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
    chart_placeholder = st.empty()

    data_no_mecc = pd.DataFrame()
    data_mecc = pd.DataFrame()

    for step in range(st.session_state.num_steps):
        if step == st.session_state.num_steps - 1:
            model_message.success("Simulation completed!")
            progress_bar.empty()
        else:
            progress = (step + 1) / st.session_state.num_steps
            progress_bar.progress(progress)

        data_no_mecc = run_simulation_step(model_no_mecc)
        data_mecc = run_simulation_step(model_mecc)

        fig = create_comparison_figure(data_no_mecc, data_mecc, step)
        with chart_placeholder:
            st.plotly_chart(fig, use_container_width=True)

        time.sleep(st.session_state.animation_speed)

    st.session_state.simulation_completed = True  # set to True after completion

    data_no_mecc.to_csv("./streamlit_app/outputs/data_no_mecc.csv", index=False)
    data_mecc.to_csv("./streamlit_app/outputs/data_mecc.csv", index=False)

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

## filepaths for outputs
qmd_path = './streamlit_app/mecc_simulation_report.qmd'
output_dir = './downloads'
output_dest = './streamlit_app/downloads'

if st.session_state.simulation_completed:

    report_message = st.info("Generating Report for Download")

    print("Starting quarto subprocess")

    ## forces result to be html
    # result = subprocess.run(["quarto", "render"
    #                          , qmd_path, "--to"
    #                          , "html", "--output-dir", output_dir]
    #                         , capture_output=True, text=True, shell=True, )

    render_quarto(input=qmd_path,
                  output_dir=output_dir,
                  output_format="html",
                  find_quarto_path=True,
                  print_command=True,
                  verbose=True,
                  shell=True)

    print("Render complete")

    html_filename = os.path.basename(qmd_path).replace('.qmd', '.html')
    dest_html_path = os.path.join(output_dest, html_filename)

    if os.path.exists(dest_html_path):

        with open(dest_html_path, "r") as f:
            html_data = f.read()

        report_message.success("Report Available for Download")

        if st.download_button(
            label="Download MECC Simulation Report",
            data=html_data,
            file_name=html_filename,
            mime="text/html",
            disabled=not st.session_state.simulation_completed
        ):
            # set simulation_completed to False after download to reset the button
            st.session_state.simulation_completed = False
