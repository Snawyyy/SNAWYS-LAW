#!/usr/bin/env node
// Cross-platform hook entry point for the snawys_law plugin.
//
// One node process replaces bash + cat + jq, so the same hooks.json works on
// Windows and on Linux. Node is guaranteed: Claude Code runs on it.
//
//   node snawys.mjs law           print the answering rules
//   node snawys.mjs session-start stamp the session flag, print the rules
//   node snawys.mjs subagent      same text, wrapped for SubagentStart
//   node snawys.mjs statusline    print the badge
//   node snawys.mjs --self-test   check the checkable parts

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
const FLAG_NAME = '.snawys-law-active';
const RULES_FILE = ['rules', 'answering.md'];

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

function selfTest() {
  assert.equal(sessionIdFrom('{"session_id":"ab-12"}'), 'ab-12');
  assert.equal(sessionIdFrom('{"session_id":"a\\u001b[31mb/../c"}'), 'a31mbc');
  assert.equal(sessionIdFrom('not json'), '');
  assert.equal(sessionIdFrom('{"session_id":42}'), '');
  assert.ok(pluginFile(RULES_FILE).length > 0, 'law text is readable');
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
  if (command === 'session-start') {
    const session = sessionIdFrom(payload);
    if (session) {
      writeFileSync(flagPath, session);
    }
    process.stdout.write(pluginFile(RULES_FILE));
    return 0;
  }
  if (command === 'subagent') {
    const envelope = {
      hookSpecificOutput: {
        hookEventName: 'SubagentStart',
        additionalContext: pluginFile(RULES_FILE),
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
