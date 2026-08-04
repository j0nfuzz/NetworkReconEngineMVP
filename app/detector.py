from __future__ import annotations

from typing import Optional


def detect_vendor_from_show_version(output: str) -> Optional[str]:
    if not output:
        return None

    text = output.lower()

    if "arubaos" in text or "aruba" in text:
        return "aruba"
    if "cisco ios" in text or "cisco" in text:
        return "cisco"
    if "junos" in text or "juniper" in text:
        return "juniper"
    if "eos" in text or "arista" in text:
        return "arista"

    return "generic"
