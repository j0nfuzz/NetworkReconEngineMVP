from __future__ import annotations

import argparse
import getpass
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import yaml

from app.checkpoint import load_checkpoint, save_checkpoint
from app.collector import execute_device_collection, write_bundle
from app.config import load_default_credentials, load_devices
from app.detector import classify_role, identify_device
from app.models import Device, DeviceIdentity
from app.orchestrator import run_recursive_collection
from app.scope import build_troubleshooting_scope
from app.topology import build_topology_graph


def _prompt_interactive_inventory() -> Path:
    """Prompt for device details and write a temporary runtime inventory YAML."""
    print("No device inventory provided. Enter the target device details.")
    hostname = input("Hostname or IP: ").strip()
    while not hostname:
        hostname = input("Hostname or IP: ").strip()
    username = input("Username: ").strip()
    while not username:
        username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    port_input = input("SSH port [22]: ").strip()
    port = int(port_input) if port_input else 22
    vendor = input("Vendor [auto]: ").strip() or "auto"
    name = hostname

    payload = {
        "devices": [
            {
                "name": name,
                "hostname": hostname,
                "vendor": vendor,
                "port": port,
                "username": username,
                "password": password,
            }
        ]
    }

    fd, runtime_path = tempfile.mkstemp(suffix=".yml", prefix="interactive_devices_")
    runtime_path = Path(runtime_path)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.safe_dump(payload, f)
    except Exception:
        runtime_path.unlink(missing_ok=True)
        raise
    return runtime_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect network device diagnostics over SSH.")
    parser.add_argument("--config", default=None, help="Path to YAML device inventory; if omitted, interactive prompts are used")
    parser.add_argument("--output-dir", default="output", help="Directory for generated bundle")
    parser.add_argument("--dry-run", action="store_true", help="Validate configuration without trying SSH")
    parser.add_argument("--verbose", action="store_true", help="Print detailed SSH and collection diagnostics")
    parser.add_argument("--probe", action="store_true", help="Probe device(s), report reachability/legacy classification, then exit")
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Backward-compatible alias: recursive discovery is now the default; use --no-recurse to disable",
    )
    parser.add_argument("--no-recurse", action="store_true", help="Disable recursive discovery from the target device")
    parser.add_argument("--checkpoint-file", default=None, help="Path to JSON checkpoint file for resume/recursive runs")
    parser.add_argument("--target-device", default=None, help="Use this configured device as the traversal root and limit scope to its topology neighbours")
    parser.add_argument(
        "--scope-depth",
        type=int,
        default=1,
        help="Topology radius for --target-device scoping (default 1; no effect without --target-device)",
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=5,
        help="Maximum simultaneous SSH sessions for scoped parallel collection (1-10, default 5)",
    )
    return parser.parse_args()


def _run_recursive_cli(
    seed_device: Device,
    config_path: str,
    output_root: Path,
    bundle_summary: Dict[str, Any],
    log_verbose,
    *,
    checkpoint_file: str | None,
    dry_run: bool,
    target_device: str | None,
    scope_depth: int = 1,
    max_concurrent: int = 5,
) -> None:
    """Run recursive collection from a seed device and populate bundle_summary."""
    default_credentials = load_default_credentials(config_path)

    if dry_run:
        log_verbose("[verbose] Recursive dry-run: skipping real collection")
        bundle = execute_device_collection(seed_device, dry_run=True)
        device_dir = write_bundle(bundle, output_root)
        bundle_summary["devices"].append({
            "name": seed_device.name,
            "vendor": seed_device.vendor,
            "bundle_path": str(device_dir),
            "status": bundle.summary.get("status"),
            "summary": bundle.summary,
        })
        return

    resume_state = None
    if checkpoint_file:
        resume_state = load_checkpoint(checkpoint_file)

    def on_collected(state):
        if checkpoint_file:
            save_checkpoint(checkpoint_file, state)

    allowed_devices = None
    if target_device:
        topology_path = output_root / "topology.json"
        if topology_path.exists():
            topology = json.loads(topology_path.read_text(encoding="utf-8"))
            scope = build_troubleshooting_scope(
                topology, target_device, hops=scope_depth
            )
            allowed_devices = set(scope)
            log_verbose(f"[verbose] Limiting recursive collection to scope: {scope}")
        else:
            log_verbose(f"[verbose] Targeting {target_device} as traversal root; scope will expand as neighbours are discovered")

    if target_device is not None:
        from app.parallel_collector import run_parallel_scoped_collection

        result = run_parallel_scoped_collection(
            seed_device,
            default_credentials=default_credentials,
            resume_state=resume_state,
            on_collected=on_collected,
            allowed_devices=allowed_devices,
            max_concurrent=max_concurrent,
        )
        bundle_items = sorted(result["bundles"].items(), key=lambda item: item[0])
    else:
        result = run_recursive_collection(
            seed_device,
            default_credentials=default_credentials,
            resume_state=resume_state,
            on_collected=on_collected,
            allowed_devices=allowed_devices,
        )
        bundle_items = result["bundles"].items()

    for name, error in result.get("probe_errors", {}).items():
        log_verbose(f"[verbose] Probe error for {name}: {error}")

    for name, bundle in bundle_items:
        log_verbose(f"[verbose] Finished collection for {name}: {bundle.summary.get('status')}")
        device_dir = write_bundle(bundle, output_root)
        bundle_summary["devices"].append({
            "name": name,
            "vendor": bundle.device_vendor,
            "bundle_path": str(device_dir),
            "status": bundle.summary.get("status"),
            "summary": bundle.summary,
        })


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


def _run_cli_collection(
    args: argparse.Namespace,
    devices: List[Device],
    config_path: str,
    output_root: Path,
    verbose: bool,
) -> int:
    """Run collection for parsed devices and write artefacts."""
    output_root.mkdir(parents=True, exist_ok=True)

    bundle_summary: Dict[str, Any] = {
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "dry_run": args.dry_run,
        "devices": [],
    }

    def log_verbose(message: str) -> None:
        if verbose:
            print(message)

    no_recurse = getattr(args, "no_recurse", False)
    recurse = bool(devices and not no_recurse)
    if recurse:
        if args.target_device:
            target_matches = [d for d in devices if d.name == args.target_device]
            if not target_matches:
                print(f"Unknown target device '{args.target_device}' not found in config.")
                return 1
            seed_device = target_matches[0]
        else:
            seed_device = devices[0]
        _run_recursive_cli(
            seed_device,
            config_path,
            output_root,
            bundle_summary,
            log_verbose,
            checkpoint_file=args.checkpoint_file,
            dry_run=args.dry_run,
            target_device=args.target_device,
            scope_depth=args.scope_depth,
            max_concurrent=args.max_concurrent,
        )
    elif devices:
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
                            if result.get("_recovered_client"):
                                recovered = result["_recovered_client"]
                                client.close(connection)
                                connection = recovered
                            identity = identify_device(result.get("stdout", ""))
                            device.vendor = identity.vendor
                            device.metadata["identity"] = {
                                "vendor": identity.vendor,
                                "platform": identity.platform,
                                "model": identity.model,
                                "confidence": identity.confidence,
                            }
                            role = classify_role(identity, device.name)
                            device.metadata["role"] = {"role": role.role, "confidence": role.confidence}
                            log_verbose(
                                f"[verbose] Detected identity for {device.hostname}: "
                                f"vendor={identity.vendor}, platform={identity.platform}, model={identity.model}, role={role.role}"
                            )
                        finally:
                            client.close(connection)
                    else:
                        device.vendor = "generic"
                except Exception as exc:
                    log_verbose(f"[verbose] Auto-detect failed for {device.hostname}: {exc}")
                    device.vendor = "generic"

            if "role" not in device.metadata:
                identity = device.metadata.get("identity")
                identity_obj = DeviceIdentity(**identity) if identity else DeviceIdentity(vendor=device.vendor)
                role = classify_role(identity_obj, device.name)
                device.metadata["role"] = {"role": role.role, "confidence": role.confidence}
                log_verbose(
                    f"[verbose] Classified role for {device.hostname}: "
                    f"role={role.role}, confidence={role.confidence}"
                )

            bundle = execute_device_collection(device, dry_run=args.dry_run)
            if verbose:
                print(f"[verbose] Finished collection for {device.name}: {bundle.summary.get('status')}")
            device_dir = write_bundle(bundle, output_root)
            bundle_summary["devices"].append({
                "name": device.name,
                "vendor": device.vendor,
                "bundle_path": str(device_dir),
                "status": bundle.summary.get("status"),
                "summary": bundle.summary,
            })

    manifest_path = output_root / "bundle_manifest.json"
    manifest_path.write_text(json.dumps(bundle_summary, indent=2), encoding="utf-8")

    topology = build_topology_graph(device["summary"] for device in bundle_summary["devices"])
    topology_path = output_root / "topology.json"
    topology_path.write_text(json.dumps(topology, indent=2), encoding="utf-8")

    print(f"Generated bundle manifest: {manifest_path}")
    return 0


def main() -> int:
    args = parse_args()
    verbose = args.verbose
    output_root = Path(args.output_dir)

    interactive_config_path: Path | None = None
    config_path = args.config
    if config_path is None:
        interactive_config_path = _prompt_interactive_inventory()
        config_path = str(interactive_config_path)

    try:
        devices_data = load_devices(config_path)
        devices = [Device.from_dict(item) for item in devices_data]

        if args.probe:
            results = probe_devices(devices)
            print(json.dumps(results, indent=2))
            return 0

        return _run_cli_collection(
            args=args,
            devices=devices,
            config_path=config_path,
            output_root=output_root,
            verbose=verbose,
        )
    finally:
        if interactive_config_path is not None and interactive_config_path.exists():
            try:
                interactive_config_path.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
