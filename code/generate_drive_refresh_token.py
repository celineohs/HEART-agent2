#!/usr/bin/env python3
"""
One-time helper: obtain GOOGLE_DRIVE_OAUTH_REFRESH_TOKEN for Streamlit secrets.

Service accounts cannot upload to personal My Drive folders (no storage quota).
Use OAuth so uploads use your Google account's Drive.

Prerequisites:
  - Google Cloud project with Drive API enabled
  - OAuth client (Desktop app) → CLIENT_ID and CLIENT_SECRET

Usage (from the code/ directory):
  pip install google-auth-oauthlib
  export GOOGLE_DRIVE_OAUTH_CLIENT_ID="....apps.googleusercontent.com"
  export GOOGLE_DRIVE_OAUTH_CLIENT_SECRET="...."
  python generate_drive_refresh_token.py

Or pass a downloaded OAuth client JSON:
  python generate_drive_refresh_token.py ~/Downloads/client_secret_....json

Add the printed refresh token to Streamlit Cloud secrets as GOOGLE_DRIVE_OAUTH_REFRESH_TOKEN.
Remove or leave empty GOOGLE_DRIVE_CREDENTIALS_JSON so OAuth is used first.
"""

from __future__ import annotations

import json
import os
import sys

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _client_config_from_env() -> dict:
    client_id = os.environ.get("GOOGLE_DRIVE_OAUTH_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_DRIVE_OAUTH_CLIENT_SECRET", "").strip()
    if not (client_id and client_secret):
        print(
            "Set GOOGLE_DRIVE_OAUTH_CLIENT_ID and GOOGLE_DRIVE_OAUTH_CLIENT_SECRET, "
            "or pass a client_secret JSON file path.",
            file=sys.stderr,
        )
        sys.exit(1)
    return {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }


def main() -> None:
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("pip install google-auth-oauthlib", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) > 1:
        flow = InstalledAppFlow.from_client_secrets_file(sys.argv[1], SCOPES)
    else:
        flow = InstalledAppFlow.from_client_config(_client_config_from_env(), SCOPES)

    creds = flow.run_local_server(port=0)
    print("\nAdd to Streamlit secrets (.streamlit/secrets.toml or Cloud):")
    print(f"GOOGLE_DRIVE_OAUTH_REFRESH_TOKEN = {json.dumps(creds.refresh_token)}")
    if creds.client_id:
        print(f"GOOGLE_DRIVE_OAUTH_CLIENT_ID = {json.dumps(creds.client_id)}")
    if creds.client_secret:
        print(f"GOOGLE_DRIVE_OAUTH_CLIENT_SECRET = {json.dumps(creds.client_secret)}")
    print("\nGOOGLE_DRIVE_FOLDER_ID = folder id from your My Drive folder URL")


if __name__ == "__main__":
    main()
