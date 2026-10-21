#!/usr/bin/env python3
"""Snawy's Law linter.

Checks paths passed on the command line, or reads Claude PostToolUse hook JSON
on stdin. Exits 2 with findings so the calling agent has to fix them.

Run `snawys_lint.py --self-test` to check the checker.
"""

import json
import re
import sys

EXTS = (".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".inl")
MAX_COLS = 80
MAX_FUNC_LINES = 60
MAX_FILE_LINES = 400

# Line regexes, not a parser. Misses multi-line conditions and
# macro-heavy code; swap in libclang if the false-positive rate ever bites.
IF_LINE = re.compile(r"^\s*(?:\}\s*)?(?:else\s+)?if\s*(?:constexpr\s*)?\((.*)\)")
# A single variable or call is already named; only compound logic needs one.
COMPOUND = re.compile(r"&&|\|\||\?|\band\b|\bor\b")
# Outside any body, a line with ")" that opens a brace starts a function;
# this also catches the last line of a signature split over lines.
FUNC_OPEN = re.compile(r"^.*\).*\{\s*$")
# Namespace braces hold functions, they are not one.
NAMESPACE_OPEN = re.compile(r"^\s*(?:inline\s+)?namespace\b[^;]*\{\s*$")
NAMESPACE_CLOSE = re.compile(r"^\s*\}\s*//\s*namespace\b")
# Qt parent ownership: an object built with a parent is deleted by it.
PARENTED_NEW = re.compile(
    r"\bnew\s+[\w:<>]+\s*\([^;]*\b(?:this|\w*parent\w*)\s*\)"
)

BANNED = (
    (re.compile(r"\bgoto\b"), "goto: banned, restructure the control flow"),
    (re.compile(r"\b(?:setjmp|longjmp)\b"), "setjmp/longjmp: banned"),
    (re.compile(r"\bNULL\b"), "NULL: use nullptr"),
    (re.compile(r"^using namespace\b"), "using namespace at namespace scope"),
    (re.compile(r"\b(?:dynamic_cast|typeid)\b"), "RTTI: banned"),
    (re.compile(r"\bthrow\b|\bcatch\s*\("), "exceptions: banned, return status"),
    (re.compile(r"(?<!= )\bdelete\b"), "raw delete: use a smart pointer"),
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
            is_unowned_new = bool(re.search(r"\bnew\b", line)) and not (
                PARENTED_NEW.search(line)
            )
            if is_unowned_new:
                findings.append(
                    (number, "raw new: use a smart pointer or a Qt parent")
                )
            condition = IF_LINE.match(line)
            is_compound_condition = bool(condition) and bool(
                COMPOUND.search(condition.group(1))
            )
            if is_compound_condition:
                findings.append(
                    (number, "compound if condition: name it in a const bool")
                )
            in_function = depth > 0
            is_namespace_brace = not in_function and bool(
                NAMESPACE_OPEN.match(line) or NAMESPACE_CLOSE.match(line)
            )
            if is_namespace_brace:
                continue
            if not in_function and FUNC_OPEN.match(line):
                func_start = number
            depth += line.count("{") - line.count("}")
            func_closed = depth <= 0 and func_start > 0
            if func_closed:
                length = number - func_start + 1
                if length > MAX_FUNC_LINES:
                    findings.append(
                        (func_start, f"function is {length} lines: limit is "
                                     f"{MAX_FUNC_LINES}")
                    )
                func_start = 0
                depth = 0
    return findings


def self_test():
    bad = [
        "void Foo() {\n",
        "  if (a == b && c) {\n",
        "    int* p = NULL;\n",
        "    auto* w = new Widget();\n",
        "    delete w;\n",
        "  }\n",
        "}\n",
    ]
    bad.append("  // em dash \u2014 here\n")
    messages = [message for _, message in check(bad)]
    assert any("fancy punctuation" in m for m in messages), messages
    assert any("compound if" in m for m in messages), messages
    assert any("nullptr" in m for m in messages), messages
    assert any("raw new" in m for m in messages), messages
    assert any("raw delete" in m for m in messages), messages
    good = [
        "void Foo() {\n",
        "  const bool is_ready = ready_ && count_ > 0;\n",
        "  if (is_ready) {\n",
        "    Run();\n",
        "  }\n",
        "  if (!stream_->Ready()) {\n",
        "    return;\n",
        "  }\n",
        "  auto* label = new QLabel(tr(\"Hi\"), this);\n",
        "  auto* view = new TimelineView(parent);\n",
        "}\n",
        "Foo(const Foo&) = delete;\n",
    ]
    assert check(good) == [], check(good)
    long_body = ["void Foo() {\n"] + ["  Run();\n"] * MAX_FUNC_LINES
    nested = ["namespace a {\n", "int Bar(int x,\n", "        int y) {\n"]
    nested += long_body[1:] + ["}\n", "}  // namespace a\n"]
    assert any("function is" in m for _, m in check(nested)), "namespace"
    wrapped = ["namespace a {\n"] + good + ["}  // namespace a\n"]
    assert check(wrapped) == [], check(wrapped)
    long_file = good + ["// filler\n"] * MAX_FILE_LINES
    assert any("file is" in m for _, m in check(long_file)), "file limit"
    print("self-test passed")


def main():
    if "--self-test" in sys.argv:
        self_test()
        return 0
    paths = sys.argv[1:]
    if not paths:
        try:
            event = json.load(sys.stdin)
        except (json.JSONDecodeError, ValueError):
            return 0
        assert isinstance(event, dict), "hook payload must be an object"
        paths = [event.get("tool_input", {}).get("file_path", "")]
    reports = []
    for path in paths:
        if not path.endswith(EXTS):
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as handle:
                lines = handle.readlines()
        except OSError as error:
            reports.append(f"{path}: cannot read file: {error}")
            continue
        reports.extend(f"{path}:{n}: {m}" for n, m in check(lines)[:40])
    if reports:
        report = "\n".join(reports)
        print("Snawy's Law violations - fix them now:\n" + report, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
