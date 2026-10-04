"""Subagent definitions, and how a subagent is spawned.

This is the hand-built equivalent of the Agent SDK's AgentDefinition: each
subagent has a description (the coordinator reads it to decide who to use), a
system prompt and a restricted toolset (exam tasks 1.3 and 2.3).

EXERCISE 2 (exam tasks 1.3 and 5.6): the search agent returns loose prose, so
source ids and dates are lost on the way to the synthesis agent, and the
synthesis prompt makes it pick ONE number when sources disagree. Fix both
prompts so that claim -> source mappings survive all the way to the report.
"""

import sources
from common import run_agent, tool_result

AGENTS = {
    "search": {
        "description": "Finds and reads sources in the research library on one assigned subtopic. "
                       "Give it a specific subtopic, not the whole question.",
        # TODO(exercise 2): ask for structured findings instead of prose.
        "system": "You are a research assistant. Search the library for the subtopic you're given, "
                  "read the relevant sources, and summarize what you learned in a few paragraphs. "
                  "The finding have to be returned in a specific structure - claim, evidence quote, source id, title, date and what was measured.",
        "tools": sources.TOOLS,
    },
    "synthesis": {
        "description": "Writes the final report from findings it is given. It has no tools and "
                       "can't search, so it only knows what you put in its task.",
        # TODO(exercise 2): keep conflicting values with attribution, cite sources, mark gaps.
        "system": "You write clear research reports. When sources give different numbers for the same "
                  "statistic, choose the most reliable one so the reader gets a single clear answer. "
                  "Use `[S3]` style ids for citation, keep conflicting numbers side by side with their sources and end with coverage-gaps sections.",
        "tools": [],
    },
}


def spawn(agent_name: str, task: str, trace: list, verbose: bool = True) -> str:
    """Start a subagent in a FRESH conversation. It sees only `task`, never the coordinator's history."""
    spec = AGENTS[agent_name]

    def execute(calls):
        # Subagent tool calls are cheap and local, so run them one by one.
        return [tool_result(c.id, sources.run(c.name, c.input)) for c in calls]

    return run_agent(agent_name, spec["system"], spec["tools"], task, execute, trace, verbose)
