"""
Inbox Flow - Email Management System
"""

import streamlit as st
from config.settings import settings
from models.database import Database
from ui.email_list import render_email_list
from ui.prompt_config import render_prompt_config
from ui.email_chat import render_email_chat
from ui.draft_editor import render_draft_editor


# Page configuration
st.set_page_config(
    page_title="Inbox Flow",
    page_icon="📨",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def initialize_app():
    """Setup app state"""
    db = Database()
    
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.selected_email = None
        st.session_state.selected_draft = None
        st.session_state.chat_history = []
        st.session_state.emails_loaded = False
        st.session_state.active_tab = 0


def render_header():
    """Minimal header"""
    st.title("Inbox Flow")


def main():
    initialize_app()
    render_header()
    
    # Clean tabs
    tab_names = ["Inbox", "Assistant", "Drafts", "Settings"]
    tabs = st.tabs(tab_names)
    
    with tabs[0]:
        render_email_list()
    
    with tabs[1]:
        # Check config silently
        is_valid, _ = settings.validate()
        if not is_valid:
            st.info("Please configure your API key in Settings to enable the Assistant.")
        else:
            render_email_chat()
    
    with tabs[2]:
        render_draft_editor()

    with tabs[3]:
        render_prompt_config()
    
    # Minimal footer
    st.markdown("---")
    st.caption("v1.0.0 • Local Storage")


if __name__ == "__main__":
    main()
