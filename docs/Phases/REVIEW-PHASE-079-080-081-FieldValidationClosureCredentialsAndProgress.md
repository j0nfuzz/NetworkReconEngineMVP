# REVIEW-PHASE-079-080-081-FieldValidationClosureCredentialsAndProgress

REVIEW VERDICT:
Not Approved (scoped: PHASE-081 only; see per-phase dispositions below)

CRITICAL ISSUES:
None

MAJOR ISSUES:
Issue:
PHASE-081 identity progress line unconditionally reports success wording. In app/orchestrator.py, after `_probe_identity()` on a reachable `auto`/`unknown` device whose banner yields no positive-confidence identity, the emitted line is `identity resolved: vendor=auto`.

Why It Matters:
This is misleading operator output in the exact scenario the project's field history makes safety-critical: an unresolved `auto` vendor proceeds to the generic-profile path. PHASE-061A deliberately gates identity overwrite on positive confidence; the acceptance criterion requires the progress lines to be consistent with that wiring, and the implementation's own tests only cover the mutated-metadata path. An operator debugging a wrong-profile collection would trust "identity resolved" and be actively misled.

Recommended Fix:
Emit the resolved line only when identity metadata carries positive confidence (or vendor left the auto/unknown set); otherwise emit an explicit unresolved line (e.g. `identity probe: no confident match; retaining vendor=<vendor>`). Add regressions for both outcomes using a probe fake that leaves metadata unmutated.

PER-PHASE DISPOSITIONS:
- PHASE-079 field-validation closure: independently consistent with the FT060920261933 bundle record (provenance SHA 1bcd549 verified in both device bundles; capabilities and defects dispositioned correctly). Meets criteria; not reopened.
- PHASE-080: Approved-quality. Payload default block verified in diff; load_default_credentials round-trip regression present; consumer-side coverage retained (test_default_credentials_applied_to_neighbors); seed-device behaviour, temp-file lifecycle (PHASE-022 guarantees), and DD-010 surface untouched; README drift avoided. No issues.
- PHASE-081: collector progress emission, enumeration, probe-failure line, silent-when-omitted contract, conditional orchestrator forwarding (preserving positional-only patched-collector contracts), and CLI verbose wiring are all implemented and tested as recorded. One MAJOR issue above blocks approval.

VALIDATION ASSESSMENT:
- Reviewer independently re-ran the full suite: 342 passed, 1 pre-existing warning (matches implementer record).
- Reviewer inspected the unified diff: production changes limited to app/cli.py (+5/+1), app/collector.py (+14/-2), app/orchestrator.py (+12/-1), README.md (1 line). classification.py, discovery.py, topology.py, parallel_collector.py, ssh_client.py, provenance.py, checkpoint.py untouched - DO-NOT-REOPEN list respected.
- Artefacts present: findings document, PHASE/IMPLEMENTED records for 079/080/081, journal entries (Claude, Kimi).

REGRESSION ASSESSMENT:
- New modules/tests: tests/test_collector.py (4), test_orchestrator.py (+2), test_cli.py (+2). Gap: no test covers the unresolved-banner progress wording - the locus of the MAJOR issue.

CHECKPOINT ASSESSMENT:
NOT A STABLE CHECKPOINT while the MAJOR issue is open. PHASE-080 could ship independently, but the tree is committed atomically; hold the push until 081A lands.

DDR REVIEW:
UNCHANGED DD:DD-008

OUTSTANDING RISKS:
- Parallel/scoped intra-device progress deferred (documented, accepted scope).
- console.log timestamps deferred (documented open question).
- HOSTNAME-06 field re-validation pending the refreshed build.

OPEN QUESTIONS:
None

RECOMMENDED NEXT PHASE:
PHASE-081A-IdentityProbeProgressAccuracyRemediation

PUSH DECISION:
DO NOT PUSH

Reason:
PHASE-081 acceptance criterion (identity lines consistent with PHASE-061A confidence-gated wiring) is not met; one MAJOR issue open.
