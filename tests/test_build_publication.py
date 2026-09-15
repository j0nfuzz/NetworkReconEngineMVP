"""Release builds must not package private data from removed diff lines."""
import subprocess
import zipfile

import pytest

import build_portable


@pytest.mark.parametrize("status", [" M README.md\n", "?? private-notes.txt\n"])
def test_dirty_release_is_rejected_before_build(monkeypatch, status):
    monkeypatch.setattr("sys.argv", ["build_portable.py"])
    monkeypatch.setattr(build_portable.subprocess, "run", lambda *a, **kw:
                        subprocess.CompletedProcess(a, 0, status, ""))
    monkeypatch.setattr(build_portable, "_build_embedded", lambda *a, **kw:
                        pytest.fail("Dirty source must not reach package staging"))
    assert build_portable.main() == 1


def test_missing_git_repository_is_rejected(monkeypatch):
    monkeypatch.setattr("sys.argv", ["build_portable.py", "--pyinstaller"])
    monkeypatch.setattr(build_portable.subprocess, "run", lambda *a, **kw:
                        subprocess.CompletedProcess(a, 128, "", "not a repository"))
    monkeypatch.setattr(build_portable, "_build_pyinstaller", lambda *a, **kw:
                        pytest.fail("Unverified source must not reach package staging"))
    assert build_portable.main() == 1


def test_clean_release_preserves_legacy_selection(monkeypatch):
    monkeypatch.setattr("sys.argv", ["build_portable.py", "--legacy"])
    monkeypatch.setattr(build_portable.subprocess, "run", lambda *a, **kw:
                        subprocess.CompletedProcess(a, 0, "", ""))
    selected = []
    monkeypatch.setattr(build_portable, "_build_embedded", lambda *a, **kw:
                        selected.append(kw["legacy"]) or 0)
    assert build_portable.main() == 0
    assert selected == [True]


def test_bundle_excludes_build_paths_in_caches_and_installer_launchers(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    (repo / "app" / "__pycache__").mkdir(parents=True)
    (repo / "app" / "__init__.py").write_text("")
    (repo / "app" / "__pycache__" / "old.pyc").write_bytes(b"private build path")
    (repo / "config").mkdir()
    (repo / "config" / "devices.yml.example").write_text("devices: []")
    (repo / "run_portable.py").write_text("print('ok')")
    (repo / "requirements.txt").write_text("")

    def download(url, destination):
        destination.parent.mkdir(parents=True, exist_ok=True)
        if str(destination).endswith(".zip"):
            with zipfile.ZipFile(destination, "w") as archive:
                archive.writestr("python.exe", b"test runtime")
                archive.writestr("python312._pth", "python312.zip\n.\n#import site\n")
                archive.writestr("Scripts/pip.exe", b"private interpreter path")
                archive.writestr("Lib/__pycache__/pip.pyc", b"private source path")
        else:
            destination.write_text("# Test installer")

    monkeypatch.setattr(build_portable, "_download", download)
    monkeypatch.setattr(build_portable, "capture_provenance", lambda:
                        {"head_commit_sha": "test", "dirty": "false", "patch": ""})
    monkeypatch.setattr(build_portable.subprocess, "run", lambda *a, **kw:
                        subprocess.CompletedProcess(a, 0))
    assert build_portable._build_embedded(repo, repo / "dist") == 0
    with zipfile.ZipFile(repo / "dist" / "NetworkReconEngine.zip") as archive:
        names = archive.namelist()
        assert "app/__init__.py" in names
        assert "config/devices.yml.example" in names
        assert "python/python.exe" in names
        assert not any("__pycache__" in name or name.startswith("python/Scripts/") for name in names)
