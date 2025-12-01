"""Email Agent Chat UI Component"""
import streamlit as st
from services.llm_service import llm_service
from services.email_service import email_service
from services.processing_engine import processing_engine


def render_email_chat():
    """Render the chat interface"""
    
    # Initialize chat history if empty
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "How can I help you with your inbox today?"}
        ]
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Check if there's a context email
    context_email_id = st.session_state.get('chat_email_context')
    
    if context_email_id:
        email = email_service.get_email_by_id(context_email_id)
        if email:
            with st.container(border=True):
                st.write("📧 **Context Email:**")
                st.write(f"**Subject:** {email['subject']}")
                st.write(f"**From:** {email['sender']}")
                
                if st.button("❌ Clear Context"):
                    st.session_state.chat_email_context = None
                    st.rerun()
    
    # Quick action buttons
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Summarize Selected", use_container_width=True):
            if context_email_id:
                add_user_message("Summarize this email")
                handle_chat_query("Summarize this email", context_email_id)
            else:
                st.warning("⚠️ Please select an email first")
    
    with col2:
        if st.button("📋 Show All Tasks", use_container_width=True):
            add_user_message("What are all my tasks?")
            handle_tasks_query()
    
    with col3:
        if st.button("🔴 Show Urgent Emails", use_container_width=True):
            add_user_message("Show me urgent emails")
            handle_urgent_query()
    
    st.divider()
    
    # Chat messages display
    chat_container = st.container(height=400)
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                with st.chat_message("user"):
                    st.write(message['content'])
            else:
                with st.chat_message("assistant"):
                    st.write(message['content'])
    
    # Chat input
    user_input = st.chat_input("Type your question here...")
    
    if user_input:
        add_user_message(user_input)
        handle_chat_query(user_input, context_email_id)
        st.rerun()


def add_user_message(content: str):
    """Add a user message to chat history"""
    st.session_state.chat_history.append({
        'role': 'user',
        'content': content
    })


def add_assistant_message(content: str):
    """Add an assistant message to chat history"""
    st.session_state.chat_history.append({
        'role': 'assistant',
        'content': content
    })


def handle_chat_query(query: str, email_id: str = None):
    """Handle a chat query from the user"""
    
    query_lower = query.lower()
    
    # Check for specific query types
    if "task" in query_lower or "to-do" in query_lower or "action" in query_lower:
        handle_tasks_query()
    elif "urgent" in query_lower or "important" in query_lower:
        handle_urgent_query()
    elif "draft" in query_lower or "reply" in query_lower:
        handle_draft_query(email_id)
    elif email_id:
        # General query about a specific email
        handle_email_query(query, email_id)
    else:
        # General query about inbox
        handle_general_query(query)


def handle_tasks_query():
    """Handle query about tasks"""
    action_items = email_service.get_all_action_items(status="pending")
    
    if not action_items:
        add_assistant_message("You have no pending tasks! 🎉")
        return
    
    response = f"You have **{len(action_items)} pending tasks:**\n\n"
    
    for item in action_items:
        email = email_service.get_email_by_id(item['email_id'])
        email_subject = email['subject'] if email else "Unknown"
        
        response += f"• **{item['task']}**\n"
        response += f"  📅 Deadline: {item['deadline']}\n"
        response += f"  📧 From email: {email_subject}\n\n"
    
    add_assistant_message(response)


def handle_urgent_query():
    """Handle query about urgent/important emails"""
    important_emails = email_service.get_all_emails(category_filter="Important")
    
    if not important_emails:
        add_assistant_message("No urgent emails at the moment! ✅")
        return
    
    response = f"You have **{len(important_emails)} important emails:**\n\n"
    
    for email in important_emails[:10]:  # Limit to 10
        response += f"📧 **{email['subject']}**\n"
        response += f"   From: {email['sender']}\n\n"
    
    add_assistant_message(response)


def handle_draft_query(email_id: str = None):
    """Handle query about drafting a reply"""
    if not email_id:
        add_assistant_message("Please select an email first to generate a reply draft.")
        return
    
    result = processing_engine.generate_draft_for_email(email_id)
    
    if result['success']:
        response = f"I've generated a reply draft:\n\n"
        response += f"**Subject:** {result['subject']}\n\n"
        response += f"**Body:**\n{result['body']}"
        
        add_assistant_message(response)
    else:
        add_assistant_message(f"❌ Error generating draft: {result['message']}")


def handle_email_query(query: str, email_id: str):
    """Handle a query about a specific email"""
    email = email_service.get_email_by_id(email_id)
    
    if not email:
        add_assistant_message("❌ Email not found.")
        return
    
    # Build context
    context = f"Email from {email['sender']}\n"
    context += f"Subject: {email['subject']}\n\n"
    context += f"Body:\n{email['body']}"
    
    # Query LLM
    response = llm_service.handle_chat_query(query, context)
    
    add_assistant_message(response)


def handle_general_query(query: str):
    """Handle a general query about the inbox"""
    
    # Get some context about the inbox
    all_emails = email_service.get_all_emails()
    stats = email_service.get_category_stats()
    
    context = f"Inbox summary:\n"
    context += f"Total emails: {len(all_emails)}\n"
    context += f"Categories: {stats}\n\n"
    
    # Add summary of recent emails
    context += "Recent emails:\n"
    for email in all_emails[:5]:
        context += f"- {email['subject']} from {email['sender']}\n"
    
    # Query LLM
    response = llm_service.handle_chat_query(query, context)
    
    add_assistant_message(response)
