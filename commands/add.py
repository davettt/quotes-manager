"""Add quote command implementation."""

from datetime import datetime

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from ai.author_identifier import identify_author
from ai.categorizer import suggest_categories
from ai.claude_client import is_api_available
from ai.duplicate_detector import check_duplicates, get_similarity_level
from models.quote import AIMetadata, Quote
from utils.category_selector import select_categories
from utils.display import display_success, display_warning, set_theme
from utils.storage import load_quotes, save_quotes

console = Console()


def add_quote(
    text: str = typer.Option(None, "--text", "-t", help="Quote text"),
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
        text = Prompt.ask("Quote text")

        if not text.strip():
            display_warning("Quote text cannot be empty")
            raise typer.Exit(1)

        author_input = Prompt.ask("Author (or press Enter if unknown)", default="")
        source = Prompt.ask("Where did you see this? (optional)", default="")
        note = Prompt.ask("Why did this resonate with you? (optional)", default="")

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
                        author_result = identify_author(text.strip())
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
                    console.print("  [yellow]u[/yellow] - Update existing quote")
                    console.print("  [yellow]n[/yellow] - Add as new quote anyway")
                    console.print("  [yellow]c[/yellow] - Cancel")

                    choice = Prompt.ask(
                        "Choice", choices=["u", "n", "c"], default="n"
                    ).lower()

                    if choice == "c":
                        console.print("\n[yellow]Cancelled[/yellow]")
                        return
                    elif choice == "u":
                        # Update existing quote
                        existing_quote_obj = next(
                            q for q in existing_quotes if q.id == sim_quote["id"]
                        )
                        existing_quote_obj.text = text.strip()
                        existing_quote_obj.author = author
                        if source:
                            existing_quote_obj.source = source.strip()
                        if note:
                            existing_quote_obj.personal_note = note.strip()
                        save_quotes(existing_quotes)
                        console.print()
                        display_success(
                            f"Quote updated! (ID: {existing_quote_obj.id[:8]})"
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
        if not text.strip():
            display_warning("Quote text cannot be empty")
            raise typer.Exit(1)

        # Use defaults for unspecified fields
        author = author if author is not None else "Anonymous"
        source = source if source is not None else ""
        note = note if note is not None else ""
        category_list = (
            [c.strip() for c in categories.split(",") if c.strip()]
            if categories
            else []
        )

        # In non-interactive mode, still do AI author lookup if no author provided
        if ai_available and author == "Anonymous":
            try:
                author_result = identify_author(text.strip())
                if author_result["author"] != "Anonymous":
                    author = author_result["author"]
                    ai_metadata.author_confidence = author_result["confidence"]
            except Exception:
                pass  # Silently fail in non-interactive mode

    # Create quote object
    quote = Quote(
        text=text.strip(),
        author=author.strip() if author else "Anonymous",
        source=source.strip() if source else "",
        personal_note=note.strip() if note else "",
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
