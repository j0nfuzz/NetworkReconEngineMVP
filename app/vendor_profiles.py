from __future__ import annotations

import re
from typing import Dict, List

READ_ONLY_PREFIXES = (
    "show",
    "get",
    "display",
    "ping",
    "traceroute",
    "ls",
    "dir",
    "cat",
    "more",
)

WRITE_BLOCKLIST = (
    "configure",
    "copy",
    "write",
    "install",
    "reload",
    "clear",
    "delete",
    "remove",
    "set",
    "commit",
    "save",
    "boot",
)


def validate_read_only_command(command: str) -> bool:
    if not isinstance(command, str) or not command.strip():
        return False

    normalized = command.strip().lower()
    if any(normalized.startswith(prefix) for prefix in WRITE_BLOCKLIST):
        return False

    if any(normalized.startswith(prefix) for prefix in READ_ONLY_PREFIXES):
        return True

    return False


VENDOR_PROFILES: Dict[str, Dict[str, Dict[str, List[str]]]] = {
    "cisco": {
        "commands": [
            "show version",
            "show inventory",
            "show interfaces status",
            "show ip interface brief",
            "show ip route summary",
            "show cdp neighbors detail",
            "show arp",
            "show process cpu sorted",
            "show memory statistics",
            "show logging",
        ],
        "roles": {
            "switch": [
                "show version",
                "show inventory",
                "show interfaces status",
                "show interface counters errors",
                "show spanning-tree summary",
                "show mac address-table count",
                "show cdp neighbors detail",
                "show logging",
                "show processes cpu sorted",
                "show memory statistics",
            ],
            "router": [
                "show version",
                "show inventory",
                "show interfaces",
                "show ip route summary",
                "show arp",
                "show logging",
                "show processes cpu sorted",
            ],
        },
    },
    "juniper": {
        "commands": [
            "show version",
            "show chassis hardware",
            "show interfaces terse",
            "show route summary",
            "show arp",
            "show lldp neighbors detail",
            "show system uptime",
            "show system processes extensive",
            "show log messages",
        ]
    },
    "arista": {
        "commands": [
            "show version",
            "show inventory",
            "show interfaces status",
            "show ip interface brief",
            "show ip bgp summary",
            "show lldp neighbors detail",
            "show logging",
        ]
    },
    "aruba": {
        "commands": [
            "show version",
            "show inventory",
            "show interfaces brief",
            "show ip interface brief",
            "show ip route",
            "show lldp neighbors detail",
            "show arp",
            "show system",
            "show switch info",
            "show log buffer",
        ]
    },
    "aruba-cx": {
        "commands": [
            "show version",
            "show module",
            "show interface brief",
            "show ip interface brief",
            "show ip route",
            "show lldp neighbor-info detail",
            "show arp",
            "show system",
            "show running-config",
            "show log",
        ]
    },
    "generic": {
        "commands": [
            "show version",
            "show interfaces",
            "show ip route",
            "show arp",
            "show system uptime",
        ]
    },
}


def get_vendor_commands(
    vendor: str, role: str | None = None, platform: str | None = None
) -> List[str]:
    key = (vendor or "generic").lower()
    if key == "aruba" and platform and "cx" in platform.lower():
        key = "aruba-cx"
    profile = VENDOR_PROFILES.get(key, VENDOR_PROFILES["generic"])
    commands = _resolve_commands(profile, role)
    invalid = [cmd for cmd in commands if not validate_read_only_command(cmd)]
    if invalid:
        raise ValueError(f"Invalid non-read-only vendor commands detected: {invalid}")
    return commands


def _resolve_commands(profile: Dict[str, Dict[str, List[str]]], role: str | None) -> List[str]:
    if role:
        role_key = role.lower()
        role_commands = profile.get("roles", {}).get(role_key)
        if role_commands:
            return list(role_commands)
    return list(profile.get("commands", []))


def validate_device_command_set(commands: List[str]) -> List[str]:
    invalid = [cmd for cmd in commands if not validate_read_only_command(cmd)]
    return invalid
