"""Minimum time per interview section before Continue can unlock."""

from __future__ import annotations

import time

import streamlit as st

SECTION_MIN_DURATION_SEC = 3 * 60


def _section_time_key(section: str) -> str:
    return f"_section_start_time_{section}"


def ensure_section_clock(section: str) -> None:
    if _section_time_key(section) not in st.session_state:
        st.session_state[_section_time_key(section)] = time.monotonic()


def section_elapsed_sec(section: str) -> float:
    start = st.session_state.get(_section_time_key(section))
    if start is None:
        return 0.0
    return max(0.0, time.monotonic() - float(start))


def section_min_met(section: str) -> bool:
    return section_elapsed_sec(section) >= SECTION_MIN_DURATION_SEC


def section_can_continue(section: str) -> bool:
    return section_min_met(section)


def format_mmss(seconds: float) -> str:
    total = max(0, int(seconds))
    minutes, secs = divmod(total, 60)
    return f"{minutes}:{secs:02d}"


def section_remaining_continue_sec(section: str) -> int:
    if section_min_met(section):
        return 0
    return max(0, int(SECTION_MIN_DURATION_SEC - section_elapsed_sec(section)))
