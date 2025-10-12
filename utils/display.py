"""Terminal display utilities using Rich - Theme-aware."""

from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from models.quote import Quote
from utils.date_utils import format_date, format_relative_time
from utils.themes import get_color, load_theme

console = Console()

# Load theme once at module import
THEME = load_theme()
_CURRENT_THEME_NAME = "auto"  # Track the current theme name


def set_theme(theme_name: str):
    """Change theme at runtime."""
    global THEME, _CURRENT_THEME_NAME
    THEME = load_theme(theme_name)
    _CURRENT_THEME_NAME = theme_name


def get_current_theme_name() -> str:
    """Get the name of the currently active theme."""
    return _CURRENT_THEME_NAME


def display_quote_boxed(quote: Quote, show_id: bool = False) -> None:
    """
    Display a quote in a boxed format.

    Args:
        quote: Quote object to display
        show_id: Whether to show the quote ID
    """
    # Build quote text
    quote_text = Text()
    quote_text.append(f'"{quote.text}"', style=get_color("primary"))
    quote_text.append("\n\n")
    quote_text.append(f"— {quote.author}", style=get_color("secondary"))

    # Create panel
    panel = Panel(
        quote_text,
        border_style=get_color("border"),
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
        console.print(" | ".join(metadata), style=get_color("secondary"))


def display_quote_minimal(quote: Quote) -> None:
    """
    Display a quote in minimal format (for --quiet mode).

    Args:
        quote: Quote object to display
    """
    console.print(f'"{quote.text}"', style=get_color("primary"), end="")
    console.print(f" — {quote.author}", style=get_color("secondary"))


def display_quote_detailed(quote: Quote) -> None:
    """
    Display a quote with full details.

    Args:
        quote: Quote object to display
    """
    # Main quote text
    quote_text = Text()
    quote_text.append(f'"{quote.text}"', style=f"bold {get_color('primary')}")
    quote_text.append("\n\n")
    quote_text.append(f"— {quote.author}", style=get_color("secondary"))

    # Details
    details = Text()

    if quote.source:
        details.append("\n\nSource: ", style=f"bold {get_color('secondary')}")
        details.append(quote.source)

    if quote.personal_note:
        details.append("\n\nYour note:\n", style=f"bold {get_color('secondary')}")
        details.append(quote.personal_note)

    if quote.categories:
        details.append("\n\nCategories: ", style=f"bold {get_color('secondary')}")
        details.append(", ".join(quote.categories), style=get_color("emphasis"))

    details.append("\n\nAdded: ", style=f"bold {get_color('secondary')}")
    details.append(format_date(quote.date_added))

    if quote.date_modified:
        details.append("\nLast modified: ", style=f"bold {get_color('secondary')}")
        details.append(format_date(quote.date_modified))

    if quote.last_shown:
        details.append("\nLast shown: ", style=f"bold {get_color('secondary')}")
        details.append(format_relative_time(quote.last_shown))

    details.append("\nTimes shown: ", style=f"bold {get_color('secondary')}")
    details.append(str(quote.times_shown))

    # Combine and display
    full_text = quote_text + details

    panel = Panel(
        full_text,
        border_style=get_color("border"),
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
        console.print("No quotes found.", style=get_color("warning"))
        return

    total = len(quotes)
    display_quotes = quotes[:max_display]

    for i, quote in enumerate(display_quotes, 1):
        # Truncate long quotes
        text = quote.text
        if len(text) > 80:
            text = text[:77] + "..."

        # Format line - show quote ID instead of sequential number
        console.print(f"({quote.id[:8]}) ", style=get_color("warning"), end="")
        console.print(f'"{text}"', style=get_color("primary"))
        console.print(f"   — {quote.author}", style=get_color("secondary"), end="")

        if quote.categories:
            console.print(
                f" | {', '.join(quote.categories)}", style=get_color("emphasis"), end=""
            )

        if quote.date_added:
            console.print(
                f" | Added: {format_relative_time(quote.date_added)}",
                style=get_color("dim"),
            )
        else:
            console.print()

    if total > max_display:
        console.print(
            f"\nShowing {max_display} of {total} quotes", style=get_color("warning")
        )


def display_search_results(quotes: List[Quote], query: str) -> None:
    """
    Display search results.

    Args:
        quotes: List of matching Quote objects
        query: The search query
    """
    if not quotes:
        console.print(f"No quotes found matching '{query}'", style=get_color("warning"))
        return

    console.print(
        f"\nFound {len(quotes)} quote(s):\n", style=f"{get_color('success')} bold"
    )
    display_quote_list(quotes)


def display_success(message: str) -> None:
    """
    Display a success message.

    Args:
        message: Message to display
    """
    console.print(f"✅ {message}", style=f"bold {get_color('success')}")


def display_error(message: str) -> None:
    """
    Display an error message.

    Args:
        message: Message to display
    """
    console.print(f"❌ {message}", style=f"bold {get_color('error')}")


def display_warning(message: str) -> None:
    """
    Display a warning message.

    Args:
        message: Message to display
    """
    console.print(f"⚠️  {message}", style=f"bold {get_color('warning')}")


def display_info(message: str) -> None:
    """
    Display an info message.

    Args:
        message: Message to display
    """
    console.print(message, style=get_color("border"))


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
        f"\n⚠️  Similar quote found ({similarity:.0f}% match):\n",
        style=f"{get_color('warning')} bold",
    )

    # Existing quote
    console.print("Existing quote:", style=f"bold {get_color('secondary')}")
    console.print(f'  "{existing_quote.text}"', style=get_color("primary"))
    console.print(f"  — {existing_quote.author}", style=get_color("secondary"))
    console.print(
        f"  Added: {format_date(existing_quote.date_added)}", style=get_color("dim")
    )

    console.print()

    # New quote
    console.print("Your new quote:", style=f"bold {get_color('secondary')}")
    console.print(f'  "{new_text}"', style=get_color("primary"))


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
