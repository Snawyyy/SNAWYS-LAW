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
python3 skills/snawys-law/scripts/snawys_lint.py --self-test
```
