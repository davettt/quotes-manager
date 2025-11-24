"""Edit quote command implementation."""

import os

# Import the multiline input function from add.py
import sys

import typer
from rich.console import Console

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from commands.add import _read_multiline_input, _sanitize_text
from utils.display import (
    display_error,
    display_quote_detailed,
    display_success,
    set_theme,
)
from utils.input_helpers import prompt_choice, prompt_input
from utils.storage import get_quote_by_id, load_quotes, update_quote

console = Console()


def edit_quote(
    quote_id: str = typer.Argument(..., help="Quote ID to edit (full or partial)"),
    theme: str = typer.Option(
        None, "--theme", help="Color theme: auto, dark, light, high-contrast, none"
    ),
):
    """
    Edit an existing quote.

    You can edit the text, author, source, personal note, or categories.

    Example:
        quotes edit a1b2c3d4
        quotes edit a1b2     # Partial ID works too
    """
    # Set theme if provided
    if theme:
        set_theme(theme)

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

    choice = prompt_choice(
        "\nChoice: ", choices=["t", "a", "s", "n", "c", "x"], default="x"
    )

    if choice == "x":
        console.print("\nEdit cancelled")
        return

    # Edit based on choice
    if choice == "t":
        console.print("\n[dim]Current text:[/dim]")
        console.print(f"{quote.text}\n")
        console.print("[cyan]Enter new text (use arrow keys to navigate):[/cyan]")
        new_text = _read_multiline_input("New quote text", sentinel="END")
        if new_text.strip():
            quote.text = _sanitize_text(new_text).strip()

    elif choice == "a":
        console.print(f"\n[dim]Current author:[/dim] {quote.author}")
        new_author = prompt_input(
            "New author (or press Enter to keep current): ", default=""
        )
        if new_author.strip():
            quote.author = _sanitize_text(new_author).strip()

    elif choice == "s":
        console.print(
            f"\n[dim]Current source:[/dim] {quote.source if quote.source else '(none)'}"
        )
        new_source = prompt_input(
            "New source (or press Enter to keep current): ", default=""
        )
        if new_source.strip() or new_source == "":
            quote.source = _sanitize_text(new_source).strip()

    elif choice == "n":
        console.print(
            f"\n[dim]Current note:[/dim] {quote.personal_note if quote.personal_note else '(none)'}"
        )
        new_note = prompt_input(
            "New note (or press Enter to keep current): ", default=""
        )
        if new_note.strip() or new_note == "":
            quote.personal_note = _sanitize_text(new_note).strip()

    elif choice == "c":
        current_cats = ", ".join(quote.categories) if quote.categories else "(none)"
        console.print(f"\n[dim]Current categories:[/dim] {current_cats}")
        new_categories = prompt_input(
            "New categories (comma-separated, or press Enter to keep current): ",
            default="",
        )
        if new_categories.strip():
            quote.categories = [
                _sanitize_text(c).strip().lower()
                for c in new_categories.split(",")
                if c.strip()
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
