PHASE:
PHASE-081A-IdentityProbeProgressAccuracyRemediation

FILES:
- app/orchestrator.py
- tests/test_orchestrator.py

ARCHITECT DISPOSITION OF TERRA FINDING:
Agree. PHASE-081's acceptance criterion requires identity-phase lines consistent with the PHASE-061/061A confidence-gated wiring; `identity resolved: vendor=auto` after an unresolved probe misrepresents state in precisely the auto-to-generic degradation scenario this project has repeatedly been harmed by in the field. Remediation is justified and narrowly scoped to the progress line.

ACCEPTANCE CRITERIA:
- After a successful (non-error) identity probe, the resolved line `[verbose] <device>: identity resolved: vendor=<vendor>` is emitted only when the probe produced a concrete identity (positive identity confidence in device metadata, or device.vendor no longer in ("auto", "unknown")).
- Otherwise an explicit unresolved line is emitted: `[verbose] <device>: identity probe: no confident match; retaining vendor=<vendor>`.
- Probe-error path wording unchanged (`identity probe failed: <error>`).
- Regression test: unrecognized banner (probe leaves vendor auto, no identity metadata) emits the unresolved line and never the resolved line.
- Regression test: confident probe (fake sets vendor and positive-confidence identity metadata) emits the resolved line with the detected vendor.
- Existing forwarding and no-callback contract tests continue to pass; full suite green.

CONSTRAINTS:
- No changes to _probe_identity() logic, confidence gating (PHASE-061/061A), traversal, queueing, classification, checkpointing, collector, CLI, or parallel path.
- app/orchestrator.py and tests/test_orchestrator.py only.

KNOWN RISKS:
- None; logging-wording accuracy only.

OUTSTANDING RISKS:
- None added; existing deferred items (parallel intra-device progress, console timestamps) unchanged.

OPEN QUESTIONS:
- None.
