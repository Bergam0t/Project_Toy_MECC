import streamlit as st

st.set_page_config(layout="wide")

pg = st.navigation(

    [st.Page("homepage.py", 
             title="Hackacthon Details", 
             icon=":material/add_circle:"),
    #  st.Page("abs.py", 
    #          title="Agent Based Simulation", 
    #          icon=":material/people:"),
    #  st.Page("mesa_abs.py", 
    #          title="Mesa Agent Based Simulation", 
    #          icon=":material/people:"),
    #  st.Page("mesa_abs_two_types.py", 
    #          title="Primary Care smoking cessation", 
    #          icon=":material/people:"),
    st.Page("mesa_abs_two_types_mecc.py", 
             title="Primary Care smoking cessation with MECC", 
             icon=":material/people:"),         

     ]
     )

pg.run()


