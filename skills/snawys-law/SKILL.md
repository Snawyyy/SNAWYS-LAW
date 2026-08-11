---
name: snawys-law
description: Snawy's Law for C and C++ - named bools in if, RAII, modular managers, NASA Power of 10, Google C++ Style. Use whenever writing, reviewing, or refactoring C or C++ code, or when a Snawy's Law lint violation is reported.
---

# Snawy's Law

Binding on all C and C++ code written in this workspace. A `hooks/hooks.json`
linter checks every file after it is written; these are the same rules, stated
in full so the code is right the first time.

## The first rule

`if` takes a named bool, never a raw expression - the name replaces the
comment.

```cpp
const bool is_stream_ready = stream_ != nullptr && stream_->Ready();
if (is_stream_ready) {
```

## Design

- RAII. The resource is acquired in a constructor and released in a
  destructor. No manual cleanup path, no `close()` anyone has to remember,
  no leak on early return.
- A file is about 400 lines, hard stop. Past that the file is holding more
  than one concern: split the extra concern into its own manager with its
  own header and source file.
- Separate modular managers. One manager per concern, owning its own state,
  reached through a narrow interface. Design them first, then use them - no
  logic loose at the call site that belongs inside a manager.

## Power of 10 (NASA JPL, trimmed)

1. No goto, setjmp/longjmp, recursion.
2. Every loop has a fixed upper bound.
3. Functions fit one page (~60 lines).
4. Two assertions per function minimum.
5. Declare data at the smallest possible scope.
6. Check every non-void return value and every parameter.
7. One level of pointer dereference, no function pointers.
8. All warnings on, all warnings fixed, static analysis clean.

## Google C++ Style

1. Headers self-contained, `#define` guard on each.
2. Include what you use, forward-declare sparingly.
3. No `using namespace` at namespace scope.
4. No non-const global variables, no dynamic initialization of statics.
5. Single-argument constructors are `explicit`.
6. Composition over inheritance, interfaces pure abstract.
7. No exceptions.
8. No RTTI / `dynamic_cast`.
9. `const` and `constexpr` wherever it holds.
10. `nullptr`, never `NULL` or `0`.
11. Ownership explicit, smart pointers over raw `new`/`delete`.
12. Inputs by value or const ref, outputs by return or pointer.
13. Names: `CamelCase` types, `snake_case` variables, `kConstant`, `member_`.
14. 80 columns, 2-space indent, no tabs.
15. Comments say why, not what; `TODO(name)`.
16. Avoid macros.
17. Prefer plain `int`, `<cstdint>` for exact widths, unsigned only for bit
    work.
18. `auto` only when it helps readability.

## What the linter catches

Tabs, over-80-column lines, raw `if` conditions, `goto`, `setjmp`/`longjmp`,
`NULL`, `using namespace` at file scope, `dynamic_cast`/`typeid`,
`throw`/`catch`, raw `new`/`delete`, `malloc`/`free`, `#pragma once`,
function-like macros, files over 400 lines, functions over 60 lines,
functions with fewer than two assertions, and fancy punctuation (em dash, en dash, curly quotes, ellipsis
character) anywhere in the file.

The rest - naming, `explicit`, const-correctness, ownership, loop bounds,
checked returns - is on you; the linter cannot see it.
