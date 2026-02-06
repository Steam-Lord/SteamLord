"""Checking for availability of requested games."""

from __future__ import annotations

import json
import os
import threading
from typing import List, Dict

from royal_gateway import check_game_exists, get_api_client, check_availability_batch
from throne_logger import logger
from kingdom_paths import backend_path, REQUEST_GAME_DIR


def _get_requested_games_dir() -> str:
    return REQUEST_GAME_DIR


def _get_local_requested_games() -> List[int]:
    """Get list of locally requested game appids."""
    requested_dir = _get_requested_games_dir()
    requested: List[int] = []
    
    if not os.path.isdir(requested_dir):
        return requested
    
    for filename in os.listdir(requested_dir):
        try:
            # Files are named like "12345" or "12345.json"
            name = filename.replace(".json", "").replace(".txt", "")
            appid = int(name)
            requested.append(appid)
        except Exception:
            pass
    
    return requested


def _remove_local_request(appid: int) -> None:
    """Remove a local request file."""
    requested_dir = _get_requested_games_dir()
    
    possible_files = [
        os.path.join(requested_dir, str(appid)),
        os.path.join(requested_dir, f"{appid}.json"),
        os.path.join(requested_dir, f"{appid}.txt"),
    ]
    
    for path in possible_files:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass


def _fetch_game_name(appid: int) -> str:
    """Fetch game name from Steam API."""
    try:
        client = get_api_client()
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
        resp = client.get(url, follow_redirects=True, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        entry = data.get(str(appid), {})
        if isinstance(entry, dict):
            inner = entry.get("data", {})
            name = inner.get("name")
            if isinstance(name, str) and name.strip():
                return name.strip()
    except Exception:
        pass
    return f"Game {appid}"


_PENDING_AVAILABLE_GAMES: List[Dict] = []
_CHECK_LOCK = threading.Lock()

def check_available_requested_games() -> str:
    """
    Check if any locally requested games are now available (Batch Mode).
    Returns list of games that are now available.
    """
    global _PENDING_AVAILABLE_GAMES
    try:
        requested_appids = _get_local_requested_games()
        if not requested_appids:
            return json.dumps({"success": True, "games": _PENDING_AVAILABLE_GAMES})
        
        logger.log(f"SteamLord: Checking availability for {len(requested_appids)} requested games (Batch)...")
        
        new_available: List[Dict] = []
        
        # Batch check
        result = check_availability_batch(requested_appids)
        
        if result.get("success"):
            available_appids = result.get("available", [])
            logger.log(f"SteamLord: Batch availability check found {len(available_appids)} games")
            
            for appid in available_appids:
                try:
                    name = _fetch_game_name(appid)
                    game_info = {"appid": appid, "name": name}
                    new_available.append(game_info)
                    
                    # Store safely
                    with _CHECK_LOCK:
                        _PENDING_AVAILABLE_GAMES.append(game_info)
                        
                    # Remove local request file
                    _remove_local_request(appid)
                    logger.log(f"SteamLord: Requested game {appid} ({name}) is now available!")
                except Exception as exc:
                     logger.warn(f"SteamLord: Failed to process available game {appid}: {exc}")
        else:
             logger.warn(f"SteamLord: Batch availability check failed: {result.get('error')}")
        
        # Return currently pending (including new ones)
        with _CHECK_LOCK:
             # Return a copy
             return json.dumps({"success": True, "games": list(_PENDING_AVAILABLE_GAMES)})
        
    except Exception as exc:
        logger.warn(f"SteamLord: check_available_requested_games failed: {exc}")
        return json.dumps({"success": False, "error": str(exc)})


def get_and_clear_availability_notifications() -> str:
    """Retrieve pending notifications and clear them."""
    global _PENDING_AVAILABLE_GAMES
    with _CHECK_LOCK:
        games = list(_PENDING_AVAILABLE_GAMES)
        # We don't clear them immediately? 
        # Actually frontend calls this. If we return them, we should probably clear them 
        # so they don't show up again on reload? 
        # User wants them to show "when Steam opens". 
        # Let's clear after returning.
        _PENDING_AVAILABLE_GAMES.clear()
        
    return json.dumps({"success": True, "games": games})


def create_local_request(appid: int) -> bool:
    """Create a local request file for a game."""
    try:
        requested_dir = _get_requested_games_dir()
        os.makedirs(requested_dir, exist_ok=True)
        
        filepath = os.path.join(requested_dir, f"{appid}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({"appid": appid}, f)
        
        return True
    except Exception as exc:
        logger.warn(f"SteamLord: Failed to create local request for {appid}: {exc}")
        return False


def start_single_check_thread():
    """Start a single-run availability check in a background thread."""
    threading.Thread(target=check_available_requested_games, daemon=True).start()
    logger.log("AvailabilityChecker: Started single check thread")

__all__ = [
    "check_available_requested_games",
    "create_local_request",
    "start_single_check_thread",
    "get_and_clear_availability_notifications",
]
