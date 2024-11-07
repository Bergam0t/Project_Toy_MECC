import streamlit as st
import os
import subprocess

# Download Quarto
os.system("wget https://github.com/quarto-dev/quarto-cli/releases/download/v1.5.57/quarto-1.5.57-linux-amd64.tar.gz")

# Create directory and extract Quarto
os.system("mkdir -p ~/opt")
os.system("tar -C ~/opt -xvzf quarto-1.5.57-linux-amd64.tar.gz")

os.system("echo $PATH")

# Create symlink in a directory that's typically in PATH
os.system("mkdir -p /local/bin/quarto")
os.system("ln -s ~/opt/quarto-1.5.57/bin/quarto /local/bin/quarto")

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


