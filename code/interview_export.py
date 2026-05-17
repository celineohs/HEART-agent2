"""Build interview JSON and upload to Google Drive on completion."""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import streamlit as st

from gdrive_upload import upload_file_to_drive

SCHEMA_VERSION = 1


def get_env(key: str, default: Optional[str] = None) -> str:
    val = os.environ.get(key)
    if val is not None and str(val).strip():
        return str(val).strip()
    try:
        secret = st.secrets.get(key, default)
    except Exception:
        secret = default
    if secret is None:
        return (default or "").strip()
    return str(secret).strip()


def is_drive_configured() -> bool:
    folder_id = get_env("GOOGLE_DRIVE_FOLDER_ID")
    if not folder_id:
        return False
    oauth = all(
        get_env(k)
        for k in (
            "GOOGLE_DRIVE_OAUTH_CLIENT_ID",
            "GOOGLE_DRIVE_OAUTH_CLIENT_SECRET",
            "GOOGLE_DRIVE_OAUTH_REFRESH_TOKEN",
        )
    )
    if oauth:
        return True
    return bool(get_env("GOOGLE_DRIVE_CREDENTIALS_JSON"))


def build_interview_record() -> dict[str, Any]:
    boundaries = {
        name: st.session_state.get(f"_section_start_idx_{name}")
        for name in ("event", "emotion", "thoughts")
        if f"_section_start_idx_{name}" in st.session_state
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "study": "HEART-agent2",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "session_id": st.session_state.get(
            "_interview_session_id",
            str(uuid.uuid4()),
        ),
        "intake": {
            "brief_conflict": st.session_state.get("brief_conflict", ""),
            "relationship_type": st.session_state.get("relationship_type", ""),
        },
        "section_boundaries": boundaries,
        "messages": list(st.session_state.get("messages", [])),
    }


def _export_filename() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    short_id = st.session_state.get("_interview_session_id", uuid.uuid4().hex)[:8]
    return f"heart_interview_{ts}_{short_id}.json"


def ensure_session_id() -> None:
    if "_interview_session_id" not in st.session_state:
        st.session_state["_interview_session_id"] = uuid.uuid4().hex


def upload_interview_once() -> tuple[bool, str]:
    """Upload interview JSON once per session. Returns (ok, message)."""
    if st.session_state.get("_interview_uploaded"):
        return (
            bool(st.session_state.get("_drive_upload_ok", True)),
            str(st.session_state.get("_drive_upload_message", "")),
        )

    ensure_session_id()
    record = build_interview_record()
    filename = _export_filename()

    if not is_drive_configured():
        st.session_state["_interview_uploaded"] = True
        st.session_state["_drive_upload_ok"] = True
        st.session_state["_drive_upload_message"] = "Drive not configured (skipped)."
        return True, "Drive not configured (skipped)."

    tmp_dir = tempfile.mkdtemp(prefix="heart_export_")
    tmp_path = os.path.join(tmp_dir, filename)
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)

        ok, msg = upload_file_to_drive(tmp_path, get_env)
        st.session_state["_interview_uploaded"] = True
        st.session_state["_drive_upload_ok"] = ok
        st.session_state["_drive_upload_message"] = msg
        return ok, msg
    finally:
        if os.path.isfile(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        try:
            os.rmdir(tmp_dir)
        except OSError:
            pass
