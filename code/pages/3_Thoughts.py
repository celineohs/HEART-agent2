import streamlit as st

st.set_page_config(
    page_title="HEART · Interview",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from interview_ui import render_chat_page

render_chat_page(
    section="thoughts",
    headline="Your perspective",
    blurb=(
        "Reflect on **beliefs and expectations** you held, what an **ideal interaction** might have looked like, "
        "and (tentatively) whether you imagine the other person would have shared that ideal."
    ),
)
