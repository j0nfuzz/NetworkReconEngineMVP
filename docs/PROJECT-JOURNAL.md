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

Date: 2026-08-04
Agent: Claude

Phase: PHASE-005-TopologyGraph

Changes:
- Selected Topology Graph as next implementation phase (Wishlist Phase 5).

Reason:
- PHASE-004 now produces discovered_neighbors per device; converting that into a graph structure is required before any traversal engine (Phase 6) can operate, and needs no new collection logic.

Risks Introduced:
- None (selection only).

Risks Resolved:
- None.

Next Recommended Action:
- Implement PHASE-005-TopologyGraph.md.

---

Date: 2026-08-04
Agent: Kimi

Phase: PHASE-005-TopologyGraph

Changes:
- Added app/topology.py with build_topology_graph() consuming device summaries.
- cli.py writes topology.json alongside bundle_manifest.json.
- Added tests for connected devices, isolated node, and empty graph.

Reason:
- Convert discovered_neighbors into a deterministic graph structure for future traversal.

Risks Introduced:
- Neighbour name mismatches can produce edges to absent nodes.

Risks Resolved:
- None.

Next Recommended Action:
- Review PHASE-005 and select next phase.

---

Date: 2026-08-04
Agent: Kimi

Phase: PHASE-005A-TopologyGraphRemediation

Changes:
- Materialized `summaries` iterable to a list at the start of build_topology_graph() in app/topology.py.
- Added tests/test_cli.py::test_build_topology_graph_from_generator_produces_edges.

Reason:
- Reviewer found build_topology_graph() consumed the generator in its first pass, so cli.py's generator input produced nodes but no edges.

Risks Introduced:
- None.

Risks Resolved:
- Generator-consumption bug in topology graph construction.

Next Recommended Action:
- Re-review PHASE-005A and confirm no regressions.

---

Date: 2026-08-04
Agent: Kimi

Phase: PHASE-006-TraversalEngine

Changes:
- Added app/traversal.py with traverse_topology() for deterministic BFS.
- Added tests for linear chain, cycle prevention, branching, orphaned neighbour, single-node, and missing start.

Reason:
- PHASE-005/005A produce a correct graph; loop-safe traversal is required before Phase 7 recursive collection.

Risks Introduced:
- None.

Risks Resolved:
- None.

Next Recommended Action:
- Review PHASE-006-TraversalEngine.

---

Date: 2026-08-04
Agent: Kimi

Phase: PHASE-006A-TraversalEngineRemediation

Changes:
- Fixed `visited` ordering in app/traversal.py to use deterministic BFS order.
- Fixed missing start-node path to report all graph nodes as `pending`.
- Updated traversal tests to assert `visited` order and missing-start pending.

Reason:
- Reviewer found `visited` was returned from an unordered set and missing start reported `pending: []` despite unvisited graph nodes.

Risks Introduced:
- None.

Risks Resolved:
- Non-deterministic `visited` ordering.
- Missing start-node pending under-reporting.

Next Recommended Action:
- Re-review PHASE-006A-TraversalEngineRemediation.

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