PHASE:
CredentialFileExposureRemediation

STATUS:
Implemented

FILES MODIFIED:
- .gitignore
  - Replaced specific `config/interactive_devices.yml` entry with generic `config/*.yml` ignore rule.
  - Added exception `!config/*.yml.example` so tracked example templates remain tracked.
  - Added `field_output_040/` to generated-output ignores.
- config/devices.yml.example
  - Created from previous `config/devices.yml` with all passwords replaced by `CHANGEME` placeholder.
- config/interactive_devices.yml.example
  - Created from previous `config/interactive_devices.yml` with hostname, username, and password replaced by placeholder values.
- README.md
  - Updated Option 3 to instruct copying from `config/devices.yml.example`.
  - Added note that `config/*.yml` files are gitignored to prevent credential leakage.
- config/devices.yml
  - Untracked from git (remains locally as an ignored file).
- config/interactive_devices.yml
  - Already untracked/ignored; remains locally as an ignored file.

TESTS ADDED:
- None (git/ops hygiene change; verified via git status, check-ignore, and full pytest suite).

DDR UPDATES:
UNCHANGED DD:DD-008

RISKS INTRODUCED:
- Operators must recreate local `config/*.yml` files from example templates on fresh clones.

RISKS RESOLVED:
- Prevents future commits of plaintext credentials in `config/*.yml`.

OPEN ISSUES:
- The previously committed real credential remains in prior git history; rotation and/or history purge requires separate authorization.
- DD-007 remains inconclusively validated on real hardware (carried from PHASE-040).
