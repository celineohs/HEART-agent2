import streamlit as st

st.set_page_config(
    page_title="HEART · Intake",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("HEART qualitative interview (pilot)")
st.markdown(
    """
This study explores **one recent interpersonal conflict** you experienced. Everything here is in **English**.

The interview has three short chat sections—**Event**, **Emotion**, and **Thoughts**—after this page.
Your answers are **not** counseling and **not** an evaluation; we are listening to **your account** in your own words.

Please avoid including real names or identifying details; use roles (e.g. “my supervisor,” “a friend”) instead.
    """
)

with st.sidebar:
    st.markdown("### Sections")
    st.page_link("app.py", label="Home · Intake")
    st.page_link("pages/1_Event.py", label="Event")
    st.page_link("pages/2_Emotion.py", label="Emotion")
    st.page_link("pages/3_Thoughts.py", label="Thoughts")
    st.divider()
    if st.button("Clear conversation & intake (reset study session)", type="secondary"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

with st.form("intake_form"):
    st.subheader("Background (free text)")
    q1 = st.text_area(
        "(1) Briefly describe an interpersonal conflict you've had with someone close to you recently.",
        height=140,
        value=st.session_state.get("brief_conflict", ""),
        placeholder="A short factual description in your own words is enough.",
    )
    q2 = st.text_area(
        "(2) What is your relationship to the other person?",
        height=100,
        value=st.session_state.get("relationship_type", ""),
        placeholder="e.g. partner, flatmate, colleague, friend, family member …",
    )
    submitted = st.form_submit_button("Save and continue to Event")
    if submitted:
        if not (q1 or "").strip() or not (q2 or "").strip():
            st.error("Please answer both questions before continuing.")
        else:
            st.session_state["brief_conflict"] = q1.strip()
            st.session_state["relationship_type"] = q2.strip()
            st.switch_page("pages/1_Event.py")
