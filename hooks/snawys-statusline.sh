#!/bin/bash
# Statusline badge for the snawys_law plugin.
#
# Green [SNAWYS LAW] when the plugin is live in this session, red
# [SNAWYS LAW: OFF] when it is not. The SessionStart hook stamps the current
# session id into the flag file; if the plugin is disabled that hook never
# runs, the stamp belongs to an older session, and the badge reads OFF.
#
# Wire it next to the other badges in ~/.claude/statusline-combined.sh, or on
# its own:
#   "statusLine": { "type": "command", "command": "bash /path/to/snawys-statusline.sh" }
#
# Set SNAWYS_LAW_STATUSLINE=0 to hide the badge entirely.

[ "${SNAWYS_LAW_STATUSLINE:-1}" = "0" ] && exit 0

input=$(cat)
flag="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.snawys-law-active"
session=$(printf '%s' "$input" | jq -r '.session_id // empty' 2>/dev/null | tr -cd 'A-Za-z0-9-')

# Refuse symlinks: a local attacker could point the flag at any file and have
# its bytes, escape sequences included, rendered on every keystroke.
stamp=""
if [ -f "$flag" ] && [ ! -L "$flag" ]; then
  stamp=$(head -c 64 "$flag" 2>/dev/null | tr -cd 'A-Za-z0-9-')
fi

if [ -n "$session" ] && [ "$stamp" = "$session" ]; then
  printf '\033[38;5;71m[SNAWYS LAW]\033[0m'
else
  printf '\033[38;5;131m[SNAWYS LAW: OFF]\033[0m'
fi
