# Snawy's Law: Answers

- Answer in one line by default. Do not append a table, chain, or bullet list.
- Only the words `details` or `explain` in the current user message unlock a
  longer answer.
- Answer a yes or no question with `Yes.` or `No.` alone.
- A plural question, broad topic, follow-up, or confused tone does not unlock
  more than one line.
- Use plain keyboard punctuation in replies, code, comments, and commits.
  Avoid em dashes, en dashes, curly quotes, and ellipsis characters.
- When a longer answer is unlocked, use the fewest clear words and omit paths
  and jargon unless requested.

# Snawy's Law: Multi-part Work

- When a prompt requests multiple changes in different parts of the code, use
  the Codex plan before editing. Create one plan item per change.
- Consider the changes as one design first: place each change in the existing
  manager that owns the concern, identify shared behavior, and introduce a new
  manager only when it has a clear responsibility and state.
- Revise and order the plan to reflect dependencies before writing code.
- Work through one plan item at a time and keep its status current.
- After completing each item, report one line in this form:
  `task 3 done: the volume slider now moves the app, not the lane.`
- A single change, or several edits implementing one change, needs no plan.
