"""Generate quote image command implementation."""

import os
import platform
import subprocess  # nosec B404
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ai.unsplash import (
    PhotoResult,
    cleanup_photo,
    fetch_background_photo,
    format_attribution,
    format_credit,
    is_available,
)
from commands.daily import get_daily_quote
from utils.display import display_error, display_warning, set_theme
from utils.image_renderer import PRESETS, RATIOS, render_quote_image
from utils.storage import get_quote_by_id, load_quotes

console = Console()

# Output directory for generated images
_IMAGES_DIR = Path(__file__).parent.parent / "local_data" / "images"

_VALID_RATIOS = list(RATIOS.keys())
_VALID_STYLES = list(PRESETS.keys())


def _open_preview(path: Path) -> None:
    """Open the image file in the system default viewer."""
    try:
        system = platform.system()
        if system == "Darwin":
            subprocess.run(["open", str(path)], check=False)  # nosec B603 B607
        elif system == "Linux":
            subprocess.run(["xdg-open", str(path)], check=False)  # nosec B603 B607
        elif system == "Windows":
            os.startfile(str(path))  # type: ignore[attr-defined]  # nosec B606
    except Exception:
        pass  # Preview is best-effort


def _fetch_photo(search_term: str, ratio: str) -> Optional[PhotoResult]:
    """Fetch a background photo from Unsplash. Returns None if unavailable."""
    if not is_available():
        return None
    with console.status(f"  Searching Unsplash for [dim]{search_term}[/dim]..."):
        return fetch_background_photo(search_term, ratio=ratio)


def _render_and_save(
    quote,
    photo: Optional[PhotoResult],
    ratio: str,
    style: str,
    no_preview: bool,
) -> Optional[Path]:
    """Render *quote* with *style* and save to disk. Returns the saved path."""
    try:
        with console.status("  Rendering image..."):
            png_bytes = render_quote_image(
                quote_text=quote.text,
                author=quote.author,
                categories=quote.categories,
                ratio=ratio,
                style=style,
                bg_image_path=photo.temp_path if photo else None,
                photo_credit=format_credit(photo) if photo else None,
            )
    except Exception as e:
        display_error(f"Render failed: {e}")
        return None

    _IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"quote-{quote.id[:8]}-{ratio}-{style}.png"
    out_path = _IMAGES_DIR / filename

    try:
        out_path.write_bytes(png_bytes)
    except OSError as e:
        display_error(f"Could not save image: {e}")
        return None

    console.print(f"\n  [green]✓[/green] Saved: {out_path}")

    if photo:
        console.print(f"\n  [dim]{format_attribution(photo)}[/dim]")

    if not no_preview:
        _open_preview(out_path)

    return out_path


def generate_image_for_quote(
    quote,
    ratio: str = "square",
    style: str = "dark",
    topic: Optional[str] = None,
    no_photo: bool = False,
    no_preview: bool = False,
) -> Optional[Path]:
    """
    Fetch photo + render once. Used by the CLI command.

    Returns:
        Path to the saved image, or None on failure.
    """
    search_term = topic or (quote.categories[0] if quote.categories else "nature")
    photo = None if no_photo else _fetch_photo(search_term, ratio)
    try:
        return _render_and_save(quote, photo, ratio, style, no_preview)
    finally:
        if photo:
            cleanup_photo(photo)


def generate_image_interactive(
    quote,
    ratio: str = "square",
    style: str = "dark",
    topic: Optional[str] = None,
    no_photo: bool = False,
    no_preview: bool = False,
) -> Optional[Path]:
    """
    Fetch photo then offer a refinement loop: restyle with the same photo,
    fetch a new photo, or keep the current result.

    Used by the interactive menu and view screen.
    """
    from utils.input_helpers import prompt_input

    search_term = topic or (quote.categories[0] if quote.categories else "nature")
    photo = None if no_photo else _fetch_photo(search_term, ratio)

    try:
        current_style = style
        current_search = search_term
        last_path: Optional[Path] = None

        while True:
            last_path = _render_and_save(quote, photo, ratio, current_style, no_preview)
            if last_path is None:
                return None

            other_styles = [s for s in _VALID_STYLES if s != current_style]
            hint = f"  [dim]Styles: {', '.join(other_styles)}"
            if not no_photo and is_available():
                hint += "  |  (p) new photo  |  (k) new keyword"
            hint += "[/dim]"
            console.print(f"\n{hint}")

            action = (
                prompt_input(
                    "  Type a style, (p) new photo, (k) new keyword, or Enter to keep: "
                )
                .strip()
                .lower()
            )

            if not action:
                return last_path

            if action == "p":
                if not no_photo and is_available():
                    if photo:
                        cleanup_photo(photo)
                        photo = None
                    photo = _fetch_photo(current_search, ratio)
            elif action == "k":
                if not no_photo and is_available():
                    new_keyword = prompt_input(
                        f"  Search keyword (current: {current_search}): "
                    ).strip()
                    if new_keyword:
                        current_search = new_keyword
                    if photo:
                        cleanup_photo(photo)
                        photo = None
                    photo = _fetch_photo(current_search, ratio)
            elif action in _VALID_STYLES:
                current_style = action
            else:
                return last_path

    finally:
        if photo:
            cleanup_photo(photo)


def image_quote(
    quote_id: str = typer.Option(
        "",
        "--id",
        "-i",
        help="Quote ID to use (defaults to today's daily quote)",
        show_default=False,
    ),
    ratio: str = typer.Option(
        "square",
        "--ratio",
        "-r",
        help=f"Aspect ratio: {', '.join(_VALID_RATIOS)}",
    ),
    style: str = typer.Option(
        "dark",
        "--style",
        "-s",
        help=f"Style preset: {', '.join(_VALID_STYLES)}",
    ),
    topic: Optional[str] = typer.Option(
        None,
        "--topic",
        "-t",
        help="Override Unsplash search term (default: quote's first category)",
    ),
    no_photo: bool = typer.Option(
        False,
        "--no-photo",
        help="Use gradient background instead of Unsplash photo",
    ),
    no_preview: bool = typer.Option(
        False,
        "--no-preview",
        help="Save image without opening a preview",
    ),
    theme: Optional[str] = typer.Option(
        None, "--theme", help="Color theme: auto, dark, light, high-contrast, none"
    ),
):
    """
    Generate a shareable image for a quote.

    Uses today's daily quote when no ID is given. Background photos are fetched
    from Unsplash (requires UNSPLASH_ACCESS_KEY in .env); falls back to a
    gradient if unavailable or when --no-photo is set.

    Examples:
        quotes image
        quotes image --id a1b2c3d4
        quotes image --id a1b2c3d4 --ratio mobile --style bold
        quotes image --id a1b2c3d4 --topic "mountains" --no-preview
    """
    if theme:
        set_theme(theme)

    # Validate ratio and style
    if ratio not in _VALID_RATIOS:
        display_error(
            f"Invalid ratio '{ratio}'. Choose from: {', '.join(_VALID_RATIOS)}"
        )
        raise typer.Exit(1)

    if style not in _VALID_STYLES:
        display_error(
            f"Invalid style '{style}'. Choose from: {', '.join(_VALID_STYLES)}"
        )
        raise typer.Exit(1)

    # Resolve quote
    quote = None
    if quote_id:
        quote = get_quote_by_id(quote_id)

        if not quote:
            quotes = load_quotes()
            matches = [q for q in quotes if q.id.startswith(quote_id)]
            if len(matches) == 1:
                quote = matches[0]
            elif len(matches) > 1:
                display_error(
                    f"Multiple quotes match '{quote_id}'. Please be more specific:"
                )
                for q in matches:
                    console.print(f'  [dim]{q.id[:8]}[/dim]: "{q.text[:60]}..."')
                raise typer.Exit(1)

        if not quote:
            display_error(f"No quote found with ID '{quote_id}'")
            raise typer.Exit(1)
    else:
        quote = get_daily_quote()
        if not quote:
            display_warning("No quotes saved yet. Add some with: quotes add")
            raise typer.Exit(1)

    # Display what we're generating
    w, h = RATIOS[ratio]
    console.print()
    console.print(
        f'  [dim]"{quote.text[:70]}{"..." if len(quote.text) > 70 else ""}"[/dim]'
    )
    console.print(f"  [dim]— {quote.author}[/dim]")
    console.print(
        f"\n  Style: [cyan]{style}[/cyan]  |  Ratio: [cyan]{ratio}[/cyan] ({w}×{h})"
    )
    console.print()

    generate_image_for_quote(
        quote=quote,
        ratio=ratio,
        style=style,
        topic=topic,
        no_photo=no_photo,
        no_preview=no_preview,
    )
    console.print()
