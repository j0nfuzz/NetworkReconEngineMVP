"""Tests for app.provenance build-state capture."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

import app.provenance as provenance_module
from app.provenance import (
    _load_runtime_provenance,
    capture_provenance,
    compute_checksum,
    get_head_commit_sha,
    is_working_tree_dirty,
    set_provenance_capture_enabled,
    write_provenance_artifact,
)


@pytest.fixture(autouse=True)
def enable_provenance_for_module(monkeypatch):
    """Provenance tests need capture enabled despite the global test disable env var."""
    monkeypatch.delenv("NRE_DISABLE_PROVENANCE", raising=False)
    set_provenance_capture_enabled(True)
    yield
    set_provenance_capture_enabled(False)


def test_get_head_commit_sha_returns_hex_string(monkeypatch):
    monkeypatch.setattr(provenance_module, "_run_git", lambda *args: "a1b2c3d4")
    assert get_head_commit_sha() == "a1b2c3d4"


def test_get_head_commit_sha_returns_unknown_when_git_missing(monkeypatch):
    monkeypatch.setattr(provenance_module, "_run_git", lambda *args: "")
    assert get_head_commit_sha() == "unknown"


def test_is_working_tree_dirty_true(monkeypatch):
    monkeypatch.setattr(provenance_module, "_run_git", lambda *args: " M app.py")
    assert is_working_tree_dirty() is True


def test_is_working_tree_dirty_false(monkeypatch):
    monkeypatch.setattr(provenance_module, "_run_git", lambda *args: "")
    assert is_working_tree_dirty() is False


def test_compute_checksum_is_sha256():
    assert (
        compute_checksum("hello")
        == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    )


def test_capture_provenance_clean_tree(monkeypatch):
    monkeypatch.setattr(provenance_module, "get_head_commit_sha", lambda: "abc123")
    monkeypatch.setattr(provenance_module, "is_working_tree_dirty", lambda: False)

    result = capture_provenance()

    assert result["head_commit_sha"] == "abc123"
    assert result["dirty"] == "false"
    assert result["patch"] == ""
    assert result["patch_checksum"] == ""
    assert result["excluded_paths"] == "config/*.yml"


def test_capture_provenance_dirty_tree(monkeypatch):
    monkeypatch.setattr(provenance_module, "get_head_commit_sha", lambda: "abc123")
    monkeypatch.setattr(provenance_module, "is_working_tree_dirty", lambda: True)
    monkeypatch.setattr(provenance_module, "get_unified_diff_patch", lambda excluded_paths: "diff --git a/app.py b/app.py\n+change")

    result = capture_provenance()

    assert result["head_commit_sha"] == "abc123"
    assert result["dirty"] == "true"
    assert result["patch"] == "diff --git a/app.py b/app.py\n+change"
    assert result["patch_checksum"] == compute_checksum(result["patch"])


def test_capture_provenance_excludes_config_yml_from_patch(monkeypatch):
    captured_kwargs = []

    def fake_diff(*args, **kwargs):
        captured_kwargs.append(kwargs)
        return ""

    monkeypatch.setattr(provenance_module, "get_head_commit_sha", lambda: "abc123")
    monkeypatch.setattr(provenance_module, "is_working_tree_dirty", lambda: True)
    monkeypatch.setattr(provenance_module, "get_unified_diff_patch", fake_diff)

    capture_provenance(excluded_paths=("config/*.yml", "secrets.env"))

    assert captured_kwargs[0]["excluded_paths"] == ("config/*.yml", "secrets.env")


def test_write_provenance_artifact_creates_json(tmp_path, monkeypatch):
    monkeypatch.setattr(provenance_module, "get_head_commit_sha", lambda: "def789")
    monkeypatch.setattr(provenance_module, "is_working_tree_dirty", lambda: True)
    monkeypatch.setattr(
        provenance_module,
        "get_unified_diff_patch",
        lambda excluded_paths: "diff --git a/x.py b/x.py\n+line",
    )

    device_dir = tmp_path / "device"
    device_dir.mkdir()
    artifact_path = write_provenance_artifact(device_dir)

    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["head_commit_sha"] == "def789"
    assert payload["dirty"] == "true"
    assert payload["patch"] == "diff --git a/x.py b/x.py\n+line"
    assert payload["patch_checksum"] == compute_checksum(payload["patch"])


def test_write_provenance_artifact_uses_provided_payload(tmp_path):
    provided = {
        "head_commit_sha": "000000",
        "dirty": "false",
        "patch": "",
        "patch_checksum": "",
        "excluded_paths": "config/*.yml",
    }
    artifact_path = write_provenance_artifact(tmp_path, provenance=provided)
    assert json.loads(artifact_path.read_text(encoding="utf-8")) == provided


def test_capture_provenance_falls_back_to_runtime_file_when_git_unavailable(
    monkeypatch, tmp_path
):
    """PHASE-076: portable deployments without .git use embedded build provenance."""
    monkeypatch.setattr(provenance_module, "_run_git", lambda *args: "")

    runtime_path = tmp_path / "build_runtime_provenance.json"
    runtime_path.write_text(
        json.dumps(
            {
                "head_commit_sha": "abc123def456",
                "dirty": "false",
                "patch": "",
                "patch_checksum": "",
                "excluded_paths": "config/*.yml",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(provenance_module, "RUNTIME_PROVENANCE_PATH", runtime_path)

    result = capture_provenance()
    assert result["head_commit_sha"] == "abc123def456"
    assert result["dirty"] == "false"


def test_runtime_provenance_resolves_to_bundle_root_in_portable_layout(
    monkeypatch, tmp_path
):
    """PHASE-076A: RUNTIME_PROVENANCE_PATH resolves to bundle root, not python/."""
    import types

    bundle_root = tmp_path / "NetworkReconEngine"
    python_dir = bundle_root / "python"
    python_dir.mkdir(parents=True)
    fake_exe = python_dir / "python.exe"
    fake_exe.write_text("", encoding="utf-8")

    runtime_file = bundle_root / "build_runtime_provenance.json"
    runtime_file.write_text(
        json.dumps(
            {
                "head_commit_sha": "bundlecommit123",
                "dirty": "false",
                "patch": "",
                "patch_checksum": "",
                "excluded_paths": "config/*.yml",
            }
        ),
        encoding="utf-8",
    )

    fake_sys = types.ModuleType("sys")
    fake_sys.modules = sys.modules
    fake_sys.executable = str(fake_exe)
    monkeypatch.setattr(provenance_module, "sys", fake_sys)
    monkeypatch.setattr(provenance_module, "_run_git", lambda *args: "")

    expected_path = Path(fake_sys.executable).parent.parent / "build_runtime_provenance.json"
    monkeypatch.setattr(provenance_module, "RUNTIME_PROVENANCE_PATH", expected_path)

    assert _load_runtime_provenance() == {
        "head_commit_sha": "bundlecommit123",
        "dirty": "false",
        "patch": "",
        "patch_checksum": "",
        "excluded_paths": "config/*.yml",
    }

    result = capture_provenance()
    assert result["head_commit_sha"] == "bundlecommit123"
    assert result["dirty"] == "false"
