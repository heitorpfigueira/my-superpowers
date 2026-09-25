# Dual-host compatibility implementation plan

**Spec:** ../spec/2026-09-24-dual-host-compatibility-spec.md

1. Add shared platform, Claude, Codex, and shell references under using-superpowers.
   Update skill entry points and dispatch templates to resolve operations through
   them. Retain all workflow gates and role requirements.
2. Adapt coordinator state/discovery and startup precedence. Scope cached capability
   observations correctly; update stale path and invocation assumptions.
3. Add one portable Python SDD implementation and keep Bash launchers. Verify
   fenced task extraction, complete commit-range reviews, ignored workspaces,
   ledger isolation, path validation, and plan-specific cleanup.
4. Add a preview-first installer with per-host defaults, explicit overrides,
   ownership tracking, conflict detection, update handling, and activation snippets.
   Verify in temporary destinations, including preservation of local registry data.
5. Document installation, activation, prerequisites, fallback behavior, and testing.
   Check changed local references and metadata; run the mechanics tests on Windows.
6. Inspect the final diff and apply it to the requested repository while preserving
   its pre-existing executable-bit changes. Report exact verification and remaining
   environment limits. Do not install live skills or run skill-behavior evaluations.
