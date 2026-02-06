"""Module to manage pending notifications for the user."""
import json
import os
from kingdom_paths import backend_path

PENDING_GAMES_FILE = "pending_added_games.json"

_STARTUP_GAMES = []
_INITIALIZED = False

def _get_pending_path() -> str:
    return backend_path(PENDING_GAMES_FILE)

def _initialize():
    """Read pending games into memory at startup and clear the file."""
    global _STARTUP_GAMES, _INITIALIZED
    if _INITIALIZED:
        return
    
    try:
        path = _get_pending_path()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = json.load(f)
                if isinstance(content, list):
                    _STARTUP_GAMES = content
            
            # Clear the file so these games aren't loaded again next time
            # But we keep them in _STARTUP_GAMES to show them in this session
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f)
    except Exception:
        pass
    finally:
        _INITIALIZED = True

# Initialize on module import (Simulation of Plugin Startup)
_initialize()

def add_pending_game(appid: int, name: str) -> None:
    """Add a game to the split of pending post-restart notifications (next session)."""
    try:
        path = _get_pending_path()
        current_list = []
        
        # Read current content (which might have been cleared by init, or has new games)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    current_list = json.load(f) or []
            except Exception:
                pass
        
        # Check if already exists to avoid duplicates
        for entry in current_list:
            if entry.get("appid") == appid:
                return

        current_list.append({"appid": appid, "name": name})
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(current_list, f, indent=2)
            
    except Exception:
        pass

def get_and_clear_pending_games() -> str:
    """Get list of games that were pending AT STARTUP, and clear the memory cache."""
    global _STARTUP_GAMES
    
    try:
        # Return the games loaded at startup
        games = list(_STARTUP_GAMES)
        
        # Clear the memory cache so we don't show the modal again on page refresh
        _STARTUP_GAMES = []
        
        return json.dumps({"success": True, "games": games})
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})
