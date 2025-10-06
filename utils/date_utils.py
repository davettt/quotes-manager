"""Date and time utilities."""

from datetime import datetime, timedelta
from typing import Optional


def parse_iso_datetime(iso_string: Optional[str]) -> Optional[datetime]:
    """
    Parse ISO format datetime string.

    Args:
        iso_string: ISO format datetime string

    Returns:
        datetime object or None if parsing fails
    """
    if not iso_string:
        return None

    try:
        # Handle both with and without microseconds
        if "." in iso_string:
            return datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        else:
            return datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    except Exception:
        return None


def is_today(iso_string: Optional[str]) -> bool:
    """
    Check if a datetime string is from today.

    Args:
        iso_string: ISO format datetime string

    Returns:
        True if the datetime is from today, False otherwise
    """
    if not iso_string:
        return False

    dt = parse_iso_datetime(iso_string)
    if not dt:
        return False

    # Compare dates (ignoring time)
    today = datetime.utcnow().date()
    return dt.date() == today


def days_ago(iso_string: Optional[str]) -> Optional[int]:
    """
    Calculate how many days ago a datetime was.

    Args:
        iso_string: ISO format datetime string

    Returns:
        Number of days ago, or None if parsing fails
    """
    if not iso_string:
        return None

    dt = parse_iso_datetime(iso_string)
    if not dt:
        return None

    now = datetime.utcnow()
    delta = now - dt
    return delta.days


def format_relative_time(iso_string: Optional[str]) -> str:
    """
    Format a datetime as relative time (e.g., "2 days ago", "just now").

    Args:
        iso_string: ISO format datetime string

    Returns:
        Human-readable relative time string
    """
    if not iso_string:
        return "never"

    dt = parse_iso_datetime(iso_string)
    if not dt:
        return "unknown"

    now = datetime.utcnow()
    delta = now - dt

    if delta.days == 0:
        if delta.seconds < 60:
            return "just now"
        elif delta.seconds < 3600:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif delta.days == 1:
        return "yesterday"
    elif delta.days < 7:
        return f"{delta.days} days ago"
    elif delta.days < 30:
        weeks = delta.days // 7
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif delta.days < 365:
        months = delta.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = delta.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"


def format_date(iso_string: Optional[str]) -> str:
    """
    Format a datetime as a readable date (e.g., "March 15, 2024").

    Args:
        iso_string: ISO format datetime string

    Returns:
        Formatted date string
    """
    if not iso_string:
        return "unknown"

    dt = parse_iso_datetime(iso_string)
    if not dt:
        return "unknown"

    return dt.strftime("%B %d, %Y")


def is_within_days(iso_string: Optional[str], days: int) -> bool:
    """
    Check if a datetime is within the last N days.

    Args:
        iso_string: ISO format datetime string
        days: Number of days to check

    Returns:
        True if datetime is within the last N days, False otherwise
    """
    if not iso_string:
        return False

    dt = parse_iso_datetime(iso_string)
    if not dt:
        return False

    now = datetime.utcnow()
    cutoff = now - timedelta(days=days)
    return dt >= cutoff
