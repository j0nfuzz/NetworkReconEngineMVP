from __future__ import annotations

from collections import deque
from typing import Any, Dict, List, Optional

from app.checkpoint import state_to_checkpoint
from app.classification import classify_neighbors
from app.collector import execute_device_collection
from app.detector import classify_role, identify_device
from app.models import Device, DeviceBundle
from app.ssh_client import DeviceSSHClient


def _existing_identity_confidence(device: Device) -> float:
    identity = device.metadata.get("identity")
    if isinstance(identity, dict):
        return float(identity.get("confidence", 0.0))
    return 0.0


def _probe_identity(device: Device) -> Optional[str]:
    """Probe device identity and update vendor/platform/role metadata when more confident.

    Mutates ``device`` in place.  Any failure leaves the device unchanged so that
    collection can still proceed with the original vendor/platform hints.

    Returns the probe error string when the device is unreachable, otherwise ``None``.
    """
    existing_confidence = _existing_identity_confidence(device)

    client = DeviceSSHClient(
        hostname=device.hostname,
        username=device.username,
        password=device.password,
        port=device.port,
        timeout=device.timeout,
        host_key_policy=device.host_key_policy,
        known_hosts=device.known_hosts,
    )
    probe = client.probe()
    if not probe.get("reachable"):
        return str(probe.get("error") or "")

    connection = None
    try:
        connection = client.connect()
        result = client.run_command("show version", client=connection)
        identity = identify_device(result.get("stdout", ""))
        if identity.confidence > 0 and identity.confidence > existing_confidence:
            device.vendor = identity.vendor
            device.metadata["identity"] = {
                "vendor": identity.vendor,
                "platform": identity.platform,
                "model": identity.model,
                "confidence": identity.confidence,
            }
            role = classify_role(identity, device.name)
            device.metadata["role"] = {"role": role.role, "confidence": role.confidence}
        elif existing_confidence > 0 and device.vendor in ("auto", "unknown"):
            existing = device.metadata.get("identity") or {}
            existing_vendor = existing.get("vendor")
            if existing_vendor:
                device.vendor = existing_vendor
    except Exception:
        return None
    finally:
        client.close(connection)

    return None


def _device_identity_set(device: Device) -> set[str]:
    """Return the identity-equivalence set for a device (name + hostname).

    Hostnames and names are normalised to lower-case because network identities
    are case-insensitive; this lets the same physical box be recognised whether
    it is reached by LLDP-reported system-name or management-address.
    """
    identities: set[str] = {device.name.lower()}
    if device.hostname:
        identities.add(device.hostname.lower())
    return identities


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
                metadata={"discovered_neighbor": True},
            )
        )
    return devices


def run_recursive_collection(
    seed_device: Device,
    default_credentials: Optional[Dict[str, Any]] = None,
    *,
    max_devices: int = 100,
    on_collected: Any = None,
    on_device_collected: Any = None,
    resume_state: Optional[Dict[str, Any]] = None,
    allowed_devices: Optional[set[str]] = None,
    on_progress: Any = None,
) -> Dict[str, Any]:
    """Collect from a seed device, then recursively collect from supported neighbors.

    Args:
        on_device_collected: Optional callback invoked immediately after each device
            is collected. Receives (device_name, bundle) so callers can stream artefacts
            live instead of buffering until the run finishes.
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

    known_identities: set[str] = set()
    known_identities.update({name.lower() for name in visited})
    for device in queue:
        queued.add(device.name)
        known_identities.update(_device_identity_set(device))

    probe_errors: Dict[str, str] = {}

    while queue and len(visited) < max_devices:
        device = queue.popleft()
        queued.discard(device.name)
        if device.name in visited:
            continue
        visited.add(device.name)

        discovered_neighbor = bool(device.metadata.get("discovered_neighbor"))
        if device.vendor in ("auto", "unknown") or (
            discovered_neighbor and _existing_identity_confidence(device) <= 0
        ):
            if callable(on_progress):
                on_progress(f"[verbose] {device.name}: probing identity...")
            probe_error = _probe_identity(device)
            if probe_error:
                probe_errors[device.name] = probe_error
                if callable(on_progress):
                    on_progress(f"[verbose] {device.name}: identity probe failed: {probe_error}")
            elif callable(on_progress):
                if _existing_identity_confidence(device) > 0 or device.vendor not in ("auto", "unknown"):
                    on_progress(f"[verbose] {device.name}: identity resolved: vendor={device.vendor}")
                else:
                    on_progress(f"[verbose] {device.name}: identity probe: no confident match; retaining vendor={device.vendor}")

        if callable(on_progress):
            bundle = execute_device_collection(device, progress=on_progress)
        else:
            bundle = execute_device_collection(device)
        bundles[device.name] = bundle

        def _emit_checkpoint() -> None:
            state = state_to_checkpoint(
                visited=visited,
                queued=queued,
                successful=successful,
                failed=failed,
                unsupported=unsupported,
            )
            if callable(on_collected):
                on_collected(state)
            if callable(on_device_collected):
                on_device_collected(device.name, bundle, state)

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

            neighbor_device = Device(
                name=neighbor_name,
                hostname=ip,
                vendor=classification,
                username=defaults.get("username", ""),
                password=defaults.get("password", ""),
                enable_password=defaults.get("enable_password"),
                metadata={"discovered_neighbor": True},
            )
            if _device_identity_set(neighbor_device) & known_identities:
                continue

            queued.add(neighbor_name)
            known_identities.update(_device_identity_set(neighbor_device))
            queue.append(neighbor_device)

        _emit_checkpoint()

    return {
        "successful": successful,
        "failed": failed,
        "unsupported": unsupported,
        "bundles": bundles,
        "probe_errors": probe_errors,
    }
