from __future__ import annotations

import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.models import CommandResult, Device, DeviceBundle
from app.ssh_client import DeviceSSHClient
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
    commands = get_vendor_commands(device.vendor)
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
            if result["success"]:
                raw_outputs[command] = result["stdout"]
            else:
                raw_outputs[command] = f"ERROR: {result.get('error', 'Command failed')}\n{result.get('stderr', '')}"
                failed_commands.append(command)
            summary["commands_run"] += 1
    finally:
        ssh_client.close(connection)

    summary["status"] = "collected" if not failed_commands else "partial"
    summary["failed_commands"] = failed_commands
    return DeviceBundle(
        device_name=device.name,
        device_vendor=device.vendor,
        timestamp=datetime.now(timezone.utc).isoformat(),
        summary=summary,
        raw_outputs=raw_outputs,
        failed_commands=failed_commands,
    )


def zip_bundle(device_dir: Path) -> Path:
    archive_path = device_dir.with_suffix(".zip")
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in device_dir.iterdir():
            zf.write(item, arcname=item.name)
    return archive_path


def _safe_filename(name: str) -> str:
    """Return a filesystem-safe stem, replacing Windows-incompatible characters."""
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._")
    return safe or "device"


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
    zip_bundle(device_dir)

    return device_dir
