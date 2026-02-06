"""Game fix lookup, application, and removal logic."""

from __future__ import annotations

import json
import os
import shutil
import threading
import zipfile
from datetime import datetime
from typing import Dict

from royal_gateway import download_fix_zip, download_with_split_support
from royal_fetcher import fetch_app_name
from throne_logger import logger
from lord_tools import ensure_temp_download_dir
from steam_realm import get_game_install_path_response

FIX_DOWNLOAD_STATE: Dict[int, Dict[str, any]] = {}
FIX_DOWNLOAD_LOCK = threading.Lock()
UNFIX_STATE: Dict[int, Dict[str, any]] = {}
UNFIX_LOCK = threading.Lock()


def _set_fix_download_state(appid: int, update: dict) -> None:
    with FIX_DOWNLOAD_LOCK:
        state = FIX_DOWNLOAD_STATE.get(appid) or {}
        state.update(update)
        FIX_DOWNLOAD_STATE[appid] = state


def _get_fix_download_state(appid: int) -> dict:
    with FIX_DOWNLOAD_LOCK:
        return FIX_DOWNLOAD_STATE.get(appid, {}).copy()


def _set_unfix_state(appid: int, update: dict) -> None:
    with UNFIX_LOCK:
        state = UNFIX_STATE.get(appid) or {}
        state.update(update)
        UNFIX_STATE[appid] = state


def _get_unfix_state(appid: int) -> dict:
    with UNFIX_LOCK:
        return UNFIX_STATE.get(appid, {}).copy()


def check_for_fixes(appid: int) -> str:
    """Check if fix exists for the game - always returns True, actual check happens on download."""
    # Fix buttons are always visible, actual existence check happens during download
    return json.dumps({"success": True, "appid": appid, "exists": True})


def _download_and_apply_lord_fix(appid: int, install_path: str, game_name: str):
    """Download and apply fix via Cloudflare API."""
    try:
        # Check if already fixed
        log_file_path = os.path.join(install_path, "LordFix.txt")
        if os.path.exists(log_file_path):
            _set_fix_download_state(appid, {"status": "failed", "error": "This Game Already Fixed"})
            return

        dest_root = ensure_temp_download_dir()
        dest_zip = os.path.join(dest_root, f"fix_{appid}.zip")
        
        _set_fix_download_state(appid, {"status": "downloading", "bytesRead": 0, "totalBytes": 0, "error": None})
        logger.log(f"SteamLord: Downloading fix for {appid} via API")

        def progress_callback(read, total):
            _set_fix_download_state(appid, {
                "status": "downloading",
                "bytesRead": read,
                "totalBytes": total
            })

        # Download via Cloudflare API (supports split archives)
        success, error = download_with_split_support(appid, dest_zip, "fix", progress_callback=progress_callback)
        
        if not success:
            _set_fix_download_state(appid, {"status": "failed", "error": error})
            return

        if _get_fix_download_state(appid).get("status") == "cancelled":
            return

        logger.log(f"SteamLord: Download complete, extracting to {install_path}")
        _set_fix_download_state(appid, {"status": "extracting"})

        extracted_files = []
        backup_dir = os.path.join(install_path, "LordFix")
        
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
                    logger.log(f"SteamLord: Backed up {member} to LordFix/")

                # Extract
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, "wb") as output:
                    output.write(archive.read(member))
                
                extracted_files.append(member)

        # Create LordFix.txt log
        try:
            with open(log_file_path, "w", encoding="utf-8") as log_file:
                log_file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                log_file.write(f"Game: {game_name}\n")
                log_file.write(f"AppID: {appid}\n")
                log_file.write("Files:\n")
                for f in extracted_files:
                    log_file.write(f"{f}\n")
            logger.log(f"SteamLord: Created LordFix.txt with {len(extracted_files)} files")
        except Exception as exc:
            logger.warn(f"SteamLord: Failed to create LordFix.txt: {exc}")

        _set_fix_download_state(appid, {"status": "done", "success": True})
        
        # Increment stat on success
        try:
            from kingdom_records import increment_stat
            increment_stat('online_fix_count')
        except:
            pass
        
        try:
            os.remove(dest_zip)
        except Exception:
            pass

    except Exception as exc:
        if str(exc) == "cancelled":
            _set_fix_download_state(appid, {"status": "cancelled", "success": False, "error": "Cancelled by user"})
            return
        logger.warn(f"SteamLord: Failed to apply fix: {exc}")
        _set_fix_download_state(appid, {"status": "failed", "error": str(exc)})


def apply_game_fix(appid: int, download_url: str, install_path: str, fix_type: str = "", game_name: str = "") -> str:
    """Start applying a fix to a game."""
    try:
        appid = int(appid)
    except Exception:
        return json.dumps({"success": False, "error": "Invalid appid"})

    if not install_path or not os.path.exists(install_path):
        return json.dumps({"success": False, "error": "Install path not found"})

    # Local validation to avoid unnecessary API requests
    from royal_auth import can_download_local
    can_download, error_code = can_download_local("fix")
    if not can_download:
        error_messages = {
            "NOT_ACTIVATED": "Activation Required",
            "SESSION_EXPIRED": "Session Timeout: Re-login",
            "FIX_LIMIT_REACHED": "Fix Limit Reached",
            "FEATURE_DISABLED": "Online Fix Locked: Upgrade Now",
        }
        error_msg = error_messages.get(error_code, f"Cannot apply fix: {error_code}")
        _set_fix_download_state(appid, {"status": "failed", "error": error_msg})
        return json.dumps({"success": False, "error": error_msg})

    _set_fix_download_state(appid, {"status": "queued", "bytesRead": 0, "totalBytes": 0, "error": None})
    thread = threading.Thread(
        target=_download_and_apply_lord_fix, args=(appid, install_path, game_name), daemon=True
    )
    thread.start()
    return json.dumps({"success": True})


def get_apply_fix_status(appid: int) -> str:
    try:
        appid = int(appid)
    except Exception:
        return json.dumps({"success": False, "error": "Invalid appid"})
    return json.dumps({"success": True, "state": _get_fix_download_state(appid)})


def cancel_apply_fix(appid: int) -> str:
    try:
        appid = int(appid)
    except Exception:
        return json.dumps({"success": False, "error": "Invalid appid"})
    _set_fix_download_state(appid, {"status": "cancelled", "error": "Cancelled by user"})
    return json.dumps({"success": True})


def _remove_lord_fix_worker(appid: int, install_path: str):
    """Remove fix files and restore backups."""
    try:
        log_file_path = os.path.join(install_path, "LordFix.txt")
        if not os.path.exists(log_file_path):
            _set_unfix_state(appid, {"status": "failed", "error": "This Game Dont Have Fix to Remove it"})
            return

        _set_unfix_state(appid, {"status": "removing", "progress": "Reading log..."})
        
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
            _set_unfix_state(appid, {"status": "failed", "error": f"Failed to read log: {e}"})
            return

        # Delete files
        _set_unfix_state(appid, {"status": "removing", "progress": f"Removing {len(files_to_delete)} files..."})
        for rel_path in files_to_delete:
            full_path = os.path.join(install_path, rel_path)
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                except Exception:
                    pass
        
        # Restore backups
        backup_dir = os.path.join(install_path, "LordFix")
        if os.path.exists(backup_dir):
            _set_unfix_state(appid, {"status": "removing", "progress": "Restoring original files..."})
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
            
            # Remove LordFix folder
            try:
                shutil.rmtree(backup_dir)
            except Exception:
                pass

        # Remove log
        try:
            os.remove(log_file_path)
        except Exception:
            pass

        _set_unfix_state(appid, {"status": "done", "success": True})

    except Exception as e:
        _set_unfix_state(appid, {"status": "failed", "error": str(e)})


def unfix_game(appid: int, install_path: str = "") -> str:
    """Start removing a fix from a game."""
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

    _set_unfix_state(appid, {"status": "queued", "progress": "Starting...", "error": None})
    thread = threading.Thread(target=_remove_lord_fix_worker, args=(appid, install_path), daemon=True)
    thread.start()
    return json.dumps({"success": True})


def get_unfix_status(appid: int) -> str:
    try:
        appid = int(appid)
    except Exception:
        return json.dumps({"success": False, "error": "Invalid appid"})
    return json.dumps({"success": True, "state": _get_unfix_state(appid)})


def get_all_active_fixes() -> Dict[int, Dict]:
    """Get all active fix operations."""
    active = {}
    with FIX_DOWNLOAD_LOCK:
        for appid, state in FIX_DOWNLOAD_STATE.items():
            status = state.get("status")
            if status in {"queued", "downloading", "extracting"}:
                active[appid] = state.copy()
    
    with UNFIX_LOCK:
        for appid, state in UNFIX_STATE.items():
            status = state.get("status")
            if status in {"queued", "removing"}:
                # Merge into active with a type flag if needed, usually just appid key is enough
                # But task types are separate in frontend
                pass 
                # Actually frontend treats fix and unfix as same 'fix' task type usually
                # But for dock persistence we care mostly about download/apply progress
                if appid not in active:
                    active[appid] = state.copy()
    return active


__all__ = [
    "apply_game_fix",
    "cancel_apply_fix",
    "check_for_fixes",
    "get_apply_fix_status",
    "get_unfix_status",
    "unfix_game",
]
