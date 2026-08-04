# PROJECT-JOURNAL.md

## Purpose

PROJECT-JOURNAL.md is the operational history of the project.

It is the authoritative record of:

- What changed
- Why it changed
- Risks introduced
- Risks resolved
- Recommended next actions

The journal is append-only.

Entries must never be modified after creation.

---

## Consumption Rules

Agents must:

- Read the latest 5 entries only.
- Reference prior entries by date.
- Avoid reproducing historical content.

Agents must not:

- Regenerate project state.
- Create summaries of the entire journal.
- Rewrite previous entries.

---

## Entry Format

```text
Date:
Agent:

Phase:

Changes:

Reason:

Risks Introduced:

Risks Resolved:

Next Recommended Action:
```

---

## Delta Rules

Entries must contain only:

- New work completed
- New risks discovered
- Risks resolved
- New recommendations

Do not include:

- Existing project state
- Existing design decisions
- Repeated history

---

## Example Entry

```text
Date: 2026-08-04
Agent: Claude

Phase: CheckpointManager

Changes:
- Selected CheckpointManager as next implementation phase.

Reason:
- Enables safe recovery of future traversal operations.

Risks Introduced:
- Concurrent checkpoint write conflicts.

Risks Resolved:
- None.

Next Recommended Action:
- Implement checkpoint persistence.
```

---

## Journal Health Rules

Keep entries concise.

Target:

- <150 tokens per entry

Use:

- Bullet points
- References
- Dates

Avoid:

- Long narratives
- Repeated context
- Restating prior decisions