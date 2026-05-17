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
    blurb=(
        "In this section, we'll talk through **what happened** in the situation you "
        "described—step by step, from **your** point of view."
    ),
    next_page="pages/2_Emotion.py",
    next_label="Continue",
)
