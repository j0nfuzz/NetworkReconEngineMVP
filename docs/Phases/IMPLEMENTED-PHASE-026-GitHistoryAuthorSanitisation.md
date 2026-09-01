PHASE:
GitHistoryAuthorSanitisation

STATUS:
Prepared (rewrite not executed)

FILES ADDED:
- .mailmap
  - Maps <USERNAME> <person@example.com> to <USERNAME> <person@example.com>.
  - Non-destructive: affects `git log`/`git shortlog` display only until a rewrite is executed.
- docs/Phases/IMPLEMENTED-PHASE-026-GitHistoryAuthorSanitisation.md (this file)

VALIDATION EVIDENCE (pre-rewrite, non-destructive):
- `git shortlog -sne --all` with .mailmap present shows a single consolidated identity:
  34	<USERNAME> <person@example.com>
- `git log --all --format=%an <%ae>` (raw, mailmap not applied) confirms exactly 2 distinct raw identities across 34 commits, matching the phase file's stated 32/2 split.

TESTS ADDED:
- None (repository metadata preparation only; no application code changed).

DDR UPDATES:
UNCHANGED DD:DD-005

RISKS INTRODUCED:
- None from this preparation step. Execution of the rewrite (not performed here) carries the risks below.

RISKS RESOLVED:
- None yet; author identity in the actual commit objects is unchanged until the rewrite below is executed.

OPEN ISSUES:
- The rewrite itself has not been executed, per phase constraints. The commands below must be run manually by the repository owner, who must confirm acceptance of the force-push before proceeding.

---

EXECUTION PLAN (NOT RUN — for repository owner to execute manually)

Prerequisites:
- Install git-filter-repo: `pip install git-filter-repo` or `winget install git-filter-repo` (per your platform).
- Ensure a clean working tree (`git status` shows no pending changes) before starting.
- Ensure `.mailmap` (already added by this phase) is present at the repository root.

Step 1 — Create a full local backup (rollback point):
```
git bundle create ../NetworkReconEngine-pre-rewrite.bundle --all
git tag pre-mailmap-rewrite
```

Step 2 — Run the mailmap-based rewrite (rewrites author/committer, not tree/message content):
```
# Before running, capture the pre-rewrite commit list from the backup tag for comparison in Step 3.
git log pre-mailmap-rewrite --format="%H" > ..\before-rewrite-ids.txt

git filter-repo --mailmap .mailmap --force
```

Step 3 — Validate the rewrite before pushing:

filter-repo writes the old-to-new commit mapping to `.git/filter-repo/commit-map`.
The following validation compares every pre-rewrite commit ID with its mapped post-rewrite
commit ID to prove that count, order, author date, commit message, and tree hash are preserved.

```powershell
# 1. Load the old->new commit map.
$map = @{}
foreach ($line in Get-Content .git/filter-repo/commit-map) {
    $parts = $line -split '\s+', 2
    $map[$parts[0]] = $parts[1]
}

# 2. Commit count must be unchanged (old count vs new master count).
$beforeList = Get-Content ..\before-rewrite-ids.txt
$afterList  = git log master --format="%H"
if ($beforeList.Count -ne $afterList.Count) {
    throw "Commit count changed: $($beforeList.Count) -> $($afterList.Count)"
}

# 3. For each old commit in order, locate its mapped new commit and verify content.
for ($i = 0; $i -lt $beforeList.Count; $i++) {
    $old = $beforeList[$i]
    $new = $map[$old]

    if (-not $new) { throw "Old commit $old has no mapped new commit" }
    if ($new -ne $afterList[$i]) { throw "Commit order mismatch at position $i" }

    $oldInfo = git show -s --format="%at%n%B%n%T" $old
    $newInfo = git show -s --format="%at%n%B%n%T" $new
    if ($oldInfo -ne $newInfo) {
        throw "Commit content mismatch at position ${i}: old=$old new=$new"
    }
}

# 4. Confirm no commit on the rewritten master shows the old identity.
$authorHits  = git log master --format=%an,%ae | Select-String -Pattern "example-employer"
$committerHits = git log master --format=%cn,%ce | Select-String -Pattern "example-employer"
if ($authorHits -or $committerHits) { throw "Old identity still present in history" }

Write-Host "Validation passed: $($afterList.Count) commits rewritten, order/messages/trees preserved, no old identity found."
```

If any of the checks above throw, stop immediately. Do not proceed to Step 4; instead
restore from the backup tag or bundle (see Rollback below), correct the cause, and retry.

Step 4 — Re-add the remote (filter-repo removes it as a safety measure) and force-push:
```
git remote add origin https://github.com/<USERNAME>/NetworkReconEngine.git
git push --force origin master
git push --force origin --tags
```

Rollback (if the rewrite is found to be incorrect before or after pushing):
```
# Before pushing: restore from the local backup bundle.
git reset --hard pre-mailmap-rewrite

# If already pushed and rollback is required: restore the remote from the bundle.
git clone ../NetworkReconEngine-pre-rewrite.bundle NetworkReconEngine-restore
cd NetworkReconEngine-restore
git push --force https://github.com/<USERNAME>/NetworkReconEngine.git master
git push --force https://github.com/<USERNAME>/NetworkReconEngine.git --tags
```

Post-rewrite cleanup:
```
# Once validated and pushed successfully, the local backup bundle and tag can be
# retained indefinitely for audit purposes or removed:
git tag -d pre-mailmap-rewrite
```

IMPORTANT NOTES:
- This rewrite changes every commit hash in the repository. Any existing local clones,
  forks, or open pull requests based on the current history will become divergent and
  require a fresh clone after the force-push.
- Do not run Step 2 onward without explicit confirmation from the repository owner.
- This phase intentionally stops after adding .mailmap and this execution plan; no
  destructive command above has been run.
