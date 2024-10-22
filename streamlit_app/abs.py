import pandas as pd
import numpy as np
# import mesa
import streamlit as st
# from des_classes import 


# st.logo("hsma_logo.png")


st.title("Toy MECC")

with st.sidebar:
    st.markdown("#### Parameters")
    input_eg1 =  st.slider("parameter one", 1, 10, 5)
    
    input_eg2 = st.slider("parameter two", 1, 100, 10)

    st.divider()



# button_run_pressed = st.button("Run simulation")

# if button_run_pressed:
#     with st.spinner('Simulating the system...'):
        