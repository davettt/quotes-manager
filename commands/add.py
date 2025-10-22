"""Add quote command implementation."""

import os
import re
import shlex
import subprocess  # nosec B404
import tempfile
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from ai.author_identifier import identify_author_enhanced
from ai.categorizer import suggest_categories
from ai.claude_client import is_api_available
from ai.duplicate_detector import check_duplicates, get_similarity_level
from models.quote import AIMetadata, Quote
from utils.category_selector import select_categories
from utils.display import display_success, display_warning, set_theme
from utils.storage import load_quotes, save_quotes

# Enable line editing (arrow keys) for input() where supported
try:
    import readline  # noqa: F401

    try:
        # Best-effort to enable bracketed paste if available
        readline.parse_and_bind("set enable-bracketed-paste on")
    except Exception:
        pass
except Exception:
    pass

# Optional rich multiline editor with full cursor movement across lines
PT_AVAILABLE = False
try:
    from prompt_toolkit import PromptSession  # type: ignore
    from prompt_toolkit.key_binding import KeyBindings  # type: ignore

    PT_AVAILABLE = True
except Exception:
    PT_AVAILABLE = False

console = Console()


def _sanitize_text(text: str) -> str:
    """Sanitize user-provided text while preserving meaningful content.

    - Normalize CRLF/CR to LF
    - Strip trailing whitespace on each line
    - Remove NUL and other non-printable control chars (except tab/newline)
    - Trim a single trailing newline at the end of content
    """
    if text is None:
        return ""
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Remove NULs and control chars except tab/newline
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)
    # Strip trailing whitespace per line
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    # Remove a single trailing newline, but keep internal newlines
    if text.endswith("\n"):
        text = text[:-1]
    return text


def _cleanup_pasted_text(text: str) -> str:
    """Heuristically clean up pasted content.

    - Strip ANSI escape sequences and caret-notation arrow keys (e.g., ^[[D)
    - Remove common left/right box borders using │ or |
    - Dedent by common leading whitespace
    - Trim extra blank lines at start/end
    """
    if not text:
        return ""
    # Remove ANSI CSI sequences (e.g., ESC[31m, ESC[A)
    text = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)
    # Remove caret-notation sequences like ^[[D, ^[[A, ^[[1;5C
    text = re.sub(r"\^\[\[[0-9;]*[~A-Za-z]", "", text)

    lines = text.split("\n")

    # Detect and strip common left border (│ or |) for majority of lines
    def strip_left_border(s: str) -> str:
        return re.sub(r"^\s*[│|]\s?", "", s)

    def has_left_border(s: str) -> bool:
        return re.match(r"^\s*[│|]\s?", s) is not None

    non_empty = [ln for ln in lines if ln.strip()]
    if non_empty:
        count_left = sum(1 for ln in non_empty if has_left_border(ln))
        if count_left >= max(1, int(0.6 * len(non_empty))):  # if majority
            lines = [strip_left_border(ln) for ln in lines]

    # Strip right border if present
    lines = [re.sub(r"\s*[│|]\s*$", "", ln) for ln in lines]

    # Dedent by common leading whitespace across non-empty lines
    non_empty = [ln for ln in lines if ln.strip()]
    if non_empty:
        # Compute min common indent
        def leading_spaces(s: str) -> int:
            return len(s) - len(s.lstrip(" "))

        min_indent = min(leading_spaces(ln) for ln in non_empty)
        if min_indent > 0:
            lines = [ln[min_indent:] if len(ln) >= min_indent else ln for ln in lines]

    # Trim leading/trailing blank lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    # Re-trim trailing whitespace on each line
    lines = [ln.rstrip() for ln in lines]

    return "\n".join(lines)


def _truthy(val: Optional[str]) -> bool:
    if val is None:
        return False
    return val.strip().lower() in {"1", "true", "yes", "on"}


def _edit_in_editor(initial_text: str = "") -> str:
    """Open $EDITOR (or nano) to capture multi-line content.

    - Prefills a helpful header as comments that are removed on save.
    - Honors EDITOR env var; supports editors like 'code -w'.
    """
    editor = os.environ.get("EDITOR", "nano").strip()
    if not editor:
        editor = "nano"

    header = (
        "# Quotes Manager - Editor Input\n"
        "# Write or paste your quote below. Lines starting with '#' are ignored.\n"
        "# Save and close the editor when done.\n\n"
    )

    with tempfile.NamedTemporaryFile("w+", suffix=".quote.txt", delete=False) as tf:
        path = tf.name
        tf.write(header)
        if initial_text:
            tf.write(initial_text)
        tf.flush()

    try:
        # Use shlex.split to support commands like "code -w"
        # Editor is from trusted env var EDITOR, path is controlled temp file
        cmd = shlex.split(editor) + [path]
        subprocess.run(cmd, check=True)  # nosec B603
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    finally:
        try:
            os.remove(path)
        except Exception:
            pass

    # Remove commented lines from header and any other comment lines
    lines = [ln for ln in content.splitlines() if not ln.lstrip().startswith("#")]
    return _sanitize_text("\n".join(lines))


def _read_multiline_input(prompt_title: str, sentinel: str = "END") -> str:
    """Read multi-line input with full cursor movement support.

    Uses prompt_toolkit for rich editing experience with arrow keys.
    Falls back to sentinel mode if prompt_toolkit unavailable.
    """
    if PT_AVAILABLE:
        console.print(
            f"[bold cyan]{prompt_title}[/bold cyan]\n"
            "[dim]Multi-line editor - use arrow keys to navigate.[/dim]\n"
            "[dim]• ↑↓←→ to move cursor anywhere[/dim]\n"
            "[dim]• [bold]Ctrl+D[/bold] or [bold]Esc Enter[/bold] to finish[/dim]\n"
        )

        try:
            kb = KeyBindings()

            # Ctrl+D to finish
            @kb.add("c-d")
            def _finish_ctrl_d(event):  # type: ignore
                event.app.exit(result=event.app.current_buffer.text)

            # Esc then Enter to finish (alternative)
            @kb.add("escape", "enter")
            def _finish_esc_enter(event):  # type: ignore
                event.app.exit(result=event.app.current_buffer.text)

            session = PromptSession(
                multiline=True,
                key_bindings=kb,
                wrap_lines=True,  # Wrap long lines for better display
            )

            text = session.prompt("")  # type: ignore

            if text:
                text = _sanitize_text(text)
                text = _cleanup_pasted_text(text)
                return text
            return ""

        except KeyboardInterrupt:
            console.print("\n[yellow]Input cancelled[/yellow]")
            raise typer.Exit(0)
        except Exception as e:
            # If prompt_toolkit fails, show error and fall back
            console.print(f"\n[yellow]⚠️  Editor error: {e}[/yellow]")
            console.print("[yellow]Falling back to basic input mode...[/yellow]\n")
            # Fall through to sentinel mode below

    # Sentinel-based fallback
    if not PT_AVAILABLE:
        console.print(
            "[yellow]⚠️  Full arrow key support unavailable[/yellow]\n"
            "[yellow]   Install with: pip install prompt_toolkit[/yellow]\n"
        )

    instruction = (
        f"[bold cyan]{prompt_title}[/bold cyan]\n"
        f"[dim]Type or paste text. Type [bold]{sentinel}[/bold] on its own line when finished.[/dim]\n"
        f"[dim]Note: Arrow keys only work on current line in this mode.[/dim]\n"
    )
    console.print(instruction)

    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        except KeyboardInterrupt:
            console.print("\n[yellow]Input cancelled[/yellow]")
            raise typer.Exit(0)
        if line.strip() == sentinel:
            break
        lines.append(line)

    text = "\n".join(lines)
    text = _sanitize_text(text)
    text = _cleanup_pasted_text(text)
    return text


def add_quote(
    text: str = typer.Option(None, "--text", "-t", help="Quote text"),
    editor: bool = typer.Option(
        False,
        "--editor",
        help="Open $EDITOR for entering the quote text (set EDITOR; fallback to nano)",
    ),
    author: str = typer.Option(None, "--author", "-a", help="Quote author"),
    source: str = typer.Option(None, "--source", "-s", help="Quote source"),
    note: str = typer.Option(None, "--note", "-n", help="Personal note"),
    categories: str = typer.Option(
        None, "--categories", "-c", help="Comma-separated categories"
    ),
    skip_ai: bool = typer.Option(
        False, "--skip-ai", help="Skip AI features (author lookup, duplicates, etc.)"
    ),
    theme: str = typer.Option(
        None, "--theme", help="Color theme: auto, dark, light, high-contrast, none"
    ),
):
    """
    Add a new quote to your collection.

    Features AI-powered author identification, duplicate detection, and category suggestions.
    Use --skip-ai to disable AI features.

    If you provide --text, other fields default to empty if not specified.
    If you don't provide --text, you'll be prompted interactively for all fields.
    """
    # Set theme if provided
    if theme:
        set_theme(theme)

    # Determine if we're in interactive mode (no text provided)
    interactive_mode = text is None

    # Initialize AI metadata
    ai_metadata = AIMetadata()
    ai_available = is_api_available() and not skip_ai

    if interactive_mode:
        # Full interactive mode
        console.print("\n[bold cyan]Add a New Quote[/bold cyan]\n")
        # Choose best input method: editor > prompt_toolkit > sentinel mode
        use_editor = editor or _truthy(os.environ.get("QUOTES_USE_EDITOR"))
        if use_editor:
            console.print(
                "[dim]Opening your editor for quote text (set EDITOR to change).[/dim]"
            )
            text = _edit_in_editor("")
        else:
            # Support multi-line paste/input with explicit END sentinel or prompt_toolkit
            text = _read_multiline_input("Quote text (multi-line supported)")

        if not text.strip():
            display_warning("Quote text cannot be empty")
            raise typer.Exit(1)

        author_input = Prompt.ask("Author (or press Enter if unknown)", default="")
        source = Prompt.ask("Where did you see this? (optional)", default="")
        note = Prompt.ask("Why did this resonate with you? (optional)", default="")

        # Sanitize auxiliary fields
        author_input = _sanitize_text(author_input)
        source = _sanitize_text(source)
        note = _sanitize_text(note)

        # AI Processing Phase
        if ai_available:
            console.print()

            # Store results to display after processing
            author_result = None
            similar_quotes = []
            cat_result = None

            with console.status("🤔 Analyzing quote..."):
                # 1. Author identification (if not provided)
                if not author_input or author_input.strip() == "":
                    try:
                        author_result = identify_author_enhanced(text.strip())
                        author = author_result["author"]
                        ai_metadata.author_confidence = author_result["confidence"]
                    except Exception as e:
                        author_result = {
                            "error": str(e),
                            "author": "Anonymous",
                            "confidence": 0.0,
                        }
                        author = "Anonymous"
                else:
                    author = author_input.strip()

                # 2. Duplicate detection
                existing_quotes = load_quotes()
                existing_quote_dicts = [q.to_dict() for q in existing_quotes]

                try:
                    similar_quotes = check_duplicates(
                        text.strip(), existing_quote_dicts
                    )
                    ai_metadata.duplicate_check_date = datetime.utcnow().isoformat()
                except Exception as e:
                    console.print(f"\n[yellow]Duplicate detection error: {e}[/yellow]")
                    similar_quotes = []

                # 3. Category suggestion
                try:
                    cat_result = suggest_categories(text.strip())
                    ai_metadata.suggested_categories = cat_result["suggested"]
                    ai_metadata.category_confidence = cat_result["confidence"]
                except Exception:
                    cat_result = None

            # Now display results AFTER status completes
            console.print()

            # Display author identification results
            if author_result:
                if "error" in author_result:
                    console.print(
                        f"[yellow]⚠️  Author identification unavailable: {author_result['error']}[/yellow]"
                    )
                elif author != "Anonymous":
                    console.print(
                        f"[green]✓ Author identified:[/green] [bold]{author}[/bold] (confidence: {author_result['confidence']:.0%})"
                    )
                    if author_result.get("source"):
                        console.print(
                            f"  [dim]Source info: {author_result['source']}[/dim]"
                        )
                else:
                    console.print(
                        "[yellow]○ Could not identify author[/yellow] [dim](using Anonymous)[/dim]"
                    )

            # Display duplicate detection results
            if similar_quotes:
                # Show similar quotes
                console.print()
                for similar in similar_quotes[:3]:  # Show top 3
                    sim_quote = similar["quote"]
                    similarity = similar["similarity"]
                    level = get_similarity_level(similarity)

                    console.print(
                        Panel(
                            f"[yellow]⚠️  Similar quote found ({similarity:.0%} match - {level})[/yellow]\n\n"
                            f"Existing quote:\n"
                            f'"{sim_quote["text"]}"\n'
                            f'— {sim_quote["author"]}\n\n'
                            f"Your quote:\n"
                            f'"{text.strip()}"\n'
                            f"— {author}\n\n"
                            f'[dim]{similar["reason"]}[/dim]',
                            border_style="yellow",
                        )
                    )

                    # Ask what to do
                    console.print("\nOptions:")
                    console.print(
                        "  [yellow]e[/yellow] - Edit the existing quote (recommended)"
                    )
                    console.print("  [yellow]n[/yellow] - Add as new quote anyway")
                    console.print("  [yellow]c[/yellow] - Cancel")

                    choice = Prompt.ask(
                        "Choice", choices=["e", "n", "c"], default="e"
                    ).lower()

                    if choice == "c":
                        console.print("\n[yellow]Cancelled[/yellow]")
                        return
                    elif choice == "e":
                        # Guide user to edit command
                        quote_id_short = sim_quote["id"][:8]
                        console.print("\n[cyan]To edit the existing quote, run:[/cyan]")
                        console.print(f"  [bold]quotes edit {quote_id_short}[/bold]")
                        console.print(
                            "\n[dim]The edit command provides full multiline support with arrow keys.[/dim]"
                        )
                        return
                    else:
                        # Continue with adding new quote
                        break
            else:
                console.print("[green]✓ No duplicates found[/green]")

            # Display category suggestion results
            if cat_result:
                suggested_cats = cat_result["suggested"]
                console.print()
                console.print(
                    f"[green]✓ Suggested categories:[/green] [cyan]{', '.join(suggested_cats)}[/cyan] [dim](confidence: {cat_result['confidence']:.0%})[/dim]"
                )
                console.print(f"  [dim]{cat_result['reasoning']}[/dim]")
            else:
                suggested_cats = []

        else:
            # No AI available
            author = author_input.strip() if author_input else "Anonymous"
            suggested_cats = []
            if not skip_ai:
                console.print(
                    "\n[yellow]AI features unavailable (no API key configured)[/yellow]"
                )

        # Use interactive category selector with AI suggestions pre-selected
        if ai_available and (author_result or similar_quotes or cat_result):
            console.print()
            Prompt.ask("[dim]Press Enter to select categories[/dim]", default="")
        else:
            console.print()

        category_list = select_categories(
            preselected=suggested_cats,
            ai_suggested=bool(suggested_cats and ai_available),
        )

    else:
        # Non-interactive mode with defaults
        text = _sanitize_text(text)
        if not text.strip():
            display_warning("Quote text cannot be empty")
            raise typer.Exit(1)

        # Use defaults for unspecified fields
        author = author if author is not None else "Anonymous"
        source = source if source is not None else ""
        note = note if note is not None else ""
        # Sanitize provided fields
        author = _sanitize_text(author)
        source = _sanitize_text(source)
        note = _sanitize_text(note)
        category_list = (
            [c.strip() for c in categories.split(",") if c.strip()]
            if categories
            else []
        )

        # In non-interactive mode, still do AI author lookup if no author provided
        if ai_available and author == "Anonymous":
            try:
                author_result = identify_author_enhanced(text.strip())
                if author_result["author"] != "Anonymous":
                    author = author_result["author"]
                    ai_metadata.author_confidence = author_result["confidence"]
            except Exception:
                pass  # Silently fail in non-interactive mode

    # Create quote object
    quote = Quote(
        text=_sanitize_text(text).strip(),
        author=_sanitize_text(author).strip() if author else "Anonymous",
        source=_sanitize_text(source).strip() if source else "",
        personal_note=_sanitize_text(note).strip() if note else "",
        categories=category_list,
        ai_metadata=ai_metadata,
    )

    # Save to storage
    quotes = load_quotes()
    quotes.append(quote)
    save_quotes(quotes)

    # Show success message
    console.print()
    display_success(f"Quote saved! (ID: {quote.id[:8]})")

    # Show summary
    console.print(f'\n"{quote.text}"', style="cyan")
    console.print(f"— {quote.author}", style="dim white")
    if quote.categories:
        console.print(f"Categories: {', '.join(quote.categories)}", style="blue")
