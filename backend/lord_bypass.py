"""Game bypass lookup, application, and removal logic."""

from __future__ import annotations

import json
import os
import shutil
import threading
import zipfile
from datetime import datetime
from typing import Dict

from royal_gateway import download_bypass_zip, download_with_split_support, download_bypass_status_json
from throne_logger import logger
from lord_tools import ensure_temp_download_dir
from steam_realm import get_game_install_path_response

BYPASS_DOWNLOAD_STATE: Dict[int, Dict[str, any]] = {}
BYPASS_DOWNLOAD_LOCK = threading.Lock()
REMOVE_BYPASS_STATE: Dict[int, Dict[str, any]] = {}
REMOVE_BYPASS_LOCK = threading.Lock()


def _set_bypass_download_state(appid: int, update: dict) -> None:
    with BYPASS_DOWNLOAD_LOCK:
        state = BYPASS_DOWNLOAD_STATE.get(appid) or {}
        state.update(update)
        BYPASS_DOWNLOAD_STATE[appid] = state


def _get_bypass_download_state(appid: int) -> dict:
    with BYPASS_DOWNLOAD_LOCK:
        return BYPASS_DOWNLOAD_STATE.get(appid, {}).copy()


def _set_remove_bypass_state(appid: int, update: dict) -> None:
    with REMOVE_BYPASS_LOCK:
        state = REMOVE_BYPASS_STATE.get(appid) or {}
        state.update(update)
        REMOVE_BYPASS_STATE[appid] = state


def _get_remove_bypass_state(appid: int) -> dict:
    with REMOVE_BYPASS_LOCK:
        return REMOVE_BYPASS_STATE.get(appid, {}).copy()


def _get_bypass_game_info(appid: int) -> dict:
    """Read game info from BypassStatus.json for the given appid."""
    try:
        status_path = os.path.join(os.path.dirname(__file__), "BypassStatus.json")
        if not os.path.exists(status_path):
            return None
        
        with open(status_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # BypassStatus.json has appid as string keys
        appid_str = str(appid)
        if appid_str in data:
            return data[appid_str]
        
        return None
    except Exception as exc:
        logger.warn(f"SteamLord: Failed to read BypassStatus.json: {exc}")
        return None


def _download_and_apply_bypass(appid: int, install_path: str):
    """Download and apply bypass via Cloudflare API."""
    try:
        # Check if already bypassed
        log_file_path = os.path.join(install_path, "LordBaypass.txt")
        if os.path.exists(log_file_path):
            _set_bypass_download_state(appid, {"status": "failed", "error": "This Game Already Baypassed"})
            return

        dest_root = ensure_temp_download_dir()
        dest_zip = os.path.join(dest_root, f"bypass_{appid}.zip")
        
        # Download BypassStatus.json (fresh copy each time)
        status_path = os.path.join(os.path.dirname(__file__), "BypassStatus.json")
        try:
            success_status, _ = download_bypass_status_json(status_path)
            if success_status:
                logger.log(f"SteamLord: Downloaded fresh BypassStatus.json")
        except Exception as exc:
            logger.warn(f"SteamLord: Failed to download BypassStatus.json: {exc}")
        
        _set_bypass_download_state(appid, {"status": "downloading", "bytesRead": 0, "totalBytes": 0, "error": None})
        logger.log(f"SteamLord: Downloading bypass for {appid} via API")

        def progress_callback(read, total):
            _set_bypass_download_state(appid, {
                "status": "downloading",
                "bytesRead": read,
                "totalBytes": total
            })

        # Download via Cloudflare API (supports split archives)
        success, error = download_with_split_support(appid, dest_zip, "bypass", progress_callback=progress_callback)
        
        if not success:
            _set_bypass_download_state(appid, {"status": "failed", "error": error})
            return

        if _get_bypass_download_state(appid).get("status") == "cancelled":
            return

        logger.log(f"SteamLord: Download complete, extracting to {install_path}")
        _set_bypass_download_state(appid, {"status": "extracting"})

        extracted_files = []
        backup_dir = os.path.join(install_path, "LordBaypass")
        
        with zipfile.ZipFile(dest_zip, "r") as archive:
            for member in archive.namelist():
                if member.endswith("/"):
                    continue
                
                # Determine target path
                target_path = os.path.join(install_path, member)
                
                # Backup logic
                if os.path.exists(target_path):
                    os.makedirs(backup_dir, exist_ok=True)
                    backup_path = os.path.join(backup_dir, member)
                    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                    shutil.move(target_path, backup_path)
                    logger.log(f"SteamLord: Backed up {member} to LordBaypass/")

                # Extract
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, "wb") as output:
                    output.write(archive.read(member))
                
                extracted_files.append(member)

        # Create LordBaypass.txt log
        try:
            with open(log_file_path, "w", encoding="utf-8") as log_file:
                log_file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                log_file.write(f"AppID: {appid}\n")
                log_file.write("Files:\n")
                for f in extracted_files:
                    log_file.write(f"{f}\n")
            logger.log(f"SteamLord: Created LordBaypass.txt with {len(extracted_files)} files")
        except Exception as exc:
            logger.warn(f"SteamLord: Failed to create LordBaypass.txt: {exc}")

        # Get game info from BypassStatus.json
        game_info = _get_bypass_game_info(appid)
        
        _set_bypass_download_state(appid, {"status": "done", "success": True, "gameInfo": game_info})
        
        # Increment stat on success
        try:
            from kingdom_records import increment_stat
            increment_stat('bypass_count')
        except:
            pass
        
        try:
            os.remove(dest_zip)
        except Exception:
            pass

    except Exception as exc:
        if str(exc) == "cancelled":
            _set_bypass_download_state(appid, {"status": "cancelled", "success": False, "error": "Cancelled by user"})
            return
        logger.warn(f"SteamLord: Failed to apply bypass: {exc}")
        _set_bypass_download_state(appid, {"status": "failed", "error": str(exc)})


def apply_bypass(appid: int, install_path: str) -> str:
    """Start applying a bypass to a game."""
    try:
        appid = int(appid)
    except Exception:
        return json.dumps({"success": False, "error": "Invalid appid"})

    if not install_path or not os.path.exists(install_path):
        return json.dumps({"success": False, "error": "Install path not found"})

    # Local validation to avoid unnecessary API requests
    from royal_auth import can_download_local
    can_download, error_code = can_download_local("bypass")
    if not can_download:
        error_messages = {
            "NOT_ACTIVATED": "Activation Required",
            "SESSION_EXPIRED": "Session Timeout: Re-login",
            "BYPASS_NOT_ALLOWED": "Bypass Locked: Upgrade Now",
            "FEATURE_DISABLED": "Bypass Locked: Upgrade Now",
            "BYPASS_LIMIT_REACHED": "Bypass Limit Reached",
        }
        error_msg = error_messages.get(error_code, f"Cannot apply bypass: {error_code}")
        _set_bypass_download_state(appid, {"status": "failed", "error": error_msg})
        return json.dumps({"success": False, "error": error_msg})

    _set_bypass_download_state(appid, {"status": "queued", "bytesRead": 0, "totalBytes": 0, "error": None})
    thread = threading.Thread(
        target=_download_and_apply_bypass, args=(appid, install_path), daemon=True
    )
    thread.start()
    return json.dumps({"success": True})


def get_apply_bypass_status(appid: int) -> str:
    try:
        appid = int(appid)
    except Exception:
        return json.dumps({"success": False, "error": "Invalid appid"})
    return json.dumps({"success": True, "state": _get_bypass_download_state(appid)})


def _remove_bypass_worker(appid: int, install_path: str):
    """Remove bypass files and restore backups."""
    try:
        log_file_path = os.path.join(install_path, "LordBaypass.txt")
        if not os.path.exists(log_file_path):
            _set_remove_bypass_state(appid, {"status": "failed", "error": "This Game Dont Have Bypass to Remove it"})
            return

        _set_remove_bypass_state(appid, {"status": "removing", "progress": "Reading log..."})
        
        files_to_delete = []
        try:
            with open(log_file_path, "r", encoding="utf-8") as f:
                reading_files = False
                for line in f:
                    line = line.strip()
                    if line == "Files:":
                        reading_files = True
                        continue
                    if reading_files and line:
                        files_to_delete.append(line)
        except Exception as e:
            _set_remove_bypass_state(appid, {"status": "failed", "error": f"Failed to read log: {e}"})
            return

        # Delete files
        _set_remove_bypass_state(appid, {"status": "removing", "progress": f"Removing {len(files_to_delete)} files..."})
        for rel_path in files_to_delete:
            full_path = os.path.join(install_path, rel_path)
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                except Exception:
                    pass
        
        # Restore backups
        backup_dir = os.path.join(install_path, "LordBaypass")
        if os.path.exists(backup_dir):
            _set_remove_bypass_state(appid, {"status": "removing", "progress": "Restoring original files..."})
            for root, dirs, files in os.walk(backup_dir):
                for file in files:
                    backup_file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(backup_file_path, backup_dir)
                    target_path = os.path.join(install_path, rel_path)
                    
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    try:
                        shutil.move(backup_file_path, target_path)
                    except Exception as e:
                        logger.warn(f"Failed to restore {rel_path}: {e}")
            
            # Remove LordBaypass folder
            try:
                shutil.rmtree(backup_dir)
            except Exception:
                pass

        # Remove log
        try:
            os.remove(log_file_path)
        except Exception:
            pass

        _set_remove_bypass_state(appid, {"status": "done", "success": True})

    except Exception as e:
        _set_remove_bypass_state(appid, {"status": "failed", "error": str(e)})


def remove_bypass(appid: int, install_path: str = "") -> str:
    """Start removing a bypass from a game."""
    try:
        appid = int(appid)
    except Exception:
        return json.dumps({"success": False, "error": "Invalid appid"})

    if not install_path:
        res = get_game_install_path_response(appid)
        if res.get("success"):
            install_path = res["installPath"]
        else:
            return json.dumps({"success": False, "error": "Could not find game path"})

    _set_remove_bypass_state(appid, {"status": "queued", "progress": "Starting...", "error": None})
    thread = threading.Thread(target=_remove_bypass_worker, args=(appid, install_path), daemon=True)
    thread.start()
    return json.dumps({"success": True})


def get_remove_bypass_status(appid: int) -> str:
    try:
        appid = int(appid)
    except Exception:
        return json.dumps({"success": False, "error": "Invalid appid"})
    return json.dumps({"success": True, "state": _get_remove_bypass_state(appid)})


def get_all_active_bypasses() -> Dict[int, Dict]:
    """Get all active bypass operations."""
    active = {}
    with BYPASS_DOWNLOAD_LOCK:
        for appid, state in BYPASS_DOWNLOAD_STATE.items():
            status = state.get("status")
            if status in {"queued", "downloading", "extracting"}:
                active[appid] = state.copy()
    
    with REMOVE_BYPASS_LOCK:
        for appid, state in REMOVE_BYPASS_STATE.items():
            status = state.get("status")
            if status in {"queued", "removing"}:
                if appid not in active:
                    active[appid] = state.copy()
    return active


__all__ = [
    "apply_bypass",
    "get_apply_bypass_status",
    "remove_bypass",
    "get_remove_bypass_status",
]
