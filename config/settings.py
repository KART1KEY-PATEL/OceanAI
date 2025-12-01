import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application configuration settings"""
    
    # LLM Provider Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GROK_API_KEY = os.getenv("GROK_API_KEY", "")
    
    # Model Configuration
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.0-flash")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "500"))
    
    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", "data/email_agent.db")
    
    # Mock Data Paths
    MOCK_INBOX_PATH = "data/mock_inbox.json"
    DEFAULT_PROMPTS_PATH = "data/default_prompts.json"
    
    @classmethod
    def validate(cls):
        """Validate that required API key is present"""
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            return False, "OpenAI API key is required. Please set OPENAI_API_KEY in .env file"
        elif cls.LLM_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
            return False, "Anthropic API key is required. Please set ANTHROPIC_API_KEY in .env file"
        elif cls.LLM_PROVIDER == "gemini" and not cls.GOOGLE_API_KEY:
            return False, "Google API key is required. Please set GOOGLE_API_KEY in .env file"
        elif cls.LLM_PROVIDER == "grok" and not cls.GROK_API_KEY:
            return False, "Grok API key is required. Please set GROK_API_KEY in .env file"
        return True, "Configuration is valid"
    
    @classmethod
    def get_api_key(cls):
        """Get the API key for the configured provider"""
        if cls.LLM_PROVIDER == "openai":
            return cls.OPENAI_API_KEY
        elif cls.LLM_PROVIDER == "anthropic":
            return cls.ANTHROPIC_API_KEY
        elif cls.LLM_PROVIDER == "gemini":
            return cls.GOOGLE_API_KEY
        elif cls.LLM_PROVIDER == "grok":
            return cls.GROK_API_KEY
        return ""


settings = Settings()
