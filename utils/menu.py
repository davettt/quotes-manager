"""Interactive menu for Quotes Manager."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

console = Console()


def display_menu() -> None:
    """Display the main menu with available options."""
    console.clear()

    # Create title
    title = Text()
    title.append("Quotes Manager", style="bold cyan")
    title.append(" - Interactive Menu", style="dim")

    # Create menu table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Number", style="dim yellow", width=4)
    table.add_column("Command", style="cyan")

    menu_items = [
        ("1", "Add new quote"),
        ("2", "View daily quote"),
        ("3", "List all quotes"),
        ("4", "Search quotes"),
        ("5", "View quote details"),
        ("6", "Edit quote"),
        ("7", "Delete quote"),
        ("8", "Setup shell integration"),
        ("0", "Exit"),
    ]

    for number, command in menu_items:
        table.add_row(number, command)

    # Display in a panel
    panel = Panel(
        table,
        title=title,
        border_style="blue",
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
    choice = Prompt.ask(
        "[bold yellow]Select an option[/bold yellow]",
        choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"],
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
