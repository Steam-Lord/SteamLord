import json
import os

THEME_FILE = "user_theme.json"

def _get_theme_path():
    """Get path to the theme JSON file in current directory."""
    return os.path.join(os.path.dirname(__file__), THEME_FILE)

def load_theme():
    """Load theme data from JSON."""
    path = _get_theme_path()
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            pass
    # Default theme (Blue)
    return {"id": "blue", "primary": "#3b82f6", "gradient_start": "#3b82f6", "gradient_end": "#2563eb", "shadow": "rgba(59, 130, 246, 0.5)"}

def save_theme(theme_data):
    """Save theme data to JSON."""
    path = _get_theme_path()
    try:
        with open(path, 'w') as f:
            json.dump(theme_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Failed to save theme: {e}")
        return False
