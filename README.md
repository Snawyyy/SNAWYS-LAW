# snawys_law

Claude Code plugin that enforces Snawy's Law.

- `UserPromptSubmit` hook injects the answering rules and the multi-part
  work rule into every turn: a prompt asking for several changes in different
  parts of the code goes into the built-in todo list with `TaskCreate` first,
  then one task at a time, each followed by a one-line "done" message.
- `PostToolUse` hook lints every C/C++ file written or edited and exits 2 on
  a violation, so Claude has to fix it.
- `snawys-law` skill carries the full design rules for Claude to read while
  writing code.

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
python3 scripts/snawys_lint.py --self-test   # py -3 on Windows
```
