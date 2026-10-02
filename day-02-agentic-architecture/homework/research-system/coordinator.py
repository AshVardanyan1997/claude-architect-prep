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

from agents import AGENTS, spawn
from common import log, run_agent, tool_result

# TODO(exercise 1): replace the procedure with research goals and quality criteria.
COORDINATOR_PROMPT = """You coordinate a research team and produce cited reports.

Follow these steps exactly:
1. Delegate search tasks for the topic's subtopics. For creative industries, the subtopics are
   AI in digital art, AI in graphic design, and AI in photography.
2. When the searches are done, delegate the report to the synthesis agent.
3. Return the synthesis agent's report as your final answer, unchanged."""

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
    # TODO(exercise 4): these run one after another. Use concurrent.futures.ThreadPoolExecutor
    # so that several delegations in the same response run at the same time.
    results = []
    for call in calls:
        log(trace, "coordinator", "delegate-start", f"{call.input['agent']}: {call.input['task']}", verbose)
        output = spawn(call.input["agent"], call.input["task"], trace, verbose)
        log(trace, "coordinator", "delegate-end", f"{call.input['agent']} returned {len(output)} chars", verbose)
        results.append(tool_result(call.id, output))
    return results


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
