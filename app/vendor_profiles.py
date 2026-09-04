from __future__ import annotations

import warnings
from typing import Dict, List, Optional, Tuple

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

GENERIC_PROFILE_KEY = "generic"


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
            "show lldp neighbors",
            "show arp",
            "show processes cpu sorted",
            "show memory statistics",
            "show logging",
            "show spanning-tree summary",
            "show interfaces counters errors",
            "show etherchannel summary",
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
                "show lldp neighbors",
                "show logging",
                "show processes cpu sorted",
                "show memory statistics",
                "show etherchannel summary",
            ],
            "router": [
                "show version",
                "show inventory",
                "show interfaces",
                "show ip route summary",
                "show arp",
                "show lldp neighbors",
                "show logging",
                "show processes cpu sorted",
                "show etherchannel summary",
            ],
        },
    },
    "cisco-nxos": {
        "commands": [
            "show version",
            "show inventory",
            "show interface status",
            "show ip interface brief",
            "show ip route summary",
            "show cdp neighbors detail",
            "show lldp neighbors",
            "show mac address-table",
            "show spanning-tree summary",
            "show system resources",
            "show logging log",
            "show interface counters errors",
            "show port-channel summary",
        ]
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
            "show interfaces statistics",
            "show lacp interfaces",
            "show ethernet-switching table",
        ]
    },
    "arista": {
        "commands": [
            "show version",
            "show inventory",
            "show interfaces status",
            "show ip interface brief",
            "show ip route summary",
            "show lldp neighbors detail",
            "show mac address-table",
            "show logging",
            "show interfaces counters errors",
            "show spanning-tree detail",
            "show port-channel",
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
            "show mac-address-table",
            "show spanning-tree",
            "show trunks",
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
            "show logging",
            "show mac-address-table",
        ]
    },
    "fortigate": {
        "commands": [
            "get system status",
            "get system performance status",
            "get system interface physical",
            "get router info routing-table all",
            "get system arp",
            "show firewall policy",
            "get hardware status",
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

PLATFORM_PROFILE_RULES: Tuple[Tuple[str, str, str], ...] = (
    ("aruba", "cx", "aruba-cx"),
    ("cisco", "nx", "cisco-nxos"),
)


def resolve_profile_key(vendor: Optional[str], platform: Optional[str] = None) -> Tuple[str, bool]:
    """Resolve the command profile key for a vendor/platform pair.

    Returns the profile key and whether the generic fallback was used.
    Unknown vendor keys (including unresolved "auto"/"unknown") fall back to
    the generic profile and emit a warning so the degradation is observable
    rather than silent.
    """
    key = (vendor or GENERIC_PROFILE_KEY).lower()

    if platform:
        platform_normalized = platform.lower()
        for rule_vendor, marker, profile_key in PLATFORM_PROFILE_RULES:
            if key == rule_vendor and marker in platform_normalized:
                key = profile_key
                break

    fell_back = key not in VENDOR_PROFILES
    if fell_back:
        detail = f"vendor '{vendor}'"
        if platform:
            detail += f", platform '{platform}'"
        warnings.warn(
            f"No command profile for {detail}; falling back to the "
            f"'{GENERIC_PROFILE_KEY}' profile.",
            stacklevel=2,
        )
        key = GENERIC_PROFILE_KEY

    return key, fell_back


def get_vendor_commands(
    vendor: str, role: str | None = None, platform: str | None = None
) -> List[str]:
    key, _fell_back = resolve_profile_key(vendor, platform)
    profile = VENDOR_PROFILES[key]
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
