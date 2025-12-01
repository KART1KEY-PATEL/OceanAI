# Inbox Flow

A streamlined email management workspace designed for efficiency.

## Overview

Inbox Flow helps you manage your emails with intelligent categorization, action item extraction, and drafting assistance. It runs locally on your machine, ensuring your data stays private.

## Features

- **Smart Inbox**: Automatically categorizes emails (Important, To-Do, Newsletter, Spam).
- **Action Items**: Extracts tasks and deadlines from your emails.
- **Drafting**: Generates reply drafts based on context.
- **Local Storage**: All data is stored locally in a SQLite database.

## Quick Start

1.  **Setup Environment**
    ```bash
    cp .env.example .env
    # Add your Google API key to .env (LLM_PROVIDER=gemini)
    ```

2.  **Run Application**
    ```bash
    source venv/bin/activate
    streamlit run app.py
    ```

## Technology

Built with Python, Streamlit, and SQLite.
# OceanAI
