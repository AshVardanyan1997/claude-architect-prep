# Day 4 homework, part 1: tool descriptions and error design (15 min, blank page)

On the mock you scored 7/11 on Tools & MCP. Most of that domain comes down to two skills: writing a tool description that routes correctly, and designing an error the agent can act on. Write your answers in `homework/tool-drill.md` before you open `../answers/tool-drill-answers.md`.

---

**T1. Rename and split.** A research agent has one tool:

```text
analyze_document(input: str) -> str
"Analyzes a document."
```

The agent uses it for extracting numbers, for summaries, and for checking whether a claim is supported, and it often does the wrong one. Design **three** tools to replace it: give each a name, a description of 2–4 sentences, and an input/output contract. (Task 2.1)

extract_numeric_facts = {
    "name": "extract_numeric_facts",
    "description": (
        "reads the provided text and extracts all the numeric facts in a format: date, fact, number, notes. For each fact keep 1 row. Example, text: "
        "'there was an accident near 12345 Main Str on Sep-20, 2 cars were involved, each of them thought he was innocent and claimed correspondigly $15.000 and $20.000 reimbursment."' "
        "your extract should be: "Sep-20, car accident, 15.000, car 1 claim, 12345 Main St" and  "Sep-20, car accident, 15.000, car 2 claim, 13245 Main St"
    ),
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "date": {"type": "string", "description": "Date the claim was issued, as YYYY-MM-DD."},
            "fact": {"type": "string", "description": "What the amount stands for."},
            "amount": {"type": "string", "description": "The amount of the claim."},
            "notes": {"type": "string", "description": "Additional notes to describe the fact."},
        },
        "required": ["date", "fact", "amount", ],
        "additionalProperties": False,
    }
}

summarize_facts = {
    "name": "summarize_facts",
    "description": (
        "reads the extracted facts and provides a summary report which must include ground summaries at top, then summaries by dates only after that print all the facts received from extract_numeric_fact" " tool "
    )
}

verify_claim = {
    "name": "verify_claim",
    "description": (
        "verifies the claims in the reports. Example, verify the number of car accidents in September. It greps all the **/reports/Sept_*.md files and returns all the claims made in September "
    )
}

**T2. Built-in vs MCP.** A team adds an MCP tool `search_tickets` that searches Jira with JQL. Claude Code keeps running Grep over the repo instead. The current description is *"Searches tickets."* Rewrite it so the agent prefers it whenever the question is about tickets. (Task 2.4)

Search tickets using search_tickets tool because it is customized with our requirements. Grep will not provide the answer that is needed in the same format we need.

**T3. Four errors.** A `process_refund` MCP tool can fail in four ways:

1. The payment provider times out. - transient, yes, payment provider times out, retrying
2. The amount is negative. - validation, no, the amount in the account is negative - aborting the process
3. The refund is over the $500 policy limit. - business, no, you can't make a refund more than $500, that is the policy
4. The API key lacks refund permission. - permission, no, you don't have enough permission to do the transaction

For each one, write the error object: `errorCategory`, `isRetryable`, and a `message`. For the policy limit, the message should be something the agent can repeat to the customer. (Task 2.2)

**T4. Empty vs failed.** `search_orders` for a new customer finds nothing. Should the result have `isError: true`? Answer in one sentence, saying what the agent would do wrong otherwise. (Task 2.2)
isError: False, there is no order associated with this customer. Agent should send a message that there is no order for this customer.

**T5. Which built-in tool?** Name the built-in tool you'd use first for each:

1. Find every file matching `**/*.test.tsx`. --glob
2. Find every caller of `formatPrice(`. grep
3. Change one line in a config file, where the text appears exactly once. edit write
4. The same change, but the text appears 4 times and Edit fails. bash

(Task 2.5)
