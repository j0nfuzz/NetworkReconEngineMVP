from __future__ import annotations

import re
from typing import Optional

from app.models import DeviceIdentity


def detect_vendor_from_show_version(output: str) -> Optional[str]:
    """Legacy vendor-only detection kept for backward compatibility."""
    identity = identify_device(output)
    return identity.vendor if identity.confidence > 0 else None


def identify_device(output: str) -> DeviceIdentity:
    """Return vendor, platform, and model extracted from device banner/version text.

    Falls back to generic/unknown values when no match is found.
    """
    if not output:
        return DeviceIdentity()

    text = output.lower()

    if "arubaos" in text or "aruba" in text:
        platform = _extract_first(text, ["arubaos-cx", "arubaos", "aruba"])
        model = _extract_model(text, [r"model:\s*([^\s,\n)]+)", r"(\d{4}[a-z0-9-]*)"])
        return DeviceIdentity(vendor="aruba", platform=platform, model=model, confidence=0.6)

    if "cisco ios" in text or "cisco" in text or "cisco ios-xe" in text:
        platform = _extract_first(text, ["cisco ios-xe", "cisco ios", "ios-xe", "ios"])
        model = _extract_model(text, [r"model number\s*[:\s]+\s*([^\s,\n]+)", r"cisco\s+([^\s,(]+)", r"(\w+-\d+[^\s,\n]*)"])
        return DeviceIdentity(vendor="cisco", platform=platform, model=model, confidence=0.7)

    if "junos" in text or "juniper" in text:
        platform = _extract_first(text, ["junos", "juniper"])
        model = _extract_model(text, [r"model:\s*([^\s,\n]+)", r"juniper\s+networks\s+([^\s,\n]+)", r"(\w+-\d+[^\s,\n]*)"])
        return DeviceIdentity(vendor="juniper", platform=platform, model=model, confidence=0.6)

    if "eos" in text or "arista" in text:
        platform = _extract_first(text, ["arista eos", "eos", "arista"])
        model = _extract_model(text, [r"arista\s+networks\s+([^\s,\n]+)", r"(dcs-\d+[^\s,\n]*)", r"(\w+-\d+[^\s,\n]*)"])
        return DeviceIdentity(vendor="arista", platform=platform, model=model, confidence=0.5)

    return DeviceIdentity()


def _extract_first(text: str, candidates: list[str]) -> str:
    for candidate in candidates:
        if candidate in text:
            return candidate.strip()
    return "unknown"


def _extract_model(text: str, patterns: list[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            if candidate:
                return candidate
    return "unknown"
