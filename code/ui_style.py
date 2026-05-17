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
</style>
        """,
        unsafe_allow_html=True,
    )
