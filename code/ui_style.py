"""Global Streamlit appearance: larger type, no sidebar chrome."""

import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
<style>
    html, body, .stApp, [data-baseweb] {
        font-size: 1.125rem;
    }
    h1 { font-size: 2.05rem !important; line-height: 1.25 !important; }
    h2 { font-size: 1.55rem !important; }
    h3 { font-size: 1.35rem !important; }
    .stMarkdown, .stChatMessage { font-size: 1.08rem; }
    [data-testid="stChatInput"] textarea { font-size: 1.08rem !important; }
    section[data-testid="stSidebar"],
    [data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNav"] ul {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        overflow: hidden !important;
        pointer-events: none !important;
    }
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        display: none !important;
        visibility: hidden !important;
    }
    button[kind="header"] { display: none !important; }

    .heart-section-guidance {
        background: linear-gradient(135deg, #eef4fc 0%, #e8f0fa 100%);
        border: 1px solid #b8cfe8;
        border-left: 5px solid #1d4ed8;
        border-radius: 10px;
        padding: 1.1rem 1.35rem 1.15rem;
        margin: 0 0 1.5rem 0;
        box-shadow: 0 2px 8px rgba(29, 78, 216, 0.1);
    }
    .heart-section-guidance__title {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #1e3a8a !important;
        margin: 0 0 0.75rem 0 !important;
        letter-spacing: 0.01em;
    }
    .heart-section-guidance__list {
        margin: 0 !important;
        padding-left: 1.35rem !important;
        color: #1e293b;
        line-height: 1.55 !important;
    }
    .heart-section-guidance__list li {
        margin-bottom: 0.55rem !important;
    }
    .heart-section-guidance__list li:last-child {
        margin-bottom: 0 !important;
    }

    .heart-chat-area-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 0.25rem 0 1rem 0;
        padding: 0.65rem 0 0.75rem;
        border-top: 2px solid #e2e8f0;
    }
    .heart-chat-area-header__label {
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #64748b;
        white-space: nowrap;
    }
    .heart-chat-area-header__line {
        flex: 1;
        height: 1px;
        background: #e2e8f0;
    }
    @media (prefers-color-scheme: dark) {
        .heart-section-guidance {
            background: linear-gradient(135deg, #1e293b 0%, #172033 100%);
            border-color: #334155;
            border-left-color: #60a5fa;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25);
        }
        .heart-section-guidance__title { color: #93c5fd !important; }
        .heart-section-guidance__list { color: #e2e8f0; }
        .heart-chat-area-header { border-top-color: #334155; }
        .heart-chat-area-header__label { color: #94a3b8; }
        .heart-chat-area-header__line { background: #334155; }
    }
</style>
        """,
        unsafe_allow_html=True,
    )
