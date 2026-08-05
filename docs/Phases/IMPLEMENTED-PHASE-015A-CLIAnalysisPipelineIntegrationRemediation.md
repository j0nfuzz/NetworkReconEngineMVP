PHASE:
CLIAnalysisPipelineIntegrationRemediation

STATUS:
Implemented

FILES MODIFIED:
- app/collector.py
- app/cli.py
- tests/test_cli.py

TESTS ADDED:
- test_non_recursive_cli_writes_analysis_artifacts (updated to assert merged raw+health summary)
- test_non_recursive_dry_run_does_not_write_analysis_artifacts (updated to assert ZIP omits analysis artifacts)
- test_recursive_cli_writes_analysis_artifacts (updated to assert ZIP contains analysis artifacts)
- test_non_recursive_cli_packages_analysis_artifacts_in_zip
- test_analysis_pipeline_order_is_deterministic (relocated to app.collector pipeline)
- test_analysis_pipeline_preserves_existing_outputs

DDR UPDATES:
UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- None beyond the existing PoC risk that summary.json consumers may need to tolerate extra health keys.

RISKS RESOLVED:
- summary.json no longer overwrites the raw bundle summary; it merges health fields into the existing raw fields.
- Device ZIP archives now include summary.json (merged) and troubleshooting_bundle.json.
- Recursive, non-recursive, and dry-run paths behave correctly.

OPEN ISSUES:
- Briefing remains generic until future topology-aware/vendor-specific phases (carried from PHASE-014).
- Health thresholds and Cisco format drift remain accepted PoC risks (carried from PHASE-012/013).
