from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

_default_settings: Dict[str, Any] = {
    "telemetry_enabled": True,
    "logging_enabled": True,
    "log_level": "INFO",
}

_settings_file: Optional[str] = None


def _get_settings_path() -> str:
    global _settings_file
    if _settings_file:
        return _settings_file

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(base_dir, "config")
    os.makedirs(config_dir, exist_ok=True)
    _settings_file = os.path.join(config_dir, "telemetry_settings.json")
    return _settings_file


def load_user_settings() -> Dict[str, Any]:
    settings_path = _get_settings_path()

    if not os.path.exists(settings_path):
        return _default_settings.copy()

    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        merged = _default_settings.copy()
        merged.update(loaded)
        return merged
    except (json.JSONDecodeError, IOError) as e:
        logging.warning(f"Failed to load telemetry settings: {e}")
        return _default_settings.copy()


def save_user_settings(settings: Dict[str, Any]) -> None:
    settings_path = _get_settings_path()

    current = load_user_settings()
    current.update(settings)

    try:
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, ensure_ascii=False)
    except IOError as e:
        logging.error(f"Failed to save telemetry settings: {e}")


def get_telemetry_enabled() -> bool:
    settings = load_user_settings()
    return settings.get("telemetry_enabled", True)


def set_telemetry_enabled(enabled: bool) -> None:
    save_user_settings({"telemetry_enabled": enabled})


def get_log_level() -> str:
    settings = load_user_settings()
    return settings.get("log_level", "INFO")


def set_log_level(level: str) -> None:
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if level.upper() in valid_levels:
        save_user_settings({"log_level": level.upper()})


def is_logging_enabled() -> bool:
    settings = load_user_settings()
    return settings.get("logging_enabled", True)


def set_logging_enabled(enabled: bool) -> None:
    save_user_settings({"logging_enabled": enabled})


def reset_settings() -> None:
    save_user_settings(_default_settings)