import streamlit as st

st.set_page_config(layout="wide")

pg = st.navigation(
    [st.Page("homepage.py", title="Hackacthon Details", icon=":material/add_circle:"),
     st.Page("abs.py", title="Agent Based Simulation", icon=":material/people:"),
     ]
     )

pg.run()


