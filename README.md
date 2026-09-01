# Network Recon Engine

A read-only SSH diagnostics tool for collecting device telemetry and packaging it into an AI-ready bundle.

This project is designed to be safe and operationally useful:

- no configuration writes are attempted
- only diagnostic commands are allowed
- output is grouped into a per-device bundle for review or AI analysis
- it supports interactive startup and direct CLI execution

## Features

- YAML-based device inventory
- interactive PowerShell bootstrap for host, username, port, and password
- SSH connectivity via Paramiko
- vendor-aware command profiles for Cisco, Juniper, Aruba, Arista, and generic devices
- strict read-only command enforcement
- legacy SSH KEX fallback handling for older network appliances
- raw command output capture
- bundle generation with summary and AI prompt output
- ZIP packaging for each device bundle
- dry-run validation mode
- verbose SSH collection diagnostics
- recursive collection with topology-aware scoping
- checkpoint resume support
- bounded parallel collection for scoped runs

## Safety model

This tool is intentionally read-only.

- no `configure`, `copy`, `write`, or change commands are permitted
- vendor profiles only include safe show/get style commands
- the app validates the command set before collection starts
- all output is focused on diagnostics, troubleshooting, and AI-assisted analysis

## Quick start

### Option 1: interactive launch (no inventory file required)

The CLI can prompt for everything needed for a single-device collection. Omit `--config` and enter the target details when asked:

```powershell
.\.venv\Scripts\python.exe -m app.cli --output-dir output --verbose
```

You will be prompted for:

- Hostname or IP
- Username
- Password (hidden)
- SSH port (defaults to `22`)
- Vendor (defaults to `auto`)

The CLI writes the entered details to a temporary runtime YAML in the system temp directory, then runs the normal collection path and deletes the file. Existing `--config` workflows are unchanged.

The packaged executable supports the same prompt-based launch:

```powershell
.\NetworkDeviceDiagnostics.exe --output-dir output --verbose
```

### Option 2: interactive bootstrap (PowerShell)

From the project root:

```powershell
.\interactive_bootstrap.ps1
```

This will:

- prompt for the switch/router host/IP, username, port, and password
- prompt for timeout, host-key policy (`auto`/`reject`/`warning`), and an optional `known_hosts` file
- **auto-detect** the SSH profile by probing the device (modern vs legacy/SHA-1), so operators don't need to know in advance
- create the local virtual environment if needed (`.venv` for modern, `.venv-legacy` for legacy)
- install dependencies unless `-SkipInstall` is used
- build a temporary config and run the collection

You can force a profile explicitly with `-ParamikoProfile modern` or `-ParamikoProfile legacy`; the default `auto` probes the device to decide.

You can also skip the dependency reinstall step on repeat runs:

```powershell
.\interactive_bootstrap.ps1 -SkipInstall
```

### Option 3: direct CLI run with an inventory file

Create or update `config/devices.yml`:

```yaml
devices:
  - name: access-switch-01
    hostname: 10.0.0.10
    vendor: aruba
    port: 22
    username: admin
    password: "<PASSWORD>"
```

Then run a dry validation:

```powershell
.\.venv\Scripts\python.exe -m app.cli --config config\devices.yml --output-dir demo_output --dry-run
```

Run a live collection:

```powershell
.\.venv\Scripts\python.exe -m app.cli --config config\devices.yml --output-dir output
```

Run with detailed SSH diagnostics:

```powershell
.\.venv\Scripts\python.exe -m app.cli --config config\devices.yml --output-dir output --verbose
```

## Recursive collection

Collect from a seed device and discover neighbouring infrastructure devices automatically:

```powershell
.\.venv\Scripts\python.exe -m app.cli --config config\devices.yml --output-dir output --recursive
```

The first device in the inventory becomes the seed. Supported neighbours (Cisco, Aruba, FortiGate, Juniper) are queued and collected automatically; unsupported devices are recorded but skipped. Omitting `--recursive` performs a flat, non-recursive collection of the configured devices only.

### Scope collection to a target device and its neighbours

Use `--target-device` to limit recursion to a single device and its direct topology neighbours:

```powershell
.\.venv\Scripts\python.exe -m app.cli --config config\devices.yml --output-dir output --recursive --target-device core-switch-01
```

This requires a `topology.json` file in the output directory. If no topology file exists, collection is limited to the named device only. Omitting `--target-device` runs recursive collection unscoped using the sequential orchestrator without topology-based limiting. `--target-device` is the only path that enables parallel SSH sessions.

### Bounded parallel collection

When `--target-device` is used, multiple devices in scope are collected concurrently. The default concurrency is 5 and the maximum allowed is 10:

```powershell
.\.venv\Scripts\python.exe -m app.cli --config config\devices.yml --output-dir output --recursive --target-device core-switch-01 --max-concurrent 8
```

Parallel collection is gated by scoping to prevent estate-wide AAA or device overload.

## Checkpoint and resume

Long-running recursive collections can be resumed. Pass `--checkpoint-file` to persist state after each device is processed:

```powershell
.\.venv\Scripts\python.exe -m app.cli --config config\devices.yml --output-dir output --recursive --checkpoint-file output\checkpoint.json
```

Omitting `--checkpoint-file` runs collection without loading or saving checkpoint state. If the run is interrupted, rerun the same command. Visited, pending, successful, failed, and unsupported device lists are restored and the queue continues from the last saved state.

When `--target-device` is used, checkpoint state is filtered to the same scope, so out-of-scope pending entries cannot re-enter the collection.

## Live run behavior

The tool will:

- test SSH reachability
- detect vendor automatically when configured as `vendor: auto`
- run the allowed read-only commands for that device family
- capture raw output for each command
- write a device bundle and summary JSON
- create an AI prompt file suitable for troubleshooting analysis
- export the final bundle as a ZIP archive

## Output format

Each device produces a directory under the output folder, for example:

- `output/access-switch-01/`
  - `summary.json` - structured device state, health score, discovered neighbours
  - `show_version.txt`, `show_interfaces_brief.txt`, ... - raw command output
  - `ai_prompt.txt` - AI-ready diagnostic briefing
  - `troubleshooting_bundle.json` - normalised summary + health assessment
  - `access-switch-01.zip` - packaged device bundle

The following artefacts are also written to the output root:

- `output/bundle_manifest.json` - list of all collected devices, sorted by device name
- `output/topology.json` - discovered device graph; used by `--target-device` scoping

### summary.json fields

Key fields include:

- `device` - inventory name
- `hostname` - management address
- `vendor` - detected or configured vendor
- `platform` / `model` - platform identification when available
- `role` - inferred device role when available
- `commands_run` - number of diagnostic commands executed
- `failed_commands` - list of commands that returned errors
- `discovered_neighbors` - neighbour records from CDP/LLDP
- `status` - one of `collected`, `partial`, `unreachable`, `dry-run-success`
- `health_score` - numeric score added when collection completes successfully
- `warnings` / `critical` - deterministic health observations

### troubleshooting_bundle.json

A condensed diagnostic bundle combining the normalised summary, health score, warnings, critical items, and selected raw outputs. It is intended for direct review or LLM-assisted troubleshooting without exposing every raw file.

### topology.json

A graph of discovered devices and their adjacencies. It is produced at the end of every run and is required by `--target-device` scoping for subsequent targeted collections.

## SSH compatibility notes

Older network appliances sometimes reject modern Paramiko defaults during key exchange negotiation. The tool includes compatibility fallbacks for legacy algorithms and surfaces a clearer diagnostic message when the SSH peer is older or incompatible.

If a device fails with an SSH handshake error, the connection logic will retry with legacy KEX fallbacks and print a more actionable explanation in verbose mode.

Per-device host-key options are also supported in the inventory (`host_key_policy`, optional `known_hosts`), so strict verification can be enabled in production; see `config/devices.yml` and `interactive_bootstrap.ps1` for examples.

## Project structure

- `app/` - CLI, collector, SSH client, vendor profiles, and detection logic
- `config/` - sample device inventory and generated runtime config
- `tests/` - regression coverage for dry-run behavior, vendor detection, and SSH compatibility
- `interactive_bootstrap.ps1` - single-command entry point for local setup and collection

## Portable distribution

A self-contained Windows executable can be built from the repository using PyInstaller. This allows the tool to run on a workstation that does not have Python or Git installed.

Build the executable from the project root:

```powershell
.\.venv\Scripts\python.exe -m build_portable
```

The build produces `dist\NetworkDeviceDiagnostics.zip`, a single archive containing `NetworkDeviceDiagnostics.exe` and its bundled dependencies. Extract the archive on the target workstation and run the executable with the same arguments as the Python CLI.

### Interactive packaged launch

If you do not have a prepared inventory, launch the executable without `--config` and enter the device details at the prompts:

```powershell
.\NetworkDeviceDiagnostics.exe --output-dir output --verbose
```

The executable will prompt for hostname/IP, username, hidden password, SSH port (default `22`), and vendor (default `auto`), then write a temporary runtime YAML and continue with collection.

### Packaged launch with an existing inventory

If you already have an inventory file, use the same `--config` path as the source CLI:

```powershell
.\NetworkDeviceDiagnostics.exe --config config\devices.yml --output-dir output
```

Some endpoint protection products may quarantine or delete unsigned executables; if this happens, restore the file from quarantine or build the executable on the target workstation.

The source-based workflow remains available and unchanged for development or custom environments.

## Typical workflow

1. Start the project with `interactive_bootstrap.ps1` or the packaged `NetworkDeviceDiagnostics.exe`
2. Enter the device host, username, port, and password
3. Review the generated bundle under the output directory
4. Use the summary, troubleshooting bundle, and AI prompt files to investigate the device state
5. For larger environments, use `--recursive` with `--checkpoint-file` to discover neighbours and resume after an interruption

## Requirements

- Python 3.10+
- Paramiko
- PyYAML
- Windows PowerShell is used for the interactive bootstrap script, but the Python CLI itself can be run in a standard Python env
