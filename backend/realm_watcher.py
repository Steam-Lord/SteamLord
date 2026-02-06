"""Checking for per-game updates from the server."""

from __future__ import annotations

import json
import os
import threading
import time
from typing import Dict, List, Optional

from royal_gateway import download_game_zip, download_game_json, check_updates_batch
from kingdom_config import UPDATE_CHECK_INTERVAL_SECONDS
from royal_fetcher import ensure_temp_download_dir
from throne_logger import logger
from kingdom_paths import backend_path
from steam_realm import detect_steam_install_path

import Millennium  # type: ignore


_update_check_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()


def _get_local_game_releases() -> Dict[int, dict]:
    """Read all local {appid}.json files from Update Release directory."""
    releases: Dict[int, dict] = {}
    release_dir = backend_path("Update Release")
    
    if not os.path.isdir(release_dir):
        return releases
    
    for filename in os.listdir(release_dir):
        if filename.endswith(".json"):
            try:
                appid = int(filename[:-5])  # Remove .json
                filepath = os.path.join(release_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                releases[appid] = data
            except Exception:
                pass
    
    return releases


def _check_single_game_update(appid: int, local_data: dict) -> bool:
    """Check if a single game has an update available."""
    try:
        # Get remote JSON
        remote_data = download_game_json(appid)
        if not remote_data:
            return False
        
        local_release = local_data.get("release")
        remote_release = remote_data.get("release")
        
        if not local_release or not remote_release:
            return False
        
        # Compare releases (could be version string or timestamp)
        if str(remote_release) != str(local_release):
            logger.log(f"SteamLord: Update available for {appid}: {local_release} -> {remote_release}")
            return True
        
        return False
        
    except Exception as exc:
        logger.warn(f"SteamLord: Failed to check update for {appid}: {exc}")
        return False


def _apply_game_update(appid: int) -> bool:
    """Download and apply a game update."""
    import zipfile
    import re
    
    try:
        dest_root = ensure_temp_download_dir()
        dest_path = os.path.join(dest_root, f"{appid}_update.zip")
        
        # Download the updated game
        success, error = download_game_zip(appid, dest_path)
        if not success:
            logger.warn(f"SteamLord: Failed to download update for {appid}: {error}")
            return False
        
        # Install like normal
        base_path = detect_steam_install_path() or Millennium.steam_path()
        target_dir = os.path.join(base_path or "", "config", "stplug-in")
        os.makedirs(target_dir, exist_ok=True)
        
        with zipfile.ZipFile(dest_path, "r") as archive:
            names = archive.namelist()
            
            # Extract manifest files
            depotcache_dir = os.path.join(base_path or "", "depotcache")
            os.makedirs(depotcache_dir, exist_ok=True)
            for name in names:
                if name.lower().endswith(".manifest"):
                    pure = os.path.basename(name)
                    data = archive.read(name)
                    with open(os.path.join(depotcache_dir, pure), "wb") as f:
                        f.write(data)
            
            # Find and extract lua file
            for name in names:
                pure = os.path.basename(name)
                if re.fullmatch(r"\d+\.lua", pure):
                    data = archive.read(name)
                    text = data.decode("utf-8", errors="replace")
                    dest_file = os.path.join(target_dir, f"{appid}.lua")
                    with open(dest_file, "w", encoding="utf-8") as f:
                        f.write(text)
                    break
        
        # Update local JSON
        new_json = download_game_json(appid)
        if new_json:
            release_dir = backend_path("Update Release")
            os.makedirs(release_dir, exist_ok=True)
            json_path = os.path.join(release_dir, f"{appid}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(new_json, f, ensure_ascii=False, indent=2)
        
        # Cleanup
        try:
            os.remove(dest_path)
        except Exception:
            pass
        
        logger.log(f"SteamLord: Successfully updated game {appid}")
        return True
        
    except Exception as exc:
        logger.warn(f"SteamLord: Failed to apply update for {appid}: {exc}")
        return False


def check_game_updates_once() -> None:
    """Run a single pass of game update checks using batch request."""
    # Wait briefly before first check to let Steam settle
    time.sleep(10) 
    
    try:
        local_releases = _get_local_game_releases()
        if not local_releases:
            logger.log("SteamLord: No local games found to check for updates")
            return

        # Prepare payload: { "123": "v1.0" }
        games_payload = {}
        for appid, data in local_releases.items():
            # Support both 'release' and 'version' keys
            ver = data.get("release") or data.get("version", "0.0.0")
            games_payload[str(appid)] = str(ver)
            
        logger.log(f"SteamLord: Checking updates for {len(games_payload)} games (Title Batch)")

        # Batch check
        result = check_updates_batch(games_payload)
        
        if result.get("success"):
            updates = result.get("updates", [])
            logger.log(f"SteamLord: Batch check found {len(updates)} updates")
            
            for update in updates:
                appid = update.get("appid")
                if appid:
                    logger.log(f"SteamLord: Applying update for {update.get('name')}...")
                    if _apply_game_update(appid):
                        # Small delay between downloads to be polite
                        time.sleep(2)
        else:
             logger.warn(f"SteamLord: Batch check failed: {result.get('error')}")

        logger.log("SteamLord: Game update check completed")
            
    except Exception as exc:
        logger.warn(f"SteamLord: Game update check failed: {exc}")


def start_single_check_thread():
    """Start a single-run game update check in a background thread."""
    threading.Thread(target=check_game_updates_once, daemon=True).start()
    logger.log("SteamLord: Started single game update check thread")

__all__ = [
    "check_game_updates_now",
    "check_game_updates_once",
    "start_single_check_thread",
]
