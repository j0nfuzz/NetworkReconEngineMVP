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
