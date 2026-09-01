# Build a self-contained Windows executable for network device diagnostics.
# Requires: PowerShell, Python 3.12+, and a virtual environment with PyInstaller.
# Usage: .\.venv\Scripts\python.exe -m build_portable

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    venv_python = repo_root / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        print("Virtual environment not found. Run the interactive bootstrap or setup first.")
        return 1

    dist_dir = repo_root / "dist"
    build_dir = repo_root / "build" / "portable"

    for directory in (dist_dir, build_dir):
        if directory.exists():
            shutil.rmtree(directory, ignore_errors=True)

    cmd = [
        str(venv_python),
        "-m",
        "PyInstaller",
        "--name",
        "NetworkDeviceDiagnostics",
        "--onedir",
        "--noconsole",
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


if __name__ == "__main__":
    raise SystemExit(main())
