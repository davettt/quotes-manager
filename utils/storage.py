"""JSON storage utilities for quotes and configuration."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from models.config import Config
from models.quote import Quote

# Storage paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "local_data" / "personal_data"
QUOTES_FILE = DATA_DIR / "quotes.json"
QUOTES_BACKUP_FILE = DATA_DIR / "quotes.json.bak"
CONFIG_FILE = DATA_DIR / "config.json"


def ensure_data_dir() -> None:
    """Ensure data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _atomic_write(path: Path, data: dict) -> None:
    """Write *data* to *path* atomically via a sibling .tmp file.

    Writes to <path>.tmp first, then calls Path.replace() which maps to
    rename(2) on POSIX — atomic on the same filesystem.  This means a
    crash or cloud-sync interruption mid-write can never leave a partial
    or merged file at the real path.
    """
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.replace(path)


def _backup_quotes() -> None:
    """Copy quotes.json → quotes.json.bak, but only when the source is valid JSON.

    Validates before copying so the backup always holds the last known-good
    state — a corrupt primary file never overwrites a healthy backup.
    """
    if not QUOTES_FILE.exists():
        return
    try:
        with open(QUOTES_FILE, "r", encoding="utf-8") as f:
            json.load(f)
        shutil.copy2(QUOTES_FILE, QUOTES_BACKUP_FILE)
    except Exception:
        pass  # Never overwrite a good backup with a corrupt file


def _load_raw() -> dict:
    """Read and return the raw data dict from quotes.json.

    Returns an empty dict on any read/parse failure so callers can apply
    defaults without duplicating error handling.
    """
    if not QUOTES_FILE.exists():
        return {}
    try:
        with open(QUOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _recover_from_backup(original_error: Exception) -> List[Quote]:
    """Attempt to restore quotes from quotes.json.bak after a load failure.

    Prints a warning to stderr so the user is informed regardless of which
    command triggered the load.  Returns recovered quotes, or [] if the
    backup is also unreadable.
    """
    from rich.console import Console

    console = Console(stderr=True)

    if QUOTES_BACKUP_FILE.exists():
        try:
            with open(QUOTES_BACKUP_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            quotes = [Quote.from_dict(q) for q in data.get("quotes", [])]
            console.print(
                f"\n[yellow]Warning: quotes.json was corrupted "
                f"({original_error}). "
                f"Recovered {len(quotes)} quotes from backup.[/yellow]\n"
            )
            return quotes
        except Exception:
            pass

    console.print(
        f"\n[red]Error: quotes.json is corrupted and no valid backup exists.\n"
        f"Data file: {QUOTES_FILE}[/red]\n"
    )
    return []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_quotes() -> List[Quote]:
    """Load all quotes from storage.

    On JSON parse failure, automatically attempts recovery from the backup
    file and warns the user.  Returns [] only when both files are unreadable.
    """
    ensure_data_dir()

    if not QUOTES_FILE.exists():
        return []

    try:
        with open(QUOTES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Quote.from_dict(q) for q in data.get("quotes", [])]
    except Exception as exc:
        return _recover_from_backup(exc)


def save_quotes(quotes: List[Quote]) -> None:
    """Save quotes to storage atomically, backing up the previous state first."""
    ensure_data_dir()

    data = _load_raw()
    data["quotes"] = [q.to_dict() for q in quotes]
    data.setdefault("version", "1.0")
    data.setdefault("display_history", [])
    data.setdefault("last_daily_display", None)
    if "stats" not in data:
        data["stats"] = {
            "total_quotes": len(quotes),
            "quotes_added_this_month": 0,
            "most_shown_quote_id": None,
        }
    else:
        data["stats"]["total_quotes"] = len(quotes)

    _backup_quotes()
    _atomic_write(QUOTES_FILE, data)


def get_display_history() -> List[Dict]:
    """Return the display history list."""
    ensure_data_dir()
    return _load_raw().get("display_history", [])


def add_to_display_history(quote_id: str) -> None:
    """Record that *quote_id* was displayed today."""
    ensure_data_dir()

    data = _load_raw() or {"quotes": [], "display_history": []}
    data.setdefault("display_history", [])

    data["display_history"].append(
        {"quote_id": quote_id, "shown_at": datetime.now().isoformat()}
    )

    # Keep only the most recent 21 entries
    if len(data["display_history"]) > 21:
        data["display_history"] = data["display_history"][-21:]

    data["last_daily_display"] = datetime.now().isoformat()

    _backup_quotes()
    _atomic_write(QUOTES_FILE, data)


def get_last_daily_display() -> Optional[str]:
    """Return the ISO timestamp of the last daily display, or None."""
    ensure_data_dir()
    return _load_raw().get("last_daily_display")


def load_config() -> Config:
    """Load configuration from storage."""
    ensure_data_dir()

    if not CONFIG_FILE.exists():
        return Config()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Config.from_dict(data)
    except Exception:
        return Config()


def save_config(config: Config) -> None:
    """Save configuration atomically."""
    ensure_data_dir()
    _atomic_write(CONFIG_FILE, config.to_dict())


def get_quote_by_id(quote_id: str) -> Optional[Quote]:
    """Return the quote with the given ID, or None."""
    for quote in load_quotes():
        if quote.id == quote_id:
            return quote
    return None


def update_quote(updated_quote: Quote) -> bool:
    """Update an existing quote. Returns True if found and saved."""
    quotes = load_quotes()
    for i, quote in enumerate(quotes):
        if quote.id == updated_quote.id:
            updated_quote.date_modified = datetime.utcnow().isoformat()
            quotes[i] = updated_quote
            save_quotes(quotes)
            return True
    return False


def delete_quote(quote_id: str) -> bool:
    """Delete a quote by ID. Returns True if found and deleted."""
    quotes = load_quotes()
    original_count = len(quotes)
    quotes = [q for q in quotes if q.id != quote_id]
    if len(quotes) < original_count:
        save_quotes(quotes)
        return True
    return False
