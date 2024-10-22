import streamlit as st

st.logo("resources\MECC.jpg")

st.title("Toy MECC - Making Every Contact Count")

st.image("resources\MECC.jpg", width=500)

st.write("""
A (toy) model for showing the benefit of Making Every Contact Count (MECC) Training_
Build a Streamlit app for an Agent Based Simulation.
The pop culture 80's references will all be in the form of toy robots.
There is an initial group of people and an initial group of government services.
People can have lifestyle factors: smoking/drinking/no exercise.
People may have a probability of making a quit attempt (smoking/drinking/no exercise) with a probability of success.
People have contact with government services at random.
Services can have MECC training, and therefore a probability that any contact will lead to a Very Brief Intervention.
Services with MECC training increase over time with a training rate.
A Very Brief Intervention increases the probability that a patient will make a quit attempt.
Outputs will be MECC training numbers, number of quit attempts, and number of successful quits over time.
""")


st.write("https://github.com/DomRowney/Project_Toy_MECC.git")