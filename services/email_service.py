"""Email Service - Manages email operations"""
import json
from typing import List, Dict, Optional, Any
from models.database import EmailModel, ActionItemModel
from config.settings import settings


class EmailService:
    """Service for managing emails"""
    
    @staticmethod
    def load_mock_inbox() -> tuple[bool, str, int]:
        """
        Load emails from mock inbox JSON file
        
        Returns:
            Tuple of (success, message, count)
        """
        try:
            with open(settings.MOCK_INBOX_PATH, 'r') as f:
                emails = json.load(f)
            
            loaded_count = 0
            for email_data in emails:
                success = EmailModel.insert(email_data)
                if success:
                    loaded_count += 1
            
            return True, f"Successfully loaded {loaded_count} emails", loaded_count
        except FileNotFoundError:
            return False, f"Mock inbox file not found: {settings.MOCK_INBOX_PATH}", 0
        except Exception as e:
            return False, f"Error loading mock inbox: {str(e)}", 0
    
    @staticmethod
    def get_all_emails(category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all emails, optionally filtered by category
        
        Args:
            category_filter: Filter by this category (or None for all)
            
        Returns:
            List of email dictionaries
        """
        return EmailModel.get_all(category_filter)
    
    @staticmethod
    def get_email_by_id(email_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single email by ID
        
        Args:
            email_id: Email ID
            
        Returns:
            Email dictionary or None
        """
        return EmailModel.get_by_id(email_id)
    
    @staticmethod
    def update_category(email_id: str, new_category: str) -> bool:
        """
        Update email category
        
        Args:
            email_id: Email ID
            new_category: New category name
            
        Returns:
            True if successful
        """
        return EmailModel.update_category(email_id, new_category)
    
    @staticmethod
    def get_category_stats() -> Dict[str, int]:
        """
        Get statistics about email categories
        
        Returns:
            Dictionary mapping categories to counts
        """
        return EmailModel.get_count_by_category()
    
    @staticmethod
    def add_action_item(email_id: str, task: str, deadline: str = "Not specified") -> int:
        """
        Add an action item for an email
        
        Args:
            email_id: Email ID
            task: Task description
            deadline: Deadline (optional)
            
        Returns:
            ID of created action item
        """
        return ActionItemModel.insert(email_id, task, deadline)
    
    @staticmethod
    def get_action_items(email_id: str) -> List[Dict[str, Any]]:
        """
        Get all action items for an email
        
        Args:
            email_id: Email ID
            
        Returns:
            List of action item dictionaries
        """
        return ActionItemModel.get_by_email(email_id)
    
    @staticmethod
    def get_all_action_items(status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all action items across all emails
        
        Args:
            status: Filter by status (optional)
            
        Returns:
            List of action item dictionaries
        """
        return ActionItemModel.get_all(status)
    
    @staticmethod
    def update_action_item_status(item_id: int, status: str) -> bool:
        """
        Update action item status
        
        Args:
            item_id: Action item ID
            status: New status (pending/completed)
            
        Returns:
            True if successful
        """
        return ActionItemModel.update_status(item_id, status)
    
    @staticmethod
    def search_emails(query: str, in_field: str = "all") -> List[Dict[str, Any]]:
        """
        Search emails by query
        
        Args:
            query: Search query
            in_field: Field to search in (subject, body, sender, all)
            
        Returns:
            List of matching emails
        """
        all_emails = EmailModel.get_all()
        query_lower = query.lower()
        
        results = []
        for email in all_emails:
            if in_field == "all":
                searchable_text = f"{email['subject']} {email['body']} {email['sender']}".lower()
            else:
                searchable_text = email.get(in_field, "").lower()
            
            if query_lower in searchable_text:
                results.append(email)
        
        return results


# Create singleton instance
email_service = EmailService()
