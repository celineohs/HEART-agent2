import streamlit as st

st.set_page_config(
    page_title="HEART · Thank you",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from ui_style import apply_global_styles

apply_global_styles()

if not st.session_state.get("_interview_completed"):
    st.warning("Please complete the interview on the **Thoughts** page first.")
    st.page_link("app.py", label="→ Go to start")
    st.page_link("pages/3_Thoughts.py", label="→ Go to Thoughts")
    st.stop()

st.title("Thank you")
st.markdown(
    """
Thank you for taking part in this research study.

Your thoughtful answers help us understand how people experience and make sense of interpersonal conflicts. We appreciate the time and care you put into sharing your perspective.
"""
)
