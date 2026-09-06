from __future__ import annotations

import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import os

from app.discovery import extract_neighbors
from app.health import score_device_health
from app.models import CommandResult, Device, DeviceBundle
from app.normalization import build_device_summary
from app.provenance import write_provenance_artifact
from app.ssh_client import DeviceSSHClient
from app.troubleshooting import build_troubleshooting_bundle
from app.vendor_profiles import get_vendor_commands, validate_device_command_set


def execute_device_collection(device: Device, *, dry_run: bool = False) -> DeviceBundle:
    summary: Dict[str, Any] = {
        "device": device.name,
        "hostname": device.hostname,
        "vendor": device.vendor,
        "platform": "unknown",
        "model": "unknown",
        "identity_confidence": 0.0,
        "role": "unknown",
        "role_confidence": 0.0,
        "discovered_neighbors": [],
        "status": "dry-run" if dry_run else "pending",
        "commands_run": 0,
        "failed_commands": [],
    }
    identity = device.metadata.get("identity")
    if identity:
        summary["platform"] = identity.get("platform", "unknown")
        summary["model"] = identity.get("model", "unknown")
        summary["identity_confidence"] = identity.get("confidence", 0.0)
    role = device.metadata.get("role")
    if role:
        summary["role"] = role.get("role", "unknown")
        summary["role_confidence"] = role.get("confidence", 0.0)

    raw_outputs: Dict[str, str] = {}
    failed_commands: List[str] = []
    failed_command_details: List[Dict[str, object]] = []
    recovered_commands: List[Dict[str, object]] = []
    role = (device.metadata.get("role") or {}).get("role")
    platform = identity.get("platform") if identity else None
    commands = get_vendor_commands(device.vendor, role=role, platform=platform)
    invalid_commands = validate_device_command_set(commands)
    if invalid_commands:
        raise ValueError(f"Read-only policy violation for {device.name}: {invalid_commands}")

    if dry_run:
        for command in commands:
            raw_outputs[command] = f"DRY RUN: {command}\n[simulated output placeholder]"
        summary["commands_run"] = len(commands)
        summary["status"] = "dry-run-success"
        return DeviceBundle(
            device_name=device.name,
            device_vendor=device.vendor,
            timestamp=datetime.now(timezone.utc).isoformat(),
            summary=summary,
            raw_outputs=raw_outputs,
            failed_commands=failed_commands,
        )

    ssh_client = DeviceSSHClient(
        hostname=device.hostname,
        username=device.username,
        password=device.password,
        port=device.port,
        timeout=device.timeout,
        host_key_policy=device.host_key_policy,
        known_hosts=device.known_hosts,
    )

    probe = ssh_client.probe()
    if not probe.get("reachable", False):
        summary["status"] = "unreachable"
        summary["error"] = probe.get("error", "SSH connection failed")
        return DeviceBundle(
            device_name=device.name,
            device_vendor=device.vendor,
            timestamp=datetime.now(timezone.utc).isoformat(),
            summary=summary,
            raw_outputs=raw_outputs,
            failed_commands=commands,
        )

    try:
        connection = ssh_client.connect()
    except Exception as exc:
        summary["status"] = "unreachable"
        summary["error"] = str(exc)
        return DeviceBundle(
            device_name=device.name,
            device_vendor=device.vendor,
            timestamp=datetime.now(timezone.utc).isoformat(),
            summary=summary,
            raw_outputs=raw_outputs,
            failed_commands=commands,
        )

    try:
        for command in commands:
            result = ssh_client.run_command(command, client=connection)
            if result.get("_recovered_client"):
                recovered = result["_recovered_client"]
                ssh_client.close(connection)
                connection = recovered
            if result["success"]:
                raw_outputs[command] = result["stdout"]
            else:
                raw_outputs[command] = (
                    f"ERROR: {result.get('error', 'Command failed')}\n"
                    f"STDOUT:\n{result.get('stdout', '')}\n"
                    f"STDERR:\n{result.get('stderr', '')}"
                )
                failed_commands.append(command)
            command_evidence = {
                "command": command,
                "elapsed_seconds": result.get("elapsed_seconds"),
                "error_type": result.get("error_type"),
                "transport_active": result.get("transport_active"),
                "transport_state": result.get("transport_state"),
                "channel_state": result.get("channel_state"),
                "recovery_attempted": result.get("recovery_attempted"),
                "recovery_successful": result.get("recovery_successful"),
                "original_error_type": result.get("original_error_type"),
                "original_elapsed_seconds": result.get("original_elapsed_seconds"),
                "original_stdout": result.get("original_stdout"),
                "original_stderr": result.get("original_stderr"),
                "original_transport_active": result.get("original_transport_active"),
                "retry_error": result.get("retry_error"),
                "retry_error_type": result.get("retry_error_type"),
                "retry_elapsed_seconds": result.get("retry_elapsed_seconds"),
            }
            if result.get("success") and result.get("recovery_attempted"):
                recovered_commands.append(command_evidence)
            elif not result.get("success"):
                failed_command_details.append(command_evidence)
            summary["commands_run"] += 1
    finally:
        ssh_client.close(connection)

    summary["status"] = "collected" if not failed_commands else "partial"
    summary["failed_commands"] = failed_commands
    summary["failed_command_details"] = failed_command_details
    summary["recovered_commands"] = recovered_commands
    summary["discovered_neighbors"] = extract_neighbors(device.vendor, raw_outputs)
    return DeviceBundle(
        device_name=device.name,
        device_vendor=device.vendor,
        timestamp=datetime.now(timezone.utc).isoformat(),
        summary=summary,
        raw_outputs=raw_outputs,
        failed_commands=failed_commands,
    )


def zip_bundle(device_dir: Path) -> Path:
    archive_path = device_dir.parent / f"{device_dir.name}.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in device_dir.iterdir():
            zf.write(item, arcname=item.name)
    return archive_path


def _safe_filename(name: str) -> str:
    """Return a filesystem-safe stem, replacing Windows-incompatible characters."""
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._")
    return safe or "device"


def _merge_health_into_summary(summary: Dict[str, Any], health: Dict[str, Any]) -> Dict[str, Any]:
    """Merge health scoring into an existing summary without removing fields."""
    merged = dict(summary)
    merged.update({
        "health_score": health["score"],
        "warnings": health["warnings"],
        "critical": health["critical"],
    })
    return merged


def _write_analysis_artifacts(bundle: DeviceBundle, device_dir: Path) -> None:
    """Write raw summary merged with health, plus troubleshooting bundle."""
    normalized_summary = build_device_summary(bundle)
    health = score_device_health(normalized_summary)
    troubleshooting = build_troubleshooting_bundle(normalized_summary, health, bundle.raw_outputs or {})

    summary_with_health = _merge_health_into_summary(bundle.summary, health)

    (device_dir / "summary.json").write_text(json.dumps(summary_with_health, indent=2), encoding="utf-8")
    (device_dir / "troubleshooting_bundle.json").write_text(json.dumps(troubleshooting, indent=2), encoding="utf-8")


def write_bundle(bundle: DeviceBundle, output_dir: str | Path) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    device_dir = directory / _safe_filename(bundle.device_name)
    device_dir.mkdir(parents=True, exist_ok=True)

    summary_path = device_dir / "summary.json"
    summary_path.write_text(json.dumps(bundle.summary, indent=2), encoding="utf-8")

    for command_name, content in bundle.raw_outputs.items():
        safe_name = _safe_filename(command_name)
        (device_dir / f"{safe_name}.txt").write_text(content, encoding="utf-8")

    sample_output = "\n\n".join(
        f"Command: {name}\n{content[:600]}" for name, content in bundle.raw_outputs.items()
    )

    ai_prompt = (
        "You are analyzing a network device diagnostic bundle.\n"
        "Use only the output files in this directory.\n"
        "Focus on read-only diagnostics, device health, interface status, and known issues.\n"
        "Do not attempt any config changes or write operations.\n\n"
        f"Device: {bundle.device_name}\n"
        f"Vendor: {bundle.device_vendor}\n"
        f"Timestamp: {bundle.timestamp}\n\n"
        "Available artifacts:\n"
        + "\n".join(f"- {name}" for name in bundle.raw_outputs.keys())
        + "\n\n"
        "Device output snapshot:\n"
        + sample_output
        + "\n\n"
        "Please summarize device state, call out any warnings, and provide suspected causes or next steps."
    )
    (device_dir / "ai_prompt.txt").write_text(ai_prompt, encoding="utf-8")

    if not str(bundle.summary.get("status", "")).startswith("dry-run"):
        _write_analysis_artifacts(bundle, device_dir)

    if os.environ.get("NRE_DISABLE_PROVENANCE", "").lower() not in ("1", "true", "yes"):
        write_provenance_artifact(device_dir)
    zip_bundle(device_dir)

    return device_dir
