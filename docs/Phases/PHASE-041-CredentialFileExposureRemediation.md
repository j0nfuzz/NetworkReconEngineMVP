PHASE:
CredentialFileExposureRemediation

FILES:
.gitignore
config/interactive_devices.yml.example
config/devices.yml.example

ACCEPTANCE CRITERIA:
- config/interactive_devices.yml (and any file matching config/*.yml except *.example) is removed from git tracking and added to .gitignore.
- Example templates (config/*.yml.example) with placeholder credentials are committed instead.
- README updated only if it directly references the removed tracked file path.
- Git history rewrite is explicitly OUT OF SCOPE (requires separate authorized action); this phase only stops future tracking and removes secrets from the current tree.

CONSTRAINTS:
- Do not modify app/ssh_client.py, app/collector.py, timeout/retry/recovery logic, or provenance code.
- Do not rewrite git history without explicit user authorization.
- Do not commit any real credential value in the example templates.

KNOWN RISKS:
- Secret remains in prior git history until a separate, authorized history-rewrite/rotation action is taken.
- Removing the tracked file will require operators to recreate their local config from the example template.

OUTSTANDING RISKS:
- DD-007 remains inconclusively validated on real hardware (carried from PHASE-040).
- Device-side root cause of the original `show version` timeout remains unknown (carried from PHASE-034).

OPEN QUESTIONS:
- Should the exposed credential be rotated/invalidated as a separate operational action outside this repo?
- Is a git history purge (BFG/filter-repo) authorized in a future phase?
