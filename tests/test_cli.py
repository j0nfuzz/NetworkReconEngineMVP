from __future__ import annotations

import json
from pathlib import Path

import paramiko

import app.collector as collector_module
from app.cli import parse_args, probe_devices, _is_legacy_error
from app.collector import execute_device_collection, write_bundle
from app.detector import detect_vendor_from_show_version
from app.models import Device, DeviceBundle
from app.ssh_client import DeviceSSHClient
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


def test_run_command_returns_failure_for_eof_error():
    class FakeSSHClient:
        def exec_command(self, command, timeout=None):
            raise EOFError("remote closed connection")

    client = DeviceSSHClient("device.example", "user", "pass")
    result = client.run_command("show version", client=FakeSSHClient())

    assert result["success"] is False
    assert result["exit_code"] == -1
    assert "remote closed connection" in result["error"]


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
