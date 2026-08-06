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

## Safety model

This tool is intentionally read-only.

- no `configure`, `copy`, `write`, or change commands are permitted
- vendor profiles only include safe show/get style commands
- the app validates the command set before collection starts
- all output is focused on diagnostics, troubleshooting, and AI-assisted analysis

## Quick start

### Option 1: interactive bootstrap (recommended)

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

### Option 2: direct CLI run

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
  - `summary.json`
  - `show_version.txt`
  - `show_interfaces_brief.txt`
  - `ai_prompt.txt`
  - `access-switch-01.zip`

The manifest is also written to:

- `output/bundle_manifest.json`

## SSH compatibility notes

Older network appliances sometimes reject modern Paramiko defaults during key exchange negotiation. The tool includes compatibility fallbacks for legacy algorithms and surfaces a clearer diagnostic message when the SSH peer is older or incompatible.

If a device fails with an SSH handshake error, the connection logic will retry with legacy KEX fallbacks and print a more actionable explanation in verbose mode.

Per-device host-key options are also supported in the inventory (`host_key_policy`, optional `known_hosts`), so strict verification can be enabled in production; see `config/devices.yml` and `interactive_bootstrap.ps1` for examples.

## Project structure

- `app/` - CLI, collector, SSH client, vendor profiles, and detection logic
- `config/` - sample device inventory and generated runtime config
- `tests/` - regression coverage for dry-run behavior, vendor detection, and SSH compatibility
- `interactive_bootstrap.ps1` - single-command entry point for local setup and collection

## Typical workflow

1. Start the project with `interactive_bootstrap.ps1`
2. Enter the device host, username, port, and password
3. Review the generated bundle under the output directory
4. Use the AI prompt and summary files to investigate the device state

## Requirements

- Python 3.10+
- Paramiko
- PyYAML
- Windows PowerShell is used for the interactive bootstrap script, but the Python CLI itself can be run in a standard Python env
