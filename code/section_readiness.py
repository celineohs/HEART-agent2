"""LLM-based check that a section has enough qualitative coverage."""

from __future__ import annotations

from typing import Any

from chat_client import run_turn

SECTION_CRITERIA: dict[str, str] = {
    "event": """
- A concrete moment in the conflict episode is anchored (when/where or clear situational frame).
- The interaction is narrated in rough sequence: what they noticed, said, and did (observable thread).
- Their behaviour and the other person's behaviour in that situation are described at the level of what happened.
- Their reasons or intent for their own actions during the event are explored at least briefly.
- Tentative sense of whether the other would agree with their account and/or know their reasons has been touched.
- At least some careful inference about the other's mental state or attitude during the event, with what led them there.
""".strip(),
    "emotion": """
- Emotion type(s) or quality during that same situation are described in the participant's own words.
- Strength or intensity (and, if offered, stability/shift across the episode) is addressed.
""".strip(),
    "thoughts": """
- Beliefs or expectations about the other, situation, or topic around this episode are described.
- What an ideal version of the interaction would have looked like to them is described concretely enough to picture.
- Tentative sense of whether the other might have shared that ideal (or where mismatch might be) has been explored.
""".strip(),
}


def _format_transcript(messages: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for m in messages:
        role = m.get("role", "unknown")
        content = (m.get("content") or "").strip()
        if not content:
            continue
        label = "Interviewer" if role == "assistant" else "Participant"
        lines.append(f"{label}: {content}")
    return "\n\n".join(lines) if lines else "(no messages yet)"


def assess_section_readiness(
    section: str,
    messages: list[dict[str, Any]],
    *,
    brief_conflict: str,
    relationship: str,
) -> bool:
    if section not in SECTION_CRITERIA:
        raise ValueError(f"Unknown section: {section}")

    criteria = SECTION_CRITERIA[section]
    transcript = _format_transcript(messages)

    system = f"""You judge whether a qualitative interview **section** has gathered **enough usable data** to move on.

Be **conservative**: answer READY only when the criteria below are **substantively** covered in the **participant's own words** (brief but usable answers count; one-word or evasive replies do not).

Ignore onboarding seed text that only restates intake forms unless the participant elaborated in later turns.

**Section:** {section.title()}

**Criteria (all should be met in substance):**
{criteria}

**Onboarding context (for reference only):**
Conflict (brief): {brief_conflict}
Relationship: {relationship}

Reply with **exactly one word**: READY or NOT_READY."""

    user = f"## Transcript (this section only)\n\n{transcript}"

    verdict = run_turn(
        system=system,
        messages=[{"role": "user", "content": user}],
        max_tokens=16,
    ).strip().upper()

    return "READY" in verdict and "NOT_READY" not in verdict
