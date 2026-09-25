# Claude Code mapping

- Load an installed skill through `Skill` when available. Otherwise read its
  SKILL.md from the session's catalog and resolve supporting files relative to it.
- The personal skills directory is normally `~/.claude/skills`. An installation
  using `CLAUDE_CONFIG_DIR` can override the configuration root; use the actual
  session catalog rather than searching an assumed folder only.
- For automatic activation, merge the installer's bootstrap block into the active
  CLAUDE.md. Explicit invocation by name also works. No custom hook is required.
- Bind worker operations to the available `Agent`/messaging/resume capabilities.
  Use their actual parameters and returned IDs. Nested workers, messaging, and
  background execution depend on the version/configuration; verify availability.
- Translate model tiers to permitted choices in this installation. Do not embed
  a fixed list of Claude models in the shared workflow.
- Default state: `<CLAUDE_CONFIG_DIR or ~/.claude>/my-superpowers`.

References checked 2026-09-24:
[skills](https://code.claude.com/docs/en/skills),
[subagents](https://code.claude.com/docs/en/sub-agents).
The running client's schemas take precedence over these example tool names.
