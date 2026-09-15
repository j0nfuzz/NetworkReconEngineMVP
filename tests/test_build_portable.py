from __future__ import annotations

import json
import shutil
import sys
import zipfile
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
    monkeypatch.setattr(build_portable.subprocess, "run", lambda *a, **kw:
                        build_portable.subprocess.CompletedProcess(a, 0, stdout="", stderr=""))
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
    monkeypatch.setattr(build_portable.subprocess, "run", lambda *a, **kw:
                        build_portable.subprocess.CompletedProcess(a, 0, stdout="", stderr=""))
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


def test_embedded_build_excludes_local_config_and_includes_manifest(tmp_path):
    """Verify portable bundle hygiene and embedded build manifest."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    app_dir = repo_root / "app"
    app_dir.mkdir()
    (app_dir / "__init__.py").write_text("", encoding="utf-8")
    (app_dir / "provenance.py").write_text(
        'def capture_provenance():\n'
        '    return {\n'
        '        "head_commit_sha": "abc123",\n'
        '        "dirty": "true",\n'
        '        "patch_checksum": "deadbeef",\n'
        '        "excluded_paths": "config/*.yml",\n'
        '    }\n',
        encoding="utf-8",
    )

    config_dir = repo_root / "config"
    config_dir.mkdir()
    (config_dir / "devices.yml").write_text("<PASSWORD-01>", encoding="utf-8")
    (config_dir / "interactive_devices.yml").write_text("<PASSWORD-01>", encoding="utf-8")
    (config_dir / "devices.yml.example").write_text("example", encoding="utf-8")
    (repo_root / "run_portable.py").write_text("print('ok')", encoding="utf-8")
    (repo_root / "requirements.txt").write_text("paramiko", encoding="utf-8")

    build_dir = repo_root / "build" / "embedded"
    bundle_dir = build_dir / "NetworkReconEngine"
    fake_python_dir = bundle_dir / "python"
    fake_python_dir.mkdir(parents=True)
    (fake_python_dir / "python.exe").write_text("", encoding="utf-8")
    (fake_python_dir / "python312._pth").write_text("", encoding="utf-8")

    config_dst = bundle_dir / "config"
    config_dst.mkdir(parents=True)
    for item in config_dir.iterdir():
        if item.is_file() and item.suffix == ".example":
            shutil.copy2(item, config_dst / item.name)
        elif item.is_dir():
            shutil.copytree(item, config_dst / item.name)
    shutil.copy2(repo_root / "run_portable.py", bundle_dir / "run_portable.py")
    shutil.copy2(repo_root / "requirements.txt", bundle_dir / "requirements.txt")

    manifest = {
        "commit_sha": "abc123",
        "dirty": "true",
        "build_timestamp": "2026-09-05T00:00:00+00:00",
        "patch_checksum": "deadbeef",
        "excluded_paths": "config/*.yml",
    }
    (bundle_dir / "build_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    dist_dir = tmp_path / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dist_dir / "NetworkReconEngine.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in bundle_dir.rglob("*"):
            if item.is_file():
                zf.write(item, arcname=str(item.relative_to(bundle_dir)))

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        assert "config/devices.yml.example" in names
        assert "config/devices.yml" not in names
        assert "config/interactive_devices.yml" not in names
        assert "build_manifest.json" in names
        manifest_data = json.loads(zf.read("build_manifest.json").decode("utf-8"))
        assert manifest_data["commit_sha"] == "abc123"
        assert manifest_data["dirty"] == "true"
        assert manifest_data["patch_checksum"] == "deadbeef"


def _stage_minimal_repo(repo_root: Path) -> None:
    """Create a minimal source tree sufficient for build_portable._build_embedded."""
    app_dir = repo_root / "app"
    app_dir.mkdir(parents=True)
    (app_dir / "__init__.py").write_text("", encoding="utf-8")
    (app_dir / "provenance.py").write_text(
        'def capture_provenance():\n'
        '    return {"head_commit_sha": "abc123", "dirty": "false"}\n',
        encoding="utf-8",
    )
    config_dir = repo_root / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "devices.yml.example").write_text("example", encoding="utf-8")
    (repo_root / "run_portable.py").write_text("print('ok')", encoding="utf-8")
    (repo_root / "requirements.txt").write_text("paramiko", encoding="utf-8")


def _make_fake_embedded_python(python_dir: Path) -> None:
    """Create a fake embedded python layout that _build_embedded expects."""
    python_dir.mkdir(parents=True)
    (python_dir / "python.exe").write_text("", encoding="utf-8")
    (python_dir / "python312._pth").write_text(
        "python312.zip\n.\n#import site\n", encoding="utf-8"
    )


def test_embedded_build_generates_launchers_with_unbuffered_flags(tmp_path, monkeypatch):
    """PHASE-068B: launchers are generated by _build_embedded with correct unbuffered syntax."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _stage_minimal_repo(repo_root)

    dist_dir = repo_root / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    downloads_dir = repo_root / "build" / "downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)
    # Empty zip file bytes satisfy the mocked extractall and pth edit path.
    (downloads_dir / "python-embed.zip").write_bytes(
        b"PK\x05\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    )
    (downloads_dir / "get-pip.py").write_text("", encoding="utf-8")

    bundle_dir = repo_root / "build" / "embedded" / "NetworkReconEngine"
    _make_fake_embedded_python(bundle_dir / "python")

    monkeypatch.setattr(build_portable, "_download", lambda url, dest: None)
    monkeypatch.setattr("zipfile.ZipFile.extractall", lambda self, path: None)

    def fake_subprocess_run(*args, **kwargs):
        return type("R", (), {"returncode": 0, "stdout": ""})()

    monkeypatch.setattr("subprocess.run", fake_subprocess_run)

    assert build_portable._build_embedded(repo_root, dist_dir, legacy=False) == 0

    cmd = bundle_dir / "Start_NetworkRecon.cmd"
    ps1 = bundle_dir / "Start_NetworkRecon.ps1"
    assert cmd.exists()
    assert ps1.exists()

    cmd_script = cmd.read_text(encoding="utf-8")
    assert "set PYTHONUNBUFFERED=1" in cmd_script
    assert "python\\python.exe -u run_portable.py %*" in cmd_script

    ps1_script = ps1.read_text(encoding="utf-8")
    assert "$env:PYTHONUNBUFFERED = '1'" in ps1_script
    assert "& $pyExe -u $runPortable @args" in ps1_script
    # Reject the broken comma-separated-array syntax from PHASE-068.
    assert "'-u'," not in ps1_script
