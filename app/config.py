from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List

import yaml

_CREDENTIAL_FIELDS = ("username", "password", "enable_password")

# Match exactly ${ENV_VAR_NAME} for credential substitution.
_ENV_PLACEHOLDER_RE = re.compile(r"^\$\{([A-Za-z_][A-Za-z0-9_]*)\}$")

# Detect strings that look like environment-variable references but are not valid.
_ENV_MALFORMED_RE = re.compile(r"\$\{.*\}")


def _resolve_credential_value(value: Any, field_name: str = "credential") -> Any:
    """Resolve a credential field value.

    If the value is a string matching ${ENV_VAR}, look up the environment
    variable and return it.  Missing variables raise ValueError.  Non-string
    values and literal strings are returned unchanged.  Malformed ${...}
    references raise ValueError without exposing secret values.
    """
    if not isinstance(value, str):
        return value
    if not value.startswith("${"):
        return value
    if _ENV_MALFORMED_RE.match(value) and not _ENV_PLACEHOLDER_RE.match(value):
        raise ValueError(f"Malformed environment variable reference for {field_name}")
    match = _ENV_PLACEHOLDER_RE.match(value)
    if not match:
        return value
    env_name = match.group(1)
    if env_name not in os.environ:
        raise ValueError(f"Missing environment variable for credential: ${{{env_name}}}")
    return os.environ[env_name]


def _load_config_payload(config_path: str | Path) -> Dict[str, Any]:
    """Return the raw parsed YAML payload."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _resolve_credentials(mapping: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of *mapping* with credential placeholders resolved."""
    resolved = dict(mapping)
    for field in _CREDENTIAL_FIELDS:
        if field in resolved:
            resolved[field] = _resolve_credential_value(resolved[field], field_name=field)
    return resolved


def load_default_credentials(config_path: str | Path) -> Dict[str, Any]:
    """Return credential fields from the raw config default block."""
    payload = _load_config_payload(config_path)
    default = payload.get("default", {}) or {}
    if not isinstance(default, dict):
        raise ValueError("Config file 'default' block must be a mapping.")
    return _resolve_credentials(
        {field: default[field] for field in _CREDENTIAL_FIELDS if field in default}
    )


def load_devices(config_path: str | Path) -> List[Dict[str, Any]]:
    payload = _load_config_payload(config_path)

    devices = payload.get("devices", [])
    if not isinstance(devices, list):
        raise ValueError("Config file must contain a 'devices' list.")

    default = payload.get("default", {}) or {}
    if not isinstance(default, dict):
        raise ValueError("Config file 'default' block must be a mapping.")

    default = _resolve_credentials(default)

    merged_devices = []
    for device in devices:
        merged = _resolve_credentials(dict(device))
        for field in _CREDENTIAL_FIELDS:
            if field not in merged and field in default:
                merged[field] = default[field]
        merged_devices.append(merged)

    return merged_devices
