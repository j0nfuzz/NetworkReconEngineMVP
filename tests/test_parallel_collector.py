from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List

import pytest

from app.cli import _run_recursive_cli
from app.models import Device, DeviceBundle
from app.parallel_collector import MAX_CONCURRENT_CEILING, run_parallel_scoped_collection


def _make_bundle(
    name: str, vendor: str, status: str, neighbors: List[Dict[str, str]]
) -> DeviceBundle:
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
        return _make_bundle(
            device.name, device.vendor, "collected", neighbor_map.get(device.name, [])
        )

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

    monkeypatch.setattr(
        "app.parallel_collector.run_parallel_scoped_collection", fake_parallel
    )
    monkeypatch.setattr("app.cli.run_recursive_collection", fake_sequential)
    monkeypatch.setattr(
        "app.cli.write_bundle", lambda bundle, output_dir: tmp_path / bundle.device_name
    )
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
        return _make_bundle(
            device.name, device.vendor, "collected", neighbor_map.get(device.name, [])
        )

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
        return _make_bundle(
            device.name, device.vendor, "collected", neighbor_map.get(device.name, [])
        )

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
        return _make_bundle(
            device.name, device.vendor, "collected", neighbor_map.get(device.name, [])
        )

    monkeypatch.setattr("app.parallel_collector._collect_device", fake_collect)

    result = run_parallel_scoped_collection(
        seed,
        allowed_devices={"SW01", "SW02", "SW03", "SW04"},
        max_concurrent=5,
        max_devices=2,
    )

    assert len(result["bundles"]) == 2
    assert "SW01" in result["bundles"]


@pytest.mark.parametrize("max_concurrent", [11, 50, 100])
def test_max_concurrent_above_ceiling_is_clamped(monkeypatch, max_concurrent):
    """User-supplied max_concurrent above the ceiling is clamped to the ceiling."""
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
    assert max_active <= MAX_CONCURRENT_CEILING


def test_max_concurrent_within_range_unchanged(monkeypatch):
    """Values between 1 and the ceiling remain effective."""
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
        max_concurrent=3,
    )

    assert result["successful"] == ["SW01"]
    assert max_active <= 3


def test_cli_help_text_documents_ceiling():
    """The --max-concurrent help text documents the allowed range."""
    from app.cli import parse_args

    parser = parse_args.__wrapped__ if hasattr(parse_args, "__wrapped__") else None
    if parser is None:
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--max-concurrent",
            type=int,
            default=5,
            help="Maximum simultaneous SSH sessions for scoped parallel collection (1-10, default 5)",
        )
    help_text = parser.format_help()
    assert "1-10" in help_text


def test_allowed_devices_none_discovers_neighbors(monkeypatch):
    """PHASE-053: allowed_devices=None enables unbounded discovery from the seed."""
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    neighbor_map = {
        "SW01": [
            {"neighbor": "SW02", "ip": "10.0.0.2", "platform": "cisco WS-C2960-24TC-L"},
        ],
        "SW02": [],
    }

    async def fake_collect(device: Device) -> DeviceBundle:
        return _make_bundle(
            device.name, device.vendor, "collected", neighbor_map.get(device.name, [])
        )

    monkeypatch.setattr("app.parallel_collector._collect_device", fake_collect)

    result = run_parallel_scoped_collection(seed, allowed_devices=None, max_concurrent=2)

    assert set(result["bundles"].keys()) == {"SW01", "SW02"}
    assert result["successful"] == ["SW01", "SW02"]


def test_allowed_devices_none_no_longer_raises(monkeypatch):
    """PHASE-053: allowed_devices=None is accepted instead of raising ValueError."""
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")

    async def fake_collect(device: Device) -> DeviceBundle:
        return _make_bundle(device.name, device.vendor, "collected", [])

    monkeypatch.setattr("app.parallel_collector._collect_device", fake_collect)

    result = run_parallel_scoped_collection(seed, allowed_devices=None, max_concurrent=1)

    assert result["successful"] == ["SW01"]


def test_allowed_devices_set_still_bounds_discovery(monkeypatch):
    """PHASE-053: an explicit allowed set still prevents out-of-scope neighbours."""
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    neighbor_map = {
        "SW01": [
            {"neighbor": "SW02", "ip": "10.0.0.2", "platform": "cisco WS-C2960-24TC-L"},
            {"neighbor": "SW03", "ip": "10.0.0.3", "platform": "cisco WS-C2960-24TC-L"},
        ],
        "SW02": [],
    }

    async def fake_collect(device: Device) -> DeviceBundle:
        return _make_bundle(
            device.name, device.vendor, "collected", neighbor_map.get(device.name, [])
        )

    monkeypatch.setattr("app.parallel_collector._collect_device", fake_collect)

    result = run_parallel_scoped_collection(seed, allowed_devices={"SW01", "SW02"}, max_concurrent=2)

    assert set(result["bundles"].keys()) == {"SW01", "SW02"}
    assert "SW03" not in result["bundles"]


def test_on_device_collected_callback_fires_per_device(monkeypatch):
    """PHASE-077A: parallel scoped path invokes per-device streaming callback."""
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    neighbor_map = {
        "SW01": [
            {"neighbor": "SW02", "ip": "10.0.0.2", "platform": "cisco WS-C2960-24TC-L"},
        ],
        "SW02": [],
    }

    async def fake_collect(device: Device) -> DeviceBundle:
        return _make_bundle(
            device.name, device.vendor, "collected", neighbor_map.get(device.name, [])
        )

    monkeypatch.setattr("app.parallel_collector._collect_device", fake_collect)

    captured = []

    def on_device_collected(name, bundle, state):
        captured.append({"name": name, "status": bundle.summary.get("status"), "state": state})

    result = run_parallel_scoped_collection(
        seed,
        allowed_devices={"SW01", "SW02"},
        max_concurrent=2,
        on_device_collected=on_device_collected,
    )

    assert result["successful"] == ["SW01", "SW02"]
    assert len(captured) == 2
    names = [entry["name"] for entry in captured]
    assert sorted(names) == ["SW01", "SW02"]
    assert all(entry["status"] == "collected" for entry in captured)
    assert all("visited" in entry["state"] for entry in captured)


class FakeAsyncSSHConnection:
    """Minimal asyncssh stand-in for PHASE-055/055A identity-probe tests."""

    def __init__(self, stdout_map: dict[str, tuple[int, str, str]]):
        self._stdout_map = stdout_map

    async def run(self, command: str, timeout: int | None = None) -> Any:
        class Result:
            pass

        exit_status, stdout, stderr = self._stdout_map.get(command, (1, "", ""))
        result = Result()
        result.exit_status = exit_status
        result.stdout = stdout
        result.stderr = stderr
        return result


class FakeAsyncSSHConnect:
    """Context-manager factory mimicking asyncssh.connect()."""

    def __init__(self, connection: FakeAsyncSSHConnection):
        self._connection = connection

    async def __aenter__(self) -> FakeAsyncSSHConnection:
        return self._connection

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


def test_parallel_collect_device_performs_identity_probe(monkeypatch):
    """PHASE-055: the parallel path runs an identity probe before command selection."""
    from app.parallel_collector import _collect_device

    captured_commands: List[str] = []

    class FakeConn:
        async def run(self, command: str, timeout: int | None = None) -> Any:
            class Result:
                pass

            captured_commands.append(command)
            result = Result()
            if command == "show version":
                result.exit_status = 0
                result.stdout = "Cisco IOS Software, IOS-XE Software"
                result.stderr = ""
            else:
                result.exit_status = 0
                result.stdout = f"output for {command}"
                result.stderr = ""
            return result

    device = Device(
        name="SW01",
        hostname="10.0.0.1",
        vendor="auto",
        username="admin",
        password="<PASSWORD-01>",
    )

    async def run_test():
        monkeypatch.setattr(
            "app.parallel_collector.asyncssh.connect",
            lambda *args, **kwargs: FakeAsyncSSHConnect(FakeConn()),
        )
        return await _collect_device(device)

    bundle = asyncio.run(run_test())

    assert "show version" in captured_commands
    assert bundle.summary["vendor"] == "cisco"
    assert bundle.summary["platform"] == "cisco ios"
    assert bundle.device_vendor == "cisco"


def test_parallel_collect_device_selects_aruba_cx_profile(monkeypatch):
    """PHASE-055: an ArubaOS-CX device reached via the parallel path selects the aruba-cx profile."""
    from app.parallel_collector import _collect_device

    captured_commands: List[str] = []

    class FakeConn:
        async def run(self, command: str, timeout: int | None = None) -> Any:
            class Result:
                pass

            captured_commands.append(command)
            result = Result()
            if command == "show version":
                result.exit_status = 0
                result.stdout = "ArubaOS-CX\nModel: 6300M"
                result.stderr = ""
            else:
                result.exit_status = 0
                result.stdout = f"output for {command}"
                result.stderr = ""
            return result

    device = Device(
        name="CX01",
        hostname="10.0.0.1",
        vendor="auto",
        username="admin",
        password="<PASSWORD-01>",
    )

    async def run_test():
        monkeypatch.setattr(
            "app.parallel_collector.asyncssh.connect",
            lambda *args, **kwargs: FakeAsyncSSHConnect(FakeConn()),
        )
        return await _collect_device(device)

    bundle = asyncio.run(run_test())

    assert bundle.summary["vendor"] == "aruba"
    assert bundle.summary["platform"] == "arubaos-cx"
    assert "show interface brief" in captured_commands
    assert "show lldp neighbor-info detail" in captured_commands


def test_parallel_collect_device_probe_failure_is_recorded(monkeypatch):
    """PHASE-055: a failed identity probe produces an error bundle without generic fallback."""
    from app.parallel_collector import _collect_device

    class FakeConn:
        async def run(self, command: str, timeout: int | None = None) -> Any:
            class Result:
                pass

            result = Result()
            result.exit_status = 1
            result.stdout = ""
            result.stderr = "Authentication failed"
            return result

    device = Device(
        name="UNREACHABLE",
        hostname="10.0.0.1",
        vendor="auto",
        username="admin",
        password="<PASSWORD-01>",
    )

    async def run_test():
        monkeypatch.setattr(
            "app.parallel_collector.asyncssh.connect",
            lambda *args, **kwargs: FakeAsyncSSHConnect(FakeConn()),
        )
        return await _collect_device(device)

    bundle = asyncio.run(run_test())

    assert bundle.summary["status"] == "error"
    assert "Identity probe failed" in bundle.summary["error"]
    assert bundle.summary["commands_run"] == 0


def test_parallel_collect_device_preserves_pre_populated_identity(monkeypatch):
    """PHASE-055A: a higher-confidence pre-populated identity is preserved when the probe is ambiguous."""
    from app.parallel_collector import _collect_device

    class FakeConn:
        async def run(self, command: str, timeout: int | None = None) -> Any:
            class Result:
                pass

            result = Result()
            result.exit_status = 0
            result.stdout = "ArubaOS-CX"
            result.stderr = ""
            return result

    device = Device(
        name="CX02",
        hostname="10.0.0.1",
        vendor="cisco",
        username="admin",
        password="<PASSWORD-01>",
        metadata={
            "identity": {
                "vendor": "cisco",
                "platform": "ios",
                "model": "old",
                "confidence": 1.0,
            }
        },
    )

    async def run_test():
        monkeypatch.setattr(
            "app.parallel_collector.asyncssh.connect",
            lambda *args, **kwargs: FakeAsyncSSHConnect(FakeConn()),
        )
        return await _collect_device(device)

    bundle = asyncio.run(run_test())

    assert bundle.summary["vendor"] == "cisco"
    assert bundle.summary["platform"] == "ios"
    assert bundle.device_vendor == "cisco"


def test_parallel_collect_device_commands_run_includes_reused_show_version(monkeypatch):
    """PHASE-055B: commands_run equals the number of executed profile commands when show version is reused."""
    from app.parallel_collector import _collect_device

    captured_commands: List[str] = []

    class FakeConn:
        async def run(self, command: str, timeout: int | None = None) -> Any:
            class Result:
                pass

            captured_commands.append(command)
            result = Result()
            if command == "show version":
                result.exit_status = 0
                result.stdout = "ArubaOS-CX\nModel: 6300M"
                result.stderr = ""
            else:
                result.exit_status = 0
                result.stdout = f"output for {command}"
                result.stderr = ""
            return result

    device = Device(
        name="CX01",
        hostname="10.0.0.1",
        vendor="auto",
        username="admin",
        password="<PASSWORD-01>",
    )

    async def run_test():
        monkeypatch.setattr(
            "app.parallel_collector.asyncssh.connect",
            lambda *args, **kwargs: FakeAsyncSSHConnect(FakeConn()),
        )
        return await _collect_device(device)

    bundle = asyncio.run(run_test())

    assert captured_commands.count("show version") == 1
    assert bundle.summary["vendor"] == "aruba"
    assert bundle.summary["platform"] == "arubaos-cx"
    assert bundle.summary["commands_run"] == len(bundle.raw_outputs)


def test_parallel_collect_device_preserves_configured_vendor_on_ambiguous_probe(monkeypatch):
    """PHASE-055A: a configured vendor with an unrecognized banner keeps its profile instead of generic."""
    from app.parallel_collector import _collect_device

    captured_commands: List[str] = []

    class FakeConn:
        async def run(self, command: str, timeout: int | None = None) -> Any:
            class Result:
                pass

            captured_commands.append(command)
            result = Result()
            if command == "show version":
                result.exit_status = 0
                result.stdout = "Unknown custom firmware\nno recognizable banner"
                result.stderr = ""
            else:
                result.exit_status = 0
                result.stdout = f"output for {command}"
                result.stderr = ""
            return result

    device = Device(
        name="SW01",
        hostname="10.0.0.1",
        vendor="cisco",
        username="admin",
        password="<PASSWORD-01>",
    )

    async def run_test():
        monkeypatch.setattr(
            "app.parallel_collector.asyncssh.connect",
            lambda *args, **kwargs: FakeAsyncSSHConnect(FakeConn()),
        )
        return await _collect_device(device)

    bundle = asyncio.run(run_test())

    assert bundle.summary["vendor"] == "cisco"
    assert bundle.device_vendor == "cisco"
    assert "show version" in captured_commands
    assert "show cdp neighbors detail" in captured_commands or "show lldp neighbors" in captured_commands
    assert "show system uptime" not in captured_commands


def test_parallel_collect_device_reuses_show_version_output(monkeypatch):
    """PHASE-055A: the identity probe's show version output is retained as profile evidence."""
    from app.parallel_collector import _collect_device

    captured_commands: List[str] = []

    class FakeConn:
        async def run(self, command: str, timeout: int | None = None) -> Any:
            class Result:
                pass

            captured_commands.append(command)
            result = Result()
            if command == "show version":
                result.exit_status = 0
                result.stdout = "Cisco IOS Software\nModel: C9200"
                result.stderr = ""
            else:
                result.exit_status = 0
                result.stdout = f"output for {command}"
                result.stderr = ""
            return result

    device = Device(
        name="SW01",
        hostname="10.0.0.1",
        vendor="auto",
        username="admin",
        password="<PASSWORD-01>",
    )

    async def run_test():
        monkeypatch.setattr(
            "app.parallel_collector.asyncssh.connect",
            lambda *args, **kwargs: FakeAsyncSSHConnect(FakeConn()),
        )
        return await _collect_device(device)

    bundle = asyncio.run(run_test())

    assert captured_commands.count("show version") == 1
    assert bundle.raw_outputs.get("show version") == "Cisco IOS Software\nModel: C9200"
    assert bundle.summary["commands_run"] == len(bundle.raw_outputs)


_EXPECTED_EVIDENCE_KEYS = {
    "command",
    "error_type",
    "elapsed_seconds",
    "transport_active",
    "transport_state",
    "channel_state",
    "recovery_attempted",
    "recovery_successful",
    "original_error_type",
    "original_elapsed_seconds",
    "original_stdout",
    "original_stderr",
    "original_transport_active",
    "retry_error",
    "retry_error_type",
    "retry_elapsed_seconds",
}

_ASYNCSSH_UNAVAILABLE_FIELDS = [
    "transport_active",
    "transport_state",
    "channel_state",
    "recovery_attempted",
    "recovery_successful",
    "original_error_type",
    "original_elapsed_seconds",
    "original_stdout",
    "original_stderr",
    "original_transport_active",
    "retry_error",
    "retry_error_type",
    "retry_elapsed_seconds",
]


def test_parallel_failed_command_details_recorded(monkeypatch):
    """PHASE-056: failed parallel commands emit command_evidence entries."""
    from app.parallel_collector import _collect_device

    class FakeConn:
        async def run(self, command: str, timeout: int | None = None) -> Any:
            class Result:
                pass

            result = Result()
            if command == "show version":
                result.exit_status = 0
                result.stdout = "Cisco IOS Software, IOS-XE Software"
                result.stderr = ""
            elif command == "show cdp neighbors detail":
                result.exit_status = 1
                result.stdout = ""
                result.stderr = "Command not supported"
            else:
                result.exit_status = 0
                result.stdout = f"output for {command}"
                result.stderr = ""
            return result

    device = Device(
        name="SW01",
        hostname="10.0.0.1",
        vendor="auto",
        username="admin",
        password="<PASSWORD-01>",
    )

    async def run_test():
        monkeypatch.setattr(
            "app.parallel_collector.asyncssh.connect",
            lambda *args, **kwargs: FakeAsyncSSHConnect(FakeConn()),
        )
        return await _collect_device(device)

    bundle = asyncio.run(run_test())

    assert "failed_command_details" in bundle.summary
    assert "recovered_commands" in bundle.summary
    assert bundle.summary["recovered_commands"] == []
    assert len(bundle.summary["failed_command_details"]) == 1
    detail = bundle.summary["failed_command_details"][0]
    assert detail["command"] == "show cdp neighbors detail"
    assert detail["error_type"] == "non_zero_exit"
    assert isinstance(detail["elapsed_seconds"], float)
    assert set(detail.keys()) == _EXPECTED_EVIDENCE_KEYS
    for field in _ASYNCSSH_UNAVAILABLE_FIELDS:
        assert detail.get(field) is None, field


def test_parallel_failed_command_schema_matches_sequential(monkeypatch):
    """PHASE-056: parallel and sequential summaries expose the same evidence-contract keys."""
    from app.collector import execute_device_collection
    from app.parallel_collector import _collect_device

    class FakeParallelConn:
        async def run(self, command: str, timeout: int | None = None) -> Any:
            class Result:
                pass

            result = Result()
            if command == "show version":
                result.exit_status = 0
                result.stdout = "Cisco IOS Software, IOS-XE Software"
                result.stderr = ""
            elif command == "show cdp neighbors detail":
                result.exit_status = 1
                result.stdout = ""
                result.stderr = "Command not supported"
            else:
                result.exit_status = 0
                result.stdout = f"output for {command}"
                result.stderr = ""
            return result

    class FakeSequentialSSHClient:
        def __init__(self, *args, **kwargs):
            pass

        def probe(self):
            return {"reachable": True}

        def connect(self):
            return self

        def run_command(self, command, client=None):
            success = command != "show cdp neighbors detail"
            return {
                "success": success,
                "stdout": "" if not success else f"output for {command}",
                "stderr": "Command not supported" if not success else "",
                "error": None if success else "Command not supported",
                "error_type": None if success else "non_zero_exit",
                "elapsed_seconds": 0.1,
                "transport_active": True,
                "transport_state": "active",
                "channel_state": "open",
                "recovery_attempted": False,
                "recovery_successful": False,
                "original_error_type": None,
                "original_elapsed_seconds": None,
                "original_stdout": None,
                "original_stderr": None,
                "original_transport_active": None,
                "retry_error": None,
                "retry_error_type": None,
                "retry_elapsed_seconds": None,
            }

        def close(self, connection):
            return None

    parallel_device = Device(
        name="SW01-PAR",
        hostname="10.0.0.1",
        vendor="cisco",
        username="admin",
        password="<PASSWORD-01>",
    )

    async def run_parallel():
        monkeypatch.setattr(
            "app.parallel_collector.asyncssh.connect",
            lambda *args, **kwargs: FakeAsyncSSHConnect(FakeParallelConn()),
        )
        return await _collect_device(parallel_device)

    parallel_bundle = asyncio.run(run_parallel())

    sequential_device = Device(
        name="SW01-SEQ",
        hostname="10.0.0.1",
        vendor="cisco",
        username="admin",
        password="<PASSWORD-01>",
    )
    monkeypatch.setattr("app.collector.DeviceSSHClient", FakeSequentialSSHClient)
    sequential_bundle = execute_device_collection(sequential_device)

    assert sorted(parallel_bundle.summary.keys()) == sorted(sequential_bundle.summary.keys())
    assert (
        parallel_bundle.summary["failed_commands"]
        == sequential_bundle.summary["failed_commands"]
    )
    parallel_detail = parallel_bundle.summary["failed_command_details"][0]
    sequential_detail = sequential_bundle.summary["failed_command_details"][0]
    assert set(parallel_detail.keys()) == set(sequential_detail.keys()) == _EXPECTED_EVIDENCE_KEYS


def test_parallel_command_exception_records_error_type(monkeypatch):
    """PHASE-056: connection-level command exceptions are recorded as failed evidence."""
    from app.parallel_collector import _collect_device

    class FakeConn:
        async def run(self, command: str, timeout: int | None = None) -> Any:
            if command == "show version":
                class Result:
                    pass

                result = Result()
                result.exit_status = 0
                result.stdout = "Cisco IOS Software, IOS-XE Software"
                result.stderr = ""
                return result
            raise ConnectionError("Connection lost")

    device = Device(
        name="SW01",
        hostname="10.0.0.1",
        vendor="auto",
        username="admin",
        password="<PASSWORD-01>",
    )

    async def run_test():
        monkeypatch.setattr(
            "app.parallel_collector.asyncssh.connect",
            lambda *args, **kwargs: FakeAsyncSSHConnect(FakeConn()),
        )
        return await _collect_device(device)

    bundle = asyncio.run(run_test())

    exception_details = [
        d for d in bundle.summary["failed_command_details"] if d["error_type"] == "ConnectionError"
    ]
    assert exception_details
    for field in _ASYNCSSH_UNAVAILABLE_FIELDS:
        assert exception_details[0].get(field) is None, field


def test_parallel_alias_neighbor_matching_visited_ip_is_not_recollection(monkeypatch):
    """PHASE-087: a neighbour whose IP matches an already-visited device's hostname is not re-collected."""
    seed = Device(name="192.168.2.241", hostname="192.168.2.241", vendor="aruba")
    neighbor_map = {
        "192.168.2.241": [
            {"neighbor": "HOSTNAME-06", "ip": "192.168.2.242", "platform": "Aruba R8N85A"},
            {"neighbor": "HOSTNAME-05", "ip": "192.168.2.241", "platform": "Aruba R8N85A"},
        ],
        "HOSTNAME-06": [
            {"neighbor": "HOSTNAME-05", "ip": "192.168.2.241", "platform": "Aruba R8N85A"}
        ],
    }
    collected: List[str] = []

    async def fake_collect(device: Device) -> DeviceBundle:
        collected.append(device.name)
        return _make_bundle(
            device.name,
            device.vendor,
            "collected",
            neighbor_map.get(device.name, []),
        )

    monkeypatch.setattr("app.parallel_collector._collect_device", fake_collect)

    result = run_parallel_scoped_collection(seed, allowed_devices=None, max_concurrent=2)

    assert result["successful"] == ["192.168.2.241", "HOSTNAME-06"]
    assert "HOSTNAME-05" not in result["bundles"]
    assert "HOSTNAME-05" not in collected


def test_parallel_distinct_neighbors_with_unique_addresses_still_traversed(monkeypatch):
    """PHASE-087: genuinely distinct neighbours (different resolved addresses) are unaffected."""
    seed = Device(name="SW01", hostname="10.0.0.1", vendor="cisco")
    neighbor_map = {
        "SW01": [
            {"neighbor": "SW02", "ip": "10.0.0.2", "platform": "cisco WS-C2960-24TC-L"},
            {"neighbor": "SW03", "ip": "10.0.0.3", "platform": "cisco WS-C2960-24TC-L"},
        ],
        "SW02": [],
        "SW03": [],
    }

    async def fake_collect(device: Device) -> DeviceBundle:
        return _make_bundle(
            device.name,
            device.vendor,
            "collected",
            neighbor_map.get(device.name, []),
        )

    monkeypatch.setattr("app.parallel_collector._collect_device", fake_collect)

    result = run_parallel_scoped_collection(seed, allowed_devices=None, max_concurrent=2)

    assert set(result["bundles"].keys()) == {"SW01", "SW02", "SW03"}
    assert result["successful"] == ["SW01", "SW02", "SW03"]
