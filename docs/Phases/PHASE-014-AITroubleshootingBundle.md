PHASE:
AITroubleshootingBundle

FILES:
- app/troubleshooting.py
- tests/test_troubleshooting.py

ACCEPTANCE CRITERIA:
- `build_troubleshooting_bundle(summary: dict, health: dict, raw_outputs: dict) -> dict` returns a deterministic AI-ready briefing.
- Output includes device identity, health score, warnings, critical issues, and ordered available raw-evidence command names.
- Output includes a stable plain-text briefing derived only from its inputs; no model/API invocation.
- Missing/empty inputs produce safe defaults and never mutate input dictionaries.
- Add tests for populated output, missing data, deterministic shape/order, and input immutability.

CONSTRAINTS:
- No new dependencies, AI/API calls, CLI wiring, SSH, collection, or normalization changes.
- Reuse existing normalized summary and health result shapes only.
- Retain raw evidence by reference/name only; do not duplicate command output in the briefing.

KNOWN RISKS:
- Briefing is generic until future vendor- and topology-aware analysis phases.

OUTSTANDING RISKS:
- CLI integration of normalization, health scoring, and troubleshooting output remains deferred.
- Fixed health thresholds, Cisco format drift, and unsupported-vendor defaults remain accepted PoC risks.

OPEN QUESTIONS:
- None.
