import streamlit as st

st.set_page_config(layout="wide")

pg = st.navigation(

    [st.Page("homepage.py", 
             title="Toy MECC Details", 
             icon=":material/cottage:"),
    st.Page("parameters.py", 
             title="Parameters for Simulation", 
             icon=":material/settings:"),
    st.Page("generic_mecc_model.py", 
             title="Simple MECC", 
             icon=":material/people:"),
    st.Page("mesa_abs_two_types_mecc.py", 
             title="Smoking cessation with MECC", 
             icon=":material/smoke_free:")
     ]
     )

pg.run()


