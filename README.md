# snawys_law

Codex skill and Claude Code plugin that enforce Snawy's Law.

## Codex

Install `skills/snawys-law` in the Codex skills directory. Codex loads the
rules automatically for C and C++ work and runs the bundled linter after
editing C or C++ files.

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
- `PostToolUse` hook lints every C/C++ file written or edited and exits 2 on
  a violation, so Claude has to fix it.
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

## Windows and Linux

Every hook runs through `hooks/snawys.mjs`, so the only hard requirement is
`node`, which Claude Code already ships on. The linter needs Python and the
launcher differs per platform, so `snawys.mjs` probes `py -3`, then `python3`,
then `python`, and stays silent if none of them exist.

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
python3 skills/snawys-law/scripts/snawys_lint.py --self-test   # py -3 on Windows
```
