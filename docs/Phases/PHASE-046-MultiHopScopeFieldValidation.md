PHASE:
MultiHopScopeFieldValidation

FILES:
docs/FieldEvidence/PHASE-046-<timestamp>-bundle-findings.md

ACCEPTANCE CRITERIA:
- Run a real (or best-available reachable) recursive collection with `--target-device` and `--scope-depth` set to 2 or 3 against actual discovered topology.json output, not synthetic/mocked topology fixtures.
- Confirm the resulting `allowed_devices` scope produced by `build_troubleshooting_scope()` matches the real topology graph's multi-hop neighbours, not just the seed and its direct neighbours.
- Document the actual topology.json neighbours structure observed, the computed scope at the tested depth, and which devices were included/excluded.
- If a live multi-hop-capable topology is unreachable, explicitly document that constraint and record findings using the most recent available field topology data instead of fabricating one.
- No source code changes; this is an evidence-collection-only phase.

CONSTRAINTS:
- Do not modify app/scope.py, app/cli.py, or any other production code.
- Do not modify timeout, retry, recovery, SSH, credential, or provenance behaviour.
- Do not fabricate topology data; use genuinely discovered neighbours only.

KNOWN RISKS:
- Reachable field topology may only be 1-2 hops deep, limiting how much of the multi-hop path can be exercised.

OUTSTANDING RISKS:
- DD-007 remains inconclusively validated on real hardware; timeout investigation remains parked.
- Large `--scope-depth` values on dense topologies remain an engineer-controlled trade-off (PHASE-045).

OPEN QUESTIONS:
- Should a future phase cap `--scope-depth` to a configurable maximum to bound collection size on very large topologies?
