---
name: snawys-law
description: Snawy's Law for C and C++ - named bools for compound conditions, RAII, modular managers, NASA Power of 10, Google C++ Style, with Qt carve-outs. Use whenever writing, reviewing, or refactoring C or C++ code, or when a Snawy's Law lint violation is reported.
---

# Snawy's Law

Apply these rules to C and C++ code you write, review, or refactor. After
changing C or C++ files, run the bundled `scripts/snawys_lint.py` on every
changed path and fix what it reports. A rule exists to make code clearer;
where following it makes the code worse, break it and say why in a comment.

## The first rule

A compound `if` condition (`&&`, `||`, `?:`) goes into a named bool first,
so the name replaces the comment. A single call or variable is already named.

```cpp
const bool is_stream_ready = stream_ != nullptr && stream_->Ready();
if (is_stream_ready) {
```

## Design

- RAII. Acquire in a constructor, release in a destructor. No manual cleanup
  path, no leak on early return.
- Separate modular managers. One manager per concern, owning its own state,
  reached through a narrow interface. Logic that belongs inside a manager
  does not sit at the call site.
- A file past about 400 lines holds more than one concern: split one out.

## Power of 10 (NASA JPL, trimmed)

1. No goto, setjmp/longjmp. Recursion only with a hard depth cap.
2. Loops have a clear bound. Event loops are exempt.
3. Functions fit one page (~60 lines).
4. Assert preconditions and invariants that can actually fail.
5. Declare data at the smallest possible scope.
6. Check every return value that can fail, and every untrusted parameter.
7. One level of pointer dereference. Lambdas, `std::function`, and Qt
   signals/slots are fine; raw function pointers are not.
8. All warnings on, all warnings fixed, static analysis clean.

## Google C++ Style

1. Headers self-contained, `#define` guard on each.
2. Include what you use, forward-declare sparingly.
3. No `using namespace` at namespace scope.
4. No non-const globals, no dynamic initialization of statics.
5. Single-argument constructors are `explicit`.
6. Composition over inheritance, interfaces pure abstract. Subclassing a
   framework base (`QObject`, `QWidget`) is fine.
7. No exceptions.
8. No RTTI / `dynamic_cast`. `qobject_cast` is fine.
9. `const` and `constexpr` wherever it holds.
10. `nullptr`, never `NULL` or `0`.
11. Ownership explicit: smart pointers over raw `new`/`delete`. A Qt object
    handed to a parent at construction (`new Foo(this)`) is owned by it.
12. Inputs by value or const ref, outputs by return or pointer.
13. Names: `CamelCase` types, `snake_case` variables, `kConstant`, `member_`.
14. 80 columns, 2-space indent, no tabs.
15. Comments say why, not what; `TODO(name)`.
16. Avoid macros (Qt's `Q_OBJECT` and friends are fine).
17. Prefer plain `int`, `<cstdint>` for exact widths, unsigned only for bit
    work.
18. `auto` only when it helps readability.

## What the linter catches

Tabs, lines over 80 columns, compound `if` conditions, `goto`,
`setjmp`/`longjmp`, `NULL`, `using namespace` at file scope,
`dynamic_cast`/`typeid`, `throw`/`catch`, raw `new` without a parent, raw
`delete`, `malloc`/`free`, `#pragma once`, function-like macros, files over
400 lines, functions over 60 lines, and fancy punctuation.

Naming, `explicit`, const-correctness, ownership, loop bounds, assertions,
and checked returns need review by eye.
