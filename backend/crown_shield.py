"""
File Guard - Activation Guard System
Manages the guard file based on session validity.

When session is valid: guard file (enabled)
When session is invalid: guard file (disabled)
"""

from __future__ import annotations

import os
import time
import threading
from typing import Optional, Tuple

import Millennium  # type: ignore

from throne_logger import logger

# File names
import base64

def _d(s: str) -> str:
    return base64.b64decode(s).decode()

# File names (Obfuscated)
ENABLED_FILE = _d("eGlucHV0MV80LmRsbA==")
DISABLED_FILE = _d("eGltcHV0MV80LmRsbA==")




class FileGuard:
    """
    Manages the activation guard file.
    
    - On session valid: enables the guard file
    - On session invalid: disables the guard file
    """
    
    def __init__(self):
        self._steam_path: Optional[str] = None
        self._initialized = False
        
    def _get_steam_path(self) -> str:
        """Get Steam installation path."""
        if self._steam_path:
            return self._steam_path
            
        try:
            self._steam_path = Millennium.steam_path()
        except:
            # Fallback detection
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")
                self._steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
                winreg.CloseKey(key)
            except:
                self._steam_path = r"C:\Program Files (x86)\Steam"
                
        return self._steam_path
    
    def _get_enabled_path(self) -> str:
        """Get path to enabled file."""
        return os.path.join(self._get_steam_path(), ENABLED_FILE)
    
    def _get_disabled_path(self) -> str:
        """Get path to disabled file."""
        return os.path.join(self._get_steam_path(), DISABLED_FILE)
    
    def _file_exists(self, enabled: bool = True) -> bool:
        """Check if the guard file exists in enabled or disabled state."""
        path = self._get_enabled_path() if enabled else self._get_disabled_path()
        return os.path.exists(path)
    
    
    def is_enabled(self) -> bool:
        """Check if the guard file is currently enabled."""
        return self._file_exists(enabled=True)
    
    def is_disabled(self) -> bool:
        """Check if the guard file is currently disabled."""
        return self._file_exists(enabled=False)
    
    def enable(self) -> Tuple[bool, str]:
        """
        Ensure the guard file is present.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            if self.is_enabled():
                return True, "Already enabled"
            
            # Since dynamic renaming is disabled, we just check existence
            # If enabled file is missing, we report it needs download
            return False, "Guard file not found"
            
        except Exception as e:
            logger.warn(f"FileGuard: Failed to enable: {e}")
            return False, str(e)
    
    def disable(self) -> Tuple[bool, str]:
        """
        No-op for disable as per new static file policy.
        
        Returns:
            Tuple of (success, message)
        """
        return True, "Disabled successfully (No-op)"
    
    def download_guard_file(self, api_client_func) -> Tuple[bool, str]:
        """
        Download the guard file from GitHub repo.
        
        Args:
            api_client_func: Function to call API for downloading
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Download to disabled path first
            dest_path = self._get_disabled_path()
            
            success, error = api_client_func(dest_path)
            
            if success:
                logger.log(f"FileGuard: Downloaded guard file to {dest_path}")
                return True, "Downloaded successfully"
            else:
                return False, error
                
        except Exception as e:
            logger.warn(f"FileGuard: Failed to download: {e}")
            return False, str(e)
    
    def ensure_correct_state(self, session_valid: bool) -> Tuple[bool, str]:
        """
        Ensure the guard file is in the correct state based on session validity.
        
        Args:
            session_valid: Whether the session is currently valid
            
        Returns:
            Tuple of (success, message)
        """
        if session_valid:
            return self.enable()
        else:
            return self.disable()
    
    def get_status(self) -> dict:
        """Get current status of the guard file."""
        return {
            "enabled": self.is_enabled(),
            "disabled": self.is_disabled(),
            "exists": self.is_enabled() or self.is_disabled(),
            "steam_path": self._get_steam_path(),
            "enabled_path": self._get_enabled_path(),
            "disabled_path": self._get_disabled_path(),
        }


# Singleton instance
_file_guard: Optional[FileGuard] = None


def get_file_guard() -> FileGuard:
    """Get the singleton FileGuard instance."""
    global _file_guard
    if _file_guard is None:
        _file_guard = FileGuard()
    return _file_guard


# Public API functions for main.py
def on_session_start(session_valid: bool) -> dict:
    """
    Called when Steam/plugin starts.
    Checks session and enables/disables guard file accordingly.
    """
    guard = get_file_guard()
    
    # First, ensure file exists
    if not guard.is_enabled() and not guard.is_disabled():
        return {
            "success": False,
            "needs_download": True,
            "message": "Guard file not found, needs download"
        }
    
    # Set correct state based on session
    success, message = guard.ensure_correct_state(session_valid)
    
    return {
        "success": success,
        "message": message,
        "status": guard.get_status()
    }


def on_session_end() -> dict:
    """
    Called when session ends (Steam closes, plugin disabled, session expires).
    Disables the guard file.
    """
    guard = get_file_guard()
    success, message = guard.disable()
    
    return {
        "success": success,
        "message": message,
        "status": guard.get_status()
    }


def download_guard_file_from_api(dest_path: str) -> Tuple[bool, str]:
    """
    Download guard file from API.
    This should be called from royal_gateway.py
    """
    # This will be implemented to use the API client
    pass


def get_guard_status() -> dict:
    """Get current guard file status."""
    guard = get_file_guard()
    return guard.get_status()


__all__ = [
    "FileGuard",
    "get_file_guard",
    "on_session_start",
    "on_session_end",
    "get_guard_status",
    "ENABLED_FILE",
    "DISABLED_FILE",
]
