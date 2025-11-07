"""Change color theme command."""

import typer
from rich.console import Console
from rich.table import Table

from utils.display import get_current_theme_name, set_theme
from utils.input_helpers import prompt_choice
from utils.themes import THEMES, get_color

console = Console()


def change_theme_interactive():
    """Interactive theme selection for menu mode."""
    # Get current theme name
    current_name = get_current_theme_name()

    # Display available themes
    console.print("\n[bold cyan]Available Themes:[/bold cyan]\n")

    table = Table(show_header=True, box=None, padding=(0, 2))
    table.add_column("Number", style="dim yellow", width=6)
    table.add_column("Theme", style="cyan", width=20)
    table.add_column("Description", style="default")
    table.add_column("Current", style="green", width=8)

    themes_list = [
        ("1", "auto", "Adapts to your terminal (default)"),
        ("2", "dark", "Bright colors for dark backgrounds"),
        ("3", "light", "Darker colors for light backgrounds"),
        ("4", "high-contrast", "Maximum contrast for accessibility"),
        ("5", "none", "Plain text, no colors"),
    ]

    for num, name, desc in themes_list:
        current_mark = "✓" if name == current_name else ""
        table.add_row(num, name, desc, current_mark)

    console.print(table)
    console.print()

    # Get selection
    choice = prompt_choice(
        "[bold yellow]Select theme:[/bold yellow] ",
        choices=["1", "2", "3", "4", "5"],
        default="1",
    )

    # Map choice to theme name
    theme_map = {
        "1": "auto",
        "2": "dark",
        "3": "light",
        "4": "high-contrast",
        "5": "none",
    }

    selected_theme = theme_map[choice]

    # Apply theme
    set_theme(selected_theme)

    # Show confirmation with example
    console.print(
        f"\n[green]✓[/green] Theme changed to [bold cyan]{selected_theme}[/bold cyan]"
    )

    # Show a preview of the new colors
    console.print("\n[dim]Preview of colors:[/dim]")
    console.print("  Primary:  ", end="")
    console.print("██████████████████████████", style=get_color("primary"))
    console.print("  Success:  ", end="")
    console.print("██████████████████████████", style=get_color("success"))
    console.print("  Warning:  ", end="")
    console.print("██████████████████████████", style=get_color("warning"))
    console.print("  Error:    ", end="")
    console.print("██████████████████████████", style=get_color("error"))

    console.print(
        "\n[dim]Theme will apply to all menu operations until you exit.[/dim]"
    )


def change_theme_command(
    theme: str = typer.Argument(
        None, help="Theme name: auto, dark, light, high-contrast, none"
    ),
):
    """
    Change the color theme.

    Examples:
        quotes theme          # Interactive selection
        quotes theme dark     # Set to dark theme
        quotes theme light    # Set to light theme
    """
    if theme is None:
        # Interactive mode
        change_theme_interactive()
    else:
        # Direct theme setting
        if theme not in THEMES:
            console.print(f"[red]Error: Unknown theme '{theme}'[/red]")
            console.print(
                f"\n[yellow]Available themes:[/yellow] {', '.join(THEMES.keys())}"
            )
            raise typer.Exit(1)

        set_theme(theme)
        console.print(
            f"[green]✓[/green] Theme changed to [bold cyan]{theme}[/bold cyan]"
        )
