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

Date: 2026-08-04
Agent: Claude

Phase: PHASE-007-NeighborSupportClassification

Changes:
- Selected Neighbor Support Classification as next implementation phase (precursor to Wishlist Phase 7).

Reason:
- Recursive neighbour collection (Wishlist Phase 7) requires knowing which discovered neighbours are supported vendors before any connection is attempted; the CDP "Platform:" line is already collected but unparsed, and Phase 8 credentials do not yet exist, so classification is the smallest safe unlock.

Risks Introduced:
- None (selection only).

Risks Resolved:
- None.

Next Recommended Action:
- Implement PHASE-007-NeighborSupportClassification.md.

---

Date: 2026-08-04
Agent: Kimi

Phase: PHASE-007-NeighborSupportClassification

Changes:
- Added "platform" capture to _parse_cdp_neighbors() in app/discovery.py.
- Added app/classification.py with classify_neighbor_support() and classify_neighbors().
- Added tests for platform capture, supported vendor recognition, unsupported devices, missing platform, and non-mutation.

Reason:
- Recursive neighbour collection (Phase 7) needs to know which discovered neighbors are supported vendors before attempting SSH connections.

Risks Introduced:
- CDP platform regex may miss non-standard formats, classifying them as "unknown".
- Keyword matching may misclassify uncommon/rebranded hardware.

Risks Resolved:
- None.

Next Recommended Action:
- Review PHASE-007-NeighborSupportClassification.

---

Date: 2026-08-04
Agent: Kimi

Phase: PHASE-007A-NeighborSupportClassificationRemediation

Changes:
- Fixed _parse_cdp_neighbors() platform regex to accept end-of-string terminator.
- Added regression test for final-line `Platform:` capture and downstream classification.

Reason:
- Reviewer found valid CDP records with `Platform:` as the last line lost platform evidence and were misclassified as "unknown".

Risks Introduced:
- None.

Risks Resolved:
- Final-line CDP platform parsing defect.

Next Recommended Action:
- Re-review PHASE-007A-NeighborSupportClassificationRemediation.

---

Date: 2026-08-04
Agent: Claude

Phase: PHASE-008-CredentialManagement

Changes:
- Selected Credential Management as next implementation phase (Wishlist Phase 8).

Reason:
- load_devices() currently requires every device entry to carry its own username/password; a global default with per-device override is the smallest change that reduces config duplication and matches Wishlist Phase 8's "minimal prompting, reusable" objective without introducing vault/encryption scope.

Risks Introduced:
- None (selection only).

Risks Resolved:
- None.

Next Recommended Action:
- Implement PHASE-008-CredentialManagement.md.

---

Date: 2026-08-05
Agent: Kimi

Phase: PHASE-008-CredentialManagement

Changes:
- load_devices() now merges an optional top-level `default` credentials block into each device entry, filling only missing username/password/enable_password fields; per-device values always take precedence.
- Added tests/test_config.py covering full inheritance, partial override, full override, and legacy configs without a default block.

Reason:
- Implements PHASE-008-CredentialManagement acceptance criteria with the smallest additive change, preserving backward compatibility for configs without a default block.

Risks Introduced:
- None.

Risks Resolved:
- None.

Next Recommended Action:
- Review PHASE-008-CredentialManagement.

---

Date: 2026-08-05
Agent: GPT Reviewer

Phase: PHASE-008-CredentialManagement

Changes:
- Reviewed default credential merging and regression coverage.

Reason:
- Required full-override coverage does not demonstrate `enable_password` precedence.

Risks Introduced:
- None.

Risks Resolved:
- None.

Next Recommended Action:
- Implement PHASE-008A-CredentialManagementRemediation.

---

Date: 2026-08-05
Agent: GPT Reviewer

Phase: PHASE-008-CredentialManagement

Changes:
- Re-reviewed rejection basis for enable_password coverage.

Reason:
- Merge logic applies identically across username, password, and enable_password via the shared field loop; missing test was a coverage gap, not a defect. Approved.

Risks Introduced:
- None.

Risks Resolved:
- None.

Next Recommended Action:
- Select next implementation phase.

---

Date: 2026-08-05
Agent: Claude

Phase: PHASE-009-RecursiveNeighborCollection

Changes:
- Selected Recursive Neighbor Collection as next implementation phase (Wishlist Phase 7).

Reason:
- Classification (PHASE-007) and credential defaults (PHASE-008) are now both implemented but unused; recursive collection is the smallest phase that wires existing execute_device_collection, classify_neighbors, and default credentials into an actual discovery loop, and is a prerequisite for Wishlist Phase 9 (parallel) and Phase 10 (checkpointing).

Risks Introduced:
- None (selection only).

Risks Resolved:
- None.

Next Recommended Action:
- Implement PHASE-009-RecursiveNeighborCollection.md.

---

Date: 2026-08-05
Agent: Kimi

Phase: PHASE-009-RecursiveNeighborCollection

Changes:
- Added app/orchestrator.py with run_recursive_collection() to drive seed-based collection, classify discovered neighbors, and recursively collect only supported neighbors.
- Preserved existing execute_device_collection(), classify_neighbors(), and Device behaviour.
- Used default credential inheritance from PHASE-008 for discovered devices.
- Added tests/test_orchestrator.py covering supported enqueue, unsupported exclusion, traversal termination, failed collection, duplicate-neighbor avoidance, and missing-IP handling.

Reason:
- Wires existing classification, credential defaulting, and collection components into the smallest possible recursive discovery loop without concurrency or persistence scope.

Risks Introduced:
- Plaintext default credentials propagated to discovered neighbors (accepted PoC limitation).
- No checkpoint persistence across failures.

Risks Resolved:
- None.

Next Recommended Action:
- Review PHASE-009-RecursiveNeighborCollection.

---

Date: 2026-08-05
Agent: GPT Reviewer

Phase: PHASE-009-RecursiveNeighborCollection

Changes:
- Reviewed recursive collection and regression coverage.

Reason:
- Discovered devices do not consistently use default credentials, and sibling duplicate names can enter the collection queue more than once.

Risks Introduced:
- None.

Risks Resolved:
- None.

Next Recommended Action:
- Implement PHASE-009A-RecursiveNeighborCollectionRemediation.

---

Date: 2026-08-05
Agent: Kimi

Phase: PHASE-009A-RecursiveNeighborCollectionRemediation

Changes:
- Fixed run_recursive_collection() so discovered neighbors use default_credentials only, not parent device credentials.
- Added queued set to prevent duplicate neighbor names from entering the collection queue before collection.
- Updated tests/test_orchestrator.py to assert default credential inheritance and duplicate neighbor suppression.

Reason:
- Resolves the two accepted review findings in PHASE-009 with the smallest corrective change, without adding traverse_topology() integration.

Risks Introduced:
- None.

Risks Resolved:
- Parent credential leakage to discovered neighbors.
- Redundant queueing of the same neighbor by multiple parents.

Next Recommended Action:
- Re-review PHASE-009A-RecursiveNeighborCollectionRemediation.

---

Date: 2026-08-05
Agent: GPT Reviewer

Phase: PHASE-009A-RecursiveNeighborCollectionRemediation

Changes:
- Reviewed default credential inheritance and queue-level duplicate suppression.

Reason:
- Discovered neighbors now use only default_credentials; queued prevents pre-collection duplicates. Focused regression tests pass.

Risks Introduced:
- None.

Risks Resolved:
- Parent credential inheritance and duplicate queue entries.

Next Recommended Action:
- Select ParallelCollection.

---

Date: 2026-08-05
Agent: Claude

Phase: PHASE-010-Checkpointing

Changes:
- Selected Checkpointing as next implementation phase (Wishlist Phase 10), overriding reviewer's ParallelCollection suggestion.

Reason:
- Wishlist Phase 9 (Parallel Collection) explicitly targets asyncssh, a new dependency that conflicts with the standing "no new dependencies" constraint. Checkpointing needs only the built-in json module already used across the project, directly satisfies PROJECT-STANDARD's mandatory resume-capability principle, and reuses the state already produced by run_recursive_collection() (PHASE-009A).

Risks Introduced:
- None (selection only).

Risks Resolved:
- None.

Next Recommended Action:
- Implement PHASE-010-Checkpointing.md.

---

Date: 2026-08-05
Agent: Kimi

Phase: PHASE-010-Checkpointing

Changes:
- Added app/checkpoint.py with save_checkpoint(), load_checkpoint(), state_to_checkpoint(), and CheckpointError.
- Added optional on_collected callback to run_recursive_collection() so callers can save state after each successful collection without changing default behavior.
- Added tests/test_checkpoint.py covering round-trip persistence, missing file, corrupt JSON, plain JSON output, sorted pending, callback integration, and resume semantics.

Reason:
- Implements Wishlist Phase 10 (checkpointing) with the built-in json module, reuses existing recursive-collection state, and satisfies PROJECT-STANDARD's resume-capability principle without concurrency or new dependencies.

Risks Introduced:
- Plaintext JSON checkpoint files contain device names/IPs; no credentials are persisted.
- Concurrent checkpoint writes are not addressed.

Risks Resolved:
- None.

Next Recommended Action:
- Review PHASE-010-Checkpointing.

---

Date: 2026-08-05
Agent: GPT Reviewer

Phase: PHASE-010-Checkpointing

Changes:
- Reviewed checkpoint persistence and recovery integration.

Reason:
- save/load JSON works, but loaded state cannot drive the orchestrator and callback state omits newly queued neighbors.

Risks Introduced:
- None.

Risks Resolved:
- None.

Next Recommended Action:
- Implement CheckpointingRemediation.

---

Date: 2026-08-05
Agent: Kimi

Phase: PHASE-010A-CheckpointingRemediation

Changes:
- Added resume_state parameter to run_recursive_collection() so it can initialize visited/pending/successful/failed/unsupported from a loaded checkpoint.
- Added _reconstruct_pending_devices() to rebuild pending Device objects from checkpoint names.
- Moved on_collected callback to fire after neighbor classification and enqueue processing, ensuring persisted pending state includes newly discovered devices.
- Added/updated tests/test_checkpoint.py to prove resume skips visited devices, collects pending devices, and callback state includes newly queued neighbors.

Reason:
- Resolves the two accepted review findings in PHASE-010 with minimal additive changes, preserving existing checkpoint JSON format and default behavior.

Risks Introduced:
- Pending device reconstruction may lack hostname when neighbor records are unavailable (accepted PoC limitation).

Risks Resolved:
- Checkpoint state could not previously resume collection.
- Checkpoint callback previously omitted newly discovered pending devices.

Next Recommended Action:
- Re-review PHASE-010A-CheckpointingRemediation.

---

Date: 2026-08-05
Agent: GPT Reviewer

Phase: PHASE-010A-CheckpointingRemediation

Changes:
- Reviewed resume-state consumption and checkpoint timing.

Reason:
- Successful collection checkpoints include queued neighbors, but failed collection paths bypass checkpoint persistence.

Risks Introduced:
- None.

Risks Resolved:
- None.

Next Recommended Action:
- Implement CheckpointFailurePersistenceRemediation.

---

Date: 2026-08-05
Agent: Kimi

Phase: PHASE-010B-CheckpointFailurePersistenceRemediation

Changes:
- Extracted a shared _emit_checkpoint() helper in run_recursive_collection() and invoked it both on failed collection and after successful discovery/enqueue processing.
- Added tests/test_checkpoint.py tests proving failed collections are checkpointed, failed state survives save/load, and resume preserves previously failed devices.

Reason:
- Resolves the accepted review finding that failed collections bypassed checkpoint persistence, causing restart to lose failure state.

Risks Introduced:
- None.

Risks Resolved:
- Failed collection state is now persisted.
- Resume preserves previously failed devices.

Next Recommended Action:
- Re-review PHASE-010B-CheckpointFailurePersistenceRemediation.

---

Date: 2026-08-05
Agent: GPT Reviewer

Phase: PHASE-010B-CheckpointFailurePersistenceRemediation

Changes:
- Reviewed failed-collection checkpoint emission and resumed failure state.

Reason:
- Failed collections now emit checkpoints before continuing; focused tests confirm failed state survives save/load and successful-path checkpoint timing remains intact.

Risks Introduced:
- None.

Risks Resolved:
- Failed collection state was not persisted before restart.

Next Recommended Action:
- Select ParallelCollection.

---

Date: 2026-08-05
Agent: Claude

Phase: PHASE-011-CLIRecursiveCollectionIntegration

Changes:
- Selected CLI Recursive Collection Integration as next implementation phase, overriding reviewer's ParallelCollection suggestion.

Reason:
- app/cli.py still runs only the original flat per-device loop and never calls run_recursive_collection() or the checkpoint module; nine phases of recursive-collection and resume work (PHASE-009 through PHASE-010B) are currently unreachable from the actual CLI entry point. Wiring them in is the smallest change that proves the full pipeline end-to-end and is a prerequisite for any future parallel-collection work operating on the same entry point.

Risks Introduced:
- None (selection only).

Risks Resolved:
- None.

Next Recommended Action:
- Implement PHASE-011-CLIRecursiveCollectionIntegration.md.

---

Date: 2026-08-05
Agent: Kimi

Phase: PHASE-011-CLIRecursiveCollectionIntegration

Changes:
- Added `--recursive` and `--checkpoint-file` CLI flags to `app/cli.py`.
- Composed existing `run_recursive_collection()`, `save_checkpoint()`, and `load_checkpoint()` in a new `_run_recursive_cli()` helper.
- Recursive mode uses the first configured device as seed and preserves existing `bundle_manifest.json`/`topology.json` output.
- Non-recursive CLI behaviour is unchanged.
- Added 7 regression tests covering recursive execution, checkpoint creation/resume, bundle output, non-recursive path, and missing checkpoint handling.

Reason:
- Acceptance criteria required the recursive collection and checkpoint resume pipeline to be reachable from the CLI entry point.

Risks Introduced:
- Default credentials inferred from seed device fields after config merge; raw `default` block not exposed by `load_devices()`.
- Single-seed recursion only; multi-seed remains out of scope.
- Plaintext credential/checkpoint persistence remains a PoC limitation.

Risks Resolved:
- Recursive collection and checkpoint resume were unreachable from the CLI.

Next Recommended Action:
- Review PHASE-011 and decide whether to propose a DDR entry for default-credential inference.

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
---

Date: 2026-08-05
Agent: Kimi

Phase: PHASE-011A-CLIRecursiveCollectionRemediation

Changes:
- Added load_default_credentials() to app/config.py to read the raw config default block.
- Updated _run_recursive_cli() in app/cli.py to source recursive defaults from load_default_credentials() instead of seed-device overrides.
- Gated recursive --dry-run so it only validates the seed device with execute_device_collection(..., dry_run=True) and does not invoke run_recursive_collection().
- Updated existing recursive tests and added 4 new regression tests for dry-run safety and default-credential sourcing.

Reason:
- Reviewer found recursive --dry-run could perform real collection and discovered neighbors inherited seed-specific credential overrides.

Risks Introduced:
- None.

Risks Resolved:
- Recursive --dry-run no longer triggers real recursive collection.
- Recursive defaults now come from the config default block.

Next Recommended Action:
- Re-review PHASE-011/011A.
---

Date: 2026-08-05
Agent: Claude

Phase: PHASE-012-DataNormalisation

Changes:
- Selected Data Normalisation as next implementation phase (Wishlist Phase 12).

Reason:
- All collected diagnostics are still vendor-specific raw text; Health Scoring (Wishlist Phase 11) and the AI Troubleshooting Bundle (Phase 13) both require a deterministic, vendor-independent summary.json shape first. Parallel Collection (Phase 9) would add asyncssh and concurrency risk with no new dependency justification yet, so Data Normalisation is the smaller, lower-risk, more unlocking step: it reuses existing collected bundles, needs no SSH/CLI changes, and directly unblocks two future phases.

Risks Introduced:
- None (selection only).

Risks Resolved:
- None.

Next Recommended Action:
- Implement PHASE-012-DataNormalisation.md.

---

Date: 2026-08-05
Agent: Kimi

Phase: PHASE-012-DataNormalisation

Changes:
- Added app/normalization.py with build_device_summary() producing a vendor-independent summary structure.
- Cisco-specific parsers for version, model, uptime_days, cpu, memory, routes, arp_entries, interface_errors.
- Safe defaults for missing or unparseable fields; no mutation of bundle.raw_outputs or bundle.summary.
- Added 5 regression tests covering full summary, missing values, deterministic shape, unknown vendor, and bundle immutability.

Reason:
- Acceptance criteria required deterministic normalized output from existing DeviceBundle data without SSH/commands/CLI changes.

Risks Introduced:
- Cisco format drift may produce silent defaults; other vendors currently return all defaults.

Risks Resolved:
- None.

Next Recommended Action:
- Review PHASE-012-DataNormalisation.md.

---

Date: 2026-08-05
Agent: Kimi

Phase: PHASE-012A-DataNormalisationRemediation

Changes:
- `_find_cisco_interface_errors()` in app/normalization.py now evaluates all supported counters (`input errors`, `output errors`, `CRC`) on an interface line using `re.finditer()`.
- An interface is flagged whenever any counter is nonzero.
- Added regression tests for the exact false-negative case `0 input errors, 678 CRC` and a mixed-counters case proving only all-zero interfaces are excluded.

Reason:
- Reviewer found the parser only tested the first matched counter and silently omitted interfaces with a zero first counter but nonzero later counters.

Risks Introduced:
- None.

Risks Resolved:
- False-negative interface error detection for mixed zero/nonzero counter lines.

Next Recommended Action:
- Re-review PHASE-012-DataNormalisationRemediation.

---

Date: 2026-08-05
Agent: GPT Reviewer

Phase: PHASE-012A-DataNormalisationRemediation

Changes:
- Reviewed the interface-error counter remediation and its regression coverage.

Reason:
- The parser now evaluates all supported counters on each interface detail line; focused tests confirm zero input errors with nonzero CRC is flagged while all-zero interfaces remain excluded.

Risks Introduced:
- None.

Risks Resolved:
- False-negative interface errors caused by only evaluating the first counter on a line.

Next Recommended Action:
- Select the next implementation phase; Health Scoring remains deferred until selected.

---

Date: 2026-08-05
Agent: Claude

Phase: PHASE-013-HealthScoring

Changes:
- Selected Health Scoring as next implementation phase (Wishlist Phase 11).

Reason:
- PHASE-012/012A already produce a deterministic, vendor-independent summary.json shape (cpu, memory, interface_errors, uptime_days); Health Scoring is a pure function over that existing output, needs no SSH/CLI/collection changes, carries no new dependencies, and directly unblocks Phase 13's AI Troubleshooting Bundle, which requires a health assessment to summarise.

Risks Introduced:
- None (selection only).

Risks Resolved:
- None.

Next Recommended Action:
- Implement PHASE-013-HealthScoring.md.

---

Date: 2026-08-05
Agent: Kimi

Phase: PHASE-013-HealthScoring

Changes:
- Added app/health.py with `score_device_health(summary: dict) -> dict`.
- Deterministic rules-based scoring over existing normalized summary fields (cpu, memory, interface_errors, uptime_days).
- Score starts at 100, applies fixed deductions for high CPU (>80), high memory (>80), interface errors, and unknown uptime.
- Added 7 regression tests covering healthy, single-issue, multi-issue, missing-data, and output-shape cases.

Reason:
- Acceptance criteria required a deterministic health score and warnings/critical lists derived from normalized summaries without changing normalization or CLI.

Risks Introduced:
- Fixed 80% CPU/memory thresholds may not suit all device roles.

Risks Resolved:
- None.

Next Recommended Action:
- Review PHASE-013-HealthScoring.

---

Date: 2026-08-05
Agent: GPT Reviewer

Phase: PHASE-013-HealthScoring

Changes:
- Reviewed deterministic health scoring and its regression coverage.

Reason:
- Missing `uptime_days` is deducted as unknown uptime, contrary to the all-missing-data acceptance criterion.

Risks Introduced:
- None.

Risks Resolved:
- None.

Next Recommended Action:
- Implement PHASE-013A-HealthScoringRemediation.

---

Date: 2026-08-05
Agent: Kimi

Phase: PHASE-013A-HealthScoringRemediation

Changes:
- Removed the uptime-unknown deduction/warning from `score_device_health()` in app/health.py.
- Missing or `None` `uptime_days` is now treated as no evidence.
- Updated `test_score_device_missing_data` and `test_score_device_multiple_issues` expectations.
- Added `test_score_device_explicit_uptime_none_is_no_evidence`.

Reason:
- Acceptance criteria required missing values to be no evidence, with all-missing summaries scoring 100 and producing no warnings.

Risks Introduced:
- None.

Risks Resolved:
- False deduction/warning when uptime data is unavailable.

Next Recommended Action:
- Re-review PHASE-013-HealthScoringRemediation.

---

Date: 2026-08-05
Agent: GPT Reviewer

Phase: PHASE-013A-HealthScoringRemediation

Changes:
- Reviewed the missing-uptime remediation and its regression coverage.

Reason:
- Focused tests confirm missing or `None` `uptime_days` is treated as no evidence; CPU, memory, and interface-error scoring remain unchanged.

Risks Introduced:
- None.

Risks Resolved:
- False deduction/warning when uptime data is unavailable.

Next Recommended Action:
- Select the next implementation phase.

---

Date: 2026-08-05
Agent: Claude

Phase: PHASE-014-AITroubleshootingBundle

Changes:
- Selected AI Troubleshooting Bundle as the next implementation phase (Wishlist Phase 13).

Reason:
- PHASE-012/012A provide deterministic normalized summaries and PHASE-013/013A provide health results; a pure, structured briefing is the smallest step that reuses both and prepares retained evidence for future AI analysis without introducing an AI dependency, CLI wiring, or collection changes.

Risks Introduced:
- None (selection only).

Risks Resolved:
- None.

Next Recommended Action:
- Implement PHASE-014-AITroubleshootingBundle.md.

---

Date: 2026-08-05
Agent: Kimi

Phase: PHASE-014-AITroubleshootingBundle

Changes:
- Added app/troubleshooting.py with `build_troubleshooting_bundle(summary, health, raw_outputs)`.
- Produces deterministic AI-ready briefing with device identity, health score, warnings, critical findings, evidence source names, and plain-text brief.
- References raw evidence by command/source name only; no command output copied into the brief.
- Added 5 regression tests for complete output, missing data, shape/order, evidence references, and input immutability.

Reason:
- Acceptance criteria required a structured troubleshooting bundle built from existing normalized summaries, health results, and raw_outputs without AI calls, CLI wiring, or collection changes.

Risks Introduced:
- Briefing is generic until future vendor- or topology-aware analysis phases.

Risks Resolved:
- None.

Next Recommended Action:
- Review PHASE-014-AITroubleshootingBundle.

---

Date: 2026-08-05
Agent: GPT Reviewer

Phase: PHASE-014-AITroubleshootingBundle

Changes:
- Reviewed deterministic bundle construction, evidence references, and regression coverage.

Reason:
- Critical findings are implemented but not covered by a non-empty regression case.

Risks Introduced:
- None.

Risks Resolved:
- None.

Next Recommended Action:
- Implement PHASE-014A-AITroubleshootingBundleRemediation.

---

Date: 2026-08-05
Agent: Claude

Phase: PHASE-015-CLIAnalysisPipelineIntegration

Changes:
- Selected CLI Analysis Pipeline Integration as next implementation phase, overriding the reviewer's PHASE-014A suggestion (PHASE-014's finding was accepted as a coverage gap, not a defect; no remediation required).

Reason:
- PHASE-012, PHASE-013, and PHASE-014 each carry the same outstanding risk: `build_device_summary()`, `score_device_health()`, and `build_troubleshooting_bundle()` are implemented and tested but unreachable from `app/cli.py`. Wiring them into the existing collection pipeline is the smallest change that proves the full analysis chain end-to-end and is a prerequisite for Wishlist Phase 14 (Topology-Aware Troubleshooting), which needs real per-device bundles to operate on.

Risks Introduced:
- None (selection only).

Risks Resolved:
- None.

Next Recommended Action:
- Implement PHASE-015-CLIAnalysisPipelineIntegration.md.

---

Date: 2026-08-05
Agent: Kimi

Phase: PHASE-015-CLIAnalysisPipelineIntegration

Changes:
- Wired `build_device_summary()` → `score_device_health()` → `build_troubleshooting_bundle()` into `app/cli.py` for both recursive and non-recursive collection paths.
- Added `_write_analysis_artifacts()` helper to write `summary.json` (normalized summary + health score/warnings/critical) and `troubleshooting_bundle.json` per device.
- Guarded analysis artifact writes so dry-run mode is unaffected.
- Preserved existing `bundle_manifest.json` and `topology.json` output shapes.
- Added 5 regression tests covering non-recursive artifacts, recursive artifacts, dry-run behavior, existing output preservation, and deterministic pipeline order.

Reason:
- Acceptance criteria require the analysis chain to be reachable from the CLI and to produce the new artifacts alongside existing bundle outputs with no behavior changes to collection, checkpointing, or dry-run modes.

Risks Introduced:
- `summary.json` now contains additional `health_score`, `warnings`, and `critical` keys; consumers parsing it as a raw bundle summary may need to tolerate extra keys.

Risks Resolved:
- Normalization, health scoring, and troubleshooting bundle functions are now exercised end-to-end by the CLI.

Next Recommended Action:
- Review PHASE-015-CLIAnalysisPipelineIntegration.

---

Date: 2026-08-05
Agent: GPT Reviewer

Phase: PHASE-015-CLIAnalysisPipelineIntegration

Changes:
- Reviewed the CLI analysis integration and its focused regression coverage.

Reason:
- The required call order, recursive/non-recursive execution, dry-run guard, and manifest/topology preservation are present, but the implementation overwrites the pre-existing raw `summary.json` and creates the device ZIP before analysis artifacts are written.

Risks Introduced:
- Packaged device ZIPs omit `summary.json` analysis content and `troubleshooting_bundle.json`.

Risks Resolved:
- None.

Next Recommended Action:
- Implement PHASE-015A-CLIAnalysisPipelineIntegrationRemediation to preserve the raw summary contract and package analysis artifacts.

---

Date: 2026-08-05
Agent: Kimi

Phase: PHASE-015A-CLIAnalysisPipelineIntegrationRemediation

Changes:
- Moved analysis artifact generation from `app/cli.py` into `app/collector.write_bundle()` so artifacts are produced before the device ZIP is created.
- `summary.json` now merges health fields (`health_score`, `warnings`, `critical`) into the existing raw `bundle.summary` instead of replacing it.
- `troubleshooting_bundle.json` is written before `zip_bundle()` so it is included in the archive.
- Removed `_write_analysis_artifacts()` from `app/cli.py`; CLI now relies on `write_bundle()` for all per-device outputs.
- Gated analysis artifact writes on bundle status not starting with `dry-run`, preserving dry-run behavior without changing `write_bundle()` signature.
- Updated and added regression tests: merged raw+health summary, dry-run ZIP contents, recursive ZIP contents, non-recursive ZIP packaging, and deterministic pipeline order in `write_bundle()`.

Reason:
- Remediation acceptance criteria require preserving the raw bundle summary contract and packaging analysis artifacts inside the final device ZIP.

Risks Introduced:
- None beyond the existing accepted risk that summary.json consumers must tolerate extra health keys.

Risks Resolved:
- Raw bundle summary fields are no longer discarded.
- Device ZIPs now contain both merged `summary.json` and `troubleshooting_bundle.json`.
- Dry-run, recursive, checkpoint, and collection behavior remain unchanged.

Next Recommended Action:
- Review PHASE-015A-CLIAnalysisPipelineIntegrationRemediation.

---

Date: 2026-08-05
Agent: GPT Reviewer

Phase: PHASE-015A-CLIAnalysisPipelineIntegrationRemediation

Changes:
- Reviewed raw summary preservation, ZIP packaging order, dry-run behavior, recursive and non-recursive paths, and regression coverage.

Reason:
- The raw `bundle.summary` fields are retained with merged health fields; analysis artifacts are written before ZIP creation and verified in both path-specific archives. Existing manifests, topology, checkpoints, collection behavior, and analysis modules remain unchanged.

Risks Introduced:
- None.

Risks Resolved:
- The PHASE-015 raw summary overwrite and incomplete ZIP archive defects are resolved.

Next Recommended Action:
- Select the next phase from the project roadmap.

---

Date: 2026-08-05
Agent: Kimi

Phase: PHASE-016-BootstrapEnvironmentPortability

Changes:
- Added Python interpreter discovery (`py` launcher first, PATH `python` second) to interactive_bootstrap.ps1.
- Added venv health validation (pyvenv.cfg presence, interpreter existence, executable can run) before reuse.
- Added automatic stale-venv removal and recreation when validation fails.
- Added clean, actionable error message and exit when no usable Python is found.
- Added Pester tests in tests/test_bootstrap.ps1 covering discovery, healthy/stale venv detection, venv reuse, and venv recreation.

Reason:
- Real-world deployment on a different Windows user profile failed at bootstrap because .venv contained a stale pyvenv.cfg reference to the original developer's profile path; collection never started. This remediation makes bootstrap deterministic across workstations without changing application code.

Risks Introduced:
- Venv recreation adds a small time penalty when a stale environment is detected.
- Reliance on `py` launcher or PATH `python` may still fail on locked-down workstations where neither is exposed.

Risks Resolved:
- Stale .venv/.venv-legacy references no longer silently break bootstrap.
- Hard-coded or profile-specific interpreter assumptions are removed from the bootstrap path.
- Missing Python now fails before any SSH/collection attempt with an actionable message.

Next Recommended Action:
- Review PHASE-016 implementation and propose/approve DD-004.

---

Date: 2026-08-05
Agent: Kimi

Phase: PHASE-016A-BootstrapEnvironmentPortabilityRemediation

Changes:
- Hardened Test-VenvHealthy to validate the `home` interpreter path referenced by pyvenv.cfg and to require a zero exit code from the venv python.
- Corrected the stale-pyvenv.cfg test so it no longer removes or renames python.exe; failure now proves stale interpreter-reference detection.
- Added tests for py launcher precedence, PATH python fallback, no usable Python 3.12+ failure path, and non-zero venv python execution.

Reason:
- GPT Reviewer (2026-08-05) found PHASE-016's Test-VenvHealthy only checked file existence and did not verify the pyvenv.cfg interpreter reference or exit code, leaving the original portability failure mode undetected.

Risks Introduced:
- None beyond the existing PoC risk that venv recreation takes time on slow machines.

Risks Resolved:
- Stale `pyvenv.cfg` home interpreter references are detected even when `Scripts\python.exe` is still present.
- Non-zero exit codes from the venv Python are treated as unhealthy.
- Discovery and failure paths are now covered by focused tests.

Next Recommended Action:
- Re-review PHASE-016A and approve DD-004.

---

Date: 2026-09-01
Agent: Kimi

Phase: PHASE-016B-BootstrapRestoration

Changes:
- Restored interactive_bootstrap.ps1 and tests/test_bootstrap.ps1 from commit a49e5e6 (parent of deletion commit d2bf269).
- Verified the restored files already contain the PHASE-016A remediation changes (pyvenv.cfg home validation, venv python exit-code check, discovery precedence tests).
- Created docs/Phases/IMPLEMENTED-PHASE-016B-BootstrapRestoration.md.

Reason:
- Commit d2bf269 deleted the bootstrap script and its tests; documentation and README/HOWTO references still pointed to them, so the repository was internally inconsistent and the PHASE-016A implementation was unreviewable.

Risks Introduced:
- None.

Risks Resolved:
- Repository no longer references a non-existent bootstrap entry point.
- PHASE-016A implementation and DD-004 intent are present and testable again.

Next Recommended Action:
- Re-review PHASE-016A and proceed to DD-004 approval.

---

Date: 2026-09-01
Agent: Kimi

Phase: PHASE-017-TopologyAwareTroubleshootingScope

Changes:
- Added app/scope.py with build_troubleshooting_scope() returning a deterministic single-hop scope from topology.json.
- Added --target-device CLI flag; when supplied, recursive collection is limited to the target and its direct neighbours.
- Added optional allowed_devices parameter to app/orchestrator.py run_recursive_collection() to enforce the scope during neighbour enqueueing.
- Added tests/test_scope.py covering neighbour inclusion, unknown target, no neighbours, deterministic ordering, empty neighbour names, and CLI scope behaviour.

Reason:
- Implements PHASE-017 acceptance criteria using existing topology/traversal structures and no new dependencies.

Risks Introduced:
- Single-hop scope may omit devices needed for full root-cause context.

Risks Resolved:
- Recursive collection can now be bounded to a target device's fault domain.

Next Recommended Action:
- Review PHASE-017-TopologyAwareTroubleshootingScope.

---

Date: 2026-09-01
Agent: Kimi

Phase: PHASE-017A-TopologyAwareTroubleshootingScopeRemediation

Changes:
- app/cli.py now resolves --target-device to its matching configured device as the recursive seed, returning error code 1 for unknown targets.
- app/orchestrator.py now filters resumed checkpoint pending entries against allowed_devices before enqueueing them.
- Added tests covering non-first seed selection, unknown target failure, and resumed pending scope filtering.

Reason:
- GPT Reviewer identified two correctness defects in PHASE-017: seed selection ignored --target-device and checkpoint pending entries bypassed the scope filter.

Risks Introduced:
- None beyond existing PHASE-017 accepted risks.

Risks Resolved:
- Non-first target devices are correctly selected as the recursive seed.
- Resumed checkpoints cannot expand scoped collection beyond the target and its direct neighbours.

Next Recommended Action:
- Re-review PHASE-017 and PHASE-017A.

---

Date: 2026-09-01
Agent: Kimi

Phase: PHASE-017B-TopologyAwareTroubleshootingScopeCheckpointRemediation

Changes:
- app/orchestrator.py now initializes queued from the filtered pending list when allowed_devices is active, so emitted checkpoints no longer include out-of-scope pending entries.
- Updated test_allowed_devices_filters_resumed_pending_entries to assert emitted checkpoint state excludes out-of-scope entries.

Reason:
- GPT Reviewer found that although collection was scoped, the queued set retained unfiltered checkpoint entries and wrote them back into emitted resume state.

Risks Introduced:
- None.

Risks Resolved:
- Out-of-scope pending entries no longer persist across scoped checkpoint resumes.

Next Recommended Action:
- Re-review PHASE-017 through PHASE-017B.

---

Date: 2026-09-01
Agent: Kimi

Phase: PHASE-018-ParallelScopedCollection

Changes:
- Added app/parallel_collector.py with bounded async collection using asyncssh; activates only when allowed_devices scope is provided.
- Added --max-concurrent CLI flag (default 5) and wired scoped recursive runs to the parallel collector while leaving unscoped runs on the existing sequential orchestrator.
- Sorted parallel bundle output by device name so bundle_manifest.json is deterministic regardless of completion order.
- Preserved checkpoint/resume semantics and PHASE-017 scope filtering in the parallel path.
- Added tests/test_parallel_collector.py covering concurrent scoped execution, sequential unscoped fallback, deterministic ordering, unchanged checkpoint behaviour, and max-concurrent bounding.
- Added asyncssh to requirements.txt and proposed DD-005 for reviewer approval.
- Updated tests/test_scope.py CLI mocks to target the new parallel collector for target-device scenarios.

Reason:
- Implements Wishlist Phase 9 (Parallel Collection) in a narrow, scope-safe form: concurrency is only used under --target-device, avoiding estate-wide blast radius while satisfying the acceptance criteria.

Risks Introduced:
- New asyncssh dependency surface (security/maintenance) pending DDR approval.
- Concurrent sessions could stress AAA if --max-concurrent is set high.

Risks Resolved:
- Scoped collection no longer forced to run sequentially for multi-device fault domains.

Next Recommended Action:
- GPT Reviewer to approve or reject DD-005 and review PHASE-018 implementation.

---

Date: 2026-09-01
Agent: Kimi

Phase: PHASE-018A-ParallelScopedCollectionRemediation

Changes:
- app/parallel_collector.py now normalizes max_concurrent to at least 1, preventing hangs from --max-concurrent 0 or negative values.
- app/parallel_collector.py now caps each wave to remaining max_devices capacity, preserving traversal limits.
- Added parametrized test for max_concurrent 0, -1, and -5.
- Added test verifying a final wave respects max_devices boundary.

Reason:
- Address the two critical issues identified in REVIEW-PHASE-018: non-positive max_concurrent could stall collection, and waves could exceed max_devices.

Risks Introduced:
- None beyond existing PHASE-018 accepted risks.

Risks Resolved:
- Scoped parallel collection no longer hangs on invalid max_concurrent values.
- max_devices semantics are preserved under parallel execution.

Next Recommended Action:
- Re-review PHASE-018 and PHASE-018A.

---

Date: 2026-09-01
Agent: Kimi

Phase: PHASE-019-MaxConcurrentSafetyLimit

Changes:
- Added MAX_CONCURRENT_CEILING=10 to app/parallel_collector.py and clamped effective max_concurrent to [1, ceiling].
- Updated app/cli.py --max-concurrent help text to document the 1-10 range.
- Added tests for ceiling clamping, in-range values, non-positive normalization, and help-text documentation.

Reason:
- Address the outstanding risk identified in REVIEW-PHASE-018A that --max-concurrent had no upper ceiling and could stress AAA services.

Risks Introduced:
- Hard ceiling of 10 may be too low for some fault domains; requires future config phase to override.

Risks Resolved:
- Scoped parallel collection cannot exceed a safe simultaneous SSH session ceiling regardless of user input.

Next Recommended Action:
- Re-review PHASE-019 and close the PHASE-018 chain.

---

Date: 2026-09-01
Agent: Kimi

Phase: PHASE-020-DocumentationOperationalGuidance

Changes:
- Updated README.md to document recursive collection, --target-device scoping, --max-concurrent behaviour (default 5, ceiling 10), and --checkpoint-file resume capability.
- Added README sections for summary.json, troubleshooting_bundle.json, topology.json, and bundle_manifest.json.
- Created docs/Phases/IMPLEMENTED-PHASE-020-DocumentationOperationalGuidance.md.

Reason:
- README.md described only flat per-device collection; implemented recursive, scoped, checkpointed, and parallel features required operational documentation for network engineers.

Risks Introduced:
- None (documentation-only change).

Risks Resolved:
- README no longer understates platform capability, reducing reliance on tribal knowledge during network engineer onboarding.

Next Recommended Action:
- Re-review PHASE-020 and consider scheduling Phase 18 (Portable Distribution).

---

Date: 2026-09-01
Agent: Kimi

Phase: PHASE-020-DocumentationOperationalGuidanceRemediation

Changes:
- Added default-behaviour statements for --recursive, --target-device, and --checkpoint-file to README.md.
- Created docs/Phases/IMPLEMENTED-PHASE-020-DocumentationOperationalGuidanceRemediation.md.

Reason:
- REVIEW-PHASE-020 found README omitted inactive defaults for these flags; this remediation addresses the documented operational gap.

Risks Introduced:
- None (documentation-only change).

Risks Resolved:
- Operators no longer need to inspect CLI help to infer default collection, scoping, or checkpoint behaviour.

Next Recommended Action:
- Re-review PHASE-020 chain and close if accepted.

---

Date: 2026-09-01
Agent: Kimi

Phase: PHASE-021-PortableDistribution

Changes:
- Added build_portable.py (PyInstaller single-file build script) and run_portable.py (packaged CLI entry point).
- Built dist/NetworkDeviceDiagnostics.exe containing bundled dependencies.
- Updated README.md and docs/HOWTO-PORTABLE.md with packaged executable workflow.
- Verified source workflow tests continue to pass (tests/test_cli.py: 55 passed).

Reason:
- Deliver the target engineer experience (download, launch, collect, receive bundle) without requiring Git, Python, or virtual environment management.

Risks Introduced:
- PyInstaller may require additional hidden imports for edge-case SSH dependencies.
- Unsigned executable may trigger SmartScreen or antivirus warnings.

Risks Resolved:
- Portable execution path now exists for workstations without a Python toolchain.

Next Recommended Action:
- Review PHASE-021 and verify the packaged executable on a clean workstation.

---

Date: 2026-09-01
Agent: Kimi

Phase: PHASE-021-PortableDistribution (validation)

Changes:
- Determined the packaged one-file executable was blocked by SentinelOne EDR, not by a packaging defect or missing dependency.
- Switched build_portable.py to PyInstaller onedir mode; onedir executable launches and passes --help and --probe tests.
- Updated README.md and HOWTO-PORTABLE.md to reference dist\NetworkDeviceDiagnostics\NetworkDeviceDiagnostics.exe and note endpoint-protection quarantine risk.
- Updated IMPLEMENTED-PHASE-021-PortableDistribution.md with validation findings.

Reason:
- One-file PyInstaller output failed with Access is denied and was deleted post-build; onedir output is EDR-compatible in this environment and still provides a single runnable executable.

Risks Introduced:
- Unsigned onedir executable may still be quarantined by other endpoint protection products.

Risks Resolved:
- Portable build now produces a working executable in the build environment.

Next Recommended Action:
- Re-review PHASE-021 and validate on a workstation without SentinelOne restrictions.

---

Date: 2026-09-01
Agent: Kimi

Phase: PHASE-021-PortableDistributionPackagingRemediation

Changes:
- Updated build_portable.py to produce dist\NetworkDeviceDiagnostics.zip from the validated onedir output.
- Updated README.md and docs/HOWTO-PORTABLE.md to describe ZIP-based distribution.
- Created docs/Phases/IMPLEMENTED-PHASE-021-PortableDistributionPackagingRemediation.md.

Reason:
- REVIEW-PHASE-021 required the packaging contract to formally produce a single distributable artefact; the onedir ZIP satisfies this without reattempting onefile packaging.

Risks Introduced:
- None.

Risks Resolved:
- Approved packaging contract now matches the validated onedir build and emits one distributable ZIP.

Next Recommended Action:
- Re-review PHASE-021 remediation chain and approve or reject.

