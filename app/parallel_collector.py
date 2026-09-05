from __future__ import annotations

import asyncio
from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import asyncssh
import time

from app.checkpoint import state_to_checkpoint
from app.classification import classify_neighbors
from app.detector import classify_role, identify_device
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
        "failed_command_details": [],
        "recovered_commands": [],
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


def _build_command_evidence(
    command: str,
    elapsed_seconds: float,
    error_type: Optional[str],
) -> Dict[str, Any]:
    """Build a command-evidence entry aligned with the sequential collector.

    Asyncssh cannot provide channel/transport introspection or retry state,
    so those fields are explicitly recorded as ``None``.
    """
    return {
        "command": command,
        "error_type": error_type,
        "elapsed_seconds": elapsed_seconds,
        "transport_active": None,
        "transport_state": None,
        "channel_state": None,
        "recovery_attempted": None,
        "recovery_successful": None,
        "original_error_type": None,
        "original_elapsed_seconds": None,
        "original_stdout": None,
        "original_stderr": None,
        "original_transport_active": None,
        "retry_error": None,
        "retry_error_type": None,
        "retry_elapsed_seconds": None,
    }


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
    """Collect a single device using asyncssh.

    An identity probe (``show version``) runs first in the same SSH session.
    When the probe returns a higher-confidence identity than any pre-populated
    metadata, the detected vendor/platform/role are adopted. Otherwise the
    configured/pre-populated identity is preserved so a recognized vendor is
    not downgraded to ``generic`` because of an unrecognized banner. The
    probe's ``show version`` output is retained as the profile's
    ``show version`` evidence to avoid running it twice.
    """
    summary = _build_summary(device)
    role = (device.metadata.get("role") or {}).get("role")
    platform = None
    commands: List[str] = []
    raw_outputs: Dict[str, str] = {}
    failed_commands: List[str] = []
    failed_command_details: List[Dict[str, Any]] = []

    try:
        async with asyncssh.connect(
            host=device.hostname,
            port=device.port,
            username=device.username,
            password=device.password,
            known_hosts=device.known_hosts if device.known_hosts else None,
            login_timeout=device.timeout,
        ) as conn:
            probe_result = await conn.run("show version", timeout=device.timeout)
            if probe_result.exit_status != 0:
                summary["status"] = "error"
                summary["error"] = f"Identity probe failed: {probe_result.stderr}"
                return _make_bundle(device, summary, {}, [])

            identity = identify_device(probe_result.stdout)
            existing_identity = device.metadata.get("identity") or {}
            existing_confidence = existing_identity.get("confidence", 0.0)

            if identity.confidence > 0 and identity.confidence > existing_confidence:
                device.vendor = identity.vendor
                device.metadata["identity"] = {
                    "vendor": identity.vendor,
                    "platform": identity.platform,
                    "model": identity.model,
                    "confidence": identity.confidence,
                }
                role_obj = classify_role(identity, device.name)
                device.metadata["role"] = {
                    "role": role_obj.role,
                    "confidence": role_obj.confidence,
                }
                role = role_obj.role
                platform = identity.platform
                summary["vendor"] = identity.vendor
                summary["platform"] = identity.platform
                summary["model"] = identity.model
                summary["identity_confidence"] = identity.confidence
                summary["role"] = role_obj.role
                summary["role_confidence"] = role_obj.confidence
            else:
                role = (device.metadata.get("role") or {}).get("role")
                platform = existing_identity.get("platform")
                summary["vendor"] = existing_identity.get("vendor", device.vendor)
                summary["platform"] = existing_identity.get("platform", "unknown")
                summary["model"] = existing_identity.get("model", "unknown")
                summary["identity_confidence"] = existing_confidence
                existing_role = device.metadata.get("role") or {}
                summary["role"] = existing_role.get("role", "unknown")
                summary["role_confidence"] = existing_role.get("confidence", 0.0)

            commands = get_vendor_commands(device.vendor, role=role, platform=platform)

            invalid = validate_device_command_set(commands)
            if invalid:
                summary["status"] = "error"
                summary["error"] = f"Read-only policy violation for {device.name}: {invalid}"
                return _make_bundle(device, summary, {}, [])

            if "show version" in commands:
                raw_outputs["show version"] = probe_result.stdout
                summary["commands_run"] += 1

            for command in commands:
                if command == "show version":
                    continue
                start = time.perf_counter()
                try:
                    result = await conn.run(command, timeout=device.timeout)
                except Exception as exc:
                    elapsed = time.perf_counter() - start
                    summary["commands_run"] += 1
                    raw_outputs[command] = f"ERROR: {exc}"
                    failed_commands.append(command)
                    failed_command_details.append(
                        _build_command_evidence(command, elapsed, type(exc).__name__)
                    )
                    continue
                elapsed = time.perf_counter() - start
                summary["commands_run"] += 1
                if result.exit_status == 0:
                    raw_outputs[command] = result.stdout
                else:
                    raw_outputs[command] = f"ERROR: {result.stderr}"
                    failed_commands.append(command)
                    failed_command_details.append(
                        _build_command_evidence(command, elapsed, "non_zero_exit")
                    )
    except ValueError as exc:
        summary["status"] = "error"
        summary["error"] = str(exc)
        return _make_bundle(device, summary, raw_outputs, commands)
    except Exception as exc:
        summary["status"] = "unreachable"
        summary["error"] = str(exc)
        return _make_bundle(device, summary, raw_outputs, commands)

    summary["status"] = "collected" if not failed_commands else "partial"
    summary["failed_commands"] = failed_commands
    summary["failed_command_details"] = failed_command_details
    summary["recovered_commands"] = []
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
