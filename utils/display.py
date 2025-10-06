"""Terminal display utilities using Rich."""

from typing import List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from models.quote import Quote
from utils.date_utils import format_date, format_relative_time


console = Console()


def display_quote_boxed(quote: Quote, show_id: bool = False) -> None:
    """
    Display a quote in a boxed format.

    Args:
        quote: Quote object to display
        show_id: Whether to show the quote ID
    """
    # Build quote text
    quote_text = Text()
    quote_text.append(f'"{quote.text}"', style="cyan")
    quote_text.append("\n\n")
    quote_text.append(f"— {quote.author}", style="dim white")

    # Create panel
    panel = Panel(
        quote_text,
        border_style="blue",
        padding=(1, 2),
    )

    console.print(panel)

    # Show metadata below box
    metadata = []
    if show_id:
        metadata.append(f"Quote #{quote.id}")
    if quote.categories:
        metadata.append(f"Categories: {', '.join(quote.categories)}")

    if metadata:
        console.print(" | ".join(metadata), style="dim")


def display_quote_minimal(quote: Quote) -> None:
    """
    Display a quote in minimal format (for --quiet mode).

    Args:
        quote: Quote object to display
    """
    console.print(f'"{quote.text}"', style="cyan", end="")
    console.print(f" — {quote.author}", style="dim white")


def display_quote_detailed(quote: Quote) -> None:
    """
    Display a quote with full details.

    Args:
        quote: Quote object to display
    """
    # Main quote text
    quote_text = Text()
    quote_text.append(f'"{quote.text}"', style="bold cyan")
    quote_text.append("\n\n")
    quote_text.append(f"— {quote.author}", style="dim white")

    # Details
    details = Text()

    if quote.source:
        details.append("\n\nSource: ", style="bold")
        details.append(quote.source)

    if quote.personal_note:
        details.append("\n\nYour note:\n", style="bold")
        details.append(quote.personal_note)

    if quote.categories:
        details.append("\n\nCategories: ", style="bold")
        details.append(", ".join(quote.categories), style="blue")

    details.append("\n\nAdded: ", style="bold")
    details.append(format_date(quote.date_added))

    if quote.last_shown:
        details.append("\nLast shown: ", style="bold")
        details.append(format_relative_time(quote.last_shown))

    details.append("\nTimes shown: ", style="bold")
    details.append(str(quote.times_shown))

    # Combine and display
    full_text = quote_text + details

    panel = Panel(
        full_text,
        border_style="blue",
        padding=(1, 2),
    )

    console.print(panel)


def display_quote_list(quotes: List[Quote], max_display: int = 10) -> None:
    """
    Display a list of quotes in summary format.

    Args:
        quotes: List of Quote objects
        max_display: Maximum number of quotes to display
    """
    if not quotes:
        console.print("No quotes found.", style="yellow")
        return

    total = len(quotes)
    display_quotes = quotes[:max_display]

    for i, quote in enumerate(display_quotes, 1):
        # Truncate long quotes
        text = quote.text
        if len(text) > 80:
            text = text[:77] + "..."

        # Format line - show quote ID instead of sequential number
        console.print(f"({quote.id[:8]}) ", style="dim yellow", end="")
        console.print(f'"{text}"', style="cyan")
        console.print(f"   — {quote.author}", style="dim white", end="")

        if quote.categories:
            console.print(f" | {', '.join(quote.categories)}", style="blue", end="")

        if quote.date_added:
            console.print(
                f" | Added: {format_relative_time(quote.date_added)}",
                style="dim",
            )
        else:
            console.print()

    if total > max_display:
        console.print(f"\nShowing {max_display} of {total} quotes", style="yellow")


def display_search_results(quotes: List[Quote], query: str) -> None:
    """
    Display search results.

    Args:
        quotes: List of matching Quote objects
        query: The search query
    """
    if not quotes:
        console.print(f"No quotes found matching '{query}'", style="yellow")
        return

    console.print(f"\nFound {len(quotes)} quote(s):\n", style="green bold")
    display_quote_list(quotes)


def display_success(message: str) -> None:
    """
    Display a success message.

    Args:
        message: Message to display
    """
    console.print(f"✅ {message}", style="bold green")


def display_error(message: str) -> None:
    """
    Display an error message.

    Args:
        message: Message to display
    """
    console.print(f"❌ {message}", style="bold red")


def display_warning(message: str) -> None:
    """
    Display a warning message.

    Args:
        message: Message to display
    """
    console.print(f"⚠️  {message}", style="bold yellow")


def display_info(message: str) -> None:
    """
    Display an info message.

    Args:
        message: Message to display
    """
    console.print(message, style="blue")


def display_similar_quote(
    existing_quote: Quote, new_text: str, similarity: float
) -> None:
    """
    Display a similar quote comparison.

    Args:
        existing_quote: The existing similar quote
        new_text: The new quote text
        similarity: Similarity score (0-100)
    """
    console.print(
        f"\n⚠️  Similar quote found ({similarity:.0f}% match):\n", style="yellow bold"
    )

    # Existing quote
    console.print("Existing quote:", style="bold")
    console.print(f'  "{existing_quote.text}"', style="cyan")
    console.print(f"  — {existing_quote.author}", style="dim white")
    console.print(f"  Added: {format_date(existing_quote.date_added)}", style="dim")

    console.print()

    # New quote
    console.print("Your new quote:", style="bold")
    console.print(f'  "{new_text}"', style="cyan")


def create_category_table(categories: List[str], selected: List[str]) -> Table:
    """
    Create a table for category selection.

    Args:
        categories: All available categories
        selected: Currently selected categories

    Returns:
        Rich Table object
    """
    table = Table(show_header=False, box=None)

    for category in categories:
        mark = "✓" if category in selected else " "
        table.add_row(f"[{mark}]", category)

    return table
