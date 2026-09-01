from __future__ import annotations

import json
import socket
import struct
import tempfile
import zipfile
from pathlib import Path

import paramiko
import pytest
import yaml

import app.collector as collector_module
from app.cli import parse_args, probe_devices, _is_legacy_error, _run_recursive_cli, _prompt_interactive_inventory
from app.collector import execute_device_collection, write_bundle
from app.classification import classify_neighbor_support, classify_neighbors
from app.detector import detect_vendor_from_show_version
from app.discovery import extract_neighbors
from app.models import Device, DeviceBundle
from app.ssh_client import DeviceSSHClient
from app.topology import build_topology_graph
from app.traversal import traverse_topology
from app.vendor_profiles import get_vendor_commands, validate_device_command_set


def test_parse_args_supports_verbose_flag(monkeypatch):
    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        "output",
        "--verbose",
    ])
    args = parse_args()
    assert args.verbose is True


def test_parse_args_supports_recursive_and_checkpoint_file(monkeypatch):
    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        "output",
        "--recursive",
        "--checkpoint-file",
        "checkpoint.json",
    ])
    args = parse_args()
    assert args.recursive is True
    assert args.checkpoint_file == "checkpoint.json"


def test_parse_args_config_is_optional(monkeypatch):
    monkeypatch.setattr("sys.argv", ["prog", "--output-dir", "output"])
    args = parse_args()
    assert args.config is None
    assert args.output_dir == "output"


def test_vendor_profile_cisco():
    commands = get_vendor_commands("cisco")
    assert "show version" in commands
    assert "show interfaces status" in commands


def test_execute_device_collection_dry_run():
    device = Device(
        name="test-device",
        hostname="10.0.0.1",
        vendor="cisco",
        username="admin",
        password="<PASSWORD-01>",
    )

    bundle = execute_device_collection(device, dry_run=True)
    assert bundle.summary["status"] == "dry-run-success"
    assert len(bundle.raw_outputs) > 0


def test_bundle_manifest_is_writable(tmp_path):
    manifest = tmp_path / "bundle_manifest.json"
    payload = {"devices": [{"name": "a", "vendor": "cisco"}]}
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    assert json.loads(manifest.read_text(encoding="utf-8"))["devices"][0]["name"] == "a"


def test_ssh_probe_reports_unreachable_host():
    client = DeviceSSHClient("192.0.2.1", "admin", "<PASSWORD-01>", port=22, timeout=1)
    result = client.probe()
    assert result["reachable"] is False
    assert "error" in result or "status" in result


def test_vendor_commands_are_read_only():
    commands = get_vendor_commands("cisco")
    invalid = validate_device_command_set(commands)
    assert invalid == []

    blocked = validate_device_command_set(["configure terminal", "show version"])
    assert "configure terminal" in blocked


def test_live_collection_executes_read_only_commands(monkeypatch):
    class FakeSSHClient:
        def __init__(
            self,
            hostname,
            username,
            password,
            port=22,
            timeout=15,
            host_key_policy="auto",
            known_hosts=None,
        ):
            self.hostname = hostname
            self.username = username
            self.password = password
            self.port = port
            self.timeout = timeout
            self.host_key_policy = host_key_policy
            self.known_hosts = known_hosts

        def probe(self):
            return {"reachable": True, "status": "connected"}

        def connect(self):
            return {"connected": True}

        def close(self, client):
            return None

        def run_command(self, command, *, client=None):
            return {
                "command": command,
                "stdout": "output for " + command,
                "stderr": "",
                "exit_code": 0,
                "success": True,
                "error": None,
            }

    monkeypatch.setattr(collector_module, "DeviceSSHClient", FakeSSHClient)

    device = Device(
        name="lab-switch",
        hostname="10.0.0.12",
        vendor="cisco",
        username="admin",
        password="<PASSWORD-01>",
    )

    bundle = execute_device_collection(device, dry_run=False)
    assert bundle.summary["status"] == "collected"
    assert "show version" in bundle.raw_outputs
    assert bundle.raw_outputs["show version"].startswith("output for show version")


def test_write_bundle_creates_ai_ready_artifacts(tmp_path):
    bundle = DeviceBundle(
        device_name="lab-switch",
        device_vendor="aruba",
        timestamp="2026-08-04T00:00:00Z",
        summary={"status": "collected", "commands_run": 2, "failed_commands": []},
        raw_outputs={
            "show version": "ArubaOS-CX version 10.13",
            "show interfaces brief": "1/1/1 up",
        },
        failed_commands=[],
    )

    output_dir = tmp_path / "bundle"
    device_dir = write_bundle(bundle, output_dir)

    assert (device_dir / "summary.json").exists()
    assert (device_dir / "show_version.txt").exists()
    assert (device_dir / "ai_prompt.txt").exists()
    assert "ArubaOS" in (device_dir / "ai_prompt.txt").read_text(encoding="utf-8")


def test_detect_vendor_from_show_version_output():
    assert detect_vendor_from_show_version("Cisco IOS XE Software, Version 17.09.04") == "cisco"
    assert detect_vendor_from_show_version("ArubaOS-CX (MODEL: 6300M) Version 10.13.1000") == "aruba"
    assert detect_vendor_from_show_version("JUNOS Software Release [18.4R3-S2]") == "juniper"


def test_is_legacy_error_markers():
    assert _is_legacy_error("Incompatible ssh peer (no acceptable kex algorithm)")
    assert _is_legacy_error("could not agree on diffie-hellman-group14-sha1")
    assert _is_legacy_error("no compatible ciphers / sha1 required")
    assert not _is_legacy_error("Connection timed out")
    assert not _is_legacy_error("Authentication failed")


def test_probe_devices_classification(monkeypatch):
    outcomes = {
        "modern": {"reachable": True, "status": "connected", "error": ""},
        "legacy": {
            "reachable": False,
            "status": "unreachable",
            "error": "SSH key exchange negotiation failed (no acceptable kex algorithm, SHA1)",
        },
        "unreachable": {"reachable": False, "status": "unreachable", "error": "Connection timed out"},
    }

    class FakeClient:
        def __init__(self, **kwargs):
            self._outcome = outcomes.get(kwargs.get("hostname"), outcomes["unreachable"])

        def probe(self):
            return self._outcome

    monkeypatch.setattr("app.ssh_client.DeviceSSHClient", FakeClient)

    devices = [
        Device(name=n, hostname=n, vendor="auto") for n in ("modern", "legacy", "unreachable")
    ]
    results = probe_devices(devices)
    by_name = {r["name"]: r["classification"] for r in results}
    assert by_name["modern"] == "modern"
    assert by_name["legacy"] == "legacy"
    assert by_name["unreachable"] == "unreachable"


def test_configured_vendor_device_gets_role_classified(monkeypatch, tmp_path):
    """Configured-vendor devices must receive role classification without SSH probing."""
    device_dict = {
        "name": "dist-sw01",
        "hostname": "10.0.0.10",
        "vendor": "cisco",
        "username": "admin",
        "password": "<PASSWORD-01>",
    }

    monkeypatch.setattr("app.cli.load_devices", lambda path: [device_dict])

    captured_device = None

    def fake_execute(device, dry_run=False):
        nonlocal captured_device
        captured_device = device
        return DeviceBundle(
            device_name=device.name,
            device_vendor=device.vendor,
            timestamp="2026-08-04T00:00:00Z",
            summary={"status": "dry-run-success", "commands_run": 0, "failed_commands": []},
            raw_outputs={},
            failed_commands=[],
        )

    monkeypatch.setattr("app.cli.execute_device_collection", fake_execute)
    monkeypatch.setattr("app.cli.write_bundle", lambda bundle, output_dir: tmp_path / "bundle")

    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        str(tmp_path),
        "--dry-run",
    ])

    from app.cli import main

    result = main()
    assert result == 0
    assert captured_device is not None
    assert captured_device.metadata["role"]["role"] == "switch"
    assert captured_device.metadata["role"]["confidence"] > 0


def test_vendor_commands_role_specific_cisco_switch():
    commands = get_vendor_commands("cisco", role="switch")
    assert "show version" in commands
    assert "show mac address-table count" in commands
    assert "show spanning-tree summary" in commands
    assert "show ip route summary" not in commands


def test_vendor_commands_role_specific_cisco_router():
    commands = get_vendor_commands("cisco", role="router")
    assert "show version" in commands
    assert "show ip route summary" in commands
    assert "show mac address-table count" not in commands


def test_vendor_commands_unmatched_role_falls_back():
    commands = get_vendor_commands("cisco", role="firewall")
    assert "show version" in commands
    assert "show interfaces status" in commands


def test_extract_neighbors_cisco_cdp():
    output = """\nDevice ID: SW02\nEntry address(es):\n  IP address: 10.0.0.2\nPlatform: cisco WS-C2960-24TC-L,  Capabilities: Switch IGMP\nInterface: GigabitEthernet1/0/1,  Port ID (outgoing port): GigabitEthernet0/1\nHoldtime : 148 sec\n\nDevice ID: FW01\nEntry address(es):\n  IP address: 10.0.0.254\nPlatform: cisco ASA-5510,  Capabilities: Host Firewall\nInterface: GigabitEthernet1/0/2,  Port ID (outgoing port): Ethernet0/0\nHoldtime : 120 sec\n"""
    neighbors = extract_neighbors("cisco", {"show cdp neighbors detail": output})
    by_name = {n["neighbor"]: n for n in neighbors}
    assert by_name["SW02"]["ip"] == "10.0.0.2"
    assert by_name["FW01"]["ip"] == "10.0.0.254"
    assert all(n["source"] == "show cdp neighbors detail" for n in neighbors)


def test_extract_neighbors_returns_empty_when_no_discovery_output():
    neighbors = extract_neighbors("cisco", {"show version": "Cisco IOS XE Software"})
    assert neighbors == []


def test_extract_neighbors_cisco_cdp_captures_platform():
    output = """\nDevice ID: SW02\nEntry address(es):\n  IP address: 10.0.0.2\nPlatform: cisco WS-C2960-24TC-L,  Capabilities: Switch IGMP\nInterface: GigabitEthernet1/0/1,  Port ID (outgoing port): GigabitEthernet0/1\nHoldtime : 148 sec\n"""
    neighbors = extract_neighbors("cisco", {"show cdp neighbors detail": output})
    by_name = {n["neighbor"]: n for n in neighbors}
    assert by_name["SW02"]["platform"] == "cisco WS-C2960-24TC-L"


def test_extract_neighbors_cisco_cdp_captures_platform_at_end_of_string():
    output = "Device ID: SW03\nEntry address(es):\n  IP address: 10.0.0.3\nPlatform: cisco WS-C2960-24TC-L"
    neighbors = extract_neighbors("cisco", {"show cdp neighbors detail": output})
    assert len(neighbors) == 1
    assert neighbors[0]["neighbor"] == "SW03"
    assert neighbors[0]["platform"] == "cisco WS-C2960-24TC-L"
    assert classify_neighbor_support(neighbors[0]) == "cisco"


def test_classify_neighbor_support_recognizes_supported_vendors():
    assert classify_neighbor_support({"platform": "cisco WS-C2960-24TC-L"}) == "cisco"
    assert classify_neighbor_support({"platform": "Aruba 6300M"}) == "aruba"
    assert classify_neighbor_support({"platform": "FortiGate-100F"}) == "fortigate"
    assert classify_neighbor_support({"platform": "Juniper Networks ex4300"}) == "juniper"


def test_classify_neighbor_support_marks_unsupported_devices():
    assert classify_neighbor_support({"platform": "HP LaserJet Printer"}) == "unsupported"
    assert classify_neighbor_support({"platform": "APC Smart-UPS 3000"}) == "unsupported"
    assert classify_neighbor_support({"platform": "Polycom SoundPoint IP Phone"}) == "unsupported"


def test_classify_neighbor_support_unknown_when_no_platform():
    assert classify_neighbor_support({"neighbor": "SW02"}) == "unknown"
    assert classify_neighbor_support({"platform": ""}) == "unknown"


def test_classify_neighbors_returns_classification_per_name():
    neighbors = [
        {"neighbor": "SW02", "platform": "cisco WS-C2960-24TC-L"},
        {"neighbor": "PR01", "platform": "HP LaserJet Printer"},
        {"neighbor": "UNKNOWN"},
    ]
    result = classify_neighbors(neighbors)
    assert result == {
        "SW02": "cisco",
        "PR01": "unsupported",
        "UNKNOWN": "unknown",
    }


def test_classify_neighbors_does_not_mutate_input():
    neighbors = [{"neighbor": "SW02", "platform": "cisco WS-C2960-24TC-L"}]
    _ = classify_neighbors(neighbors)
    assert "classification" not in neighbors[0]



def test_execute_device_collection_dry_run_has_empty_neighbors():
    device = Device(
        name="test-device",
        hostname="10.0.0.1",
        vendor="cisco",
        username="admin",
        password="<PASSWORD-01>",
    )
    bundle = execute_device_collection(device, dry_run=True)
    assert bundle.summary["discovered_neighbors"] == []


def test_build_topology_graph_links_connected_devices():
    summaries = [
        {
            "device": "SW01",
            "vendor": "cisco",
            "role": "switch",
            "discovered_neighbors": [{"neighbor": "SW02", "source": "show cdp neighbors detail"}],
        },
        {
            "device": "SW02",
            "vendor": "cisco",
            "role": "switch",
            "discovered_neighbors": [{"neighbor": "SW01", "source": "show cdp neighbors detail"}],
        },
    ]
    graph = build_topology_graph(summaries)
    assert "SW01" in graph["nodes"]
    assert "SW02" in graph["nodes"]
    assert "SW02" in graph["nodes"]["SW01"]["neighbors"]
    assert "SW01" in graph["nodes"]["SW02"]["neighbors"]
    assert len(graph["edges"]) == 2


def test_build_topology_graph_isolated_node():
    summaries = [
        {
            "device": "SW01",
            "vendor": "cisco",
            "role": "switch",
            "discovered_neighbors": [],
        }
    ]
    graph = build_topology_graph(summaries)
    assert graph["nodes"]["SW01"]["neighbors"] == []
    assert graph["edges"] == []


def test_build_topology_graph_empty_input():
    graph = build_topology_graph([])
    assert graph["nodes"] == {}
    assert graph["edges"] == []


def test_ssh_client_retries_on_legacy_kex_failure(monkeypatch):
    calls = {"count": 0}

    class FakeSSHClient:
        def __init__(self):
            self.connected = False

        def set_missing_host_key_policy(self, policy):
            return None

        def connect(self, **kwargs):
            calls["count"] += 1
            if calls["count"] == 1:
                raise paramiko.SSHException("Incompatible ssh peer (no acceptable kex algorithm)")
            return "connected"

    monkeypatch.setattr(paramiko, "SSHClient", FakeSSHClient)
    client = DeviceSSHClient("device.example", "user", "pass")
    result = client.connect()
    assert isinstance(result, FakeSSHClient)
    assert calls["count"] == 2


def test_ssh_client_explain_error_includes_kex_diagnostics():
    peer_kex = ["diffie-hellman-group1-sha1"]
    explanation = DeviceSSHClient.explain_compatibility_error(
        paramiko.SSHException("Incompatible ssh peer (no acceptable kex algorithm)"),
        peer_kex_algorithms=peer_kex,
    )
    assert "Supported KEX algorithms" in explanation
    assert "Peer offered KEX algorithms" in explanation
    assert "diffie-hellman-group1-sha1" in explanation


def test_ssh_client_explain_error_without_peer_kex_is_actionable():
    explanation = DeviceSSHClient.explain_compatibility_error(
        paramiko.SSHException("Incompatible ssh peer (no acceptable kex algorithm)")
    )
    assert "Supported KEX algorithms" in explanation
    assert "Peer offered KEX algorithms" in explanation
    assert "requirements-legacy.txt" in explanation


def test_ssh_client_extract_peer_kex_from_kexinit_packet():
    # SSH_MSG_KEXINIT (20), 16-byte cookie, then name-list length + "person@example.com,diffie-hellman-group14-sha256"
    cookie = b"\x00" * 16
    kex_names = "person@example.com,diffie-hellman-group14-sha256"
    name_list = struct.pack(">I", len(kex_names)) + kex_names.encode("utf-8")
    packet = bytes([20]) + cookie + name_list
    peer_kex = DeviceSSHClient._extract_peer_kex_from_init(packet)
    assert peer_kex == ["person@example.com", "diffie-hellman-group14-sha256"]


def test_ssh_client_probe_reports_kex_diagnostics(monkeypatch):
    class FakeSSHClient:
        def set_missing_host_key_policy(self, policy):
            return None

        def connect(self, **kwargs):
            raise paramiko.SSHException("Incompatible ssh peer (no acceptable kex algorithm)")

    monkeypatch.setattr(paramiko, "SSHClient", FakeSSHClient)
    monkeypatch.setattr(
        DeviceSSHClient,
        "get_peer_kex_algorithms",
        classmethod(lambda cls, hostname, port, timeout: ["diffie-hellman-group1-sha1"]),
    )
    client = DeviceSSHClient("192.0.2.1", "admin", "<PASSWORD-01>", timeout=1)
    result = client.probe()
    assert result["reachable"] is False
    assert "Supported KEX algorithms" in result["error"]
    assert "diffie-hellman-group1-sha1" in result["error"]


def test_run_command_returns_failure_for_eof_error():
    class FakeSSHClient:
        def exec_command(self, command, timeout=None):
            raise EOFError("remote closed connection")

    client = DeviceSSHClient("device.example", "user", "pass")
    result = client.run_command("show version", client=FakeSSHClient())

    assert result["success"] is False
    assert result["exit_code"] == -1
    assert "remote closed connection" in result["error"]


def test_run_command_records_elapsed_seconds_on_success():
    class FakeChannel:
        def recv_exit_status(self):
            return 0

    class FakeStdout:
        channel = FakeChannel()

        def read(self):
            return b"success output"

    class FakeStderr:
        channel = FakeChannel()

        def read(self):
            return b""

    class FakeSSHClient:
        def exec_command(self, command, timeout=None):
            return None, FakeStdout(), FakeStderr()

    client = DeviceSSHClient("device.example", "user", "pass")
    result = client.run_command("show version", client=FakeSSHClient())

    assert result["success"] is True
    assert result["stdout"] == "success output"
    assert "elapsed_seconds" in result
    assert isinstance(result["elapsed_seconds"], float)
    assert result["elapsed_seconds"] >= 0


def test_run_command_classifies_timeout_and_preserves_partial_output():
    class FakeChannel:
        def __init__(self):
            self._stdout_buffer = b"partial line\n"
            self._stderr_buffer = b""

        def recv_ready(self):
            return len(self._stdout_buffer) > 0

        def recv(self, nbytes):
            data = self._stdout_buffer
            self._stdout_buffer = b""
            return data

        def recv_stderr_ready(self):
            return len(self._stderr_buffer) > 0

        def recv_stderr(self, nbytes):
            data = self._stderr_buffer
            self._stderr_buffer = b""
            return data

    class FakeStdout:
        def __init__(self):
            self.channel = FakeChannel()

        def read(self):
            raise socket.timeout("Command timed out")

    class FakeStderr:
        def __init__(self):
            self.channel = FakeChannel()

        def read(self):
            return b""

    class FakeSSHClient:
        def exec_command(self, command, timeout=None):
            return None, FakeStdout(), FakeStderr()

    client = DeviceSSHClient("device.example", "user", "pass")
    result = client.run_command("show version", client=FakeSSHClient())

    assert result["success"] is False
    assert result["exit_code"] == -1
    assert result["error_type"] == "timeout"
    assert "partial line" in result["stdout"]
    assert "elapsed_seconds" in result
    assert isinstance(result["elapsed_seconds"], float)


def test_run_command_classifies_ssh_exception():
    class FakeSSHClient:
        def exec_command(self, command, timeout=None):
            raise paramiko.SSHException("channel closed")

    client = DeviceSSHClient("device.example", "user", "pass")
    result = client.run_command("show version", client=FakeSSHClient())

    assert result["success"] is False
    assert result["exit_code"] == -1
    assert result["error_type"] == "ssh_exception"
    assert "channel closed" in result["error"]
    assert "elapsed_seconds" in result


def test_run_command_preserves_partial_stderr_on_ssh_exception():
    class FakeChannel:
        def __init__(self):
            self._stdout_buffer = b""
            self._stderr_buffer = b"partial error\n"

        def recv_ready(self):
            return len(self._stdout_buffer) > 0

        def recv(self, nbytes):
            data = self._stdout_buffer
            self._stdout_buffer = b""
            return data

        def recv_stderr_ready(self):
            return len(self._stderr_buffer) > 0

        def recv_stderr(self, nbytes):
            data = self._stderr_buffer
            self._stderr_buffer = b""
            return data

    class FakeStdout:
        def __init__(self):
            self.channel = FakeChannel()

        def read(self):
            raise paramiko.SSHException("channel closed")

    class FakeStderr:
        def __init__(self):
            self.channel = FakeChannel()

        def read(self):
            return b""

    class FakeSSHClient:
        def exec_command(self, command, timeout=None):
            return None, FakeStdout(), FakeStderr()

    client = DeviceSSHClient("device.example", "user", "pass")
    result = client.run_command("show version", client=FakeSSHClient())

    assert result["success"] is False
    assert result["error_type"] == "ssh_exception"
    assert "partial error" in result["stderr"]


def test_execute_device_collection_records_failed_command_evidence(monkeypatch):
    commands = ["show version"]
    monkeypatch.setattr("app.collector.get_vendor_commands", lambda vendor, role=None: commands)

    class FakeSSHClient:
        def __init__(self, **kwargs):
            pass

        def probe(self):
            return {"reachable": True, "status": "connected"}

        def connect(self):
            return object()

        def close(self, client):
            return None

        def run_command(self, command, *, client=None):
            return {
                "command": command,
                "stdout": "partial output",
                "stderr": "error text",
                "exit_code": -1,
                "success": False,
                "error": "Command timed out or failed: timeout",
                "elapsed_seconds": 7.5,
                "error_type": "timeout",
            }

    monkeypatch.setattr(collector_module, "DeviceSSHClient", FakeSSHClient)

    device = Device(
        name="lab-switch",
        hostname="10.0.0.12",
        vendor="cisco",
        username="admin",
        password="<PASSWORD-01>",
    )

    bundle = execute_device_collection(device, dry_run=False)

    assert bundle.summary["status"] == "partial"
    assert bundle.summary["failed_commands"] == commands
    assert len(bundle.summary["failed_command_details"]) == 1
    detail = bundle.summary["failed_command_details"][0]
    assert detail["command"] == "show version"
    assert detail["elapsed_seconds"] == 7.5
    assert detail["error_type"] == "timeout"
    assert bundle.failed_commands == commands


def test_ssh_client_includes_supported_kex_fallbacks(monkeypatch):
    original = list(getattr(paramiko.Transport, "_preferred_kex", ()))
    original_info = dict(getattr(paramiko.Transport, "_kex_info", {}))

    class FakeSSHClient:
        def __init__(self):
            self.connected = False

        def set_missing_host_key_policy(self, policy):
            return None

        def connect(self, **kwargs):
            self.connected = True
            return None

    monkeypatch.setattr(paramiko, "SSHClient", FakeSSHClient)
    DeviceSSHClient._apply_ssh_compatibility_settings()
    preferred = list(getattr(paramiko.Transport, "_preferred_kex", ()))
    assert "diffie-hellman-group14-sha256" in preferred
    assert "diffie-hellman-group16-sha512" in preferred
    assert all(name in getattr(paramiko.Transport, "_kex_info", {}) for name in preferred)
    paramiko.Transport._preferred_kex = tuple(original)
    paramiko.Transport._kex_info = original_info


def test_build_topology_graph_from_generator_produces_edges():
    """Regression test for generator-consumption bug: edges must be produced."""
    summaries = (
        {
            "device": "SW01",
            "vendor": "cisco",
            "role": "switch",
            "discovered_neighbors": [{"neighbor": "SW02"}],
        },
        {
            "device": "SW02",
            "vendor": "cisco",
            "role": "switch",
            "discovered_neighbors": [{"neighbor": "SW01"}],
        },
    )
    graph = build_topology_graph(summary for summary in summaries)
    assert set(graph["nodes"].keys()) == {"SW01", "SW02"}
    assert {"source": "SW01", "target": "SW02"} in graph["edges"]
    assert {"source": "SW02", "target": "SW01"} in graph["edges"]


def _build_graph(summaries):
    return build_topology_graph(summaries)


def test_traverse_topology_linear_chain():
    graph = _build_graph([
        {"device": "A", "vendor": "cisco", "role": "switch", "discovered_neighbors": [{"neighbor": "B"}]},
        {"device": "B", "vendor": "cisco", "role": "switch", "discovered_neighbors": [{"neighbor": "C"}]},
        {"device": "C", "vendor": "cisco", "role": "switch", "discovered_neighbors": []},
    ])
    result = traverse_topology(graph, "A")
    assert result["successful"] == ["A", "B", "C"]
    assert result["visited"] == result["successful"]
    assert result["pending"] == []
    assert result["failed"] == []


def test_traverse_topology_cycle_prevents_revisit():
    graph = _build_graph([
        {"device": "A", "vendor": "cisco", "role": "switch", "discovered_neighbors": [{"neighbor": "B"}]},
        {"device": "B", "vendor": "cisco", "role": "switch", "discovered_neighbors": [{"neighbor": "A"}]},
    ])
    result = traverse_topology(graph, "A")
    assert result["successful"] == ["A", "B"]
    assert result["visited"] == result["successful"]
    assert result["pending"] == []
    assert result["failed"] == []


def test_traverse_topology_branching():
    graph = _build_graph([
        {"device": "A", "vendor": "cisco", "role": "switch", "discovered_neighbors": [{"neighbor": "B"}, {"neighbor": "C"}]},
        {"device": "B", "vendor": "cisco", "role": "switch", "discovered_neighbors": []},
        {"device": "C", "vendor": "cisco", "role": "switch", "discovered_neighbors": []},
    ])
    result = traverse_topology(graph, "A")
    assert result["successful"] == ["A", "B", "C"]
    assert result["visited"] == result["successful"]
    assert result["pending"] == []
    assert result["failed"] == []


def test_traverse_topology_orphaned_neighbor_is_failed():
    graph = _build_graph([
        {"device": "A", "vendor": "cisco", "role": "switch", "discovered_neighbors": [{"neighbor": "MISSING"}]},
    ])
    result = traverse_topology(graph, "A")
    assert result["successful"] == ["A"]
    assert result["pending"] == []
    assert result["failed"] == ["MISSING"]


def test_traverse_topology_single_node():
    graph = _build_graph([
        {"device": "A", "vendor": "cisco", "role": "switch", "discovered_neighbors": []},
    ])
    result = traverse_topology(graph, "A")
    assert result["successful"] == ["A"]
    assert result["pending"] == []
    assert result["failed"] == []


def test_traverse_topology_missing_start_is_failed():
    graph = _build_graph([
        {"device": "A", "vendor": "cisco", "role": "switch", "discovered_neighbors": []},
    ])
    result = traverse_topology(graph, "MISSING")
    assert result["successful"] == []
    assert result["failed"] == ["MISSING"]
    assert result["visited"] == []
    assert result["pending"] == ["A"]


def test_recursive_cli_invokes_orchestrator(monkeypatch, tmp_path):
    """Recursive mode calls run_recursive_collection with the first device as seed."""
    config_path = tmp_path / "devices.yml"
    config_path.write_text(
        "default:\n"
        "  username: admin\n"
        "  password: <PASSWORD-01>\n"
        "  enable_password: <PASSWORD-02>\n"
        "devices:\n"
        "  - name: seed-sw\n"
        "    hostname: 10.0.0.1\n"
        "    vendor: cisco\n"
    , encoding="utf-8")

    captured = {}

    def fake_run_recursive_collection(
        seed_device,
        default_credentials=None,
        *,
        max_devices=100,
        on_collected=None,
        resume_state=None,
        **kwargs,
    ):
        captured["seed"] = seed_device
        captured["default_credentials"] = default_credentials
        captured["resume_state"] = resume_state
        captured["on_collected"] = on_collected
        bundle = DeviceBundle(
            device_name=seed_device.name,
            device_vendor=seed_device.vendor,
            timestamp="2026-08-04T00:00:00Z",
            summary={"status": "dry-run-success", "commands_run": 0, "failed_commands": []},
            raw_outputs={},
            failed_commands=[],
        )
        return {
            "successful": [seed_device.name],
            "failed": [],
            "unsupported": [],
            "bundles": {seed_device.name: bundle},
        }

    monkeypatch.setattr("app.cli.run_recursive_collection", fake_run_recursive_collection)
    monkeypatch.setattr("app.cli.write_bundle", lambda bundle, output_dir: output_dir / bundle.device_name)

    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        str(config_path),
        "--output-dir",
        str(tmp_path),
        "--recursive",
    ])

    from app.cli import main

    assert main() == 0
    assert captured["seed"].name == "seed-sw"
    assert captured["seed"].vendor == "cisco"
    assert captured["default_credentials"] == {
        "username": "admin",
        "password": "<PASSWORD-01>",
        "enable_password": "<PASSWORD-02>",
    }
    assert captured["resume_state"] is None


def test_recursive_cli_creates_checkpoint_file(monkeypatch, tmp_path):
    """Recursive mode with --checkpoint-file persists state via save_checkpoint."""
    device_dict = {
        "name": "seed-sw",
        "hostname": "10.0.0.1",
        "vendor": "cisco",
        "username": "admin",
        "password": "<PASSWORD-01>",
        "enable_password": "<PASSWORD-02>",
    }

    monkeypatch.setattr("app.cli.load_devices", lambda path: [device_dict])

    def fake_run_recursive_collection(
        seed_device,
        default_credentials=None,
        *,
        max_devices=100,
        on_collected=None,
        resume_state=None,
        **kwargs,
    ):
        # Simulate orchestrator emitting a checkpoint.
        if callable(on_collected):
            on_collected({
                "visited": {seed_device.name},
                "pending": [],
                "successful": [seed_device.name],
                "failed": [],
                "unsupported": [],
            })
        bundle = DeviceBundle(
            device_name=seed_device.name,
            device_vendor=seed_device.vendor,
            timestamp="2026-08-04T00:00:00Z",
            summary={"status": "dry-run-success", "commands_run": 0, "failed_commands": []},
            raw_outputs={},
            failed_commands=[],
        )
        return {
            "successful": [seed_device.name],
            "failed": [],
            "unsupported": [],
            "bundles": {seed_device.name: bundle},
        }

    monkeypatch.setattr("app.cli.run_recursive_collection", fake_run_recursive_collection)
    monkeypatch.setattr("app.cli.write_bundle", lambda bundle, output_dir: output_dir / bundle.device_name)

    checkpoint_path = tmp_path / "checkpoint.json"
    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        str(tmp_path),
        "--recursive",
        "--checkpoint-file",
        str(checkpoint_path),
    ])

    from app.cli import main

    assert main() == 0
    assert checkpoint_path.exists()
    payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    assert "seed-sw" in payload["visited"]


def test_recursive_cli_resumes_from_existing_checkpoint(monkeypatch, tmp_path):
    """Recursive mode loads an existing checkpoint and passes it as resume_state."""
    device_dict = {
        "name": "seed-sw",
        "hostname": "10.0.0.1",
        "vendor": "cisco",
        "username": "admin",
        "password": "<PASSWORD-01>",
        "enable_password": "<PASSWORD-02>",
    }

    monkeypatch.setattr("app.cli.load_devices", lambda path: [device_dict])

    checkpoint_path = tmp_path / "checkpoint.json"
    checkpoint_path.write_text(json.dumps({
        "visited": ["seed-sw"],
        "pending": ["neighbor-sw"],
        "successful": ["seed-sw"],
        "failed": [],
        "unsupported": [],
    }), encoding="utf-8")

    captured = {}

    def fake_run_recursive_collection(
        seed_device,
        default_credentials=None,
        *,
        max_devices=100,
        on_collected=None,
        resume_state=None,
        **kwargs,
    ):
        captured["resume_state"] = resume_state
        bundle = DeviceBundle(
            device_name=seed_device.name,
            device_vendor=seed_device.vendor,
            timestamp="2026-08-04T00:00:00Z",
            summary={"status": "dry-run-success", "commands_run": 0, "failed_commands": []},
            raw_outputs={},
            failed_commands=[],
        )
        return {
            "successful": [seed_device.name],
            "failed": [],
            "unsupported": [],
            "bundles": {seed_device.name: bundle},
        }

    monkeypatch.setattr("app.cli.run_recursive_collection", fake_run_recursive_collection)
    monkeypatch.setattr("app.cli.write_bundle", lambda bundle, output_dir: output_dir / bundle.device_name)

    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        str(tmp_path),
        "--recursive",
        "--checkpoint-file",
        str(checkpoint_path),
    ])

    from app.cli import main

    assert main() == 0
    assert captured["resume_state"] is not None
    assert "seed-sw" in captured["resume_state"]["visited"]
    assert captured["resume_state"]["pending"] == ["neighbor-sw"]


def test_recursive_cli_writes_bundle_manifest(monkeypatch, tmp_path):
    """Recursive mode still writes bundle_manifest.json and topology.json."""
    device_dict = {
        "name": "seed-sw",
        "hostname": "10.0.0.1",
        "vendor": "cisco",
        "username": "admin",
        "password": "<PASSWORD-01>",
    }

    monkeypatch.setattr("app.cli.load_devices", lambda path: [device_dict])

    def fake_run_recursive_collection(
        seed_device,
        default_credentials=None,
        *,
        max_devices=100,
        on_collected=None,
        resume_state=None,
        **kwargs,
    ):
        bundle = DeviceBundle(
            device_name=seed_device.name,
            device_vendor=seed_device.vendor,
            timestamp="2026-08-04T00:00:00Z",
            summary={"status": "dry-run-success", "commands_run": 0, "failed_commands": []},
            raw_outputs={},
            failed_commands=[],
        )
        return {
            "successful": [seed_device.name],
            "failed": [],
            "unsupported": [],
            "bundles": {seed_device.name: bundle},
        }

    monkeypatch.setattr("app.cli.run_recursive_collection", fake_run_recursive_collection)

    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        str(tmp_path),
        "--recursive",
    ])

    from app.cli import main

    assert main() == 0
    manifest = tmp_path / "bundle_manifest.json"
    assert manifest.exists()
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["dry_run"] is False
    assert payload["devices"][0]["name"] == "seed-sw"
    assert (tmp_path / "topology.json").exists()


def test_non_recursive_path_unchanged(monkeypatch, tmp_path):
    """Without --recursive the CLI still iterates devices and writes the manifest."""
    device_dict = {
        "name": "flat-sw",
        "hostname": "10.0.0.1",
        "vendor": "cisco",
        "username": "admin",
        "password": "<PASSWORD-01>",
    }

    monkeypatch.setattr("app.cli.load_devices", lambda path: [device_dict])

    captured = {}

    def fake_execute(device, dry_run=False):
        captured["device"] = device
        captured["dry_run"] = dry_run
        return DeviceBundle(
            device_name=device.name,
            device_vendor=device.vendor,
            timestamp="2026-08-04T00:00:00Z",
            summary={"status": "dry-run-success", "commands_run": 0, "failed_commands": []},
            raw_outputs={},
            failed_commands=[],
        )

    monkeypatch.setattr("app.cli.execute_device_collection", fake_execute)
    monkeypatch.setattr("app.cli.write_bundle", lambda bundle, output_dir: output_dir / bundle.device_name)

    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        str(tmp_path),
        "--dry-run",
    ])

    from app.cli import main

    assert main() == 0
    assert captured["device"].name == "flat-sw"
    assert captured["dry_run"] is True
    manifest = json.loads((tmp_path / "bundle_manifest.json").read_text(encoding="utf-8"))
    assert manifest["devices"][0]["name"] == "flat-sw"


def test_missing_checkpoint_file_is_handled(monkeypatch, tmp_path):
    """A non-existent checkpoint file is treated as no resume state."""
    device_dict = {
        "name": "seed-sw",
        "hostname": "10.0.0.1",
        "vendor": "cisco",
        "username": "admin",
        "password": "<PASSWORD-01>",
    }

    monkeypatch.setattr("app.cli.load_devices", lambda path: [device_dict])

    captured = {}

    def fake_run_recursive_collection(
        seed_device,
        default_credentials=None,
        *,
        max_devices=100,
        on_collected=None,
        resume_state=None,
        **kwargs,
    ):
        captured["resume_state"] = resume_state
        bundle = DeviceBundle(
            device_name=seed_device.name,
            device_vendor=seed_device.vendor,
            timestamp="2026-08-04T00:00:00Z",
            summary={"status": "dry-run-success", "commands_run": 0, "failed_commands": []},
            raw_outputs={},
            failed_commands=[],
        )
        return {
            "successful": [seed_device.name],
            "failed": [],
            "unsupported": [],
            "bundles": {seed_device.name: bundle},
        }

    monkeypatch.setattr("app.cli.run_recursive_collection", fake_run_recursive_collection)
    monkeypatch.setattr("app.cli.write_bundle", lambda bundle, output_dir: output_dir / bundle.device_name)

    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        str(tmp_path),
        "--recursive",
        "--checkpoint-file",
        str(tmp_path / "missing.json"),
    ])

    from app.cli import main

    assert main() == 0
    assert captured["resume_state"] is None


def test_recursive_cli_dry_run_does_not_invoke_orchestrator(monkeypatch, tmp_path):
    """Recursive --dry-run must not call run_recursive_collection or real collection."""
    device_dict = {
        "name": "seed-sw",
        "hostname": "10.0.0.1",
        "vendor": "cisco",
        "username": "admin",
        "password": "<PASSWORD-01>",
    }

    monkeypatch.setattr("app.cli.load_devices", lambda path: [device_dict])

    called = {"orchestrator": False, "execute": False}

    def fake_run_recursive_collection(*args, **kwargs):
        called["orchestrator"] = True
        return {}

    def fake_execute(device, dry_run=False):
        called["execute"] = True
        return DeviceBundle(
            device_name=device.name,
            device_vendor=device.vendor,
            timestamp="2026-08-04T00:00:00Z",
            summary={"status": "dry-run-success", "commands_run": 0, "failed_commands": []},
            raw_outputs={},
            failed_commands=[],
        )

    monkeypatch.setattr("app.cli.run_recursive_collection", fake_run_recursive_collection)
    monkeypatch.setattr("app.cli.execute_device_collection", fake_execute)
    monkeypatch.setattr("app.cli.write_bundle", lambda bundle, output_dir: output_dir / bundle.device_name)

    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        str(tmp_path),
        "--dry-run",
        "--recursive",
    ])

    from app.cli import main

    assert main() == 0
    assert called["orchestrator"] is False
    assert called["execute"] is True

    manifest = json.loads((tmp_path / "bundle_manifest.json").read_text(encoding="utf-8"))
    assert manifest["dry_run"] is True
    assert manifest["devices"][0]["status"] == "dry-run-success"


def test_recursive_cli_uses_config_default_block_for_credentials(monkeypatch, tmp_path):
    """Default credentials for recursive neighbors come from the config default block, not seed overrides."""
    from app.config import load_default_credentials

    config_path = tmp_path / "devices.yml"
    config_path.write_text(
        "default:\n"
        "  username: global-user\n"
        "  password: <PASSWORD-03>\n"
        "  enable_password: <PASSWORD-04>\n"
        "devices:\n"
        "  - name: seed-sw\n"
        "    hostname: 10.0.0.1\n"
        "    vendor: cisco\n"
        "    username: seed-user\n"
        "    password: <PASSWORD-12>\n"
    , encoding="utf-8")

    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        str(config_path),
        "--output-dir",
        str(tmp_path),
        "--recursive",
    ])

    captured = {}

    def fake_run_recursive_collection(
        seed_device,
        default_credentials=None,
        *,
        max_devices=100,
        on_collected=None,
        resume_state=None,
        **kwargs,
    ):
        captured["default_credentials"] = default_credentials
        bundle = DeviceBundle(
            device_name=seed_device.name,
            device_vendor=seed_device.vendor,
            timestamp="2026-08-04T00:00:00Z",
            summary={"status": "dry-run-success", "commands_run": 0, "failed_commands": []},
            raw_outputs={},
            failed_commands=[],
        )
        return {
            "successful": [seed_device.name],
            "failed": [],
            "unsupported": [],
            "bundles": {seed_device.name: bundle},
        }

    monkeypatch.setattr("app.cli.run_recursive_collection", fake_run_recursive_collection)
    monkeypatch.setattr("app.cli.write_bundle", lambda bundle, output_dir: output_dir / bundle.device_name)

    from app.cli import main

    assert main() == 0
    assert captured["default_credentials"] == {
        "username": "global-user",
        "password": "<PASSWORD-03>",
        "enable_password": "<PASSWORD-04>",
    }


def test_load_default_credentials_reads_raw_config_block(tmp_path):
    from app.config import load_default_credentials

    config_path = tmp_path / "devices.yml"
    config_path.write_text(
        "default:\n"
        "  username: a\n"
        "  password: <PASSWORD-05>\n"
        "devices:\n"
        "  - name: d\n"
    , encoding="utf-8")

    assert load_default_credentials(config_path) == {"username": "a", "password": "<PASSWORD-05>"}


def test_load_default_credentials_returns_empty_when_no_default(tmp_path):
    from app.config import load_default_credentials

    config_path = tmp_path / "devices.yml"
    config_path.write_text(
        "devices:\n"
        "  - name: d\n"
    , encoding="utf-8")

    assert load_default_credentials(config_path) == {}


def test_interactive_temp_inventory_is_deleted_on_success(monkeypatch, tmp_path):
    inputs = iter(["10.0.0.1", "admin", "<PASSWORD-01>", "22", "cisco"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    monkeypatch.setattr("getpass.getpass", lambda prompt: next(inputs))
    monkeypatch.setattr("app.cli.load_devices", lambda path: [{"name": "sw", "hostname": "10.0.0.1", "vendor": "cisco", "username": "admin", "password": "<PASSWORD-01>"}])

    bundles = []
    def fake_execute(device, dry_run=False):
        from app.models import DeviceBundle
        bundles.append(device)
        return DeviceBundle(
            device_name=device.name,
            device_vendor=device.vendor,
            timestamp="2026-09-01T00:00:00Z",
            summary={"status": "dry-run-success"},
            raw_outputs={},
            failed_commands=[],
        )
    monkeypatch.setattr("app.cli.execute_device_collection", fake_execute)
    monkeypatch.setattr("app.cli.write_bundle", lambda bundle, output_dir: tmp_path / bundle.device_name)

    monkeypatch.setattr("sys.argv", ["prog", "--output-dir", str(tmp_path), "--dry-run"])
    from app.cli import main
    main()
    assert not any(Path(p).name.startswith("interactive_devices_") for p in (tmp_path.glob("*")))


def test_interactive_temp_inventory_is_deleted_on_exception(monkeypatch, tmp_path):
    import app.cli as cli_module
    captured_paths = []
    original_prompt = cli_module._prompt_interactive_inventory

    def tracking_prompt():
        path = original_prompt()
        captured_paths.append(path)
        return path

    inputs = iter(["10.0.0.1", "admin", "<PASSWORD-01>", "22", "cisco"])
    monkeypatch.setattr("app.cli._prompt_interactive_inventory", tracking_prompt)
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    monkeypatch.setattr("getpass.getpass", lambda prompt: next(inputs))
    monkeypatch.setattr("app.cli.load_devices", lambda path: (_ for _ in ()).throw(RuntimeError("boom")))

    monkeypatch.setattr("sys.argv", ["prog", "--output-dir", str(tmp_path)])
    from app.cli import main
    try:
        main()
    except RuntimeError:
        pass
    assert captured_paths
    assert not captured_paths[0].exists()


def test_interactive_temp_inventory_is_deleted_on_dry_run(monkeypatch, tmp_path):
    inputs = iter(["10.0.0.1", "admin", "<PASSWORD-01>", "22", "cisco"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    monkeypatch.setattr("getpass.getpass", lambda prompt: next(inputs))
    monkeypatch.setattr("app.cli.load_devices", lambda path: [{"name": "sw", "hostname": "10.0.0.1", "vendor": "cisco", "username": "admin", "password": "<PASSWORD-01>"}])
    monkeypatch.setattr("app.cli.execute_device_collection", lambda device, dry_run=False: None)

    monkeypatch.setattr("sys.argv", ["prog", "--output-dir", str(tmp_path), "--dry-run", "--probe"])
    from app.cli import main
    main()
    assert not any(Path(p).name.startswith("interactive_devices_") for p in (tmp_path.glob("*")))


def test_prompt_interactive_inventory_writes_valid_yaml(monkeypatch):
    inputs = iter(["10.0.0.1", "admin", "22", "cisco"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    monkeypatch.setattr("getpass.getpass", lambda prompt: "<PASSWORD-01>")

    runtime_path = _prompt_interactive_inventory()

    import yaml
    data = yaml.safe_load(runtime_path.read_text(encoding="utf-8"))
    assert data["devices"][0]["hostname"] == "10.0.0.1"
    assert data["devices"][0]["username"] == "admin"
    assert data["devices"][0]["password"] == "<PASSWORD-01>"
    assert data["devices"][0]["port"] == 22
    assert data["devices"][0]["vendor"] == "cisco"
    runtime_path.unlink(missing_ok=True)


def test_prompt_interactive_inventory_defaults_port_and_vendor(monkeypatch):
    inputs = iter(["10.0.0.2", "admin", "", ""])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    monkeypatch.setattr("getpass.getpass", lambda prompt: "<PASSWORD-01>")

    runtime_path = _prompt_interactive_inventory()
    import yaml
    data = yaml.safe_load(runtime_path.read_text(encoding="utf-8"))
    assert data["devices"][0]["port"] == 22
    assert data["devices"][0]["vendor"] == "auto"
    runtime_path.unlink(missing_ok=True)


def test_prompt_interactive_inventory_password_not_echoed(monkeypatch):
    captured = []

    def recording_input(prompt):
        captured.append(("input", prompt))
        return next(inputs)

    def capturing_getpass(prompt):
        captured.append(("getpass", prompt))
        return "<PASSWORD-01>"

    inputs = iter(["10.0.0.3", "admin", "22", ""])
    monkeypatch.setattr("builtins.input", recording_input)
    monkeypatch.setattr("getpass.getpass", capturing_getpass)

    runtime_path = _prompt_interactive_inventory()
    input_values = [value for kind, value in captured if kind == "input"]
    assert "<PASSWORD-01>" not in input_values
    assert any(kind == "getpass" for kind, _ in captured)
    runtime_path.unlink(missing_ok=True)


def test_prompt_interactive_inventory_unlinks_file_on_yaml_failure(monkeypatch):
    inputs = iter(["10.0.0.4", "admin", "22", ""])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    monkeypatch.setattr("getpass.getpass", lambda prompt: "<PASSWORD-01>")

    def failing_dump(*args, **kwargs):
        raise RuntimeError("disk full")

    monkeypatch.setattr("yaml.safe_dump", failing_dump)
    with pytest.raises(RuntimeError, match="disk full"):
        _prompt_interactive_inventory()
    assert not any(Path(p).name.startswith("interactive_devices_") for p in Path(tempfile.gettempdir()).glob("interactive_devices_*"))


def test_prompt_interactive_inventory_propagates_unlink_failure(monkeypatch):
    inputs = iter(["10.0.0.5", "admin", "22", ""])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    monkeypatch.setattr("getpass.getpass", lambda prompt: "<PASSWORD-01>")

    def fake_mkstemp(*args, **kwargs):
        return -1, str(Path(tempfile.gettempdir()) / "interactive_devices_unlink_fail.yml")

    def failing_dump(*args, **kwargs):
        raise RuntimeError("disk full")

    def failing_unlink(self, *args, **kwargs):
        raise OSError(13, "Permission denied")

    monkeypatch.setattr("tempfile.mkstemp", fake_mkstemp)
    monkeypatch.setattr("yaml.safe_dump", failing_dump)
    monkeypatch.setattr("pathlib.Path.unlink", failing_unlink)
    with pytest.raises(OSError, match="Permission denied"):
        _prompt_interactive_inventory()
    assert not Path(tempfile.gettempdir(), "interactive_devices_unlink_fail.yml").exists()


def test_non_recursive_cli_writes_analysis_artifacts(monkeypatch, tmp_path):
    inputs = iter(["10.0.0.5", "admin", "22", ""])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    monkeypatch.setattr("getpass.getpass", lambda prompt: "<PASSWORD-01>")

    def failing_dump(*args, **kwargs):
        raise RuntimeError("disk full")

    def failing_unlink(self, *args, **kwargs):
        raise OSError(13, "Permission denied")

    monkeypatch.setattr("yaml.safe_dump", failing_dump)
    monkeypatch.setattr("pathlib.Path.unlink", failing_unlink)
    with pytest.raises(OSError, match="Permission denied"):
        _prompt_interactive_inventory()


def test_non_recursive_cli_writes_analysis_artifacts(monkeypatch, tmp_path):
    """Non-recursive collections generate merged summary.json and troubleshooting_bundle.json."""
    device_dict = {
        "name": "flat-sw",
        "hostname": "10.0.0.1",
        "vendor": "cisco",
        "username": "admin",
        "password": "<PASSWORD-01>",
    }

    monkeypatch.setattr("app.cli.load_devices", lambda path: [device_dict])

    bundle = DeviceBundle(
        device_name="flat-sw",
        device_vendor="cisco",
        timestamp="2026-08-04T00:00:00Z",
        summary={
            "device": "flat-sw",
            "hostname": "10.0.0.1",
            "vendor": "cisco",
            "status": "collected",
            "commands_run": 1,
            "failed_commands": [],
        },
        raw_outputs={"show version": "Cisco IOS XE Software, Version 17.09.04"},
        failed_commands=[],
    )
    monkeypatch.setattr("app.cli.execute_device_collection", lambda device, dry_run=False: bundle)

    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        str(tmp_path),
    ])

    from app.cli import main

    assert main() == 0

    device_dir = tmp_path / "flat-sw"
    summary_path = device_dir / "summary.json"
    troubleshooting_path = device_dir / "troubleshooting_bundle.json"
    assert summary_path.exists()
    assert troubleshooting_path.exists()

    summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))
    troubleshooting_payload = json.loads(troubleshooting_path.read_text(encoding="utf-8"))

    # Raw collector fields are preserved.
    assert summary_payload["device"] == "flat-sw"
    assert summary_payload["hostname"] == "10.0.0.1"
    assert summary_payload["vendor"] == "cisco"
    assert summary_payload["status"] == "collected"
    assert summary_payload["commands_run"] == 1
    # Health fields are merged in.
    assert "health_score" in summary_payload
    assert "warnings" in summary_payload
    assert "critical" in summary_payload

    assert troubleshooting_payload["hostname"] == "10.0.0.1"
    assert troubleshooting_payload["health_score"] == summary_payload["health_score"]
    assert "briefing" in troubleshooting_payload


def test_non_recursive_dry_run_does_not_write_analysis_artifacts(monkeypatch, tmp_path):
    """Dry-run mode does not generate analysis artifacts."""
    device_dict = {
        "name": "flat-sw",
        "hostname": "10.0.0.1",
        "vendor": "cisco",
        "username": "admin",
        "password": "<PASSWORD-01>",
    }

    monkeypatch.setattr("app.cli.load_devices", lambda path: [device_dict])
    monkeypatch.setattr("app.cli.execute_device_collection", lambda device, dry_run=False: DeviceBundle(
        device_name=device.name,
        device_vendor=device.vendor,
        timestamp="2026-08-04T00:00:00Z",
        summary={
            "device": device.name,
            "hostname": "10.0.0.1",
            "vendor": "cisco",
            "status": "dry-run-success",
            "commands_run": 0,
            "failed_commands": [],
        },
        raw_outputs={},
        failed_commands=[],
    ))

    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        str(tmp_path),
        "--dry-run",
    ])

    from app.cli import main

    assert main() == 0

    device_dir = tmp_path / "flat-sw"
    summary_path = device_dir / "summary.json"
    assert summary_path.exists()
    # Raw summary is preserved; health/analysis fields must be absent.
    summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary_payload["status"] == "dry-run-success"
    assert "health_score" not in summary_payload
    assert not (device_dir / "troubleshooting_bundle.json").exists()

    # ZIP should not contain analysis artifacts in dry-run.
    with zipfile.ZipFile(device_dir.with_suffix(".zip"), "r") as zf:
        assert "troubleshooting_bundle.json" not in zf.namelist()
        raw_summary = json.loads(zf.read("summary.json"))
        assert raw_summary["status"] == "dry-run-success"
        assert "health_score" not in raw_summary


def test_recursive_cli_writes_analysis_artifacts(monkeypatch, tmp_path):
    """Recursive collections generate analysis artifacts per collected device."""
    device_dict = {
        "name": "seed-sw",
        "hostname": "10.0.0.1",
        "vendor": "cisco",
        "username": "admin",
        "password": "<PASSWORD-01>",
    }

    monkeypatch.setattr("app.cli.load_devices", lambda path: [device_dict])

    def fake_run_recursive_collection(
        seed_device,
        default_credentials=None,
        *,
        max_devices=100,
        on_collected=None,
        resume_state=None,
        **kwargs,
    ):
        bundles = {}
        for name in ("seed-sw", "neighbor-sw"):
            bundles[name] = DeviceBundle(
                device_name=name,
                device_vendor="cisco",
                timestamp="2026-08-04T00:00:00Z",
                summary={
                    "device": name,
                    "hostname": f"10.0.0.{len(bundles) + 1}",
                    "vendor": "cisco",
                    "status": "collected",
                    "commands_run": 1,
                    "failed_commands": [],
                },
                raw_outputs={"show version": "Cisco IOS XE Software, Version 17.09.04"},
                failed_commands=[],
            )
        return {
            "successful": list(bundles.keys()),
            "failed": [],
            "unsupported": [],
            "bundles": bundles,
        }

    monkeypatch.setattr("app.cli.run_recursive_collection", fake_run_recursive_collection)

    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        str(tmp_path),
        "--recursive",
    ])

    from app.cli import main

    assert main() == 0

    for name in ("seed-sw", "neighbor-sw"):
        device_dir = tmp_path / name
        assert (device_dir / "summary.json").exists()
        assert (device_dir / "troubleshooting_bundle.json").exists()

        summary_payload = json.loads((device_dir / "summary.json").read_text(encoding="utf-8"))
        assert summary_payload["device"] == name
        assert "health_score" in summary_payload

        # Analysis artifacts are packaged into the ZIP.
        with zipfile.ZipFile(device_dir.with_suffix(".zip"), "r") as zf:
            assert "summary.json" in zf.namelist()
            assert "troubleshooting_bundle.json" in zf.namelist()
            archived_summary = json.loads(zf.read("summary.json"))
            assert archived_summary["device"] == name
            assert "health_score" in archived_summary


def test_analysis_pipeline_preserves_existing_outputs(monkeypatch, tmp_path):
    """Existing bundle_manifest.json and topology.json shapes are unchanged."""
    device_dict = {
        "name": "flat-sw",
        "hostname": "10.0.0.1",
        "vendor": "cisco",
        "username": "admin",
        "password": "<PASSWORD-01>",
    }

    monkeypatch.setattr("app.cli.load_devices", lambda path: [device_dict])

    bundle = DeviceBundle(
        device_name="flat-sw",
        device_vendor="cisco",
        timestamp="2026-08-04T00:00:00Z",
        summary={
            "device": "flat-sw",
            "hostname": "10.0.0.1",
            "vendor": "cisco",
            "role": "switch",
            "discovered_neighbors": [{"neighbor": "sw02", "source": "show cdp neighbors detail"}],
            "status": "collected",
            "commands_run": 1,
            "failed_commands": [],
        },
        raw_outputs={"show version": "Cisco IOS XE Software, Version 17.09.04"},
        failed_commands=[],
    )
    monkeypatch.setattr("app.cli.execute_device_collection", lambda device, dry_run=False: bundle)

    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        str(tmp_path),
    ])

    from app.cli import main

    assert main() == 0

    manifest = json.loads((tmp_path / "bundle_manifest.json").read_text(encoding="utf-8"))
    assert manifest["dry_run"] is False
    assert manifest["devices"][0]["name"] == "flat-sw"
    assert manifest["devices"][0]["vendor"] == "cisco"
    assert manifest["devices"][0]["status"] == "collected"
    assert "bundle_path" in manifest["devices"][0]

    topology = json.loads((tmp_path / "topology.json").read_text(encoding="utf-8"))
    assert "flat-sw" in topology["nodes"]
    assert any(edge["source"] == "flat-sw" for edge in topology["edges"])


def test_non_recursive_cli_packages_analysis_artifacts_in_zip(monkeypatch, tmp_path):
    """Non-recursive collections include summary.json and troubleshooting_bundle.json in the ZIP."""
    device_dict = {
        "name": "flat-sw",
        "hostname": "10.0.0.1",
        "vendor": "cisco",
        "username": "admin",
        "password": "<PASSWORD-01>",
    }

    monkeypatch.setattr("app.cli.load_devices", lambda path: [device_dict])

    bundle = DeviceBundle(
        device_name="flat-sw",
        device_vendor="cisco",
        timestamp="2026-08-04T00:00:00Z",
        summary={
            "device": "flat-sw",
            "hostname": "10.0.0.1",
            "vendor": "cisco",
            "status": "collected",
            "commands_run": 1,
            "failed_commands": [],
        },
        raw_outputs={"show version": "Cisco IOS XE Software, Version 17.09.04"},
        failed_commands=[],
    )
    monkeypatch.setattr("app.cli.execute_device_collection", lambda device, dry_run=False: bundle)

    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        str(tmp_path),
    ])

    from app.cli import main

    assert main() == 0

    device_dir = tmp_path / "flat-sw"
    archive_path = device_dir.with_suffix(".zip")
    assert archive_path.exists()

    with zipfile.ZipFile(archive_path, "r") as zf:
        assert "summary.json" in zf.namelist()
        assert "troubleshooting_bundle.json" in zf.namelist()
        archived_summary = json.loads(zf.read("summary.json"))
        assert archived_summary["device"] == "flat-sw"
        assert "health_score" in archived_summary


def test_analysis_pipeline_order_is_deterministic(monkeypatch, tmp_path):
    """write_bundle executes summary → health → troubleshooting bundle in order."""
    bundle = DeviceBundle(
        device_name="flat-sw",
        device_vendor="cisco",
        timestamp="2026-08-04T00:00:00Z",
        summary={"device": "flat-sw", "hostname": "10.0.0.1", "vendor": "cisco", "status": "collected"},
        raw_outputs={"show version": "Cisco IOS XE Software, Version 17.09.04"},
        failed_commands=[],
    )

    calls = []

    def fake_build_device_summary(bundle):
        calls.append("summary")
        return {"hostname": bundle.device_name}

    def fake_score_device_health(summary):
        calls.append("health")
        return {"score": 100, "warnings": [], "critical": []}

    def fake_build_troubleshooting_bundle(summary, health, raw_outputs):
        calls.append("troubleshooting")
        return {"briefing": "ok"}

    monkeypatch.setattr("app.collector.build_device_summary", fake_build_device_summary)
    monkeypatch.setattr("app.collector.score_device_health", fake_score_device_health)
    monkeypatch.setattr("app.collector.build_troubleshooting_bundle", fake_build_troubleshooting_bundle)

    from app.collector import write_bundle

    device_dir = write_bundle(bundle, tmp_path)
    assert calls == ["summary", "health", "troubleshooting"]
    assert (device_dir / "summary.json").exists()
    assert (device_dir / "troubleshooting_bundle.json").exists()

