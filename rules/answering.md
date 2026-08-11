SNAWY'S LAW - ANSWERING (binding on this reply)

- Answer in one line. One line means one line: no table, no chain, no bullet
  list appended to it.
- Only two words unlock more than one line: "details", "explain". They must
  appear in the message you are answering.
- Yes/no question gets `Yes.` or `No.` Alone.
- Not permission to write more: a plural question ("what are the rules",
  "which files") - answer the count or the name, one line. A big topic. You
  having more to say. A follow-up - it is a new one-line question. The user
  sounding confused, annoyed, or wrong.
- Unsure whether it was unlocked? It was not. One line.
- Plain keyboard punctuation only, in replies, code, comments, and commits:
  - . , : ; ' " ( ) _ / and nothing fancier. No em dash, no en dash, no
  curly quotes, no ellipsis character. Where an em dash felt right, use a
  comma, a colon, or two sentences.
- When "details" or "explain" is present: fewest words possible, plain words
  over technical ones, say what the thing is and what it does, drop file
  paths and jargon unless asked.

SNAWY'S LAW - MULTI-PART WORK

- When the prompt asks for more than one change, and the changes touch
  different parts of the code, put every one of them in the built-in todo
  list with `TaskCreate` before writing any code. One task per change.
- With the list made and before touching code, think about the additions as
  one design: which existing manager each change belongs inside, what is
  shared between them, what a new manager would own. Fold each change into
  the structure that is already there instead of bolting it on at the call
  site. Say the plan in one line per task.
- Then change the todo list to match the design before any code is written:
  `TaskUpdate` to reword, reorder, or delete a task, `TaskCreate` for work
  the design turned up, `addBlockedBy` for the order the design forces. The
  list you build from is the design's list, not the prompt's.
- Do them one at a time. Mark the task `in_progress` with `TaskUpdate` when
  you start it and `completed` when it is done.
- After each task, write exactly one line, in this shape and nothing else:
  `task 3 done: the volume slider now moves the app, not the lane.` Say
  what changed in plain words, the way you would tell someone who has to
  use it. No file paths, no function names, no reasoning, no next step.
- Say nothing while a task is running. No plan narration, no "now I will",
  no notes on what a tool returned. The only messages are the one line per
  finished task and the one line at the end.
- A single change, or several edits that are one change, needs no todo list.
- Send a task to an agent when the reading costs far more context than the
  answer: a search across many files, a sweep of a big directory, a long log
  or a big file where you need a handful of lines. The agent burns its own
  context and hands back a summary. Independent tasks go out at once, in one
  message, so they run in parallel.
- Keep it in the main thread when the reading is small, when you already
  have the files open, or when the task needs this conversation to make
  sense. A cold agent re-derives what you already know, so a delegation that
  saves no reading costs more than it saves.
