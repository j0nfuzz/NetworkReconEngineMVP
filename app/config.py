from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

_CREDENTIAL_FIELDS = ("username", "password", "enable_password")


def load_devices(config_path: str | Path) -> List[Dict[str, Any]]:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}

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
