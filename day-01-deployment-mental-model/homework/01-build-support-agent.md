# Day 1 homework, part 1: run a real support agent (60–75 min)

You'll run the exam's Scenario 1 for real: a support agent that calls the Claude API, uses tools against a fake CRM, and has to follow refund and escalation rules. The starter works but is deliberately weak. You'll watch it misbehave, fix it at the right layer, and rerun the scenarios.

Everything is in [`support-agent/`](support-agent/). This *is* the "runtime C" picture from the lesson, small enough to read in ten minutes:

| File | Layer from the lesson |
|---|---|
| `agent.py` | The host process: the agent loop, `stop_reason` handling, and per-conversation state |
| `prompts/system.md` | The system prompt (probabilistic guidance) |
| `tools.py` | Tool definitions Claude sees, plus the dispatcher |
| `hooks.py` | Deterministic rules in code (guarantees) |
| `backend.py` | The company's systems. They're fake here; in production they'd sit behind MCP servers. |
| `scenarios.py` | Six scripted customers, each testing one exam rule |
| `test_hooks.py` | Free unit tests for your hooks, with no API calls |

## Setup (once)

```bash
cd day-01-deployment-mental-model/homework/support-agent
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then open .env and paste your key after ANTHROPIC_API_KEY=
```

**Keep the key out of chat and out of git.** `.env` is in `.gitignore`. Run `git status` before every commit: if `.env` ever shows up, stop and don't commit.

Cost: `scenarios.py` makes about 15–30 API calls per full run on the default model (`claude-opus-5-5`, effort `medium`). That's a few US cents. You can set `EFFORT=low` in `.env` to make it cheaper.

## Step 1: see the baseline (10 min)

```bash
python test_hooks.py      # free: fails, because the hooks are empty
python scenarios.py       # real API: read the trace for each scenario
```

Before you look at the results, predict which of the six scenarios will fail. Then read the `[tool]`, `[blocked]` and `[result]` lines and work out *why* each one passed or failed. Notice that some refund scenarios may pass by luck, but with `enforced_by_hook=False`.

## Step 2: the three fixes

Each fix belongs to a different layer. That's the lesson.

1. **Tool descriptions** in `tools.py` (exam 2.1). Rewrite the two vague descriptions so they give purpose, input format, an example, and when *not* to use the tool.
2. **Hooks** in `hooks.py` (exam 1.4, 1.5). Implement `before_tool` so refunds are blocked until the customer is verified, and over-$500 refunds are blocked with a reason that redirects Claude to `escalate_to_human`. Done when `python test_hooks.py` shows 6/6.
3. **System prompt** in `prompts/system.md` (exam 4.1, 4.2, 5.2). Add explicit escalation criteria, the multiple-matches rule, and 2–3 few-shot examples of borderline cases.

Rerun `python scenarios.py` after each fix to see which one moved which scenario. Aim for 6/6, with `enforced_by_hook=True` on scenarios 1 and 2.

**Stretch (exam 5.1):** in `after_tool`, trim `lookup_order` output to the fields a support agent needs, and convert `delivered_at` to ISO 8601.

## Step 3: talk to it (5 min)

```bash
python agent.py
```

Try to break it: claim to be someone else, ask for a refund on someone else's order, change your mind mid-conversation. Watch the `state:` line. That's the case-facts store your host keeps, and the API never sees it unless you send it.

## Step 4: write down what you learned

Add a short `NOTES.md` in `support-agent/` with one line for each scenario: what failed, which layer fixed it, and the exam rule behind it. Then commit and push. Don't commit `.env`.

```bash
git add -A && git status    # check .env is NOT listed
git commit -m "Day 1 support agent" && git push
```

I'll review your diff like an exam grader. If you get stuck, there's a reference solution in [`../answers/support-agent-solution/`](../answers/support-agent-solution/).

## One thing to know for the exam

The guide tests `tool_choice: "any"` and forced tool selection (`{"type": "tool", "name": ...}`). The newest models (Claude Opus 5.5, Sonnet 5.5 and Fable 5.1) now reject forced `tool_choice` with a 400 error, and the API recommends `auto` plus `strict: true` instead. On the exam, answer as the guide describes. In your own code, you'll see `strict: true` on `escalate_to_human`.

Then take the quiz in `02-quiz.md`.
