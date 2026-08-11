#!/bin/bash
# SessionStart hook for the snawys_law plugin.
#
# Prints the law so it loads into context, and stamps this session's id into a
# flag file so the statusline badge can tell enabled from disabled: if the
# plugin is off, this never runs, the stamp stays stale, and the badge reads
# OFF.

input=$(cat)
flag="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.snawys-law-active"
session=$(printf '%s' "$input" | jq -r '.session_id // empty' | tr -cd 'A-Za-z0-9-')

[ -n "$session" ] && printf '%s' "$session" > "$flag"

cat "${CLAUDE_PLUGIN_ROOT}/rules/answering.md" \
    "${CLAUDE_PLUGIN_ROOT}/skills/snawys-law/SKILL.md"
