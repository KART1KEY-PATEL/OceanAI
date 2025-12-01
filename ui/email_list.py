"""Email List UI Component"""
import streamlit as st
from services.email_service import email_service
from services.processing_engine import processing_engine
from utils.helpers import format_timestamp, get_category_emoji, truncate_text

def render_email_list():
    """Render the email list view"""
    
    # Sidebar controls
    with st.sidebar:
        st.header("Controls")
        
        if st.button("🔄 Refresh Inbox", use_container_width=True):
            with st.spinner("Syncing..."):
                email_service.load_mock_inbox()
                st.session_state.emails_loaded = True
                st.rerun()
        
        if st.button("⚡ Process Emails", type="primary", use_container_width=True):
            with st.spinner("Processing..."):
                processing_engine.process_inbox()
                st.rerun()
        
        st.divider()
        
        # Filters
        st.subheader("Filters")
        category_filter = st.selectbox(
            "Category",
            ["All", "Important", "To-Do", "Newsletter", "Spam", "Uncategorized"]
        )

    # Get emails
    filter_val = None if category_filter == "All" else category_filter
    emails = email_service.get_all_emails(filter_val)
    
    if not emails:
        st.info("No emails found. Click 'Refresh Inbox' to load data.")
        return
    
    # Display email count
    st.caption(f"{len(emails)} emails")
    
    # Create two columns: email list and detail view
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Email list
        for email in emails:
            with st.container():
                # Email subject as button
                label = f"{get_category_emoji(email['category'])} **{truncate_text(email['subject'], 35)}**"
                if st.button(
                    label,
                    key=f"email_{email['id']}",
                    use_container_width=True
                ):
                    st.session_state.selected_email = email
                    st.rerun()
                
                # Metadata
                st.caption(f"{email['sender']} • {format_timestamp(email['timestamp'])}")
                st.divider()
    
    with col2:
        if st.session_state.selected_email:
            render_email_detail(st.session_state.selected_email)
        else:
            st.info("Select an email to view details")


def render_email_detail(email):
    """Render detailed view of a selected email"""
    
    # Header with actions
    c1, c2 = st.columns([3, 1])
    with c1:
        st.subheader(email['subject'])
    with c2:
        if st.button("✕ Close"):
            st.session_state.selected_email = None
            st.rerun()
    
    # Metadata
    st.caption(f"From: {email['sender']} • {format_timestamp(email['timestamp'])}")
    
    # Category badge
    st.caption(f"Category: {get_category_emoji(email['category'])} {email['category']}")
    
    st.divider()
    
    # Body
    st.markdown(email['body'])
    
    st.divider()
    
    # Actions
    ac1, ac2 = st.columns(2)
    with ac1:
        if st.button("📝 Draft Reply", use_container_width=True):
            with st.spinner("Drafting..."):
                draft = processing_engine.generate_draft(email['id'])
                if draft:
                    st.session_state.selected_draft = draft['id']
                    st.session_state.active_tab = 2 # Switch to Drafts tab
                    st.rerun()
    
    with ac2:
        if st.button("🔄 Reprocess", use_container_width=True):
            processing_engine.process_email(email['id'])
            st.rerun()
