# PROJECT-STANDARD.md

## Project Purpose

This project is a vendor-agnostic network diagnostics and reconnaissance platform.

Core capabilities:

- SSH device collection
- Multi-vendor support
- Device classification
- Topology discovery
- Network traversal
- Health scoring
- Structured parsing
- AI-ready troubleshooting bundles
- Recovery checkpointing

The project already exists.

The objective is controlled iteration and continuous improvement.

Not regeneration.

Not redesign.

Not rewriting.

---

# Truth Sources

Only the following are considered canonical project state:

- PROJECT-JOURNAL.md
- DESIGN-DECISION-REGISTER.md

All other information should be derived from these sources.

---

# Architectural Principles

1. Small changes over large rewrites.

2. Incremental delivery over theoretical perfection.

3. Vendor abstraction over vendor-specific implementations.

4. Structured data over raw text.

5. Graph-based topology over recursive traversal.

6. Deterministic behaviour over AI decision making.

7. Resume capability is mandatory.

8. Raw evidence must always be retained.

9. Token efficiency is a design requirement.

---

# Scope Management

Agents may:

- Implement requested work.
- Improve requested work.
- Identify risks.
- Recommend future phases.

Agents may not:

- Redesign unrelated areas.
- Rewrite large portions of the codebase.
- Remove working functionality.
- Begin future phases without instruction.
- Expand scope beyond the active phase.

---

# Governance

## Design Decision Register (DDR)

Ownership:

- Architect (Claude): Create decisions.
- Implementer (Kimi): Propose decision updates.
- Reviewer (GPT): Approve or reject decision updates.

Rules:

- All architectural decisions must be tracked in DDR.
- Proposed DDR updates must include a reason.
- Approved decisions become authoritative.
- If DDR is unchanged, output:

```text
UNCHANGED DD:[LastModified]
```

---

# Required Artefacts

## PROJECT-JOURNAL.md

Purpose:

Append-only engineering journal.

Consumption:

Read latest 5 entries only.

Update using delta entries only.

Format:

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

## DESIGN-DECISION-REGISTER.md

Purpose:

Authoritative architectural decision log.

Consumption:

Read entire register.

Should remain concise.

Format:

```text
Decision ID:
Decision:
Reason:
Status:
Approver:
Date:
```

---

# Consumption Limits

To minimise token usage:

PROJECT-JOURNAL.md

- Read latest 5 entries only.

DESIGN-DECISION-REGISTER.md

- Read entire register.

Wishlist

- Read only the current phase under discussion.

Source Code

- Read only files required for the active task.

---

# Delta-Only Mentality

Agents must output only what changed.

Avoid repeating:

- Existing state
- Existing decisions
- Existing journal entries

Use:

```text
UNCHANGED
```

where applicable.

Reference decisions by ID rather than reproducing content.

---

# Change Budget

If implementation exceeds:

- 10 files modified

OR

- 1000 lines changed

Stop.

Produce a decomposition recommendation instead.

Optimise for small reviewable changes.

---

# Output Rules

All outputs must be concise.

Use:

- Bullet points
- IDs
- References

Avoid:

- Long summaries
- Repeated context
- Regenerating existing state

All deltas should be produced in a single fenced block titled:

```text
DELTA
```

---

# Required Handover Information

Every phase handover must include:

```text
PHASE:
FILES:
ACCEPTANCE CRITERIA:
CONSTRAINTS:
KNOWN RISKS:
OUTSTANDING RISKS:
OPEN QUESTIONS:
```

Only include active and relevant information.

---

# Workflow

Claude Architect
    ↓
Phase Delta

Kimi Implementer
    ↓
Implementation Delta

GPT Reviewer
    ↓
Approved / Not Approved

Journal Update
DDR Update

Repeat

---

# Success Criteria

The workflow is considered successful when:

- State can be reconstructed from Journal + DDR.
- Architectural decisions remain traceable.
- Agents work from deltas rather than full context.
- Token usage remains predictable.
- Small implementation cycles are encouraged.
- Project progress exceeds workflow maintenance effort.