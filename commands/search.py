"""Search quotes command implementation."""

import typer
from rich.console import Console

from utils.storage import load_quotes
from utils.display import display_search_results, display_warning

console = Console()


def search_quotes(
    query: str = typer.Argument(..., help="Search query (keywords to find in quotes)"),
    case_sensitive: bool = typer.Option(
        False, "--case-sensitive", "-c", help="Case-sensitive search"
    ),
):
    """
    Search quotes by keyword.

    Searches in quote text, author, source, personal note, and categories.

    Examples:
        quotes search "passion"
        quotes search "steve jobs"
        quotes search "work life" --case-sensitive
    """
    quotes = load_quotes()

    if not quotes:
        display_warning("No quotes found. Add your first quote with 'quotes add'")
        return

    # Prepare search query
    search_query = query if case_sensitive else query.lower()

    # Search through all quote fields
    matching_quotes = []

    for quote in quotes:
        # Build searchable text from all fields
        searchable_fields = [
            quote.text,
            quote.author,
            quote.source,
            quote.personal_note,
            " ".join(quote.categories),
        ]

        searchable_text = " ".join(searchable_fields)

        if not case_sensitive:
            searchable_text = searchable_text.lower()

        # Check if query matches
        if search_query in searchable_text:
            matching_quotes.append(quote)

    # Display results
    display_search_results(matching_quotes, query)

    if matching_quotes:
        console.print("\n[dim]Use 'quotes view <id>' to see full quote details[/dim]")
