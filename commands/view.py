"""View quote command implementation."""

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.markdown import Markdown

from utils.storage import get_quote_by_id, update_quote, load_quotes
from utils.display import display_quote_detailed, display_error
from ai.claude_client import is_api_available
from ai.explainer import explain_quote

console = Console()


def view_quote(
    quote_id: str = typer.Argument(..., help="Quote ID to view (full or partial)"),
    explain: bool = typer.Option(
        False, "--explain", "-e", help="Show AI explanation immediately"
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
    # Check if AI is available
    ai_available = is_api_available()

    # Build options
    options_text = "\n".join(
        [
            (
                "  [yellow]e[/yellow] - Explain this quote (AI)"
                if ai_available
                else "  [dim]e - Explain (AI unavailable)[/dim]"
            ),
            "  [yellow]q[/yellow] - Back to menu",
        ]
    )

    console.print(f"{options_text}\n")

    choices = ["e", "q"] if ai_available else ["q"]
    choice = Prompt.ask("Choice", choices=choices, default="q")

    if choice == "e" and ai_available:
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

            # Show options again
            console.print()
            show_interactive_options(quote)
