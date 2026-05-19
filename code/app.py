import re

import streamlit as st

st.set_page_config(
    page_title="LLM-based Interview about Recent Interpersonal Conflict",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from interview_export import ensure_session_id
from ui_style import apply_global_styles

apply_global_styles()
ensure_session_id()

# Minimum response length so “continue” only works with real answers (not one word / whitespace).
INTAKE_MIN_LEN_Q1 = 40
PROLIFIC_ID_RE = re.compile(r"^[A-Za-z0-9]{20,32}$")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("LLM-based Interview about Recent Interpersonal Conflict")
st.markdown(
    "Please continue **only if** you can describe **one recent interpersonal conflict** "
    "where **the other person's perspective, intentions, or feelings were hard for you to understand**—"
    "not every disagreement fits. Also tell us **who they are** to you."
)

st.divider()

with st.form("intake_form"):
    st.subheader("Participant ID")
    prolific_id = st.text_input(
        "Prolific ID",
        value=st.session_state.get("prolific_id", ""),
        placeholder="Paste the ID shown on your Prolific study page",
        max_chars=32,
    )
    st.subheader("Background (free text)")
    q1 = st.text_area(
        "(1) Briefly describe a recent interpersonal conflict where the other person's "
        "perspective or intentions were not clear to you.",
        height=160,
        value=st.session_state.get("brief_conflict", ""),
        placeholder="A short factual description in your own words.",
    )
    q2 = st.text_area(
        "(2) What is your relationship to the other person?",
        height=110,
        value=st.session_state.get("relationship_type", ""),
        placeholder="e.g. partner, flatmate, colleague, friend, family member …",
    )
    submitted = st.form_submit_button("Continue")
    if submitted:
        pid = (prolific_id or "").strip()
        t1 = (q1 or "").strip()
        t2 = (q2 or "").strip()
        problems = []
        if not pid:
            problems.append("Please enter your **Prolific ID**.")
        elif not PROLIFIC_ID_RE.match(pid):
            problems.append(
                "Please check your **Prolific ID** (letters and numbers only, about 24 characters)."
            )
        if len(t1) < INTAKE_MIN_LEN_Q1:
            problems.append(
                f"Please write a bit more for **(1)** (at least {INTAKE_MIN_LEN_Q1} characters)."
            )
        if not t2:
            problems.append("Please answer **(2)**.")
        if problems:
            for p in problems:
                st.error(p)
        else:
            st.session_state["prolific_id"] = pid
            st.session_state["brief_conflict"] = t1
            st.session_state["relationship_type"] = t2
            st.switch_page("pages/1_Event.py")
