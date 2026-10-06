# Day 4 homework, part 1: tool descriptions and error design (15 min, blank page)

On the mock you scored 7/11 on Tools & MCP. Most of that domain comes down to two skills: writing a tool description that routes correctly, and designing an error the agent can act on. Write your answers in `homework/tool-drill.md` before you open `../answers/tool-drill-answers.md`.

---

**T1. Rename and split.** A research agent has one tool:

```text
analyze_document(input: str) -> str
"Analyzes a document."
```

The agent uses it for extracting numbers, for summaries, and for checking whether a claim is supported, and it often does the wrong one. Design **three** tools to replace it: give each a name, a description of 2–4 sentences, and an input/output contract. (Task 2.1)

**T2. Built-in vs MCP.** A team adds an MCP tool `search_tickets` that searches Jira with JQL. Claude Code keeps running Grep over the repo instead. The current description is *"Searches tickets."* Rewrite it so the agent prefers it whenever the question is about tickets. (Task 2.4)

**T3. Four errors.** A `process_refund` MCP tool can fail in four ways:

1. The payment provider times out.
2. The amount is negative.
3. The refund is over the $500 policy limit.
4. The API key lacks refund permission.

For each one, write the error object: `errorCategory`, `isRetryable`, and a `message`. For the policy limit, the message should be something the agent can repeat to the customer. (Task 2.2)

**T4. Empty vs failed.** `search_orders` for a new customer finds nothing. Should the result have `isError: true`? Answer in one sentence, saying what the agent would do wrong otherwise. (Task 2.2)

**T5. Which built-in tool?** Name the built-in tool you'd use first for each:

1. Find every file matching `**/*.test.tsx`.
2. Find every caller of `formatPrice(`.
3. Change one line in a config file, where the text appears exactly once.
4. The same change, but the text appears 4 times and Edit fails.

(Task 2.5)
