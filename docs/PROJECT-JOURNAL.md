# PROJECT-JOURNAL.md

## Purpose

PROJECT-JOURNAL.md is the operational history of the project.

It is the authoritative record of:

- What changed
- Why it changed
- Risks introduced
- Risks resolved
- Recommended next actions

The journal is append-only.

Entries must never be modified after creation.

---

## Consumption Rules

Agents must:

- Read the latest 5 entries only.
- Reference prior entries by date.
- Avoid reproducing historical content.

Agents must not:

- Regenerate project state.
- Create summaries of the entire journal.
- Rewrite previous entries.

---

## Entry Format

```text
Date:
Agent:

Phase:

Changes:

Reason:

Risks Introduced:

Risks Resolved:

Next Recommended Action:
```

---

## Delta Rules

Entries must contain only:

- New work completed
- New risks discovered
- Risks resolved
- New recommendations

Do not include:

- Existing project state
- Existing design decisions
- Repeated history

---

Date: 2026-08-04
Agent: Kimi

Phase: PHASE-002A-RoleDetectionRemediation

Changes:
- app/cli.py now classifies role for every device, not only vendor="auto".
- Configured-vendor devices use a synthetic DeviceIdentity(vendor=device.vendor).
- Added tests/test_cli.py::test_configured_vendor_device_gets_role_classified.

Reason:
- Reviewer found configured-vendor devices bypassed classify_role(); acceptance criteria required role storage for all CLI paths.

Risks Introduced:
- None.

Risks Resolved:
- Configured-vendor role classification gap.

Next Recommended Action:
- Re-review PHASE-002A and DD-002.

---

## Example Entry

```text
Date: 2026-08-04
Agent: Claude

Phase: CheckpointManager

Changes:
- Selected CheckpointManager as next implementation phase.

Reason:
- Enables safe recovery of future traversal operations.

Risks Introduced:
- Concurrent checkpoint write conflicts.

Risks Resolved:
- None.

Next Recommended Action:
- Implement checkpoint persistence.
```

---

## Journal Health Rules

Keep entries concise.

Target:

- <150 tokens per entry

Use:

- Bullet points
- References
- Dates

Avoid:

- Long narratives
- Repeated context
- Restating prior decisions