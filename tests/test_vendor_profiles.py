from __future__ import annotations

import pytest

from app.vendor_profiles import (
    get_vendor_commands,
    validate_device_command_set,
    validate_read_only_command,
)


ARUBA_PROFILE_COMMANDS = [
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

ARUBA_CX_PROFILE_COMMANDS = [
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
]


@pytest.mark.parametrize("platform", ["arubaos-cx", "ArubaOS-CX", "ARUBAOS-CX", "cx"])
def test_aruba_cx_platform_selects_corrected_profile(platform: str) -> None:
    commands = get_vendor_commands("aruba", platform=platform)
    assert commands == ARUBA_CX_PROFILE_COMMANDS


def test_aruba_non_cx_platform_uses_generic_aruba_profile() -> None:
    commands = get_vendor_commands("aruba", platform="arubaos-switch")
    assert commands == ARUBA_PROFILE_COMMANDS


@pytest.mark.parametrize("platform", [None, "", "unknown"])
def test_aruba_unknown_platform_defaults_to_generic_aruba_profile(platform: str | None) -> None:
    commands = get_vendor_commands("aruba", platform=platform)
    assert commands == ARUBA_PROFILE_COMMANDS


def test_aruba_cx_profile_replaces_rejected_commands() -> None:
    commands = get_vendor_commands("aruba", platform="arubaos-cx")
    assert "show inventory" not in commands
    assert "show interfaces brief" not in commands
    assert "show lldp neighbors detail" not in commands
    assert "show switch info" not in commands
    assert "show log buffer" not in commands

    assert "show module" in commands
    assert "show interface brief" in commands
    assert "show lldp neighbor-info detail" in commands
    assert "show running-config" in commands
    assert "show logging" in commands


def test_aruba_cx_profile_retains_accepted_commands() -> None:
    commands = get_vendor_commands("aruba", platform="arubaos-cx")
    for retained in (
        "show version",
        "show ip interface brief",
        "show ip route",
        "show arp",
        "show system",
    ):
        assert retained in commands


def test_aruba_cx_commands_are_read_only() -> None:
    commands = get_vendor_commands("aruba", platform="arubaos-cx")
    invalid = validate_device_command_set(commands)
    assert invalid == []
    for command in commands:
        assert validate_read_only_command(command) is True


def test_aruba_cx_profile_replaces_ambiguous_log_command() -> None:
    commands = get_vendor_commands("aruba", platform="arubaos-cx")
    assert "show log" not in commands
    assert "show logging" in commands


def test_aruba_cx_profile_order_is_deterministic() -> None:
    first = get_vendor_commands("aruba", platform="arubaos-cx")
    second = get_vendor_commands("aruba", platform="arubaos-cx")
    assert first is not second
    assert first == second


def test_aruba_cx_ignores_role() -> None:
    commands = get_vendor_commands("aruba", platform="arubaos-cx", role="switch")
    assert commands == ARUBA_CX_PROFILE_COMMANDS


def test_non_aruba_vendors_ignore_platform() -> None:
    cisco_commands = get_vendor_commands("cisco", platform="arubaos-cx")
    assert "show version" in cisco_commands
    assert "show ip interface brief" in cisco_commands


def test_get_vendor_commands_defaults_to_generic_for_unknown_vendor() -> None:
    commands = get_vendor_commands("unknown-vendor")
    assert "show version" in commands
    assert "show interfaces" in commands
