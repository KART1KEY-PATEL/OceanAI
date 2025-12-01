"""Utility functions"""

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max_length characters"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def format_timestamp(timestamp: str) -> str:
    """Format ISO timestamp to readable format"""
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y %I:%M %p")
    except:
        return timestamp


def get_category_color(category: str) -> str:
    """Get color for category badge"""
    colors = {
        "Important": "red",
        "To-Do": "orange",
        "Newsletter": "blue",
        "Spam": "gray",
        "Uncategorized": "lightgray"
    }
    return colors.get(category, "lightgray")


def get_category_emoji(category: str) -> str:
    """Get emoji for category"""
    emojis = {
        "Important": "🔴",
        "To-Do": "📋",
        "Newsletter": "📰",
        "Spam": "🗑️",
        "Uncategorized": "❓"
    }
    return emojis.get(category, "📧")
