# DESIGN-DECISION-REGISTER.md

## Purpose

The Design Decision Register (DDR) is the authoritative record of architectural decisions.

All significant design decisions must be tracked here.

The register should remain small, concise and easy to review.

---

## Governance

Creation:

- Claude Architect

Proposal:

- Kimi Implementer

Approval:

- GPT Reviewer

Rules:

- Kimi may propose changes.
- GPT must approve or reject proposals.
- Only approved decisions become authoritative.

---

## Consumption Rules

Agents must:

- Read the entire DDR.
- Reference decisions by ID.
- Avoid duplicating decision content.

If no changes are required, output:

```text
UNCHANGED DD:[LastModified]
```

---

## Entry Format

```text
Decision ID:
Decision:

Reason:

Status:
Proposed | Approved | Rejected

Approver:

Date:
```

---

## Example Entry

```text
Decision ID: DD-001

Decision:
Use graph-based traversal instead of recursive discovery.

Reason:
Prevents loops and simplifies checkpoint recovery.

Status:
Approved

Approver:
GPT Reviewer

Date:
2026-08-04
```

---

## Design Principles

Record decisions for:

- Architecture
- Data structures
- Traversal approaches
- Persistence mechanisms
- Vendor abstraction strategies
- Significant implementation constraints

Do not record:

- Bug fixes
- Minor refactors
- Formatting changes
- Test additions

---

## Register Health Rules

Keep entries concise.

Target:

- <50 tokens per decision update

Use:

- Decision IDs
- Short rationale
- Approval state

Avoid:

- Long discussions
- Repeating journal history
- Restating project goals

Decision ID: DD-001

Decision:
Introduce a structured DeviceIdentity returned by identify_device().

Reason:
Separate vendor detection from CLI logic and enable future role detection.

Status:
Approved

Approver:
GPT Reviewer

Date:
2026-08-04

Phase:
PHASE-001-VendorPlatformIdentity

Decision ID: DD-002

Decision:
Role classification uses deterministic hostname/model heuristics only; defer routing-table/LLDP-based inference to a later phase.

Reason:
Keeps PoC deterministic and testable, avoids new SSH commands until role-aware profiles are needed.

Status:
Approved

Approver:
GPT Reviewer

Date:
2026-08-04

Phase:
PHASE-002-RoleDetection (remediated PHASE-002A-RoleDetectionRemediation)

Decision ID: DD-003

Decision:
Extend vendor command profiles with an optional role dimension; role-unmatched vendor/role combinations fall back to the existing vendor-level profile.

Reason:
Enables role-appropriate collection depth (Wishlist Phase 3) without restructuring the existing VENDOR_PROFILES data or breaking vendor-only callers.

Status:
Approved

Approver:
GPT Reviewer

Date:
2026-08-04

Phase:
PHASE-003-VendorCommandProfiles

---

Decision ID: DD-004

Decision:
Bootstrap must discover Python via `py` launcher or PATH `python` only (no hard-coded interpreter paths), and must validate venv health (pyvenv.cfg interpreter existence and ability to execute) before reuse, recreating the venv on failure.

Reason:
Copied or synced .venv directories retain machine-specific interpreter references; folder-existence checks alone cause silent bootstrap failure on other workstations.

Status:
Approved

Approver:
GPT Reviewer

Date:
2026-08-05

Phase:
PHASE-016-BootstrapEnvironmentPortability

---

Decision ID: DD-005

Decision:
Add asyncssh as a project dependency to enable bounded concurrent SSH collection when `--target-device` scoping is active.

Reason:
Scoped parallel collection (PHASE-018) requires async concurrency; asyncssh provides an asyncio-native SSH client suitable for small, deterministic device sets.

Status:
Approved

Approver:
GPT Reviewer

Date:
2026-09-01

Phase:
PHASE-018-ParallelScopedCollection

---

Decision ID: DD-006

Decision:
Provide an opt-in legacy dependency profile for portable embedded builds via `--legacy`, installing requirements-legacy.txt instead of requirements.txt.

Reason:
Allows field-tested legacy SSH compatibility without weakening the default embedded-runtime profile.

Status:
Approved

Approver:
GPT Reviewer

Date:
2026-09-01

Phase:
PHASE-029-SSHLegacyKexPortableSupport

---

Decision ID: DD-007

Decision:
Perform exactly one reconnect and single retry on timeout failures only; do not retry ssh_exception failures.

Reason:
PHASE-032 field evidence shows an initial timeout followed by a cascade of ssh_exception failures against a dead Paramiko session. A bounded timeout-only recovery gathers evidence without masking device-side root causes or changing timeout/paging behaviour. The recovered client is adopted by the sequential collector and the obsolete client is closed exactly once; original timeout evidence is preserved separately from retry outcome.

Status:
Approved

Approver:
GPT Reviewer

Date:
2026-09-02

Phase:
PHASE-033-CommandTimeoutSessionRecovery

---

Decision ID: DD-008

Decision:
Every field-evidence collection run must automatically emit a provenance artifact containing the HEAD commit SHA and, if the working tree is dirty, the full uncommitted diff patch content plus a SHA-256 checksum of that patch.

Reason:
PHASE-034 review established that a diff fingerprint alone cannot reconstruct an uncommitted build; only durable, stored patch content is independently verifiable.

Status:
Approved

Approver:
GPT Reviewer

Date:
2026-09-03

Phase:
PHASE-035-FieldEvidenceBuildProvenance

---

Decision ID: DD-009

Decision:
Recovered-command diagnostic fields (channel_state/transport_state) must reflect the final session state after a successful retry, not the pre-retry snapshot; the pre-retry snapshot is preserved separately as original_channel_state/original_transport_state.

Reason:
The current recovery result spreads the original result first, leaving top-level channel_state/transport_state describing the dead original session even after a successful reconnect, misrepresenting which session the evidence describes.

Status:
Approved

Approver:
GPT Reviewer

Date:
2026-09-03

Phase:
PHASE-039-RecoveredSessionDiagnosticStateRefresh

---

Decision ID: DD-010

Decision:
Allow exact `${ENV_VAR}` references for credential fields in YAML configuration; resolve them before existing default-to-device credential merging. Reject any credential value that contains both `${` and `}` markers anywhere in the value unless it matches the exact valid `${ENV_VAR}` pattern for the whole value.

Reason:
Enables secret-free tracked templates while preserving current YAML configuration and deterministic device-level overrides. PHASE-044 added validation so malformed references are rejected regardless of position.

Status:
Approved

Approver:
GPT Reviewer

Date:
2026-09-03

Phase:
PHASE-044-MalformedCredentialPlaceholderDetectionRemediation

---

Decision ID: DD-011

Decision:
`build_troubleshooting_scope()` accepts an optional `hops` parameter (default `1`, preserving current behaviour) that performs bounded, cycle-safe breadth-first traversal to the requested depth; CLI exposes this as `--scope-depth`, engineer-controlled and only active alongside `--target-device`.

Reason:
Wishlist Phase 14's own worked example requires multi-hop scoping (a 3-hop device chain); single-hop scoping has been an unaddressed risk since PHASE-017. Making depth an explicit, opt-in parameter preserves default behaviour and existing tests while unlocking the required capability.

Status:
Approved

Approver:
GPT Reviewer

Date:
2026-09-03

Phase:
PHASE-045-MultiHopTroubleshootingScope

---

Decision ID: DD-012

Decision:
`get_vendor_commands()` accepts an optional `platform` parameter; when `vendor == "aruba"` and `platform` contains `"cx"` (case-insensitive), an `"aruba-cx"` command profile is selected instead of the existing generic `"aruba"` profile. `app/collector.py` supplies the already-computed `device.metadata["identity"]["platform"]` at the existing call site. Callers omitting `platform`, and all other vendors, are unaffected.

Reason:
PHASE-046 field evidence showed 5 of 10 generic `"aruba"` profile commands rejected by an ArubaOS-CX device's CLI parser while the other 5 succeeded, proving a command-syntax/profile defect rather than a vendor-detection, transport, or topology defect. Platform-aware profile selection is the minimal additive change that corrects this without touching SSH, retry, recovery, topology, provenance, or credential code.

Status:
Approved

Approver:
GPT Reviewer

Date:
2026-09-04

Phase:
PHASE-047-ArubaOSCXCommandProfileCorrection

---

Decision ID: DD-013

Decision:
Static platform-specific command-profile changes require a documented command source, deterministic regression tests, and sanitised field validation before being treated as validated beyond the observed platform/version. Runtime capability detection and command fallback remain deferred unless field evidence shows the static profile is insufficient.

Reason:
PHASE-047 corrects commands from evidence obtained on one ArubaOS-CX platform/version. This governance preserves a small, auditable profile model while preventing unsupported generalisation or speculative execution-engine changes.

Status:
Approved

Approver:
GPT Reviewer

Date:
2026-09-04

Phase:
PHASE-048-ArubaOSCXCommandProfileFieldValidation

---

Decision ID: DD-014

Decision:
`--target-device` becomes the traversal root directly without requiring a pre-existing `topology.json`; recursive collection defaults to enabled and is disabled explicitly via `--no-recurse`. The existing `--recursive` flag is retained as a backward-compatible no-op/alias.

Reason:
Field testing showed the current opt-in, topology-file-dependent recursion model does not match the project's stated goal of a single-target-to-complete-package workflow; this is the smallest change that aligns CLI defaults with that goal without altering the traversal algorithm itself.

Status:
Rejected

Approver:
GPT Reviewer

Date:
2026-09-04

Phase:
PHASE-052-AutomaticTraversalRootSelection

Rejection Reason:
The implementation constrains the no-topology target root to a fixed one-device allowed scope, so discovered neighbours cannot be traversed and DD-014's complete-package objective is not met.

---

Decision ID: DD-015

Decision:
`run_parallel_scoped_collection`/`run_parallel_scoped_collection_async` accept `allowed_devices=None` to mean unbounded neighbour discovery from the seed device, mirroring the existing `None`-handling already present in `run_recursive_collection`. `app/cli.py` passes `allowed_devices=None` for `--target-device` when no `topology.json` exists (unbounded, bounded-concurrency discovery from the target root), and continues to pass the computed hop-limited set when `topology.json` exists.

Reason:
DD-014's implementation (PHASE-052) was rejected because it passed a fixed single-device `allowed_devices` set to the parallel collector, which unconditionally rejects any device outside that set, preventing neighbour discovery. The parallel collector's `ValueError` guard against `allowed_devices=None` was an artificial restriction not present in the sequential orchestrator; relaxing it to match the sequential path's existing pattern is the smallest corrective change that restores the target-root-to-complete-package workflow without altering the traversal/BFS algorithm.

Status:
Approved

Approver:
GPT Reviewer

Date:
2026-09-04

Phase:
PHASE-053-AutomaticTraversalRootExpansionRemediation
