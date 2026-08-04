from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from app.collector import execute_device_collection, write_bundle
from app.config import load_devices
from app.detector import identify_device
from app.models import Device


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect network device diagnostics over SSH.")
    parser.add_argument("--config", required=True, help="Path to YAML device inventory")
    parser.add_argument("--output-dir", default="output", help="Directory for generated bundle")
    parser.add_argument("--dry-run", action="store_true", help="Validate configuration without trying SSH")
    parser.add_argument("--verbose", action="store_true", help="Print detailed SSH and collection diagnostics")
    parser.add_argument("--probe", action="store_true", help="Probe device(s), report reachability/legacy classification, then exit")
    return parser.parse_args()


def _is_legacy_error(text: str) -> bool:
    """Heuristic: does an SSH failure message point to a legacy/SHA-1 device?"""
    lowered = (text or "").lower()
    markers = (
        "sha1", "sha-1", "kex", "key exchange", "algorithm", "compatib",
        "group1", "group14", "no acceptable", "incompatible",
    )
    return any(marker in lowered for marker in markers)


def probe_devices(devices: List[Device]) -> List[Dict[str, object]]:
    """Attempt an SSH connection to each device and classify it for backend choice.

    Classification:
      - ``modern``: connection succeeded (current Paramiko works fine).
      - ``legacy``: not reachable and the failure looks like a SHA-1/KEX mismatch
        (device only speaks older algorithms) -> use the legacy Paramiko profile.
      - ``unreachable``: not reachable for a non-legacy reason (e.g. network/timeout/auth).
    """
    from app.ssh_client import DeviceSSHClient

    results: List[Dict[str, object]] = []
    for device in devices:
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
        error = str(probe.get("error", ""))
        if probe.get("reachable"):
            classification = "modern"
        elif _is_legacy_error(error):
            classification = "legacy"
        else:
            classification = "unreachable"
        results.append({
            "name": device.name,
            "hostname": device.hostname,
            "reachable": bool(probe.get("reachable")),
            "classification": classification,
            "error": error,
        })
    return results


def main() -> int:
    args = parse_args()
    verbose = args.verbose
    devices_data = load_devices(args.config)
    devices = [Device.from_dict(item) for item in devices_data]

    if args.probe:
        results = probe_devices(devices)
        print(json.dumps(results, indent=2))
        return 0

    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    bundle_summary: Dict[str, Any] = {
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "dry_run": args.dry_run,
        "devices": [],
    }

    def log_verbose(message: str) -> None:
        if verbose:
            print(message)

    for device in devices:
        log_verbose(f"[verbose] Starting device: {device.name} ({device.hostname}:{device.port})")
        if device.vendor == "auto":
            try:
                # Auto-detect vendor from a quick read-only probe.
                from app.ssh_client import DeviceSSHClient

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
                log_verbose(f"[verbose] Probe result for {device.hostname}: {probe}")
                if probe.get("reachable"):
                    connection = client.connect()
                    try:
                        result = client.run_command("show version", client=connection)
                        identity = identify_device(result.get("stdout", ""))
                        device.vendor = identity.vendor
                        device.metadata["identity"] = {
                            "vendor": identity.vendor,
                            "platform": identity.platform,
                            "model": identity.model,
                            "confidence": identity.confidence,
                        }
                        log_verbose(
                            f"[verbose] Detected identity for {device.hostname}: "
                            f"vendor={identity.vendor}, platform={identity.platform}, model={identity.model}"
                        )
                    finally:
                        client.close(connection)
                else:
                    device.vendor = "generic"
            except Exception as exc:
                log_verbose(f"[verbose] Auto-detect failed for {device.hostname}: {exc}")
                device.vendor = "generic"

        bundle = execute_device_collection(device, dry_run=args.dry_run)
        if verbose:
            print(f"[verbose] Finished collection for {device.name}: {bundle.summary.get('status')}")
        bundle_path = write_bundle(bundle, output_root)
        bundle_summary["devices"].append({
            "name": device.name,
            "vendor": device.vendor,
            "bundle_path": str(bundle_path),
            "status": bundle.summary.get("status"),
        })

    manifest_path = output_root / "bundle_manifest.json"
    manifest_path.write_text(json.dumps(bundle_summary, indent=2), encoding="utf-8")

    print(f"Generated bundle manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
