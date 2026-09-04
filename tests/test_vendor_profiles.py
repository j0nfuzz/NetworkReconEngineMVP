from __future__ import annotations

import pytest

from app.vendor_profiles import (
    GENERIC_PROFILE_KEY,
    VENDOR_PROFILES,
    get_vendor_commands,
    resolve_profile_key,
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
    "show mac-address-table",
    "show spanning-tree",
    "show trunks",
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
    "show mac-address-table",
]

CISCO_NXOS_PROFILE_COMMANDS = [
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

FORTIGATE_PROFILE_COMMANDS = [
    "get system status",
    "get system performance status",
    "get system interface physical",
    "get router info routing-table all",
    "get system arp",
    "show firewall policy",
    "get hardware status",
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


def test_non_aruba_vendors_ignore_aruba_platform_rule() -> None:
    cisco_commands = get_vendor_commands("cisco", platform="arubaos-cx")
    assert "show version" in cisco_commands
    assert "show ip interface brief" in cisco_commands
    assert "show interface brief" not in cisco_commands


@pytest.mark.parametrize("platform", ["nx-os", "cisco nx-os", "NX-OS", "Cisco NX-OS"])
def test_cisco_nx_platform_selects_nxos_profile(platform: str) -> None:
    commands = get_vendor_commands("cisco", platform=platform)
    assert commands == CISCO_NXOS_PROFILE_COMMANDS


@pytest.mark.parametrize("platform", [None, "", "unknown", "cisco ios", "ios-xe", "arubaos-cx"])
def test_cisco_non_nx_platform_uses_base_cisco_profile(platform: str | None) -> None:
    key, fell_back = resolve_profile_key("cisco", platform)
    assert key == "cisco"
    assert fell_back is False


def test_arista_uses_route_summary_instead_of_bgp_summary() -> None:
    commands = get_vendor_commands("arista")
    assert "show ip route summary" in commands
    assert "show ip bgp summary" not in commands
    assert "show mac address-table" in commands


def test_cisco_base_profile_includes_lldp_topology_command() -> None:
    commands = get_vendor_commands("cisco")
    assert "show lldp neighbors" in commands


def test_cisco_profiles_include_loop_error_and_lacp_diagnostics() -> None:
    base = get_vendor_commands("cisco")
    assert "show spanning-tree summary" in base
    assert "show interfaces counters errors" in base
    assert "show etherchannel summary" in base

    switch = get_vendor_commands("cisco", role="switch")
    assert "show spanning-tree summary" in switch
    assert "show interface counters errors" in switch
    assert "show etherchannel summary" in switch

    router = get_vendor_commands("cisco", role="router")
    assert "show etherchannel summary" in router


def test_juniper_profile_includes_statistics_lacp_and_mac_table() -> None:
    commands = get_vendor_commands("juniper")
    assert "show interfaces statistics" in commands
    assert "show lacp interfaces" in commands
    assert "show ethernet-switching table" in commands


def test_arista_profile_includes_error_stp_and_lacp_diagnostics() -> None:
    commands = get_vendor_commands("arista")
    assert "show interfaces counters errors" in commands
    assert "show spanning-tree detail" in commands
    assert "show port-channel" in commands


def test_fortigate_profile_selection() -> None:
    commands = get_vendor_commands("fortigate")
    assert commands == FORTIGATE_PROFILE_COMMANDS


def test_fortigate_profile_is_read_only() -> None:
    commands = get_vendor_commands("fortigate")
    assert validate_device_command_set(commands) == []
    for command in commands:
        assert validate_read_only_command(command) is True


def test_juniper_profile_remains_single_unified_profile() -> None:
    commands = get_vendor_commands("juniper")
    assert "show version" in commands
    assert "show chassis hardware" in commands
    assert "show lldp neighbors detail" in commands


def test_get_vendor_commands_defaults_to_generic_for_unknown_vendor() -> None:
    with pytest.warns(UserWarning):
        commands = get_vendor_commands("unknown-vendor")
    assert "show version" in commands
    assert "show interfaces" in commands


@pytest.mark.parametrize("vendor", ["auto", "unknown"])
def test_unresolved_vendor_falls_back_with_warning(vendor: str) -> None:
    with pytest.warns(UserWarning):
        commands = get_vendor_commands(vendor)
    assert commands == VENDOR_PROFILES[GENERIC_PROFILE_KEY]["commands"]


def test_none_vendor_selects_generic_without_warning() -> None:
    import warnings as warnings_module

    with warnings_module.catch_warnings():
        warnings_module.simplefilter("error")
        commands = get_vendor_commands(None)
    assert commands == VENDOR_PROFILES[GENERIC_PROFILE_KEY]["commands"]


def test_known_vendors_do_not_warn() -> None:
    import warnings as warnings_module

    for vendor in ("cisco", "juniper", "arista", "aruba", "fortigate"):
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("error")
            commands = get_vendor_commands(vendor)
        assert commands


def test_resolve_profile_key_reports_fallback() -> None:
    key, fell_back = resolve_profile_key("no-such-vendor", "mystery-os")
    assert key == GENERIC_PROFILE_KEY
    assert fell_back is True

    key, fell_back = resolve_profile_key("aruba", "arubaos-cx")
    assert key == "aruba-cx"
    assert fell_back is False


@pytest.mark.parametrize("profile_key", sorted(VENDOR_PROFILES))
def test_every_profile_key_is_resolvable_and_read_only(profile_key: str) -> None:
    key, fell_back = resolve_profile_key(profile_key)
    assert key == profile_key
    assert fell_back is False
    for command in get_vendor_commands(profile_key):
        assert validate_read_only_command(command) is True
