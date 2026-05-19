"""Minimum time per interview section before Continue can unlock."""

from __future__ import annotations

import time
from typing import Any

import streamlit as st

SECTION_MIN_DURATION_SEC: dict[str, int] = {
    "event": 5 * 60,
    "emotion": 3 * 60,
    "thoughts": 5 * 60,
}

INTERVIEW_SECTIONS = ("event", "emotion", "thoughts")

_INTERVIEW_START_KEY = "_interview_start_monotonic"
_INTERVIEW_END_KEY = "_interview_end_monotonic"
_SECTION_DURATIONS_KEY = "_section_durations_sec"


def section_min_duration_sec(section: str) -> int:
    return SECTION_MIN_DURATION_SEC.get(section, 3 * 60)


def _section_time_key(section: str) -> str:
    return f"_section_start_time_{section}"


def _round_duration_sec(seconds: float) -> float:
    return round(max(0.0, seconds), 1)


def _section_durations() -> dict[str, float]:
    raw = st.session_state.get(_SECTION_DURATIONS_KEY)
    if not isinstance(raw, dict):
        raw = {}
        st.session_state[_SECTION_DURATIONS_KEY] = raw
    return raw


def ensure_section_clock(section: str) -> None:
    if _section_time_key(section) not in st.session_state:
        st.session_state[_section_time_key(section)] = time.monotonic()
    if section == "event" and _INTERVIEW_START_KEY not in st.session_state:
        st.session_state[_INTERVIEW_START_KEY] = time.monotonic()


def finalize_section_duration(section: str) -> None:
    """Freeze elapsed time for a section (idempotent). Called when leaving the section."""
    durations = _section_durations()
    if section in durations:
        return
    start = st.session_state.get(_section_time_key(section))
    if start is None:
        return
    durations[section] = _round_duration_sec(time.monotonic() - float(start))


def mark_interview_complete() -> None:
    """Freeze total interview duration at completion (idempotent)."""
    if _INTERVIEW_END_KEY not in st.session_state:
        st.session_state[_INTERVIEW_END_KEY] = time.monotonic()


def build_timing_record() -> dict[str, Any]:
    """Section and total durations for JSON export."""
    stored = dict(_section_durations())
    section_durations: dict[str, float] = {}
    for name in INTERVIEW_SECTIONS:
        if name in stored:
            section_durations[name] = stored[name]
            continue
        start = st.session_state.get(_section_time_key(name))
        if start is not None:
            section_durations[name] = _round_duration_sec(
                time.monotonic() - float(start)
            )

    interview_start = st.session_state.get(_INTERVIEW_START_KEY)
    interview_end = st.session_state.get(_INTERVIEW_END_KEY)
    if interview_start is not None and interview_end is not None:
        total = float(interview_end) - float(interview_start)
    else:
        total = sum(section_durations.values())

    return {
        "section_durations_sec": section_durations,
        "total_duration_sec": _round_duration_sec(total),
    }


def section_elapsed_sec(section: str) -> float:
    start = st.session_state.get(_section_time_key(section))
    if start is None:
        return 0.0
    return max(0.0, time.monotonic() - float(start))


def section_min_met(section: str) -> bool:
    return section_elapsed_sec(section) >= section_min_duration_sec(section)


def section_can_continue(section: str) -> bool:
    return section_min_met(section)


def format_mmss(seconds: float) -> str:
    total = max(0, int(seconds))
    minutes, secs = divmod(total, 60)
    return f"{minutes}:{secs:02d}"


def section_remaining_continue_sec(section: str) -> int:
    if section_min_met(section):
        return 0
    return max(0, int(section_min_duration_sec(section) - section_elapsed_sec(section)))
