---
name: snawys-law
description: Snawy's Law for C and C++ - named bools for compound conditions, one manager per concern, no exceptions or RTTI, small files, plain punctuation. Use whenever writing, reviewing, or refactoring C or C++ code.
---

# Snawy's Law

1. A compound `if` condition (`&&`, `||`, `?:`) goes into a named `const
   bool` first; the name replaces the comment.
2. One manager per concern, owning its own state behind a narrow interface.
   Logic that belongs inside a manager does not sit at the call site.
3. No exceptions, no RTTI (`dynamic_cast`, `typeid`). Return a status;
   `qobject_cast` is fine.
4. A file past about 400 lines holds more than one concern: split one out
   into its own manager.
5. Plain keyboard punctuation in code and comments: no em dash, en dash,
   curly quotes, or ellipsis character.

```cpp
const bool is_stream_ready = stream_ != nullptr && stream_->Ready();
if (is_stream_ready) {
```
