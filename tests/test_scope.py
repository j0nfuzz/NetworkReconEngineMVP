from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from app.scope import build_troubleshooting_scope


@pytest.mark.parametrize(
    "target,expected",
    [
        ("SW01", ["SW01", "SW02"]),
        ("SW02", ["FW01", "SW01", "SW02"]),
        ("FW01", ["FW01", "SW02"]),
    ],
)
def test_build_troubleshooting_scope_includes_direct_neighbours(target, expected):
    topology = {
        "nodes": {
            "SW01": {"neighbors": ["SW02"]},
            "SW02": {"neighbors": ["SW01", "FW01"]},
            "FW01": {"neighbors": ["SW02"]},
        },
        "edges": [],
    }
    assert build_troubleshooting_scope(topology, target) == expected


def test_build_troubleshooting_scope_unknown_target_returns_target_only():
    topology = {
        "nodes": {"SW01": {"neighbors": ["SW02"]}},
        "edges": [],
    }
    assert build_troubleshooting_scope(topology, "MISSING") == ["MISSING"]


def test_build_troubleshooting_scope_no_neighbours_returns_target_only():
    topology = {
        "nodes": {"SW01": {"neighbors": []}},
        "edges": [],
    }
    assert build_troubleshooting_scope(topology, "SW01") == ["SW01"]


def test_build_troubleshooting_scope_ordering_is_deterministic():
    topology = {
        "nodes": {
            "SW01": {"neighbors": ["AP02", "AP01", "SW03"]},
        },
        "edges": [],
    }
    assert build_troubleshooting_scope(topology, "SW01") == ["AP01", "AP02", "SW01", "SW03"]


def test_build_troubleshooting_scope_ignores_empty_neighbor_names():
    topology = {
        "nodes": {"SW01": {"neighbors": ["", "SW02", ""]}},
        "edges": [],
    }
    assert build_troubleshooting_scope(topology, "SW01") == ["SW01", "SW02"]


def test_cli_target_device_limits_recursive_collection(tmp_path, monkeypatch):
    config = tmp_path / "devices.yml"
    config.write_text(
        "devices:\n"
        "  - name: SW01\n"
        "    hostname: 192.168.2.1\n"
        "    vendor: cisco\n"
        "    username: u\n"
        "    password: <PASSWORD-06>\n"
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    topology = {
        "nodes": {
            "SW01": {"neighbors": ["SW02", "SW03"]},
            "SW02": {"neighbors": []},
            "SW03": {"neighbors": []},
        },
        "edges": [],
    }
    (output_dir / "topology.json").write_text(json.dumps(topology), encoding="utf-8")

    collected: list[str] = []

    def fake_run_parallel_scoped_collection(seed_device, *, allowed_devices=None, **kwargs):
        collected.append((seed_device.name, allowed_devices))
        return {
            "successful": [],
            "failed": [],
            "unsupported": [],
            "bundles": {},
        }

    monkeypatch.setattr("app.parallel_collector.run_parallel_scoped_collection", fake_run_parallel_scoped_collection)
    monkeypatch.setattr("app.cli.run_recursive_collection", lambda *args, **kwargs: None)
    monkeypatch.setattr("app.cli.load_default_credentials", lambda _path: {})

    from app.cli import main

    with patch.object(sys, "argv", [
        "cli.py",
        "--config", str(config),
        "--output-dir", str(output_dir),
        "--recursive",
        "--target-device", "SW01",
    ]):
        main()

    assert len(collected) == 1
    seed_name, allowed = collected[0]
    assert seed_name == "SW01"
    assert allowed == {"SW01", "SW02", "SW03"}


def test_cli_without_target_device_allows_full_collection(tmp_path, monkeypatch):
    config = tmp_path / "devices.yml"
    config.write_text(
        "devices:\n"
        "  - name: SW01\n"
        "    hostname: 192.168.2.1\n"
        "    vendor: cisco\n"
        "    username: u\n"
        "    password: <PASSWORD-06>\n"
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    collected: list[str] = []

    def fake_run_recursive_collection(seed_device, *, allowed_devices=None, **kwargs):
        collected.append((seed_device.name, allowed_devices))
        return {
            "successful": [],
            "failed": [],
            "unsupported": [],
            "bundles": {},
        }

    monkeypatch.setattr("app.cli.run_recursive_collection", fake_run_recursive_collection)
    monkeypatch.setattr("app.cli.load_default_credentials", lambda _path: {})

    from app.cli import main

    with patch.object(sys, "argv", [
        "cli.py",
        "--config", str(config),
        "--output-dir", str(output_dir),
        "--recursive",
    ]):
        main()

    assert len(collected) == 1
    _, allowed = collected[0]
    assert allowed is None


def test_cli_target_device_without_topology_uses_target_only(tmp_path, monkeypatch):
    config = tmp_path / "devices.yml"
    config.write_text(
        "devices:\n"
        "  - name: SW01\n"
        "    hostname: 192.168.2.1\n"
        "    vendor: cisco\n"
        "    username: u\n"
        "    password: <PASSWORD-06>\n"
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    collected: list[str] = []

    def fake_run_parallel_scoped_collection(seed_device, *, allowed_devices=None, **kwargs):
        collected.append((seed_device.name, allowed_devices))
        return {
            "successful": [],
            "failed": [],
            "unsupported": [],
            "bundles": {},
        }

    monkeypatch.setattr("app.parallel_collector.run_parallel_scoped_collection", fake_run_parallel_scoped_collection)
    monkeypatch.setattr("app.cli.run_recursive_collection", lambda *args, **kwargs: None)
    monkeypatch.setattr("app.cli.load_default_credentials", lambda _path: {})

    from app.cli import main

    with patch.object(sys, "argv", [
        "cli.py",
        "--config", str(config),
        "--output-dir", str(output_dir),
        "--recursive",
        "--target-device", "SW01",
    ]):
        main()

    _, allowed = collected[0]
    assert allowed == {"SW01"}


def test_cli_target_device_selects_non_first_seed(tmp_path, monkeypatch):
    config = tmp_path / "devices.yml"
    config.write_text(
        "devices:\n"
        "  - name: SW01\n"
        "    hostname: 192.168.2.1\n"
        "    vendor: cisco\n"
        "    username: u\n"
        "    password: <PASSWORD-06>\n"
        "  - name: SW02\n"
        "    hostname: 192.168.2.2\n"
        "    vendor: cisco\n"
        "    username: u\n"
        "    password: <PASSWORD-06>\n"
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    collected: list[str] = []

    def fake_run_parallel_scoped_collection(seed_device, *, allowed_devices=None, **kwargs):
        collected.append((seed_device.name, allowed_devices))
        return {
            "successful": [],
            "failed": [],
            "unsupported": [],
            "bundles": {},
        }

    monkeypatch.setattr("app.parallel_collector.run_parallel_scoped_collection", fake_run_parallel_scoped_collection)
    monkeypatch.setattr("app.cli.run_recursive_collection", lambda *args, **kwargs: None)
    monkeypatch.setattr("app.cli.load_default_credentials", lambda _path: {})

    from app.cli import main

    with patch.object(sys, "argv", [
        "cli.py",
        "--config", str(config),
        "--output-dir", str(output_dir),
        "--recursive",
        "--target-device", "SW02",
    ]):
        main()

    assert len(collected) == 1
    seed_name, allowed = collected[0]
    assert seed_name == "SW02"
    assert allowed == {"SW02"}


def test_cli_unknown_target_device_exits_before_collection(tmp_path, monkeypatch):
    config = tmp_path / "devices.yml"
    config.write_text(
        "devices:\n"
        "  - name: SW01\n"
        "    hostname: 192.168.2.1\n"
        "    vendor: cisco\n"
        "    username: u\n"
        "    password: <PASSWORD-06>\n"
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    called = {"seed": None}

    def fake_run_recursive_collection(seed_device, *, allowed_devices=None, **kwargs):
        called["seed"] = seed_device.name
        return {
            "successful": [],
            "failed": [],
            "unsupported": [],
            "bundles": {},
        }

    monkeypatch.setattr("app.cli.run_recursive_collection", fake_run_recursive_collection)
    monkeypatch.setattr("app.cli.load_default_credentials", lambda _path: {})

    from app.cli import main

    with patch.object(sys, "argv", [
        "cli.py",
        "--config", str(config),
        "--output-dir", str(output_dir),
        "--recursive",
        "--target-device", "MISSING",
    ]):
        assert main() == 1
    assert called["seed"] is None
