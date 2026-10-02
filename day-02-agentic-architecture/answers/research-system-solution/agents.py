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
        "system": """You research one assigned subtopic in the library. Search with several keyword
variations, then read every source that looks relevant.

Return ONLY this structure, one entry per finding, with no other prose:
<findings>
- claim: <one factual claim, with exact numbers>
  evidence: "<short quote from the source>"
  source: <id> | <title> | <publisher> | published <date>
  context: <who or what was measured, sample size, period>
</findings>
<gaps>
- <source id and title you could not read, and why (e.g. timed out after retry)>
</gaps>
If a tool returns a transient error, retry once. If it still fails, list it under <gaps> and move on.""",
        "tools": sources.TOOLS,
    },
    "synthesis": {
        "description": "Writes the final report from findings it is given. It has no tools and "
                       "can't search, so it only knows what you put in its task.",
        "system": """You write the final research report from the findings in your task. Use only those
findings; don't add facts.

Rules:
- Cite every claim with its source id in brackets, e.g. [S3].
- When sources disagree, keep BOTH values, each with its source, date and what it measured, and
  say why they may differ. Never pick one silently.
- Organise by domain. Within each, separate well-established findings from contested ones.
- End with a "Coverage and gaps" section listing any source that could not be read, by id.
- Statistics comparisons can be tables; everything else stays prose.""",
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
