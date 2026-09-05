PHASE:
DefaultRecursivePathIdentityPropagation

FILES:
app/orchestrator.py
tests/test_orchestrator.py

ACCEPTANCE CRITERIA:
- run_recursive_collection() resolves vendor/platform/identity for devices with vendor "auto" or "unknown" before command-profile selection.
- Identity detection reuses existing identify_device() logic.
- Confidence-gated overwrite from PHASE-055A is applied: probe result only replaces existing identity when its confidence is strictly greater.
- Traversal, neighbor enqueueing, and checkpointing behaviour remain unchanged.
- parallel_collector.py and target-device behaviour are unaffected.
- Regression tests prove vendor="auto" is resolved and generic-profile fallback no longer occurs when detection succeeds.

CONSTRAINTS:
- No changes to app/collector.py, app/parallel_collector.py, app/discovery.py, app/vendor_profiles.py, app/health.py, app/ssh_client.py, or CLI argument parsing.
- No architecture redesign.
- Minimise delta; prefer reuse of PHASE-055A patterns.

KNOWN RISKS:
- Probing adds one SSH connection per auto/unknown device before collection begins; this is unavoidable without modifying collector.py.

OUTSTANDING RISKS:
- The observed "unreachable" field symptom remains a separate, uninvestigated issue outside this phase's scope.

OPEN QUESTIONS:
- None.
