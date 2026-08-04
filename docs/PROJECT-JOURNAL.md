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

Date: 2026-08-04
Agent: Claude

Phase: PHASE-003-VendorCommandProfiles

Changes:
- Selected Vendor Command Profiles as next implementation phase (Wishlist Phase 3).

Reason:
- PHASE-001/002 give vendor and role identity but collection still uses vendor-only command sets; role-aware profiles are the next highest-value step before topology discovery.

Risks Introduced:
- None (selection only).

Risks Resolved:
- None.

Next Recommended Action:
- Implement PHASE-003-VendorCommandProfiles.md.

---

Date: 2026-08-04
Agent: Kimi

Phase: PHASE-003-VendorCommandProfiles

Changes:
- Added optional role parameter to get_vendor_commands() with vendor-level fallback.
- Added cisco switch/router role-specific read-only command lists.
- collector.py passes device.metadata["role"]["role"] to get_vendor_commands().
- Added tests for role match, role mismatch fallback, and profile contents.

Reason:
- Execute role-appropriate collection depth using PHASE-001/002 outputs.

Risks Introduced:
- Role misclassification selects wrong profile; limited to cisco switch/router for now.

Risks Resolved:
- Vendor/role metadata no longer ignored during command selection.

Next Recommended Action:
- Review and approve DD-003; select next phase.

---

Date: 2026-08-04
Agent: Claude

Phase: PHASE-004-DeviceDiscovery

Changes:
- Selected Device Discovery as next implementation phase (Wishlist Phase 4).

Reason:
- PHASE-003 already collects CDP/LLDP raw output; parsing it into a neighbour list reduces uncertainty for the Phase 5 topology graph and Phase 6 traversal engine before any recursive connection logic is built.

Risks Introduced:
- None (selection only).

Risks Resolved:
- None.

Next Recommended Action:
- Implement PHASE-004-DeviceDiscovery.md.

---

Date: 2026-08-04
Agent: Kimi

Phase: PHASE-004-DeviceDiscovery

Changes:
- Added app/discovery.py with extract_neighbors() for CDP/LLDP raw output.
- collector.py stores discovered_neighbors in bundle.summary.
- Added tests for Cisco CDP extraction, empty fallback, and dry-run handling.

Reason:
- Convert already-collected neighbor command output into structured neighbor records.

Risks Introduced:
- Regex-based parsing may miss neighbors on non-standard output formats.

Risks Resolved:
- None.

Next Recommended Action:
- Review PHASE-004 and select next phase.

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