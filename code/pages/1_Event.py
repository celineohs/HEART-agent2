import streamlit as st

st.set_page_config(
    page_title="HEART · Interview",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from interview_ui import render_chat_page

render_chat_page(
    section="event",
    headline="Your situation",
    blurb=(
        "Narrate **what happened** in the situation you described—**in order**, from **your** perspective—"
        "before moving to how you read the other person’s intentions."
    ),
    next_page="pages/2_Emotion.py",
    next_label="Continue",
)
