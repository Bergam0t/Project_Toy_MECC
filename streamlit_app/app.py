import streamlit as st
import os
import subprocess
import platform

@st.cache_data
def get_quarto():
    # Download Quarto
    os.system("wget https://github.com/quarto-dev/quarto-cli/releases/download/v1.5.57/quarto-1.5.57-linux-amd64.tar.gz")

    # Create directory and extract Quarto
    os.system("mkdir -p ~/opt")
    os.system("tar -C ~/opt -xvzf quarto-1.5.57-linux-amd64.tar.gz")

    os.system("echo 'Original PATH'")
    os.system("echo $PATH")

    # Create symlink in a directory that's typically in PATH
    os.system("mkdir -p ~/.local/bin/quarto")
    os.system("ln -s ~/opt/quarto-1.5.57/bin/quarto ~/.local/bin/quarto")

    # Try alternative approach to path updating
    bashrc_path = os.path.expanduser("~/.bashrc")
    export_statement = '\nexport PATH="$HOME/.local/bin:$PATH"\n'

    # Check if the export statement already exists in .bashrc
    with open(bashrc_path, 'r') as file:
        if export_statement.strip() not in file.read():
            # Append the export statement to .bashrc
            with open(bashrc_path, 'a') as file:
                file.write(export_statement)

    # Update PATH in the current Python process
    os.environ['PATH'] = f"{os.path.expanduser('~/.local/bin')}:{os.environ['PATH']}"

    # check path updated
    os.system("echo 'New PATH'")
    os.system("echo $PATH")

    subprocess.run(['quarto', 'check'], capture_output=True, text=True)

st.set_page_config(layout="wide")

print(f"Output of platform.processor(): {platform.processor()}")
print(f"type:  {type(platform.processor())}")

if platform.processor() is None:
    get_quarto()

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
