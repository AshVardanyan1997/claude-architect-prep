"""Free tests for the two code exercises. No API calls, no cost.

Run:  python test_offline.py

- Exercise 3: read_source must return structured errors.
- Exercise 4: several delegations from one response must run in parallel.
"""

import time

import coordinator
import sources

failed = 0


def check(desc, ok):
    global failed
    failed += not ok
    print(f"{'PASS' if ok else 'FAIL'}  {desc}")


# --- Exercise 3: structured errors ---------------------------------------------------------
timeout = sources.read_source("S5")
check("timeout is reported as an error, not an empty source", timeout.get("isError") is True)
check("timeout is marked transient and retryable",
      timeout.get("errorCategory") == "transient" and timeout.get("isRetryable") is True)
check("error message says what was attempted (mentions S5)", "S5" in str(timeout.get("message", "")))

missing = sources.read_source("S99")
check("unknown id is a validation error, not retryable",
      missing.get("isError") is True and missing.get("errorCategory") == "validation"
      and missing.get("isRetryable") is False)

ok = sources.read_source("S3")
check("a working source still returns its text", "38%" in ok.get("text", ""))

empty = sources.search_corpus("zzzz nothing matches")
check("an empty search is a valid empty result, not an error", empty["results"] == [] and not empty.get("isError"))


# --- Exercise 4: parallel delegation --------------------------------------------------------
class FakeCall:
    def __init__(self, i):
        self.id, self.name, self.input = f"call{i}", "delegate", {"agent": "search", "task": f"task {i}"}


def slow_spawn(agent, task, trace, verbose=True):
    time.sleep(1.0)
    return f"result for {task}"


coordinator.spawn = slow_spawn
start = time.time()
results = coordinator.execute_delegations([FakeCall(i) for i in range(3)], [], verbose=False)
elapsed = time.time() - start
check(f"3 one-second delegations finish in under 2s (took {elapsed:.1f}s)", elapsed < 2.0)
check("every call gets its own result with the matching tool_use_id",
      sorted(r["tool_use_id"] for r in results) == ["call0", "call1", "call2"])

print(f"\n{'all passed' if not failed else f'{failed} failed'}")
raise SystemExit(1 if failed else 0)
