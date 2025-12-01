#!/usr/bin/env python3
"""
Setup script for Email Productivity Agent
Run this script to initialize the database and load default data
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import Database
from services.prompt_service import PromptService


def main():
    """Initialize the application"""
    print("🚀 Email Productivity Agent - Setup")
    print("=" * 50)
    
    # Initialize database
    print("\n📊 Initializing database...")
    db = Database()
    print("✅ Database initialized successfully!")
    
    # Load default prompts
    print("\n📝 Loading default prompts...")
    prompt_service = PromptService()
    success, message = prompt_service.load_default_prompts()
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"⚠️  {message}")
    
    print("\n" + "=" * 50)
    print("✨ Setup complete!")
    print("\n📋 Next steps:")
    print("1. Copy .env.example to .env")
    print("2. Add your API key to .env")
    print("3. Run: streamlit run app.py")
    print("\n💡 See README.md for detailed instructions")


if __name__ == "__main__":
    main()
