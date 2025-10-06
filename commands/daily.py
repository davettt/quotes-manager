"""Daily quote command implementation."""

import random
from datetime import datetime
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from models.quote import Quote
from utils.storage import (
    load_quotes,
    save_quotes,
    get_display_history,
    add_to_display_history,
    get_last_daily_display,
)
from utils.display import display_warning

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
        last_display_date = datetime.fromisoformat(last_display).date()
        today = datetime.utcnow().date()

        if last_display_date == today:
            # Already shown today, find and return that quote
            display_history = get_display_history()
            if display_history:
                last_quote_id = display_history[-1]["quote_id"]
                for quote in quotes:
                    if quote.id == last_quote_id:
                        return quote

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
):
    """
    Display today's quote of the day.

    Shows a different quote each day, with no repeats within 21 days.
    Use --quiet for a minimal display suitable for shell startup.
    """
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
