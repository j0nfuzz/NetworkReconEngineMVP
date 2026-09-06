from __future__ import annotations

import re
from typing import Any, Dict, List


def extract_neighbors(vendor: str, raw_outputs: Dict[str, str]) -> List[Dict[str, str]]:
    """Parse CDP/LLDP output already collected and return discovered neighbor records."""
    vendor_key = (vendor or "").lower()
    neighbors: List[Dict[str, str]] = []

    for command, output in (raw_outputs or {}).items():
        command_key = command.lower()
        if "cdp" in command_key:
            neighbors.extend(_parse_cdp_neighbors(output, command))
        elif "lldp" in command_key:
            neighbors.extend(_parse_lldp_neighbors(output, command))

    return neighbors


def _parse_cdp_neighbors(output: str, source_command: str) -> List[Dict[str, str]]:
    neighbors: List[Dict[str, str]] = []
    if not output:
        return neighbors

    entries = re.split(r"\n(?=Device ID:)", output, flags=re.IGNORECASE)
    for entry in entries:
        device_match = re.search(r"Device ID:\s*(.+)", entry, re.IGNORECASE)
        ip_match = re.search(r"IP address:\s*(\S+)", entry, re.IGNORECASE)
        platform_match = re.search(r"Platform:\s*(.+?)(?:,\s*Capabilities:|\n|$)", entry, re.IGNORECASE)
        if not device_match:
            continue
        neighbor = {
            "neighbor": device_match.group(1).strip(),
            "source": source_command,
        }
        if ip_match:
            neighbor["ip"] = ip_match.group(1).strip()
        if platform_match:
            neighbor["platform"] = platform_match.group(1).strip()
        neighbors.append(neighbor)

    return neighbors


def _parse_lldp_neighbors(output: str, source_command: str) -> List[Dict[str, str]]:
    neighbors: List[Dict[str, str]] = []
    if not output:
        return neighbors

    def _field_value(entry: str, label: str) -> str:
        for line in entry.splitlines():
            stripped = line.strip()
            if stripped.lower().startswith(label.lower()):
                _, _, value = stripped.partition(":")
                return value.strip()
        return ""

    if "neighbor chassis-id" in output.lower():
        entries = re.split(r"\n(?=\s*Port\s*:\s*)", output, flags=re.IGNORECASE)
        for entry in entries:
            chassis_value = _field_value(entry, "Neighbor Chassis-ID")
            if not chassis_value:
                continue

            system_value = _field_value(entry, "Neighbor System-Name")
            description_value = _field_value(entry, "Neighbor System-Description")
            mgmt_value = _field_value(entry, "Neighbor Management-Address")
            capabilities_value = _field_value(entry, "Chassis Capabilities Available")
            identity = system_value or mgmt_value.split(",")[0].strip()
            if not identity:
                identity = chassis_value

            neighbor: Dict[str, str] = {
                "neighbor": identity,
                "source": source_command,
            }
            if mgmt_value:
                candidate = mgmt_value.split(",")[0].strip()
                if re.match(r"\d{1,3}(\.\d{1,3}){3}", candidate):
                    neighbor["ip"] = candidate
            if not neighbor.get("ip") and re.match(r"\d{1,3}(\.\d{1,3}){3}", chassis_value):
                neighbor["ip"] = chassis_value
            if description_value:
                neighbor["platform"] = description_value
            elif not neighbor.get("ip"):
                neighbor["platform"] = chassis_value
            if capabilities_value:
                neighbor["capabilities"] = capabilities_value
            neighbors.append(neighbor)
        return neighbors

    entries = re.split(r"\n(?=\s*Chassis id:\s*)", output, flags=re.IGNORECASE)
    for entry in entries:
        chassis_match = re.search(r"Chassis id:\s*(.+)", entry, re.IGNORECASE)
        system_match = re.search(r"System Name:\s*(.+)", entry, re.IGNORECASE)
        if not system_match:
            continue
        neighbor = {
            "neighbor": system_match.group(1).strip(),
            "source": source_command,
        }
        if chassis_match:
            candidate = chassis_match.group(1).strip()
            if re.match(r"\d{1,3}(\.\d{1,3}){3}", candidate):
                neighbor["ip"] = candidate
        neighbors.append(neighbor)

    return neighbors
