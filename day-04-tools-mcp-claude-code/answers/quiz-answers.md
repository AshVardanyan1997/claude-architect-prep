# Day 4 quiz: answers and reasoning

Multiple-response questions score only if every pick is right. 12+ means you're on track.

| Q | Answer | Rule (task) |
|---|---|---|
| 1 | **C** | User-level `~/.claude/CLAUDE.md` applies only to that user and isn't in git. Move team rules to the project level and check with `/memory` (3.1). |
| 2 | **A** | Glob-pattern rules beat folder CLAUDE.md files for conventions spread across the codebase (3.3). B is 30 copies to maintain, C loads for every task, and D relies on people remembering. |
| 3 | **D** | `context: fork` isolates verbose output in a sub-agent (3.2). A limits tools but not output, and C throws away the context you wanted to keep. |
| 4 | **B, C** | Shared servers go in project-scoped `.mcp.json`, with `${VAR}` expansion so secrets stay out of git (2.4). A and E commit secrets; D isn't shared. |
| 5 | **B** | Enhance the MCP tool's description so the agent prefers it over built-in tools (2.4). A breaks every other Grep use, and C is a prompt rule where the description is the mechanism. |
| 6 | **C** | Rename and differentiate to remove functional overlap. This is the guide's own example (2.1). A recreates a generic tool, and B is a prompt rule fighting the descriptions. |
| 7 | **D** | Uniform errors prevent recovery decisions. Category + retryable + message lets the agent choose (2.2). |
| 8 | **B** | Distinguish access failures from valid empty results (2.2). A still calls it an error. |
| 9 | **A, C** | Business-rule violations are non-retryable and carry a customer-friendly explanation (2.2). B is the wrong category, D kills the workflow, and E lies. |
| 10 | **A** | Too many tools degrades selection, and agents misuse tools outside their role. Scope tools to the role (2.3). B is a prompt-level patch, and D forces tool calls without fixing the choice. |
| 11 | **C** | Plan mode for large, multi-file changes with several valid approaches, then direct execution of the plan (3.4). |
| 12 | **B** | Direct execution for a well-scoped fix with a clear stack trace (3.4). Planning adds no value here. |
| 13 | **D** | When Edit can't find unique anchor text, Read + Write is the reliable fallback (2.5). B changes all four occurrences, and A can't edit. |
| 14 | **A** | Personal variants go in `~/.claude/skills/` under a different name, so teammates aren't affected (3.2). D adds it for the whole team. |
| 15 | **A, B** | Concrete input/output examples fix inconsistent interpretation, and the interview pattern surfaces unknowns in unfamiliar domains (3.5). D is wrong for *interacting* problems, which belong in one message. C and E are adjectives. |

## Pattern to notice

Questions 1, 4 and 14 come down to **who gets it**: the repo (team) or `~/` (you). Questions 5, 6 and 10 come down to **the tool description and tool list, not the system prompt**. Whenever an option adds a prompt rule to fix tool routing ("Always use X", "Don't search"), look for the option that fixes the tool itself.
