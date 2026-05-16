import streamlit as st

st.set_page_config(page_title="HEART · Emotion", layout="wide")

from interview_ui import render_chat_page

render_chat_page(
    section="emotion",
    headline="Section 2 · Emotion",
    blurb=(
        "Focus on **how you felt** during **that same situation**: the quality of the feeling and **how strong** it was."
    ),
)
