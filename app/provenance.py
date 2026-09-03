"""Capture repository provenance so field bundles can be traced to an immutable source state."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


DEFAULT_EXCLUDED_PATHS = ("config/*.yml",)


def _env_disables_capture() -> bool:
    """Check whether the environment requests provenance capture be skipped."""
    return os.environ.get("NRE_DISABLE_PROVENANCE", "").lower() in ("1", "true", "yes")


def _is_running_under_pytest() -> bool:
    """Detect pytest execution without adding a runtime dependency on pytest."""
    return "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST") is not None


# Allow tests and CI to disable git-based provenance capture to avoid subprocess crashes.
_provenance_capture_enabled = not (_env_disables_capture() or _is_running_under_pytest())


def is_provenance_capture_enabled() -> bool:
    """Return whether provenance capture is currently enabled."""
    return _provenance_capture_enabled


def set_provenance_capture_enabled(enabled: bool) -> None:
    """Enable or disable provenance capture globally."""
    global _provenance_capture_enabled
    _provenance_capture_enabled = enabled


def _run_git(*args: str) -> str:
    """Run a git command and return stripped stdout; return empty string on failure."""
    try:
        result = subprocess.run(
            ["git", *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            text=True,
            encoding="utf-8",
        )
        return result.stdout.strip()
    except FileNotFoundError:
        return ""


def get_head_commit_sha() -> str:
    """Return the HEAD commit SHA, or 'unknown' if not in a git repository."""
    sha = _run_git("rev-parse", "HEAD")
    return sha if sha else "unknown"


def is_working_tree_dirty() -> bool:
    """Return True if the working tree has uncommitted changes."""
    return _run_git("status", "--porcelain") != ""


def get_unified_diff_patch(excluded_paths: Optional[tuple[str, ...]] = None) -> str:
    """Return the full unified diff patch for tracked files, excluding sensitive paths.

    Args:
        excluded_paths: Glob-style path patterns to exclude from the diff. Defaults to
            credential-bearing config files.
    """
    excluded = excluded_paths or DEFAULT_EXCLUDED_PATHS
    pathspecs = [f":(exclude){pattern}" for pattern in excluded]
    patch = _run_git("diff", "--", *pathspecs)
    return patch


def compute_checksum(content: str) -> str:
    """Return the SHA-256 hex digest of the provided content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def capture_provenance(excluded_paths: Optional[tuple[str, ...]] = None) -> dict[str, str]:
    """Capture the current repository provenance.

    Returns a dictionary with:
    - head_commit_sha
    - dirty ("true"/"false")
    - patch (full unified diff, or empty string if clean/disabled)
    - patch_checksum (SHA-256 of the stored patch content, or empty string if clean/disabled)
    - excluded_paths (comma-separated list)
    """
    if not _provenance_capture_enabled or _env_disables_capture():
        return {
            "head_commit_sha": get_head_commit_sha(),
            "dirty": "unknown",
            "patch": "",
            "patch_checksum": "",
            "excluded_paths": ",".join(excluded_paths or DEFAULT_EXCLUDED_PATHS),
            "capture_disabled": "true",
        }

    head = get_head_commit_sha()
    dirty = is_working_tree_dirty()
    patch = get_unified_diff_patch(excluded_paths=excluded_paths) if dirty else ""
    checksum = compute_checksum(patch) if patch else ""
    return {
        "head_commit_sha": head,
        "dirty": "true" if dirty else "false",
        "patch": patch,
        "patch_checksum": checksum,
        "excluded_paths": ",".join(excluded_paths or DEFAULT_EXCLUDED_PATHS),
    }


def write_provenance_artifact(device_dir: Path, provenance: Optional[dict[str, str]] = None) -> Path:
    """Write a provenance JSON artifact into the bundle directory.

    Args:
        device_dir: Bundle directory for a single device.
        provenance: Optional pre-captured provenance; if omitted, capture() is called.

    Returns:
        Path to the written provenance artifact.
    """
    payload = provenance or capture_provenance()
    artifact_path = device_dir / "build_provenance.json"
    artifact_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return artifact_path
