PHASE:
PHASE-080-InteractiveDefaultCredentialPropagation

STATUS:
Implemented

ROOT CAUSE:
- The interactive runtime YAML built by _prompt_interactive_inventory() contained a devices block only. load_default_credentials() returned {}, so orchestrator and parallel-collector neighbour Device construction received empty username/password (orchestrator.py defaults.get(...)). HOSTNAME-06 therefore authenticated with empty credentials and failed, terminating the branch. Credentials were NOT PROPAGATED on the default interactive journey.

FILES MODIFIED:
- app/cli.py: interactive payload now includes a default block carrying the prompted username and password alongside the existing single-device entry (+5 lines).
- README.md: documents that interactive credentials are reused for discovered neighbours and that config-file users should set a default: block for recursive runs.
- tests/test_cli.py: added test_prompt_interactive_inventory_writes_default_credentials_block (runtime YAML -> load_default_credentials round-trip equals mocked prompts).

TESTS ADDED:
- tests/test_cli.py::test_prompt_interactive_inventory_writes_default_credentials_block
- Existing coverage retained: test_orchestrator.py::test_default_credentials_applied_to_neighbors (consumer side), interactive temp-file lifecycle tests (PHASE-022 guarantees).

VALIDATION:
- Full suite: 342 passed, 1 pre-existing warning.

UNIFIED DIFF SUMMARY:
- app/cli.py +5; README.md 1 line replaced; tests/test_cli.py +18. No other production files touched.

REGRESSION COVERAGE:
- Prompt flow, YAML validity, port/vendor defaults, password non-echo, temp-file cleanup tests all pass unchanged.

SCOPE CONFIRMATION:
- No changes to config resolution (DD-010 surface untouched), traversal, queueing, classification, parallel collector, SSH, or provenance. MVP candidate A only; candidate B (mid-run prompting) not implemented per Architect direction.

DDR UPDATES:
UNCHANGED DD:DD-008

RISKS INTRODUCED:
- Discovered neighbours now receive real credentials on the interactive journey (bounded by max_devices and scope rules; matches documented config-file behaviour).
- Prompted literal passwords containing both ${ and } remain subject to the existing DD-010 rejection trade-off.

RISKS RESOLVED:
- Neighbour authentication failures caused by empty propagated credentials on interactive recursive runs.

OPEN ISSUES:
- Field re-validation of the HOSTNAME-06 branch pending the next field run against a refreshed build.
