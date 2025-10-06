"""Shell integration setup command."""

import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()


def detect_shell() -> tuple[str, Path]:
    """
    Detect the user's shell and profile file.

    Returns:
        Tuple of (shell_name, profile_path)
    """
    shell = os.environ.get("SHELL", "")

    if "zsh" in shell:
        profile = Path.home() / ".zshrc"
        return ("zsh", profile)
    elif "bash" in shell:
        # Check for .bash_profile first, then .bashrc
        bash_profile = Path.home() / ".bash_profile"
        bashrc = Path.home() / ".bashrc"
        if bash_profile.exists():
            return ("bash", bash_profile)
        else:
            return ("bash", bashrc)
    elif "fish" in shell:
        profile = Path.home() / ".config" / "fish" / "config.fish"
        return ("fish", profile)
    else:
        # Default to bashrc
        return ("unknown", Path.home() / ".bashrc")


def setup_shell():
    """
    Setup shell integration to show daily quote on terminal startup.

    Shows instructions for adding the daily quote command to the shell profile.
    """
    console.print("\n[bold cyan]Shell Integration Setup[/bold cyan]\n")
    console.print(
        "This will show you how to add a daily quote to your shell startup.\n"
        "You'll see a quote each time you open a new terminal.\n"
    )

    # Detect shell
    shell_name, profile_path = detect_shell()

    console.print(f"[green]✓ Detected shell:[/green] {shell_name}")
    console.print(f"[green]✓ Profile file:[/green] {profile_path}\n")

    # Show the line to add
    integration_line = "quotes daily --quiet"

    console.print("[bold]Add this line to your shell profile:[/bold]\n")
    console.print(
        Panel(integration_line, border_style="cyan", padding=(0, 1)), style="cyan bold"
    )

    console.print("\n[bold]Instructions:[/bold]\n")
    console.print(f"  1. Open your profile file: [cyan]{profile_path}[/cyan]")
    console.print("  2. Add the line above at the end of the file")
    console.print("  3. Save and close the file")
    console.print(f"  4. Restart your terminal, or run: [cyan]source {profile_path}[/cyan]\n")

    console.print("[dim]Note: Make sure you've installed this package first with:[/dim]")
    console.print("[dim]pip install -e .[/dim]\n")

    console.print("[green]✓ That's it! Your daily quote will appear when you open a new terminal.[/green]\n")
