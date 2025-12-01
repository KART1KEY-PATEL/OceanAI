"""Prompt Configuration UI Component"""
import streamlit as st
from services.prompt_service import prompt_service
from services.processing_engine import processing_engine


def render_prompt_config():
    """Render the prompt configuration view"""
    
    st.header("Settings")
    st.caption("Customize how the assistant processes your emails.")
    
    # Ensure prompts are loaded
    success, message = prompt_service.ensure_prompts_loaded()
    
    if not success:
        st.error(f"❌ {message}")
        if st.button("📥 Load Default Prompts"):
            success, msg = prompt_service.load_default_prompts()
            if success:
                st.success(f"✅ {msg}")
                st.rerun()
            else:
                st.error(f"❌ {msg}")
        return
    
    # Get all prompts
    prompts = prompt_service.get_all_prompts()
    
    # Create tabs for each prompt type
    tab1, tab2, tab3 = st.tabs([
        "📊 Categorization",
        "📋 Action Items",
        "✉️ Auto-Reply"
    ])
    
    with tab1:
        render_prompt_editor(
            "categorization",
            "Email Categorization Prompt",
            prompts.get("categorization", ""),
            "This prompt determines how emails are categorized into Important, Newsletter, Spam, or To-Do."
        )
    
    with tab2:
        render_prompt_editor(
            "action_item",
            "Action Item Extraction Prompt",
            prompts.get("action_item", ""),
            "This prompt extracts tasks and deadlines from emails."
        )
    
    with tab3:
        render_prompt_editor(
            "auto_reply",
            "Auto-Reply Draft Prompt",
            prompts.get("auto_reply", ""),
            "This prompt generates professional reply drafts for emails."
        )


def render_prompt_editor(prompt_type: str, title: str, current_content: str, description: str):
    """Render editor for a specific prompt type"""
    
    st.subheader(title)
    st.caption(description)
    
    # Text area for editing prompt
    edited_content = st.text_area(
        "Prompt Content",
        value=current_content,
        height=300,
        key=f"prompt_{prompt_type}",
        help="Edit the prompt template. Use {sender}, {subject}, and {body} as placeholders."
    )
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Changes", key=f"save_{prompt_type}", use_container_width=True):
            if edited_content.strip():
                success = prompt_service.update_prompt(prompt_type, edited_content)
                if success:
                    st.success("✅ Prompt saved successfully!")
                else:
                    # Try creating if update failed
                    prompt_service.create_prompt(prompt_type, edited_content)
                    st.success("✅ Prompt created successfully!")
            else:
                st.error("❌ Prompt content cannot be empty")
    
    with col2:
        if st.button("🔄 Reset to Default", key=f"reset_{prompt_type}", use_container_width=True):
            # Reload default prompts
            prompt_service.load_default_prompts()
            st.success("✅ Reset to default prompt")
            st.rerun()
    
    with col3:
        if st.button("🧪 Test Prompt", key=f"test_{prompt_type}", use_container_width=True):
            st.session_state[f"show_test_{prompt_type}"] = True
    
    # Test panel (expandable)
    if st.session_state.get(f"show_test_{prompt_type}", False):
        st.divider()
        st.subheader("🧪 Test Prompt")
        
        # Sample email input
        col1, col2 = st.columns(2)
        
        with col1:
            test_sender = st.text_input("Sender", "test@example.com", key=f"test_sender_{prompt_type}")
            test_subject = st.text_input("Subject", "Test Email", key=f"test_subject_{prompt_type}")
        
        with col2:
            test_body = st.text_area("Body", "This is a test email body.", height=100, key=f"test_body_{prompt_type}")
        
        if st.button("▶️ Run Test", key=f"run_test_{prompt_type}"):
            sample_email = {
                'sender': test_sender,
                'subject': test_subject,
                'body': test_body
            }
            
            with st.spinner("Testing prompt..."):
                # First save the edited prompt
                prompt_service.update_prompt(prompt_type, edited_content)
                
                # Test it
                result = processing_engine.test_prompt(prompt_type, sample_email)
                
                st.subheader("Test Result:")
                with st.container(border=True):
                    st.write(result)
        
        if st.button("❌ Close Test Panel", key=f"close_test_{prompt_type}"):
            st.session_state[f"show_test_{prompt_type}"] = False
            st.rerun()
    
    st.divider()
    
    # Show placeholders info
    with st.expander("ℹ️ Available Placeholders"):
        st.markdown("""
        Use these placeholders in your prompt:
        - `{sender}` - Email sender address
        - `{subject}` - Email subject line
        - `{body}` - Email body content
        
        Example:
        ```
        Analyze this email:
        From: {sender}
        Subject: {subject}
        {body}
        ```
        """)
