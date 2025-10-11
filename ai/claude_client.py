"""Claude API client wrapper for quotes manager."""

import json
import os
from typing import Any, Dict, Optional

import anthropic
from dotenv import load_dotenv
from rich.console import Console

console = Console()

# Load environment variables
load_dotenv()


class ClaudeClient:
    """Wrapper for Claude API interactions."""

    def __init__(self):
        """Initialize Claude client with API key from environment."""
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment. "
                "Please set it in your .env file."
            )
        # Initialize client with only api_key (avoid passing unsupported kwargs)
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"

    def complete(
        self,
        prompt: str,
        max_tokens: int = 1000,
        system: Optional[str] = None,
    ) -> str:
        """
        Send completion request to Claude API.

        Args:
            prompt: The user prompt to send
            max_tokens: Maximum tokens in response
            system: Optional system prompt

        Returns:
            Response text from Claude

        Raises:
            Exception: If API call fails
        """
        try:
            message_params = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }

            if system:
                message_params["system"] = system

            response = self.client.messages.create(**message_params)

            # Extract text from response
            return response.content[0].text

        except anthropic.APIError as e:
            console.print(f"[red]Claude API error: {e}[/red]")
            raise
        except Exception as e:
            console.print(f"[red]Unexpected error calling Claude API: {e}[/red]")
            raise

    def complete_json(
        self,
        prompt: str,
        max_tokens: int = 1000,
        system: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send completion request expecting JSON response.

        Args:
            prompt: The user prompt to send
            max_tokens: Maximum tokens in response
            system: Optional system prompt

        Returns:
            Parsed JSON response as dictionary

        Raises:
            ValueError: If response is not valid JSON
            Exception: If API call fails
        """
        response_text = self.complete(prompt, max_tokens, system)

        try:
            # Try to parse the response as JSON
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            console.print(f"[red]Failed to parse JSON response: {e}[/red]")
            console.print(f"[dim]Response text: {response_text}[/dim]")
            raise ValueError(f"Invalid JSON response from Claude: {response_text}")


# Global client instance (initialized on first use)
_client: Optional[ClaudeClient] = None


def get_client() -> ClaudeClient:
    """
    Get or create the global Claude client instance.

    Returns:
        ClaudeClient instance

    Raises:
        ValueError: If ANTHROPIC_API_KEY not set
    """
    global _client
    if _client is None:
        _client = ClaudeClient()
    return _client


def is_api_available() -> bool:
    """
    Check if Claude API is available (API key is set).

    Returns:
        True if API key is set, False otherwise
    """
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    return (
        api_key is not None and api_key.strip() != "" and api_key != "your_api_key_here"
    )
