from __future__ import annotations

from app.models import Device, DeviceBundle
from app.orchestrator import run_recursive_collection


class _FakeCollector:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def __call__(self, device):
        self.calls.append(device)
        return self.responses.get(
            device.name,
            DeviceBundle(
                device_name=device.name,
                device_vendor=device.vendor,
                timestamp="2026-08-05T00:00:00Z",
                summary={"status": "collected", "discovered_neighbors": []},
            ),
        )


def _make_bundle(name, vendor, status, neighbors):
    return DeviceBundle(
        device_name=name,
        device_vendor=vendor,
        timestamp="2026-08-05T00:00:00Z",
        summary={
            "status": status,
            "discovered_neighbors": neighbors,
        },
    )


def test_seed_only_no_neighbors(monkeypatch):
    device = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    monkeypatch.setattr(
        "app.orchestrator.execute_device_collection",
        lambda d: _make_bundle(d.name, d.vendor, "collected", []),
    )
    result = run_recursive_collection(device)
    assert result["successful"] == ["SW01"]
    assert result["failed"] == []
    assert result["unsupported"] == []


def test_supported_neighbor_enqueued_and_collected(monkeypatch):
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    responses = {
        "SW01": _make_bundle(
            "SW01",
            "cisco",
            "collected",
            [{"neighbor": "SW02", "ip": "10.0.0.2", "platform": "cisco WS-C2960-24TC-L"}],
        ),
        "SW02": _make_bundle("SW02", "cisco", "collected", []),
    }
    collector = _FakeCollector(responses)
    monkeypatch.setattr("app.orchestrator.execute_device_collection", collector)

    result = run_recursive_collection(seed)
    assert result["successful"] == ["SW01", "SW02"]
    assert "SW02" in result["bundles"]
    sw02 = next(d for d in collector.calls if d.name == "SW02")
    assert sw02.hostname == "10.0.0.2"
    assert sw02.vendor == "cisco"


def test_unsupported_neighbor_recorded_not_connected(monkeypatch):
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    collector = _FakeCollector(
        {
            "SW01": _make_bundle(
                "SW01",
                "cisco",
                "collected",
                [{"neighbor": "PR01", "ip": "10.0.0.10", "platform": "HP LaserJet Printer"}],
            ),
        }
    )
    monkeypatch.setattr("app.orchestrator.execute_device_collection", collector)

    result = run_recursive_collection(seed)
    assert result["successful"] == ["SW01"]
    assert result["unsupported"] == ["PR01"]
    assert "PR01" not in result["bundles"]
    assert not any(d.name == "PR01" for d in collector.calls)


def test_visited_neighbor_not_requeued(monkeypatch):
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    responses = {
        "SW01": _make_bundle(
            "SW01",
            "cisco",
            "collected",
            [{"neighbor": "SW02", "ip": "10.0.0.2", "platform": "cisco WS-C2960-24TC-L"}],
        ),
        "SW02": _make_bundle(
            "SW02",
            "cisco",
            "collected",
            [{"neighbor": "SW01", "ip": "10.0.0.1", "platform": "cisco WS-C2960-24TC-L"}],
        ),
    }
    collector = _FakeCollector(responses)
    monkeypatch.setattr("app.orchestrator.execute_device_collection", collector)

    result = run_recursive_collection(seed)
    assert result["successful"] == ["SW01", "SW02"]
    assert [d.name for d in collector.calls] == ["SW01", "SW02"]


def test_neighbor_missing_ip_skipped(monkeypatch):
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    collector = _FakeCollector(
        {
            "SW01": _make_bundle(
                "SW01",
                "cisco",
                "collected",
                [{"neighbor": "SW02", "platform": "cisco WS-C2960-24TC-L"}],
            ),
        }
    )
    monkeypatch.setattr("app.orchestrator.execute_device_collection", collector)

    result = run_recursive_collection(seed)
    assert result["successful"] == ["SW01"]
    assert result["failed"] == ["SW02"]
    assert "SW02" not in result["bundles"]


def test_failed_collection_path(monkeypatch):
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    collector = _FakeCollector(
        {
            "SW01": _make_bundle("SW01", "cisco", "unreachable", []),
        }
    )
    monkeypatch.setattr("app.orchestrator.execute_device_collection", collector)

    result = run_recursive_collection(seed)
    assert result["successful"] == []
    assert result["failed"] == ["SW01"]


def test_default_credentials_applied_to_neighbors(monkeypatch):
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco", username="seeduser", password="<PASSWORD-08>")
    responses = {
        "SW01": _make_bundle(
            "SW01",
            "cisco",
            "collected",
            [{"neighbor": "SW02", "ip": "10.0.0.2", "platform": "cisco WS-C2960-24TC-L"}],
        ),
        "SW02": _make_bundle("SW02", "cisco", "collected", []),
    }
    defaults = {"username": "admin", "password": "<PASSWORD-01>", "enable_password": "<PASSWORD-07>"}

    collector2 = _FakeCollector(responses)
    monkeypatch.setattr("app.orchestrator.execute_device_collection", collector2)
    run_recursive_collection(seed, default_credentials=defaults)
    sw02 = next(d for d in collector2.calls if d.name == "SW02")
    assert sw02.username == "admin"
    assert sw02.password == "<PASSWORD-01>"
    assert sw02.enable_password == "<PASSWORD-07>"


def test_duplicate_neighbor_not_queued_multiple_times(monkeypatch):
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    responses = {
        "SW01": _make_bundle(
            "SW01",
            "cisco",
            "collected",
            [
                {"neighbor": "SW02", "ip": "10.0.0.2", "platform": "cisco WS-C2960-24TC-L"},
                {"neighbor": "SW03", "ip": "10.0.0.3", "platform": "cisco WS-C2960-24TC-L"},
            ],
        ),
        "SW02": _make_bundle(
            "SW02",
            "cisco",
            "collected",
            [{"neighbor": "SW03", "ip": "10.0.0.3", "platform": "cisco WS-C2960-24TC-L"}],
        ),
        "SW03": _make_bundle("SW03", "cisco", "collected", []),
    }
    collector = _FakeCollector(responses)
    monkeypatch.setattr("app.orchestrator.execute_device_collection", collector)

    result = run_recursive_collection(seed)
    assert result["successful"] == ["SW01", "SW02", "SW03"]
    assert [d.name for d in collector.calls] == ["SW01", "SW02", "SW03"]


def test_allowed_devices_filters_resumed_pending_entries(monkeypatch):
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    collector = _FakeCollector({
        "SW01": _make_bundle("SW01", "cisco", "collected", []),
        "SW02": _make_bundle("SW02", "cisco", "collected", []),
        "SW03": _make_bundle("SW03", "cisco", "collected", []),
    })
    monkeypatch.setattr("app.orchestrator.execute_device_collection", collector)

    resume_state = {
        "visited": [],
        "pending": ["SW02", "SW03"],
        "successful": [],
        "failed": [],
        "unsupported": [],
    }

    emitted = []
    result = run_recursive_collection(
        seed,
        resume_state=resume_state,
        allowed_devices={"SW01", "SW02"},
        on_collected=emitted.append,
    )
    assert result["successful"] == ["SW02", "SW01"]
    assert "SW03" not in result["bundles"]
    assert not any(d.name == "SW03" for d in collector.calls)
    for state in emitted:
        assert "SW03" not in state["pending"]


def test_allowed_devices_none_preserves_all_resumed_pending_entries(monkeypatch):
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    collector = _FakeCollector({
        "SW01": _make_bundle("SW01", "cisco", "collected", []),
        "SW02": _make_bundle("SW02", "cisco", "collected", []),
    })
    monkeypatch.setattr("app.orchestrator.execute_device_collection", collector)

    resume_state = {
        "visited": [],
        "pending": ["SW02"],
        "successful": [],
        "failed": [],
        "unsupported": [],
    }

    result = run_recursive_collection(seed, resume_state=resume_state)
    assert result["successful"] == ["SW02", "SW01"]
    assert "SW02" in result["bundles"]


class _FakeSSHClient:
    """Stand-in for DeviceSSHClient in orchestrator identity tests."""

    def __init__(self, *, probe_reachable=True, version_stdout="", fail_probe=False, fail_command=False, **kwargs):
        self.probe_reachable = probe_reachable
        self.fail_probe = fail_probe
        self.fail_command = fail_command
        self.version_stdout = version_stdout
        self.calls = []

    def probe(self):
        self.calls.append("probe")
        if self.fail_probe:
            return {"reachable": False, "status": "unreachable", "error": "simulated failure"}
        if self.probe_reachable:
            return {"reachable": True, "status": "connected"}
        return {"reachable": False, "status": "unreachable"}

    def connect(self):
        self.calls.append("connect")
        if self.fail_command:
            raise RuntimeError("simulated connection failure")
        return self

    def run_command(self, command, *, client=None):
        self.calls.append(("run_command", command))
        if self.fail_command:
            raise RuntimeError("simulated command failure")
        return {
            "command": command,
            "stdout": self.version_stdout,
            "stderr": "",
            "exit_code": 0,
            "success": True,
        }

    def close(self, client):
        self.calls.append("close")


def test_auto_vendor_resolved_before_collection(monkeypatch):
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="auto")
    collector = _FakeCollector({
        "SW01": _make_bundle(
            "SW01",
            "aruba",
            "collected",
            [{"neighbor": "SW02", "ip": "10.0.0.2", "platform": "aruba 6300"}],
        ),
        "SW02": _make_bundle("SW02", "aruba", "collected", []),
    })
    monkeypatch.setattr("app.orchestrator.execute_device_collection", collector)

    fake = _FakeSSHClient(
        version_stdout="ArubaOS-CX Virtual Switch\nModel: 6300\n"
    )
    monkeypatch.setattr("app.orchestrator.DeviceSSHClient", lambda **_: fake)

    result = run_recursive_collection(seed)
    assert result["successful"] == ["SW01", "SW02"]
    sw01 = next(d for d in collector.calls if d.name == "SW01")
    assert sw01.vendor == "aruba"
    assert sw01.metadata["identity"]["platform"] == "arubaos-cx"
    assert sw01.metadata["identity"]["confidence"] > 0


def test_unknown_vendor_on_resumed_pending_device_is_resolved(monkeypatch):
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    collector = _FakeCollector({
        "SW01": _make_bundle("SW01", "cisco", "collected", []),
        "SW02": _make_bundle("SW02", "juniper", "collected", []),
    })
    monkeypatch.setattr("app.orchestrator.execute_device_collection", collector)

    fake = _FakeSSHClient(version_stdout="Juniper Networks, Inc. srx300\nJUNOS 21.4R1.12\n")
    monkeypatch.setattr("app.orchestrator.DeviceSSHClient", lambda **_: fake)

    resume_state = {
        "visited": [],
        "pending": ["SW02"],
        "successful": [],
        "failed": [],
        "unsupported": [],
    }

    result = run_recursive_collection(seed, resume_state=resume_state)
    sw02 = next(d for d in collector.calls if d.name == "SW02")
    assert sw02.vendor == "juniper"
    assert sw02.metadata["identity"]["vendor"] == "juniper"


def test_higher_confidence_identity_not_downgraded(monkeypatch):
    seed = Device(
        name="SW01",
        hostname="10.0.0.1",
        vendor="cisco",
        metadata={
            "identity": {
                "vendor": "cisco",
                "platform": "ios-xe",
                "model": "C9300",
                "confidence": 0.95,
            }
        },
    )
    collector = _FakeCollector({"SW01": _make_bundle("SW01", "cisco", "collected", [])})
    monkeypatch.setattr("app.orchestrator.execute_device_collection", collector)

    fake = _FakeSSHClient(
        version_stdout="Cisco IOS Software, C9200 Software (C9200-UNIVERSALK9-M)\n"
    )
    monkeypatch.setattr("app.orchestrator.DeviceSSHClient", lambda **_: fake)

    run_recursive_collection(seed)
    sw01 = collector.calls[0]
    assert sw01.vendor == "cisco"
    assert sw01.metadata["identity"]["platform"] == "ios-xe"
    assert sw01.metadata["identity"]["confidence"] == 0.95


def test_probe_failure_does_not_block_collection(monkeypatch):
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="auto")
    collector = _FakeCollector({"SW01": _make_bundle("SW01", "auto", "collected", [])})
    monkeypatch.setattr("app.orchestrator.execute_device_collection", collector)

    fake = _FakeSSHClient(fail_probe=True)
    monkeypatch.setattr("app.orchestrator.DeviceSSHClient", lambda **_: fake)

    result = run_recursive_collection(seed)
    assert result["successful"] == ["SW01"]
    assert result["probe_errors"] == {"SW01": "simulated failure"}
    sw01 = collector.calls[0]
    assert sw01.vendor == "auto"
    assert "identity" not in sw01.metadata or not sw01.metadata.get("identity")


def test_auto_vendor_synced_when_retaining_higher_confidence_identity(monkeypatch):
    seed = Device(
        name="SW01",
        hostname="10.0.0.1",
        vendor="auto",
        metadata={
            "identity": {
                "vendor": "aruba",
                "platform": "arubaos-cx",
                "model": "6300",
                "confidence": 0.95,
            }
        },
    )
    collector = _FakeCollector({"SW01": _make_bundle("SW01", "aruba", "collected", [])})
    monkeypatch.setattr("app.orchestrator.execute_device_collection", collector)

    fake = _FakeSSHClient(
        version_stdout="Cisco IOS Software, C9200 Software (C9200-UNIVERSALK9-M)\n"
    )
    monkeypatch.setattr("app.orchestrator.DeviceSSHClient", lambda **_: fake)

    run_recursive_collection(seed)
    sw01 = collector.calls[0]
    assert sw01.vendor == "aruba"
    assert sw01.metadata["identity"]["vendor"] == "aruba"
    assert sw01.metadata["identity"]["confidence"] == 0.95

