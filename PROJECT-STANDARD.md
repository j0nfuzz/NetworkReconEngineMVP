# PROJECT STANDARD

## Project Purpose

This project is a vendor-agnostic network diagnostics and reconnaissance platform.

Core capabilities:

- SSH device collection
- Multi-vendor support
- Topology discovery
- Recursive traversal
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

# Architectural Principles

1. Small changes over large rewrites.

2. Incremental delivery over theoretical perfection.

3. Vendor abstraction over vendor-specific logic.

4. Structured data over raw text.

5. Graph-based topology over recursive traversal.

6. Deterministic behaviour over AI decision making.

7. Resume capability is mandatory.

8. Raw evidence must always be retained.

---

# Scope Management

Agents may:

- Implement requested work.
- Improve requested work.
- Identify risks.

Agents may not:

- Redesign unrelated areas.
- Rewrite large portions of the codebase.
- Begin future phases without instruction.
- Remove working functionality.

---

# Change Budget

If work exceeds:

- 10 files modified
OR
- 1000 lines changed

Stop.

Recommend decomposition instead.

---

# Required Artefacts

Every agent must update:

## CURRENT-STATE-SNAPSHOT.md

Contains:

- Completed phases
- Active phases
- Outstanding phases
- Key decisions
- Risks
- Technical debt

## DESIGN-DECISION-REGISTER.md

Contains:

Decision ID:
Decision:
Reason:
Alternatives:
Status:

## PROJECT-JOURNAL.md

Append-only history.

Format:

Date:
Agent:
Phase:
Changes:
Reason:
Risks Introduced:
Risks Resolved:
Next Action:

---

# DO NOT REVISIT

Approved decisions remain final unless:

- Security risk
- Data integrity risk
- Scalability blocker
- Critical production risk

Preference is refinement, not redesign.

---

# Artefact Register

Every agent must produce:

## New Artefacts

Filename:
Purpose:
Producer:
Consumer:

## Updated Artefacts

Filename:
Purpose:

## Deprecated Artefacts

Filename:
Reason:

## Dependencies

Which future agents require which artefacts.

---

# Output Rules

All generated files must be provided as markdown content.

Never claim files were written to disk.

Never invent filesystem actions.

Always output file contents directly.

---

# Next Agent Package

Every agent must finish by generating:

```markdown
# NEXT AGENT PACKAGE

Current State Snapshot

Design Decision Register

Outstanding Risks

Outstanding Work

Relevant Artefacts

Required Inputs

Required Outputs
```

The next agent must be able to continue using only this package.
