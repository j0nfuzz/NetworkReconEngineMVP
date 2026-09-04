from __future__ import annotations

import asyncio
from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import asyncssh

from app.checkpoint import state_to_checkpoint
from app.classification import classify_neighbors
from app.discovery import extract_neighbors
from app.models import Device, DeviceBundle
from app.vendor_profiles import get_vendor_commands, validate_device_command_set

DEFAULT_MAX_CONCURRENT = 5
MAX_CONCURRENT_CEILING = 10


def _build_summary(device: Device) -> Dict[str, Any]:
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
        "status": "pending",
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
    return summary


def _make_bundle(device: Device, summary: Dict[str, Any], raw_outputs: Dict[str, str], failed_commands: List[str]) -> DeviceBundle:
    return DeviceBundle(
        device_name=device.name,
        device_vendor=device.vendor,
        timestamp=datetime.now(timezone.utc).isoformat(),
        summary=summary,
        raw_outputs=raw_outputs,
        failed_commands=failed_commands,
    )


def _reconstruct_pending_devices(
    pending_names: List[str],
    discovered: List[Dict[str, str]],
    defaults: Dict[str, Any],
) -> List[Device]:
    """Rebuild pending devices from names, using neighbor records for hostname when possible."""
    name_to_ip = {
        record.get("neighbor", ""): record.get("ip", "")
        for record in discovered or []
        if record.get("neighbor")
    }
    devices: List[Device] = []
    for name in pending_names:
        devices.append(
            Device(
                name=name,
                hostname=name_to_ip.get(name, ""),
                vendor="unknown",
                username=defaults.get("username", ""),
                password=defaults.get("password", ""),
                enable_password=defaults.get("enable_password"),
            )
        )
    return devices


async def _collect_device(device: Device) -> DeviceBundle:
    """Collect a single device using asyncssh."""
    summary = _build_summary(device)
    role = (device.metadata.get("role") or {}).get("role")

    try:
        commands = get_vendor_commands(device.vendor, role=role)
    except ValueError as exc:
        summary["status"] = "error"
        summary["error"] = str(exc)
        return _make_bundle(device, summary, {}, [])

    invalid = validate_device_command_set(commands)
    if invalid:
        summary["status"] = "error"
        summary["error"] = f"Read-only policy violation for {device.name}: {invalid}"
        return _make_bundle(device, summary, {}, [])

    raw_outputs: Dict[str, str] = {}
    failed_commands: List[str] = []

    try:
        async with asyncssh.connect(
            host=device.hostname,
            port=device.port,
            username=device.username,
            password=device.password,
            known_hosts=device.known_hosts if device.known_hosts else None,
            login_timeout=device.timeout,
        ) as conn:
            for command in commands:
                try:
                    result = await conn.run(command, timeout=device.timeout)
                    summary["commands_run"] += 1
                    if result.exit_status == 0:
                        raw_outputs[command] = result.stdout
                    else:
                        raw_outputs[command] = f"ERROR: {result.stderr}"
                        failed_commands.append(command)
                except Exception as exc:
                    summary["commands_run"] += 1
                    raw_outputs[command] = f"ERROR: {exc}"
                    failed_commands.append(command)
    except Exception as exc:
        summary["status"] = "unreachable"
        summary["error"] = str(exc)
        return _make_bundle(device, summary, raw_outputs, commands)

    summary["status"] = "collected" if not failed_commands else "partial"
    summary["failed_commands"] = failed_commands
    summary["discovered_neighbors"] = extract_neighbors(device.vendor, raw_outputs)
    return _make_bundle(device, summary, raw_outputs, failed_commands)


async def run_parallel_scoped_collection_async(
    seed_device: Device,
    default_credentials: Optional[Dict[str, Any]] = None,
    *,
    max_devices: int = 100,
    max_concurrent: int = DEFAULT_MAX_CONCURRENT,
    on_collected: Any = None,
    resume_state: Optional[Dict[str, Any]] = None,
    allowed_devices: Optional[set[str]] = None,
) -> Dict[str, Any]:
    """Collect recursively from a seed device using bounded concurrency.

    This path is used when a target-device scope or unbounded recursive discovery
    is active. It preserves the same checkpoint/resume semantics and neighbor
    filtering as the sequential orchestrator, but collects all queued devices in
    each wave concurrently. ``allowed_devices=None`` means unbounded discovery.
    """

    defaults = default_credentials or {}
    resume = resume_state or {}
    visited: set[str] = set(resume.get("visited", []))
    successful: List[str] = list(resume.get("successful", []))
    failed: List[str] = list(resume.get("failed", []))
    unsupported: List[str] = list(resume.get("unsupported", []))
    bundles: Dict[str, DeviceBundle] = {}

    pending_names = list(resume.get("pending", []))
    if allowed_devices is not None:
        pending_names = [name for name in pending_names if name in allowed_devices]
    queued: set[str] = set(pending_names)
    pending_devices = _reconstruct_pending_devices(pending_names, [], defaults)
    queue: deque[Device] = deque(pending_devices)
    if seed_device.name not in visited:
        queue.append(seed_device)
    for device in queue:
        queued.add(device.name)

    effective_max_concurrent = min(max(max_concurrent, 1), MAX_CONCURRENT_CEILING)
    semaphore = asyncio.Semaphore(effective_max_concurrent)

    async def _bounded_collect(device: Device) -> DeviceBundle:
        async with semaphore:
            return await _collect_device(device)

    def _emit_checkpoint() -> None:
        if callable(on_collected):
            on_collected(
                state_to_checkpoint(
                    visited=visited,
                    queued=queued,
                    successful=successful,
                    failed=failed,
                    unsupported=unsupported,
                )
            )

    while queue and len(visited) < max_devices:
        remaining = max_devices - len(visited)
        wave_size = min(effective_max_concurrent, remaining)
        wave: List[Device] = []
        while queue and len(wave) < wave_size:
            device = queue.popleft()
            queued.discard(device.name)
            wave.append(device)

        tasks = [_bounded_collect(device) for device in wave]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        pairs: List[tuple[Device, DeviceBundle]] = []
        for device, outcome in zip(wave, results):
            if isinstance(outcome, Exception):
                bundle = _make_unreachable_bundle(device, str(outcome))
            else:
                bundle = outcome
            pairs.append((device, bundle))
        pairs.sort(key=lambda item: item[0].name)

        next_queue: deque[Device] = deque()

        for device, bundle in pairs:
            if device.name in visited:
                continue
            visited.add(device.name)
            bundles[device.name] = bundle

            status = bundle.summary.get("status")
            if status in ("collected", "dry-run-success", "partial"):
                successful.append(device.name)
            else:
                failed.append(device.name)
                continue

            discovered = bundle.summary.get("discovered_neighbors", [])
            classifications = classify_neighbors(discovered)

            for record in discovered:
                neighbor_name = record.get("neighbor")
                if not neighbor_name or neighbor_name in visited or neighbor_name in queued:
                    continue
                if allowed_devices is not None and neighbor_name not in allowed_devices:
                    continue

                classification = classifications.get(neighbor_name, "unknown")
                if classification not in ("cisco", "aruba", "fortigate", "juniper"):
                    if neighbor_name not in unsupported:
                        unsupported.append(neighbor_name)
                    continue

                ip = record.get("ip")
                if not ip:
                    if neighbor_name not in failed:
                        failed.append(neighbor_name)
                    continue

                queued.add(neighbor_name)
                next_queue.append(
                    Device(
                        name=neighbor_name,
                        hostname=ip,
                        vendor=classification,
                        username=defaults.get("username", ""),
                        password=defaults.get("password", ""),
                        enable_password=defaults.get("enable_password"),
                    )
                )

        for device in sorted(next_queue, key=lambda d: d.name):
            queue.append(device)

        _emit_checkpoint()

    return {
        "successful": successful,
        "failed": failed,
        "unsupported": unsupported,
        "bundles": dict(sorted(bundles.items())),
    }


def _make_unreachable_bundle(device: Device, error: str) -> DeviceBundle:
    summary = _build_summary(device)
    summary["status"] = "unreachable"
    summary["error"] = error
    return _make_bundle(device, summary, {}, [])


def run_parallel_scoped_collection(
    seed_device: Device,
    default_credentials: Optional[Dict[str, Any]] = None,
    *,
    max_devices: int = 100,
    max_concurrent: int = DEFAULT_MAX_CONCURRENT,
    on_collected: Any = None,
    resume_state: Optional[Dict[str, Any]] = None,
    allowed_devices: Optional[set[str]] = None,
) -> Dict[str, Any]:
    """Synchronous entry point for parallel scoped collection."""
    return asyncio.run(
        run_parallel_scoped_collection_async(
            seed_device,
            default_credentials,
            max_devices=max_devices,
            max_concurrent=max_concurrent,
            on_collected=on_collected,
            resume_state=resume_state,
            allowed_devices=allowed_devices,
        )
    )
