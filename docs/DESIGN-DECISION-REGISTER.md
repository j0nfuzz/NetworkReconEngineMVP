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
