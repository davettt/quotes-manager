"""Color theme system for CLI display."""

import os
from pathlib import Path
from typing import Dict

# Theme definitions
THEMES = {
    "auto": {
        # Default - Use Rich's adaptive colors
        "primary": "cyan",
        "secondary": "default",
        "emphasis": "magenta",
        "success": "green",
        "warning": "yellow",
        "error": "red",
        "dim": "dim default",
        "border": "blue",
    },
    "dark": {
        # Optimized for dark backgrounds
        "primary": "bright_cyan",
        "secondary": "bright_white",
        "emphasis": "bright_magenta",
        "success": "bright_green",
        "warning": "bright_yellow",
        "error": "bright_red",
        "dim": "bright_white",
        "border": "bright_blue",
    },
    "light": {
        # Optimized for light backgrounds
        "primary": "blue",
        "secondary": "black",
        "emphasis": "purple",
        "success": "dark_green",
        "warning": "#B8860B",  # dark goldenrod
        "error": "dark_red",
        "dim": "dim black",
        "border": "blue",
    },
    "high-contrast": {
        # Maximum contrast for accessibility
        "primary": "bright_white",
        "secondary": "white",
        "emphasis": "bright_yellow",
        "success": "bright_green",
        "warning": "bright_yellow",
        "error": "bright_red",
        "dim": "white",
        "border": "white",
    },
    "none": {
        # No colors - plain text only
        "primary": "default",
        "secondary": "default",
        "emphasis": "default",
        "success": "default",
        "warning": "default",
        "error": "default",
        "dim": "default",
        "border": "default",
    },
}


def load_theme(theme_name: str = None) -> Dict[str, str]:
    """
    Load color theme based on priority:
    1. Provided theme_name parameter
    2. Environment variable (QUOTES_THEME)
    3. Config file (~/.config/quotes-manager/config.toml)
    4. Default "auto"

    Returns:
        Dict mapping purpose to color string
    """
    # Priority 1: Parameter
    if theme_name and theme_name in THEMES:
        return THEMES[theme_name]

    # Priority 2: Environment variable
    env_theme = os.getenv("QUOTES_THEME")
    if env_theme and env_theme in THEMES:
        return THEMES[env_theme]

    # Priority 3: Config file (optional - future enhancement)
    config_path = Path.home() / ".config" / "quotes-manager" / "config.toml"
    if config_path.exists():
        try:
            # Note: tomli only needed for Python < 3.11
            # For Python 3.11+, use: import tomllib
            try:
                import tomllib  # Python 3.11+
            except ImportError:
                import tomli as tomllib  # Python < 3.11

            with open(config_path, "rb") as f:
                config = tomllib.load(f)
                config_theme = config.get("display", {}).get("theme")
                if config_theme and config_theme in THEMES:
                    return THEMES[config_theme]
        except (ImportError, Exception):
            pass  # Fall back to default if config reading fails

    # Priority 4: Default
    return THEMES["auto"]


def get_color(purpose: str, theme: Dict[str, str] = None) -> str:
    """
    Get color string for a specific purpose.

    Args:
        purpose: Color purpose (primary, secondary, emphasis, etc.)
        theme: Optional theme dict (uses active theme from display if None)

    Returns:
        Color string for Rich styling
    """
    if theme is None:
        # Import module and access attribute to get current value
        import utils.display

        theme = utils.display.THEME
    return theme.get(purpose, "default")
