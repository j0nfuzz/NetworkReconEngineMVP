from __future__ import annotations

from collections import deque
from typing import Any, Dict, List, Optional

from app.checkpoint import state_to_checkpoint
from app.classification import classify_neighbors
from app.collector import execute_device_collection
from app.models import Device, DeviceBundle


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


def run_recursive_collection(
    seed_device: Device,
    default_credentials: Optional[Dict[str, Any]] = None,
    *,
    max_devices: int = 100,
    on_collected: Any = None,
    resume_state: Optional[Dict[str, Any]] = None,
    allowed_devices: Optional[set[str]] = None,
) -> Dict[str, Any]:
    """Collect from a seed device, then recursively collect from supported neighbors."""
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

    while queue and len(visited) < max_devices:
        device = queue.popleft()
        queued.discard(device.name)
        if device.name in visited:
            continue
        visited.add(device.name)

        bundle = execute_device_collection(device)
        bundles[device.name] = bundle

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

        status = bundle.summary.get("status")
        if status in ("collected", "dry-run-success", "partial"):
            successful.append(device.name)
        else:
            failed.append(device.name)
            _emit_checkpoint()
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
            queue.append(
                Device(
                    name=neighbor_name,
                    hostname=ip,
                    vendor=classification,
                    username=defaults.get("username", ""),
                    password=defaults.get("password", ""),
                    enable_password=defaults.get("enable_password"),
                )
            )

        _emit_checkpoint()

    return {
        "successful": successful,
        "failed": failed,
        "unsupported": unsupported,
        "bundles": bundles,
    }
