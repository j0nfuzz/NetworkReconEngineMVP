from __future__ import annotations

from collections import deque
from typing import Any, Dict, List, Optional

from app.classification import classify_neighbors
from app.collector import execute_device_collection
from app.models import Device, DeviceBundle


def run_recursive_collection(
    seed_device: Device,
    default_credentials: Optional[Dict[str, Any]] = None,
    *,
    max_devices: int = 100,
) -> Dict[str, Any]:
    """Collect from a seed device, then recursively collect from supported neighbors."""
    defaults = default_credentials or {}
    visited: set[str] = set()
    queued: set[str] = {seed_device.name}
    successful: List[str] = []
    failed: List[str] = []
    unsupported: List[str] = []
    bundles: Dict[str, DeviceBundle] = {}
    queue: deque[Device] = deque([seed_device])

    while queue and len(visited) < max_devices:
        device = queue.popleft()
        queued.discard(device.name)
        if device.name in visited:
            continue
        visited.add(device.name)

        bundle = execute_device_collection(device)
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

    return {
        "successful": successful,
        "failed": failed,
        "unsupported": unsupported,
        "bundles": bundles,
    }
