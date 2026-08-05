PHASE:
CLIAnalysisPipelineIntegration

STATUS:
Implemented

FILES MODIFIED:
- app/cli.py
- tests/test_cli.py

TESTS ADDED:
- test_non_recursive_cli_writes_analysis_artifacts
- test_non_recursive_dry_run_does_not_write_analysis_artifacts
- test_recursive_cli_writes_analysis_artifacts
- test_analysis_pipeline_preserves_existing_outputs
- test_analysis_pipeline_order_is_deterministic

DDR UPDATES:
UNCHANGED DD:2026-08-04

RISKS INTRODUCED:
- Summary.json now contains health_score/warnings/critical keys written by the CLI. Consumers that expect only the raw bundle summary may need to ignore extra keys.

RISKS RESOLVED:
- build_device_summary(), score_device_health(), and build_troubleshooting_bundle() are no longer unreachable from the CLI.
- End-to-end proof that normalization → health → troubleshooting executes for every collected device.

OPEN ISSUES:
- Briefing remains generic until future topology-aware/vendor-specific phases (carried from PHASE-014).
- Health thresholds and Cisco format drift remain accepted PoC risks (carried from PHASE-012/013).
