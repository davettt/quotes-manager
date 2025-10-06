"""Author identification using Claude AI."""

from typing import Dict, Any
from rich.console import Console
from ai.claude_client import get_client, is_api_available

console = Console()


def identify_author(quote_text: str) -> Dict[str, Any]:
    """
    Attempt to identify the quote's author using Claude AI.

    Args:
        quote_text: The text of the quote to identify

    Returns:
        Dictionary with:
            - author: Author name or "Anonymous"
            - confidence: Confidence score (0.0-1.0)
            - source: Optional source information if known
            - reasoning: Brief explanation

    Raises:
        Exception: If AI is unavailable or request fails
    """
    if not is_api_available():
        raise ValueError("Claude API key not configured")

    client = get_client()

    prompt = f"""Who said this quote? If you're confident (>70% sure), provide the author's name.
If you're unsure or don't know, respond with "Anonymous".

Quote: "{quote_text}"

Respond with ONLY a JSON object in this exact format:
{{
    "author": "Author Name or Anonymous",
    "confidence": 0.95,
    "source": "Where it was said (if known), or empty string",
    "reasoning": "brief explanation of your identification"
}}

DO NOT include any text outside the JSON object.
Be honest about your confidence level - if you're not sure, use "Anonymous" and a low confidence score."""

    try:
        response = client.complete_json(prompt, max_tokens=500)

        # Validate response structure
        if not isinstance(response.get("author"), str):
            raise ValueError("Response missing 'author' string")
        if not isinstance(response.get("confidence"), (int, float)):
            raise ValueError("Response missing 'confidence' score")

        author = response["author"].strip()
        confidence = float(response["confidence"])

        # If confidence is too low, use Anonymous
        if confidence < 0.7:
            author = "Anonymous"
            confidence = 0.0

        return {
            "author": author,
            "confidence": confidence,
            "source": response.get("source", ""),
            "reasoning": response.get("reasoning", ""),
        }

    except Exception as e:
        console.print(f"[yellow]Author identification failed: {e}[/yellow]")
        # Return fallback
        return {
            "author": "Anonymous",
            "confidence": 0.0,
            "source": "",
            "reasoning": "AI unavailable",
        }


def identify_author_safe(quote_text: str) -> str:
    """
    Safely identify author with fallback to "Anonymous".

    This is a convenience wrapper that never raises exceptions.

    Args:
        quote_text: The text of the quote to identify

    Returns:
        Author name or "Anonymous" if identification fails
    """
    try:
        result = identify_author(quote_text)
        return result.get("author", "Anonymous")
    except Exception:
        return "Anonymous"
