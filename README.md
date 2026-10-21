# snawys_law

Codex skill and Claude Code plugin that enforce Snawy's Law.

## Codex

Install `skills/snawys-law` in the Codex skills directory. Codex loads the
rules automatically for C and C++ work.

```bash
cp -R skills/snawys-law "${CODEX_HOME:-$HOME/.codex}/skills/snawys-law"
```

Install the general answering and multi-part work rules as always-on Codex
instructions:

```bash
cp codex/AGENTS.md "${CODEX_HOME:-$HOME/.codex}/AGENTS.md"
```

The Codex skill provides agent-level enforcement. The Claude plugin below
keeps its product-specific prompt and post-edit hooks.

## Claude Code

- `SessionStart` hook injects the answering and work rules once per session
  (again after a clear or a compaction), and `SubagentStart` hands the same
  rules to each agent. They are not repeated on every prompt: that cost
  context and attention for no gain.
- `snawys-law` skill carries the C++ design rules and loads only when C++
  work starts.

## Install

```bash
claude --plugin-dir /path/to/snawys_law
```

Or as a marketplace, from a clone of this repo:

```
/plugin marketplace add /path/to/snawys_law
/plugin install snawys_law@snawys-law
```

## Statusline

Statusline badge (green when the plugin is live in this session, red when it
is not), in `settings.json`:

```json
"statusLine": {
  "type": "command",
  "command": "node \"/path/to/snawys_law/hooks/snawys.mjs\" statusline"
}
```

Set `SNAWYS_LAW_STATUSLINE=0` to hide it.

## Check the checker

```bash
node hooks/snawys.mjs --self-test
```
