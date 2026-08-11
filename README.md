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
claude --plugin-dir /mnt/DataVault/tools/snawys_law
```

## Check the checker

```bash
python3 scripts/snawys_lint.py --self-test
```
