import streamlit as st
import os

os.system("wget https://github.com/quarto-dev/quarto-cli/releases/download/v1.5.57/quarto-1.5.57-linux-amd64.tar.gz")

os.system("tar -xvzf quarto-1.5.57-linux-amd64.tar.gz")

os.system("ls")

os.system("cd quarto-1.5.57")

os.system("ls")

os.system("cp -r ./bin/* $HOME/.local/bin/")
os.system("cp -r ./share/* $HOME/.local/share/")

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


