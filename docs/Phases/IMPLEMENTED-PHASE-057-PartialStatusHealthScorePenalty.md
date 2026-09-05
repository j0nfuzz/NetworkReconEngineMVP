PHASE:
PHASE-057-PartialStatusHealthScorePenalty

STATUS:
Implemented

FILES MODIFIED:
app/health.py
- Added a 15-point penalty and warning to `score_device_health()` when `summary["status"] == "partial"` or `summary.get("failed_commands")` is non-empty.
- Existing CPU (>80%), memory (>80%), and interface-error thresholds remain unchanged.
- Penalty is applied before the existing floor of `max(score, 0)`.

tests/test_health.py
- Added `test_score_device_partial_status_reduces_score`.
- Added `test_score_device_failed_commands_reduces_score`.
- Added `test_score_device_partial_with_other_issues_stacks_penalties`.
- Added `test_score_device_empty_failed_commands_list_unchanged`.

TESTS ADDED:
tests/test_health.py::test_score_device_partial_status_reduces_score
tests/test_health.py::test_score_device_failed_commands_reduces_score
tests/test_health.py::test_score_device_partial_with_other_issues_stacks_penalties
tests/test_health.py::test_score_device_empty_failed_commands_list_unchanged

DDR UPDATES:
UNCHANGED DD:2026-09-04

RISKS INTRODUCED:
- Health scores for partial/failed-command collections are now reduced; consumers that expected 100 may need adjustment.
- The 15-point penalty weight is a judgement call and may need tuning with cross-vendor field evidence.

RISKS RESOLVED:
- Partial or failed-command bundles no longer report a misleadingly perfect health score.

OPEN ISSUES:
- Penalty tuning remains empirical pending broader field evidence.
