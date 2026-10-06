# Day 4 tool drill: answers

**T1.** Split the generic tool into purpose-specific tools with clear contracts (task 2.1):

| Tool | Description | Contract |
|---|---|---|
| `extract_data_points` | Pull the numbers, dates and named statistics out of one document, each with the sentence it came from. Use it when you need values to compare or cite. Doesn't summarise. | in: `document_id`; out: `[{value, unit, quote, location}]` |
| `summarize_content` | Summarise one document's argument and conclusions in up to 5 sentences. Use it to decide whether a document is relevant. Doesn't return quotes or numbers you can cite. | in: `document_id`, optional `focus`; out: `{summary}` |
| `verify_claim_against_source` | Check whether one specific claim is supported, contradicted or not addressed by one document, and quote the evidence. Use it before stating a claim as fact. | in: `claim`, `document_id`; out: `{verdict: supported/contradicted/not_addressed, quote}` |

Each description says what the tool is for **and** what it isn't for, so the agent can tell them apart.

**T2.**

> Search this team's Jira tickets with a JQL query, e.g. `project = SHOP AND status = "In Progress"`. Returns key, title, status, assignee and last update for up to 50 tickets. Use this for any question about tickets, bugs, sprints or who is working on what: ticket data is **not** in the repository, so Grep and Read can't find it. To read one ticket's full description and comments, call `get_ticket` with its key.

The key line is the one that says why the built-in tools can't answer. Without it, the model falls back to tools it already trusts (task 2.4).

**T3.**

| Failure | errorCategory | isRetryable | message |
|---|---|---|---|
| Provider timeout | transient | true | "Payment provider timed out. Retry once; if it fails again, tell the customer the refund is queued." |
| Negative amount | validation | false | "Amount must be positive. Check the order total and call again with the correct amount." |
| Over $500 | business | false | "Refunds over $500 need a human agent. Tell the customer you've passed it to a colleague and call escalate_to_human." |
| No permission | permission | false | "This API key can't issue refunds. Escalate; retrying won't help." |

The guide's skills list names transient, validation and permission, and its knowledge list adds **business** errors (policy violations), marked non-retryable with a customer-friendly explanation.

**T4.** No. An empty result is a **successful query with no matches**. If it were marked as an error, the agent would retry or report a failure when the true answer is "this customer has no orders" (task 2.2).

**T5.**

1. **Glob** finds files by name pattern.
2. **Grep** searches file contents.
3. **Edit** makes a targeted change anchored on unique text.
4. **Read the whole file, then Write it back.** That's the guide's named fallback when Edit's anchor isn't unique (task 2.5). Giving Edit more surrounding context so the match becomes unique also works in practice, but the exam's answer is Read + Write.
