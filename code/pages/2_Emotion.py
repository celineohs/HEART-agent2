import streamlit as st

st.set_page_config(
    page_title="HEART · Emotion",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from interview_ui import render_chat_page

render_chat_page(
    section="emotion",
    headline="Emotion",
    next_page="pages/3_Thoughts.py",
    next_label="Continue",
)
