"""Prompt Service - Manages prompt templates"""
import json
from typing import Dict, Optional
from models.database import PromptModel
from config.settings import settings


class PromptService:
    """Service for managing prompt templates"""
    
    @staticmethod
    def load_default_prompts():
        """Load default prompts from JSON file and store in database"""
        try:
            with open(settings.DEFAULT_PROMPTS_PATH, 'r') as f:
                prompts_data = json.load(f)
            
            for prompt_type, prompt_info in prompts_data.items():
                PromptModel.insert(
                    name=prompt_type,
                    content=prompt_info['content'],
                    is_active=True
                )
            
            return True, "Default prompts loaded successfully"
        except FileNotFoundError:
            return False, f"Default prompts file not found: {settings.DEFAULT_PROMPTS_PATH}"
        except Exception as e:
            return False, f"Error loading default prompts: {str(e)}"
    
    @staticmethod
    def get_prompt(prompt_type: str) -> Optional[str]:
        """
        Get prompt content by type
        
        Args:
            prompt_type: Type of prompt (categorization, action_item, auto_reply)
            
        Returns:
            Prompt content string or None
        """
        prompt = PromptModel.get_by_name(prompt_type)
        if prompt:
            return prompt['content']
        return None
    
    @staticmethod
    def update_prompt(prompt_type: str, new_content: str) -> bool:
        """
        Update prompt content
        
        Args:
            prompt_type: Type of prompt to update
            new_content: New prompt content
            
        Returns:
            True if successful, False otherwise
        """
        return PromptModel.update(prompt_type, new_content)
    
    @staticmethod
    def create_prompt(prompt_type: str, content: str) -> int:
        """
        Create a new prompt
        
        Args:
            prompt_type: Name/type of the prompt
            content: Prompt content
            
        Returns:
            ID of created prompt
        """
        return PromptModel.insert(prompt_type, content, is_active=True)
    
    @staticmethod
    def get_all_prompts() -> Dict[str, str]:
        """
        Get all prompts as a dictionary
        
        Returns:
            Dictionary mapping prompt names to content
        """
        prompts = PromptModel.get_all()
        return {p['name']: p['content'] for p in prompts if p['is_active']}
    
    @staticmethod
    def ensure_prompts_loaded():
        """Ensure default prompts are loaded in database"""
        existing_prompts = PromptModel.get_all()
        
        if not existing_prompts:
            # No prompts in database, load defaults
            return PromptService.load_default_prompts()
        
        return True, "Prompts already loaded"


# Initialize prompts on import
prompt_service = PromptService()
