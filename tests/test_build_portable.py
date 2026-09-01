from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

import build_portable


@pytest.fixture(autouse=True)
def _reset_sys_argv():
    original = sys.argv[:]
    yield
    sys.argv[:] = original


def test_main_defaults_to_embedded_modern_profile(monkeypatch, tmp_path):
    calls = []

    def fake_build_embedded(repo_root, dist_dir, *, legacy=False):
        calls.append(("embedded", legacy, dist_dir))
        return 0

    def fake_build_pyinstaller(repo_root, dist_dir):
        calls.append(("pyinstaller", dist_dir))
        return 0

    monkeypatch.setattr(build_portable, "_build_embedded", fake_build_embedded)
    monkeypatch.setattr(build_portable, "_build_pyinstaller", fake_build_pyinstaller)

    sys.argv = ["build_portable"]
    assert build_portable.main() == 0
    assert calls == [("embedded", False, Path(__file__).resolve().parent.parent / "dist")]


def test_main_legacy_flag_selects_legacy_requirements(monkeypatch, tmp_path):
    calls = []

    def fake_build_embedded(repo_root, dist_dir, *, legacy=False):
        calls.append(("embedded", legacy, dist_dir))
        return 0

    monkeypatch.setattr(build_portable, "_build_embedded", fake_build_embedded)
    monkeypatch.setattr(build_portable, "_build_pyinstaller", lambda r, d: 0)

    sys.argv = ["build_portable", "--legacy"]
    assert build_portable.main() == 0
    assert calls == [("embedded", True, Path(__file__).resolve().parent.parent / "dist")]


def test_main_pyinstaller_and_legacy_are_mutually_exclusive(monkeypatch):
    monkeypatch.setattr(build_portable, "_build_embedded", lambda r, d, *, legacy=False: 0)
    monkeypatch.setattr(build_portable, "_build_pyinstaller", lambda r, d: 0)

    sys.argv = ["build_portable", "--pyinstaller", "--legacy"]
    with pytest.raises(SystemExit):
        build_portable.main()
