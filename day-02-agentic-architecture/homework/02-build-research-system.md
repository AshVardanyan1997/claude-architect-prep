# Day 2 homework, part 2: a live multi-agent research system (75 min)

This is the exam's Scenario 3 (multi-agent research system) and the guide's official Exercise 4, running on the real API. A coordinator delegates to search subagents and a synthesis subagent, which read a small research library (`corpus.json`). The library is built to be messy, like real sources: two credible sources disagree on a statistic, and one publisher's server is down.

The test topic is the exam's own example, *"impact of AI on creative industries"*. Out of the box the system makes the exact mistakes from the official sample questions.

## Files

| File | Role | Layer |
|---|---|---|
| `coordinator.py` | The hub. Its only tool is `delegate` (the Agent SDK's `Task`). Runs the delegations. | host code + coordinator prompt |
| `agents.py` | Subagent definitions (like `AgentDefinition`) and `spawn()`, which starts each one with a fresh context | subagent prompts and toolsets |
| `sources.py` | The search agent's tools over the library | tool code |
| `common.py` | One generic agent loop shared by every agent | host code |
| `checks.py` | Runs the whole system and grades the report: 6 checks | — |
| `test_offline.py` | Free tests for the two code exercises | — |

## Setup

Use the same venv as Day 1: `C:\venvs\ccarf\Scripts\Activate.ps1`. Then:

```powershell
cd day-02-agentic-architecture\homework\research-system
copy ..\..\..\day-01-deployment-mental-model\homework\support-agent\.env .env
pip install -r requirements.txt     # already installed if you use the same venv
```

**Cost:** a full `checks.py` run makes roughly 20–40 API calls with growing contexts. My estimate is a few tens of US cents per run, but I haven't measured it. Do several fixes between runs. `EFFORT=low` in `.env` makes it cheaper.

## Step 1: baseline (10 min)

```powershell
python test_offline.py    # free: 5 failures expected
python checks.py          # live: read the trace as it runs
```

Predict the result of each of the 6 checks before it finishes. While it runs, watch the `[coordinator:delegate-start]` lines and see what the coordinator actually asks each subagent to do.

## Step 2: four fixes, four different layers

1. **Coordinator prompt** (exam 1.2, 1.6). Replace `COORDINATOR_PROMPT` with the one you wrote in the prompt drill. This should fix *coverage*.
2. **Subagent prompts** in `agents.py` (exam 1.3, 5.6). Make the search agent return structured findings: claim, evidence quote, source id, title, date, and what was measured. Make the synthesis agent cite `[S3]`-style ids, keep conflicting numbers side by side with their sources, and end with a coverage-gaps section. This should fix *provenance* and *conflict kept*.
3. **Tool error handling** in `sources.py` (exam 2.2, 5.3). `read_source` turns a timeout into an empty source, so the failure disappears. Return structured errors (`isError`, `errorCategory`, `isRetryable`, what was attempted, a message saying what to do next) and tell a timeout apart from an unknown id. This should fix *gap reported*. `test_offline.py` checks it for free.
4. **Parallel execution** in `coordinator.py` (exam 1.3). `execute_delegations` runs delegations one after another even when the coordinator asks for several at once. Use `concurrent.futures.ThreadPoolExecutor`, then compare the elapsed time before and after. `test_offline.py` checks it for free.

Aim for 6/6 on `checks.py` and all tests passing in `test_offline.py`.

## Step 3: notes and push

Add `NOTES.md` in `research-system/` with one line for each fix: what was wrong, which layer fixed it, the exam rule, and the elapsed time before and after parallelism. Then:

```powershell
git add -A ; git status     # .env must NOT be listed
git commit -m "Day 2 research system" ; git push
```

The reference solution is in `../answers/research-system-solution/`. Open it after you've had a real attempt.

Then take the quiz in `03-quiz.md`.
