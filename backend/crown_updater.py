"""Automatic plugin update logic."""

from __future__ import annotations

import json
import os
import shutil
import threading
import time
import subprocess
import zipfile
from typing import Optional, Dict

import Millennium  # type: ignore

from royal_gateway import get_latest_update, download_update_zip
from kingdom_config import (
    UPDATE_CHECK_INTERVAL_SECONDS,
    UPDATE_PENDING_ZIP,
    UPDATE_PENDING_INFO,
)
from throne_logger import logger
from kingdom_paths import backend_path
from lord_tools import get_plugin_version, parse_version

# Flag to track if restart is required
_RESTART_REQUIRED = False
_RESTART_LOCK = threading.Lock()

# Background check thread
_background_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()


def _get_pending_update_zip_path() -> str:
    return backend_path(UPDATE_PENDING_ZIP)


def _get_pending_update_info_path() -> str:
    return backend_path(UPDATE_PENDING_INFO)


def is_restart_required() -> str:
    global _RESTART_REQUIRED
    with _RESTART_LOCK:
        return json.dumps({"success": True, "required": _RESTART_REQUIRED})


def set_restart_required(val: bool = True) -> None:
    global _RESTART_REQUIRED
    with _RESTART_LOCK:
        _RESTART_REQUIRED = val


def apply_pending_update_if_any() -> None:
    """Apply any pending update at startup."""
    try:
        zip_path = _get_pending_update_zip_path()
        info_path = _get_pending_update_info_path()
        
        if not os.path.exists(zip_path):
            return
        
        logger.log(f"SteamLord: Found pending update at {zip_path}")
        
        # Get the plugin directory (parent of backend)
        plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        
        try:
            with zipfile.ZipFile(zip_path, "r") as archive:
                for member in archive.namelist():
                    # Skip if it's just a directory entry
                    if member.endswith("/"):
                        continue
                    
                    # Determine target path
                    # Handle if zip has a root folder like "ltsteamplugin/"
                    parts = member.split("/")
                    if len(parts) > 1 and parts[0] in ("ltsteamplugin", "SteamLord"):
                        rel_path = "/".join(parts[1:])
                    else:
                        rel_path = member
                    
                    if not rel_path:
                        continue

                    # Skip .git files
                    if ".git" in rel_path or ".git" in member:
                        continue
                    
                    target_path = os.path.join(plugin_dir, rel_path)
                    
                    try:
                        # Create parent directories
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        
                        # Extract file
                        with open(target_path, "wb") as f:
                            f.write(archive.read(member))
                    except Exception as write_exc:
                        logger.warn(f"SteamLord: Failed to update file {rel_path}: {write_exc}")
                        # Continue updating other files
                
                logger.log("SteamLord: Pending update applied (errors logged if any)")
        except Exception as exc:
            logger.warn(f"SteamLord: Failed to apply pending update: {exc}")
        
        # Clean up
        try:
            os.remove(zip_path)
        except Exception:
            pass
        try:
            os.remove(info_path)
        except Exception:
            pass
            
    except Exception as exc:
        logger.warn(f"SteamLord: apply_pending_update_if_any failed: {exc}")


def _check_for_update() -> Optional[Dict]:
    """Check for updates via Cloudflare API."""
    try:
        current_version = get_plugin_version()
        logger.log(f"SteamLord: Checking for updates. Current version: {current_version}")
        
        update_info = get_latest_update()
        if not update_info:
            logger.log("SteamLord: No update info available")
            return None
        
        remote_version = update_info.get("version", "")
        if not remote_version:
            return None
        
        current_parsed = parse_version(current_version)
        remote_parsed = parse_version(remote_version)
        
        if remote_parsed > current_parsed:
            logger.log(f"SteamLord: Update available: {current_version} -> {remote_version}")
            return update_info
        else:
            logger.log(f"SteamLord: No update needed. Remote: {remote_version}")
            return None
            
    except Exception as exc:
        logger.warn(f"SteamLord: _check_for_update failed: {exc}")
        return None


def _download_and_stage_update(update_info: Dict) -> bool:
    """Download update and stage it for next restart."""
    try:
        assets = update_info.get("assets", [])
        if not assets:
            logger.warn("SteamLord: No assets in update")
            return False
        
        # Find the zip file
        zip_asset = None
        for asset in assets:
            name = asset.get("name", "").lower()
            if name.endswith(".zip") and "steamlord" in name:
                zip_asset = asset
                break
        
        if not zip_asset:
            zip_asset = assets[0]  # Fallback to first asset
        
        download_endpoint = zip_asset.get("download_endpoint")
        if not download_endpoint:
            logger.warn("SteamLord: No download endpoint in asset")
            return False
        
        dest_path = _get_pending_update_zip_path()
        logger.log(f"SteamLord: Downloading update to {dest_path}")
        
        success, error = download_update_zip(download_endpoint, dest_path)
        
        if not success:
            logger.warn(f"SteamLord: Failed to download update: {error}")
            return False
        
        # Save update info
        info_path = _get_pending_update_info_path()
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(update_info, f)
        
        logger.log("SteamLord: Update staged successfully")
        set_restart_required(True)
        return True
        
    except Exception as exc:
        logger.warn(f"SteamLord: _download_and_stage_update failed: {exc}")
        return False


def _background_update_check():
    """Background thread for periodic update checks."""
    while not _stop_event.is_set():
        try:
            update_info = _check_for_update()
            if update_info:
                _download_and_stage_update(update_info)
        except Exception as exc:
            logger.warn(f"SteamLord: Background update check failed: {exc}")
        
        # Wait for interval or stop event
        _stop_event.wait(UPDATE_CHECK_INTERVAL_SECONDS)


def start_auto_update_background_check():
    """Start the background update check thread."""
    global _background_thread
    
    if _background_thread is not None and _background_thread.is_alive():
        return
    
    _stop_event.clear()
    _background_thread = threading.Thread(target=_background_update_check, daemon=True)
    _background_thread.start()
    logger.log("SteamLord: Started background update check")


def stop_auto_update_background_check():
    """Stop the background update check thread."""
    global _background_thread
    _stop_event.set()
    if _background_thread is not None:
        _background_thread.join(timeout=2)
    _background_thread = None


def check_for_update_now() -> str:
    """Manually check for updates."""
    try:
        update_info = _check_for_update()
        if update_info:
            return json.dumps({
                "success": True,
                "updateAvailable": True,
                "version": update_info.get("version"),
            })
        return json.dumps({"success": True, "updateAvailable": False})
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})


def trigger_update_download() -> str:
    """Manually trigger update download."""
    try:
        update_info = _check_for_update()
        if not update_info:
            return json.dumps({"success": False, "error": "No update available"})
        
        if _download_and_stage_update(update_info):
            return json.dumps({"success": True, "version": update_info.get("version")})
        else:
            return json.dumps({"success": False, "error": "Download failed"})
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})


def restart_steam() -> str:
    """Restart Steam to apply updates."""
    try:
        import Millennium  # type: ignore
        steam_path = Millennium.steam_path()
        steam_exe = os.path.join(steam_path, "Steam.exe") if steam_path else "steam.exe"
        
        cmd_path = backend_path("realm_restart.cmd")
        
        # Use simple wmic/taskkill logic directly in Python to avoid cmd window if possible
        # Or use CREATE_NO_WINDOW with the cmd file
        
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE # 0
        
        if os.path.exists(cmd_path):
            subprocess.Popen(
                [cmd_path],
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                startupinfo=startupinfo
            )
        else:
            # Fallback: kill and restart Steam silently
            # We use a detached process that waits then starts steam
            command = f'taskkill /IM steam.exe /F && timeout /t 3 && start "" "{steam_exe}"'
            subprocess.Popen(
                command,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
        return json.dumps({"success": True})
    except Exception as exc:
        logger.warn(f"SteamLord: restart_steam failed: {exc}")
        return json.dumps({"success": False, "error": str(exc)})


__all__ = [
    "apply_pending_update_if_any",
    "check_for_update_now",
    "is_restart_required",
    "restart_steam",
    "set_restart_required",
    "start_auto_update_background_check",
    "stop_auto_update_background_check",
    "trigger_update_download",
]
