from __future__ import annotations

from typing import Any, Dict, List


SUPPORTED_VENDOR_MARKERS = {
    "cisco": ["cisco"],
    "aruba": ["aruba"],
    "fortigate": ["fortigate", "fortinet"],
    "juniper": ["juniper", "juniper networks"],
}

UNSUPPORTED_MARKERS = [
    "printer",
    "ups",
    "phone",
    "iot",
    "camera",
    "appliance",
    "workstation",
    "server",
    "unknown",
]


def classify_neighbor_support(neighbor_record: Dict[str, str]) -> str:
    """Classify a neighbor as a supported vendor, unsupported, or unknown."""
    platform = (neighbor_record.get("platform") or "").lower()
    capabilities = (neighbor_record.get("capabilities") or "").lower()
    combined = f"{platform} {capabilities}".strip()

    if not combined:
        return "unknown"

    for vendor, markers in SUPPORTED_VENDOR_MARKERS.items():
        if any(marker in combined for marker in markers):
            return vendor

    if any(marker in combined for marker in UNSUPPORTED_MARKERS):
        return "unsupported"

    return "unknown"


def classify_neighbors(neighbors: List[Dict[str, str]]) -> Dict[str, str]:
    """Return a deterministic classification per neighbor name.

    Duplicate neighbor names keep the first encountered classification.
    """
    classifications: Dict[str, str] = {}
    for record in neighbors or []:
        name = record.get("neighbor")
        if not name:
            continue
        if name not in classifications:
            classifications[name] = classify_neighbor_support(record)
    return classifications
