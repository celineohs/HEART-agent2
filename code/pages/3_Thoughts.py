import streamlit as st

st.set_page_config(
    page_title="HEART · Thoughts",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from interview_ui import render_chat_page

render_chat_page(
    section="thoughts",
    headline="Thoughts",
    next_page="pages/4_Thank_you.py",
    next_label="End interview",
)
