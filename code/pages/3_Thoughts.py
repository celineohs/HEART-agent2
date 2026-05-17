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
    blurb=(
        "In this section, we'll explore **what you believed or expected**, what an "
        "**ideal interaction** might have looked like to you, and—tentatively—whether "
        "you imagine the other person would have shared that ideal."
    ),
    next_page="pages/4_Thank_you.py",
    next_label="End interview",
)
