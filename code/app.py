import streamlit as st

st.set_page_config(
    page_title="HEART · Intake",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from interview_export import ensure_session_id
from section_timing import SECTION_MAX_DURATION_SEC, SECTION_MIN_DURATION_SEC
from ui_style import apply_global_styles

apply_global_styles()
ensure_session_id()

# Minimum response length so “continue” only works with real answers (not one word / whitespace).
INTAKE_MIN_LEN_Q1 = 40
INTAKE_MIN_LEN_Q2 = 8

if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("HEART qualitative interview (pilot)")
st.markdown(
    "Briefly tell us about **one recent interpersonal conflict** and **who the other person is** to you."
)
st.caption(
    f"Each conversation part is about **{SECTION_MIN_DURATION_SEC // 60}–"
    f"{SECTION_MAX_DURATION_SEC // 60} minutes**."
)

st.divider()

with st.form("intake_form"):
    st.subheader("Background (free text)")
    q1 = st.text_area(
        "(1) Briefly describe an interpersonal conflict you've had with someone close to you recently.",
        height=160,
        value=st.session_state.get("brief_conflict", ""),
        placeholder="A short factual description in your own words is enough.",
    )
    q2 = st.text_area(
        "(2) What is your relationship to the other person?",
        height=110,
        value=st.session_state.get("relationship_type", ""),
        placeholder="e.g. partner, flatmate, colleague, friend, family member …",
    )
    submitted = st.form_submit_button("Continue")
    if submitted:
        t1 = (q1 or "").strip()
        t2 = (q2 or "").strip()
        problems = []
        if len(t1) < INTAKE_MIN_LEN_Q1:
            problems.append(
                f"Please write a bit more for **(1)** (at least {INTAKE_MIN_LEN_Q1} characters)."
            )
        if len(t2) < INTAKE_MIN_LEN_Q2:
            problems.append(
                f"Please write a bit more for **(2)** (at least {INTAKE_MIN_LEN_Q2} characters)."
            )
        if problems:
            for p in problems:
                st.error(p)
        else:
            st.session_state["brief_conflict"] = t1
            st.session_state["relationship_type"] = t2
            st.switch_page("pages/1_Event.py")
