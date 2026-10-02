# Day 1 homework, part 1: scaffold the support agent (45–60 min, no API key needed)

**Scaffold the S1 support agent as if you were the architect handing it to a team.** Build it inside [`support-agent/`](support-agent/) in this folder, so it's committed with the rest of the repo:

1. Create the repo tree *from memory first*, then compare it with section 4 (S1) of the lesson.
2. Write `prompts/system.md` (≤ 40 lines). It should cover role, scope, the policies, explicit escalation triggers (explicit request for a human, policy gap or exception, no progress after N attempts, multiple customer matches → ask for another identifier), and the handoff format.
3. Write `src/tools.json` with JSON definitions for `get_customer`, `lookup_order`, `process_refund`, `escalate_to_human`. Each description should say what the tool is for, its input format, when *not* to use it, and one example.
4. Write `src/hooks.py` as pseudo-code. A `before_tool(name, input, state)` returns `allow` / `deny + reason`, and enforces: no `process_refund` without `state.verified_customer_id`, and no amount > 500.
5. Write one paragraph in `README.md` answering: where does this run, what triggers it, where does history live, where do secrets live, what happens when the CRM times out?

Commit and push, or paste the files in the thread, and I'll review them like an exam grader. Tomorrow you turn this skeleton into a running loop with a mock model.


Then take the quiz in `02-quiz.md`.
