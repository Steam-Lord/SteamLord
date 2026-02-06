"""HTTP client helper for SteamLord backend.

This module provides a shared httpx.Client instance for general HTTP requests.
For GitHub API calls, use royal_gateway.py instead.
"""

from __future__ import annotations

from typing import Optional

import httpx

from kingdom_config import HTTP_TIMEOUT_SECONDS

_CLIENT: Optional[httpx.Client] = None


def get_http_client() -> httpx.Client:
    """Get or create the shared HTTP client for general requests."""
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = httpx.Client(timeout=HTTP_TIMEOUT_SECONDS)
    return _CLIENT


def close_http_client() -> None:
    """Close the shared HTTP client."""
    global _CLIENT
    if _CLIENT is not None:
        try:
            _CLIENT.close()
        except Exception:
            pass
        _CLIENT = None


__all__ = [
    "get_http_client",
    "close_http_client",
]
