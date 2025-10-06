"""Edit quote command implementation."""

import typer
from rich.console import Console
from rich.prompt import Prompt

from utils.storage import load_quotes, update_quote, get_quote_by_id
from utils.display import display_success, display_error, display_quote_detailed

console = Console()


def edit_quote(
    quote_id: str = typer.Argument(..., help="Quote ID to edit (full or partial)")
):
    """
    Edit an existing quote.

    You can edit the text, author, source, personal note, or categories.

    Example:
        quotes edit a1b2c3d4
        quotes edit a1b2     # Partial ID works too
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

    # Show current quote
    console.print("\n[bold cyan]Current quote:[/bold cyan]\n")
    display_quote_detailed(quote)

    # Ask what to edit
    console.print("\n[bold cyan]What would you like to edit?[/bold cyan]")
    console.print("[T] Text")
    console.print("[A] Author")
    console.print("[S] Source")
    console.print("[N] Personal note")
    console.print("[C] Categories")
    console.print("[X] Cancel")

    choice = Prompt.ask("\nChoice", choices=["t", "a", "s", "n", "c", "x"], default="x")

    if choice == "x":
        console.print("\nEdit cancelled")
        return

    # Edit based on choice
    if choice == "t":
        console.print(f"\n[dim]Current text:[/dim] {quote.text}")
        new_text = Prompt.ask("New text (or press Enter to keep current)")
        if new_text.strip():
            quote.text = new_text.strip()

    elif choice == "a":
        console.print(f"\n[dim]Current author:[/dim] {quote.author}")
        new_author = Prompt.ask(
            "New author (or press Enter to keep current)", default=""
        )
        if new_author.strip():
            quote.author = new_author.strip()

    elif choice == "s":
        console.print(
            f"\n[dim]Current source:[/dim] {quote.source if quote.source else '(none)'}"
        )
        new_source = Prompt.ask(
            "New source (or press Enter to keep current)", default=""
        )
        if new_source.strip() or new_source == "":
            quote.source = new_source.strip()

    elif choice == "n":
        console.print(
            f"\n[dim]Current note:[/dim] {quote.personal_note if quote.personal_note else '(none)'}"
        )
        new_note = Prompt.ask("New note (or press Enter to keep current)", default="")
        if new_note.strip() or new_note == "":
            quote.personal_note = new_note.strip()

    elif choice == "c":
        current_cats = ", ".join(quote.categories) if quote.categories else "(none)"
        console.print(f"\n[dim]Current categories:[/dim] {current_cats}")
        new_categories = Prompt.ask(
            "New categories (comma-separated, or press Enter to keep current)",
            default="",
        )
        if new_categories.strip():
            quote.categories = [
                c.strip() for c in new_categories.split(",") if c.strip()
            ]

    # Save changes
    if update_quote(quote):
        console.print()
        display_success("Quote updated!")

        # Show updated quote
        console.print()
        display_quote_detailed(quote)
    else:
        display_error("Failed to update quote")
        raise typer.Exit(1)
