PHASE:
MaxConcurrentSafetyLimit

FILES:
app/parallel_collector.py
app/cli.py
tests/test_parallel_collector.py

ACCEPTANCE CRITERIA:
- max_concurrent is clamped to a defined safe ceiling (e.g. 10) regardless of user input.
- Values below 1 remain normalized to 1 (PHASE-018A behaviour unchanged).
- --max-concurrent help text documents the ceiling.

CONSTRAINTS:
- No changes to checkpoint format, scope filtering, or asyncssh integration.
- Sequential (unscoped) path remains untouched.
- No new dependencies.

KNOWN RISKS:
- A hard ceiling may be too low for very large fault domains; ceiling value should be conservative but overridable only via future config, not this phase.

OUTSTANDING RISKS:
- Cross-workstation bootstrap validation remains pending (operational, carried forward).

OPEN QUESTIONS:
- Should the ceiling be configurable via device inventory/global config in a later phase?
