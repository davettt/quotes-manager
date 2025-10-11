"""Interactive category selector for quotes."""

from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()

# Predefined categories from spec
PREDEFINED_CATEGORIES = [
    "inspiration",
    "wisdom",
    "creativity",
    "leadership",
    "relationships",
    "growth",
    "resilience",
    "humor",
    "reflection",
    "action",
]


def select_categories(
    preselected: List[str] = None, ai_suggested: bool = False
) -> List[str]:
    """
    Interactive category selection with checkboxes.

    Args:
        preselected: List of categories to pre-select (for AI suggestions in Phase 3)
        ai_suggested: Whether the preselected categories came from AI (for display)

    Returns:
        List of selected category names
    """
    if preselected is None:
        preselected = []

    selected = set(preselected)
    custom_categories = []

    while True:
        # Clear and display header
        console.clear()
        console.print("\n[bold cyan]Select Categories[/bold cyan]\n")
        if ai_suggested and preselected:
            console.print(
                f"[green]✓ AI suggested:[/green] [cyan]{', '.join(preselected)}[/cyan]\n"
            )
        console.print(
            "[dim]Use the number to toggle categories, or 'c' to add custom[/dim]\n"
        )

        # Create table showing all categories
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Number", style="dim yellow", width=4)
        table.add_column("Status", width=3)
        table.add_column("Category", style="cyan")

        # Add predefined categories
        for i, category in enumerate(PREDEFINED_CATEGORIES, 1):
            checkbox = "✓" if category in selected else " "
            table.add_row(str(i), f"[{checkbox}]", category)

        # Add custom categories if any
        for i, category in enumerate(custom_categories, len(PREDEFINED_CATEGORIES) + 1):
            checkbox = "✓" if category in selected else " "
            table.add_row(str(i), f"[{checkbox}]", f"{category} [dim](custom)[/dim]")

        # Display in a panel
        panel = Panel(table, border_style="blue", padding=(1, 2))
        console.print(panel)

        # Show current selection
        if selected:
            console.print(
                f"\n[bold]Selected:[/bold] {', '.join(sorted(selected))}", style="green"
            )
        else:
            console.print("\n[dim]No categories selected[/dim]")

        # Get user input
        console.print(
            "\n[yellow]Options:[/yellow] Enter number to toggle | [cyan]c[/cyan] = add custom | [cyan]d[/cyan] = done | [cyan]x[/cyan] = cancel"
        )
        choice = Prompt.ask("Choice", default="d").lower().strip()

        if choice == "d":
            # Done selecting
            return sorted(list(selected))

        elif choice == "x":
            # Cancel
            return []

        elif choice == "c":
            # Add custom category
            custom = Prompt.ask("\n[cyan]Enter custom category name[/cyan]")
            if custom.strip():
                custom = custom.strip().lower()
                if (
                    custom not in PREDEFINED_CATEGORIES
                    and custom not in custom_categories
                ):
                    custom_categories.append(custom)
                    selected.add(custom)
                    console.print(f"[green]✓ Added '{custom}'[/green]")
                else:
                    console.print(
                        f"[yellow]Category '{custom}' already exists[/yellow]"
                    )
                Prompt.ask("[dim]Press Enter to continue[/dim]", default="")

        elif choice.isdigit():
            # Toggle category
            num = int(choice)
            all_categories = PREDEFINED_CATEGORIES + custom_categories

            if 1 <= num <= len(all_categories):
                category = all_categories[num - 1]
                if category in selected:
                    selected.remove(category)
                else:
                    selected.add(category)


def display_category_summary(categories: List[str]) -> None:
    """
    Display a summary of selected categories.

    Args:
        categories: List of category names
    """
    if categories:
        console.print(
            f"\n[bold]Categories:[/bold] {', '.join(categories)}", style="blue"
        )
    else:
        console.print("\n[dim]No categories selected[/dim]")
