---
name: writing-documentation
description: Use whenever project knowledge needs to be captured somewhere more durable than a conversation or a commit message - a new architectural decision, a technology choice, a business rule or use case, a new coding convention or style rule someone just settled on, or a new term that needs a shared, agreed definition. Also use during brainstorming to document scope, market/tech research, impact analysis, architecture or UI/UX exploration, and ubiquitous-language terms that came out of the design discussion. Distinct from docs/development (spec/plan/report), which record one unit of work in time - this skill covers the living reference docs in docs/ that stay current and get updated in place.
---

# Writing Documentation

## Overview

`docs/development/` (spec, plan, report) is a timeline — one dated file per unit of work, never edited again once written. `docs/` outside that folder is the opposite: a small set of living references, organized by category, that get updated in place as the project's understanding of itself changes. This skill is about the second kind.

**Announce at start:** "I'm using the writing-documentation skill to record this in the docs."

**Core principle:** If you'd have to re-derive a fact by reading code, git history, or old conversations, and it's the kind of fact that will come up again, write it down where it's organized, not where it happened.

## Categories

```
docs/
├── glossary.md          - shared vocabulary, ubiquitous language
├── architecture/         - system & software architecture, security
├── technology/           - internal tech stack and why it was chosen
├── features/              - use cases, business rules, access, UI/UX
└── coding/                - style, conventions, paradigm
```

| Category | Covers | One file per... |
|---|---|---|
| `glossary.md` | Names and terms used in the project — the ubiquitous language | the whole project (single file, one entry per term) |
| `architecture/` | System and software architecture, security | subsystem or major architectural decision |
| `technology/` | Internal tech stack, why each piece was chosen | technology or significant dependency |
| `features/` | Use cases, functionality, business rules, access rules, UI/UX, focused on behavior and intent | feature or feature area |
| `coding/` | General code styling, paradigm (declarative vs imperative, etc.), conventions | language, layer, or convention area — don't force everything into one file |

Only create a category folder when you actually have something to put in it. An empty `docs/architecture/` waiting for content is worse than no folder — it invites someone to assume it's been thought through.

## Doc Creation Template

Every file except `glossary.md` (see below) follows this shape:

```markdown
# <Title>

**Created:** YYYY-MM-DD
**Last modified:** YYYY-MM-DD

## Summary

<A few sentences - what is this, in one breath, for someone who's
never seen this project.>

## Decisions & Definitions

<The actual content: decisions made and why, definitions,
configuration, explanations. This is the section that scales with
the topic's complexity - a paragraph for something simple, several
sections with subheadings for something involved.>
```

Category-specific content goes under its own heading after that (e.g. `features/` docs add "Use Cases," "Business Rules," "Access," "UI/UX"; `architecture/` docs add "Components," "Data Flow," "Security"). Update `Last modified` every time you edit a doc's content — it's how a reader knows whether what they're looking at might be stale.

**Updating vs. creating:** check whether an existing file already covers this topic before starting a new one. A new coding convention about React components belongs in the existing `coding/frontend.md` if one exists, not in a new file that fragments the same subject across two places.

## Glossary

`docs/glossary.md` is a single running file, one entry per term, alphabetical:

```markdown
## <Term>

<Definition, in the sense this project uses it - especially where
that sense is narrower or different from the word's everyday
meaning.>
```

Add a term the moment it's coined or the moment ambiguity about it surfaces — during brainstorming when a design conversation settles on a name for a concept, or any time you notice two people (or you and your human partner) using the same word to mean slightly different things.

## When This Gets Invoked

- **From brainstorming:** design exploration often produces things worth keeping past the spec itself — market or tech research findings, an impact analysis, an architecture sketch, UI/UX exploration, new ubiquitous-language terms. Not every design needs all of these; do the ones that make sense for what's being built, and write the durable parts here (architecture findings to `architecture/`, tech evaluation to `technology/`, terms to `glossary.md`, business rules and UI/UX to `features/`). The spec itself still goes to `docs/development/spec/` — this skill captures the reference material the spec draws on, not the spec.
- **From git-branch-workflow Step 3:** before closing out a parent branch, capture any coding or styling convention that got settled during implementation and doesn't already live in `coding/`. If three child branches independently had to decide "do we use named exports or default exports here," that decision belongs in `coding/` now, so the fourth branch doesn't re-litigate it.
- **Standalone:** any time a decision gets made that the next person (or the next session of you) will need and won't be able to reconstruct from the code alone.

## What Doesn't Belong Here

- Anything that's just as clear from reading the code — don't document what good naming already says.
- Task-by-task implementation detail — that's the plan's job, in `docs/development/plan/`.
- A record of what happened in one work session — that's the report's job, in `docs/development/report/`.
