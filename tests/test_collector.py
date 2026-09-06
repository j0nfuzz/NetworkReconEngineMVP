from __future__ import annotations

import app.collector as collector_module
from app.collector import execute_device_collection
from app.models import Device
from app.vendor_profiles import get_vendor_commands


class _FakeSSHClient:
    def __init__(self, *args, **kwargs):
        self.commands = []
        self.reachable = kwargs.pop("reachable", True)

    def probe(self):
        if self.reachable:
            return {"reachable": True, "status": "connected"}
        return {"reachable": False, "error": "connection refused"}

    def connect(self):
        return object()

    def run_command(self, command, client=None):
        self.commands.append(command)
        return {"success": True, "stdout": f"output for {command}", "stderr": ""}

    def close(self, connection):
        pass


def _fake_client_factory(reachable: bool = True):
    def factory(*args, **kwargs):
        client = _FakeSSHClient(*args, reachable=reachable, **kwargs)
        return client

    return factory


def _device(name="sw01", vendor="cisco"):
    return Device(name=name, hostname="10.0.0.1", vendor=vendor, username="u", password="<PASSWORD-06>")


def test_progress_callback_receives_probe_connect_and_command_lines(monkeypatch):
    monkeypatch.setattr(collector_module, "DeviceSSHClient", _fake_client_factory())
    lines = []
    bundle = execute_device_collection(_device(), progress=lines.append)

    assert bundle.summary["status"] == "collected"
    joined = "\n".join(lines)
    assert "[verbose] sw01: probing SSH reachability..." in joined
    assert "[verbose] sw01: probe: reachable" in joined
    assert "[verbose] sw01: connecting..." in joined
    assert "[verbose] sw01: (1/" in joined
    assert "show version" in joined


def test_progress_command_lines_are_enumerated_over_full_profile(monkeypatch):
    monkeypatch.setattr(collector_module, "DeviceSSHClient", _fake_client_factory())
    lines = []
    execute_device_collection(_device(), progress=lines.append)

    expected_total = len(get_vendor_commands("cisco"))
    numbered = [line for line in lines if "] (" in line or ": (" in line]
    assert len(numbered) == expected_total
    assert any(f"({expected_total}/{expected_total})" in line for line in lines)


def test_progress_reports_probe_failure(monkeypatch):
    monkeypatch.setattr(collector_module, "DeviceSSHClient", _fake_client_factory(reachable=False))
    lines = []
    bundle = execute_device_collection(_device(), progress=lines.append)

    assert bundle.summary["status"] == "unreachable"
    assert any("probe failed:" in line for line in lines)


def test_collection_without_progress_callback_is_unchanged(monkeypatch):
    monkeypatch.setattr(collector_module, "DeviceSSHClient", _fake_client_factory())
    bundle = execute_device_collection(_device())

    assert bundle.summary["status"] == "collected"
    assert bundle.summary["commands_run"] == len(get_vendor_commands("cisco"))
    assert bundle.raw_outputs
