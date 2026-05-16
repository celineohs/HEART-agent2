"""Shared Streamlit UI for interview sections."""

from __future__ import annotations

import streamlit as st

from chat_client import get_api_key, run_turn, stream_turn
from prompts import build_system
from ui_style import apply_global_styles


def _top_nav() -> None:
    apply_global_styles()
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1.1])
    with c1:
        st.page_link("app.py", label="Home")
    with c2:
        st.page_link("pages/1_Event.py", label="Event")
    with c3:
        st.page_link("pages/2_Emotion.py", label="Emotion")
    with c4:
        st.page_link("pages/3_Thoughts.py", label="Thoughts")
    with c5:
        if st.button("Reset session", type="secondary", key="nav_reset_session"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
    st.divider()


def _require_intake() -> None:
    b = st.session_state.get("brief_conflict", "").strip()
    r = st.session_state.get("relationship_type", "").strip()
    if not b or not r:
        st.error("Please complete the intake on the **Home** page first.")
        st.page_link("app.py", label="→ Go to Home")
        st.stop()


def _bootstrap_event(system: str) -> None:
    seed = (
        "[Study onboarding — begin the **Event** section in English.]\n\n"
        "**(1) Brief description of the recent interpersonal conflict:**\n"
        f"{st.session_state['brief_conflict']}\n\n"
        "**(2) Relationship to the other person:**\n"
        f"{st.session_state['relationship_type']}"
    ).strip()
    st.session_state["messages"].append({"role": "user", "content": seed})
    try:
        text = run_turn(system=system, messages=st.session_state["messages"])
    except Exception as e:
        st.session_state["messages"].pop()
        raise e
    st.session_state["messages"].append({"role": "assistant", "content": text})
    st.session_state["_event_seeded"] = True


def render_chat_page(
    *,
    section: str,
    headline: str,
    blurb: str,
) -> None:
    _top_nav()
    _require_intake()

    if not get_api_key():
        st.error(
            "Configure **ANTHROPIC_API_KEY** (environment variable or `.streamlit/secrets.toml`). "
            "See `.streamlit/secrets.toml.example`."
        )
        st.stop()

    system = build_system(
        section,
        st.session_state["brief_conflict"],
        st.session_state["relationship_type"],
    )

    if section == "event" and not st.session_state.get("_event_seeded"):
        with st.spinner("Starting the interview…"):
            try:
                _bootstrap_event(system)
            except Exception as e:
                st.error(f"Could not reach the model: {e}")
                st.stop()
    elif section != "event" and not st.session_state.get("_event_seeded"):
        st.info(
            "Tip: completing the **Event** section first usually makes this part easier, "
            "but you can still continue whenever you are ready."
        )

    st.title(headline)
    st.markdown(blurb)

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_text := st.chat_input("Type your reply…"):
        st.session_state["messages"].append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)
        assistant_box = st.chat_message("assistant")
        with assistant_box:
            try:
                full = st.write_stream(
                    stream_turn(system=system, messages=st.session_state["messages"])
                )
            except Exception as e:
                st.error(f"Could not reach the model: {e}")
                st.session_state["messages"].pop()
                st.stop()
        st.session_state["messages"].append(
            {"role": "assistant", "content": full or ""}
        )
