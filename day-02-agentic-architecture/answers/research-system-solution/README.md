# Reference solution: Day 2 research system

Only open this after a real attempt. To run it, copy your `.env` here.

- `coordinator.py`: a goal-and-criteria prompt (coverage, partitioning, context passing, parallelism, refinement), plus a `ThreadPoolExecutor` for delegations in the same response.
- `agents.py`: the search agent returns structured `<findings>` (claim, evidence, source, context) and `<gaps>`. The synthesis agent cites `[S#]` ids, keeps conflicts side by side, and ends with "Coverage and gaps".
- `sources.py`: `read_source` returns structured errors, transient (retryable) for a timeout and validation for an unknown id, and says what was attempted.
