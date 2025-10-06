#!/usr/bin/env python3
"""
Quotes Manager CLI - Main entry point.

A CLI tool for managing and reflecting on meaningful quotes with AI insights.
"""

import typer
from rich.console import Console
from rich.prompt import Prompt

from version import __version__

# Import command implementations
from commands.add import add_quote
from commands.list_cmd import list_quotes
from commands.view import view_quote
from commands.search import search_quotes
from commands.edit import edit_quote
from commands.delete import delete_quote_command
from commands.daily import show_daily
from commands.setup_shell import setup_shell
from utils.menu import display_menu, get_menu_choice

# Initialize Typer app
app = typer.Typer(
    name="quotes",
    help="Manage and reflect on meaningful quotes with AI insights",
    add_completion=False,
    no_args_is_help=False,  # Changed to False to allow menu mode
)

console = Console()


def version_callback(value: bool):
    """Show version information."""
    if value:
        console.print(f"Quotes Manager v{__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """
    Quotes Manager - Manage and reflect on meaningful quotes.

    Run without arguments for interactive menu, or use commands directly.
    """
    # If a subcommand was invoked, don't show the menu
    if ctx.invoked_subcommand is not None:
        return

    # If no subcommand, show interactive menu
    run_interactive_menu()


def run_interactive_menu():
    """Run the interactive menu loop."""
    while True:
        try:
            display_menu()
            choice = get_menu_choice()

            if choice == "0":
                console.print("\n[cyan]Goodbye! 📖✨[/cyan]\n")
                return  # Exit the loop cleanly

            elif choice == "1":
                # Add new quote
                console.clear()
                add_quote(
                    text=None,
                    author=None,
                    source=None,
                    note=None,
                    categories=None,
                    skip_ai=False,
                )
                Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")

            elif choice == "2":
                # View daily quote
                console.clear()
                show_daily(quiet=False, force=False)
                Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")

            elif choice == "3":
                # List all quotes
                console.clear()
                list_quotes(category=None, author=None, limit=10, all=False)
                Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")

            elif choice == "4":
                # Search quotes
                console.clear()
                query = Prompt.ask("[bold cyan]Search query[/bold cyan]")
                if query:
                    search_quotes(query=query, case_sensitive=False)
                Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")

            elif choice == "5":
                # View quote details
                console.clear()
                quote_id = Prompt.ask("[bold cyan]Enter quote ID[/bold cyan]")
                if quote_id:
                    view_quote(quote_id=quote_id)
                Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")

            elif choice == "6":
                # Edit quote
                console.clear()
                quote_id = Prompt.ask("[bold cyan]Enter quote ID to edit[/bold cyan]")
                if quote_id:
                    edit_quote(quote_id=quote_id)
                Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")

            elif choice == "7":
                # Delete quote
                console.clear()
                quote_id = Prompt.ask("[bold cyan]Enter quote ID to delete[/bold cyan]")
                if quote_id:
                    delete_quote_command(quote_id=quote_id, force=False)
                Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")

            elif choice == "8":
                # Setup shell integration
                console.clear()
                setup_shell()
                Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")

        except KeyboardInterrupt:
            console.print("\n\n[cyan]Goodbye! 📖✨[/cyan]\n")
            return  # Exit cleanly
        except typer.Exit:
            # Don't catch typer.Exit - let it propagate
            raise
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]\n")
            Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


# Register commands
app.command(name="add")(add_quote)
app.command(name="list")(list_quotes)
app.command(name="view")(view_quote)
app.command(name="search")(search_quotes)
app.command(name="edit")(edit_quote)
app.command(name="delete")(delete_quote_command)
app.command(name="daily")(show_daily)
app.command(name="setup")(setup_shell)


if __name__ == "__main__":
    app()
