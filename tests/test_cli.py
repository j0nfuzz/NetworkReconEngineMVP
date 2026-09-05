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
from app.cli import parse_args, probe_devices, _is_legacy_error, _is_valid_target, _run_recursive_cli, _prompt_interactive_inventory
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


@pytest.mark.parametrize(
    "hostname,expected",
    [
        ("10.0.0.1", True),
        ("192.168.2.241", True),
        ("255.255.255.255", True),
        ("0.0.0.0", True),
        ("::1", True),
        ("fe80::1", True),
        ("2001:db8::1", True),
        ("sw01.example.com", True),
        ("sw01", True),
        ("192.168.241", False),
        ("10.0.0.256", False),
        ("10.0.0", False),
        ("", False),
        ("   ", False),
        ("-invalid.com", False),
        ("invalid-.com", False),
    ],
)
def test_is_valid_target(hostname, expected):
    assert _is_valid_target(hostname) is expected


def test_invalid_target_fails_before_ssh_probe(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(
        "app.cli.load_devices",
        lambda _path: [
            {
                "name": "bad-device",
                "hostname": "192.168.241",
                "vendor": "auto",
                "username": "admin",
                "password": "<PASSWORD-01>",
            }
        ],
    )

    def fail_if_probed(*args, **kwargs):
        raise AssertionError("probe boundary should not be reached for invalid target")

    monkeypatch.setattr("app.cli.probe_devices", fail_if_probed)
    monkeypatch.setattr("app.cli.execute_device_collection", fail_if_probed)
    monkeypatch.setattr("app.cli.run_recursive_collection", fail_if_probed)

    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        str(tmp_path / "devices.yml"),
        "--output-dir",
        str(tmp_path),
    ])

    from app.cli import main

    assert main() == 1
    captured = capsys.readouterr().out
    assert "Invalid target '192.168.241'" in captured
    assert "Provide a valid IPv4, IPv6, or DNS hostname" in captured


def test_empty_target_fails_before_ssh_probe(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(
        "app.cli.load_devices",
        lambda _path: [
            {
                "name": "empty-device",
                "hostname": "",
                "vendor": "auto",
                "username": "admin",
                "password": "<PASSWORD-01>",
            }
        ],
    )

    def fail_if_probed(*args, **kwargs):
        raise AssertionError("probe boundary should not be reached for empty target")

    monkeypatch.setattr("app.cli.probe_devices", fail_if_probed)
    monkeypatch.setattr("app.cli.execute_device_collection", fail_if_probed)
    monkeypatch.setattr("app.cli.run_recursive_collection", fail_if_probed)

    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        str(tmp_path / "devices.yml"),
        "--output-dir",
        str(tmp_path),
    ])

    from app.cli import main

    assert main() == 1
    captured = capsys.readouterr().out
    assert "Invalid target" in captured


def test_valid_target_proceeds_to_collection(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "app.cli.load_devices",
        lambda _path: [
            {
                "name": "good-device",
                "hostname": "192.168.2.241",
                "vendor": "auto",
                "username": "admin",
                "password": "<PASSWORD-01>",
            }
        ],
    )

    captured = {}

    def fake_execute(device, dry_run=False):
        captured["device"] = device
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
        str(tmp_path / "devices.yml"),
        "--output-dir",
        str(tmp_path),
        "--no-recurse",
        "--dry-run",
    ])

    from app.cli import main

    assert main() == 0
    assert captured["device"].hostname == "192.168.2.241"


def test_valid_hostname_proceeds_to_collection(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "app.cli.load_devices",
        lambda _path: [
            {
                "name": "good-device",
                "hostname": "sw01.lab.example.com",
                "vendor": "auto",
                "username": "admin",
                "password": "<PASSWORD-01>",
            }
        ],
    )

    captured = {}

    def fake_execute(device, dry_run=False):
        captured["device"] = device
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
        str(tmp_path / "devices.yml"),
        "--output-dir",
        str(tmp_path),
        "--no-recurse",
        "--dry-run",
    ])

    from app.cli import main

    assert main() == 0
    assert captured["device"].hostname == "sw01.lab.example.com"


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
        "--no-recurse",
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


def test_run_command_records_transport_state_fields_on_success():
    class FakeChannel:
        def recv_exit_status(self):
            return 0

    class FakeTransport:
        def is_active(self):
            return True

    class FakeStdout:
        channel = FakeChannel()

        def read(self):
            return b"ok"

    class FakeStderr:
        channel = FakeChannel()

        def read(self):
            return b""

    class FakeSSHClient:
        def __init__(self):
            self._transport = FakeTransport()

        def exec_command(self, command, timeout=None):
            return None, FakeStdout(), FakeStderr()

        def get_transport(self):
            return self._transport

    client = DeviceSSHClient("device.example", "user", "pass")
    result = client.run_command("show version", client=FakeSSHClient())

    assert result["success"] is True
    assert result["transport_active"] is True
    assert result["recovery_attempted"] is False
    assert result["recovery_successful"] is None


def test_run_command_recovers_from_timeout_on_retry():
    class FakeTransport:
        def is_active(self):
            return False

    class FailingStdout:
        channel = None

        def read(self):
            raise socket.timeout("Command timed out")

    class SucceedingStdout:
        class _Channel:
            def recv_exit_status(self):
                return 0

        channel = _Channel()

        def read(self):
            return b"recovered output"

    class FailingStderr:
        channel = None

        def read(self):
            return b""

    class SucceedingStderr:
        channel = SucceedingStdout._Channel()

        def read(self):
            return b""

    class FailingSSHClient:
        _transport = FakeTransport()

        def exec_command(self, command, timeout=None):
            return None, FailingStdout(), FailingStderr()

        def get_transport(self):
            return self._transport

    class SucceedingSSHClient:
        _transport = FakeTransport()

        def exec_command(self, command, timeout=None):
            return None, SucceedingStdout(), SucceedingStderr()

        def get_transport(self):
            return self._transport

    client = DeviceSSHClient("device.example", "user", "pass")

    original_connect = client.connect
    call_count = {"n": 0}

    def fake_connect():
        call_count["n"] += 1
        return SucceedingSSHClient()

    client.connect = fake_connect
    result = client.run_command("show version", client=FailingSSHClient())

    assert result["success"] is True
    assert result["stdout"] == "recovered output"
    assert result["recovery_attempted"] is True
    assert result["recovery_successful"] is True
    assert result.get("original_elapsed_seconds") is not None
    assert result.get("original_stdout") is not None
    assert result.get("_recovered_client") is not None
    assert call_count["n"] == 1

    client.connect = original_connect


def test_run_command_recovery_preserves_original_timeout_partial_output_on_success():
    class FakeChannel:
        def __init__(self):
            self._stdout_buffer = b"partial version line\n"
            self._stderr_buffer = b"partial error line\n"

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

    class FakeTransport:
        def is_active(self):
            return False

    class TimeoutStdout:
        def __init__(self):
            self.channel = FakeChannel()

        def read(self):
            raise socket.timeout("Command timed out")

    class FailingStderr:
        def __init__(self):
            self.channel = FakeChannel()

        def read(self):
            return b""

    class SucceedingChannel:
        def recv_exit_status(self):
            return 0

    class SucceedingStdout:
        channel = SucceedingChannel()

        def read(self):
            return b"full version output"

    class SucceedingStderr:
        channel = SucceedingChannel()

        def read(self):
            return b""

    class FailingSSHClient:
        _transport = FakeTransport()

        def exec_command(self, command, timeout=None):
            return None, TimeoutStdout(), FailingStderr()

        def get_transport(self):
            return self._transport

    class RecoveredSSHClient:
        _transport = FakeTransport()

        def exec_command(self, command, timeout=None):
            return None, SucceedingStdout(), SucceedingStderr()

        def get_transport(self):
            return self._transport

    client = DeviceSSHClient("device.example", "user", "pass")
    client.connect = lambda: RecoveredSSHClient()
    result = client.run_command("show version", client=FailingSSHClient())

    assert result["success"] is True
    assert result["stdout"] == "full version output"
    assert "partial version line" in result["original_stdout"]
    assert "partial error line" in result["original_stderr"]
    assert result.get("retry_stdout") == "full version output"
    assert result.get("original_error_type") == "timeout"
    assert result.get("_recovered_client") is not None


def test_run_command_recovery_preserves_original_timeout_evidence_on_retry_failure():
    class FakeTransport:
        def is_active(self):
            return False

    class FailingStdout:
        channel = None

        def read(self):
            raise socket.timeout("Command timed out")

    class FailingStderr:
        channel = None

        def read(self):
            return b""

    class FailingSSHClient:
        _transport = FakeTransport()

        def exec_command(self, command, timeout=None):
            return None, FailingStdout(), FailingStderr()

        def get_transport(self):
            return self._transport

    class RecoveredFailingSSHClient:
        _transport = FakeTransport()

        def exec_command(self, command, timeout=None):
            raise paramiko.SSHException("channel closed after reconnect")

        def get_transport(self):
            return self._transport

    client = DeviceSSHClient("device.example", "user", "pass")
    client.connect = lambda: RecoveredFailingSSHClient()
    result = client.run_command("show version", client=FailingSSHClient())

    assert result["success"] is False
    assert result["error_type"] == "timeout"
    assert result["recovery_attempted"] is True
    assert result["recovery_successful"] is False
    assert result.get("original_error_type") == "timeout" or result["error_type"] == "timeout"
    assert result.get("retry_error_type") == "ssh_exception"
    assert result.get("original_elapsed_seconds") is not None
    assert result.get("_recovered_client") is None


def test_run_command_records_recovery_failure_after_timeout():
    class FakeTransport:
        def is_active(self):
            return False

    class FailingStdout:
        channel = None

        def read(self):
            raise socket.timeout("Command timed out")

    class FailingStderr:
        channel = None

        def read(self):
            return b""

    class FailingSSHClient:
        _transport = FakeTransport()

        def exec_command(self, command, timeout=None):
            return None, FailingStdout(), FailingStderr()

        def get_transport(self):
            return self._transport

    client = DeviceSSHClient("device.example", "user", "pass")
    client.connect = lambda: (_ for _ in ()).throw(paramiko.SSHException("dead"))
    result = client.run_command("show version", client=FailingSSHClient())

    assert result["success"] is False
    assert result["error_type"] == "timeout"
    assert result["recovery_attempted"] is True
    assert result["recovery_successful"] is False
    assert result.get("original_elapsed_seconds") is not None
    assert "dead" in result["retry_error"] or "dead" in result["error"]


def test_run_command_does_not_retry_ssh_exception():
    class FakeTransport:
        def is_active(self):
            return False

    class FailingSSHClient:
        _transport = FakeTransport()

        def exec_command(self, command, timeout=None):
            raise paramiko.SSHException("channel closed")

        def get_transport(self):
            return self._transport

    client = DeviceSSHClient("device.example", "user", "pass")
    client.connect = lambda: (_ for _ in ()).throw(RuntimeError("should not reconnect"))
    result = client.run_command("show version", client=FailingSSHClient())

    assert result["success"] is False
    assert result["error_type"] == "ssh_exception"
    assert result["recovery_attempted"] is False
    assert result["recovery_successful"] is None
    assert result["transport_active"] is False


def test_cli_auto_detect_adopts_recovered_client_and_closes_both(monkeypatch, tmp_path):
    import argparse
    import app.cli as cli_module

    class FakeTransport:
        def is_active(self):
            return True

    class SucceedingChannel:
        def recv_exit_status(self):
            return 0

    class SucceedingStdout:
        channel = SucceedingChannel()

        def read(self):
            return b"Cisco IOS Software"

    class SucceedingStderr:
        channel = SucceedingChannel()

        def read(self):
            return b""

    class DeadChannel:
        def recv_exit_status(self):
            return -1

    class TimeoutStdout:
        channel = DeadChannel()

        def read(self):
            raise socket.timeout("Command timed out")

    class FailingStderr:
        channel = DeadChannel()

        def read(self):
            return b""

    closed_clients = []

    class OriginalSSHClient:
        _transport = FakeTransport()

        def exec_command(self, command, timeout=None):
            return None, TimeoutStdout(), FailingStderr()

        def get_transport(self):
            return self._transport

        def close(self):
            closed_clients.append("original")

    class RecoveredSSHClient:
        _transport = FakeTransport()

        def exec_command(self, command, timeout=None):
            return None, SucceedingStdout(), SucceedingStderr()

        def get_transport(self):
            return self._transport

        def close(self):
            closed_clients.append("recovered")

    class FakeSSHClient:
        def __init__(self, **kwargs):
            pass

        def probe(self):
            return {"reachable": True, "status": "connected"}

        def connect(self):
            return OriginalSSHClient()

        def run_command(self, command, *, client=None):
            if isinstance(client, OriginalSSHClient):
                return {
                    "command": command,
                    "stdout": "Cisco IOS Software",
                    "stderr": "",
                    "exit_code": 0,
                    "success": True,
                    "error": None,
                    "elapsed_seconds": 0.2,
                    "transport_active": True,
                    "recovery_attempted": True,
                    "recovery_successful": True,
                    "original_elapsed_seconds": 15.0,
                    "_recovered_client": RecoveredSSHClient(),
                }
            return {
                "command": command,
                "stdout": "Cisco IOS Software",
                "stderr": "",
                "exit_code": 0,
                "success": True,
                "error": None,
                "elapsed_seconds": 0.1,
            }

        def close(self, client):
            if client is not None:
                client.close()

    monkeypatch.setattr("app.ssh_client.DeviceSSHClient", FakeSSHClient)
    monkeypatch.setattr(cli_module, "identify_device", lambda output: type("I", (), {
        "vendor": "cisco", "platform": "ios", "model": "unknown", "confidence": 1.0,
    })())
    monkeypatch.setattr(cli_module, "classify_role", lambda identity, name: type("R", (), {
        "role": "switch", "confidence": 1.0,
    })())
    monkeypatch.setattr(cli_module, "execute_device_collection", lambda device, dry_run=False: type("B", (), {
        "summary": {"status": "collected"},
        "raw_outputs": {},
        "failed_commands": [],
    })())
    monkeypatch.setattr(cli_module, "write_bundle", lambda bundle, output_root: output_root)

    from app.models import Device
    device = Device(
        name="lab-switch",
        hostname="10.0.0.12",
        vendor="auto",
        username="admin",
        password="<PASSWORD-01>",
    )
    args = argparse.Namespace(
        dry_run=False,
        recursive=False,
        no_recurse=True,
        checkpoint_file=None,
        target_device=None,
        scope_depth=1,
        max_concurrent=5,
    )
    cli_module._run_cli_collection(args, [device], "", tmp_path, verbose=False)

    assert "original" in closed_clients
    assert "recovered" in closed_clients
    assert closed_clients.count("original") == 1
    assert closed_clients.count("recovered") == 1


def test_execute_device_collection_records_failed_command_evidence(monkeypatch):
    commands = ["show version"]
    monkeypatch.setattr("app.collector.get_vendor_commands", lambda vendor, role=None, platform=None: commands)

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


def test_run_recursive_cli_verbose_logs_probe_errors(monkeypatch, tmp_path):
    """Recursive verbose output surfaces probe errors returned by the orchestrator."""
    logs: list[str] = []

    def log_verbose(message: str) -> None:
        logs.append(message)

    seed = Device(name="seed-sw", hostname="10.0.0.1", vendor="cisco")
    bundle_summary: dict[str, object] = {"devices": []}

    def fake_run_recursive_collection(*args, **kwargs):
        bundle = DeviceBundle(
            device_name=seed.name,
            device_vendor=seed.vendor,
            timestamp="2026-08-04T00:00:00Z",
            summary={"status": "unreachable", "commands_run": 0, "failed_commands": []},
            raw_outputs={},
            failed_commands=[],
        )
        return {
            "successful": [],
            "failed": [seed.name],
            "unsupported": [],
            "bundles": {seed.name: bundle},
            "probe_errors": {seed.name: "[Errno 11001] getaddrinfo failed"},
        }

    monkeypatch.setattr("app.cli.run_recursive_collection", fake_run_recursive_collection)
    monkeypatch.setattr("app.cli.load_default_credentials", lambda _path: {})
    monkeypatch.setattr("app.cli.write_bundle", lambda bundle, output_dir: output_dir / bundle.device_name)

    _run_recursive_cli(
        seed,
        str(tmp_path / "devices.yml"),
        tmp_path,
        bundle_summary,
        log_verbose,
        checkpoint_file=None,
        dry_run=False,
        target_device=None,
    )

    assert any(
        "[verbose] Probe error for seed-sw: [Errno 11001] getaddrinfo failed" in msg
        for msg in logs
    )


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
        "--no-recurse",
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
        "--no-recurse",
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


def test_failed_command_details_survive_into_bundle_artifacts(tmp_path):
    """PHASE-031 regression: elapsed_seconds and error_type survive serialization."""
    failed_details = [
        {
            "command": "show interfaces",
            "elapsed_seconds": 15.23,
            "error_type": "timeout",
        },
        {
            "command": "show ip route",
            "elapsed_seconds": 0.04,
            "error_type": "ssh_exception",
        },
    ]
    bundle = DeviceBundle(
        device_name="partial-sw",
        device_vendor="cisco",
        timestamp="2026-08-04T00:00:00Z",
        summary={
            "device": "partial-sw",
            "hostname": "10.0.0.1",
            "vendor": "cisco",
            "status": "partial",
            "commands_run": 5,
            "failed_commands": ["show interfaces", "show ip route"],
            "failed_command_details": failed_details,
        },
        raw_outputs={"show version": "Cisco IOS XE Software, Version 17.09.04"},
        failed_commands=["show interfaces", "show ip route"],
    )

    from app.collector import write_bundle

    device_dir = write_bundle(bundle, tmp_path)

    summary_payload = json.loads((device_dir / "summary.json").read_text(encoding="utf-8"))
    troubleshooting_payload = json.loads((device_dir / "troubleshooting_bundle.json").read_text(encoding="utf-8"))

    assert summary_payload["failed_commands"] == ["show interfaces", "show ip route"]
    assert summary_payload["failed_command_details"] == failed_details
    assert troubleshooting_payload["failed_commands"] == ["show interfaces", "show ip route"]
    assert troubleshooting_payload["failed_command_details"] == failed_details

    with zipfile.ZipFile(device_dir.with_suffix(".zip"), "r") as zf:
        archived_summary = json.loads(zf.read("summary.json"))
        archived_troubleshooting = json.loads(zf.read("troubleshooting_bundle.json"))
    assert archived_summary["failed_command_details"] == failed_details
    assert archived_troubleshooting["failed_command_details"] == failed_details


def test_failed_command_partial_output_survives_in_bundle_artifacts(tmp_path):
    """PHASE-031 regression: partial stdout/stderr from a failed command is packaged unchanged."""
    partial_stdout = "Interface summary line 1\nInterface summary line 2"
    partial_stderr = "Warning: truncated"
    failed_details = [
        {
            "command": "show interfaces",
            "elapsed_seconds": 15.23,
            "error_type": "timeout",
        },
    ]
    raw_outputs = {
        "show version": "Cisco IOS XE Software, Version 17.09.04",
        "show interfaces": (
            f"ERROR: Command timed out\n"
            f"STDOUT:\n{partial_stdout}\n"
            f"STDERR:\n{partial_stderr}"
        ),
    }
    bundle = DeviceBundle(
        device_name="partial-sw",
        device_vendor="cisco",
        timestamp="2026-08-04T00:00:00Z",
        summary={
            "device": "partial-sw",
            "hostname": "10.0.0.1",
            "vendor": "cisco",
            "status": "partial",
            "commands_run": 2,
            "failed_commands": ["show interfaces"],
            "failed_command_details": failed_details,
        },
        raw_outputs=raw_outputs,
        failed_commands=["show interfaces"],
    )

    from app.collector import write_bundle

    device_dir = write_bundle(bundle, tmp_path)

    artifact_path = device_dir / "show_interfaces.txt"
    assert artifact_path.exists()
    artifact_text = artifact_path.read_text(encoding="utf-8")
    assert partial_stdout in artifact_text
    assert partial_stderr in artifact_text

    artifact_bytes = artifact_path.read_bytes()
    with zipfile.ZipFile(device_dir.with_suffix(".zip"), "r") as zf:
        archived_artifact = zf.read("show_interfaces.txt")
    assert archived_artifact == artifact_bytes


def test_recovered_command_evidence_includes_failed_retry_attempts(monkeypatch, tmp_path):
    """PHASE-033: a timeout followed by a failed retry is recorded in failed_command_details with original evidence."""
    commands = ["show version"]
    monkeypatch.setattr("app.collector.get_vendor_commands", lambda vendor, role=None, platform=None: commands)

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
                "stderr": "",
                "exit_code": -1,
                "success": False,
                "error": "Command timed out or failed: timeout",
                "elapsed_seconds": 20.0,
                "error_type": "timeout",
                "transport_active": False,
                "transport_state": {"exists": True, "active": False},
                "channel_state": {"exists": True, "closed": True},
                "recovery_attempted": True,
                "recovery_successful": False,
                "original_error_type": "timeout",
                "original_elapsed_seconds": 15.0,
                "original_stdout": "partial output",
                "original_stderr": "",
                "retry_error": "Command timed out or failed: timeout",
                "retry_error_type": "timeout",
                "retry_elapsed_seconds": 5.0,
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
    assert bundle.summary["recovered_commands"] == []
    detail = bundle.summary["failed_command_details"][0]
    assert detail["recovery_attempted"] is True
    assert detail["recovery_successful"] is False
    assert detail["original_error_type"] == "timeout"
    assert detail["original_stdout"] == "partial output"
    assert detail["retry_error_type"] == "timeout"
    assert detail["retry_elapsed_seconds"] == 5.0
    assert detail["transport_state"] == {"exists": True, "active": False}
    assert detail["channel_state"] == {"exists": True, "closed": True}

    device_dir = write_bundle(bundle, tmp_path)
    summary_payload = json.loads((device_dir / "summary.json").read_text(encoding="utf-8"))
    troubleshooting_payload = json.loads((device_dir / "troubleshooting_bundle.json").read_text(encoding="utf-8"))

    failed_detail = summary_payload["failed_command_details"][0]
    assert failed_detail["transport_state"] == {"exists": True, "active": False}
    assert failed_detail["channel_state"] == {"exists": True, "closed": True}
    assert troubleshooting_payload["failed_command_details"][0]["transport_state"] == {"exists": True, "active": False}
    assert troubleshooting_payload["failed_command_details"][0]["channel_state"] == {"exists": True, "closed": True}

    with zipfile.ZipFile(device_dir.with_suffix(".zip"), "r") as zf:
        archived_summary = json.loads(zf.read("summary.json"))
        archived_troubleshooting = json.loads(zf.read("troubleshooting_bundle.json"))
    assert archived_summary["failed_command_details"][0]["transport_state"] == {"exists": True, "active": False}
    assert archived_summary["failed_command_details"][0]["channel_state"] == {"exists": True, "closed": True}
    assert archived_troubleshooting["failed_command_details"][0]["transport_state"] == {"exists": True, "active": False}
    assert archived_troubleshooting["failed_command_details"][0]["channel_state"] == {"exists": True, "closed": True}


def test_end_to_end_timeout_recovery_serializes_evidence(monkeypatch, tmp_path):
    """PHASE-033 end-to-end: real DeviceSSHClient recovery, caller adoption, and artefact serialization."""
    closed_clients: list[str] = []

    class FakeTransport:
        def __init__(self, active: bool):
            self._active = active

        def is_active(self):
            return self._active

    class TimeoutStdout:
        channel = None

        def read(self):
            raise socket.timeout("Command timed out")

    class EmptyStderr:
        channel = None

        def read(self):
            return b""

    class OriginalClient:
        _transport = FakeTransport(False)

        def exec_command(self, command, timeout=None):
            return None, TimeoutStdout(), EmptyStderr()

        def get_transport(self):
            return self._transport

        def close(self):
            if "original" not in closed_clients:
                closed_clients.append("original")

    class RecoveredChannel:
        active = True
        eof_received = False
        closed = False

        def recv_exit_status(self):
            return 0

        def exit_status_ready(self):
            return True

        def recv_ready(self):
            return False

        def recv_stderr_ready(self):
            return False

    class RecoveredStdout:
        channel = RecoveredChannel()

        def read(self):
            return b"Cisco IOS XE Software, Version 17.09.04"

    class RecoveredStderr:
        channel = RecoveredChannel()

        def read(self):
            return b""

    class RecoveredClient:
        _transport = FakeTransport(True)

        def exec_command(self, command, timeout=None):
            return None, RecoveredStdout(), RecoveredStderr()

        def get_transport(self):
            return self._transport

        def close(self):
            if "recovered" not in closed_clients:
                closed_clients.append("recovered")

    connect_calls: list[str] = []

    def fake_connect(self):
        if not connect_calls:
            connect_calls.append("original")
            return OriginalClient()
        connect_calls.append("recovered")
        return RecoveredClient()

    monkeypatch.setattr(DeviceSSHClient, "connect", fake_connect)
    monkeypatch.setattr(DeviceSSHClient, "probe", lambda self: {"reachable": True, "status": "connected"})
    monkeypatch.setattr("app.collector.get_vendor_commands", lambda vendor, role=None, platform=None: ["show version"])

    device = Device(
        name="e2e-switch",
        hostname="10.0.0.99",
        vendor="cisco",
        username="admin",
        password="<PASSWORD-01>",
    )

    bundle = execute_device_collection(device, dry_run=False)
    device_dir = write_bundle(bundle, tmp_path)

    assert bundle.summary["status"] == "collected"
    assert bundle.summary["commands_run"] == 1
    assert bundle.raw_outputs["show version"] == "Cisco IOS XE Software, Version 17.09.04"
    assert "original" in closed_clients
    assert "recovered" in closed_clients

    recovered = bundle.summary["recovered_commands"]
    assert len(recovered) == 1
    evidence = recovered[0]
    assert evidence["command"] == "show version"
    assert evidence["recovery_attempted"] is True
    assert evidence["recovery_successful"] is True
    assert evidence["original_error_type"] == "timeout"
    assert evidence["original_elapsed_seconds"] is not None
    assert evidence["original_transport_active"] is False
    assert evidence["transport_active"] is True
    assert "transport_state" in evidence
    assert "channel_state" in evidence

    summary_payload = json.loads((device_dir / "summary.json").read_text(encoding="utf-8"))
    troubleshooting_payload = json.loads((device_dir / "troubleshooting_bundle.json").read_text(encoding="utf-8"))
    assert summary_payload["recovered_commands"] == recovered
    assert troubleshooting_payload["recovered_commands"] == recovered
    assert summary_payload["recovered_commands"][0]["transport_state"]["exists"] is True

    with zipfile.ZipFile(device_dir.with_suffix(".zip"), "r") as zf:
        archived_summary = json.loads(zf.read("summary.json"))
        archived_troubleshooting = json.loads(zf.read("troubleshooting_bundle.json"))
    assert archived_summary["recovered_commands"] == recovered
    assert archived_troubleshooting["recovered_commands"] == recovered
    assert "channel_state" in archived_summary["recovered_commands"][0]
    assert "transport_state" in archived_summary["recovered_commands"][0]


def test_parse_args_no_recurse_disables_recursion(monkeypatch):
    """PHASE-052: --no-recurse is parsed and disables default recursive discovery."""
    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        "output",
        "--no-recurse",
    ])
    args = parse_args()
    assert args.no_recurse is True


def test_parse_args_recursive_is_backward_compatible_alias(monkeypatch):
    """PHASE-052: --recursive remains a valid backward-compatible alias."""
    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        "output",
        "--recursive",
    ])
    args = parse_args()
    assert args.recursive is True


def test_default_recursion_enabled_uses_first_device(monkeypatch, tmp_path):
    """PHASE-052: recursive discovery is enabled by default when devices are supplied."""
    device_dict = {
        "name": "seed-sw",
        "hostname": "10.0.0.1",
        "vendor": "cisco",
        "username": "admin",
        "password": "<PASSWORD-01>",
    }
    monkeypatch.setattr("app.cli.load_devices", lambda path: [device_dict])

    captured = {}

    def fake_run_recursive_collection(seed_device, **kwargs):
        captured["seed"] = seed_device
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
    ])

    from app.cli import main

    assert main() == 0
    assert captured["seed"].name == "seed-sw"


def test_no_recurse_runs_flat_collection(monkeypatch, tmp_path):
    """PHASE-052: --no-recurse forces flat (non-recursive) collection."""
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
    monkeypatch.setattr("app.cli.run_recursive_collection", lambda *args, **kwargs: None)

    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        str(tmp_path),
        "--no-recurse",
    ])

    from app.cli import main

    assert main() == 0
    assert captured["device"].name == "flat-sw"


def test_target_device_becomes_traversal_root_without_topology(monkeypatch, tmp_path):
    """PHASE-052: --target-device is the traversal root even without a pre-existing topology.json."""
    device_dicts = [
        {"name": "SW01", "hostname": "10.0.0.1", "vendor": "cisco", "username": "admin", "password": "<PASSWORD-01>"},
        {"name": "SW02", "hostname": "10.0.0.2", "vendor": "cisco", "username": "admin", "password": "<PASSWORD-01>"},
    ]
    monkeypatch.setattr("app.cli.load_devices", lambda path: device_dicts)

    captured = {}

    def fake_run_parallel_scoped_collection(seed_device, *, allowed_devices=None, **kwargs):
        captured["seed"] = seed_device
        captured["allowed_devices"] = allowed_devices
        return {
            "successful": [seed_device.name],
            "failed": [],
            "unsupported": [],
            "bundles": {},
        }

    monkeypatch.setattr("app.parallel_collector.run_parallel_scoped_collection", fake_run_parallel_scoped_collection)
    monkeypatch.setattr("app.cli.run_recursive_collection", lambda *args, **kwargs: None)
    monkeypatch.setattr("app.cli.load_default_credentials", lambda _path: {})

    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        str(tmp_path),
        "--target-device",
        "SW02",
    ])

    from app.cli import main

    assert main() == 0
    assert captured["seed"].name == "SW02"
    assert captured["allowed_devices"] is None


def test_target_device_with_topology_uses_scoped_collection(monkeypatch, tmp_path):
    """PHASE-052: --target-device with an existing topology.json still scopes to neighbours."""
    device_dicts = [
        {"name": "SW01", "hostname": "10.0.0.1", "vendor": "cisco", "username": "admin", "password": "<PASSWORD-01>"},
        {"name": "SW02", "hostname": "10.0.0.2", "vendor": "cisco", "username": "admin", "password": "<PASSWORD-01>"},
    ]
    monkeypatch.setattr("app.cli.load_devices", lambda path: device_dicts)

    topology = {
        "nodes": {
            "SW01": {"neighbors": ["SW02"]},
            "SW02": {"neighbors": ["SW01"]},
        },
        "edges": [],
    }
    (tmp_path / "topology.json").write_text(json.dumps(topology), encoding="utf-8")

    captured = {}

    def fake_run_parallel_scoped_collection(seed_device, *, allowed_devices=None, **kwargs):
        captured["seed"] = seed_device
        captured["allowed_devices"] = allowed_devices
        return {
            "successful": [],
            "failed": [],
            "unsupported": [],
            "bundles": {},
        }

    monkeypatch.setattr("app.parallel_collector.run_parallel_scoped_collection", fake_run_parallel_scoped_collection)
    monkeypatch.setattr("app.cli.run_recursive_collection", lambda *args, **kwargs: None)
    monkeypatch.setattr("app.cli.load_default_credentials", lambda _path: {})

    monkeypatch.setattr("sys.argv", [
        "prog",
        "--config",
        "config/devices.yml",
        "--output-dir",
        str(tmp_path),
        "--target-device",
        "SW01",
    ])

    from app.cli import main

    assert main() == 0
    assert captured["seed"].name == "SW01"
    assert captured["allowed_devices"] == {"SW01", "SW02"}

