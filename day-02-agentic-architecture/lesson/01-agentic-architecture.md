# Day 2: Agentic architecture & orchestration (27% of the exam, the biggest domain)

**Goal for today:** for any agent question, you can say what runs the loop, what each agent can see, who decides the next step, and which layer enforces the rules.

This lesson follows the official task statements 1.1–1.7. You already built two pieces of this on Day 1 (the loop, and hooks as guarantees). Today adds multi-agent systems.

---

## 1. The agentic loop (task 1.1)

```
            ┌──────────────────────────────────────────────┐
            │ messages = [user request]                    │
            └──────────────┬───────────────────────────────┘
                           ▼
            ┌──────────────────────────────┐
     ┌────▶ │ call Claude (system, tools,  │
     │      │ full message history)        │
     │      └──────────────┬───────────────┘
     │                     ▼
     │          stop_reason == ?
     │       ┌─────────────┴──────────────┐
     │   "tool_use"                   "end_turn"
     │       ▼                            ▼
     │  append assistant content     done: return text
     │  run EVERY tool_use block
     │  append ALL tool_results
     └─ in ONE user message
```

The only correct stop signal is `stop_reason`. These three anti-patterns are favourite distractors:

| Anti-pattern | Why it's wrong |
|---|---|
| Parsing the text for "I'm done" / "Task complete" | Natural language is not a control signal. The model can say "done" and still request a tool. |
| A fixed iteration cap as the *main* way to stop (e.g. "stop after 5 loops") | It cuts off legitimate work and hides real looping bugs. A cap is fine as a safety net, not as the design. |
| "If the response contains text, it's finished" | Responses often contain text *and* `tool_use` blocks together. |

**Model-driven vs pre-configured:** in an agent, Claude picks the next tool from context. In a pre-configured decision tree or fixed sequence, your code picks. Use the second when the steps are known (Day 1, section 3).

---

## 2. Hub-and-spoke multi-agent systems (task 1.2)

```
                           ┌──────────────────────────┐
         user request ───▶ │       COORDINATOR        │ ───▶ final report
                           │ tools: [Task / delegate] │
                           │ decomposes, routes,      │
                           │ evaluates, retries       │
                           └──┬─────────┬──────────┬──┘
                    task+ctx  │         │          │  task+ctx
                    ┌─────────▼──┐ ┌────▼──────┐ ┌─▼────────────┐
                    │ search     │ │ analysis  │ │ synthesis    │
                    │ subagent   │ │ subagent  │ │ subagent     │
                    │ own prompt │ │ own prompt│ │ no tools     │
                    │ own tools  │ │ own tools │ │              │
                    └────────────┘ └───────────┘ └──────────────┘
          Subagents never talk to each other. Everything goes through the hub.
```

What the exam expects you to know:
- **The coordinator owns all communication**, error handling and routing. Routing everything through it gives you observability and consistent error handling.
- **Subagents have isolated context.** They don't inherit the coordinator's history and don't share memory between calls.
- **The coordinator decides which subagents to use** based on the query. A simple question shouldn't go through the full pipeline.
- **The classic failure is decomposition that's too narrow.** If the coordinator splits "AI in creative industries" into digital art, graphic design and photography, every subagent can do its job perfectly and the report still misses music, writing and film. The root cause is the coordinator's decomposition, not the subagents. That's official sample question 7, and it's exercise 1 in today's build.
- **Partition the scope** so subagents don't duplicate each other (distinct subtopics or source types).
- **Iterative refinement:** the coordinator reads the synthesis, finds gaps, re-delegates targeted searches, and re-runs synthesis until coverage is good enough.

---

## 3. Spawning subagents and passing context (task 1.3)

**Where this lives in the Agent SDK:**

| Concept | In the Agent SDK | In today's hand-built version |
|---|---|---|
| The tool that spawns a subagent | `Task` tool | `delegate` tool in `coordinator.py` |
| Permission to spawn | `allowedTools` must include `"Task"` | `delegate` is in the coordinator's tool list |
| Subagent definition | `AgentDefinition`: description, system prompt, tool restrictions | `AGENTS` dict in `agents.py` |
| Parallel subagents | Several `Task` calls in **one** coordinator response | Several `delegate` calls in one response, run in a thread pool |
| Exploring alternatives from a shared baseline | `fork_session` | (not built) |

Rules that come up again and again:
1. **Put the complete prior findings in the subagent's prompt.** "Synthesize the research" with no findings attached produces a generic report.
2. **Separate content from metadata** with a structured format: claim, evidence, source URL or ID, document name, page, date. That's how attribution survives the hand-offs.
3. **Parallel means one response with several Task calls**, not one Task call per turn across several turns.
4. **Write coordinator prompts as goals and quality criteria, not step-by-step procedures.** Procedures make the system rigid, which is exactly how the narrow decomposition above happens.

---

## 4. Enforcement and handoffs (tasks 1.4, 1.5): Day 1 recap

- Required ordering or rules that involve money → **programmatic prerequisites and hooks**. Prompts have a non-zero failure rate.
- `PostToolUse`-style hooks **transform results** before the model sees them: normalise timestamps and status codes, trim fields.
- Hooks that intercept **outgoing calls** block policy violations and **redirect** the agent, for example to human escalation.
- **Multi-concern requests** ("refund this AND update my address AND why was I double-charged") get decomposed into separate items, investigated (in parallel where possible), then answered in one unified reply.
- **Escalation handoffs** are structured (customer ID, root cause, amount, recommended action) because the human can't see the transcript.

---

## 5. Decomposition strategies (task 1.6)

| | Fixed pipeline / prompt chaining | Dynamic adaptive decomposition |
|---|---|---|
| Use when | The steps are known and predictable | The task is open-ended and the next step depends on what you find |
| Example | Code review: per-file pass, then a cross-file integration pass | "Add comprehensive tests to this legacy codebase" |
| Shape | Your code sequences the calls | Map the structure → find high-impact areas → prioritised plan that adapts as dependencies appear |

**Big code reviews:** split them into per-file local passes plus a separate integration pass. One pass over 14 files dilutes attention and produces inconsistent, contradictory feedback (official sample question 12). A bigger context window does *not* fix attention dilution.

---

## 6. Sessions: resume vs fork vs start fresh (task 1.7)

```
 Monday:   claude --resume auth-investigation      ← named session, context still valid
                    │
 Tuesday:  code changed ─┬─▶ resume + tell it WHICH files changed (targeted re-analysis)
                         │
                         └─▶ if most earlier tool results are now stale:
                             start a NEW session and inject a structured summary
                             (more reliable than resuming on stale results)

 fork_session:  one shared analysis baseline ──┬──▶ branch A: try refactoring approach 1
                                               └──▶ branch B: try approach 2 (independent)
```

- **Resume** when the earlier context is mostly still true.
- **Fresh session + summary** when the earlier tool results are stale.
- **Fork** to compare divergent approaches from the same starting analysis.
- After resuming, tell the agent exactly what changed. Don't make it re-explore everything.

---

## 7. Decision cheat sheet

| Question says… | Reach for… |
|---|---|
| "subagents ignore earlier findings" | pass findings explicitly in the subagent prompt (no inheritance) |
| "report misses whole areas, subagents all succeeded" | coordinator decomposition too narrow |
| "slow, subagents run one after another" | several Task calls in one coordinator response |
| "subagent misuses a tool outside its role" | restrict its toolset; give a narrow scoped tool for the common case |
| "must always / must never" + money or identity | hook / programmatic prerequisite |
| "loop stops early / runs forever" | control flow on `stop_reason`, not text or a counter |
| "large review gives inconsistent comments" | per-file passes + an integration pass |
| "resumed session gives outdated answers" | tell it what changed, or start fresh with a summary |

---

**Next:** [`../homework/`](../homework/). Start with the prompt drill.
