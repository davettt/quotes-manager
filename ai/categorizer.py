"""Category suggestion using Claude AI."""

from typing import Dict, Any, List
from rich.console import Console
from ai.claude_client import get_client, is_api_available

console = Console()

# Predefined categories (same as in category_selector.py)
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


def suggest_categories(quote_text: str) -> Dict[str, Any]:
    """
    Analyze quote and suggest categories using Claude AI.

    Args:
        quote_text: The text of the quote to analyze

    Returns:
        Dictionary with:
            - suggested: List of 2-4 category names
            - confidence: Overall confidence score (0.0-1.0)
            - reasoning: Brief explanation of suggestions

    Raises:
        Exception: If AI is unavailable or request fails
    """
    if not is_api_available():
        raise ValueError("Claude API key not configured")

    client = get_client()

    prompt = f"""Analyze this quote and suggest 2-4 categories from the following list:

Categories: {", ".join(PREDEFINED_CATEGORIES)}

Quote: "{quote_text}"

Respond with ONLY a JSON object in this exact format:
{{
    "suggested": ["category1", "category2"],
    "confidence": 0.85,
    "reasoning": "brief explanation of why these categories fit"
}}

DO NOT include any text outside the JSON object.
ONLY use categories from the list provided above.
Suggest between 2 and 4 categories that best fit the quote's themes and message."""

    try:
        response = client.complete_json(prompt, max_tokens=500)

        # Validate response structure
        if not isinstance(response.get("suggested"), list):
            raise ValueError("Response missing 'suggested' list")
        if not isinstance(response.get("confidence"), (int, float)):
            raise ValueError("Response missing 'confidence' score")
        if not isinstance(response.get("reasoning"), str):
            raise ValueError("Response missing 'reasoning' string")

        # Filter to only valid predefined categories
        suggested = [
            cat for cat in response["suggested"] if cat in PREDEFINED_CATEGORIES
        ]

        # Ensure we have at least one suggestion
        if not suggested:
            suggested = ["inspiration"]  # Default fallback

        return {
            "suggested": suggested,
            "confidence": float(response["confidence"]),
            "reasoning": response["reasoning"],
        }

    except Exception as e:
        console.print(f"[yellow]Category suggestion failed: {e}[/yellow]")
        # Return fallback
        return {
            "suggested": ["inspiration"],
            "confidence": 0.0,
            "reasoning": "AI unavailable, using default",
        }


def suggest_categories_safe(quote_text: str) -> List[str]:
    """
    Safely suggest categories with fallback to empty list.

    This is a convenience wrapper that never raises exceptions.

    Args:
        quote_text: The text of the quote to analyze

    Returns:
        List of suggested category names, or empty list if AI fails
    """
    try:
        result = suggest_categories(quote_text)
        return result.get("suggested", [])
    except Exception:
        return []
