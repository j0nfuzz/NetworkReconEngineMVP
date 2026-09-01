from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List

import pytest

from app.cli import _run_recursive_cli
from app.models import Device, DeviceBundle
from app.parallel_collector import run_parallel_scoped_collection


def _make_bundle(name: str, vendor: str, status: str, neighbors: List[Dict[str, str]]) -> DeviceBundle:
    return DeviceBundle(
        device_name=name,
        device_vendor=vendor,
        timestamp="2026-09-01T00:00:00Z",
        summary={
            "status": status,
            "discovered_neighbors": neighbors,
        },
    )


def test_scoped_runs_execute_concurrently(monkeypatch):
    """Parallel collection gathers neighbors in waves, not one-by-one."""
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    neighbor_map = {
        "SW01": [
            {"neighbor": "SW02", "ip": "10.0.0.2", "platform": "cisco WS-C2960-24TC-L"},
            {"neighbor": "SW03", "ip": "10.0.0.3", "platform": "cisco WS-C2960-24TC-L"},
        ],
        "SW02": [],
        "SW03": [],
    }
    active = 0
    max_active = 0

    async def fake_collect(device: Device) -> DeviceBundle:
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        await asyncio.sleep(0.1)
        active -= 1
        return _make_bundle(device.name, device.vendor, "collected", neighbor_map.get(device.name, []))

    monkeypatch.setattr("app.parallel_collector._collect_device", fake_collect)

    start = time.monotonic()
    result = run_parallel_scoped_collection(
        seed,
        allowed_devices={"SW01", "SW02", "SW03"},
        max_concurrent=3,
    )
    elapsed = time.monotonic() - start

    assert result["successful"] == ["SW01", "SW02", "SW03"]
    assert set(result["bundles"].keys()) == {"SW01", "SW02", "SW03"}
    assert max_active == 2
    assert elapsed < 0.25


def test_unscoped_runs_remain_sequential(monkeypatch, tmp_path):
    """When no target-device scope is active, the CLI keeps the sequential orchestrator path."""
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    parallel_calls: List[tuple[tuple[Any, ...], Dict[str, Any]]] = []
    sequential_calls: List[tuple[tuple[Any, ...], Dict[str, Any]]] = []

    def fake_parallel(*args, **kwargs):
        parallel_calls.append((args, kwargs))
        return {"successful": [], "failed": [], "unsupported": [], "bundles": {}}

    def fake_sequential(*args, **kwargs):
        sequential_calls.append((args, kwargs))
        return {"successful": [], "failed": [], "unsupported": [], "bundles": {}}

    monkeypatch.setattr("app.parallel_collector.run_parallel_scoped_collection", fake_parallel)
    monkeypatch.setattr("app.cli.run_recursive_collection", fake_sequential)
    monkeypatch.setattr("app.cli.write_bundle", lambda bundle, output_dir: tmp_path / bundle.device_name)
    monkeypatch.setattr("app.cli.load_default_credentials", lambda config_path: {})

    bundle_summary: Dict[str, Any] = {"devices": []}
    _run_recursive_cli(
        seed,
        "fake.yaml",
        tmp_path,
        bundle_summary,
        lambda _msg: None,
        checkpoint_file=None,
        dry_run=False,
        target_device=None,
    )

    assert len(sequential_calls) == 1
    assert parallel_calls == []


def test_deterministic_manifest_ordering(monkeypatch):
    """Bundle order is sorted by device name regardless of completion order."""
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    neighbor_map = {
        "SW01": [
            {"neighbor": "C", "ip": "10.0.0.12", "platform": "cisco WS-C2960-24TC-L"},
            {"neighbor": "A", "ip": "10.0.0.10", "platform": "cisco WS-C2960-24TC-L"},
            {"neighbor": "B", "ip": "10.0.0.11", "platform": "cisco WS-C2960-24TC-L"},
        ],
        "A": [],
        "B": [],
        "C": [],
    }
    delays = {"A": 0.12, "B": 0.06, "C": 0.01, "SW01": 0.0}

    async def fake_collect(device: Device) -> DeviceBundle:
        await asyncio.sleep(delays.get(device.name, 0.0))
        return _make_bundle(device.name, device.vendor, "collected", neighbor_map.get(device.name, []))

    monkeypatch.setattr("app.parallel_collector._collect_device", fake_collect)

    result = run_parallel_scoped_collection(
        seed,
        allowed_devices={"SW01", "A", "B", "C"},
        max_concurrent=3,
    )

    assert list(result["bundles"].keys()) == ["A", "B", "C", "SW01"]
    assert result["successful"] == ["SW01", "A", "B", "C"]


def test_checkpoint_behaviour_unchanged(monkeypatch):
    """Resumed pending entries are still filtered by allowed_devices and checkpoint keys are unchanged."""
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")

    async def fake_collect(device: Device) -> DeviceBundle:
        return _make_bundle(device.name, device.vendor, "collected", [])

    monkeypatch.setattr("app.parallel_collector._collect_device", fake_collect)

    resume_state = {
        "visited": [],
        "pending": ["SW02", "SW03"],
        "successful": [],
        "failed": [],
        "unsupported": [],
    }
    emitted: List[Dict[str, Any]] = []

    result = run_parallel_scoped_collection(
        seed,
        resume_state=resume_state,
        allowed_devices={"SW01", "SW02"},
        max_concurrent=2,
        on_collected=emitted.append,
    )

    assert set(result["successful"]) == {"SW01", "SW02"}
    assert "SW03" not in result["bundles"]
    for state in emitted:
        assert "SW03" not in state["pending"]
        assert sorted(state.keys()) == ["failed", "pending", "successful", "unsupported", "visited"]


def test_max_concurrent_limits_simultaneous_sessions(monkeypatch):
    """The semaphore bounds the number of in-flight collection tasks."""
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    neighbor_map = {
        "SW01": [
            {"neighbor": "SW02", "ip": "10.0.0.2", "platform": "cisco WS-C2960-24TC-L"},
            {"neighbor": "SW03", "ip": "10.0.0.3", "platform": "cisco WS-C2960-24TC-L"},
        ],
        "SW02": [],
        "SW03": [],
    }
    active = 0
    max_active = 0

    async def fake_collect(device: Device) -> DeviceBundle:
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        await asyncio.sleep(0.05)
        active -= 1
        return _make_bundle(device.name, device.vendor, "collected", neighbor_map.get(device.name, []))

    monkeypatch.setattr("app.parallel_collector._collect_device", fake_collect)

    run_parallel_scoped_collection(
        seed,
        allowed_devices={"SW01", "SW02", "SW03"},
        max_concurrent=1,
    )

    assert max_active == 1


@pytest.mark.parametrize("max_concurrent", [0, -1, -5])
def test_non_positive_max_concurrent_normalized(monkeypatch, max_concurrent):
    """Non-positive max_concurrent is normalized to 1 so collection does not hang."""
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    active = 0
    max_active = 0

    async def fake_collect(device: Device) -> DeviceBundle:
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        await asyncio.sleep(0.01)
        active -= 1
        return _make_bundle(device.name, device.vendor, "collected", [])

    monkeypatch.setattr("app.parallel_collector._collect_device", fake_collect)

    result = run_parallel_scoped_collection(
        seed,
        allowed_devices={"SW01"},
        max_concurrent=max_concurrent,
    )

    assert result["successful"] == ["SW01"]
    assert max_active == 1


def test_wave_respects_max_devices_capacity(monkeypatch):
    """A final wave cannot exceed the remaining max_devices allowance."""
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    neighbor_map = {
        "SW01": [
            {"neighbor": "SW02", "ip": "10.0.0.2", "platform": "cisco WS-C2960-24TC-L"},
            {"neighbor": "SW03", "ip": "10.0.0.3", "platform": "cisco WS-C2960-24TC-L"},
            {"neighbor": "SW04", "ip": "10.0.0.4", "platform": "cisco WS-C2960-24TC-L"},
        ],
        "SW02": [],
        "SW03": [],
        "SW04": [],
    }

    async def fake_collect(device: Device) -> DeviceBundle:
        return _make_bundle(device.name, device.vendor, "collected", neighbor_map.get(device.name, []))

    monkeypatch.setattr("app.parallel_collector._collect_device", fake_collect)

    result = run_parallel_scoped_collection(
        seed,
        allowed_devices={"SW01", "SW02", "SW03", "SW04"},
        max_concurrent=5,
        max_devices=2,
    )

    assert len(result["bundles"]) == 2
    assert "SW01" in result["bundles"]
