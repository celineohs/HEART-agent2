"""Per-section time bounds for Event, Emotion, and Thoughts chat pages."""

from __future__ import annotations

import time
from typing import Optional

import streamlit as st

SECTION_MIN_DURATION_SEC = 3 * 60
SECTION_MAX_DURATION_SEC = 5 * 60


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


def section_max_reached(section: str) -> bool:
    return section_elapsed_sec(section) >= SECTION_MAX_DURATION_SEC


def section_can_continue(section: str, *, content_ready: bool) -> bool:
    if section_max_reached(section):
        return True
    return content_ready and section_min_met(section)


def section_chat_allowed(section: str) -> bool:
    return not section_max_reached(section)


def format_time_hint(section: str) -> Optional[str]:
    elapsed = section_elapsed_sec(section)
    if section_max_reached(section):
        return None
    if not section_min_met(section):
        remaining = int(SECTION_MIN_DURATION_SEC - elapsed)
        mins = max(1, (remaining + 59) // 60)
        return f"**Continue** unlocks in about {mins} min (minimum {SECTION_MIN_DURATION_SEC // 60} min per section)."
    remaining = int(SECTION_MAX_DURATION_SEC - elapsed)
    if remaining <= 60:
        return "About 1 min left in this section."
    mins = max(1, (remaining + 59) // 60)
    return f"About {mins} min left in this section (max {SECTION_MAX_DURATION_SEC // 60} min)."
