"""Generic helpers for file and data handling in the SteamLord backend."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict

from kingdom_paths import backend_path, get_plugin_dir


def read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except Exception:
        return ""


def write_text(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def read_json(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return {}


def write_json(path: str, data: Dict[str, Any]) -> None:
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
    except Exception:
        pass


def parse_version(version: str) -> tuple:
    try:
        parts = [int(part) for part in re.findall(r"\d+", str(version))]
        return tuple(parts or [0])
    except Exception:
        return (0,)


def get_plugin_version() -> str:
    try:
        plugin_json_path = os.path.join(get_plugin_dir(), "plugin.json")
        data = read_json(plugin_json_path)
        return str(data.get("version", "0"))
    except Exception:
        return "0"


def ensure_temp_download_dir() -> str:
    root = backend_path("temp_dl")
    try:
        os.makedirs(root, exist_ok=True)
    except Exception:
        pass
    return root


__all__ = [
    "backend_path",
    "ensure_temp_download_dir",
    "get_plugin_dir",
    "get_plugin_version",
    "parse_version",
    "read_json",
    "read_text",
    "write_json",
    "write_text",
]
