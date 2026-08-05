PHASE:
CLIAnalysisPipelineIntegration

FILES:
- app/cli.py
- tests/test_cli.py

ACCEPTANCE CRITERIA:
- After a device bundle is collected (recursive or non-recursive path), the CLI calls `build_device_summary()`, then `score_device_health()` on its result, then `build_troubleshooting_bundle()` with the summary/health/raw_outputs.
- Each device's bundle output directory gains a `summary.json` (normalized summary + health score/warnings/critical) and a `troubleshooting_bundle.json` (existing bundle fields + `briefing`).
- Existing `bundle_manifest.json` and `topology.json` outputs and shapes are unchanged.
- Non-recursive and recursive CLI paths both produce the new files; dry-run mode is unaffected (no new files written).
- Add regression tests: non-recursive path writes summary/troubleshooting files, recursive path writes them per collected device, dry-run writes neither, and existing bundle_manifest/topology outputs are unchanged.

CONSTRAINTS:
- No new dependencies.
- No changes to `app/normalization.py`, `app/health.py`, or `app/troubleshooting.py` function signatures/behaviour.
- No SSH/collection logic changes; reuse `execute_device_collection()`/`run_recursive_collection()` output as-is.
- No AI/API calls.

KNOWN RISKS:
- Per-device summary/health/bundle computation adds negligible CPU cost only; no I/O beyond existing bundle-writing pattern.

OUTSTANDING RISKS:
- Fixed health thresholds, Cisco format drift, and unsupported-vendor defaults remain accepted PoC risks (carried from PHASE-012/013).
- Briefing remains generic until future vendor- or topology-aware analysis phases (carried from PHASE-014).

OPEN QUESTIONS:
- None.
