import json
import os
import time

PROFILE_FILE = "user_profile.json"

def _get_profile_path():
    """Get path to the profile JSON file in current directory."""
    return os.path.join(os.path.dirname(__file__), PROFILE_FILE)

def load_profile():
    """Load profile data from JSON."""
    path = _get_profile_path()
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            pass
    return None

def save_profile(data):
    """Save profile data to JSON."""
    path = _get_profile_path()
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Failed to save profile: {e}")

def init_profile(license_key, session_data):
    """Initialize profile if it doesn't exist or key changed."""
    current = load_profile()
    
    # If key matches, don't overwrite stats
    if current and current.get("license_key") == license_key:
        # Update expiry/lifetime status just in case it changed on server
        if session_data:
            current["expiry_date"] = session_data.get("expiresAt", current.get("expiry_date"))
            current["is_lifetime"] = session_data.get("isLifetime", current.get("is_lifetime"))
            save_profile(current)
        return

    # Create new profile for new key
    profile = {
        "license_key": license_key,
        "downloads_count": 0,
        "online_fix_count": 0,
        "bypass_count": 0,
        "expiry_date": session_data.get("expiresAt", "Unknown") if session_data else "Unknown",
        "is_lifetime": session_data.get("isLifetime", False) if session_data else False,
        "registration_date": int(time.time())
    }
    save_profile(profile)

def increment_stat(stat_name):
    """Increment a specific statistic."""
    profile = load_profile()
    if profile:
        current = profile.get(stat_name, 0)
        profile[stat_name] = current + 1
        save_profile(profile)
        return True
    return False
