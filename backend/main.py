"""Main entry point for the SteamLord Millennium plugin."""

import json
import os
import shutil
import sys
import webbrowser

from typing import Any

import Millennium  # type: ignore
import PluginUtils  # type: ignore

from crown_updater import (
    apply_pending_update_if_any,
    check_for_update_now,
    restart_steam as auto_restart_steam,
    is_restart_required as auto_is_restart_required,
    set_restart_required,
    start_auto_update_background_check,
    stop_auto_update_background_check,
)
from kingdom_config import WEBKIT_DIR_NAME, WEB_UI_ICON_FILE, WEB_UI_JS_FILE
from royal_fetcher import (
    SteamLord_Cancel,
    SteamLord_Delete,
    dismiss_loaded_apps,
    ensure_temp_download_dir,
    get_add_status,
    get_icon_data_url,
    SteamLord_Found,
    read_loaded_apps,
    SteamLord_Add,
)
from lord_fixer import (
    apply_game_fix,
    cancel_apply_fix,
    check_for_fixes,
    get_apply_fix_status,
    get_unfix_status,
    unfix_game,
)
from lord_bypass import (
    apply_bypass,
    get_apply_bypass_status,
    remove_bypass,
    get_remove_bypass_status,
)
from throne_logger import logger as shared_logger
from realm_scout import check_available_requested_games, start_single_check_thread
from realm_watcher import check_game_updates_once, start_single_check_thread as start_game_update_single_thread
from crown_shield import (
    get_file_guard,
    on_session_start,
    on_session_end,
    get_guard_status,
)
from royal_gateway import close_api_client, download_guard_file
from realm_net import close_http_client
from royal_auth import (
    register_license,
    verify_session,
    logout as license_logout,
    get_license_status,
    is_logged_in,
    get_session,
    verify_on_startup,
)

from royal_fetcher import (
    SteamLord_Cancel,
    SteamLord_Delete,
    dismiss_loaded_apps,
    ensure_temp_download_dir,
    get_add_status,
    get_icon_data_url,
    SteamLord_Found,
    read_loaded_apps,
    SteamLord_Add,
)
from steam_realm import detect_steam_install_path, get_game_install_path_response, open_game_folder, clear_steam_browser_cache
from herald import get_and_clear_pending_games
from kingdom_paths import get_plugin_dir, public_path
from kingdom_records import init_profile, load_profile, increment_stat
from theme_manager import load_theme, save_theme

logger = shared_logger
HAS_CHECKED_AVAILABILITY = False





class Logger:
    @staticmethod
    def log(message: str) -> str:
        shared_logger.log(f"[Frontend] {message}")
        return json.dumps({"success": True})

    @staticmethod
    def warn(message: str) -> str:
        shared_logger.warn(f"[Frontend] {message}")
        return json.dumps({"success": True})

    @staticmethod
    def error(message: str) -> str:
        shared_logger.error(f"[Frontend] {message}")
        return json.dumps({"success": True})


def _steam_ui_path() -> str:
    return os.path.join(Millennium.steam_path(), "steamui", WEBKIT_DIR_NAME)


def _copy_webkit_files() -> None:
    plugin_dir = get_plugin_dir()
    steam_ui_path = _steam_ui_path()
    os.makedirs(steam_ui_path, exist_ok=True)

    js_src = public_path(WEB_UI_JS_FILE)
    js_dst = os.path.join(steam_ui_path, WEB_UI_JS_FILE)
    logger.log(f"Copying SteamLord web UI from {js_src} to {js_dst}")
    try:
        shutil.copy(js_src, js_dst)
    except Exception as exc:
        logger.error(f"Failed to copy SteamLord web UI: {exc}")





    # Copy logo for activation popup and sidebar
    logo_src = public_path("steamlord-logo.png")
    logo_dst = os.path.join(steam_ui_path, "steamlord-logo.png")
    if os.path.exists(logo_src):
        try:
            shutil.copy(logo_src                                                , logo_dst)
            logger.log(f"Copied SteamLord logo to {logo_dst}")
        except Exception as exc:
            logger.error(f"Failed to copy SteamLord logo: {exc}")
    else:
        logger.warn(f"SteamLord logo not found at {logo_src}")


def _inject_webkit_files() -> None:
    js_path = os.path.join(WEBKIT_DIR_NAME, WEB_UI_JS_FILE)
    Millennium.add_browser_js(js_path)
    logger.log(f"SteamLord injected web UI: {js_path}")


# ═══════════════════════════════════════════════════════════════════════════
# Frontend API Functions
# ═══════════════════════════════════════════════════════════════════════════


def CheckForUpdatesNow(contentScriptQuery: str = "") -> str:
    return check_for_update_now()


def RestartSteam(contentScriptQuery: str = "") -> str:
    return auto_restart_steam()


def ClearSteamCache(contentScriptQuery: str = "") -> str:
    """Clear Steam browser/overlay cache."""
    try:
        success, msg = clear_steam_browser_cache()
        if success:
            return json.dumps({"success": True, "message": msg})
        else:
            return json.dumps({"success": False, "error": msg})
    except Exception as exc:
        logger.warn(f"SteamLord: ClearSteamCache failed: {exc}")
        return json.dumps({"success": False, "error": str(exc)})


def SetRestartRequired(contentScriptQuery: str = "") -> str:
    set_restart_required(True)
    return json.dumps({"success": True})


def IsRestartRequired(contentScriptQuery: str = "") -> str:
    return auto_is_restart_required()


def GetPendingAddedGames(contentScriptQuery: str = "") -> str:
    return get_and_clear_pending_games()


def SteamLordFound(appid: int, contentScriptQuery: str = "") -> str:
    return SteamLord_Found(appid)


def SteamLordAdd(appid: int, contentScriptQuery: str = "") -> str:
    return SteamLord_Add(appid)


def SteamLordAddStatus(appid: int, contentScriptQuery: str = "") -> str:
    return get_add_status(appid)


def SteamLordCancel(appid: int, contentScriptQuery: str = "") -> str:
    return SteamLord_Cancel(appid)


def GetIconDataUrl(contentScriptQuery: str = "") -> str:
    return get_icon_data_url()


def GetLogoDataUrl(contentScriptQuery: str = "") -> str:
    """Return the activation logo as a base64 data URL."""
    try:
        import base64
        logo_path = public_path("steamlord-logo.png")
        if not os.path.exists(logo_path):
            return json.dumps({"success": False, "error": "Logo not found"})
        with open(logo_path, "rb") as handle:
            data = handle.read()
        b64 = base64.b64encode(data).decode("ascii")
        return json.dumps({"success": True, "dataUrl": f"data:image/png;base64,{b64}"})
    except Exception as exc:
        logger.warn(f"SteamLord: GetLogoDataUrl failed: {exc}")
        return json.dumps({"success": False, "error": str(exc)})


def ReadLoadedApps(contentScriptQuery: str = "") -> str:
    return read_loaded_apps()


def DismissLoadedApps(contentScriptQuery: str = "") -> str:
    return dismiss_loaded_apps()


def SteamLordDelete(appid: int, contentScriptQuery: str = "") -> str:
    return SteamLord_Delete(appid)


def CheckForFixes(appid: int, contentScriptQuery: str = "") -> str:
    return check_for_fixes(appid)


def ApplyGameFix(appid: int, downloadUrl: str, installPath: str, fixType: str = "", gameName: str = "", contentScriptQuery: str = "") -> str:
    return apply_game_fix(appid, downloadUrl, installPath, fixType, gameName)


def GetApplyFixStatus(appid: int, contentScriptQuery: str = "") -> str:
    return get_apply_fix_status(appid)


def CancelApplyFix(appid: int, contentScriptQuery: str = "") -> str:
    return cancel_apply_fix(appid)


def UnFixGame(appid: int, installPath: str = "", contentScriptQuery: str = "") -> str:
    return unfix_game(appid, installPath)


def GetUnfixStatus(appid: int, contentScriptQuery: str = "") -> str:
    return get_unfix_status(appid)


def ApplyBypass(appid: int, installPath: str, contentScriptQuery: str = "") -> str:
    return apply_bypass(appid, installPath)


def GetApplyBypassStatus(appid: int, contentScriptQuery: str = "") -> str:
    return get_apply_bypass_status(appid)


def RemoveBypass(appid: int, installPath: str = "", contentScriptQuery: str = "") -> str:
    return remove_bypass(appid, installPath)


def GetRemoveBypassStatus(appid: int, contentScriptQuery: str = "") -> str:
    return get_remove_bypass_status(appid)


def GetGameInstallPath(appid: int, contentScriptQuery: str = "") -> str:
    result = get_game_install_path_response(appid)
    return json.dumps(result)





def GetActiveDownloads(contentScriptQuery: str = "") -> str:
    """Get all active downloads, fixes, and bypasses."""
    try:
        from royal_fetcher import get_all_active_downloads
        from lord_fixer import get_all_active_fixes
        from lord_bypass import get_all_active_bypasses
        
        games = get_all_active_downloads()
        fixes = get_all_active_fixes()
        bypasses = get_all_active_bypasses()
        
        # Format for frontend
        active_games = [{"appid": aid, "state": s} for aid, s in games.items()]
        active_fixes = [{"appid": aid, "state": s} for aid, s in fixes.items()]
        active_bypasses = [{"appid": aid, "state": s} for aid, s in bypasses.items()]
        
        return json.dumps({
            "success": True, 
            "active": {
                "game": active_games, 
                "fix": active_fixes, 
                "bypass": active_bypasses
            }
        })
    except Exception as exc:
        logger.warn(f"SteamLord: GetActiveDownloads failed: {exc}")
        return json.dumps({"success": False, "error": str(exc)})


def CheckAvailableRequestedGames(contentScriptQuery: str = "") -> str:
    global HAS_CHECKED_AVAILABILITY
    if HAS_CHECKED_AVAILABILITY:
        return json.dumps({"success": True, "games": []})
    
    HAS_CHECKED_AVAILABILITY = True
    return check_available_requested_games()


def OpenExternalUrl(url: str, contentScriptQuery: str = "") -> str:
    try:
        value = str(url or "").strip()
        if not (value.startswith("http://") or value.startswith("https://")):
            return json.dumps({"success": False, "error": "Invalid URL"})
        if sys.platform.startswith("win"):
            try:
                os.startfile(value)  # type: ignore[attr-defined]
            except Exception:
                webbrowser.open(value)
        else:
            webbrowser.open(value)
        return json.dumps({"success": True})
    except Exception as exc:
        logger.warn(f"SteamLord: OpenExternalUrl failed: {exc}")
        return json.dumps({"success": False, "error": str(exc)})











# ═══════════════════════════════════════════════════════════════════════════
# License Management API
# ═══════════════════════════════════════════════════════════════════════════


def RegisterLicense(licenseKey: str = "", contentScriptQuery: str = "", **kwargs: Any) -> str:
    """Register with license key only (no email)."""
    try:
        if not licenseKey and "licenseKey" in kwargs:
            licenseKey = kwargs["licenseKey"]
        
        if not licenseKey:
            return json.dumps({"success": False, "error": "License key is required"})
        
        success, error, session_data = register_license(licenseKey)
        
        if success:
            # Initialize local profile
            init_profile(licenseKey, session_data)
            
            return json.dumps({
                "success": True,
                "expiresAt": session_data.get("expiresAt"),
                "isLifetime": session_data.get("isLifetime", False),
                "isFreeKey": session_data.get("isFreeKey", False),
                "limits": session_data.get("limits"),
            })
        else:
            return json.dumps({"success": False, "error": error})
    except Exception as exc:
        logger.warn(f"SteamLord: RegisterLicense failed: {exc}")
        return json.dumps({"success": False, "error": str(exc)})


def VerifyLicense(contentScriptQuery: str = "") -> str:
    """Verify the current session."""
    try:
        valid, error, info = verify_session()
        if valid:
            return json.dumps({
                "success": True,
                "valid": True,
                "email": info.get("email") if info else None,
                "expiresAt": info.get("expiresAt") if info else None,
                "isLifetime": info.get("isLifetime", False) if info else False,
            })
        else:
            return json.dumps({"success": True, "valid": False, "error": error})
    except Exception as exc:
        logger.warn(f"SteamLord: VerifyLicense failed: {exc}")
        return json.dumps({"success": False, "error": str(exc)})


def GetLicenseStatus(contentScriptQuery: str = "") -> str:
    """Get detailed license status."""
    try:
        status = get_license_status()
        if status:
            return json.dumps({"success": True, **status})
        else:
            return json.dumps({"success": False, "error": "Failed to get status"})
    except Exception as exc:
        logger.warn(f"SteamLord: GetLicenseStatus failed: {exc}")
        return json.dumps({"success": False, "error": str(exc)})


def Logout(contentScriptQuery: str = "") -> str:
    """Logout from the current session."""
    try:
        license_logout()
        return json.dumps({"success": True})
    except Exception as exc:
        logger.warn(f"SteamLord: Logout failed: {exc}")
        return json.dumps({"success": False, "error": str(exc)})


def IsLoggedIn(contentScriptQuery: str = "") -> str:
    """Check if user is logged in."""
    try:
        logged_in = is_logged_in()
        return json.dumps({"success": True, "isLoggedIn": logged_in})
    except Exception as exc:
        logger.warn(f"SteamLord: IsLoggedIn failed: {exc}")
        return json.dumps({"success": False, "error": str(exc)})


def GetSessionInfo(contentScriptQuery: str = "") -> str:
    """Get current session info."""
    try:
        session = get_session()
        if session:
            return json.dumps({
                "success": True,
                "isLoggedIn": True,
                "email": session.get("email"),
                "expiresAt": session.get("expiresAt"),
                "isLifetime": session.get("isLifetime", False),
            })
        else:
            return json.dumps({"success": True, "isLoggedIn": False})
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})


def GetProfileData(contentScriptQuery: str = "") -> str:
    """Get local profile stats."""
    try:
        profile = load_profile()
        if profile:
            return json.dumps({"success": True, "profile": profile})
        else:
            return json.dumps({"success": False, "error": "Profile not found"})
    except Exception as exc:
        logger.warn(f"SteamLord: GetProfileData failed: {exc}")
        return json.dumps({"success": False, "error": str(exc)})


def GetTheme(contentScriptQuery: str = "") -> str:
    """Get current theme settings."""
    try:
        theme = load_theme()
        return json.dumps({"success": True, "theme": theme})
    except Exception as exc:
        logger.warn(f"SteamLord: GetTheme failed: {exc}")
        return json.dumps({"success": False, "error": str(exc)})


def SetTheme(theme_data: str, contentScriptQuery: str = "") -> str:
    """Save new theme settings."""
    try:
        data = json.loads(theme_data)
        if save_theme(data):
            return json.dumps({"success": True})
        else:
            return json.dumps({"success": False, "error": "Failed to save theme"})
    except Exception as exc:
        logger.warn(f"SteamLord: SetTheme failed: {exc}")
        return json.dumps({"success": False, "error": str(exc)})


# ═══════════════════════════════════════════════════════════════════════════
# Plugin Class
# ═══════════════════════════════════════════════════════════════════════════


class Plugin:
    def _front_end_loaded(self):
        _copy_webkit_files()

    def _load(self):
        logger.log(f"bootstrapping SteamLord plugin, millennium {Millennium.version()}")

        try:
            detect_steam_install_path()
        except Exception as exc:
            logger.warn(f"SteamLord: steam path detection failed: {exc}")

        ensure_temp_download_dir()

        try:
            apply_pending_update_if_any()
        except Exception as exc:
            logger.warn(f"AutoUpdate: apply pending failed: {exc}")

        # Verify license on startup
        try:
            is_valid, error = verify_on_startup()
            if is_valid:
                logger.log("SteamLord: License verified successfully")
            else:
                logger.log(f"SteamLord: License verification: {error}")
        except Exception as exc:
            logger.warn(f"SteamLord: License verification failed: {exc}")
        
        # Download guard file once (first install only) - check if file already exists
        try:
            guard = get_file_guard()
            guard_path = guard._get_enabled_path()  # xinput1_4.dll in Steam folder
            
            # Only download if file doesn't exist
            if not os.path.exists(guard_path):
                logger.log(f"SteamLord: Guard file not found at {guard_path}, downloading...")
                success, err = download_guard_file(guard_path)
                if success:
                    logger.log("SteamLord: Guard file downloaded successfully")
                else:
                    logger.warn(f"SteamLord: Guard file download failed: {err}")
            else:
                logger.log("SteamLord: Guard file already exists, skipping download")
            # No rename logic - file stays as xinput1_4.dll always
        except Exception as guard_exc:
            logger.warn(f"SteamLord: Guard file check failed: {guard_exc}")

        _copy_webkit_files()
        _inject_webkit_files()

        try:
            start_auto_update_background_check()
        except Exception as exc:
            logger.warn(f"AutoUpdate: start background check failed: {exc}")

        try:
            # Spawn a single-shot thread for game updates
            start_game_update_single_thread()
            logger.log("GameUpdateChecker: started single check")
        except Exception as exc:
            logger.warn(f"GameUpdateChecker: start failed: {exc}")
            
        try:
            # Spawn a single-shot thread for availability check
            start_single_check_thread()
            logger.log("AvailabilityChecker: started single check")
        except Exception as exc:
            logger.warn(f"AvailabilityChecker: start failed: {exc}")

        Millennium.ready()

    def _unload(self):
        logger.log("unloading SteamLord plugin")
        
        # File Guard: No action on unload (file stays as xinput1_4.dll always)

        try:
            stop_auto_update_background_check()
        except Exception:
            pass
        
        try:
            close_api_client()
        except Exception:
            pass
        
        try:
            close_http_client()
        except Exception:
            pass


plugin = Plugin()