"""View quote command implementation."""

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm

from ai.claude_client import is_api_available
from ai.explainer import explain_quote
from utils.display import display_error, display_quote_detailed, set_theme
from utils.input_helpers import prompt_choice
from utils.storage import get_quote_by_id, load_quotes, update_quote

console = Console()


def view_quote(
    quote_id: str = typer.Argument(..., help="Quote ID to view (full or partial)"),
    explain: bool = typer.Option(
        False, "--explain", "-e", help="Show AI explanation immediately"
    ),
    theme: str = typer.Option(
        None, "--theme", help="Color theme: auto, dark, light, high-contrast, none"
    ),
):
    """
    View detailed information about a specific quote.

    You can use either the full quote ID or just the first few characters.
    Use --explain to get an AI-powered explanation of the quote's meaning.

    Example:
        quotes view a1b2c3d4
        quotes view a1b2 --explain    # Show with AI explanation
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

    # Display quote details
    console.print()
    display_quote_detailed(quote)

    # Show AI explanation if requested
    if explain and is_api_available():
        show_explanation(quote)
    elif explain and not is_api_available():
        console.print(
            "\n[yellow]AI explanation unavailable (no API key configured)[/yellow]"
        )

    # Interactive options (only if not run from command line with --explain)
    if not explain:
        console.print()
        show_interactive_options(quote)


def show_explanation(quote):
    """Show AI-generated explanation for a quote."""
    console.print()
    with console.status("🤔 Generating explanation..."):
        try:
            explanation = explain_quote(quote.to_dict())

            console.print()
            console.print(
                Panel(
                    Markdown(explanation),
                    title="[bold cyan]💡 AI Explanation[/bold cyan]",
                    border_style="cyan",
                    padding=(1, 2),
                )
            )
            return explanation

        except Exception as e:
            console.print(f"\n[yellow]Explanation unavailable: {e}[/yellow]")
            return None


def show_interactive_options(quote):
    """Show interactive options for viewing a quote."""
    # Import here to avoid circular imports
    from commands.delete import delete_quote_command
    from commands.edit import edit_quote

    # Check if AI is available
    ai_available = is_api_available()

    while True:
        # Build options
        options_text = "\n".join(
            [
                (
                    "  [yellow]e[/yellow] - Explain this quote (AI)"
                    if ai_available
                    else "  [dim]e - Explain (AI unavailable)[/dim]"
                ),
                "  [yellow]ed[/yellow] - Edit this quote",
                "  [yellow]d[/yellow] - Delete this quote",
                "  [yellow]b[/yellow] - Back to menu",
            ]
        )

        console.print(f"{options_text}\n")

        choices = ["e", "ed", "d", "b"] if ai_available else ["ed", "d", "b"]
        choice = prompt_choice("Choice: ", choices=choices, default="b")

        if choice == "b":
            # Return to menu
            return

        elif choice == "e" and ai_available:
            explanation = show_explanation(quote)

            # Ask if they want to save the explanation
            if explanation:
                console.print()
                if Confirm.ask(
                    "Would you like to save this explanation to the quote's notes?",
                    default=False,
                ):
                    # Get current note
                    current_note = quote.personal_note

                    # Append explanation
                    if current_note:
                        quote.personal_note = (
                            f"{current_note}\n\nAI Explanation:\n{explanation}"
                        )
                    else:
                        quote.personal_note = f"AI Explanation:\n{explanation}"

                    # Save
                    update_quote(quote)
                    console.print("\n[green]✓ Explanation saved to quote notes[/green]")

                # Continue to show options again
                console.print()

        elif choice == "ed":
            # Edit the quote
            console.print()
            try:
                edit_quote(quote_id=quote.id, theme=None)
                # After editing, reload the quote to show updated details
                from utils.storage import get_quote_by_id

                updated_quote = get_quote_by_id(quote.id)
                if updated_quote:
                    quote = updated_quote
                    console.print()
                    display_quote_detailed(quote)
                    console.print()
            except Exception:
                # If edit was cancelled or failed, continue
                console.print()

        elif choice == "d":
            # Delete the quote
            console.print()
            try:
                delete_quote_command(quote_id=quote.id, force=False, theme=None)
                # If deletion succeeded, exit the function (return to menu)
                return
            except Exception:
                # If deletion was cancelled or failed, continue
                console.print()
