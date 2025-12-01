"""Draft Editor UI Component"""
import streamlit as st
from models.database import DraftModel
from services.email_service import email_service
from utils.helpers import format_timestamp


def render_draft_editor():
    """Render the draft management view"""
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("Drafts")
    with col2:
        if st.button("＋ New Draft"):
            st.session_state.selected_draft = None
            st.session_state.editing_draft = 'new' # Ensure new draft mode is activated
            st.rerun()
    
    # Get all drafts
    drafts = DraftModel.get_all()
    
    if not drafts:
        st.info("📭 No drafts yet. Generate a reply from the Inbox Manager or use the Email Agent to create drafts.")
        
        # Option to create a new draft manually
        if st.button("➕ Create New Draft"):
            st.session_state.editing_draft = 'new'
            st.rerun()
        
        return
    
    # Display drafts count
    st.caption(f"You have {len(drafts)} draft(s)")
    
    # Create two columns: draft list and editor
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Drafts")
        
        # New draft button
        if st.button("➕ New Draft", use_container_width=True):
            st.session_state.editing_draft = 'new'
            st.rerun()
        
        st.divider()
        
        # Draft list
        for draft in drafts:
            with st.container():
                # Draft preview
                if st.button(
                    f"**{draft['subject'][:40]}...**" if len(draft['subject']) > 40 else f"**{draft['subject']}**",
                    key=f"draft_{draft['id']}",
                    use_container_width=True
                ):
                    st.session_state.selected_draft = draft['id']
                    st.session_state.editing_draft = None
                    st.rerun()
                
                # Draft metadata
                if draft['email_id']:
                    st.caption("↩️ Reply")
                else:
                    st.caption("📧 New email")
                
                st.caption(f"📅 {format_timestamp(draft['created_at'])}")
                
                st.divider()
    
    with col2:
        # Check if we're editing a new draft
        if st.session_state.get('editing_draft') == 'new':
            render_new_draft_editor()
        elif st.session_state.get('selected_draft'):
            render_draft_detail(st.session_state.selected_draft)
        else:
            st.info("👈 Select a draft to view and edit")


def render_new_draft_editor():
    """Render editor for creating a new draft"""
    
    st.subheader("✏️ New Draft")
    
    # Input fields
    subject = st.text_input("Subject", key="new_draft_subject")
    body = st.text_area("Body", height=400, key="new_draft_body")
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Draft", use_container_width=True, type="primary"):
            if subject.strip() and body.strip():
                draft_id = DraftModel.insert(
                    subject=subject,
                    body=body
                )
                
                st.success("✅ Draft saved!")
                st.session_state.selected_draft = draft_id
                st.session_state.editing_draft = None
                st.rerun()
            else:
                st.error("❌ Subject and body cannot be empty")
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.editing_draft = None
            st.rerun()


def render_draft_detail(draft_id: int):
    """Render detailed view and editor for a draft"""
    
    draft = DraftModel.get_by_id(draft_id)
    
    if not draft:
        st.error("Draft not found")
        return
    
    st.subheader("📄 Draft Details")
    
    # Link to original email if it's a reply
    if draft['email_id']:
        original_email = email_service.get_email_by_id(draft['email_id'])
        if original_email:
            with st.container(border=True):
                st.write("↩️ **In Reply To:**")
                st.write(f"**Subject:** {original_email['subject']}")
                st.write(f"**From:** {original_email['sender']}")
    
    st.divider()
    
    # Edit mode toggle
    if st.session_state.get(f'edit_mode_{draft_id}', False):
        # Edit mode
        st.write("✏️ **Editing Mode**")
        
        new_subject = st.text_input("Subject", value=draft['subject'], key=f"edit_subject_{draft_id}")
        new_body = st.text_area("Body", value=draft['body'], height=400, key=f"edit_body_{draft_id}")
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save Changes", key=f"save_{draft_id}", use_container_width=True):
                if new_subject.strip() and new_body.strip():
                    success = DraftModel.update(draft_id, new_subject, new_body)
                    
                    if success:
                        st.success("✅ Draft updated!")
                        st.session_state[f'edit_mode_{draft_id}'] = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to update draft")
                else:
                    st.error("❌ Subject and body cannot be empty")
        
        with col2:
            if st.button("❌ Cancel", key=f"cancel_{draft_id}", use_container_width=True):
                st.session_state[f'edit_mode_{draft_id}'] = False
                st.rerun()
    
    else:
        # View mode
        with st.container(border=True):
            st.write(f"**Subject:** {draft['subject']}")
            st.divider()
            st.write(draft['body'])
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✏️ Edit Draft", key=f"edit_{draft_id}", use_container_width=True):
                st.session_state[f'edit_mode_{draft_id}'] = True
                st.rerun()
        
        with col2:
            if st.button("🗑️ Delete Draft", key=f"delete_{draft_id}", use_container_width=True):
                if st.session_state.get(f'confirm_delete_{draft_id}', False):
                    success = DraftModel.delete(draft_id)
                    
                    if success:
                        st.success("✅ Draft deleted!")
                        st.session_state.selected_draft = None
                        st.session_state[f'confirm_delete_{draft_id}'] = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete draft")
                else:
                    st.session_state[f'confirm_delete_{draft_id}'] = True
                    st.warning("⚠️ Click again to confirm deletion")
        
        # Safety notice
        st.divider()
        st.info("🔒 **Safety Note:** Drafts are saved locally and will never be sent automatically. You must manually send them via your email client.")
