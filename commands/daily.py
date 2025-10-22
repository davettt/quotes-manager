"""Daily quote command implementation."""

import random
import sys
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from models.quote import Quote
from utils.display import display_warning, set_theme
from utils.storage import (
    add_to_display_history,
    get_display_history,
    get_last_daily_display,
    load_quotes,
    save_quotes,
)

console = Console()


def get_daily_quote(force: bool = False) -> Optional[Quote]:
    """
    Get the quote for today.

    Args:
        force: If True, get a new quote even if one was already shown today

    Returns:
        Quote object or None if no quotes available
    """
    quotes = load_quotes()

    if not quotes:
        return None

    # Check if we've already shown a quote today
    last_display = get_last_daily_display()

    if last_display and not force:
        try:
            last_display_date = datetime.fromisoformat(last_display).date()
            today = datetime.now().date()  # Use local time, not UTC

            if last_display_date == today:
                # Already shown today, find and return that quote
                display_history = get_display_history()
                if display_history:
                    last_quote_id = display_history[-1]["quote_id"]
                    for quote in quotes:
                        if quote.id == last_quote_id:
                            return quote
        except Exception:
            pass

    # Get display history for last 21 days
    display_history = get_display_history()
    recently_shown_ids = {entry["quote_id"] for entry in display_history}

    # Filter out recently shown quotes
    available_quotes = [q for q in quotes if q.id not in recently_shown_ids]

    # If all quotes have been shown recently, use all quotes
    if not available_quotes:
        available_quotes = quotes

    # Select random quote
    quote = random.choice(available_quotes)

    # Mark as shown and update display history
    quote.mark_shown()
    add_to_display_history(quote.id)

    # Save updated quote
    for i, q in enumerate(quotes):
        if q.id == quote.id:
            quotes[i] = quote
            break
    save_quotes(quotes)

    return quote


def show_daily(
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Minimal display for shell startup"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Show new quote even if one shown today"
    ),
    theme: str = typer.Option(
        None, "--theme", help="Color theme: auto, dark, light, high-contrast, none"
    ),
):
    """
    Display today's quote of the day.

    Shows a different quote each day, with no repeats within 21 days.
    Use --quiet for a minimal display suitable for shell startup.
    """
    # Handle Typer boolean flag parsing
    # Typer converts False to string 'False' for boolean options
    # Check if it's a string and convert it, or if it's None, check sys.argv
    if isinstance(quiet, str):
        quiet = (
            quiet.lower() in ("true", "1", "yes")
            or "--quiet" in sys.argv
            or "-q" in sys.argv
        )
    elif quiet is None:
        quiet = "--quiet" in sys.argv or "-q" in sys.argv

    if isinstance(force, str):
        force = (
            force.lower() in ("true", "1", "yes")
            or "--force" in sys.argv
            or "-f" in sys.argv
        )
    elif force is None:
        force = "--force" in sys.argv or "-f" in sys.argv

    # Set theme if provided
    if theme:
        set_theme(theme)

    quote = get_daily_quote(force=force)

    if not quote:
        if not quiet:
            display_warning("No quotes found. Add your first quote with 'quotes add'")
        return

    if quiet:
        # Minimal display for shell startup
        console.print()
        console.print(f'  "{quote.text}"', style="cyan")
        console.print(f"  — {quote.author}", style="dim white")
        console.print()
    else:
        # Full display with details
        console.print()

        # Create quote panel
        quote_text = Text()
        quote_text.append(f'"{quote.text}"\n\n', style="cyan")
        quote_text.append(f"— {quote.author}", style="dim white")

        panel = Panel(
            quote_text,
            title="[bold cyan]✨ Quote of the Day ✨[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )
        console.print(panel)

        # Show metadata
        console.print()
        if quote.categories:
            console.print(
                f"  [dim]Categories:[/dim] {', '.join(quote.categories)}",
                style="blue",
            )
        if quote.source:
            console.print(f"  [dim]Source:[/dim] {quote.source}")

        console.print(
            f"  [dim]Quote #{quote.id[:8]} | Shown {quote.times_shown} time{'s' if quote.times_shown != 1 else ''}[/dim]"
        )
        console.print()
