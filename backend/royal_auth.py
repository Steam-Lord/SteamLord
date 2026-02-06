"""License management module for SteamLord.

Handles HWID generation, license verification, session management,
API Token management, and communication with the Cloudflare License API.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import threading
import time
from typing import Optional, Dict, Tuple

from kingdom_config import (
    CLOUDFLARE_API_URL,
    USER_AGENT,
    HTTP_TIMEOUT_SECONDS,
)
from throne_logger import logger
from kingdom_paths import backend_path

# Session file path
SESSION_FILE = "session.json"

# Session state
_session_data: Optional[Dict] = None
_session_lock = threading.Lock()


# ═══════════════════════════════════════════════════════════════════════════
# HWID Generation
# ═══════════════════════════════════════════════════════════════════════════

def _get_windows_hwid() -> str:
    """Generate HWID on Windows using WMI."""
    components = []
    
    try:
        # CPU ID
        result = subprocess.run(
            ['wmic', 'cpu', 'get', 'processorid'],
            capture_output=True, text=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        cpu_id = result.stdout.strip().split('\n')[-1].strip()
        if cpu_id and cpu_id != 'ProcessorId':
            components.append(f"CPU:{cpu_id}")
    except Exception:
        pass
    
    try:
        # Motherboard Serial
        result = subprocess.run(
            ['wmic', 'baseboard', 'get', 'serialnumber'],
            capture_output=True, text=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        mb_serial = result.stdout.strip().split('\n')[-1].strip()
        if mb_serial and mb_serial != 'SerialNumber' and mb_serial != 'To be filled by O.E.M.':
            components.append(f"MB:{mb_serial}")
    except Exception:
        pass
    
    try:
        # Disk Serial (first disk)
        result = subprocess.run(
            ['wmic', 'diskdrive', 'get', 'serialnumber'],
            capture_output=True, text=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip() and l.strip() != 'SerialNumber']
        if lines:
            components.append(f"DISK:{lines[0]}")
    except Exception:
        pass
    
    try:
        # Machine GUID from registry
        result = subprocess.run(
            ['reg', 'query', 'HKLM\\SOFTWARE\\Microsoft\\Cryptography', '/v', 'MachineGuid'],
            capture_output=True, text=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        for line in result.stdout.split('\n'):
            if 'MachineGuid' in line:
                parts = line.split()
                if len(parts) >= 3:
                    components.append(f"GUID:{parts[-1]}")
                break
    except Exception:
        pass
    
    # Fallback: username + hostname
    if len(components) < 2:
        components.append(f"USER:{os.getenv('USERNAME', 'unknown')}")
        components.append(f"HOST:{platform.node()}")
    
    return "|".join(components)


def generate_hwid() -> str:
    """Generate a unique hardware ID for this machine."""
    try:
        raw_hwid = _get_windows_hwid()
        # Hash it for privacy and consistency
        hwid_hash = hashlib.sha256(raw_hwid.encode('utf-8')).hexdigest()
        return hwid_hash
    except Exception as exc:
        logger.warn(f"SteamLord: HWID generation failed: {exc}")
        # Fallback to basic info
        fallback = f"{platform.node()}:{os.getenv('USERNAME', 'unknown')}:{platform.machine()}"
        return hashlib.sha256(fallback.encode('utf-8')).hexdigest()


def get_device_name() -> str:
    """Get a friendly device name."""
    try:
        hostname = platform.node()
        username = os.getenv('USERNAME', 'User')
        return f"{hostname} ({username})"
    except Exception:
        return "Unknown Device"


# ═══════════════════════════════════════════════════════════════════════════
# Session Management
# ═══════════════════════════════════════════════════════════════════════════

def _session_file_path() -> str:
    """Get the path to the session file."""
    return backend_path(SESSION_FILE)


def _load_session_from_disk() -> Optional[Dict]:
    """Load session data from disk."""
    try:
        path = _session_file_path()
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as exc:
        logger.warn(f"SteamLord: Failed to load session: {exc}")
    return None


def _save_session_to_disk(data: Dict) -> bool:
    """Save session data to disk."""
    try:
        path = _session_file_path()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as exc:
        logger.warn(f"SteamLord: Failed to save session: {exc}")
        return False


def _delete_session_from_disk() -> None:
    """Delete session file from disk."""
    try:
        path = _session_file_path()
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def get_session() -> Optional[Dict]:
    """Get the current session data."""
    global _session_data
    with _session_lock:
        if _session_data is None:
            _session_data = _load_session_from_disk()
        return _session_data


def get_session_token() -> Optional[str]:
    """Get the current session token."""
    session = get_session()
    if session:
        return session.get('token')
    return None


def set_session(data: Dict) -> None:
    """Set the current session data."""
    global _session_data
    with _session_lock:
        _session_data = data
        _save_session_to_disk(data)


def clear_session() -> None:
    """Clear the current session."""
    global _session_data
    with _session_lock:
        _session_data = None
        _delete_session_from_disk()


def is_logged_in() -> bool:
    """Check if user is logged in."""
    session = get_session()
    return session is not None and 'token' in session


def validate_session_local() -> Tuple[bool, str]:
    """
    Validate session locally without making API request.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    session = get_session()
    
    # No session at all
    if not session:
        return False, "NOT_ACTIVATED"
    
    if not session.get('token'):
        return False, "NOT_ACTIVATED"
    
    # Check expiration (for non-lifetime keys)
    if not session.get('isLifetime', False):
        expires_at = session.get('expiresAt')
        if expires_at:
            try:
                from datetime import datetime
                # Parse ISO format date
                if isinstance(expires_at, str):
                    expire_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    if datetime.now(expire_time.tzinfo) > expire_time:
                        return False, "SESSION_EXPIRED"
            except Exception:
                pass  # If parsing fails, let API verify
    
    return True, ""


def can_download_local(download_type: str = "game") -> Tuple[bool, str]:
    """
    Check if user can download locally without API request.
    
    Args:
        download_type: "game", "fix", or "bypass"
    
    Returns:
        Tuple of (can_download, error_message)
    """
    # First check session validity
    is_valid, error = validate_session_local()
    if not is_valid:
        return False, error
    
    session = get_session()
    permissions = session.get('permissions', {})
    limits = session.get('limits', {})
    
    # Defaults if permissions missing (legacy fallback)
    can_dl = permissions.get('canDownload', True)
    can_fix = permissions.get('canFix', True)
    can_bypass = permissions.get('canBypass', False)

    if download_type == "game":
        if not can_dl:
            return False, "FEATURE_DISABLED"
        max_d = limits.get('maxDownloads', 0)
        used_d = limits.get('downloadsUsed', 0)
        if max_d > 0 and used_d >= max_d:
            return False, "DOWNLOAD_LIMIT_REACHED"
    
    elif download_type == "fix":
        if not can_fix:
            return False, "FEATURE_DISABLED"
        max_f = limits.get('maxFixes', 0)
        used_f = limits.get('fixesUsed', 0)
        if max_f > 0 and used_f >= max_f:
            return False, "FIX_LIMIT_REACHED"
    
    elif download_type == "bypass":
        if not can_bypass:
            return False, "FEATURE_DISABLED"
        max_b = limits.get('maxBypass', 0)
        used_b = limits.get('bypassUsed', 0)
        if max_b > 0 and used_b >= max_b:
            return False, "BYPASS_LIMIT_REACHED"
    
    return True, ""


def update_local_usage(download_type: str = "game") -> None:
    """
    Update local usage counter after successful download.
    This keeps local limits in sync with server.
    
    Args:
        download_type: "game", "fix", or "bypass"
    """
    session = get_session()
    if not session:
        return
    
    limits = session.get('limits', {})
    if not limits:
        return
    
    if download_type == "game":
        limits['downloadsUsed'] = limits.get('downloadsUsed', 0) + 1
    elif download_type == "fix":
        limits['fixesUsed'] = limits.get('fixesUsed', 0) + 1
    elif download_type == "bypass":
        limits['bypassUsed'] = limits.get('bypassUsed', 0) + 1
    
    session['limits'] = limits
    set_session(session)


def invalidate_local_session() -> None:
    """
    Mark local session as invalid (called when API returns session expired).
    """
    session = get_session()
    if session:
        # Set expired time to force local validation to fail
        session['expiresAt'] = '2000-01-01T00:00:00Z'
        set_session(session)


def get_api_token() -> Optional[str]:
    """Get the current API token, refreshing if necessary."""
    session = get_session()
    if not session:
        return None
    
    api_token = session.get('apiToken')
    api_token_expiry = session.get('apiTokenExpiry')  # timestamp in seconds
    
    if not api_token:
        return None
    
    # Check if token needs refresh (within 5 minutes of expiry)
    if api_token_expiry:
        current_time = time.time()
        if current_time >= (api_token_expiry - 300):  # 5 min buffer
            refreshed = refresh_api_token()
            if refreshed:
                session = get_session()
                return session.get('apiToken') if session else None
    
    return api_token


def refresh_api_token() -> bool:
    """Refresh the API token from server."""
    session = get_session()
    if not session or not session.get('token'):
        return False
    
    try:
        client = _get_license_client()
        response = client.post(
            f"{CLOUDFLARE_API_URL}/license/refresh-token",
            json={"sessionToken": session.get("token")},
            headers={
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            }
        )
        
        data = response.json()
        
        if data.get('success'):
            session['apiToken'] = data.get('apiToken')
            # Calculate expiry timestamp
            expiry_seconds = data.get('apiTokenExpiry', 3600)
            session['apiTokenExpiry'] = time.time() + expiry_seconds
            set_session(session)
            logger.log("SteamLord: API Token refreshed successfully")
            return True
        else:
            logger.warn(f"SteamLord: API Token refresh failed: {data.get('error')}")
            return False
            
    except Exception as exc:
        logger.warn(f"SteamLord: API Token refresh exception: {exc}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# License API Communication
# ═══════════════════════════════════════════════════════════════════════════

def _get_license_client():
    """Get HTTP client for license API calls."""
    import httpx
    return httpx.Client(timeout=HTTP_TIMEOUT_SECONDS)


def register_license(license_key: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Register with license key only (no email required).
    
    Returns:
        Tuple of (success, error_message, session_data)
    """
    try:
        hwid = generate_hwid()
        device_name = get_device_name()
        
        client = _get_license_client()
        response = client.post(
            f"{CLOUDFLARE_API_URL}/license/register",
            json={
                "key": license_key,
                "hwid": hwid,
                "deviceName": device_name,
            },
            headers={
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            }
        )
        
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            # Calculate API token expiry timestamp
            api_token_expiry_seconds = data.get('apiTokenExpiry', 3600)
            
            session_data = {
                "token": data.get("token"),
                "apiToken": data.get("apiToken"),
                "apiTokenExpiry": time.time() + api_token_expiry_seconds,
                "expiresAt": data.get("expiresAt"),
                "isLifetime": data.get("isLifetime", False),
                "isFreeKey": data.get("isFreeKey", False),
                "limits": data.get("limits"),
                "permissions": data.get("permissions"),
                "hwid": hwid,
                "licenseKey": license_key,
            }
            set_session(session_data)
            logger.log(f"SteamLord: Activated successfully with key {license_key[:8]}...")
            
            # Download guard file on activation (if not already present)
            try:
                from crown_shield import get_file_guard
                from royal_gateway import download_guard_file
                import os
                
                guard = get_file_guard()
                guard_path = guard._get_enabled_path()  # xinput1_4.dll
                
                if not os.path.exists(guard_path):
                    logger.log("SteamLord: Downloading guard file on activation...")
                    success, err = download_guard_file(guard_path)
                    if success:
                        logger.log("SteamLord: Guard file downloaded successfully")
                    else:
                        logger.warn(f"SteamLord: Guard file download failed: {err}")
                else:
                    logger.log("SteamLord: Guard file already exists")
            except Exception as guard_exc:
                logger.warn(f"SteamLord: Guard download failed: {guard_exc}")
            
            return True, "", session_data
        else:
            error = data.get("error", "Unknown error")
            code = data.get("code", "")
            logger.warn(f"SteamLord: Activation failed: {error} ({code})")
            return False, error, None
            
    except Exception as exc:
        logger.warn(f"SteamLord: Activation exception: {exc}")
        return False, str(exc), None


def verify_session() -> Tuple[bool, str, Optional[Dict]]:
    """
    Verify the current session with the server.
    
    Returns:
        Tuple of (valid, error_message, session_info)
    """
    session = get_session()
    if not session or not session.get('token'):
        return False, "No session", None
    
    try:
        hwid = generate_hwid()
        
        # Check if HWID matches
        if session.get('hwid') and session.get('hwid') != hwid:
            clear_session()
            return False, "HWID changed", None
        
        client = _get_license_client()
        response = client.post(
            f"{CLOUDFLARE_API_URL}/license/verify",
            json={
                "token": session.get("token"),
                "hwid": hwid,
            },
            headers={
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            }
        )
        
        data = response.json()
        
        if data.get('valid'):
            # Update session with latest info
            session['expiresAt'] = data.get('expiresAt')
            session['isLifetime'] = data.get('isLifetime', False)
            session['email'] = data.get('email')
            if data.get('permissions'):
                session['permissions'] = data.get('permissions')
            if data.get('limits'):
                session['limits'] = data.get('limits')
            set_session(session)
            return True, "", data
        else:
            error = data.get("error", "Invalid session")
            code = data.get("code", "")
            
            # Clear session if it's invalid
            if code in ['INVALID_SESSION', 'EXPIRED', 'SUSPENDED', 'BLOCKED', 'REVOKED', 'HWID_MISMATCH']:
                clear_session()
            
            return False, error, None
            
    except Exception as exc:
        logger.warn(f"SteamLord: Session verification failed: {exc}")
        # Don't clear session on network error
        return False, f"Network error: {exc}", None


def logout() -> bool:
    """Logout from the current session."""
    session = get_session()
    if not session or not session.get('token'):
        clear_session()
        return True
    
    try:
        client = _get_license_client()
        client.post(
            f"{CLOUDFLARE_API_URL}/license/logout",
            json={"token": session.get("token")},
            headers={
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            }
        )
    except Exception as exc:
        logger.warn(f"SteamLord: Logout API call failed: {exc}")
    
    clear_session()
    logger.log("SteamLord: Logged out")
    return True


def get_license_status() -> Optional[Dict]:
    """Get detailed license status from server."""
    session = get_session()
    if not session or not session.get('token'):
        return None
    
    try:
        client = _get_license_client()
        response = client.post(
            f"{CLOUDFLARE_API_URL}/license/status",
            json={"token": session.get("token")},
            headers={
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            }
        )
        
        data = response.json()
        if data.get('valid'):
            return data
        return None
        
    except Exception as exc:
        logger.warn(f"SteamLord: License status check failed: {exc}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# Startup Verification
# ═══════════════════════════════════════════════════════════════════════════

def verify_on_startup() -> Tuple[bool, str]:
    """
    Verify license on plugin startup.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not is_logged_in():
        return False, "NOT_LOGGED_IN"
    
    valid, error, _ = verify_session()
    
    if valid:
        logger.log("SteamLord: License verified successfully")
        return True, ""
    else:
        logger.warn(f"SteamLord: License verification failed: {error}")
        return False, error


__all__ = [
    "generate_hwid",
    "get_device_name",
    "get_session",
    "get_session_token",
    "get_api_token",
    "refresh_api_token",
    "set_session",
    "clear_session",
    "is_logged_in",
    "register_license",
    "verify_session",
    "logout",
    "get_license_status",
    "verify_on_startup",
]
