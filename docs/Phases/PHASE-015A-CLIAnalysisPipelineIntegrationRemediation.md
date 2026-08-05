PHASE:
CLIAnalysisPipelineIntegrationRemediation

FILES:
- app/collector.py
- app/cli.py
- tests/test_cli.py

ACCEPTANCE CRITERIA:
- summary.json retains all pre-existing raw bundle.summary fields (device, hostname, vendor, status, commands_run, failed_commands, etc.) merged with health_score/warnings/critical, rather than being replaced by the normalized analysis summary.
- The device ZIP archive contains summary.json (merged raw + health) and troubleshooting_bundle.json alongside existing artifacts.
- Non-recursive and recursive paths both produce a ZIP containing all analysis artifacts.
- Dry-run mode is unaffected: no analysis artifacts written and ZIP contents unchanged from current dry-run behaviour.
- Add regression tests: summary.json contains raw+health fields together; ZIP archive contents include summary.json and troubleshooting_bundle.json after non-dry-run collection (recursive and non-recursive); dry-run ZIP omits analysis artifacts.

CONSTRAINTS:
- No changes to app/normalization.py, app/health.py, or app/troubleshooting.py.
- No new dependencies.
- No SSH/collection logic changes.
- Preserve existing bundle_manifest.json and topology.json shapes.

KNOWN RISKS:
- Re-zipping occurs after analysis artifact writes; cost is negligible for PoC scale.

OUTSTANDING RISKS (carried):
- Fixed health thresholds, Cisco format drift, unsupported-vendor defaults, generic briefing (from PHASE-012/013/014).

OPEN QUESTIONS:
- None.
