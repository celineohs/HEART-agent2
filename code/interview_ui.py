"""Shared Streamlit UI for interview sections."""

from __future__ import annotations

from typing import Optional

import streamlit as st

from chat_client import get_api_key, run_turn, stream_turn
from prompts import build_system
from ui_style import apply_global_styles


def _require_intake() -> None:
    b = st.session_state.get("brief_conflict", "").strip()
    r = st.session_state.get("relationship_type", "").strip()
    if not b or not r:
        st.error("Please start from the **home** page and complete the background questions first.")
        st.page_link("app.py", label="→ Go to start")
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
    next_page: Optional[str] = None,
    next_label: str = "Continue",
) -> None:
    apply_global_styles()
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
        st.warning(
            "This step works best after you’ve gone through the first conversation. "
            "Use the link below if you landed here out of order."
        )
        st.page_link("app.py", label="→ Go to start")
        st.page_link("pages/1_Event.py", label="→ Go to first conversation")
        st.stop()

    st.title(headline)
    st.markdown(blurb)

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if next_page:
        st.divider()
        if st.button(next_label, type="primary", key=f"next_{section}"):
            st.switch_page(next_page)

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
