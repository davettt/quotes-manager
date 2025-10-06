"""Delete quote command implementation."""

import typer
from rich.console import Console
from rich.prompt import Confirm

from utils.storage import (
    load_quotes,
    delete_quote as storage_delete_quote,
    get_quote_by_id,
)
from utils.display import display_success, display_error, display_warning

console = Console()


def delete_quote_command(
    quote_id: str = typer.Argument(..., help="Quote ID to delete (full or partial)"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """
    Delete a quote from your collection.

    This action cannot be undone!

    Example:
        quotes delete a1b2c3d4
        quotes delete a1b2     # Partial ID works too
        quotes delete a1b2 --force  # Skip confirmation
    """
    # Find quote by full or partial ID
    quotes = load_quotes()

    # Try exact match first
    quote = get_quote_by_id(quote_id)

    # If not found, try partial match
    if not quote:
        matching_quotes = [q for q in quotes if q.id.startswith(quote_id)]

        if len(matching_quotes) == 0:
            display_error(f"No quote found with ID '{quote_id}'")
            console.print(
                "\n[dim]Use 'quotes list' to see all quotes and their IDs[/dim]"
            )
            raise typer.Exit(1)
        elif len(matching_quotes) > 1:
            display_error(
                f"Multiple quotes match '{quote_id}'. Please be more specific:"
            )
            for q in matching_quotes:
                console.print(f'  - {q.id[:8]}: "{q.text[:50]}..."')
            raise typer.Exit(1)
        else:
            quote = matching_quotes[0]

    # Show quote to be deleted
    console.print()
    display_warning("Are you sure you want to delete this quote?")
    console.print()
    console.print(f'  "{quote.text}"', style="cyan")
    console.print(f"  — {quote.author}", style="dim white")
    console.print()
    console.print("[red]This cannot be undone![/red]")
    console.print()

    # Ask for confirmation unless --force flag is used
    if not force:
        confirmed = Confirm.ask("Delete this quote?", default=False)
        if not confirmed:
            console.print("\nDeletion cancelled")
            return

    # Delete the quote
    if storage_delete_quote(quote.id):
        display_success("Quote deleted")
    else:
        display_error("Failed to delete quote")
        raise typer.Exit(1)
