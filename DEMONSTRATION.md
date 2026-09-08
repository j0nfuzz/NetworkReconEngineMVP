# Reproducible demonstration

This guide is self-contained for a technically competent reader. It separates an offline reproduction from a live lab collection. All example names and addresses below are synthetic; `192.0.2.0/24` is a documentation range and must be replaced for live use.

## 1. Obtain the correct source and prepare Python

Use the source commit titled `Experiment Complete 2026-09-08`, which captures the reviewed PHASE-087/087A implementation and these documents. Verify it against the source fingerprint in [EXPERIMENT-CLOSURE.md](EXPERIMENT-CLOSURE.md). The earlier assessment HEAD (`33bfd97`) lacks those fixes; existing local ZIPs are not the closure release.

From the repository root in Windows PowerShell:

```powershell
py -3.12 -m venv .venv-demo
.\.venv-demo\Scripts\python.exe -m pip install -r requirements.txt
$demoPython = (Resolve-Path .venv-demo\Scripts\python.exe).Path
```

A fresh environment avoids copied virtual environments that point at another machine's interpreter. Package installation requires access to the configured package index. Dependencies use minimum versions, so this is a source reproduction, not a bit-for-bit locked environment.

## 2. Offline validation and simulated packaging

No device, live password or network access is needed after dependencies are installed. Run the existing suite with a fresh temporary directory:

```powershell
$demoTests = Join-Path 'build' ('demo-tests-' + [guid]::NewGuid().ToString('N'))
& $demoPython -m pytest -q -o addopts= --basetemp $demoTests
```

Expected on the assessed baseline: **354 passed**, one known profile-fallback warning. Tests use fixtures/mocks; they do not prove live SSH compatibility.

Create an ignored synthetic inventory:

```powershell
@'
devices:
  - name: SWITCH-01
    hostname: 192.0.2.10
    vendor: aruba
    username: DEMO-USER
    password: "<PASSWORD>"
'@ | Set-Content -Encoding UTF8 config\closure-demo.yml

$demoOutput = Join-Path 'demo_output' ('closure-' + [guid]::NewGuid().ToString('N'))
& $demoPython -m app.cli --config config\closure-demo.yml --output-dir $demoOutput --dry-run --verbose
Get-Content (Join-Path $demoOutput 'SWITCH-01\summary.json')
Get-ChildItem $demoOutput -Recurse
```

This uses the default recursive dry-run path, which skips SSH. Expect one seed with `status: dry-run-success`, simulated raw commands, `summary.json`, `ai_prompt.txt`, normal provenance unless disabled, a sibling `SWITCH-01.zip`, root manifest, topology and console log. It does not discover a second switch and does not create `troubleshooting_bundle.json` or health analysis.

## 3. Offline alias topology reproduction

The following feeds synthetic summaries through the actual topology function. It does not simulate device collection or claim to be captured field output.

```powershell
@'
import json
from app.topology import build_topology_graph

summaries = [
    {"device": "192.0.2.10", "hostname": "192.0.2.10",
     "discovered_neighbors": [{"neighbor": "SWITCH-02", "ip": "192.0.2.20"}]},
    {"device": "SWITCH-02", "hostname": "192.0.2.20",
     "discovered_neighbors": [{"neighbor": "SWITCH-01", "ip": "192.0.2.10"}]},
]
graph = build_topology_graph(summaries)
assert set(graph["nodes"]) == {"192.0.2.10", "SWITCH-02"}
assert graph["edges"][1] == {
    "source": "SWITCH-02", "target": "192.0.2.10",
    "ip": "192.0.2.10", "alias": "SWITCH-01",
}
print(json.dumps(graph["edges"], indent=2))
'@ | & $demoPython -
```

Expected output:

```json
[
  {
    "source": "192.0.2.10",
    "target": "SWITCH-02",
    "ip": "192.0.2.20"
  },
  {
    "source": "SWITCH-02",
    "target": "192.0.2.10",
    "ip": "192.0.2.10",
    "alias": "SWITCH-01"
  }
]
```

The alias has no duplicate node. Distinct, uncollected neighbours may still have raw-name edge targets; this example proves the matched-alias case only. The full suite also checks collection deduplication on both collection paths.

## 4. Repeat the collection workflow in a lab

Use two supported, SSH-reachable Aruba-CX switches on an authorised lab network. Confirm their existing LLDP advertisements include names, platform information and usable management addresses. Both switches need credentials permitting the diagnostic profile, SSH port 22 for automatically discovered neighbours, and the relevant commands for their firmware. This guide does not change network configuration.

Example topology:

```text
Collector ── SSH ── seed 192.0.2.10 (advertised name SWITCH-01)
                         │ observed LLDP link
                         └── SWITCH-02 at 192.0.2.20
                               └── LLDP back-link to SWITCH-01 / 192.0.2.10
```

Replace the example addresses with your lab addresses. Use a fresh output directory so no old topology narrows the run and no prior bundles confuse device counts. The current unscoped recursive path can expand beyond two switches, so the reachable advertised lab topology must be within the authorised collection boundary.

Prompt for credentials and create an ignored inventory that references them:

```powershell
$env:NRE_DEMO_USER = Read-Host 'Lab SSH username'
$demoCredential = Get-Credential -UserName $env:NRE_DEMO_USER -Message 'Lab SSH credentials'
$env:NRE_DEMO_PASSWORD = $demoCredential.GetNetworkCredential().Password

@'
default:
  username: ${NRE_DEMO_USER}
  password: "<PASSWORD>"
devices:
  - name: 192.0.2.10
    hostname: 192.0.2.10
    vendor: auto
    port: 22
'@ | Set-Content -Encoding UTF8 config\closure-lab.yml
```

Edit the two address values in `config/closure-lab.yml` before running. Keep the seed name equal to its management address to exercise the alternate LLDP-name back-link.

```powershell
$labOutput = Join-Path 'output' ('closure-lab-' + [guid]::NewGuid().ToString('N'))
& $demoPython -m app.cli --config config\closure-lab.yml --output-dir $labOutput --checkpoint-file (Join-Path $labOutput 'checkpoint.json') --verbose
Remove-Item Env:\NRE_DEMO_PASSWORD
Remove-Item Env:\NRE_DEMO_USER
```

During collection, inspect the console and growing raw files. On device completion, inspect the bundle, root manifest and topology updates. An interruption can be resumed with the same inventory, output directory and checkpoint after re-establishing the environment variables. Do not start a fresh output directory for a resume.

To exercise the parallel implementation in a separate lab run, add `--target-device` using the exact configured seed name and `--max-concurrent 2`. Without an existing topology this still expands to discovered neighbours; concurrency is not a total-device limit.

## 5. Inspect the result

A successful two-switch run should produce:

```text
<labOutput>/
  console.log
  checkpoint.json
  bundle_manifest.json
  topology.json
  <seed>/
    summary.json
    build_provenance.json
    ai_prompt.txt
    troubleshooting_bundle.json
    show_version.txt
    ... other raw command files ...
  <seed>.zip
  SWITCH-02/
    ... equivalent per-device artefacts ...
  SWITCH-02.zip
```

Check the following against actual files:

- Both physical switches have successful summaries, populated platform identity and no unexpected failed commands. The observed historical Aruba-CX run used 11 commands per collection; different profiles or firmware can differ.
- Raw downstream LLDP agrees with parsed neighbour records. The historical capture had four raw and four parsed entries; a different lab is not expected to reproduce that count.
- There is one collected node per matching physical identity. The downstream back-edge targets the seed's canonical name and preserves the advertised alias/address.
- Manifest entries point at usable per-device artefacts; raw outputs, prompt and troubleshooting bundle are present.
- Provenance identifies the actual code used. Inspect `head_commit_sha`, `dirty` and any recorded patch/checksum before interpreting results. Preserve raw field evidence privately.
- Observe progress and intermediate files during the run if validating streaming; a finished archive alone does not prove timing.

A sanitised summary **excerpt**, illustrating the successful profile rather than a promised full schema:

```json
{
  "device": "SWITCH-02",
  "hostname": "192.0.2.20",
  "platform": "arubaos-cx",
  "status": "collected",
  "commands_run": 11,
  "failed_commands": []
}
```

PHASE-090 reran the offline suite, dry-run packaging and alias example. Its local dry-run check set `NRE_DISABLE_PROVENANCE=1` to avoid copying a pre-existing sensitive tracked diff; the workflow above normally includes provenance. It did not perform this live lab run. The supplied historical archive proves the collection workflow before the two identity fixes, with one redundant seed-alias collection. Approved regressions/reproduction establish the fixes; a new live run is optional continuation evidence, not a reopened closure gate.

## Limitations and evidence handling

LLDP/CDP visibility is not a complete inventory. Unsupported or anonymous advertisements may not be collected. Multiple management identities, untested vendors, unavailable credentials and SSH/firmware differences can change results. The unresolved additional rack switch is continuation research, not a pass condition here.

Read-only commands still consume sessions and device resources. The default host-key policy is permissive; this demonstration does not establish a production trust policy. The PowerShell bootstrap's inventory differs from the explicit default-credentials inventory above.

Keep live output and unsanitised provenance private. The [closure review](EXPERIMENT-CLOSURE.md#sensitive-data-and-publication-review) identifies historical exposures and distribution limits. Future work starts in [CONTINUATION-HANDOVER.md](CONTINUATION-HANDOVER.md).
