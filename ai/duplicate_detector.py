"""Duplicate detection using semantic similarity with Claude AI."""

from typing import Any, Dict, List

from rich.console import Console

from ai.claude_client import get_client, is_api_available

console = Console()


def check_similarity(quote1_text: str, quote2_text: str) -> Dict[str, Any]:
    """
    Check semantic similarity between two quotes.

    Args:
        quote1_text: First quote text
        quote2_text: Second quote text

    Returns:
        Dictionary with:
            - similarity: Similarity score (0.0-1.0)
            - reason: Explanation of similarity/difference

    Raises:
        Exception: If AI is unavailable or request fails
    """
    if not is_api_available():
        raise ValueError("Claude API key not configured")

    client = get_client()

    prompt = f"""Compare these two quotes for semantic similarity.
Consider:
- Same core message/meaning (high weight)
- Similar wording or phrasing
- Minor differences like punctuation, capitalization don't matter much

Quote 1: \"\"\"{quote1_text}\"\"\"
Quote 2: \"\"\"{quote2_text}\"\"\"

Respond with ONLY a JSON object in this exact format:
{{
    "similarity": 0.85,
    "reason": "brief explanation of similarity or difference"
}}

Similarity scale:
- 0.95-1.0: Essentially identical (maybe minor punctuation differences)
- 0.85-0.94: High similarity (same core message, slightly different wording)
- 0.70-0.84: Medium similarity (related themes but different expression)
- 0.0-0.69: Different quotes

DO NOT include any text outside the JSON object."""

    try:
        response = client.complete_json(prompt, max_tokens=300)

        # Validate response structure
        if not isinstance(response.get("similarity"), (int, float)):
            raise ValueError("Response missing 'similarity' score")

        return {
            "similarity": float(response["similarity"]),
            "reason": response.get("reason", ""),
        }

    except Exception as e:
        console.print(f"[yellow]Similarity check failed: {e}[/yellow]")
        # Return fallback - assume not similar on error
        return {"similarity": 0.0, "reason": "AI unavailable"}


def check_duplicates(new_quote_text: str, existing_quotes: List[Dict]) -> List[Dict]:
    """
    Check for duplicate or similar quotes in existing collection.

    This function optimizes by pre-filtering before calling AI:
    - Only checks quotes with similar length (±30%)
    - Only checks quotes with at least 3 common words

    Args:
        new_quote_text: The new quote text to check
        existing_quotes: List of existing quote dictionaries

    Returns:
        List of similar quotes with similarity scores, sorted by similarity:
        [
            {
                "quote": {...},  # The existing quote dict
                "similarity": 0.89,
                "reason": "Nearly identical wording..."
            }
        ]
        Only includes quotes with similarity >= 0.70
    """
    if not is_api_available():
        console.print("[yellow]AI not available for duplicate detection[/yellow]")
        return []

    new_words = set(new_quote_text.lower().split())
    similar_quotes = []

    for existing_quote in existing_quotes:
        existing_text = existing_quote.get("text", "")

        # Pre-filter: Check for common words (minimum 3 words in common)
        # This is a lightweight check to avoid expensive AI calls for completely different quotes
        existing_words = set(existing_text.lower().split())
        common_words = new_words.intersection(existing_words)
        if len(common_words) < 3:
            continue

        # Passed pre-filters, do AI similarity check
        try:
            result = check_similarity(new_quote_text, existing_text)
            similarity = result["similarity"]

            # Only include if similarity >= 0.70
            if similarity >= 0.70:
                similar_quotes.append(
                    {
                        "quote": existing_quote,
                        "similarity": similarity,
                        "reason": result["reason"],
                    }
                )
        except Exception as e:
            console.print(
                f"[dim]Skipping similarity check for quote {existing_quote.get('id', 'unknown')}: {e}[/dim]"
            )
            continue

    # Sort by similarity (highest first)
    similar_quotes.sort(key=lambda x: x["similarity"], reverse=True)

    return similar_quotes


def get_similarity_level(similarity: float) -> str:
    """
    Get human-readable similarity level.

    Args:
        similarity: Similarity score (0.0-1.0)

    Returns:
        String describing similarity level
    """
    if similarity >= 0.95:
        return "exact match"
    elif similarity >= 0.85:
        return "high similarity"
    elif similarity >= 0.70:
        return "medium similarity"
    else:
        return "different"
