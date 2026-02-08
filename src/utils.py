"""Utility functions for E-Paper Calendar Dashboard."""

import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

def format_event_time(event: dict) -> str:
    """Format event start time as human-readable string.
    
    Args:
        event: Event dictionary from Google Calendar API
        
    Returns:
        Formatted time string
    """
    start = event.get("start", {})
    
    if "dateTime" in start:
        dt = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    elif "date" in start:
        return "All day"
    
    return "Unknown"

def format_event_title(event: dict, max_length: int = 50) -> str:
    """Get event title with length limit.
    
    Args:
        event: Event dictionary
        max_length: Maximum title length
        
    Returns:
        Title string
    """
    title = event.get("summary", "Untitled")
    if len(title) > max_length:
        title = title[:max_length - 3] + "..."
    return title

def is_all_day_event(event: dict) -> bool:
    """Check if event is all-day.
    
    Args:
        event: Event dictionary
        
    Returns:
        True if all-day event
    """
    return "date" in event.get("start", {})

def get_event_date(event: dict) -> Optional[str]:
    """Get event date as ISO string (YYYY-MM-DD).
    
    Args:
        event: Event dictionary
        
    Returns:
        Date string or None
    """
    start = event.get("start", {})
    
    if "dateTime" in start:
        return start["dateTime"][:10]
    elif "date" in start:
        return start["date"]
    
    return None

def log_error(context: str, error: Exception):
    """Log error with context.
    
    Args:
        context: Error context description
        error: Exception object
    """
    logger.error(f"{context}: {type(error).__name__}: {error}")

def log_info(message: str):
    """Log info message."""
    logger.info(message)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Utils module loaded")
