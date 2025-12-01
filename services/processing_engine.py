"""Processing Engine - Orchestrates email processing with LLM"""
from typing import List, Dict, Any, Callable
from services.llm_service import llm_service
from services.prompt_service import prompt_service
from services.email_service import email_service


class ProcessingEngine:
    """Engine for processing emails through the LLM pipeline"""
    
    def __init__(self):
        self.llm = llm_service
        self.prompt_svc = prompt_service
        self.email_svc = email_service
    
    def process_inbox(self, progress_callback: Callable[[int, int, str], None] = None) -> Dict[str, Any]:
        """
        Process all emails in the inbox
        
        Args:
            progress_callback: Optional callback function(current, total, status)
            
        Returns:
            Dictionary with processing results
        """
        # Get all uncategorized emails
        all_emails = self.email_svc.get_all_emails()
        uncategorized = [e for e in all_emails if e['category'] == 'Uncategorized']
        
        total = len(uncategorized)
        processed = 0
        errors = []
        
        # Get prompts
        cat_prompt = self.prompt_svc.get_prompt('categorization')
        action_prompt = self.prompt_svc.get_prompt('action_item')
        
        if not cat_prompt or not action_prompt:
            return {
                'success': False,
                'message': 'Prompts not loaded. Please load default prompts first.',
                'processed': 0,
                'total': total,
                'errors': ['Missing prompts']
            }
        
        for email in uncategorized:
            processed += 1
            
            if progress_callback:
                progress_callback(processed, total, f"Processing: {email['subject'][:50]}...")
            
            try:
                # Step 1: Categorize email
                category = self.llm.categorize_email(email, cat_prompt)
                self.email_svc.update_category(email['id'], category)
                
                # Step 2: Extract action items (only for To-Do emails)
                if category == "To-Do":
                    action_items = self.llm.extract_action_items(email, action_prompt)
                    for item in action_items:
                        self.email_svc.add_action_item(
                            email['id'],
                            item.get('task', ''),
                            item.get('deadline', 'Not specified')
                        )
            except Exception as e:
                errors.append(f"Error processing email {email['id']}: {str(e)}")
        
        return {
            'success': True,
            'message': f'Processed {processed} emails',
            'processed': processed,
            'total': total,
            'errors': errors
        }
    
    def process_single_email(self, email_id: str) -> Dict[str, Any]:
        """
        Process a single email
        
        Args:
            email_id: ID of email to process
            
        Returns:
            Dictionary with processing results
        """
        email = self.email_svc.get_email_by_id(email_id)
        
        if not email:
            return {
                'success': False,
                'message': f'Email not found: {email_id}'
            }
        
        # Get prompts
        cat_prompt = self.prompt_svc.get_prompt('categorization')
        action_prompt = self.prompt_svc.get_prompt('action_item')
        
        if not cat_prompt or not action_prompt:
            return {
                'success': False,
                'message': 'Prompts not loaded'
            }
        
        try:
            # Categorize
            category = self.llm.categorize_email(email, cat_prompt)
            self.email_svc.update_category(email_id, category)
            
            # Extract action items if To-Do
            action_items = []
            if category == "To-Do":
                items = self.llm.extract_action_items(email, action_prompt)
                for item in items:
                    item_id = self.email_svc.add_action_item(
                        email_id,
                        item.get('task', ''),
                        item.get('deadline', 'Not specified')
                    )
                    action_items.append(item)
            
            return {
                'success': True,
                'message': 'Email processed successfully',
                'category': category,
                'action_items': action_items
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error processing email: {str(e)}'
            }
    
    def generate_draft_for_email(self, email_id: str, tone: str = "professional") -> Dict[str, Any]:
        """
        Generate a reply draft for an email
        
        Args:
            email_id: ID of email to reply to
            tone: Reply tone
            
        Returns:
            Dictionary with draft content
        """
        email = self.email_svc.get_email_by_id(email_id)
        
        if not email:
            return {
                'success': False,
                'message': f'Email not found: {email_id}'
            }
        
        # Get auto-reply prompt
        reply_prompt = self.prompt_svc.get_prompt('auto_reply')
        
        if not reply_prompt:
            return {
                'success': False,
                'message': 'Auto-reply prompt not loaded'
            }
        
        try:
            # Generate draft
            draft_body = self.llm.generate_reply_draft(email, reply_prompt, tone)
            draft_subject = f"Re: {email['subject']}"
            
            return {
                'success': True,
                'subject': draft_subject,
                'body': draft_body,
                'original_email_id': email_id
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error generating draft: {str(e)}'
            }
    
    def test_prompt(self, prompt_type: str, sample_email: Dict[str, Any]) -> str:
        """
        Test a prompt with a sample email
        
        Args:
            prompt_type: Type of prompt to test
            sample_email: Sample email data
            
        Returns:
            LLM response
        """
        prompt = self.prompt_svc.get_prompt(prompt_type)
        
        if not prompt:
            return "Error: Prompt not found"
        
        try:
            if prompt_type == "categorization":
                return self.llm.categorize_email(sample_email, prompt)
            elif prompt_type == "action_item":
                items = self.llm.extract_action_items(sample_email, prompt)
                return str(items)
            elif prompt_type == "auto_reply":
                return self.llm.generate_reply_draft(sample_email, prompt)
            else:
                return "Unknown prompt type"
        except Exception as e:
            return f"Error testing prompt: {str(e)}"


    def process_email(self, email_id: str) -> Dict[str, Any]:
        """Wrapper for process_single_email to match UI calls"""
        return self.process_single_email(email_id)

    def generate_draft(self, email_id: str) -> Dict[str, Any]:
        """Wrapper for generate_draft_for_email to match UI calls"""
        result = self.generate_draft_for_email(email_id)
        if result['success']:
            # Return just the draft dict if successful, or None
            from models.database import DraftModel
            draft_id = DraftModel.insert(
                subject=result['subject'],
                body=result['body'],
                email_id=email_id
            )
            return DraftModel.get_by_id(draft_id)
        return None

# Create singleton instance
processing_engine = ProcessingEngine()
