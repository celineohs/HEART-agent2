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
    blurb=(
        "In this section, we'll focus on **how you felt** during that same situation—the "
        "quality of the feeling and **how strong** it was."
    ),
    next_page="pages/3_Thoughts.py",
    next_label="Continue",
)
