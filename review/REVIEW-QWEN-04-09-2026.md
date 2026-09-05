# Review: Qwen Research Findings (2026-09-05)

## Evidence Reviewed

- `PROJECT-STANDARD.md`, latest five `PROJECT-JOURNAL.md` entries, and DD-001 through DD-015.
- `review/Qwen-04-09-2026.md`; Qwen's role constraints in `Prompt-Qwen-3.8-Max.md`.
- Current execution, profile, discovery, collector, health, provenance, and detection code.
- The requested `Review/Vendor-Profile-Review-04-09-2026.md` and `Review/Minimum-Diagnostic-Command-Sets-04-09-2026.md` were not present. Their apparent findings are represented in Qwen report section 14 only; no independent source citations were available for command syntax.

## Accepted Findings

- **Execution-path consistency:** accepted. Recursive target collection reaches `parallel_collector` without identity probing; its profile lookup omits platform. This bypasses DD-012's ArubaOS-CX selection.
- **ArubaOS-CX neighbour discovery:** accepted. The LLDP parser recognises `Chassis id:` and `System Name:`, not the CX `Neighbor ...` labels reported by Qwen. Real traversal remains unproven until a CX sample is parsed and field-tested.
- **Parallel evidence gap:** accepted. The parallel path does not retain the sequential path's failed-command detail, recovery state, or transport/channel evidence.
- **Generic fallback operational risk:** accepted in principle. Current code warns on fallback, so “silent fallback” is superseded; it remains a degraded collection outcome that requires recorded, operator-visible treatment.
- **Health-score blind spot:** accepted. `score_device_health()` only evaluates normalized CPU, memory, and interface errors; failed commands and partial status do not affect the score.

## Findings Requiring Validation

- ArubaOS-CX LLDP mapping and neighbour vendor classification require sanitised real output plus deterministic parser tests before any remediation is scoped.
- The loop, broadcast-storm, MAC-flap, and LACP command additions are plausible read-only diagnostic coverage, but require DD-013 evidence: authoritative command sources, regression tests, and field validation by platform/version.
- Default unbounded traversal, multi-hop expansion, checkpoint resume, and reused credentials require field validation before operational endorsement.
- Packaged-build provenance degradation to `unknown` is plausible from git-unavailable runtimes but needs a captured packaged artifact to establish current impact.

## Rejected Findings

- **FortiGate lacks a profile:** rejected as stale. A `fortigate` profile exists in the current profile table; command completeness remains unvalidated.
- **NX-OS lacks profile support:** rejected as stale. `cisco-nxos` commands and a Cisco/NX platform rule exist.
- **Generic fallback is silent:** rejected as current state. `resolve_profile_key()` emits a warning; persistence of that warning in bundle evidence is still unproven.
- Claims of production breakage, exact field-output values, and command syntax beyond the supplied report are not accepted without the cited field artifacts or vendor sources.

## Architecture Assessment

- Qwen correctly identifies cross-path divergence as the material architectural risk. It is not approval to centralise or redesign collectors.
- The platform rule table is a maintainable, deterministic extension of DD-012 for the two current rules. General rule-table expansion needs an architect-defined phase and evidence per DD-013; capability detection remains deferred.
- No DDR change is warranted by this review.

## Vendor Profile Assessment

- Current profiles improve troubleshooting breadth and retain read-only validation.
- ArubaOS-CX platform selection only improves the sequential path today; parallel/default traversal does not supply platform.
- FortiGate and NX-OS now have profile coverage, but neither should be described as field-validated.
- Static global profiles cannot substantiate per-interface counters, temporal MAC-flap/storm rates, or protocol-conditional diagnostics. These are capability limits, not safe grounds for speculative commands.

## Potential Phase Candidates

- Default-path identity and platform propagation, with path-consistency regression tests.
- ArubaOS-CX LLDP parser/classifier validation from sanitised field evidence.
- Parallel evidence-contract parity assessment.
- Partial-result health-score semantics assessment.
- Packaged-build attribution validation.

## Checkpoint Assessment

**NOT A STABLE CHECKPOINT**

The committed implementation may be a rollback point, but Qwen findings must not be treated as accepted SDLC work: the default path bypasses platform-aware selection, live neighbour expansion is unproven, and two requested source review artifacts are missing.

## Final Recommendation

Accept the evidenced execution-path, ArubaOS-CX parsing, parallel-evidence, and partial-health findings as inputs to future architectural triage. Defer command expansion and platform generalisation pending DD-013 evidence and field validation. Do not create a phase, DDR, or implementation change from this external review alone.