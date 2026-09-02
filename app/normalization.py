from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from app.models import DeviceBundle


def _first_int(text: Optional[str]) -> Optional[int]:
    if not text:
        return None
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None


def _first_float(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    match = re.search(r"\d+(?:\.\d+)?", text)
    return float(match.group()) if match else None


def _find_cisco_version(version_output: str) -> Optional[str]:
    for pattern in (
        r"Cisco IOS[- ]?XE Software,?\s*Version\s+([^,\n]+)",
        r"Cisco IOS Software,?\s*Version\s+([^,\n]+)",
        r"NXOS:?\s*version\s+([^,\n]+)",
    ):
        match = re.search(pattern, version_output, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _find_cisco_model(version_output: str) -> Optional[str]:
    match = re.search(r"[Mm]odel\s*[Nn]umber\s*:\s*([^\n]+)", version_output)
    if match:
        return match.group(1).strip()
    match = re.search(r"cisco\s+([^\(]+)\s*\([^)]*\)\s*processor", version_output, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def _find_cisco_uptime_days(version_output: str) -> Optional[int]:
    match = re.search(r"uptime\s+is\s+(.+)", version_output, re.IGNORECASE)
    if not match:
        return None
    uptime = match.group(1).lower()
    days = 0
    m = re.search(r"(\d+)\s+day", uptime)
    if m:
        days += int(m.group(1))
    m = re.search(r"(\d+)\s+week", uptime)
    if m:
        days += int(m.group(1)) * 7
    m = re.search(r"(\d+)\s+year", uptime)
    if m:
        days += int(m.group(1)) * 365
    return days if days else None


def _find_cisco_cpu(cpu_output: Optional[str]) -> Optional[float]:
    if not cpu_output:
        return None
    match = re.search(r"CPU\s+utilization.*?(\d+)\s*%", cpu_output, re.IGNORECASE)
    return _first_float(match.group(1)) if match else None


def _find_cisco_memory(mem_output: Optional[str]) -> Optional[float]:
    if not mem_output:
        return None
    # Look for "Processor Pool Total: ... Used: ..." pattern
    match = re.search(
        r"processor\s+pool\s+total:\s*\d+\s+used:\s*(\d+)",
        mem_output,
        re.IGNORECASE,
    )
    total_match = re.search(r"processor\s+pool\s+total:\s*(\d+)", mem_output, re.IGNORECASE)
    if match and total_match:
        used = int(match.group(1))
        total = int(total_match.group(1))
        return round((used / total) * 100, 2) if total else None
    return None


def _find_cisco_routes(route_output: Optional[str]) -> Optional[int]:
    if not route_output:
        return None
    for pattern in (
        r"(\d+)\s+(?:subnetted|networks)",
        r"contains\s+(\d+)\s+routes?",
    ):
        match = re.search(pattern, route_output, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def _find_cisco_arp(arp_output: Optional[str]) -> Optional[int]:
    if not arp_output:
        return None
    return len(re.findall(r"^\s*Internet\s+\d+\.\d+\.\d+\.\d+", arp_output, re.MULTILINE)) or None


def _find_cisco_interface_errors(interface_output: Optional[str]) -> List[str]:
    if not interface_output:
        return []
    errors: List[str] = []
    current_interface: Optional[str] = None
    for line in interface_output.splitlines():
        iface_match = re.match(r"^\s*([A-Za-z][A-Za-z0-9/.\-]*(?:\d+[A-Za-z0-9/.\-]*)?)\s+is", line)
        if iface_match:
            current_interface = iface_match.group(1).strip()
            continue
        if current_interface and re.search(r"\bCRC\b|\binput errors\b|\boutput errors\b", line, re.IGNORECASE):
            if any(
                int(match.group(1)) > 0
                for match in re.finditer(r"(\d+)\s+(?:input errors|CRC|output errors)", line, re.IGNORECASE)
            ):
                errors.append(current_interface)
    return errors


def build_device_summary(bundle: DeviceBundle) -> Dict[str, Any]:
    """Return a deterministic, vendor-independent summary from a DeviceBundle."""
    summary = bundle.summary or {}
    raw = bundle.raw_outputs or {}

    vendor = summary.get("vendor") or bundle.device_vendor or "unknown"
    version_output = raw.get("show version", "")
    version: Optional[str] = None
    model: Optional[str] = None
    uptime_days: Optional[int] = None

    if vendor == "cisco":
        version = _find_cisco_version(version_output)
        model = _find_cisco_model(version_output) or summary.get("model")
        uptime_days = _find_cisco_uptime_days(version_output)
        cpu = _find_cisco_cpu(raw.get("show processes cpu sorted"))
        memory = _find_cisco_memory(raw.get("show memory statistics"))
        routes = _find_cisco_routes(raw.get("show ip route summary"))
        arp_entries = _find_cisco_arp(raw.get("show arp"))
        interface_errors = _find_cisco_interface_errors(raw.get("show interfaces"))
    else:
        cpu = None
        memory = None
        routes = None
        arp_entries = None
        interface_errors = []

    return {
        "hostname": summary.get("hostname") or bundle.device_name,
        "vendor": vendor,
        "model": model or summary.get("model") or "unknown",
        "version": version or "unknown",
        "uptime_days": uptime_days,
        "cpu": cpu,
        "memory": memory,
        "routes": routes,
        "arp_entries": arp_entries,
        "interface_errors": interface_errors,
        "failed_commands": summary.get("failed_commands", []),
        "failed_command_details": summary.get("failed_command_details", []),
    }
