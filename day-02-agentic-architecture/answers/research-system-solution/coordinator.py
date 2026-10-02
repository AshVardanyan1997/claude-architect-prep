"""The coordinator: hub of a hub-and-spoke multi-agent system (exam task 1.2).

It has exactly one tool, `delegate`, the equivalent of the Agent SDK's Task
tool. A coordinator can only spawn subagents if that tool is in its toolset,
which is why the exam says allowedTools must include "Task".

Run:  python coordinator.py "impact of AI on creative industries"

EXERCISE 1 (exam tasks 1.2 and 1.6): COORDINATOR_PROMPT dictates fixed steps
instead of goals. See what that does to coverage, then rewrite it.
EXERCISE 4 (exam task 1.3): execute_delegations runs delegations one at a time,
even when the coordinator asks for several in one response. Make them run in
parallel and compare the elapsed time.
"""

import sys
import time
from concurrent.futures import ThreadPoolExecutor

from agents import AGENTS, spawn
from common import log, run_agent, tool_result

COORDINATOR_PROMPT = """You coordinate a research team and are accountable for the final report.

Goal: a report that covers the WHOLE topic, not just its most obvious part. Before delegating,
list the distinct areas the topic spans (for an industry topic, every major sector in it) and give
each search agent a different, non-overlapping area so their work doesn't duplicate.

Quality bar for the report:
- Every major area of the topic is covered, or explicitly listed as a gap.
- Every claim traces to a source id; conflicting figures are kept with attribution.
- Sources that couldn't be read are named.

How to work:
- Delegate independent searches in the SAME response so they run in parallel.
- Subagents remember nothing. When you delegate the report, paste every search agent's findings and
  gaps into the task verbatim, with source ids and dates.
- Read the draft report. If an area is thin or missing, run a targeted search for it and
  re-delegate the report with the extra findings. Then return the final report unchanged."""

DELEGATE_TOOL = {
    "name": "delegate",
    "description": (
        "Start a subagent on one task and get its result back. Each subagent starts with NO memory "
        "of this conversation, so `task` must contain everything it needs: the goal, the scope, and "
        "any findings from other subagents it should use. Available agents:\n"
        + "\n".join(f"- {name}: {spec['description']}" for name, spec in AGENTS.items())
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "agent": {"type": "string", "enum": list(AGENTS)},
            "task": {"type": "string", "description": "Complete, self-contained instructions and context."},
        },
        "required": ["agent", "task"],
    },
}


def execute_delegations(calls, trace, verbose):
    """Run the delegate calls from ONE coordinator response."""
    def one(call):
        log(trace, "coordinator", "delegate-start", f"{call.input['agent']}: {call.input['task']}", verbose)
        output = spawn(call.input["agent"], call.input["task"], trace, verbose)
        log(trace, "coordinator", "delegate-end", f"{call.input['agent']} returned {len(output)} chars", verbose)
        return tool_result(call.id, output)

    # All delegations from one response run at the same time; results come back together.
    with ThreadPoolExecutor(max_workers=max(1, len(calls))) as pool:
        return list(pool.map(one, calls))


def research(topic: str, verbose: bool = True):
    trace = []
    started = time.time()
    report = run_agent("coordinator", COORDINATOR_PROMPT, [DELEGATE_TOOL], f"Research topic: {topic}",
                       lambda calls: execute_delegations(calls, trace, verbose), trace, verbose)
    return report, trace, time.time() - started


if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) or "impact of AI on creative industries"
    report, trace, elapsed = research(topic)
    print("\n" + "=" * 70 + f"\n{report}\n" + "=" * 70)
    print(f"elapsed: {elapsed:.0f}s")
