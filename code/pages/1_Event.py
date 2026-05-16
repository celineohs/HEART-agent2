import streamlit as st

st.set_page_config(page_title="HEART · Event", layout="wide")

from interview_ui import render_chat_page

render_chat_page(
    section="event",
    headline="Section 1 · Event",
    blurb=(
        "Narrate **what happened** in the situation you described—**in order**, from **your** perspective—"
        "before moving to how you read the other person’s intentions."
    ),
)
