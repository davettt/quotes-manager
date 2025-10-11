#!/usr/bin/env python3
"""
Quotes Manager CLI - Main entry point.

A CLI tool for managing and reflecting on meaningful quotes with AI insights.
"""

import typer
from rich.console import Console
from rich.prompt import Prompt

# Import command implementations
from commands.add import add_quote
from commands.daily import show_daily
from commands.delete import delete_quote_command
from commands.edit import edit_quote
from commands.list_cmd import list_quotes
from commands.search import search_quotes
from commands.setup_shell import setup_shell
from commands.theme import change_theme_command
from commands.view import view_quote
from utils.menu import display_menu, get_menu_choice
from utils.themes import get_color
from version import __version__

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
                goodbye_style = get_color("primary")
                console.print(f"\n[{goodbye_style}]Goodbye! 📖✨[/{goodbye_style}]\n")
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
                    theme=None,
                )
                dim_style = get_color("dim")
                Prompt.ask(
                    f"\n[{dim_style}]Press Enter to continue[/{dim_style}]", default=""
                )

            elif choice == "2":
                # View daily quote
                console.clear()
                show_daily(quiet=False, force=False, theme=None)
                dim_style = get_color("dim")
                Prompt.ask(
                    f"\n[{dim_style}]Press Enter to continue[/{dim_style}]", default=""
                )

            elif choice == "3":
                # List all quotes
                console.clear()
                list_quotes(category=None, author=None, limit=10, all=True, theme=None)
                dim_style = get_color("dim")
                Prompt.ask(
                    f"\n[{dim_style}]Press Enter to continue[/{dim_style}]", default=""
                )

            elif choice == "4":
                # Search quotes
                console.clear()
                prompt_style = f"bold {get_color('primary')}"
                query = Prompt.ask(f"[{prompt_style}]Search query[/{prompt_style}]")
                if query:
                    search_quotes(query=query, case_sensitive=False, theme=None)
                dim_style = get_color("dim")
                Prompt.ask(
                    f"\n[{dim_style}]Press Enter to continue[/{dim_style}]", default=""
                )

            elif choice == "5":
                # View quote details
                console.clear()
                prompt_style = f"bold {get_color('primary')}"
                quote_id = Prompt.ask(
                    f"[{prompt_style}]Enter quote ID[/{prompt_style}]"
                )
                if quote_id:
                    view_quote(quote_id=quote_id, theme=None)
                dim_style = get_color("dim")
                Prompt.ask(
                    f"\n[{dim_style}]Press Enter to continue[/{dim_style}]", default=""
                )

            elif choice == "6":
                # Edit quote
                console.clear()
                prompt_style = f"bold {get_color('primary')}"
                quote_id = Prompt.ask(
                    f"[{prompt_style}]Enter quote ID to edit[/{prompt_style}]"
                )
                if quote_id:
                    edit_quote(quote_id=quote_id, theme=None)
                dim_style = get_color("dim")
                Prompt.ask(
                    f"\n[{dim_style}]Press Enter to continue[/{dim_style}]", default=""
                )

            elif choice == "7":
                # Delete quote
                console.clear()
                prompt_style = f"bold {get_color('primary')}"
                quote_id = Prompt.ask(
                    f"[{prompt_style}]Enter quote ID to delete[/{prompt_style}]"
                )
                if quote_id:
                    delete_quote_command(quote_id=quote_id, force=False, theme=None)
                dim_style = get_color("dim")
                Prompt.ask(
                    f"\n[{dim_style}]Press Enter to continue[/{dim_style}]", default=""
                )

            elif choice == "8":
                # Setup shell integration
                console.clear()
                setup_shell()
                dim_style = get_color("dim")
                Prompt.ask(
                    f"\n[{dim_style}]Press Enter to continue[/{dim_style}]", default=""
                )

            elif choice == "9":
                # Change theme
                console.clear()
                from commands.theme import change_theme_interactive

                change_theme_interactive()
                dim_style = get_color("dim")
                Prompt.ask(
                    f"\n[{dim_style}]Press Enter to continue[/{dim_style}]", default=""
                )

        except KeyboardInterrupt:
            goodbye_style = get_color("primary")
            console.print(f"\n\n[{goodbye_style}]Goodbye! 📖✨[/{goodbye_style}]\n")
            return  # Exit cleanly
        except typer.Exit:
            # Don't catch typer.Exit - let it propagate
            raise
        except Exception as e:
            error_style = get_color("error")
            console.print(f"\n[{error_style}]Error: {e}[/{error_style}]\n")
            dim_style = get_color("dim")
            Prompt.ask(
                f"[{dim_style}]Press Enter to continue[/{dim_style}]", default=""
            )


# Register commands
app.command(name="add")(add_quote)
app.command(name="list")(list_quotes)
app.command(name="view")(view_quote)
app.command(name="search")(search_quotes)
app.command(name="edit")(edit_quote)
app.command(name="delete")(delete_quote_command)
app.command(name="daily")(show_daily)
app.command(name="setup")(setup_shell)
app.command(name="theme")(change_theme_command)


if __name__ == "__main__":
    app()
