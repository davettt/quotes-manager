"""Author identification using Claude AI with web search fallback."""

from typing import Any, Dict

import requests
from bs4 import BeautifulSoup
from rich.console import Console

from ai.claude_client import get_client, is_api_available
from utils.storage import load_config

console = Console()

# Web search timeout in seconds
WEB_SEARCH_TIMEOUT = 5


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
            - method: 'claude' (always for this function)

    Raises:
        Exception: If AI is unavailable or request fails
    """
    if not is_api_available():
        raise ValueError("Claude API key not configured")

    client = get_client()

    prompt = f"""Who said this quote? If you're confident (>70% sure), provide the author's name.
If you're unsure or don't know, respond with "Anonymous".

Quote: \"\"\"{quote_text}\"\"\"

Respond with ONLY a JSON object in this exact format:
{{
    "author": "Author Name or Anonymous",
    "confidence": 0.95,
    "source": "Where it was said (if known), or empty string"
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

        # If confidence is too low, don't force to Anonymous here
        # Let the enhanced function decide based on web search
        if confidence > 1.0:
            confidence = 1.0
        elif confidence < 0.0:
            confidence = 0.0

        return {
            "author": author,
            "confidence": confidence,
            "source": response.get("source", ""),
            "method": "claude",
        }

    except Exception as e:
        console.print(f"[yellow]Author identification failed: {e}[/yellow]")
        # Return fallback
        return {
            "author": "Anonymous",
            "confidence": 0.0,
            "source": "",
            "method": "claude",
        }


def search_web_for_author(quote_text: str) -> Dict[str, Any]:
    """
    Search DuckDuckGo for quote author using web scraping.

    Args:
        quote_text: The text of the quote to search for

    Returns:
        Dictionary with:
            - author: Author name if found
            - confidence: Confidence score (0.0-1.0)
            - source: Source URL or description
            - method: 'web_search'
            - found: Boolean indicating if author was found
    """
    try:
        # Use DuckDuckGo HTML search
        # Prepare search query - use first 50 chars of quote for better results
        search_query = quote_text[:50].strip() + " author"

        # DuckDuckGo search
        url = "https://html.duckduckgo.com/"
        params = {
            "q": search_query,
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(
            url, params=params, headers=headers, timeout=WEB_SEARCH_TIMEOUT
        )
        response.raise_for_status()

        # Parse HTML results
        soup = BeautifulSoup(response.content, "html.parser")

        # Look for results
        results = soup.find_all("div", {"class": "result"})

        if not results:
            return {
                "author": "Anonymous",
                "confidence": 0.0,
                "source": "",
                "method": "web_search",
                "found": False,
            }

        # Extract text from first few results
        for result in results[:3]:
            text = result.get_text()

            # Look for common author indicators in result text
            if any(
                indicator in text.lower()
                for indicator in [" by ", " - ", "author:", "said by", "quote from"]
            ):
                # Try to extract author name
                # This is a simple heuristic - look for names after common indicators
                if " by " in text.lower():
                    parts = text.lower().split(" by ")
                    if len(parts) > 1:
                        author_candidate = parts[1].split("\n")[0].strip()
                        if len(author_candidate) < 100:  # Sanity check
                            return {
                                "author": author_candidate.title(),
                                "confidence": 0.65,
                                "source": (
                                    result.find("a", {"class": "result__url"}).get_text(
                                        strip=True
                                    )
                                    if result.find("a", {"class": "result__url"})
                                    else ""
                                ),
                                "method": "web_search",
                                "found": True,
                            }

        # Check if we found any quote-related results
        full_text = " ".join([r.get_text() for r in results[:3]])
        if "quote" in full_text.lower() or "said" in full_text.lower():
            # We found quote context but couldn't parse author
            return {
                "author": "Anonymous",
                "confidence": 0.3,
                "source": "",
                "method": "web_search",
                "found": False,
            }

        return {
            "author": "Anonymous",
            "confidence": 0.0,
            "source": "",
            "method": "web_search",
            "found": False,
        }

    except requests.Timeout:
        console.print("[yellow]⚠ Web search timed out[/yellow]")
        return {
            "author": "Anonymous",
            "confidence": 0.0,
            "source": "",
            "method": "web_search",
            "found": False,
        }
    except requests.ConnectionError:
        console.print("[yellow]⚠ No internet connection[/yellow]")
        return {
            "author": "Anonymous",
            "confidence": 0.0,
            "source": "",
            "method": "web_search",
            "found": False,
        }
    except Exception as e:
        console.print(f"[yellow]⚠ Web search failed: {e}[/yellow]")
        return {
            "author": "Anonymous",
            "confidence": 0.0,
            "source": "",
            "method": "web_search",
            "found": False,
        }


def identify_author_enhanced(quote_text: str) -> Dict[str, Any]:
    """
    Enhanced author identification with web search fallback.

    Two-tier approach:
    1. Try Claude's knowledge first (fast, free)
    2. If Claude is uncertain (<70%), fall back to web search

    Args:
        quote_text: The text of the quote to identify

    Returns:
        Dictionary with:
            - author: Author name or "Anonymous"
            - confidence: Confidence score (0.0-1.0)
            - source: Optional source information
            - method: 'claude', 'web_search', or 'unknown'
    """
    # Step 1: Try Claude's knowledge first (fast, free)
    claude_result = identify_author(quote_text)

    # If Claude is confident, return immediately
    if claude_result["confidence"] >= 0.7:
        console.print(
            f"[green]✓ Author identified: {claude_result['author']} "
            f"(confidence: {int(claude_result['confidence'] * 100)}%)[/green]"
        )
        return claude_result

    # Step 2: Check if web search is enabled
    try:
        config = load_config()
        enable_web_search = config.get("preferences", {}).get(
            "enable_web_search_author", True
        )
        if not enable_web_search:
            # Web search disabled, return Claude's best guess
            if claude_result["confidence"] > 0:
                return claude_result
            else:
                return {
                    "author": "Anonymous",
                    "confidence": 0.0,
                    "source": "",
                    "method": "unknown",
                }
    except Exception:
        # If config loading fails, assume web search is enabled
        enable_web_search = True

    # Step 3: Fallback to web search if enabled
    if enable_web_search:
        console.print("[dim]Searching web for author...[/dim]")
        try:
            search_result = search_web_for_author(quote_text)
            if search_result.get("found") and search_result["confidence"] >= 0.5:
                console.print(f"[green]✓ Author found: {search_result['author']}")
                return search_result
        except Exception as e:
            console.print(f"[yellow]Web search failed: {e}[/yellow]")
            # Fall through to return Claude's result or Anonymous

    # Step 4: Still unknown - return best guess or Anonymous
    if claude_result["confidence"] > 0:
        return claude_result

    return {
        "author": "Anonymous",
        "confidence": 0.0,
        "source": "",
        "method": "unknown",
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
        result = identify_author_enhanced(quote_text)
        return result.get("author", "Anonymous")
    except Exception:
        return "Anonymous"
