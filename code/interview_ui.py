"""Shared Streamlit UI for interview sections."""

from __future__ import annotations

from datetime import timedelta
from typing import Optional

import streamlit as st

from chat_client import get_api_key, run_turn, stream_turn
from prompts import build_system
from interview_export import upload_interview_once
from section_timing import (
    ensure_section_clock,
    finalize_section_duration,
    format_mmss,
    mark_interview_complete,
    section_can_continue,
    section_min_duration_sec,
    section_min_met,
    section_remaining_continue_sec,
)
from ui_style import apply_global_styles

_SECTION_NEXT: dict[str, tuple[str, str]] = {
    "event": ("pages/2_Emotion.py", "emotion"),
    "emotion": ("pages/3_Thoughts.py", "thoughts"),
}

# Sent to the API only (not stored in messages) when a section page opens.
_SECTION_OPENING_USER: dict[str, str] = {
    "emotion": """
[Section transition — internal; the participant does not see this line.]
The Event section is complete. Begin the **Emotion** section now in English.
Ask exactly one short question about how they felt during that same situation (type, quality, or strength of feeling).
Keep the reply brief (one short lead-in sentence at most). Do not recap the event.
Do not re-ask event sequencing, the other person's perspective, beliefs, or ideals.
""".strip(),
    "thoughts": """
[Section transition — internal; the participant does not see this line.]
The Emotion section is complete. Begin the **Thoughts** section now in English.
Ask exactly one short question about what they believed or expected during that episode, or what an ideal interaction would have looked like to them.
Keep the reply brief (one short lead-in sentence at most). Do not recap prior sections.
Do not re-ask event sequencing or emotion labeling unless one short phrase anchors to the scene.
""".strip(),
}


def _require_intake() -> None:
    p = st.session_state.get("prolific_id", "").strip()
    b = st.session_state.get("brief_conflict", "").strip()
    r = st.session_state.get("relationship_type", "").strip()
    if not p or not b or not r:
        st.error("Please start from the **home** page and complete the background questions first.")
        st.page_link("app.py", label="→ Go to start")
        st.stop()


def _section_start_key(section: str) -> str:
    return f"_section_start_idx_{section}"


def _section_seeded_key(section: str) -> str:
    return f"_section_seeded_{section}"


def _visible_messages(section: str) -> list:
    """Messages shown in the UI for this section (prior sections hidden)."""
    start = int(st.session_state.get(_section_start_key(section), 0))
    return st.session_state["messages"][start:]


def _render_intake_summary() -> None:
    with st.expander("What you shared at the start", expanded=True):
        st.markdown("**Prolific ID**")
        st.markdown(st.session_state.get("prolific_id", ""))
        st.markdown("**(1) Brief description of the recent interpersonal conflict**")
        st.markdown(st.session_state["brief_conflict"])
        st.markdown("**(2) Relationship to the other person**")
        st.markdown(st.session_state["relationship_type"])


def _interview_bottom():
    """Pinned footer (st.bottom or st._bottom depending on Streamlit version)."""
    return getattr(st, "bottom", st._bottom)


def _continue_availability_caption(section: str, next_label: str) -> str:
    mins = section_min_duration_sec(section) // 60
    return (
        f"**{next_label}** is available after **at least {mins} minutes** in this part. "
        f"Please press {next_label} **only after you have shared enough in your answers.**"
    )


def _render_section_chat_guidance(section: str, next_label: str) -> None:
    mins = section_min_duration_sec(section) // 60
    st.markdown(
        f"""
<div class="heart-section-guidance">
  <p class="heart-section-guidance__title">How this part works</p>
  <ul class="heart-section-guidance__list">
    <li>Submit each reply with the <strong>send button</strong> or by pressing
        <strong>Enter</strong> in the box below. <strong>{next_label}</strong> moves you to the
        next part; it becomes available after at least <strong>{mins} minutes</strong> here.</li>
    <li>Please use the time in this part to have a <strong>full conversation</strong> with the
        chatbot.</li>
  </ul>
</div>
        """.strip(),
        unsafe_allow_html=True,
    )


def _render_chat_area_header() -> None:
    st.markdown(
        """
<div class="heart-chat-area-header">
  <span class="heart-chat-area-header__label">Conversation</span>
  <span class="heart-chat-area-header__line"></span>
</div>
        """.strip(),
        unsafe_allow_html=True,
    )


def _render_page_chrome(
    *,
    section: str,
    headline: str,
    blurb: Optional[str],
    next_label: str,
) -> None:
    st.title(headline)
    if blurb:
        st.markdown(blurb)
    _render_intake_summary()
    _render_section_chat_guidance(section, next_label)
    _render_chat_area_header()


def _render_chat_messages(section: str) -> None:
    for msg in _visible_messages(section):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def _mark_next_section_start(next_section: str) -> None:
    st.session_state[_section_start_key(next_section)] = len(
        st.session_state["messages"]
    )
    st.session_state.pop(f"_section_min_phase_{next_section}", None)


def _bootstrap_event(system: str) -> None:
    """Start Event chat with intake context for the API only (not shown in the UI)."""
    intake_turn = (
        "**(1) Brief description of the recent interpersonal conflict:**\n"
        f"{st.session_state['brief_conflict']}\n\n"
        "**(2) Relationship to the other person:**\n"
        f"{st.session_state['relationship_type']}"
    ).strip()
    text = run_turn(
        system=system,
        messages=[{"role": "user", "content": intake_turn}],
    )
    st.session_state["messages"].append({"role": "assistant", "content": text})
    st.session_state["_event_seeded"] = True
    if _section_start_key("event") not in st.session_state:
        st.session_state[_section_start_key("event")] = 0


def _bootstrap_section_opening(section: str, system: str) -> None:
    """Open Emotion/Thoughts with one assistant turn; full prior history goes to the API only."""
    transition = _SECTION_OPENING_USER[section]
    api_messages = list(st.session_state["messages"])
    api_messages.append({"role": "user", "content": transition})
    text = run_turn(system=system, messages=api_messages)
    st.session_state["messages"].append({"role": "assistant", "content": text})
    st.session_state[_section_seeded_key(section)] = True


def _handle_continue(
    *,
    section: str,
    next_page: str,
) -> None:
    finalize_section_duration(section)
    if section == "thoughts":
        mark_interview_complete()
    next_meta = _SECTION_NEXT.get(section)
    if next_meta:
        _mark_next_section_start(next_meta[1])
    if section == "thoughts":
        st.session_state["_interview_completed"] = True
        with st.spinner("Saving your interview…"):
            upload_interview_once()
    st.switch_page(next_page)


def _handle_user_message(
    user_text: str,
    *,
    section: str,
    system: str,
    has_next_page: bool,
) -> None:
    st.session_state["messages"].append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)
    with st.chat_message("assistant"):
        try:
            full = st.write_stream(
                stream_turn(system=system, messages=st.session_state["messages"])
            )
        except Exception as e:
            st.error(f"Could not reach the model: {e}")
            st.session_state["messages"].pop()
            st.stop()
    st.session_state["messages"].append({"role": "assistant", "content": full or ""})
    if has_next_page:
        st.rerun()


def _render_continue_controls(
    *,
    section: str,
    next_page: str,
    next_label: str,
) -> None:
    """Timer + Continue; isolated fragment so run_every does not drop the button."""

    @st.fragment(run_every=timedelta(seconds=1))
    def _controls() -> None:
        ensure_section_clock(section)
        can_continue = section_can_continue(section)
        met = section_min_met(section)

        hint_col, timer_col = st.columns([11, 1], vertical_alignment="center")
        with hint_col:
            st.caption(_continue_availability_caption(section, next_label))
        with timer_col:
            if not met:
                st.markdown(
                    f'<p style="margin:0;color:#888;font-size:0.85rem;text-align:right;">'
                    f"{format_mmss(section_remaining_continue_sec(section))}</p>",
                    unsafe_allow_html=True,
                )
        if st.button(
            next_label,
            type="primary",
            key=f"next_{section}",
            disabled=not can_continue,
            use_container_width=True,
        ):
            _handle_continue(section=section, next_page=next_page)

    _controls()


def _render_interview_footer(
    *,
    section: str,
    system: str,
    next_page: Optional[str],
    next_label: str,
) -> None:
    with _interview_bottom():
        user_text = st.chat_input("Type your reply…", key=f"chat_input_{section}")
        if next_page:
            _render_continue_controls(
                section=section,
                next_page=next_page,
                next_label=next_label,
            )

    if user_text:
        _handle_user_message(
            user_text,
            section=section,
            system=system,
            has_next_page=bool(next_page),
        )


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
        _render_page_chrome(
            section=section, headline=headline, blurb=blurb, next_label=next_label
        )
        with st.chat_message("assistant"):
            with st.spinner("Starting the interview…"):
                try:
                    _bootstrap_event(system)
                except Exception as e:
                    st.error(f"Could not reach the model: {e}")
                    st.stop()
        st.rerun()

    if section != "event" and not st.session_state.get("_event_seeded"):
        st.warning(
            "This step works best after you’ve gone through the first conversation. "
            "Use the links below if you landed here out of order."
        )
        st.page_link("app.py", label="→ Go to start")
        st.page_link("pages/1_Event.py", label="→ Go to first conversation")
        st.stop()

    if section != "event" and _section_start_key(section) not in st.session_state:
        st.session_state[_section_start_key(section)] = len(
            st.session_state["messages"]
        )

    if (
        section in _SECTION_OPENING_USER
        and not st.session_state.get(_section_seeded_key(section))
    ):
        _render_page_chrome(
            section=section, headline=headline, blurb=blurb, next_label=next_label
        )
        with st.chat_message("assistant"):
            with st.spinner(f"Starting the {headline.lower()} section…"):
                try:
                    _bootstrap_section_opening(section, system)
                except Exception as e:
                    st.error(f"Could not reach the model: {e}")
                    st.stop()
        st.rerun()

    ensure_section_clock(section)

    _render_page_chrome(
        section=section, headline=headline, blurb=blurb, next_label=next_label
    )
    _render_chat_messages(section)
    _render_interview_footer(
        section=section,
        system=system,
        next_page=next_page,
        next_label=next_label,
    )
