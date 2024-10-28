import streamlit as st

st.set_page_config(layout="wide")

pg = st.navigation(

    [st.Page("homepage.py", 
             title="Hackathon Details", 
             icon=":material/cottage:"),
    #  st.Page("abs.py", 
    #          title="Agent Based Simulation", 
    #          icon=":material/people:"),
    #  st.Page("mesa_abs.py", 
    #          title="Mesa Agent Based Simulation", 
    #          icon=":material/people:"),
    st.Page("parameters.py", 
             title="Parameters for Simulation", 
             icon=":material/settings:"),
    st.Page("mesa_abs_two_types_mecc.py", 
             title="Smoking cessation with MECC", 
             icon=":material/people:"),         
     ]
     )

pg.run()


