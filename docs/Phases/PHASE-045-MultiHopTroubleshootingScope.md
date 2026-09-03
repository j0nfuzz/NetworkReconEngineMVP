PHASE:
MultiHopTroubleshootingScope

FILES:
app/scope.py
app/cli.py
tests/test_scope.py

ACCEPTANCE CRITERIA:
- `build_troubleshooting_scope(topology, target, hops=1)` accepts an optional `hops` parameter (default `1`) that performs a breadth-first traversal out to `hops` edges from `target`, returning the deterministic sorted union of all nodes visited within that radius.
- `hops=1` (the default) preserves exactly the current single-hop behaviour (target plus direct neighbours); existing callers and existing tests that omit `hops` continue to pass unchanged.
- `hops=0` returns only `[target]`.
- `hops` values greater than 1 correctly traverse multiple edges (e.g. a 3-node chain `AP12 -> SW02 -> SW01 -> FW01` with `hops=3` from `AP12` returns all four devices), directly satisfying the Wishlist Phase 14 example.
- Unknown target device continues to return a target-only scope without raising, regardless of `hops`.
- Traversal must not revisit nodes (cycle-safe) and must terminate for topologies containing loops.
- CLI gains an optional `--scope-depth` integer argument (default `1`) that is only meaningful in combination with `--target-device`; passing `--scope-depth` without `--target-device` has no effect (mirrors existing `--target-device`-only scoping).
- `--scope-depth` is passed through to `build_troubleshooting_scope()` as `hops`.
- Add regression tests: 2-hop and 3-hop chain traversal, `hops=0`, a topology with a cycle, and CLI wiring of `--scope-depth` alongside `--target-device`.
- Full suite passes.

CONSTRAINTS:
- No new dependencies.
- Reuse the existing `topology.json` structure from PHASE-005A; no changes to its schema.
- No changes to `traverse_topology()` or `build_topology_graph()` signatures.
- No changes to checkpoint/resume JSON format.
- Preserve existing behaviour exactly when `--scope-depth` and `--target-device` are both omitted, and when only `--target-device` is supplied (default `hops=1`).
- Do not modify timeout, retry, recovery, SSH negotiation, vendor detection, collector, or provenance behaviour.
- Do not modify credential loading, substitution, or validation behaviour (app/config.py is out of scope for this phase).

KNOWN RISKS:
- Larger `hops` values on dense topologies could scope in a large fraction of the estate; this is an explicit engineer-controlled trade-off via `--scope-depth`, not a bug.

OUTSTANDING RISKS:
- DD-007 remains inconclusively validated on real hardware; timeout investigation remains parked.

OPEN QUESTIONS:
- Should a future phase cap `--scope-depth` to a configurable maximum to bound collection size on very large topologies?
