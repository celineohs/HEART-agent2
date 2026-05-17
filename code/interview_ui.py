"""Shared Streamlit UI for interview sections."""

from __future__ import annotations

from datetime import timedelta
from typing import Optional

import streamlit as st

from chat_client import get_api_key, run_turn, stream_turn
from prompts import build_system
from interview_export import upload_interview_once
from section_readiness import assess_section_readiness
from section_timing import (
    SECTION_MIN_DURATION_SEC,
    ensure_section_clock,
    section_can_continue,
    section_min_met,
)
from ui_style import apply_global_styles

_SECTION_NEXT: dict[str, tuple[str, str]] = {
    "event": ("pages/2_Emotion.py", "emotion"),
    "emotion": ("pages/3_Thoughts.py", "thoughts"),
}


def _require_intake() -> None:
    b = st.session_state.get("brief_conflict", "").strip()
    r = st.session_state.get("relationship_type", "").strip()
    if not b or not r:
        st.error("Please start from the **home** page and complete the background questions first.")
        st.page_link("app.py", label="→ Go to start")
        st.stop()


def _section_start_key(section: str) -> str:
    return f"_section_start_idx_{section}"


def _section_messages(section: str) -> list:
    start = st.session_state.get(_section_start_key(section), 0)
    return st.session_state["messages"][start:]


def _render_intake_summary() -> None:
    with st.expander("What you shared at the start", expanded=True):
        st.markdown("**(1) Brief description of the recent interpersonal conflict**")
        st.markdown(st.session_state["brief_conflict"])
        st.markdown("**(2) Relationship to the other person**")
        st.markdown(st.session_state["relationship_type"])


def _rerun_when_min_time_met(section: str) -> None:
    """Rerun the page when the 3-minute minimum elapses so Continue can unlock."""

    @st.fragment(run_every=timedelta(seconds=10))
    def _tick() -> None:
        ensure_section_clock(section)
        met = section_min_met(section)
        phase_key = f"_section_min_phase_{section}"
        prev = st.session_state.get(phase_key)
        if prev is not None and not prev and met:
            st.rerun()
        st.session_state[phase_key] = met

    _tick()


def _continue_availability_caption(next_label: str) -> str:
    mins = SECTION_MIN_DURATION_SEC // 60
    return (
        f"**{next_label}** will be available after at least **{mins} minutes** in this part, "
        "once the interviewer has gathered enough detail."
    )


def _mark_next_section_start(next_section: str) -> None:
    st.session_state[_section_start_key(next_section)] = len(
        st.session_state["messages"]
    )
    st.session_state.pop(f"_section_ready_{next_section}", None)
    st.session_state.pop(f"_readiness_msg_count_{next_section}", None)
    st.session_state.pop(f"_section_min_phase_{next_section}", None)


def _update_section_readiness(section: str) -> bool:
    msgs = _section_messages(section)
    count_key = f"_readiness_msg_count_{section}"
    ready_key = f"_section_ready_{section}"
    if st.session_state.get(count_key) == len(msgs) and ready_key in st.session_state:
        return st.session_state[ready_key]

    ready = assess_section_readiness(
        section,
        msgs,
        brief_conflict=st.session_state["brief_conflict"],
        relationship=st.session_state["relationship_type"],
    )
    st.session_state[count_key] = len(msgs)
    st.session_state[ready_key] = ready
    return ready


def _bootstrap_event(system: str) -> None:
    """Start Event chat with intake context for the API only (not shown in the UI)."""
    intake_turn = (
        "**(1) Brief description of the recent interpersonal conflict:**\n"
        f"{st.session_state['brief_conflict']}\n\n"
        "**(2) Relationship to the other person:**\n"
        f"{st.session_state['relationship_type']}"
    ).strip()
    try:
        text = run_turn(
            system=system,
            messages=[{"role": "user", "content": intake_turn}],
        )
    except Exception:
        raise
    st.session_state["messages"].append({"role": "assistant", "content": text})
    st.session_state["_event_seeded"] = True
    if _section_start_key("event") not in st.session_state:
        st.session_state[_section_start_key("event")] = 0
    _update_section_readiness("event")


def render_chat_page(
    *,
    section: str,
    headline: str,
    blurb: Optional[str] = None,
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

    if section != "event" and _section_start_key(section) not in st.session_state:
        st.session_state[_section_start_key(section)] = len(
            st.session_state["messages"]
        )

    ensure_section_clock(section)

    st.title(headline)
    if blurb:
        st.markdown(blurb)

    _render_intake_summary()

    if next_page:
        st.caption(_continue_availability_caption(next_label))
        _rerun_when_min_time_met(section)

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if next_page:
        ready = _update_section_readiness(section)
        can_continue = section_can_continue(section, content_ready=ready)
        st.divider()
        if st.button(
            next_label,
            type="primary",
            key=f"next_{section}",
            disabled=not can_continue,
        ):
            next_meta = _SECTION_NEXT.get(section)
            if next_meta:
                _mark_next_section_start(next_meta[1])
            if section == "thoughts":
                st.session_state["_interview_completed"] = True
                with st.spinner("Saving your interview…"):
                    upload_interview_once()
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
        if next_page:
            _update_section_readiness(section)
            st.rerun()
