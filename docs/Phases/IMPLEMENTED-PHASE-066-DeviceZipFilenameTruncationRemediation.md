PHASE: PHASE-066-DeviceZipFilenameTruncationRemediation

STATUS: Implemented

IMPLEMENTATION SUMMARY:
Updated app/collector.py::zip_bundle() to preserve the full device directory name when creating archive filenames.

Changes:
- Replaced `device_dir.with_suffix(".zip")` (which truncates dotted names like "192.168.2.241" to "192.168.2.zip") with `device_dir.parent / f"{device_dir.name}.zip"`.
- This produces archives like "192.168.2.241.zip" and prevents collisions between devices sharing the same dotted prefix (e.g. "192.168.2.2").

Added regression tests in tests/test_cli.py:
- test_zip_bundle_preserves_ip_named_directory
- test_zip_bundle_distinct_prefixes_produce_distinct_archives
- test_zip_bundle_non_ip_device_name_unchanged

VALIDATION:
- python -m py_compile app/collector.py tests/test_cli.py: passed
- pytest tests/test_cli.py -k "zip_bundle": 3 passed
- Full pytest suite: 322 passed, 1 warning

FILES CHANGED:
- app/collector.py
- tests/test_cli.py

TESTS ADDED:
- tests/test_cli.py::test_zip_bundle_preserves_ip_named_directory
- tests/test_cli.py::test_zip_bundle_distinct_prefixes_produce_distinct_archives
- tests/test_cli.py::test_zip_bundle_non_ip_device_name_unchanged

DDR UPDATES:
UNCHANGED DD:2026-09-03

RISKS INTRODUCED:
- None expected; the archive path remains in the same directory with the same extension, only the stem is fully preserved.

RISKS RESOLVED:
- IP-named device zip archives no longer collide or truncate, restoring unique artefact identity in field bundles.

OPEN ISSUES:
- None.
