PHASE:
PHASE-067-NeighbourAddressIdentityTopologyRemediation

FILES:
app/topology.py
tests/test_discovery.py (or new tests/test_topology.py)

ACCEPTANCE CRITERIA:
- build_topology_graph() preserves each discovered neighbor's "ip" (when present) alongside its name in the resulting node/edge structure, instead of discarding it.
- Each neighbor referenced only as an edge target (not independently collected) still carries its discovered address in topology.json output.
- Regression test proves a summary with a discovered_neighbors entry containing "ip" produces a topology.json neighbor representation retaining that address, using sanitised fixture data.
- Regression test proves multiple neighbors with distinct IPs remain individually addressable (no collapsing onto the seed's identity).
- No change to node vendor/role fields or edge source/target naming semantics.
- Full test suite passes.

CONSTRAINTS:
- Change confined to app/topology.py's graph construction logic.
- No changes to app/discovery.py, app/orchestrator.py, app/classification.py, or CLI.
- No changes to which neighbors are classified/queued for collection (PHASE-065 territory, now superseded/out of scope here).

KNOWN RISKS:
- None; this is additive data retention, not a schema-breaking change if consumers already tolerate missing fields.

OUTSTANDING RISKS:
- Downstream consumers of topology.json (if any exist beyond this project) may need to be updated to read the new address field; none are known at this time.

OPEN QUESTIONS:
- None.
