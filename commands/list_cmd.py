"""List quotes command implementation."""

import typer
from rich.console import Console

from utils.display import display_quote_list, display_warning, set_theme
from utils.storage import load_quotes

console = Console()


def list_quotes(
    category: str = typer.Option(None, "--category", "-c", help="Filter by category"),
    author: str = typer.Option(None, "--author", "-a", help="Filter by author"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum quotes to display"),
    all: bool = typer.Option(False, "--all", help="Show all quotes"),
    theme: str = typer.Option(
        None, "--theme", help="Color theme: auto, dark, light, high-contrast, none"
    ),
):
    """
    List all quotes with optional filtering.

    Examples:
        quotes list                    # Show 10 most recent quotes
        quotes list --all              # Show all quotes
        quotes list --category work    # Show quotes in 'work' category
        quotes list --author "Steve Jobs"  # Show quotes by Steve Jobs
    """
    # Set theme if provided
    if theme:
        set_theme(theme)

    quotes = load_quotes()

    if not quotes:
        display_warning("No quotes found. Add your first quote with 'quotes add'")
        return

    # Apply filters
    filtered_quotes = quotes

    if category:
        filtered_quotes = [
            q
            for q in filtered_quotes
            if category.lower() in [c.lower() for c in q.categories]
        ]
        if not filtered_quotes:
            display_warning(f"No quotes found in category '{category}'")
            return

    if author:
        filtered_quotes = [
            q for q in filtered_quotes if author.lower() in q.author.lower()
        ]
        if not filtered_quotes:
            display_warning(f"No quotes found by author '{author}'")
            return

    # Sort by date added (newest first)
    filtered_quotes.sort(key=lambda q: q.date_added, reverse=True)

    # Display results
    if category:
        console.print(
            f"\n[bold cyan]{len(filtered_quotes)} quote(s) in '{category}':[/bold cyan]\n"
        )
    elif author:
        console.print(
            f"\n[bold cyan]{len(filtered_quotes)} quote(s) by {author}:[/bold cyan]\n"
        )
    else:
        console.print(
            f"\n[bold cyan]All quotes ({len(filtered_quotes)} total):[/bold cyan]\n"
        )

    # Display with limit unless --all flag is set
    max_display = len(filtered_quotes) if all else limit
    display_quote_list(filtered_quotes, max_display=max_display)

    # Show tip if results were limited
    if not all and len(filtered_quotes) > limit:
        console.print(
            f"\n[dim]Use --all to see all {len(filtered_quotes)} quotes[/dim]"
        )
