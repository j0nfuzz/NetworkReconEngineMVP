# Build a self-contained Windows distribution for network device diagnostics.
#
# Default mode (recommended for managed endpoints):
#   Bundles the official CPython embeddable runtime, application source, and
#   dependencies into a ZIP. A launcher script invokes the bundled Python
#   interpreter directly, avoiding low-prevalence PyInstaller executables that
#   are blocked by Defender ASR Rule 01443614 on some enterprise endpoints.
#
# Legacy mode:
#   Builds the previous PyInstaller onedir executable. Pass --pyinstaller.
#
# Legacy embedded mode:
#   Bundles the embedded runtime with requirements-legacy.txt instead of
#   requirements.txt. Pass --legacy.
#
# Usage:
#   .\.venv\Scripts\python.exe -m build_portable
#   .\.venv\Scripts\python.exe -m build_portable --pyinstaller
#   .\.venv\Scripts\python.exe -m build_portable --legacy

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.provenance import capture_provenance


def _rmtree_ro(path: Path) -> None:
    """Remove a directory tree, including read-only files."""
    def on_rm_error(func, check_path, exc_info):  # type: ignore[no-untyped-def]
        os.chmod(check_path, stat.S_IWRITE)
        func(check_path)

    if path.exists():
        shutil.rmtree(path, onerror=on_rm_error)

PYTHON_VERSION = (3, 12, 10)
EMBED_URL = (
    "https://www.python.org/ftp/python/3.12.10/"
    "python-3.12.10-embed-amd64.zip"
)
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"


def _build_pyinstaller(repo_root: Path, dist_dir: Path) -> int:
    """Build the legacy PyInstaller onedir executable."""
    venv_python = repo_root / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        print("Virtual environment not found. Run the interactive bootstrap or setup first.")
        return 1

    build_dir = repo_root / "build" / "portable"
    _rmtree_ro(dist_dir)
    _rmtree_ro(build_dir)

    cmd = [
        str(venv_python),
        "-m",
        "PyInstaller",
        "--name",
        "NetworkDeviceDiagnostics",
        "--onedir",
        "--distpath",
        str(dist_dir),
        "--workpath",
        str(build_dir),
        "--specpath",
        str(repo_root),
        "--hidden-import",
        "asyncssh",
        "--hidden-import",
        "paramiko",
        "--hidden-import",
        "yaml",
        "--hidden-import",
        "rich",
        str(repo_root / "run_portable.py"),
    ]
    result = subprocess.run(cmd, cwd=repo_root, check=False)
    if result.returncode != 0:
        print("PyInstaller build failed.")
        return result.returncode

    executable = dist_dir / "NetworkDeviceDiagnostics" / "NetworkDeviceDiagnostics.exe"
    if not executable.exists():
        print(f"Executable not found at expected path: {executable}")
        return 1

    zip_path = dist_dir / "NetworkDeviceDiagnostics.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in (dist_dir / "NetworkDeviceDiagnostics").rglob("*"):
            arcname = item.relative_to(dist_dir / "NetworkDeviceDiagnostics")
            zf.write(item, arcname=str(arcname))

    print(f"Portable executable built: {executable}")
    print(f"Distributable package: {zip_path}")
    return 0


def _download(url: str, dest: Path) -> None:
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url} ...")
    urllib.request.urlretrieve(url, dest)


def _build_embedded(repo_root: Path, dist_dir: Path, *, legacy: bool = False) -> int:
    """Bundle the official CPython embeddable runtime with the application."""
    requirements_file = "requirements-legacy.txt" if legacy else "requirements.txt"
    build_dir = repo_root / "build" / "embedded"
    downloads_dir = repo_root / "build" / "downloads"
    bundle_dir = build_dir / "NetworkReconEngine"
    python_dir = bundle_dir / "python"

    _rmtree_ro(dist_dir)
    _rmtree_ro(build_dir)
    build_dir.mkdir(parents=True)

    # Capture build-time provenance before staging so the manifest reflects
    # the source tree used for this build even after files are copied.
    provenance = capture_provenance()

    embed_zip = downloads_dir / "python-embed.zip"
    get_pip = downloads_dir / "get-pip.py"
    _download(EMBED_URL, embed_zip)
    _download(GET_PIP_URL, get_pip)

    bundle_dir.mkdir(parents=True)
    python_dir.mkdir(parents=True)

    with zipfile.ZipFile(embed_zip, "r") as zf:
        zf.extractall(python_dir)

    # Enable site-packages in the embedded runtime.
    pth_file = python_dir / f"python{PYTHON_VERSION[0]}{PYTHON_VERSION[1]}._pth"
    if pth_file.exists():
        lines = pth_file.read_text(encoding="utf-8").splitlines()
        new_lines: list[str] = []
        found_site = False
        for line in lines:
            if line.strip() == "#import site":
                new_lines.append("import site")
                found_site = True
            else:
                new_lines.append(line)
        if not found_site:
            new_lines.append("import site")
        new_lines.append("Lib\\site-packages")
        pth_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    py_exe = python_dir / "python.exe"

    print("Installing pip into embedded runtime ...")
    result = subprocess.run(
        [str(py_exe), str(get_pip), "--no-warn-script-location"],
        cwd=repo_root,
        check=False,
    )
    if result.returncode != 0:
        print("Failed to install pip into embedded runtime.")
        return result.returncode

    print(f"Installing dependencies into embedded runtime from {requirements_file} ...")
    result = subprocess.run(
        [str(py_exe), "-m", "pip", "install", "--no-warn-script-location", "-r", requirements_file],
        cwd=repo_root,
        check=False,
    )
    if result.returncode != 0:
        print("Failed to install dependencies into embedded runtime.")
        return result.returncode

    # Stage application files.
    shutil.copytree(repo_root / "app", bundle_dir / "app")
    config_src = repo_root / "config"
    config_dst = bundle_dir / "config"
    config_dst.mkdir(parents=True)
    for item in config_src.iterdir():
        if item.is_file() and item.suffix == ".example":
            shutil.copy2(item, config_dst / item.name)
        elif item.is_dir():
            shutil.copytree(item, config_dst / item.name)
    shutil.copy2(repo_root / "run_portable.py", bundle_dir / "run_portable.py")
    shutil.copy2(repo_root / requirements_file, bundle_dir / requirements_file)
    if legacy:
        # Keep the modern manifest present for reference even in legacy bundles.
        shutil.copy2(repo_root / "requirements.txt", bundle_dir / "requirements.txt")

    # Launcher scripts invoke the bundled interpreter directly.
    (bundle_dir / "Start_NetworkRecon.cmd").write_text(
        "@echo off\n"
        "cd /d \"%~dp0\"\n"
        "set PYTHONUNBUFFERED=1\n"
        "python\\python.exe -u run_portable.py %*\n",
        encoding="utf-8",
    )
    (bundle_dir / "Start_NetworkRecon.ps1").write_text(
        "$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path\n"
        "$env:PYTHONUNBUFFERED = '1'\n"
        "$pyExe = Join-Path $scriptDir 'python\\python.exe'\n"
        "$runPortable = Join-Path $scriptDir 'run_portable.py'\n"
        "& $pyExe -u $runPortable @args\n",
        encoding="utf-8",
    )

    build_manifest = {
        "commit_sha": provenance.get("head_commit_sha", "unknown"),
        "dirty": provenance.get("dirty", "unknown"),
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
        "patch_checksum": provenance.get("patch_checksum", ""),
        "excluded_paths": provenance.get("excluded_paths", ""),
    }
    (bundle_dir / "build_manifest.json").write_text(
        json.dumps(build_manifest, indent=2), encoding="utf-8"
    )

    # Embed provenance for runtime retrieval when .git is not available.
    runtime_provenance = {
        "head_commit_sha": provenance.get("head_commit_sha", "unknown"),
        "dirty": provenance.get("dirty", "unknown"),
        "patch": provenance.get("patch", ""),
        "patch_checksum": provenance.get("patch_checksum", ""),
        "excluded_paths": provenance.get("excluded_paths", ""),
    }
    (bundle_dir / "build_runtime_provenance.json").write_text(
        json.dumps(runtime_provenance, indent=2), encoding="utf-8"
    )

    dist_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dist_dir / "NetworkReconEngine.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in bundle_dir.rglob("*"):
            arcname = item.relative_to(bundle_dir)
            zf.write(item, arcname=str(arcname))

    print(f"Embedded runtime bundle: {zip_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a portable Windows distribution.")
    parser.add_argument(
        "--pyinstaller",
        action="store_true",
        help="Build the legacy PyInstaller executable instead of the embedded-runtime bundle.",
    )
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Build the embedded-runtime bundle with requirements-legacy.txt for older SSH targets.",
    )
    args = parser.parse_args()

    if args.pyinstaller and args.legacy:
        parser.error("--pyinstaller and --legacy cannot be used together.")

    repo_root = Path(__file__).resolve().parent
    dist_dir = repo_root / "dist"

    if args.pyinstaller:
        return _build_pyinstaller(repo_root, dist_dir)
    return _build_embedded(repo_root, dist_dir, legacy=args.legacy)


if __name__ == "__main__":
    raise SystemExit(main())
