PHASE:
PHASE-066-DeviceZipFilenameTruncationRemediation

OBJECTIVE:
Fix zip_bundle() so IP-address-named device directories (e.g. "192.168.2.241") are not truncated into a colliding zip filename (e.g. "192.168.2.zip") when packaged as field evidence.

FILES:
- app/collector.py
- tests/test_collector.py (or existing collector test module, whichever holds write_bundle/zip_bundle coverage)

ACCEPTANCE CRITERIA:
- zip_bundle() produces an archive filename that fully preserves the device directory name (e.g. "192.168.2.241.zip"), not Path.with_suffix()'s dot-based truncation.
- Regression test proves an IP-address-style device name (e.g. "192.168.2.241") produces a zip archive whose filename retains the full name.
- Regression test proves two distinct IP-named devices sharing the same first three octets (e.g. "192.168.2.241" and "192.168.2.2") produce distinct, non-colliding zip filenames.
- Existing non-IP device name zip behaviour (e.g. "sw01.example.com") is unchanged or explicitly verified.
- Full test suite passes.

CONSTRAINTS:
- Change confined to zip_bundle() (and any helper it needs) in app/collector.py.
- No changes to write_bundle()'s directory-naming behaviour (_safe_filename), summary/troubleshooting artefact generation, or provenance writing.
- No changes to orchestrator, discovery, or CLI.

KNOWN RISKS:
- None; this is a naming-only fix with no behavioural impact on collected data.

OUTSTANDING RISKS:
- None known.

OPEN QUESTIONS:
- None.
