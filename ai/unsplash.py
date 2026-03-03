"""Unsplash API client for fetching background photos."""

import os
import random
import tempfile
from dataclasses import dataclass
from typing import Optional

import requests  # type: ignore[import-untyped]
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_API_BASE = "https://api.unsplash.com"
_APP_NAME = "quotes-manager"

# Map image ratio → Unsplash orientation filter
_RATIO_TO_ORIENTATION: dict = {
    "square": "squarish",
    "portrait": "portrait",
    "landscape": "landscape",
    "mobile": "portrait",
    "tablet": "portrait",
}


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class PhotoResult:
    """A downloaded background photo and its attribution data."""

    temp_path: str
    photographer: str
    photographer_url: str
    photo_url: str
    photo_id: str


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_access_key() -> Optional[str]:
    """Return the Unsplash access key from the environment, or None if unset."""
    load_dotenv()
    key = os.getenv("UNSPLASH_ACCESS_KEY", "").strip()
    if key and key != "your_unsplash_access_key_here":
        return key
    return None


def _trigger_download(photo_id: str, key: str, timeout: int) -> None:
    """
    Notify Unsplash that a photo was used (required by API guidelines).
    Fires-and-forgets — any failure is silently ignored.
    """
    try:
        requests.get(
            f"{_API_BASE}/photos/{photo_id}/download",
            headers={"Authorization": f"Client-ID {key}"},
            timeout=timeout,
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def is_available() -> bool:
    """Return True if an Unsplash access key is configured."""
    return _get_access_key() is not None


def fetch_background_photo(
    query: str,
    ratio: str = "square",
    timeout: int = 15,
) -> Optional[PhotoResult]:
    """
    Search Unsplash for a photo matching *query* and download it to a temp file.

    Args:
        query:   Search term (typically the quote's primary category).
        ratio:   Image ratio key — used to filter by orientation.
        timeout: Request timeout in seconds.

    Returns:
        PhotoResult with temp file path and attribution data, or None on any
        failure (missing key, network error, no results, etc.).
    """
    key = _get_access_key()
    if not key:
        return None

    orientation = _RATIO_TO_ORIENTATION.get(ratio, "squarish")

    try:
        # Search for photos
        resp = requests.get(
            f"{_API_BASE}/search/photos",
            headers={"Authorization": f"Client-ID {key}"},
            params={
                "query": query,
                "per_page": 20,
                "orientation": orientation,
                "content_filter": "high",
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])

        if not results:
            return None

        # Pick a random photo from the top results
        photo = random.choice(results)
        photo_id = photo["id"]

        # Use the full-resolution URL for best quality across all canvas sizes
        download_url = photo["urls"]["full"]
        dl_resp = requests.get(download_url, timeout=30, stream=True)
        dl_resp.raise_for_status()

        # Stream to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            for chunk in dl_resp.iter_content(chunk_size=8192):
                tmp.write(chunk)
            temp_path = tmp.name

        # Notify Unsplash of download (API guidelines requirement)
        _trigger_download(photo_id, key, timeout)

        utm = f"?utm_source={_APP_NAME}&utm_medium=referral"
        return PhotoResult(
            temp_path=temp_path,
            photographer=photo["user"]["name"],
            photographer_url=photo["user"]["links"]["html"] + utm,
            photo_url=photo["links"]["html"] + utm,
            photo_id=photo_id,
        )

    except Exception:
        return None


def cleanup_photo(photo: PhotoResult) -> None:
    """Delete the temporary photo file. Safe to call even if already deleted."""
    try:
        os.unlink(photo.temp_path)
    except OSError:
        pass


def format_attribution(photo: PhotoResult) -> str:
    """Return a formatted attribution string for terminal output."""
    return f"Photo by {photo.photographer} on Unsplash\n{photo.photographer_url}"


def format_credit(photo: PhotoResult) -> str:
    """Return a short credit string for embedding in the image."""
    return f"Photo by {photo.photographer} / Unsplash"
