from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml


def load_devices(config_path: str | Path) -> List[Dict[str, Any]]:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}

    devices = payload.get("devices", [])
    if not isinstance(devices, list):
        raise ValueError("Config file must contain a 'devices' list.")

    return devices
