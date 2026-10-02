# Reference solution: Day 1 support agent

Only open this once you've tried exercises 1–3 yourself. To run it, copy your `.env` here, then use the same commands as the homework.

What changed compared with the starter:
- `tools.py`: the `get_customer` and `lookup_order` descriptions now give purpose, input format, examples, boundaries and error handling (exam 2.1).
- `hooks.py`: `before_tool` blocks unverified, over-limit and wrong-customer refunds and redirects to escalation (exam 1.4, 1.5). `after_tool` trims and normalises order output (exam 5.1).
- `prompts/system.md`: policy, identity rules, explicit escalation criteria and three few-shot examples (exam 4.1, 4.2, 5.2).
