"""Anthropic Messages API helper for Streamlit."""

from __future__ import annotations

import os
from typing import Any, Optional

import anthropic
import streamlit as st


def default_model() -> str:
    # Override with ANTHROPIC_MODEL; Sonnet 3.5 is widely available on Anthropic API keys.
    return os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")


def get_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        try:
            key = st.secrets.get("ANTHROPIC_API_KEY", "")
        except Exception:
            key = ""
    return key.strip()


def get_client() -> anthropic.Anthropic:
    key = get_api_key()
    if not key:
        raise RuntimeError(
            "Missing ANTHROPIC_API_KEY. Set it in the environment or "
            ".streamlit/secrets.toml (see .streamlit/secrets.toml.example)."
        )
    return anthropic.Anthropic(api_key=key)


def run_turn(
    *,
    system: str,
    messages: list[dict[str, Any]],
    model: Optional[str] = None,
    max_tokens: int = 1024,
) -> str:
    """Single non-streaming completion; returns assistant text."""
    client = get_client()
    model = model or default_model()
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    )
    parts: list[str] = []
    for block in resp.content:
        if hasattr(block, "text"):
            parts.append(block.text)
    return "".join(parts).strip()


def stream_turn(
    *,
    system: str,
    messages: list[dict[str, Any]],
    model: Optional[str] = None,
    max_tokens: int = 1024,
):
    """Yield text chunks for st.write_stream."""
    client = get_client()
    model = model or default_model()
    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text
