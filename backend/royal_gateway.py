"""Centralized Cloudflare API client for SteamLord backend.

All GitHub operations go through the Cloudflare Worker proxy.
This module provides a unified interface for all API calls.
API Token is obtained dynamically from the server (no static key!).
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

import httpx

from kingdom_config import (
    CLOUDFLARE_API_URL,
    HTTP_TIMEOUT_SECONDS,
    HTTP_DOWNLOAD_TIMEOUT_SECONDS,
    USER_AGENT,
)
from throne_logger import logger

# Shared HTTP client instance
_API_CLIENT: Optional[httpx.Client] = None


def _get_session_token() -> Optional[str]:
    """Get the current session token from royal_auth."""
    try:
        from royal_auth import get_session_token
        return get_session_token()
    except ImportError:
        return None


def _get_api_token() -> Optional[str]:
    """Get the current API token from royal_auth (auto-refreshes if needed)."""
    try:
        from royal_auth import get_api_token
        return get_api_token()
    except ImportError:
        return None


def _get_headers() -> Dict[str, str]:
    """Return headers required for API authentication."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    
    # Add API Token (server-generated, auto-refreshing)
    api_token = _get_api_token()
    if api_token:
        headers["X-API-Token"] = api_token
    
    # Add Session Token
    session_token = _get_session_token()
    if session_token:
        headers["X-Session-Token"] = session_token
    
    return headers


def get_api_client() -> httpx.Client:
    """Get or create the shared API client."""
    global _API_CLIENT
    if _API_CLIENT is None:
        _API_CLIENT = httpx.Client(timeout=HTTP_TIMEOUT_SECONDS)
    return _API_CLIENT


def close_api_client() -> None:
    """Close the shared API client."""
    global _API_CLIENT
    if _API_CLIENT is not None:
        try:
            _API_CLIENT.close()
        except Exception:
            pass
        _API_CLIENT = None


# ═══════════════════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════════════════


def api_health_check() -> Dict[str, Any]:
    """Check if the API is healthy."""
    try:
        client = get_api_client()
        resp = client.get(f"{CLOUDFLARE_API_URL}/health", headers=_get_headers())
        return resp.json()
    except Exception as exc:
        logger.warn(f"API health check failed: {exc}")
        return {"status": "error", "error": str(exc)}


def check_game_exists(appid: int) -> bool:
    """Check if a game exists in the main repository."""
    try:
        client = get_api_client()
        resp = client.get(
            f"{CLOUDFLARE_API_URL}/check-exists/{appid}",
            headers=_get_headers(),
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("exists", False)
        return False
    except Exception as exc:
        logger.warn(f"API check_game_exists failed for {appid}: {exc}")
        return False


def check_fix_exists(appid: int) -> bool:
    """Check if a fix exists for the game."""
    try:
        client = get_api_client()
        resp = client.get(
            f"{CLOUDFLARE_API_URL}/check-fix/{appid}",
            headers=_get_headers(),
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("exists", False)
        return False
    except Exception as exc:
        logger.warn(f"API check_fix_exists failed for {appid}: {exc}")
        return False


def check_bypass_exists(appid: int) -> bool:
    """Check if a bypass exists for the game."""
    try:
        client = get_api_client()
        resp = client.get(
            f"{CLOUDFLARE_API_URL}/check-bypass/{appid}",
            headers=_get_headers(),
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("exists", False)
        return False
    except Exception as exc:
        logger.warn(f"API check_bypass_exists failed for {appid}: {exc}")
        return False


def download_game_zip(appid: int, dest_path: str, progress_callback=None) -> Tuple[bool, str]:
    """
    Download a game zip file.
    
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        client = get_api_client()
        url = f"{CLOUDFLARE_API_URL}/download/{appid}"
        
        with client.stream("GET", url, headers=_get_headers(), timeout=HTTP_DOWNLOAD_TIMEOUT_SECONDS) as resp:
            if resp.status_code == 404:
                # Read body for JSON parsing (stream doesn't auto-read)
                try:
                    resp.read()
                    error_data = resp.json()
                    return False, error_data.get("error", "Unknown Error")
                except:
                    # Generic error fallback
                    return False, "Game Not Added Yet: Will Be Added Soon"
            if resp.status_code != 200:
                # Read body for JSON parsing (stream doesn't auto-read)
                try:
                    resp.read()
                    error_data = resp.json()
                    return False, error_data.get("error", f"Download failed with status {resp.status_code}")
                except:
                    return False, f"Download failed with status {resp.status_code}"
            
            total_content_length = int(resp.headers.get("content-length", 0))
            total_bytes = 0
            with open(dest_path, "wb") as f:
                for chunk in resp.iter_bytes():
                    if chunk:
                        f.write(chunk)
                        total_bytes += len(chunk)
                        if progress_callback:
                            progress_callback(total_bytes, total_content_length)
        
        return True, ""
    except Exception as exc:
        logger.warn(f"API download_game_zip failed for {appid}: {exc}")
        return False, str(exc)


def download_game_json(appid: int) -> Optional[Dict[str, Any]]:
    """Download the game JSON metadata."""
    try:
        client = get_api_client()
        resp = client.get(
            f"{CLOUDFLARE_API_URL}/json/{appid}",
            headers=_get_headers(),
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception as exc:
        logger.warn(f"API download_game_json failed for {appid}: {exc}")
        return None


def download_fix_zip(appid: int, dest_path: str, progress_callback=None) -> Tuple[bool, str]:
    """
    Download a fix zip file.
    
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        client = get_api_client()
        url = f"{CLOUDFLARE_API_URL}/fix/{appid}"
        
        with client.stream("GET", url, headers=_get_headers(), timeout=HTTP_DOWNLOAD_TIMEOUT_SECONDS) as resp:
            if resp.status_code == 404:
                try:
                    resp.read()
                    error_data = resp.json()
                    return False, error_data.get("error", "Fix not found for this game")
                except:
                    return False, "Fix not found for this game"
            if resp.status_code != 200:
                try:
                    resp.read()
                    error_data = resp.json()
                    return False, error_data.get("error", f"Download failed with status {resp.status_code}")
                except:
                    return False, f"Download failed with status {resp.status_code}"
            
            total_content_length = int(resp.headers.get("content-length", 0))
            total_bytes = 0
            
            with open(dest_path, "wb") as f:
                for chunk in resp.iter_bytes():
                    if chunk:
                        f.write(chunk)
                        total_bytes += len(chunk)
                        if progress_callback:
                            progress_callback(total_bytes, total_content_length)
        
        return True, ""
    except Exception as exc:
        logger.warn(f"API download_fix_zip failed for {appid}: {exc}")
        return False, str(exc)


def download_bypass_zip(appid: int, dest_path: str, progress_callback=None) -> Tuple[bool, str]:
    """
    Download a bypass zip file.
    
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        client = get_api_client()
        url = f"{CLOUDFLARE_API_URL}/bypass/{appid}"
        
        with client.stream("GET", url, headers=_get_headers(), timeout=HTTP_DOWNLOAD_TIMEOUT_SECONDS) as resp:
            if resp.status_code == 404:
                try:
                    resp.read()
                    error_data = resp.json()
                    return False, error_data.get("error", "Bypass not found for this game")
                except:
                    return False, "Bypass not found for this game"
            if resp.status_code != 200:
                try:
                    resp.read()
                    error_data = resp.json()
                    return False, error_data.get("error", f"Download failed with status {resp.status_code}")
                except:
                    return False, f"Download failed with status {resp.status_code}"
            
            total_content_length = int(resp.headers.get("content-length", 0))
            total_bytes = 0
            with open(dest_path, "wb") as f:
                for chunk in resp.iter_bytes():
                    if chunk:
                        f.write(chunk)
                        total_bytes += len(chunk)
                        if progress_callback:
                            progress_callback(total_bytes, total_content_length)
        
        return True, ""
    except Exception as exc:
        logger.warn(f"API download_bypass_zip failed for {appid}: {exc}")
        return False, str(exc)


def download_bypass_status_json(dest_path: str) -> Tuple[bool, str]:
    """
    Download BypassStatus.json from API.
    This file contains simplified game info (name, work_on, launcher) for all bypasses.
    
    Args:
        dest_path: Where to save the BypassStatus.json file.
    
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        client = get_api_client()
        url = f"{CLOUDFLARE_API_URL}/bypass/status"
        
        resp = client.get(url, headers=_get_headers(), timeout=HTTP_TIMEOUT_SECONDS)
        
        if resp.status_code == 200:
            # Save the JSON file
            with open(dest_path, "wb") as f:
                f.write(resp.content)
            return True, ""
        else:
            try:
                error_data = resp.json()
                return False, error_data.get("error", f"Download failed with status {resp.status_code}")
            except:
                return False, f"Download failed with status {resp.status_code}"
    except Exception as exc:
        logger.warn(f"API download_bypass_status_json failed: {exc}")
        return False, str(exc)


def download_guard_file(dest_path: str) -> Tuple[bool, str]:
    """
    Download the guard file (xinput1_4.dll) from API.
    Requires valid session.
    
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        client = get_api_client()
        url = f"{CLOUDFLARE_API_URL}/guard/download"
        
        with client.stream("GET", url, headers=_get_headers(), timeout=HTTP_DOWNLOAD_TIMEOUT_SECONDS) as resp:
            if resp.status_code == 404:
                try:
                    resp.read()
                    error_data = resp.json()
                    return False, error_data.get("error", "Guard file not found")
                except:
                    return False, "Guard file not found"
            if resp.status_code != 200:
                try:
                    resp.read()
                    error_data = resp.json()
                    return False, error_data.get("error", f"Download failed with status {resp.status_code}")
                except:
                    return False, f"Download failed with status {resp.status_code}"
            
            with open(dest_path, "wb") as f:
                for chunk in resp.iter_bytes():
                    if chunk:
                        f.write(chunk)
        
        return True, ""
    except Exception as exc:
        logger.warn(f"API download_guard_file failed: {exc}")
        return False, str(exc)


def get_latest_update() -> Optional[Dict[str, Any]]:
    """
    Get information about the latest plugin update.
    
    Returns:
        Dict with 'version' and 'assets' keys, or None on error.
    """
    try:
        client = get_api_client()
        resp = client.get(
            f"{CLOUDFLARE_API_URL}/update/latest",
            headers=_get_headers(),
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception as exc:
        logger.warn(f"API get_latest_update failed: {exc}")
        return None


def download_update_zip(download_endpoint: str, dest_path: str) -> Tuple[bool, str]:
    """
    Download the plugin update zip.
    
    Args:
        download_endpoint: The endpoint path from get_latest_update() assets.
        dest_path: Where to save the zip file.
    
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        client = get_api_client()
        # The download_endpoint already includes the full path like /update/download?asset_url=...
        url = f"{CLOUDFLARE_API_URL}{download_endpoint}"
        
        with client.stream("GET", url, headers=_get_headers(), timeout=HTTP_DOWNLOAD_TIMEOUT_SECONDS) as resp:
            if resp.status_code != 200:
                return False, f"Download failed with status {resp.status_code}"
            
            with open(dest_path, "wb") as f:
                for chunk in resp.iter_bytes():
                    if chunk:
                        f.write(chunk)
        
        return True, ""
    except Exception as exc:
        logger.warn(f"API download_update_zip failed: {exc}")
        return False, str(exc)


def create_game_request(appid: int) -> bool:
    """
    Create a request for a game that doesn't exist.
    
    Returns:
        True if request was created or already exists, False on error.
    """
    try:
        client = get_api_client()
        resp = client.put(
            f"{CLOUDFLARE_API_URL}/request/{appid}",
            headers=_get_headers(),
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        if resp.status_code in (200, 201):
            return True
        return False
    except Exception as exc:
        logger.warn(f"API create_game_request failed for {appid}: {exc}")
        return False


def check_request_exists(appid: int) -> bool:
    """Check if a game request already exists."""
    try:
        client = get_api_client()
        resp = client.get(
            f"{CLOUDFLARE_API_URL}/request/check/{appid}",
            headers=_get_headers(),
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("exists", False)
        return False
    except Exception as exc:
        logger.warn(f"API check_request_exists failed for {appid}: {exc}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# Removed Games API (for future use)
# ═══════════════════════════════════════════════════════════════════════════


def add_removed_game(appid: int) -> bool:
    """Add a game to the removed games list."""
    try:
        client = get_api_client()
        resp = client.put(
            f"{CLOUDFLARE_API_URL}/removed/{appid}",
            headers=_get_headers(),
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        return resp.status_code in (200, 201)
    except Exception as exc:
        logger.warn(f"API add_removed_game failed for {appid}: {exc}")
        return False


def check_removed_game(appid: int) -> bool:
    """Check if a game is in the removed list."""
    try:
        client = get_api_client()
        resp = client.get(
            f"{CLOUDFLARE_API_URL}/removed/check/{appid}",
            headers=_get_headers(),
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("exists", False)
        return False
    except Exception as exc:
        logger.warn(f"API check_removed_game failed for {appid}: {exc}")
        return False



def check_updates_batch(games: Dict[str, str]) -> Dict[str, Any]:
    """
    Check for updates for multiple games in a single request.
    
    Args:
        games: Dictionary mapping appid (as string) to local version string.
               Example: {"12345": "1.0.0", "67890": "2.1.0"}
               
    Returns:
        Dictionary containing success status and list of updates.
        Example: {"success": True, "updates": [...]}
    """
    try:
        client = get_api_client()
        # Ensure we send a valid JSON body
        payload = {"games": games}
        
        resp = client.post(
            f"{CLOUDFLARE_API_URL}/update/check-batch",
            headers=_get_headers(),
            json=payload,
            timeout=30.0, # Longer timeout for batch check
        )
        
        if resp.status_code == 200:
            return resp.json()
        else:
            logger.warn(f"Batch update check failed with status {resp.status_code}")
            return {"success": False, "error": f"HTTP {resp.status_code}"}
            
    except Exception as exc:
        logger.warn(f"Batch update check failed: {exc}")
        return {"success": False, "error": str(exc)}


def check_availability_batch(appids: List[int]) -> Dict[str, Any]:
    """
    Check if multiple games exist in the repo (batch mode).
    
    Args:
        appids: List of appids to check.
        
    Returns:
        Dictionary with list of available appids.
        Example: {"success": True, "available": [123, 456]}
    """
    try:
        client = get_api_client()
        payload = {"appids": appids}
        
        resp = client.post(
            f"{CLOUDFLARE_API_URL}/check-exists-batch",
            headers=_get_headers(),
            json=payload,
            timeout=30.0,
        )
        
        if resp.status_code == 200:
            return resp.json()
        return {"success": False, "error": f"HTTP {resp.status_code}"}
    except Exception as exc:
        logger.warn(f"Batch availability check failed: {exc}")
        return {"success": False, "error": str(exc)}


# ═══════════════════════════════════════════════════════════════════════════
# Split Archive Support Functions
# ═══════════════════════════════════════════════════════════════════════════


def check_download_type(appid: int, repo_type: str = "download") -> Dict[str, Any]:
    """
    Check if a game has a single zip file or split archive.
    
    Args:
        appid: The game's app ID.
        repo_type: One of 'download', 'fix', or 'bypass'.
    
    Returns:
        Dict with 'type' ('single', 'split', or 'none'), and 'files' list.
    """
    try:
        client = get_api_client()
        
        # Map repo_type to correct endpoint
        endpoint_map = {
            "download": "download",
            "fix": "fix",
            "bypass": "bypass",
        }
        endpoint = endpoint_map.get(repo_type, "download")
        
        url = f"{CLOUDFLARE_API_URL}/{endpoint}/{appid}/info"
        
        resp = client.get(url, headers=_get_headers(), timeout=HTTP_TIMEOUT_SECONDS)
        
        if resp.status_code == 200:
            return resp.json()
        
        # Handle errors (401, 403, etc)
        try:
            error_data = resp.json()
            error_msg = error_data.get("error", "Unknown error")
            return {"type": "error", "appid": appid, "files": [], "error": error_msg}
        except:
            return {"type": "error", "appid": appid, "files": [], "error": f"API Error: {resp.status_code}"}
    except Exception as exc:
        logger.warn(f"API check_download_type failed for {appid}: {exc}")
        return {"type": "error", "appid": appid, "files": [], "error": str(exc)}


def download_split_part(appid: int, filename: str, dest_path: str, repo_type: str = "download", progress_callback=None) -> Tuple[bool, str]:
    """
    Download a single part of a split archive.
    
    Args:
        appid: The game's app ID.
        filename: The filename to download (e.g., "12345.z01").
        dest_path: Where to save the downloaded file.
        repo_type: One of 'download', 'fix', or 'bypass'.
        progress_callback: Optional function(bytes_read, total_bytes) to call during download.
    
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    import os
    
    try:
        client = get_api_client()
        
        endpoint_map = {
            "download": "download",
            "fix": "fix",
            "bypass": "bypass",
        }
        endpoint = endpoint_map.get(repo_type, "download")
        
        url = f"{CLOUDFLARE_API_URL}/{endpoint}/{appid}/part/{filename}"
        logger.log(f"SteamLord: Downloading part from: {url}")
        
        with client.stream("GET", url, headers=_get_headers(), timeout=HTTP_DOWNLOAD_TIMEOUT_SECONDS) as resp:
            # Check content type - should be binary, not JSON
            content_type = resp.headers.get("content-type", "")
            logger.log(f"SteamLord: Response content-type: {content_type}, status: {resp.status_code}")
            
            if resp.status_code == 404:
                return False, f"Part file {filename} not found"
            if resp.status_code != 200:
                # Try to read error message
                try:
                    resp.read()
                    error_data = resp.json()
                    return False, error_data.get("error", f"Download failed with status {resp.status_code}")
                except:
                    return False, f"Download failed with status {resp.status_code}"
            
            # Check if response is JSON (error) instead of binary
            if "application/json" in content_type:
                try:
                    resp.read()
                    error_data = resp.json()
                    return False, error_data.get("error", "API returned JSON instead of file")
                except:
                    return False, "API returned JSON instead of binary file"
            
            # Get total size if available
            total_content_length = int(resp.headers.get("content-length", 0))
            
            total_bytes = 0
            with open(dest_path, "wb") as f:
                for chunk in resp.iter_bytes():
                    if chunk:
                        f.write(chunk)
                        total_bytes += len(chunk)
                        if progress_callback:
                            progress_callback(total_bytes, total_content_length)
        
        # Verify file was downloaded
        if not os.path.exists(dest_path):
            return False, "File was not created"
        
        file_size = os.path.getsize(dest_path)
        logger.log(f"SteamLord: Downloaded {filename}: {file_size} bytes")
        
        if file_size == 0:
            os.remove(dest_path)
            return False, "Downloaded file is empty"
    
        # Check first bytes for obvious errors (like JSON response saved as binary)
        with open(dest_path, "rb") as f:
            first_bytes = f.read(10)
            # If file starts with '{' or '[', it's likely a JSON error response
            if first_bytes.startswith(b'{') or first_bytes.startswith(b'['):
                logger.warn(f"SteamLord: Downloaded file appears to be JSON, not binary: {first_bytes[:50]}")
                os.remove(dest_path)
                return False, "Downloaded file is JSON, not binary data"
        
        return True, ""
    except Exception as exc:
        logger.warn(f"API download_split_part failed for {appid}/{filename}: {exc}")
        return False, str(exc)


def download_all_split_parts(appid: int, dest_dir: str, repo_type: str = "download", progress_callback=None) -> Tuple[bool, str, List[str]]:
    """
    Download all parts of a split archive.
    
    Args:
        appid: The game's app ID.
        dest_dir: Directory to save all parts.
        repo_type: One of 'download', 'fix', or 'bypass'.
        progress_callback: Optional function(bytes_read, total_bytes) to call during download.
    
    Returns:
        Tuple of (success: bool, error_message: str, downloaded_files: List[str])
    """
    import os
    
    try:
        # First check download type
        info = check_download_type(appid, repo_type)
        
        if info.get("type") == "none":
            return False, "Game not found", []
        
        if info.get("type") == "error":
            return False, info.get("error", "Unknown error"), []
        
        if info.get("type") == "single":
            # Single file - just download normally
            dest_path = os.path.join(dest_dir, f"{appid}.zip")
            
            # Use the regular download function
            if repo_type == "download":
                success, error = download_game_zip(appid, dest_path, progress_callback)
            elif repo_type == "fix":
                success, error = download_fix_zip(appid, dest_path, progress_callback)
            elif repo_type == "bypass":
                success, error = download_bypass_zip(appid, dest_path, progress_callback)
            else:
                success, error = download_game_zip(appid, dest_path, progress_callback)
            
            if success:
                return True, "", [dest_path]
            return False, error, []
        
        # Split archive - download all parts
        files = info.get("files", [])
        if not files:
            return False, "No files found in split archive", []
        
        logger.log(f"SteamLord: Downloading {len(files)} split parts for {appid}")
        
        # Get file sizes from info if available, or estimate
        file_sizes = info.get("sizes", {})
        total_size = sum(file_sizes.get(f, 0) for f in files)
        
        # If no size info from API, estimate based on typical split sizes
        if total_size == 0:
            # Will track actual bytes as we download
            total_size = 0
            
        # Track cumulative progress across all files
        cumulative_state = {"downloaded": 0, "total": total_size, "current_file_index": 0}
        
        def cumulative_progress_callback(bytes_read, total_bytes):
            """Wrapper to track cumulative progress across all files."""
            if progress_callback:
                # If we don't have total size, estimate it from current file progress
                if cumulative_state["total"] == 0 and total_bytes > 0:
                    # Estimate total: (current file total * number of files)
                    cumulative_state["total"] = total_bytes * len(files)
                
                # Calculate cumulative bytes downloaded
                # Previous files (fully downloaded) + current file progress
                previous_files_bytes = cumulative_state.get("previous_complete", 0)
                current_total = previous_files_bytes + bytes_read
                
                # Report cumulative progress
                progress_callback(current_total, cumulative_state["total"])
        
        downloaded_files = []
        for i, filename in enumerate(files):
            dest_path = os.path.join(dest_dir, filename)
            cumulative_state["current_file_index"] = i
            
            # Download this part with cumulative progress tracking
            success, error = download_split_part(appid, filename, dest_path, repo_type, cumulative_progress_callback)
            
            if not success:
                # Cleanup downloaded files on failure
                for f in downloaded_files:
                    try:
                        os.remove(f)
                    except:
                        pass
                return False, f"Failed to download {filename}: {error}", []
            
            # Update cumulative bytes from completed files
            if os.path.exists(dest_path):
                file_size = os.path.getsize(dest_path)
                cumulative_state["previous_complete"] = cumulative_state.get("previous_complete", 0) + file_size
                # Update total if we're tracking dynamically
                if cumulative_state["total"] == 0 or cumulative_state["total"] < cumulative_state["previous_complete"]:
                    cumulative_state["total"] = file_size * len(files)
            
            downloaded_files.append(dest_path)
            logger.log(f"SteamLord: Downloaded part {filename}")
        
        return True, "", downloaded_files
    except Exception as exc:
        logger.warn(f"API download_all_split_parts failed for {appid}: {exc}")
        return False, str(exc), []


def merge_split_archive(appid: int, parts_dir: str) -> Tuple[bool, str, str]:
    """
    Merge split archive parts into a single ZIP file.
    
    Tries both merge orders:
    1. WinRAR standard: .zip, .z01, .z02, ...
    2. Alternative: .z01, .z02, ..., .zip
    
    Args:
        appid: The game's app ID.
        parts_dir: Directory containing the split parts.
    
    Returns:
        Tuple of (success: bool, error_message: str, merged_file_path: str)
    """
    import os
    import zipfile as zf
    
    def try_merge_order(file_order: list, output_path: str) -> bool:
        """Try merging in specified order and validate result."""
        try:
            with open(output_path, "wb") as merged_file:
                for part_name in file_order:
                    part_path = os.path.join(parts_dir, part_name)
                    if not os.path.exists(part_path):
                        return False
                    with open(part_path, "rb") as part_file:
                        while True:
                            chunk = part_file.read(65536)  # 64KB chunks
                            if not chunk:
                                break
                            merged_file.write(chunk)
            
            # Validate the merged file
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                try:
                    with zf.ZipFile(output_path, 'r') as test_zip:
                        # Try to read the file list - if this works, it's valid
                        test_zip.namelist()
                    return True
                except:
                    return False
            return False
        except:
            return False
    
    try:
        # Find all part files
        numbered_parts = []
        main_zip = None
        
        for filename in os.listdir(parts_dir):
            if filename.startswith(f"{appid}.z") and not filename.endswith(".zip"):
                numbered_parts.append(filename)
            elif filename == f"{appid}.zip":
                main_zip = filename
        
        if not numbered_parts and not main_zip:
            return False, "No split archive parts found", ""
        
        # Sort numbered parts: z01, z02, z03...
        numbered_parts.sort(key=lambda x: int(x.split('.z')[-1]) if x.split('.z')[-1].isdigit() else 999)
        
        merged_path = os.path.join(parts_dir, f"{appid}_merged.zip")
        
        # Try WinRAR standard order first: .zip, .z01, .z02, ...
        if main_zip:
            order1 = [main_zip] + numbered_parts
            logger.log(f"SteamLord: Trying merge order 1 (WinRAR): {order1}")
            
            if try_merge_order(order1, merged_path):
                logger.log(f"SteamLord: Merge order 1 succeeded!")
                # Cleanup original parts
                for f in order1:
                    try:
                        os.remove(os.path.join(parts_dir, f))
                    except:
                        pass
                return True, "", merged_path
            
            # Try alternative order: .z01, .z02, ..., .zip
            order2 = numbered_parts + [main_zip]
            logger.log(f"SteamLord: Trying merge order 2 (alternative): {order2}")
            
            if try_merge_order(order2, merged_path):
                logger.log(f"SteamLord: Merge order 2 succeeded!")
                # Cleanup original parts
                for f in order2:
                    try:
                        os.remove(os.path.join(parts_dir, f))
                    except:
                        pass
                return True, "", merged_path
            
            return False, "Failed to merge split archive - invalid ZIP format", ""
        else:
            # Only numbered parts, no main zip
            logger.log(f"SteamLord: Merging numbered parts only: {numbered_parts}")
            if try_merge_order(numbered_parts, merged_path):
                for f in numbered_parts:
                    try:
                        os.remove(os.path.join(parts_dir, f))
                    except:
                        pass
                return True, "", merged_path
            return False, "Failed to merge split archive", ""
            
    except Exception as exc:
        logger.warn(f"merge_split_archive failed for {appid}: {exc}")
        return False, str(exc), ""


def extract_split_zip(appid: int, parts_dir: str, output_dir: str) -> Tuple[bool, str]:
    """
    Extract split ZIP archives using 7z (handles spanned/multi-volume ZIPs).
    
    Args:
        appid: The game's app ID.
        parts_dir: Directory containing the split parts.
        output_dir: Where to extract the contents.
    
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    import os
    import subprocess
    import shutil
    from pathlib import Path
    
    try:
        # Find the main .zip file
        main_zip = os.path.join(parts_dir, f"{appid}.zip")
        
        if not os.path.exists(main_zip):
            return False, f"Main ZIP file not found: {main_zip}"
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Get the path to bundled 7za.exe in backend/bin
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        bundled_7za = os.path.join(backend_dir, "bin", "7za.exe")
        
        # Try to find 7z - prioritize bundled version
        seven_zip_paths = [
            bundled_7za,  # Bundled portable version (PRIORITY)
            "7z",  # If in PATH
            r"C:\Program Files\7-Zip\7z.exe",
            r"C:\Program Files (x86)\7-Zip\7z.exe",
        ]
        
        seven_zip = None
        for path in seven_zip_paths:
            if os.path.exists(path) or shutil.which(path):
                seven_zip = path
                logger.log(f"SteamLord: Found 7z at: {path}")
                break
        
        if seven_zip:
            # Use 7z to extract (it handles spanned ZIPs properly)
            logger.log(f"SteamLord: Extracting with 7z: {main_zip}")
            
            # CREATE_NO_WINDOW = 0x08000000
            creationflags = 0x08000000
            
            result = subprocess.run(
                [seven_zip, "x", main_zip, f"-o{output_dir}", "-y"],
                capture_output=True,
                text=True,
                cwd=parts_dir,
                creationflags=creationflags
            )
            
            if result.returncode == 0:
                logger.log(f"SteamLord: 7z extraction successful!")
                return True, ""
            else:
                logger.log(f"SteamLord: 7z extraction failed: {result.stderr}")
                # Fall back to other methods
        else:
            logger.log("SteamLord: 7z not found, trying PowerShell")
        
        # Fallback: Try PowerShell Expand-Archive (only works for single zips)
        # First try to merge the files and use PowerShell
        numbered_parts = []
        i = 1
        while True:
            part_file = os.path.join(parts_dir, f"{appid}.z{str(i).zfill(2)}")
            if os.path.exists(part_file):
                numbered_parts.append(part_file)
                i += 1
            else:
                break
        
        if not numbered_parts:
            # Just a single ZIP, use PowerShell
            logger.log("SteamLord: Single ZIP, using PowerShell")
            try:
                # CREATE_NO_WINDOW = 0x08000000
                creationflags = 0x08000000
                
                result = subprocess.run(
                    ["powershell", "-Command", f'Expand-Archive -Path "{main_zip}" -DestinationPath "{output_dir}" -Force'],
                    capture_output=True,
                    text=True,
                    creationflags=creationflags
                )
                if result.returncode == 0:
                    return True, ""
                else:
                    return False, f"PowerShell extraction failed: {result.stderr}"
            except Exception as e:
                return False, f"PowerShell error: {e}"
        
        # If we have split parts but no 7z, we can't extract
        return False, "Internal Error: Split archive component missing. Please reinstall SteamLord."
        
    except Exception as exc:
        logger.warn(f"Split ZIP extraction failed for {appid}: {exc}")
        return False, str(exc)


def download_with_split_support(appid: int, dest_path: str, repo_type: str = "download", progress_callback=None) -> Tuple[bool, str]:
    """
    Download a game/fix/bypass with automatic split archive support.
    
    This is the main function to use for downloading - it handles both
    single files and split archives automatically.
    
    Args:
        appid: The game's app ID.
        dest_path: Where to save the final zip file.
        repo_type: One of 'download', 'fix', or 'bypass'.
        progress_callback: Optional function(bytes_read, total_bytes) to call during download.
    
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    import os
    import shutil
    import tempfile
    import zipfile
    
    try:
        # Check what type of download this is
        info = check_download_type(appid, repo_type)
        download_type = info.get("type", "none")
        
        logger.log(f"SteamLord: Download type for {appid}: {download_type}")
        
        if download_type == "none":
            if repo_type == "fix":
                return False, "No Fix Found for This Game"
            elif repo_type == "bypass":
                return False, "No Bypass Found for This Game"
            else:
                return False, "Game Not Added Yet: Will Be Added Soon"
        
        if download_type == "error":
            return False, info.get("error", "Unknown error")
        
        if download_type == "single":
            # Single file - download directly
            if repo_type == "download":
                return download_game_zip(appid, dest_path, progress_callback)
            elif repo_type == "fix":
                return download_fix_zip(appid, dest_path, progress_callback)
            elif repo_type == "bypass":
                return download_bypass_zip(appid, dest_path, progress_callback)
            return download_game_zip(appid, dest_path, progress_callback)
        
        # Split archive - download all parts and extract
        logger.log(f"SteamLord: Downloading split archive for {appid}")
        
        # Create temp directories inside backend folder (not system temp)
        backend_temp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_dl")
        os.makedirs(backend_temp, exist_ok=True)
        temp_parts_dir = tempfile.mkdtemp(prefix=f"parts_{appid}_", dir=backend_temp)
        temp_extract_dir = tempfile.mkdtemp(prefix=f"extract_{appid}_", dir=backend_temp)
        
        try:
            # Download all parts
            # Note: progress_callback is passed here too
            success, error, downloaded = download_all_split_parts(appid, temp_parts_dir, repo_type, progress_callback)
            
            if not success:
                return False, error
            
            # Extract split archive
            success, error = extract_split_zip(appid, temp_parts_dir, temp_extract_dir)
            
            if not success:
                return False, error
            
            # Create final ZIP from extracted contents
            logger.log(f"SteamLord: Creating final ZIP from extracted contents")
            
            with zipfile.ZipFile(dest_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(temp_extract_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_extract_dir)
                        zf.write(file_path, arcname)
            
            logger.log(f"SteamLord: Split archive processed and saved to {dest_path}")
            return True, ""
            
        finally:
            # Cleanup temp directories
            try:
                shutil.rmtree(temp_parts_dir)
            except:
                pass
            try:
                shutil.rmtree(temp_extract_dir)
            except:
                pass
                
    except Exception as exc:
        logger.warn(f"download_with_split_support failed for {appid}: {exc}")
        return False, str(exc)


__all__ = [
    "api_health_check",
    "check_game_exists",
    "check_fix_exists",
    "check_bypass_exists",
    "download_game_zip",
    "download_game_json",
    "download_fix_zip",
    "download_bypass_zip",
    "download_guard_file",
    "get_latest_update",
    "download_update_zip",
    "create_game_request",
    "check_request_exists",
    "add_removed_game",
    "check_removed_game",
    "get_api_client",
    "close_api_client",
    "check_updates_batch",
    "check_availability_batch",
    # Split archive support
    "check_download_type",
    "download_split_part",
    "download_all_split_parts",
    "merge_split_archive",
    "download_with_split_support",
]
