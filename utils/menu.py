"""Interactive menu for Quotes Manager."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from utils.themes import get_color

console = Console()


def display_menu() -> None:
    """Display the main menu with available options."""
    console.clear()

    # Create title
    title = Text()
    title.append("Quotes Manager", style=f"bold {get_color('primary')}")
    title.append(" - Interactive Menu", style=get_color("dim"))

    # Create menu table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Number", style=get_color("warning"), width=4)
    table.add_column("Command", style=get_color("primary"))

    menu_items = [
        ("1", "Add new quote"),
        ("2", "View daily quote"),
        ("3", "List all quotes"),
        ("4", "Search quotes"),
        ("5", "View quote details"),
        ("6", "Edit quote"),
        ("7", "Delete quote"),
        ("8", "Setup shell integration"),
        ("9", "Change theme"),
        ("0", "Exit"),
    ]

    for number, command in menu_items:
        table.add_row(number, command)

    # Display in a panel
    panel = Panel(
        table,
        title=title,
        border_style=get_color("border"),
        padding=(1, 2),
    )

    console.print()
    console.print(panel)
    console.print()


def get_menu_choice() -> str:
    """
    Get user's menu selection.

    Returns:
        Selected menu option as string
    """
    prompt_style = f"bold {get_color('warning')}"
    choice = Prompt.ask(
        f"[{prompt_style}]Select an option[/{prompt_style}]",
        choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
        default="0",
    )
    return choice


def show_menu_message(message: str, style: str = "green") -> None:
    """
    Show a message to the user before returning to menu.

    Args:
        message: Message to display
        style: Rich style for the message
    """
    console.print()
    console.print(f"[{style}]{message}[/{style}]")
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def confirm_action(message: str) -> bool:
    """
    Ask user to confirm an action.

    Args:
        message: Confirmation message

    Returns:
        True if user confirms, False otherwise
    """
    from rich.prompt import Confirm

    return Confirm.ask(message, default=False)
