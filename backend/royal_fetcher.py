"""Handling of SteamLord add/download flows and related utilities."""

from __future__ import annotations

import base64
import json
import os
import re
import threading
import time
import shutil
import tempfile
from typing import Dict

import Millennium  # type: ignore

from royal_gateway import (
    create_game_request,
    download_game_zip,
    download_game_json,
    download_with_split_support,
    get_api_client,
)
from kingdom_config import (
    APPID_LOG_FILE,
    LOADED_APPS_FILE,
    USER_AGENT,
    WEBKIT_DIR_NAME,
    WEB_UI_ICON_FILE,
    HTTP_TIMEOUT_SECONDS,
)
from throne_logger import logger
from kingdom_paths import backend_path, public_path
from steam_realm import detect_steam_install_path, has_lua_for_app
from herald import add_pending_game


DOWNLOAD_STATE: Dict[int, Dict[str, any]] = {}
DOWNLOAD_LOCK = threading.Lock()


def _set_download_state(appid: int, update: dict) -> None:
    with DOWNLOAD_LOCK:
        state = DOWNLOAD_STATE.get(appid) or {}
        state.update(update)
        DOWNLOAD_STATE[appid] = state


def _get_download_state(appid: int) -> dict:
    with DOWNLOAD_LOCK:
        return DOWNLOAD_STATE.get(appid, {}).copy()


def _loaded_apps_path() -> str:
    return backend_path(LOADED_APPS_FILE)


def _appid_log_path() -> str:
    return backend_path(APPID_LOG_FILE)


def _fetch_app_name(appid: int) -> str:
    """Fetch game name from Steam API."""
    try:
        client = get_api_client()
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
        resp = client.get(url, follow_redirects=True, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        entry = data.get(str(appid)) or data.get(int(appid)) or {}
        if isinstance(entry, dict):
            inner = entry.get("data") or {}
            name = inner.get("name")
            if isinstance(name, str) and name.strip():
                return name.strip()
    except Exception as exc:
        logger.warn(f"SteamLord: _fetch_app_name failed for {appid}: {exc}")
    return ""


def _append_loaded_app(appid: int, name: str) -> None:
    try:
        path = _loaded_apps_path()
        lines = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                lines = handle.read().splitlines()
        prefix = f"{appid}:"
        lines = [line for line in lines if not line.startswith(prefix)]
        
        # Fetch name if not provided
        if not name:
            name = _fetch_app_name(appid) or f"Game {appid}"
        
        lines.append(f"{appid}:{name}")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
        
        # Increment stat on success
        try:
            from kingdom_records import increment_stat
            increment_stat('downloads_count')
        except:
            pass

    except Exception as exc:
        logger.warn(f"SteamLord: _append_loaded_app failed for {appid}: {exc}")


def _remove_loaded_app(appid: int) -> None:
    try:
        path = _loaded_apps_path()
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()
        prefix = f"{appid}:"
        new_lines = [line for line in lines if not line.startswith(prefix)]
        if len(new_lines) != len(lines):
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("\n".join(new_lines) + ("\n" if new_lines else ""))
    except Exception as exc:
        logger.warn(f"SteamLord: _remove_loaded_app failed for {appid}: {exc}")


def _log_appid_event(action: str, appid: int, name: str) -> None:
    try:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        line = f"[{action}] {appid} - {name} - {stamp}\n"
        with open(_appid_log_path(), "a", encoding="utf-8") as handle:
            handle.write(line)
    except Exception as exc:
        logger.warn(f"SteamLord: _log_appid_event failed: {exc}")


def _get_loaded_app_name(appid: int) -> str:
    try:
        path = _loaded_apps_path()
        if not os.path.exists(path):
            return ""
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle.read().splitlines():
                if line.startswith(f"{appid}:"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        return ""
    return ""


def fetch_app_name(appid: int) -> str:
    return _fetch_app_name(appid)


def _is_download_cancelled(appid: int) -> bool:
    try:
        return _get_download_state(appid).get("status") == "cancelled"
    except Exception:
        return False


def _process_and_install_lua(appid: int, zip_path: str) -> None:
    """Extract and install lua and manifest files from downloaded zip."""
    import zipfile
    
    if _is_download_cancelled(appid):
        raise RuntimeError("cancelled")

    base_path = detect_steam_install_path() or Millennium.steam_path()
    target_dir = os.path.join(base_path or "", "config", "stplug-in")
    os.makedirs(target_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as archive:
        names = archive.namelist()
        
        # Extract manifest files to depotcache
        try:
            depotcache_dir = os.path.join(base_path or "", "depotcache")
            os.makedirs(depotcache_dir, exist_ok=True)
            for name in names:
                try:
                    if _is_download_cancelled(appid):
                        raise RuntimeError("cancelled")
                    if name.lower().endswith(".manifest"):
                        pure = os.path.basename(name)
                        data = archive.read(name)
                        out_path = os.path.join(depotcache_dir, pure)
                        with open(out_path, "wb") as manifest_file:
                            manifest_file.write(data)
                        logger.log(f"SteamLord: Extracted manifest -> {out_path}")
                except Exception as manifest_exc:
                    logger.warn(f"SteamLord: Failed to extract manifest {name}: {manifest_exc}")
        except Exception as depot_exc:
            logger.warn(f"SteamLord: depotcache extraction failed: {depot_exc}")

        # Find and extract lua file
        candidates = []
        for name in names:
            pure = os.path.basename(name)
            if re.fullmatch(r"\d+\.lua", pure):
                candidates.append(name)

        if _is_download_cancelled(appid):
            raise RuntimeError("cancelled")

        chosen = None
        preferred = f"{appid}.lua"
        for name in candidates:
            if os.path.basename(name) == preferred:
                chosen = name
                break
        if chosen is None and candidates:
            chosen = candidates[0]
        if not chosen:
            raise RuntimeError("No numeric .lua file found in zip")

        data = archive.read(chosen)
        try:
            text = data.decode("utf-8")
        except Exception:
            text = data.decode("utf-8", errors="replace")

        _set_download_state(appid, {"status": "installing"})
        dest_file = os.path.join(target_dir, f"{appid}.lua")
        
        if _is_download_cancelled(appid):
            raise RuntimeError("cancelled")
        
        with open(dest_file, "w", encoding="utf-8") as output:
            output.write(text)
        logger.log(f"SteamLord: Installed lua -> {dest_file}")
        _set_download_state(appid, {"installedPath": dest_file})

    try:
        os.remove(zip_path)
    except Exception:
        pass


def ensure_temp_download_dir() -> str:
    """Ensure and return a directory path to store temporary downloads."""
    try:
        tmp = tempfile.gettempdir()
        dest = os.path.join(tmp, "stplug-in-download")
        os.makedirs(dest, exist_ok=True)
        return dest
    except Exception:
        try:
            dest = backend_path("temp-download")
            os.makedirs(dest, exist_ok=True)
            return dest
        except Exception:
            return "."


def SteamLord_Add(appid: int) -> str:
    """Start downloading a game via Cloudflare API."""
    try:
        appid = int(appid)
    except Exception:
        return json.dumps({"success": False, "error": "Invalid appid"})

    # Local validation to avoid unnecessary API requests
    from royal_auth import can_download_local
    can_download, error_code = can_download_local("game")
    if not can_download:
        error_messages = {
            "NOT_ACTIVATED": "Activation Required",
            "SESSION_EXPIRED": "Session Timeout: Re-login",
            "DOWNLOAD_LIMIT_REACHED": "Daily Limit Reached",
        }
        error_msg = error_messages.get(error_code, f"Cannot download: {error_code}")
        _set_download_state(appid, {"status": "failed", "error": error_msg})
        return json.dumps({"success": False, "error": error_msg})

    logger.log(f"SteamLord: StartAddViaSteamLord appid={appid}")
    _set_download_state(appid, {"status": "queued", "bytesRead": 0, "totalBytes": 0})
    thread = threading.Thread(target=_download_zip_for_app, args=(appid,), daemon=True)
    thread.start()
    return json.dumps({"success": True})


def get_add_status(appid: int) -> str:
    try:
        appid = int(appid)
    except Exception:
        return json.dumps({"success": False, "error": "Invalid appid"})
    state = _get_download_state(appid)
    return json.dumps({"success": True, "state": state})


def get_all_active_downloads() -> Dict[int, Dict]:
    """Get all active downloads that are starting, downloading, or installing."""
    active = {}
    with DOWNLOAD_LOCK:
        for appid, state in DOWNLOAD_STATE.items():
            status = state.get("status")
            if status in {"queued", "checking", "downloading", "installing"}:
                active[appid] = state.copy()
    return active


def read_loaded_apps() -> str:
    try:
        path = _loaded_apps_path()
        entries = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                for line in handle.read().splitlines():
                    if ":" in line:
                        appid_str, name = line.split(":", 1)
                        appid_str = appid_str.strip()
                        name = name.strip()
                        if appid_str.isdigit() and name:
                            entries.append({"appid": int(appid_str), "name": name})
        return json.dumps({"success": True, "apps": entries})
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})


def dismiss_loaded_apps() -> str:
    try:
        path = _loaded_apps_path()
        if os.path.exists(path):
            os.remove(path)
        return json.dumps({"success": True})
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})


def SteamLord_Delete(appid: int) -> str:
    """Delete all SteamLord files for a game."""
    try:
        appid = int(appid)
    except Exception:
        return json.dumps({"success": False, "error": "Invalid appid"})

    base = detect_steam_install_path() or Millennium.steam_path()
    deleted = []

    # 1. Delete LUA files
    target_dir = os.path.join(base or "", "config", "stplug-in")
    lua_paths = [
        os.path.join(target_dir, f"{appid}.lua"),
        os.path.join(target_dir, f"{appid}.lua.disabled"),
    ]
    for path in lua_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                deleted.append(path)
        except Exception as exc:
            logger.warn(f"SteamLord: Failed to delete {path}: {exc}")

    # 2. Delete Manifest files
    depot_dir = os.path.join(base or "", "depotcache")
    if os.path.isdir(depot_dir):
        try:
            for fname in os.listdir(depot_dir):
                if str(appid) in fname and fname.lower().endswith(".manifest"):
                    full_path = os.path.join(depot_dir, fname)
                    try:
                        os.remove(full_path)
                        deleted.append(full_path)
                    except Exception as e:
                        logger.warn(f"SteamLord: Failed to delete manifest {fname}: {e}")
        except Exception as e:
            logger.warn(f"SteamLord: Failed to list depotcache: {e}")

    # 3. Delete JSON from Update Release
    update_release_dir = backend_path("Update Release")
    json_path = os.path.join(update_release_dir, f"{appid}.json")
    try:
        if os.path.exists(json_path):
            os.remove(json_path)
            deleted.append(json_path)
    except Exception as e:
        logger.warn(f"SteamLord: Failed to delete json {json_path}: {e}")

    # 4. Clean up logs
    try:
        name = _get_loaded_app_name(appid) or _fetch_app_name(appid) or f"UNKNOWN ({appid})"
        _remove_loaded_app(appid)
        if deleted:
            _log_appid_event("REMOVED", appid, name)
    except Exception:
        pass

    return json.dumps({"success": True, "deleted": deleted, "count": len(deleted)})


def get_icon_data_url() -> str:
    try:
        steam_ui_path = os.path.join(Millennium.steam_path(), "steamui", WEBKIT_DIR_NAME)
        icon_path = os.path.join(steam_ui_path, WEB_UI_ICON_FILE)
        if not os.path.exists(icon_path):
            icon_path = public_path(WEB_UI_ICON_FILE)
        with open(icon_path, "rb") as handle:
            data = handle.read()
        b64 = base64.b64encode(data).decode("ascii")
        return json.dumps({"success": True, "dataUrl": f"data:image/png;base64,{b64}"})
    except Exception as exc:
        logger.warn(f"SteamLord: GetIconDataUrl failed: {exc}")
        return json.dumps({"success": False, "error": str(exc)})


def SteamLord_Found(appid: int) -> str:
    try:
        appid = int(appid)
    except Exception:
        return json.dumps({"success": False, "error": "Invalid appid"})
    exists = has_lua_for_app(appid)
    logger.log(f"SteamLord: HasSteamLordForApp appid={appid} -> {exists}")
    return json.dumps({"success": True, "exists": exists})


def SteamLord_Cancel(appid: int) -> str:
    try:
        appid = int(appid)
    except Exception:
        return json.dumps({"success": False, "error": "Invalid appid"})

    state = _get_download_state(appid)
    if not state or state.get("status") in {"done", "failed"}:
        return json.dumps({"success": True, "message": "Nothing to cancel"})

    _set_download_state(appid, {"status": "cancelled", "error": "Cancelled by user"})
    logger.log(f"SteamLord: Cancellation requested for appid={appid}")
    return json.dumps({"success": True})


def _save_game_json(appid: int) -> None:
    """Download and save the game JSON metadata."""
    try:
        json_data = download_game_json(appid)
        if json_data:
            dest_dir = backend_path("Update Release")
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, f"{appid}.json")
            with open(dest_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            logger.log(f"SteamLord: Saved game JSON to {dest_path}")
    except Exception as exc:
        logger.warn(f"SteamLord: Failed to save game JSON for {appid}: {exc}")


def _download_zip_for_app(appid: int) -> None:
    """Download game zip via Cloudflare API."""
    dest_root = ensure_temp_download_dir()
    dest_path = os.path.join(dest_root, f"{appid}.zip")
    
    _set_download_state(
        appid,
        {"status": "checking", "bytesRead": 0, "totalBytes": 0, "dest": dest_path},
    )

    try:
        # Download via Cloudflare API (supports both single and split archives)
        logger.log(f"SteamLord: Downloading game {appid} via API")
        
        def progress_callback(read: int, total: int):
            _set_download_state(appid, {
                "status": "downloading",
                "bytesRead": read,
                "totalBytes": total
            })
            
        _set_download_state(appid, {"status": "downloading", "bytesRead": 0, "totalBytes": 0})
        
        success, error = download_with_split_support(appid, dest_path, "download", progress_callback=progress_callback)
        
        if _is_download_cancelled(appid):
            return
        
        if success:
            logger.log(f"SteamLord: Downloaded zip to {dest_path}")
            _process_and_install_lua(appid, dest_path)
            _save_game_json(appid)
            
            # Get game name and add to loaded apps
            name = _fetch_app_name(appid) or f"Game {appid}"
            _append_loaded_app(appid, name)
            _log_appid_event("ADDED", appid, name)
            
            # Queue notification for next restart
            add_pending_game(appid, name)
            
            _set_download_state(appid, {"status": "done", "success": True})
            return
        else:
            logger.warn(f"SteamLord: Download failed: {error}")
            _set_download_state(appid, {"status": "failed", "error": error})
            
            # Create request for the game ONLY if it's not a session/license error
            # Common session errors: "Invalid session", "License expired", "Rate limit", "Access denied", "Feature disabled"
            should_create_request = True
            session_errors = [
                "session", "license", "limit", "access denied", "forbidden", 
                "feature disabled", "upgrade", "expired", "revoked", "token"
            ]
            
            error_lower = error.lower()
            for err_keyword in session_errors:
                if err_keyword in error_lower:
                    should_create_request = False
                    break
            
            if should_create_request:
                logger.log(f"SteamLord: Creating request for game {appid}")
                create_game_request(appid)
                create_local_request(appid)
            else:
                logger.log(f"SteamLord: Skipping request creation due to session error: {error}")
            
    except RuntimeError as exc:
        if str(exc) == "cancelled":
            _set_download_state(appid, {"status": "cancelled", "error": "Cancelled by user"})
        else:
            _set_download_state(appid, {"status": "failed", "error": str(exc)})
    except Exception as exc:
        logger.warn(f"SteamLord: Download failed: {exc}")
        _set_download_state(appid, {"status": "failed", "error": str(exc)})



__all__ = [
    "SteamLord_Cancel",
    "SteamLord_Delete",
    "dismiss_loaded_apps",
    "ensure_temp_download_dir",
    "fetch_app_name",
    "get_add_status",
    "get_icon_data_url",
    "SteamLord_Found",
    "read_loaded_apps",
    "_get_loaded_apps_path",
    "SteamLord_Add",
]
from realm_scout import create_local_request
