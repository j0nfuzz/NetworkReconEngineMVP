# Portable Windows Setup and Recovery

This guide explains how to run Network Device Diagnostics from a copied, extracted, or newly cloned repository on a Windows workstation. It is intended for technicians who do not need to manage Python virtual environments manually.

For an entirely Python-free workflow, build or download the self-contained executable described in the [Packaged executable](#packaged-executable) section.

## Before You Start

You need:

- The complete repository folder, including `interactive_bootstrap.ps1`, `requirements.txt`, and `requirements-legacy.txt`.
- Windows PowerShell.
- Python 3.12 or later, available through either the Windows `py` launcher or `python` on `PATH`.
- SSH reachability and valid credentials for the device you will collect from.

Open PowerShell in the repository root. Do not run the bootstrap from inside `.venv` or `.venv-legacy`.

## First Run on Any Workstation

Run:

```powershell
.\interactive_bootstrap.ps1
```

The bootstrap will:

1. Prompt for the device connection details.
2. Create `config\interactive_devices.yml` for the current run.
3. Find a local Python 3.12+ interpreter. It tries `py` first, then `python` from `PATH`.
4. Check the required virtual environment before using it.
5. Create or rebuild the virtual environment if required.
6. Install dependencies unless `-SkipInstall` was supplied.
7. Probe the device to select the modern or legacy SSH profile, unless a profile was forced.
8. Run collection and write output to `output` by default.

The device password is requested as a secure PowerShell prompt. The bootstrap writes a runtime inventory file so the Python CLI can perform the current collection.

## Moving the Repository to Another Computer

Copying or extracting the repository may also copy `.venv` or `.venv-legacy`. Those folders can contain references to Python installed under the previous Windows user profile.

Do not edit those paths manually. Run the bootstrap normally:

```powershell
.\interactive_bootstrap.ps1
```

Before reuse, the bootstrap checks that:

- `pyvenv.cfg` exists.
- Its `home` Python location exists.
- `Scripts\python.exe` exists.
- The venv Python runs successfully.

If a check fails, the bootstrap removes the stale environment and recreates it using Python found on the current workstation. It does this independently for `.venv` and `.venv-legacy` when each is needed.

## Repeat Runs

After dependencies have been installed successfully, avoid reinstalling them on each collection:

```powershell
.\interactive_bootstrap.ps1 -SkipInstall
```

`-SkipInstall` skips dependency installation only. Virtual-environment health checks still run, and a stale environment is still rebuilt before collection.

## SSH Profile Selection

The default profile selection is automatic:

```powershell
.\interactive_bootstrap.ps1
```

The bootstrap probes the target and uses:

- `modern` for devices that work with the normal SSH dependency profile.
- `legacy` when the probe indicates an older SSH key-exchange or SHA-1-style compatibility issue.

Force a profile only when needed for troubleshooting:

```powershell
.\interactive_bootstrap.ps1 -ParamikoProfile modern
.\interactive_bootstrap.ps1 -ParamikoProfile legacy
```

## Common Deployment Failures

### Python not found

Expected message:

```text
Python not found.
Install Python 3.12+ and ensure either:
- the `py` launcher is available
- `python` is available in PATH
The collector has not started.
```

Install Python 3.12 or later, then reopen PowerShell so the launcher or PATH is available. Run the bootstrap again.

### A copied virtual environment refers to another user profile

Symptoms may include an error referring to a Python path under another user, such as:

```text
C:\Users\<USERNAME>\AppData\Local\Programs\Python\Python312\python.exe
```

Run `interactive_bootstrap.ps1` from the repository root. The bootstrap checks the old virtual environment and recreates it when its interpreter reference is invalid. Do not modify `pyvenv.cfg` manually.

### Dependency installation fails

The bootstrap installs the requirements needed for the selected SSH profile. Confirm the workstation has network access to the configured Python package source, then run the bootstrap again without `-SkipInstall`.

### Device probe cannot connect

The bootstrap uses the modern profile when a probe cannot classify the device as legacy. Check the host address, SSH port, credentials, routing, and host-key policy. To inspect the behavior outside the interactive flow, use the direct CLI `--probe` option described in the README.

### Older device SSH handshake failure

Retry using the legacy profile:

```powershell
.\interactive_bootstrap.ps1 -ParamikoProfile legacy
```

## Output and Evidence

Output is written to `output` unless another `-OutputDir` value is supplied:

```powershell
.\interactive_bootstrap.ps1 -OutputDir D:\Diagnostics\Run-01
```

For each live-collected device, review:

- `summary.json` for device status, identity, role, collection results, and health fields.
- `troubleshooting_bundle.json` for structured health and troubleshooting analysis.
- `*.txt` files for raw command output.
- `ai_prompt.txt` for an evidence-oriented analysis prompt.
- The adjacent `.zip` file for a portable copy of the complete device bundle.

At the output root, `bundle_manifest.json` lists device bundles. CLI runs also generate topology data where applicable.

Dry runs are different: they create simulated raw command output and a raw summary, but do not produce health-scoring or troubleshooting artifacts.

## Packaged executable

A self-contained Windows executable can be produced from a source checkout using PyInstaller.

Build the executable:

```powershell
.\.venv\Scripts\python.exe -m build_portable
```

The result is written to:

```text
dist\NetworkDeviceDiagnostics.zip
```

Extract the zip on a target workstation. It does not require Python, Git, or a virtual environment.

### Interactive packaged launch

For the simplest technician workflow, launch the executable without `--config`:

```powershell
.\NetworkDeviceDiagnostics.exe --output-dir output --verbose
```

The tool prompts for:

1. Hostname or IP
2. Username
3. Password (characters are hidden)
4. SSH port (press Enter to accept `22`)
5. Vendor (press Enter to accept `auto`)

It writes the answers to a temporary runtime YAML in the system temp directory, then runs the normal collection path and deletes the file. No inventory file needs to be created beforehand.

For a dry-run validation without connecting:

```powershell
.\NetworkDeviceDiagnostics.exe --output-dir demo_output --dry-run
```

### Packaged launch with an existing inventory

If you already have a device inventory, pass `--config` as usual:

```powershell
.\NetworkDeviceDiagnostics.exe --config config\devices.yml --output-dir output --verbose
```

For a recursive run with a checkpoint file:

```powershell
.\NetworkDeviceDiagnostics.exe --config config\devices.yml --output-dir output --recursive --checkpoint-file output\checkpoint.json --verbose
```

The packaged executable bundles the same dependencies and command profiles used by the source workflow. Distributing the interactive workflow only requires placing the extracted `NetworkDeviceDiagnostics` folder and an output location on the target workstation; distributing the `--config` workflow also requires a valid `config\devices.yml`.

Some endpoint protection products may quarantine or delete unsigned executables. If the executable is removed after copying, restore it from the endpoint protection quarantine or build the package directly on the target workstation.

## Direct CLI Recovery

If you maintain an inventory file and the modern environment is healthy, run the CLI directly:

```powershell
.\.venv\Scripts\python.exe -m app.cli --config config\devices.yml --output-dir output --verbose
```

For a recursive run with a checkpoint file:

```powershell
.\.venv\Scripts\python.exe -m app.cli --config config\devices.yml --output-dir output --recursive --checkpoint-file output\checkpoint.json --verbose
```

When a direct CLI command fails because `.venv` is stale, return to the bootstrap command. It is the supported recovery path for Python interpreter and virtual-environment portability issues.