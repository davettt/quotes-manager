"""Quote explanation using Claude AI."""

from typing import Dict

from rich.console import Console

from ai.claude_client import get_client, is_api_available

console = Console()


def explain_quote(quote_dict: Dict) -> str:
    """
    Generate a deep, meaningful explanation of a quote.

    Args:
        quote_dict: Dictionary containing quote data (text, author, personal_note, etc.)

    Returns:
        Formatted explanation text (200-400 words)

    Raises:
        Exception: If AI is unavailable or request fails
    """
    if not is_api_available():
        raise ValueError("Claude API key not configured")

    client = get_client()

    # Build context
    quote_text = quote_dict.get("text", "")
    author = quote_dict.get("author", "Anonymous")
    personal_note = quote_dict.get("personal_note", "")
    source = quote_dict.get("source", "")

    # Create prompt for deep explanation
    prompt = f"""Provide a thoughtful, insightful explanation of this quote.

Quote: \"\"\"{quote_text}\"\"\"
Author: {author}"""

    if source:
        prompt += f'\nSource: """{source}"""'

    if personal_note:
        prompt += f'\nContext: """{personal_note}"""'

    prompt += """

In 200-400 words, provide a deep, meaningful explanation that covers:

1. **Core Meaning**: What is the author really saying? What's the deeper message beyond the literal words?

2. **Context & Background**: Who said this and why? What circumstances or philosophy led to this insight?

3. **Practical Application**: How can someone apply this wisdom to their life? What specific situations does this apply to?

4. **Why It Matters**: Why is this quote significant or worth remembering?

Write in a conversational, accessible style. Be insightful and thought-provoking, not just descriptive. Help the reader gain a deeper understanding and appreciation of the quote's wisdom.

Do NOT just summarize or paraphrase the quote. Provide genuine insight and practical value."""

    try:
        response = client.complete(prompt, max_tokens=800)
        return response.strip()

    except Exception as e:
        console.print(f"[yellow]Quote explanation failed: {e}[/yellow]")
        raise


def explain_quote_safe(quote_dict: Dict) -> str:
    """
    Safely explain a quote with fallback message.

    This is a convenience wrapper that never raises exceptions.

    Args:
        quote_dict: Dictionary containing quote data

    Returns:
        Explanation text or error message
    """
    try:
        return explain_quote(quote_dict)
    except Exception as e:
        return f"Unable to generate explanation: {e}"
