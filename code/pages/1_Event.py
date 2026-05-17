import streamlit as st

st.set_page_config(
    page_title="HEART · Event",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from interview_ui import render_chat_page

render_chat_page(
    section="event",
    headline="Event",
    next_page="pages/2_Emotion.py",
    next_label="Continue",
)
