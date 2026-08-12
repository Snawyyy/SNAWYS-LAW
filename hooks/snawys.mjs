#!/usr/bin/env node
// Cross-platform hook entry point for the snawys_law plugin.
//
// One node process replaces bash + cat + jq + a hardcoded python3, so the same
// hooks.json works on Windows and on Linux. Node is guaranteed: Claude Code
// runs on it. Python is only needed for the linter, and the interpreter name
// differs per platform, so it is probed instead of assumed.
//
//   node snawys.mjs law           print the answering rules
//   node snawys.mjs session-start stamp the session flag, print rules + law
//   node snawys.mjs subagent      same text, wrapped for SubagentStart
//   node snawys.mjs lint          hand the PostToolUse payload to the linter
//   node snawys.mjs statusline    print the badge
//   node snawys.mjs --self-test   check the checkable parts

import { spawnSync } from 'node:child_process';
import { readFileSync, writeFileSync, lstatSync, openSync, readSync, closeSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert';

const UNSAFE_ID_CHARS = /[^A-Za-z0-9-]/g;
// Some Windows shells prepend a UTF-8 BOM when they pipe; JSON.parse chokes on it.
const LEADING_BOM = /^﻿/;
const STAMP_MAX_BYTES = 64;
const BADGE_ON = '\u001b[38;5;71m[SNAWYS LAW]\u001b[0m';
const BADGE_OFF = '\u001b[38;5;131m[SNAWYS LAW: OFF]\u001b[0m';
const STATUSLINE_DISABLED = '0';
const LINT_MISSING_EXIT = 0;
// cmd.exe and the Windows App Execution Alias both report a missing program
// this way; node itself only reports spawn errors for the alias case.
const WINDOWS_COMMAND_NOT_FOUND = 9009;
const PYTHON_CANDIDATES = [['py', '-3'], ['python3'], ['python']];
const FLAG_NAME = '.snawys-law-active';
const RULES_FILE = ['rules', 'answering.md'];
const LAW_FILE = ['skills', 'snawys-law', 'SKILL.md'];
const LINT_FILE = ['scripts', 'snawys_lint.py'];

const hooksDir = dirname(fileURLToPath(import.meta.url));
const pluginRoot = process.env.CLAUDE_PLUGIN_ROOT || dirname(hooksDir);
const configDir = process.env.CLAUDE_CONFIG_DIR || join(homedir(), '.claude');
const flagPath = join(configDir, FLAG_NAME);

function pluginFile(parts) {
  return readFileSync(join(pluginRoot, ...parts), 'utf8');
}

async function readStdin() {
  const noInput = process.stdin.isTTY === true;
  if (noInput) {
    return '';
  }
  const chunks = [];
  for await (const chunk of process.stdin) {
    chunks.push(chunk);
  }
  return Buffer.concat(chunks).toString('utf8').replace(LEADING_BOM, '');
}

// Session ids land in a file that a statusline renders on every keystroke, so
// anything that is not id-shaped is stripped rather than trusted.
function sessionIdFrom(payload) {
  try {
    const id = JSON.parse(payload).session_id;
    const isUsable = typeof id === 'string';
    return isUsable ? id.replace(UNSAFE_ID_CHARS, '') : '';
  } catch {
    return '';
  }
}

function readStamp() {
  // Refuse symlinks: a local attacker could point the flag at any file and have
  // its bytes, escape sequences included, rendered on every keystroke.
  try {
    const isRegularFile = lstatSync(flagPath).isFile();
    if (!isRegularFile) {
      return '';
    }
  } catch {
    return '';
  }
  const handle = openSync(flagPath, 'r');
  try {
    const buffer = Buffer.alloc(STAMP_MAX_BYTES);
    const read = readSync(handle, buffer, 0, STAMP_MAX_BYTES, 0);
    return buffer.toString('utf8', 0, read).replace(UNSAFE_ID_CHARS, '');
  } finally {
    closeSync(handle);
  }
}

function lawText() {
  return pluginFile(RULES_FILE) + pluginFile(LAW_FILE);
}

function runLint(payload) {
  const script = join(pluginRoot, ...LINT_FILE);
  for (const [command, ...args] of PYTHON_CANDIDATES) {
    const result = spawnSync(command, [...args, script], { input: payload, encoding: 'utf8' });
    const interpreterMissing =
      result.error !== undefined || result.status === WINDOWS_COMMAND_NOT_FOUND;
    if (interpreterMissing) {
      continue;
    }
    process.stdout.write(result.stdout || '');
    process.stderr.write(result.stderr || '');
    return result.status ?? LINT_MISSING_EXIT;
  }
  // No python anywhere: stay quiet rather than fail every Write and Edit.
  return LINT_MISSING_EXIT;
}

function selfTest() {
  assert.equal(sessionIdFrom('{"session_id":"ab-12"}'), 'ab-12');
  assert.equal(sessionIdFrom('{"session_id":"a\\u001b[31mb/../c"}'), 'a31mbc');
  assert.equal(sessionIdFrom('not json'), '');
  assert.equal(sessionIdFrom('{"session_id":42}'), '');
  assert.ok(lawText().length > 0, 'law text is readable');
  console.log('self-test passed');
  return 0;
}

async function main() {
  const command = process.argv[2] || 'law';
  if (command === '--self-test') {
    return selfTest();
  }
  if (command === 'law') {
    process.stdout.write(pluginFile(RULES_FILE));
    return 0;
  }
  const payload = await readStdin();
  if (command === 'lint') {
    return runLint(payload);
  }
  if (command === 'session-start') {
    const session = sessionIdFrom(payload);
    if (session) {
      writeFileSync(flagPath, session);
    }
    process.stdout.write(lawText());
    return 0;
  }
  if (command === 'subagent') {
    const envelope = {
      hookSpecificOutput: {
        hookEventName: 'SubagentStart',
        additionalContext: lawText(),
      },
    };
    process.stdout.write(JSON.stringify(envelope));
    return 0;
  }
  if (command === 'statusline') {
    const isHidden = (process.env.SNAWYS_LAW_STATUSLINE || '1') === STATUSLINE_DISABLED;
    if (isHidden) {
      return 0;
    }
    const session = sessionIdFrom(payload);
    const isActive = session !== '' && readStamp() === session;
    process.stdout.write(isActive ? BADGE_ON : BADGE_OFF);
    return 0;
  }
  process.stderr.write(`snawys.mjs: unknown command ${command}\n`);
  return 1;
}

process.exitCode = await main();
