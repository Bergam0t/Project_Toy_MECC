import streamlit as st
import os

os.system("wget https://github.com/quarto-dev/quarto-cli/releases/download/v1.6.33/quarto-1.6.33-linux-amd64.deb")

os.system("sudo dpkg -i quarto-1.6.33-linux-amd64.deb")

os.system("quarto check")

st.set_page_config(layout="wide")

pg = st.navigation(

    [st.Page("homepage.py", 
             title="Hackathon Details", 
             icon=":material/cottage:"),
    st.Page("parameters.py", 
             title="Parameters for Simulation", 
             icon=":material/settings:"),
    st.Page("mesa_abs_two_types_mecc.py", 
             title="Smoking cessation with MECC", 
             icon=":material/people:") 
     ]
     )

pg.run()


