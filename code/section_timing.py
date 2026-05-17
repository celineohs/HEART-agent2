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


def section_can_continue(section: str, *, content_ready: bool) -> bool:
    return content_ready and section_min_met(section)
