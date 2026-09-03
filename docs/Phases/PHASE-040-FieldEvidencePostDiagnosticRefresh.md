PHASE:
FieldEvidencePostDiagnosticRefresh

FILES:
docs/FieldEvidence/PHASE-040-<timestamp>-bundle-findings.md

ACCEPTANCE CRITERIA:
- Generate a fresh field-evidence bundle using the current approved commit (PHASE-039 merged), following the PHASE-032/034 field-capture procedure.
- Extract and document, for every command that timed out and/or recovered: elapsed_seconds, error_type, original_channel_state, original_transport_state, retry_channel_state, retry_transport_state, top-level channel_state/transport_state, recovery_successful.
- Record whether recovered-session diagnostics (post-PHASE-039) now differ observably from original-session diagnostics on real hardware.
- Record whether the timeout-then-cascade pattern (PHASE-032/034 evidence) still occurs, and if so, whether it now resolves via single-retry recovery.
- State explicitly whether DD-007 (timeout-only, single-retry recovery policy) is supported, contradicted, or inconclusive based on this evidence.
- No code changes; this is a data-collection and analysis phase only.

CONSTRAINTS:
- Do not modify app/ssh_client.py, app/collector.py, or any production code.
- Do not alter timeout values, retry policy, or recovery policy (DD-007).
- Use only the already-approved provenance mechanism (DD-008) to record the exact commit/patch state of the bundle.

KNOWN RISKS:
- Lab/field devices may not currently reproduce the original timeout-cascade conditions, yielding inconclusive evidence.
- Evidence quality depends on device availability at capture time.

OUTSTANDING RISKS:
- None beyond those already carried (diagnostic semantics validated only synthetically until this phase runs).

OPEN QUESTIONS:
- If evidence confirms DD-007 is insufficient (e.g. cascade persists beyond one retry), a follow-on remediation phase will be required.
