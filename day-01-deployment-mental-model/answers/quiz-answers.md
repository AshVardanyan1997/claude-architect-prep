# Day 1 quiz: answers and reasoning

Score guide: 10+ means you're on track. Fewer than 9 means re-read sections 1, 2 and 5 of the note before tomorrow.

| Q | Answer | Rule |
|---|---|---|
| 1 | **C** | Must-hold business rules go in code (hooks, preconditions). Prompt changes (A, B) only raise the odds, and temperature (D) doesn't create guarantees. |
| 2 | **B** | User-level `~/.claude/CLAUDE.md` isn't shared through git. Team conventions belong in project-level `CLAUDE.md` (or `.claude/rules/`). D works by hand but isn't a fix. |
| 3 | **A** | Subagents start with fresh context. The coordinator must pass in the full prior outputs, ideally structured with sources. C wastes work. D is false: parallel Task calls in one turn run concurrently. |
| 4 | **D** | Batch means 50% off, up to 24 h and no latency SLA, so it fits only work nobody is waiting on. There's no "priority flag" (C). `custom_id` maps results back to documents. |
| 5 | **B** | Headless CI needs `-p`. A more generous timeout (A) just waits longer, `--resume` (C) is unrelated, and moving the prompt (D) doesn't change interactivity. |
| 6 | **A** | The Messages API is stateless (B is false). Your service owns the state, and with several replicas it must be shared (C fails when a request lands on a different replica). D mixes up Claude Code config with app state. |
| 7 | **C** | Project `.mcp.json` is the shared config, and `${ENV_VAR}` substitution keeps secrets out of git. A isn't shared. B defeats the point of a shared file. D adds a custom server where a standard one fits. |
| 8 | **D** | Tool descriptions are the main signal for tool selection, so fix the layer that owns the problem. A patches around it. B makes the ambiguity worse. C breaks every other turn. |
| 9 | **A** | When the steps are known, a fixed workflow (routing + forced tool + code validation) is simpler, cheaper and more predictable than an agent. D skips `tool_use` + schema, which is the reliable way to get valid JSON. |
| 10 | **C** | Progressive summarisation loses exact numbers. Pin transactional facts in a persistent block. A and B don't fix the lossy summary, and D drops the facts entirely. |
| 11 | **D** | Subagents are conversations, not deployments. They live in the same host process with isolated context, and parallelism comes from several Task calls in one turn. |
| 12 | **B** | An explicit request for a human triggers immediate escalation, with no further investigation. Sentiment (C) is an unreliable proxy. A and D ignore the request. |

## Pattern to notice

In most of these questions the wrong answers were "plausible prompt tweaks" or "more machinery". The right answer was the one that **puts the responsibility in the layer that owns it**: code for guarantees, tool descriptions for routing, project config for team behaviour, the state store for memory, and env vars for secrets.
