"""JSON storage utilities for quotes and configuration."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from models.config import Config
from models.quote import Quote

# Storage paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "local_data" / "personal_data"
QUOTES_FILE = DATA_DIR / "quotes.json"
CONFIG_FILE = DATA_DIR / "config.json"


def ensure_data_dir() -> None:
    """Ensure data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_quotes() -> List[Quote]:
    """
    Load all quotes from storage.

    Returns:
        List of Quote objects
    """
    ensure_data_dir()

    if not QUOTES_FILE.exists():
        return []

    try:
        with open(QUOTES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        quotes_data = data.get("quotes", [])
        return [Quote.from_dict(q) for q in quotes_data]
    except json.JSONDecodeError:
        # Return empty list if file is corrupted
        return []
    except Exception:
        return []


def save_quotes(quotes: List[Quote]) -> None:
    """
    Save quotes to storage.

    Args:
        quotes: List of Quote objects to save
    """
    ensure_data_dir()

    # Load existing data structure or create new one
    if QUOTES_FILE.exists():
        try:
            with open(QUOTES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    else:
        data = {}

    # Update quotes
    data["quotes"] = [q.to_dict() for q in quotes]

    # Ensure other fields exist
    if "version" not in data:
        data["version"] = "1.0"
    if "display_history" not in data:
        data["display_history"] = []
    if "last_daily_display" not in data:
        data["last_daily_display"] = None
    if "stats" not in data:
        data["stats"] = {
            "total_quotes": len(quotes),
            "quotes_added_this_month": 0,
            "most_shown_quote_id": None,
        }
    else:
        data["stats"]["total_quotes"] = len(quotes)

    # Write to file
    with open(QUOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_display_history() -> List[Dict]:
    """
    Get the display history.

    Returns:
        List of display history entries
    """
    ensure_data_dir()

    if not QUOTES_FILE.exists():
        return []

    try:
        with open(QUOTES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("display_history", [])
    except Exception:
        return []


def add_to_display_history(quote_id: str) -> None:
    """
    Add quote to display history.

    Args:
        quote_id: ID of the quote that was displayed
    """
    ensure_data_dir()

    # Load existing data
    if QUOTES_FILE.exists():
        try:
            with open(QUOTES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    else:
        data = {"quotes": [], "display_history": []}

    # Add to history
    if "display_history" not in data:
        data["display_history"] = []

    data["display_history"].append(
        {"quote_id": quote_id, "shown_at": datetime.utcnow().isoformat()}
    )

    # Keep only last 21 days of history (approximate with 21 entries)
    if len(data["display_history"]) > 21:
        data["display_history"] = data["display_history"][-21:]

    # Update last daily display
    data["last_daily_display"] = datetime.utcnow().isoformat()

    # Write back
    with open(QUOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_last_daily_display() -> Optional[str]:
    """
    Get the timestamp of the last daily display.

    Returns:
        ISO format timestamp or None
    """
    ensure_data_dir()

    if not QUOTES_FILE.exists():
        return None

    try:
        with open(QUOTES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("last_daily_display")
    except Exception:
        return None


def load_config() -> Config:
    """
    Load configuration from storage.

    Returns:
        Config object
    """
    ensure_data_dir()

    if not CONFIG_FILE.exists():
        # Return default config
        return Config()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Config.from_dict(data)
    except Exception:
        return Config()


def save_config(config: Config) -> None:
    """
    Save configuration to storage.

    Args:
        config: Config object to save
    """
    ensure_data_dir()

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)


def get_quote_by_id(quote_id: str) -> Optional[Quote]:
    """
    Get a quote by its ID.

    Args:
        quote_id: The quote ID to search for

    Returns:
        Quote object or None if not found
    """
    quotes = load_quotes()
    for quote in quotes:
        if quote.id == quote_id:
            return quote
    return None


def update_quote(updated_quote: Quote) -> bool:
    """
    Update an existing quote.

    Args:
        updated_quote: Quote object with updated data

    Returns:
        True if quote was found and updated, False otherwise
    """
    quotes = load_quotes()
    for i, quote in enumerate(quotes):
        if quote.id == updated_quote.id:
            quotes[i] = updated_quote
            save_quotes(quotes)
            return True
    return False


def delete_quote(quote_id: str) -> bool:
    """
    Delete a quote by its ID.

    Args:
        quote_id: The quote ID to delete

    Returns:
        True if quote was found and deleted, False otherwise
    """
    quotes = load_quotes()
    original_count = len(quotes)
    quotes = [q for q in quotes if q.id != quote_id]

    if len(quotes) < original_count:
        save_quotes(quotes)
        return True
    return False
