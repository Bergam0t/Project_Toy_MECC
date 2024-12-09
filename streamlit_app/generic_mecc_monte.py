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

st.title("Simulate - Service with MECC Training")

# initialise generic_MC_simulation_completed session state
if 'generic_MC_simulation_completed' not in st.session_state:
    st.session_state.generic_MC_simulation_completed = False

if "generic_download_clicked" not in st.session_state:
    st.session_state.generic_download_clicked = False

def disable_download():
    st.session_state.generic_download_clicked = True
    st.session_state.generic_MC_simulation_completed = False
    report_message.empty()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Population Parameters")
    st.write(f" - Number of People: :blue-background[{st.session_state.N_people}]") 
    st.write(f" - Chance of Visiting a Service per Month: :blue-background[{st.session_state.visit_prob}]")

with col2: 
    st.markdown("#### Service Parameters")
    st.write(f" - Chance a Brief Intervention Made Without MECC Training: :blue-background[{st.session_state.base_make_intervention_prob}]")

    st.write("-----") #divider

    st.markdown("#### MECC Parameters")
    st.write(f" - Chance Making a Brief Intervention After MECC Training: :blue-background[{st.session_state.mecc_effect}]")


with col3:
    st.markdown("#### Simulation Parameters")
    st.write(f" - Number of Reruns: :blue-background[{st.session_state.iterations}]")
    st.write(f" - Number of Months to Simulate: :blue-background[{st.session_state.num_steps}]")
    st.write(f" - Animation Speed (seconds): :blue-background[{st.session_state.animation_speed}]")

model_parameters = {
    "model_seed": 0,
    "N_people": st.session_state.N_people,
    "N_service": 1,
    "visit_prob": st.session_state.visit_prob,
    "base_make_intervention_prob": st.session_state.base_make_intervention_prob,
    "mecc_effect": st.session_state.mecc_effect,
    "num_steps" : st.session_state.num_steps,
    "animation_speed" : st.session_state.animation_speed
}

# Sets number of iterations for model to run
iterations = st.session_state.iterations

# save to json file to be used later for the quarto report
output_path = os.path.join(os.getcwd(),'streamlit_app','outputs')
json_path = os.path.join(output_path,'session_data.json')

with open(json_path, "w") as f:
    json.dump(model_parameters, f, indent=4)


st.write("----")  # divider
if "generic_MC_simulation_completed" not in st.session_state:
    st.session_state.generic_MC_simulation_completed = False


if st.button("Run Simulations"):
    # set generic_MC_simulation_completed to False before starting - to control the download report button
    st.session_state.generic_MC_simulation_completed = False
    st.session_state.generic_download_clicked = False

    model_message = st.info(f"Simulations Running 0/{iterations}")
    progress_bar = st.progress(0)
    chart_placeholder1 = st.empty()
    chart_placeholder2 = st.empty()
    chart_placeholder3 = st.empty()

    list_data_no_mecc = []
    list_data_mecc = []

    for iteration in range(iterations):

        model_parameters["model_seed"] = iteration

        model_no_mecc = create_MECC_model(
            model_parameters=model_parameters,
            model_type='Generic',
            mecc_trained=False
        )
        model_mecc = create_MECC_model(
            model_parameters=model_parameters,
            model_type='Generic',
            mecc_trained=True
        )

        data_no_mecc = pd.DataFrame()
        data_mecc  = pd.DataFrame()

        for step in range(st.session_state.num_steps):
            data_no_mecc = run_simulation_step(model_no_mecc)
            data_mecc = run_simulation_step(model_mecc)

        if iteration == iterations - 1:
            model_message.success(f"Simulations Completed! ({iterations}/{iterations})")
            progress_bar.empty()
        else:
            model_message.info(f"Simulations Running ({iteration + 1}/{iterations})")
            progress = (iteration + 1) / (iterations)
            progress_bar.progress(progress)
            
        data_no_mecc['seed'] = iteration
        data_mecc['seed']  = iteration

        data_no_mecc = data_no_mecc.reset_index(names='month')
        data_mecc = data_mecc.reset_index(names='month')

        list_data_no_mecc.append(data_no_mecc)
        list_data_mecc.append(data_mecc)
        # fig1 = create_population_figure(data_no_mecc, data_mecc, step)
        #with chart_placeholder1:
        #    st.plotly_chart(fig1, use_container_width=True)

        #fig2 = create_intervention_figure(data_no_mecc, data_mecc, step)
        #with chart_placeholder2:
        #    st.plotly_chart(fig2, use_container_width=True)

        #fig3 = create_metrics_figure(data_no_mecc, data_mecc, step)
        #with chart_placeholder3:
        #    st.plotly_chart(fig3, use_container_width=True)
        
        time.sleep(st.session_state.animation_speed)

    data_no_mecc = pd.concat(list_data_no_mecc).reset_index(drop=True)
    data_mecc = pd.concat(list_data_mecc).reset_index(drop=True)

    st.session_state.generic_MC_simulation_completed = True  # set to True after completion
    
    # save csv files for use in quarto
    #data_no_mecc_file = os.path.join(output_path,'data_no_mecc.csv')
    #data_mecc_file = os.path.join(output_path,'data_mecc.csv')

    #data_no_mecc.to_csv(data_no_mecc_file, index=False)
    #data_mecc.to_csv(data_mecc_file, index=False)
    
######################################################

    def group_output_data(df):
        df = df[df['month']==(st.session_state.num_steps-1)]
        return df

    data_no_mecc_total = group_output_data(data_no_mecc)
    data_mecc_total = group_output_data(data_mecc)

    st.markdown("### Final Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Contacts with Intervention\n\n(No MECC Training)", 
            f"{( sum(data_no_mecc_total['Total Interventions']) / sum(data_no_mecc_total['Total Contacts']) * 100):.1f}%",
            #f"{(data_no_mecc['Total Contacts'].iloc[-1] - data_no_mecc['Total Not Smoking'].iloc[0]):.0f}"
        )
    
    with col2:
        st.metric(
            "Contacts with Intervention\n\n(MECC Trained)",
            f"{( sum(data_mecc_total['Total Interventions']) / sum(data_mecc_total['Total Contacts']) * 100):.1f}%",
            #f"{(data_mecc['Total Not Smoking'].iloc[-1] - data_mecc['Total Not Smoking'].iloc[0]):.0f}"
        )
    
    with col3:
        mecc_improvement = (
            (sum(data_mecc_total['Total Interventions']) - 
            sum(data_no_mecc_total['Total Interventions']))/iterations
        )
        st.metric(
            "MECC Training\n\nImpact",
            f"{mecc_improvement:.1f} mean additional interventions",
            #f"{(mecc_improvement / data_no_mecc['Total Interventions'].iloc[-1] * 100):.1f}%"
        )

    with st.expander("View Raw Data"):
        tab1, tab2 = st.tabs(["No MECC Training", "MECC Trained"])
        with tab1:
            st.dataframe(data_no_mecc)
        with tab2:
            st.dataframe(data_mecc)


######################################################

## empty location for report message
#report_message = st.empty()
#
#if st.session_state.generic_MC_simulation_completed:
#    
#    report_message.info("Generating Report...")
#
#    ## filepaths for 
#    output_dir = os.path.join(os.getcwd(),'streamlit_app','downloads')
#    qmd_filename = 'mecc_simulation_report.qmd'
#    qmd_path = os.path.join(os.getcwd(),'streamlit_app',qmd_filename)
#    html_filename = os.path.basename(qmd_filename).replace('.qmd', '.html')
#    dest_html_path = os.path.join(output_dir,html_filename)
#
#    try:
#        ## forces result to be html
#        result = subprocess.run(["quarto"
#                                , "render"
#                                , qmd_path
#                                , "--to"
#                                , "html"
#                                , "--output-dir"
#                                , output_dir]
#                                , capture_output=True
#                                , text=True)
#    except:
#        ## error message
#        report_message.error(f"Report cannot be generated")
#    
#    if os.path.exists(dest_html_path):
#        with open(dest_html_path, "r") as f:
#            html_data = f.read()
#
#        report_message.success("Report Available for Download")
#
#        if not st.session_state.generic_download_clicked:
#            st.download_button(
#                label="Download MECC Simulation Report and Clear Simulation Results",
#                data=html_data,
#                file_name=html_filename,
#                mime="text/html",
#                # disabled=not st.session_state.generic_MC_simulation_completed,
#                on_click=disable_download
#            )
#    else:
#        ## error message
#        report_message.error(f"Report failed to generate\n\n_{result}_")
#
#else:
#    ## empty location for report message
#    report_message = st.empty()
