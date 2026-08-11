#!/usr/bin/env python3
"""Snawy's Law linter.

Reads PostToolUse hook JSON on stdin, checks the file that was just written,
and exits 2 with the findings on stderr so Claude has to fix them.

Run `snawys_lint.py --self-test` to check the checker.
"""

import json
import re
import sys

EXTS = (".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".inl")
MAX_COLS = 80
MAX_FUNC_LINES = 60
MAX_FILE_LINES = 400
MIN_ASSERTS = 2

# ponytail: line regexes, not a parser. Misses multi-line conditions and
# macro-heavy code; swap in libclang if the false-positive rate ever bites.
IF_LINE = re.compile(r"^\s*(?:\}\s*)?(?:else\s+)?if\s*(?:constexpr\s*)?\((.*)\)")
NAMED_BOOL = re.compile(r"^!?[A-Za-z_][A-Za-z0-9_]*$")
FUNC_OPEN = re.compile(r"^[A-Za-z_~].*\).*\{\s*$")
ASSERT_CALL = re.compile(r"\b(?:assert|static_assert|CHECK|DCHECK)\s*\(")

BANNED = (
    (re.compile(r"\bgoto\b"), "goto: banned, restructure the control flow"),
    (re.compile(r"\b(?:setjmp|longjmp)\b"), "setjmp/longjmp: banned"),
    (re.compile(r"\bNULL\b"), "NULL: use nullptr"),
    (re.compile(r"^using namespace\b"), "using namespace at namespace scope"),
    (re.compile(r"\b(?:dynamic_cast|typeid)\b"), "RTTI: banned"),
    (re.compile(r"\bthrow\b|\bcatch\s*\("), "exceptions: banned, return status"),
    (re.compile(r"\bnew\b|\bdelete\b"), "raw new/delete: use a smart pointer"),
    (re.compile(r"\b(?:malloc|calloc|realloc|free)\s*\("), "manual alloc: use RAII"),
    (re.compile(r"^#pragma once"), "#pragma once: use a #define include guard"),
    (re.compile(r"^#\s*define\s+\w+\("), "function-like macro: avoid macros"),
)

SKIP_LINE = re.compile(r"^\s*(?://|\*|/\*)")
FANCY = re.compile(r"[–—‘’“”…]")


def check(lines):
    """Return a list of (line_number, message) for one file's lines."""
    assert isinstance(lines, list), "lines must be a list"
    findings = []
    if len(lines) > MAX_FILE_LINES:
        findings.append(
            (1, f"file is {len(lines)} lines: limit is {MAX_FILE_LINES}, "
                f"split a concern into its own manager")
        )
    depth = 0
    func_start = 0
    func_asserts = 0
    for number, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")
        is_comment = bool(SKIP_LINE.match(line))
        if "\t" in line:
            findings.append((number, "tab: 2-space indent, no tabs"))
        if len(line) > MAX_COLS:
            findings.append((number, f"{len(line)} columns: limit is {MAX_COLS}"))
        if FANCY.search(line):
            findings.append((number, "fancy punctuation: plain keyboard only"))
        if not is_comment:
            for pattern, message in BANNED:
                if pattern.search(line):
                    findings.append((number, message))
            condition = IF_LINE.match(line)
            is_raw_condition = bool(condition) and not NAMED_BOOL.match(
                condition.group(1).strip()
            )
            if is_raw_condition:
                findings.append(
                    (number, "if takes a named bool, not a raw expression")
                )
            if ASSERT_CALL.search(line):
                func_asserts += 1
            in_function = depth > 0
            if not in_function and FUNC_OPEN.match(line):
                func_start = number
                func_asserts = 0
            depth += line.count("{") - line.count("}")
            func_closed = depth <= 0 and func_start > 0
            if func_closed:
                length = number - func_start + 1
                if length > MAX_FUNC_LINES:
                    findings.append(
                        (func_start, f"function is {length} lines: limit is "
                                     f"{MAX_FUNC_LINES}")
                    )
                if func_asserts < MIN_ASSERTS:
                    findings.append(
                        (func_start, f"{func_asserts} assertions: minimum is "
                                     f"{MIN_ASSERTS} per function")
                    )
                func_start = 0
                depth = 0
    return findings


def self_test():
    bad = [
        "void Foo() {\n",
        "  if (a == b) {\n",
        "    int* p = NULL;\n",
        "  }\n",
        "}\n",
    ]
    bad.append("  // em dash — here\n")
    messages = [message for _, message in check(bad)]
    assert any("fancy punctuation" in m for m in messages), messages
    assert any("named bool" in m for m in messages), messages
    assert any("nullptr" in m for m in messages), messages
    assert any("assertions" in m for m in messages), messages
    good = [
        "void Foo() {\n",
        "  assert(ready_);\n",
        "  assert(count_ >= 0);\n",
        "  const bool is_ready = ready_;\n",
        "  if (is_ready) {\n",
        "    Run();\n",
        "  }\n",
        "}\n",
    ]
    assert check(good) == [], check(good)
    long_file = good + ["// filler\n"] * MAX_FILE_LINES
    assert any("file is" in m for _, m in check(long_file)), "file limit"
    print("self-test passed")


def main():
    if "--self-test" in sys.argv:
        self_test()
        return 0
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    assert isinstance(event, dict), "hook payload must be an object"
    path = event.get("tool_input", {}).get("file_path", "")
    if not path.endswith(EXTS):
        return 0
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            lines = handle.readlines()
    except OSError:
        return 0
    findings = check(lines)
    if not findings:
        return 0
    report = "\n".join(f"{path}:{n}: {m}" for n, m in findings[:40])
    print("Snawy's Law violations - fix them now:\n" + report, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
