"""LLM Service - Handles all LLM API interactions"""
import json
from typing import Dict, Any, Optional
from config.settings import settings


class LLMService:
    """Service for interacting with various LLM providers"""
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.api_key = settings.get_api_key()
        self.model_name = settings.MODEL_NAME
        self.temperature = settings.TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
        
        # Initialize the appropriate client
        self._init_client()
    
    def _init_client(self):
        """Initialize the LLM client based on provider"""
        try:
            if self.provider == "openai":
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            elif self.provider == "anthropic":
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            elif self.provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                
                # Handle deprecated model name
                model = self.model_name
                if model in ['gemini-pro', 'gemini-1.5-flash']:
                    model = 'gemini-2.0-flash'
                    
                self.client = genai.GenerativeModel(model or 'gemini-2.0-flash')
            elif self.provider == "grok":
                import openai
                # Grok uses OpenAI-compatible API
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.x.ai/v1"
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        except Exception as e:
            print(f"Error initializing LLM client: {e}")
            self.client = None
    
    def query_llm(self, prompt: str, context: str = "", temperature: Optional[float] = None) -> str:
        """
        Send a query to the LLM
        
        Args:
            prompt: The prompt template
            context: Context to include in the query
            temperature: Override default temperature
            
        Returns:
            LLM response as string
        """
        if not self.client:
            return "Error: LLM client not initialized. Please check your API key configuration."
        
        # Combine prompt and context
        full_prompt = f"{prompt}\n\n{context}" if context else prompt
        temp = temperature if temperature is not None else self.temperature
        
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful email assistant."},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=temp,
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content.strip()
            
            elif self.provider == "grok":
                # Grok uses OpenAI-compatible API
                response = self.client.chat.completions.create(
                    model=self.model_name or "grok-beta",
                    messages=[
                        {"role": "system", "content": "You are a helpful email assistant."},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=temp,
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content.strip()
            
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model_name or "claude-3-sonnet-20240229",
                    max_tokens=self.max_tokens,
                    temperature=temp,
                    messages=[
                        {"role": "user", "content": full_prompt}
                    ]
                )
                return response.content[0].text.strip()
            
            elif self.provider == "gemini":
                response = self.client.generate_content(
                    full_prompt,
                    generation_config={
                        'temperature': temp,
                        'max_output_tokens': self.max_tokens,
                    }
                )
                return response.text.strip()
            
        except Exception as e:
            error_msg = f"Error calling LLM API: {str(e)}"
            print(error_msg)
            return f"Error: {str(e)}"
    
    def categorize_email(self, email_data: Dict[str, Any], prompt_template: str) -> str:
        """
        Categorize an email using the LLM
        
        Args:
            email_data: Email dictionary with sender, subject, body
            prompt_template: Categorization prompt template
            
        Returns:
            Category name (Important, Newsletter, Spam, To-Do, or Uncategorized)
        """
        # Format the prompt with email data
        formatted_prompt = prompt_template.format(
            sender=email_data.get('sender', 'Unknown'),
            subject=email_data.get('subject', ''),
            body=email_data.get('body', '')
        )
        
        response = self.query_llm(formatted_prompt, temperature=0.3)
        
        # Clean up the response and validate
        category = response.strip()
        valid_categories = ["Important", "Newsletter", "Spam", "To-Do"]
        
        # Check if response contains a valid category
        for valid_cat in valid_categories:
            if valid_cat.lower() in category.lower():
                return valid_cat
        
        return "Uncategorized"
    
    def extract_action_items(self, email_data: Dict[str, Any], prompt_template: str) -> list:
        """
        Extract action items from an email
        
        Args:
            email_data: Email dictionary with sender, subject, body
            prompt_template: Action item extraction prompt template
            
        Returns:
            List of action items, each with 'task' and 'deadline'
        """
        # Format the prompt with email data
        formatted_prompt = prompt_template.format(
            sender=email_data.get('sender', 'Unknown'),
            subject=email_data.get('subject', ''),
            body=email_data.get('body', '')
        )
        
        response = self.query_llm(formatted_prompt, temperature=0.2)
        
        # Try to parse JSON response
        try:
            # Clean up response (remove markdown code blocks if present)
            cleaned_response = response.strip()
            if cleaned_response.startswith('```'):
                # Extract JSON from markdown code block
                lines = cleaned_response.split('\n')
                cleaned_response = '\n'.join(lines[1:-1]) if len(lines) > 2 else cleaned_response
            
            action_items = json.loads(cleaned_response)
            
            # Validate structure
            if isinstance(action_items, list):
                return action_items
            else:
                return []
        except json.JSONDecodeError:
            print(f"Failed to parse action items JSON: {response}")
            return []
    
    def generate_reply_draft(self, email_data: Dict[str, Any], prompt_template: str, user_tone: str = "professional") -> str:
        """
        Generate a reply draft for an email
        
        Args:
            email_data: Email dictionary with sender, subject, body
            prompt_template: Auto-reply prompt template
            user_tone: Tone preference for the reply
            
        Returns:
            Generated reply body
        """
        # Format the prompt with email data
        formatted_prompt = prompt_template.format(
            sender=email_data.get('sender', 'Unknown'),
            subject=email_data.get('subject', ''),
            body=email_data.get('body', '')
        )
        
        if user_tone != "professional":
            formatted_prompt += f"\n\nTone: {user_tone}"
        
        response = self.query_llm(formatted_prompt, temperature=0.7)
        
        return response.strip()
    
    def handle_chat_query(self, query: str, context: str = "") -> str:
        """
        Handle a chat query from the user
        
        Args:
            query: User's question
            context: Context (e.g., selected email content)
            
        Returns:
            AI response
        """
        if context:
            full_prompt = f"Context:\n{context}\n\nUser Question: {query}\n\nProvide a helpful response."
        else:
            full_prompt = query
        
        response = self.query_llm(full_prompt, temperature=0.7)
        
        return response


# Create a singleton instance
llm_service = LLMService()
