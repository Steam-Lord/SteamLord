"""Central configuration constants for the SteamLord backend."""

# ═══════════════════════════════════════════════════════════════════════════
# Cloudflare API Configuration
# All GitHub operations go through this secure proxy
# API Token is obtained dynamically from server on login (no static key!)
# ═══════════════════════════════════════════════════════════════════════════

CLOUDFLARE_API_URL = "https://api.steamlord.online"

# ═══════════════════════════════════════════════════════════════════════════
# File and Directory Names
# ═══════════════════════════════════════════════════════════════════════════

WEBKIT_DIR_NAME = "SteamLord"
WEB_UI_JS_FILE = "steamlord.js"
WEB_UI_ICON_FILE = "steamlord-icon.png"

# ═══════════════════════════════════════════════════════════════════════════
# HTTP Configuration
# ═══════════════════════════════════════════════════════════════════════════

DEFAULT_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "SteamLord/1.0",
}

HTTP_TIMEOUT_SECONDS = 30
HTTP_DOWNLOAD_TIMEOUT_SECONDS = 120

# ═══════════════════════════════════════════════════════════════════════════
# Update Configuration
# ═══════════════════════════════════════════════════════════════════════════

UPDATE_CONFIG_FILE = "update.json"
UPDATE_PENDING_ZIP = "update_pending.zip"
UPDATE_PENDING_INFO = "update_pending.json"
UPDATE_CHECK_INTERVAL_SECONDS = 2 * 60 * 60  # 2 hours

# ═══════════════════════════════════════════════════════════════════════════
# Local File Names
# ═══════════════════════════════════════════════════════════════════════════

LOADED_APPS_FILE = "steamlord_loadedappids.txt"
APPID_LOG_FILE = "steamlord_appidlogs.txt"

# ═══════════════════════════════════════════════════════════════════════════
# User Agent (for API identification)
# ═══════════════════════════════════════════════════════════════════════════

USER_AGENT = "SteamLord/1.0"
