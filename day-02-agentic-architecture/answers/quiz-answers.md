# Day 2 quiz: answers and reasoning

Multiple-response questions score only if every pick is right. 12+ means you're on track.

| Q | Answer | Rule (task) |
|---|---|---|
| 1 | **C** | `stop_reason` is the only reliable control signal (1.1). A is still parsing natural language, B is an arbitrary cap, and D breaks because text and `tool_use` often arrive together. |
| 2 | **A, C** | The guide names both as anti-patterns (1.1). B, D and E are correct practice. |
| 3 | **C** | Every subagent succeeded, so the decomposition is the defect (1.2). This is the same pattern as official sample Q7 with a different topic: blame the hub, not the spokes. |
| 4 | **A** | The coordinator should pick subagents based on query complexity instead of always running the full pipeline (1.2). B overloads one agent with tools (2.3). C and D treat symptoms. |
| 5 | **B** | The `Task` tool spawns subagents, and the coordinator can only use it if it's in `allowedTools` (1.3). |
| 6 | **B** | Parallel spawning means several `Task` calls in one response, not one per turn (1.3). Batches (D) is for latency-tolerant offline work and doesn't support multi-turn tool calling. |
| 7 | **A, C** | Subagents don't inherit context, so pass the complete findings, structured to keep claim→source attribution (1.3, 5.6). B is false, D wastes work, and E destroys provenance. |
| 8 | **B** | Goals and quality criteria, not step-by-step procedures (1.3). C is wrong: hooks enforce rules, they don't plan research. |
| 9 | **C** | Decompose a multi-concern request, investigate each part using shared context, and synthesise one resolution (1.4). Several concerns isn't an escalation trigger (5.2). |
| 10 | **B** | Normalising heterogeneous formats is the textbook `PostToolUse` use: deterministic, before the model reads it (1.5). A and C are probabilistic, and D is out of your control. |
| 11 | **C** | Open-ended task, so dynamic decomposition: map → prioritise → adapt (1.6). A is a fixed chain for an unpredictable task, B dilutes attention, and D has no coordination. |
| 12 | **A** | Resume when the context is mostly valid, and tell it what changed for targeted re-analysis (1.7). C wastes effort, and B relies on the agent noticing changes it has no reason to look for. |
| 13 | **A, C** | Stale tool results make a fresh start with a structured summary more reliable (1.7). B is the case for resuming, E is the case for `fork_session`, and D is an arbitrary rule. |
| 14 | **B** | Least privilege: a scoped tool for the high-frequency simple case, with complex cases still going through the coordinator (2.3; official sample Q9). A over-provisions, and C creates blocking dependencies. |
| 15 | **C** | Structured error context lets the coordinator retry, choose an alternative, or proceed with partial results and annotate the gap (5.3). B silently suppresses the failure, D kills the workflow over one failure, and A never ends. |

## Pattern to notice

Four questions (3, 7, 14, 15) were about **what information crosses the boundary between agents**. In multi-agent questions, ask: *what does this agent actually see?* It sees only its own prompt, its own tools and what it was explicitly given. Most wrong answers assume an agent knows something it was never told.
