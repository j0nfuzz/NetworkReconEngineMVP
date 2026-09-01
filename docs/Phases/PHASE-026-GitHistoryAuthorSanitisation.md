PHASE:
GitHistoryAuthorSanitisation

FILES:
.mailmap

ACCEPTANCE CRITERIA:
- All 34 commits show author and committer as a neutral identity (`<USERNAME>` <person@example.com>); zero commits reference jon@<USERNAME>.me or "legacy-user" afterward.
- Commit count remains 34; chronological order and all commit messages are unchanged (byte-for-byte, verified via `git log --format=%H %ad %s`).
- Tree/diff content of every commit is identical before and after rewrite (verified via `git diff <old-tag> <new-ref>` on each commit producing no output).
- Local backup/tag of the pre-rewrite history exists before the force-push, so the operation is reversible if the push is rejected or reverted upstream.

CONSTRAINTS:
- Use `git filter-repo --mailmap` (or equivalent) with a single mapping rule; do not touch commit message or tree content.
- Do not squash, drop, or reorder commits.
- Do not create a new orphan branch; rewrite the existing branch in place.
- This is a repository-history operation, not a file-content edit; run outside the normal PHASE-025 file-change workflow.

KNOWN RISKS:
- Rewriting authorship changes all commit hashes; any existing forks, clones, or open PRs against the current history will become divergent and require a fresh clone.
- Force-push to a public remote is a destructive, hard-to-reverse action against the published history; must be explicitly confirmed by the repository owner before execution.

OUTSTANDING RISKS:
- File-content blockers ("Sapphire", NetworkDeviceDiagnostics.spec local path, tracked ZIP artefacts) remain open until PHASE-025 is implemented; recommend implementing PHASE-025 first and rewriting history once, after both content and authorship fixes are ready, to avoid a second force-push.

OPEN QUESTIONS:
- Confirm the repository owner accepts commit-hash change and force-push as an acceptable one-time disruption to the public history before this phase is executed.
