from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

_CREDENTIAL_FIELDS = ("username", "password", "enable_password")


def _load_config_payload(config_path: str | Path) -> Dict[str, Any]:
    """Return the raw parsed YAML payload."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_default_credentials(config_path: str | Path) -> Dict[str, Any]:
    """Return credential fields from the raw config default block."""
    payload = _load_config_payload(config_path)
    default = payload.get("default", {}) or {}
    if not isinstance(default, dict):
        raise ValueError("Config file 'default' block must be a mapping.")
    return {field: default[field] for field in _CREDENTIAL_FIELDS if field in default}


def load_devices(config_path: str | Path) -> List[Dict[str, Any]]:
    payload = _load_config_payload(config_path)

    devices = payload.get("devices", [])
    if not isinstance(devices, list):
        raise ValueError("Config file must contain a 'devices' list.")

    default = payload.get("default", {}) or {}
    if not isinstance(default, dict):
        raise ValueError("Config file 'default' block must be a mapping.")

    merged_devices = []
    for device in devices:
        merged = dict(device)
        for field in _CREDENTIAL_FIELDS:
            if field not in merged and field in default:
                merged[field] = default[field]
        merged_devices.append(merged)

    return merged_devices
