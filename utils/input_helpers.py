"""Input helpers with proper backspace support using prompt_toolkit."""

from typing import List

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()

# Import prompt_toolkit for better input handling
PT_AVAILABLE = False
try:
    from prompt_toolkit import PromptSession  # type: ignore

    PT_AVAILABLE = True
except Exception:
    PT_AVAILABLE = False


def prompt_input(prompt_text: str, default: str = "") -> str:
    """Get user input with proper backspace support using prompt_toolkit.

    Ensures backspace works correctly from the very first keystroke.
    Falls back to Rich's Prompt if prompt_toolkit is unavailable.

    Args:
        prompt_text: The prompt to display to the user (can include Rich markup)
        default: Default value if user provides empty input

    Returns:
        User input or default value
    """
    if PT_AVAILABLE:
        try:
            # Print the formatted prompt using Rich, then get input with prompt_toolkit
            console.print(prompt_text)
            session = PromptSession()
            result = session.prompt("")  # Input on next line after prompt
            return result if result else default
        except KeyboardInterrupt:
            raise typer.Exit(0)
        except Exception:
            # Fall back to Rich Prompt if prompt_toolkit fails
            pass

    # Fallback to Rich's Prompt.ask()
    return Prompt.ask(prompt_text, default=default)


def prompt_choice(prompt_text: str, choices: List[str], default: str) -> str:
    """Get user to select from a list of choices.

    Uses prompt_toolkit when available for consistency, falls back to Rich.

    Args:
        prompt_text: The prompt to display (can include Rich markup)
        choices: List of valid choices
        default: Default choice if user provides empty input

    Returns:
        User's selected choice
    """
    if PT_AVAILABLE:
        try:
            while True:
                # Print the formatted prompt using Rich, then get input with prompt_toolkit
                console.print(prompt_text)
                session = PromptSession()
                result = session.prompt("").strip()  # Input on next line after prompt
                if not result:
                    return default
                if result in choices:
                    return result
                # Invalid choice, print error and try again
                console.print(
                    f"[red]Invalid choice. Valid options: {', '.join(choices)}[/red]"
                )
        except KeyboardInterrupt:
            raise typer.Exit(0)
        except Exception:
            # Fall back to Rich Prompt if prompt_toolkit fails
            pass

    # Fallback to Rich's Prompt.ask() with choices
    return Prompt.ask(prompt_text, choices=choices, default=default)


def prompt_confirm(message: str, default: bool = False) -> bool:
    """Ask user for yes/no confirmation.

    Args:
        message: The confirmation message
        default: Default value

    Returns:
        True if user confirms, False otherwise
    """
    return Confirm.ask(message, default=default)


def prompt_continue(message: str = "[dim]Press Enter to continue[/dim]") -> None:
    """Prompt user to press Enter to continue.

    Args:
        message: The message to display
    """
    prompt_input(message, default="")
