# Network Recon Engine

**Publication preparation (14 September 2026):** identifying working-tree data has been replaced with placeholders. The existing Git history and local binaries are not cleared for public release. See [SANITISATION-REPORT.md](SANITISATION-REPORT.md) before publishing or copying this folder.

**Completed AI-assisted engineering experiment; working prototype.**
PHASE-090 closes the experiment on 8 September 2026. Routine production deployment readiness is not claimed. Development is frozen in this experiment workspace; the reviewed implementation is captured with the closure documentation in the commit titled `Experiment Complete 2026-09-08`. Release tagging and hosting-side archival remain separate preparation tasks.

## Start here

| Read | Purpose |
|---|---|
| [Demonstration](DEMONSTRATION.md) | Reproduce offline behaviour, then repeat the collection workflow in an authorised lab |
| [Experiment report](EXPERIMENT-REPORT.md) | Objective, roles, evidence, findings and lessons |
| [Experiment closure](EXPERIMENT-CLOSURE.md) | Exact baseline, validation, limitations and publication review |
| [Continuation handover](CONTINUATION-HANDOVER.md) | Future repository, backlog and ownership |
| [Release notes](RELEASE_NOTES.md) | Prepared experiment release and tag recommendation |

These documents are sufficient to understand the outcome without reading the phase history.

## The experiment

The question was whether AI agents operating as **Architect, Implementer and Reviewer**, under human direction and a small documentary governance process, could incrementally deliver and validate a useful network reconnaissance prototype.

The Architect defined bounded changes and acceptance criteria. The Implementer changed code and supplied regression evidence. The Reviewer checked requirements and outputs and could reject an implementation. The project standard originally named Claude / Kimi / GPT for these roles; later records identify Terra as reviewer. Those are recorded role assignments, not an independently controlled comparison of models.

A human selected objectives, supplied access and field captures, ran deployments, clarified the real network, challenged incorrect evidence attribution and authorised closure. Runtime collection and classification are deterministic Python logic; an LLM is not required to decide which neighbour to collect. Generated prompts support subsequent human or AI analysis.

Evidence drove iteration: a field capture exposed duplicate collection of a switch under an alias. PHASE-087 stopped the duplicate but failed review because its topology edge still pointed at the alias. PHASE-087A resolved the edge to the collected node and passed review. The combined phases remain closed and DD-016 remains Approved.

## Capability and evidence

| Implemented in the working tree | Field demonstrated | Not yet validated |
|---|---|---|
| Read-only command filtering, SSH collection, vendor/platform profiles | Two distinct Aruba-CX switches produced usable evidence packages; downstream platform selection used the correct 11-command profile | Every supported vendor/version, every SSH policy or failure mode |
| LLDP/CDP parsing, classification and neighbour traversal; recursion on by default | Seed → supported neighbour → collection → evidence bundle | Complete physical inventory, the unresolved additional rack switch, deeper live traversal |
| Default credential propagation, progress callbacks, incremental raw files and bundle updates | Prior field records support these behaviours; the archive contains console and per-device evidence | Exact timing of every update cannot be established from a static ZIP |
| Identity deduplication on sequential/parallel paths and canonical topology alias edges | The supplied field archive demonstrates the original defect | No supplied post-PHASE-087A live archive; fixes are supported by approved reproduction and regression tests |
| Checkpoints, bounded concurrent target collection, health summaries, provenance, portable packaging | Portable provenance is verified for the PHASE-085 field build | Production scale, long-duration reliability and a newly packaged closure build |

Current closure validation: **354 tests passed, one established profile-fallback warning**. Passing mocked regressions is distinct from live device validation.

## Run from source

Use a working Python 3.12 installation on Windows and a fresh environment:

```powershell
py -3.12 -m venv .venv-demo
.\.venv-demo\Scripts\python.exe -m pip install -r requirements.txt
.\.venv-demo\Scripts\python.exe -m app.cli --output-dir output\lab-run --verbose
```

The last command prompts for host, username, hidden password, port and vendor, and starts a live recursive run. Only use reachable devices within an authorised lab. See [DEMONSTRATION.md](DEMONSTRATION.md) for a network-free first run and explicit lab acceptance checks.

The Python CLI's interactive inventory is temporary and supplies default credentials to discovered neighbours. With YAML, use a `default:` credentials block and exact `${ENV_VAR}` references. Per-device credentials override defaults. A missing environment variable is rejected before collection.

The separate PowerShell bootstrap supports environment recovery and SSH-profile selection, but its current generated inventory has no default credentials block. Use the direct Python CLI or an explicit inventory for the demonstrated recursive workflow.

## Run the portable build (.zip)

A pre-built Windows bundle is included at `dist\NetworkReconEngine.zip`. It embeds CPython 3.12 plus all application dependencies, so a target workstation needs **no system Python, Git, or virtual environment**.

1. Copy `dist\NetworkReconEngine.zip` to the workstation and extract it.
2. Open PowerShell inside the extracted folder and run:

   ```powershell
   .\Start_NetworkRecon.cmd --output-dir output --verbose
   ```

   If PowerShell script execution is permitted, `.\Start_NetworkRecon.ps1` accepts the same arguments. Both launchers simply run the bundled interpreter on `run_portable.py` with the arguments passed through.

Without `--config`, the tool prompts interactively for hostname or IP, username, password (hidden), SSH port (Enter accepts `22`), and vendor (Enter accepts `auto`). It writes the answers to a temporary inventory in the system temp directory, runs the collection, and deletes it.

### Recommended: always pass `--verbose`

Pass `--verbose` on every run. It prints detailed SSH and collection diagnostics to the console — per-device `Starting device:` / `Finished collection:` messages, probe errors, and the reason a collection stopped — so you can see which device is being collected, where a run is stuck, and what actually failed without opening the output folder. The same messages are always written to the run's `console.log` even without the flag, so enabling `--verbose` costs nothing and simply mirrors the log to the screen.

```powershell
.\Start_NetworkRecon.cmd --output-dir output --verbose
```

### Switches

| Switch | Effect |
|---|---|
| `--config PATH` | Use an existing YAML inventory. Omit for interactive prompts |
| `--output-dir DIR` | Output directory (default `output`) |
| `--verbose` | Print detailed SSH and collection diagnostics (recommended; see above) |
| `--dry-run` | Validate configuration and simulate collection without connecting |
| `--probe` | Check reachability and legacy/modern classification, then exit |
| `--recursive` | Backward-compatible alias — recursive discovery is already the default |
| `--no-recurse` | Flat collection of the configured devices only |
| `--target-device NAME` | Use a configured device as the traversal root; restricts scope to its topology |
| `--scope-depth N` | Topology radius for `--target-device` (default 1; no effect otherwise) |
| `--max-concurrent N` | Maximum simultaneous SSH sessions, 1–10 (default 5) |
| `--checkpoint-file PATH` | Save and resume traversal state; reuse the same inventory, output and scope |

### Inventory and examples

To use an existing inventory, create `config\devices.yml` from `config\devices.yml.example` using `<USERNAME>` / `<PASSWORD>` placeholders or `${ENV_VAR}` references (for example `${NRE_SAMPLE_CISCO_PASSWORD}`) so secrets stay out of the file, then pass it explicitly:

```powershell
.\Start_NetworkRecon.cmd --config config\devices.yml --output-dir output --verbose
```

A typical recursive run with checkpoints:

```powershell
.\Start_NetworkRecon.cmd --config config\devices.yml --output-dir output --recursive --checkpoint-file output\checkpoint.json --verbose
```

Validate without connecting:

```powershell
.\Start_NetworkRecon.cmd --output-dir demo_output --dry-run
```

Recursive discovery is the default; `--no-recurse` selects flat collection. Only use reachable devices within an authorised lab. Treat runtime inventory YAML and generated output as sensitive.

Full operations guidance — including profile selection, moved-workstation recovery and deployment troubleshooting — is in [HOWTO-PORTABLE.md](docs/HOWTO-PORTABLE.md).

The checked-in zip is the rebuilt, verified-sanitised artefact (hash and evidence in [PUBLICATION-REMEDIATION-REPORT.md](PUBLICATION-REMEDIATION-REPORT.md)). For an actual release, rebuild it from a clean committed checkout as described in [Publication builds](#publication-builds).

## Current CLI behaviour

| Invocation | Behaviour |
|---|---|
| No recursion flags | First configured device is the seed; recursive discovery is enabled |
| `--recursive` | Backward-compatible alias; recursion is already the default |
| `--no-recurse` | Flat collection of configured devices |
| `--target-device NAME` | Selects an exact configured device name as the root and uses the parallel collector |
| Target with existing `topology.json` in the output directory | Limits collection to the topology scope; `--scope-depth` defaults to 1 |
| Target without existing topology | Expands from the root through discovered supported neighbours; there is no topology radius limit |
| `--max-concurrent N` | Parallel collector clamps concurrency to 1–10; default 5. This limits simultaneous work, not total discovered devices |
| `--checkpoint-file PATH` | Saves and restores traversal state; use the same inventory, output and scope to resume |
| `--dry-run` with the default recursive path | Simulates seed commands and packaging; does not establish live discovery or collection success |

Without `--target-device`, recursive collection uses the sequential orchestrator. A supplied topology file is not required for initial discovery. `--scope-depth` does not impose a depth bound on an unscoped run.

Command-profile coverage differs from automatic neighbour classification. The classifier recognises Cisco, Aruba, FortiGate/Fortinet and Juniper markers; profile presence alone does not prove automatic traversal or live support.

## Outputs and boundaries

A live device directory contains raw command text, `summary.json`, `ai_prompt.txt`, `troubleshooting_bundle.json` and normally `build_provenance.json`. Its ZIP sits **beside** the device directory. Root `bundle_manifest.json`, `topology.json` and recursive `console.log` provide the run view. Dry runs omit health/troubleshooting analysis.

The collector filters diagnostic commands and does not intentionally change device configuration. SSH sessions still use credentials and device resources. Default host-key policy, legacy compatibility, credential storage and estate-wide operating limits need deployment-specific assessment.

Topology records observed LLDP/CDP relationships, not a complete physical inventory. Unknown or uncollected neighbours can remain edge targets without collected nodes. Alias resolution applies to the matching identities covered by PHASE-087/087A; differing management addresses can evade it.

Provenance helps attribute evidence to source. A dirty tracked diff can include sensitive text; untracked source files are not reconstructable from that diff alone. Inspect bundles before sharing.

Historical documents, tests, Git history and local archives contain sensitive-data exposure candidates. This repository is **not cleared for public publication**. The closure report records the review without reproducing identifiers. Do not distribute an existing ZIP as the closure release.

## Repository and continuation

`app/` contains the collector; `tests/` contains regressions; `config/*.example` contains inventory templates. The journal and decision register in `docs/` preserve governance history. Raw field evidence and generated outputs remain local.

[CONTINUATION-HANDOVER.md](CONTINUATION-HANDOVER.md) is the backlog entry point. PHASE-089 and PHASE-088 are deferred to a separate continuation repository; neither is active work here. Preserve this experiment as a restricted historical record, then archive it after its exact baseline has been recorded.

## Publication builds

Build public packages from a clean, committed checkout of the reviewed sanitised history. The release builder rejects dirty or unverifiable checkouts because provenance diffs can retain removed identifying data. It excludes source bytecode caches and installer launchers containing build paths. See [PUBLICATION-REMEDIATION-REPORT.md](PUBLICATION-REMEDIATION-REPORT.md) for the publication evidence and remaining boundaries.
