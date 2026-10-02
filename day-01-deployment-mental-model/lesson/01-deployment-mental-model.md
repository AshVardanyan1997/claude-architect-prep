# Day 1: The deployment mental model

**Goal for today:** when a question says "an agent resolves support cases", you can picture which files, which process, which machine, and which layer would own any behaviour the question asks about.

---

## 1. The one picture behind every scenario

Every scenario on this exam is a variation of this:

```
          YOUR SIDE (you deploy, you own)                       ANTHROPIC'S SIDE
 ┌──────────────────────────────────────────────────────┐
 │  HOST PROCESS  (a service, a CLI, a CI job)          │
 │                                                      │      ┌──────────────────┐
 │   ┌──────────────┐   request: system prompt,         │      │                  │
 │   │  AGENT LOOP  │── messages, tool definitions ────────────▶│   Claude model   │
 │   │  (your code  │                                   │      │  (Messages API)  │
 │   │  or the SDK) │◀─ response: text and/or tool_use ─────────│   stateless      │
 │   └──────┬───────┘   + stop_reason                   │      └──────────────────┘
 │          │ executes tool calls                       │
 │   ┌──────▼───────┐   ┌──────────────┐                │
 │   │    HOOKS     │   │ STATE STORE  │ history, case  │
 │   │ (code: allow │   │ facts, IDs   │ facts, session │
 │   │ /block/edit) │   └──────────────┘                │
 │   └──────┬───────┘                                   │
 │          ▼                                           │
 │   TOOLS: local functions  or  MCP client ───────────────▶ MCP servers (separate processes:
 │                                                      │    stdio child process, or a remote
 └──────────────────────────────────────────────────────┘    HTTP service) ─▶ CRM, DB, GitHub…
```

Four facts this picture makes obvious:

1. **The model doesn't run your agent.** The model only ever *proposes* (text or a `tool_use` block). Your host process runs the loop, executes the tools and decides what to send next. "The agent" means your loop plus the prompts plus the tools.
2. **The API is stateless.** Conversation memory is whatever your host sends back every turn. If something must survive (order IDs, amounts, verified identity), your host stores it and re-sends it.
3. **Hooks and tool code are deterministic. Prompts are probabilistic.** Anything that *must* happen belongs on the left side of the diagram, in code.
4. **MCP servers are separate programs.** The host connects to them, discovers their tools, and offers those tools to the model. Changing a tool's description means changing the MCP server (or its config), not the system prompt.

---

## 2. "Is the agent just a `.md` file in the repo?"

No, but `.md` files are often its *configuration*. Some runtime always reads them and runs the loop. There are three runtimes on this exam:

| Runtime | What runs the loop | Where it runs | What the `.md`/config files are |
|---|---|---|---|
| **A. Claude Code, interactive** | The `claude` CLI | A developer's laptop or devbox | `CLAUDE.md`, `.claude/rules/*.md`, `.claude/commands/*.md`, `.claude/skills/*/SKILL.md`, `.claude/agents/*.md`, `.mcp.json`. All of them are config the CLI loads. |
| **B. Claude Code, headless** | `claude -p "…"` | A CI runner (e.g. GitHub Actions) | The same repo config. CI adds flags (`--output-format json`, `--json-schema`) and secrets come from the CI secret store. |
| **C. Your own app** (Agent SDK or raw Messages API) | Your service's code. The Agent SDK is the Claude Code engine packaged as a Python/TS library. | Your infrastructure: a container, serverless function or worker | The system prompt is a string or a file in *your service's repo*. Subagents are defined in code (or as agent `.md` files it loads). Hooks are functions in your code. MCP servers are listed in your app config. |

So when the question says *"a customer support agent built with the Claude Agent SDK"*, picture **runtime C**: a backend service, deployed like any other, which calls the Claude API. The `.md` question has a direct answer there. The prompt may well live in `prompts/system.md` in that service's repo, but the agent is the deployed service that loads it.

**Quick test:** *who presses Enter?*
- A developer typing → A (interactive Claude Code)
- A pipeline event (PR opened, nightly cron) → B (headless) or C (job)
- An end user or customer in a product → C (your service)

---

## 3. Workflow or agent?

Anthropic's own distinction ("Building effective agents"):

- **Workflow:** *your code* decides the steps. Prompt chaining, routing, parallel sections, orchestrator-workers, evaluator-optimizer.
- **Agent:** *the model* decides the next step in a loop with tools, until `stop_reason == "end_turn"`.

Exam reflex: **if the steps are known in advance, a fixed workflow is the better answer.** Structured extraction is usually a workflow: one forced tool call, then validation. Open-ended investigation or research is where a dynamic agent earns its cost.

---

## 4. The scenarios, each drawn

> **Scope note (official guide §17):** hosting details such as containers, Kubernetes, gateways and specific cloud services are **out of scope**. They appear below only so the picture feels concrete. What the exam does test is *which layer owns a behaviour* (prompt, tool description, hook, config file, state store), so that's where to put your attention.

### S1. Customer support resolution agent (runtime C)

```
 Customer ──▶ Chat widget / web app ──▶ API gateway
                                            │
                                            ▼
                ┌──────────────────────────────────────────────┐
                │ support-agent service (container, N replicas)│
                │  Agent SDK loop                              │
                │  system prompt: policies, escalation criteria│
                │  + few-shot escalation examples              │
                │  PreToolUse hook: process_refund only if     │
                │    verified_customer_id set AND amount ≤ $500│
                │    else → redirect to escalate_to_human      │
                │  PostToolUse hook: trim/normalise CRM output │
                └───────┬───────────────────────┬──────────────┘
                        │ MCP                   │ read/write
                        ▼                       ▼
     MCP server(s): get_customer,        Session store (Redis/DB):
     lookup_order, process_refund,       history + "case facts" block
     escalate_to_human ──▶ CRM,          (order ID, amounts, verified ID)
     Orders, Billing, Ticketing
                        │
                        ▼  escalate_to_human(structured handoff:
                           customer_id, issue, steps tried, recommended action)
                        Human agent queue
```

Repo for this service:

```
support-agent/
├── src/
│   ├── main.py              # HTTP endpoint: receives the customer message, runs the loop
│   ├── agent.py             # agent options: system prompt, allowed tools, hooks, MCP servers
│   ├── hooks.py             # deterministic rules (refund gate, identity check, normalisation)
│   └── state.py             # load/save history + case facts per conversation
├── prompts/
│   ├── system.md            # role, policies, escalation criteria, output style
│   └── escalation_examples.md   # 2–4 few-shot cases incl. ambiguous ones
├── mcp/
│   └── orders_server/       # an MCP server you own (if no community one fits)
├── config/
│   └── mcp.json             # which MCP servers to connect; tokens via ${ENV_VARS}
├── evals/                   # labelled conversations to test prompt changes
├── Dockerfile
└── deploy/                  # k8s / Cloud Run manifests, secrets references
```

Which layer owns what in S1:

| Requirement in the question | Owner |
|---|---|
| "Must never refund > $500 without approval" | **Hook / tool-side check** (code) |
| "Must verify identity before any account change" | **Precondition in code**, not a prompt instruction |
| "Agent calls the wrong tool for order vs account lookups" | **Tool descriptions** (and possibly splitting or renaming tools) |
| "Escalates too often / too rarely" | **Explicit escalation criteria + few-shot examples** in the system prompt (not sentiment scores or self-rated confidence) |
| "Customer asks for a human" | Escalate **immediately**, no extra investigation |
| "Forgets the order number after a long chat" | **Case-facts block** kept outside the summarised history |
| "Human agents get no context on handoff" | **Structured handoff payload** |

### S2. Claude Code for code generation (runtime A)

```
 Developer laptop
 ┌─────────────────────────────────────────────────────────────┐
 │ $ claude          (CLI process; calls the Claude API)       │
 │   loads:  ~/.claude/CLAUDE.md          ← personal, not in git│
 │           ./CLAUDE.md or .claude/CLAUDE.md ← team, in git    │
 │           ./pkg/CLAUDE.md               ← loaded when working│
 │                                            in pkg/           │
 │           .claude/rules/*.md (paths: globs) ← only for       │
 │                                            matching files    │
 │           .claude/commands/, .claude/skills/, .claude/agents/│
 │           .mcp.json (team servers) / ~/.claude.json (mine)   │
 │   built-in tools: Read Write Edit Bash Grep Glob             │
 └─────────────────────────────────────────────────────────────┘
```

The classic trap: "a new teammate's Claude Code doesn't follow the conventions." The conventions live in `~/.claude/CLAUDE.md` (user level, not in git), so the fix is to move them to project level.

### S3. Multi-agent research system (runtime C, usually a job)

```
 Request (UI or API) ──▶ queue ──▶ research-worker (container/job)
                                   ┌─────────────────────────────────────────┐
                                   │ Coordinator agent  (allowed tools: Task)│
                                   │   decomposes, delegates, evaluates gaps │
                                   │     │ Task      │ Task       │ Task     │
                                   │     ▼           ▼            ▼          │
                                   │  web-search  doc-analysis  synthesis    │
                                   │  subagent    subagent      subagent     │
                                   │  (own prompt, own small toolset,        │
                                   │   FRESH context: gets only what the     │
                                   │   coordinator puts in its prompt)       │
                                   └──────────────┬──────────────────────────┘
                                                  ▼
                                    Report + claim→source map ──▶ storage / UI
```

The subagents are **not separate deployments**. They run in the same process as separate conversations, each with its own system prompt and tools. "Parallel" means the coordinator emits several `Task` calls in one turn. When a subagent fails it returns a structured error (type, what it tried, partial results), and the coordinator decides what to do next.

### S4. Developer productivity with Claude (runtime C, built on the Agent SDK)

The official scenario builds this tool with the Agent SDK, which comes with the same built-in tools as Claude Code (Read, Write, Edit, Bash, Grep, Glob). The same questions also apply to plain Claude Code. An engineer explores an unfamiliar codebase. Grep finds content, Glob finds files by name, Read traces the flow. Verbose exploration is delegated to an **Explore subagent** so the main context stays clean, and findings go in a scratchpad file. MCP servers connect internal systems (issue tracker, docs).

### S5. Claude Code in CI/CD (runtime B)

```
 PR opened ──▶ GitHub Actions runner (ephemeral VM)
               ├─ checkout repo  (brings CLAUDE.md = review standards, fixtures)
               ├─ ANTHROPIC_API_KEY from repo secrets
               ├─ claude -p "<review prompt with explicit criteria>" \
               │      --output-format json --json-schema review.schema.json
               ├─ (optional) second, independent claude -p pass to verify findings
               └─ script turns JSON findings into inline PR comments
```

Headless means no human answers prompts, which is why the run uses `-p`. JSON output is for the script that consumes the results. The reviewer should be a **separate instance** from whatever generated the code. On re-runs, pass in the previous findings so it reports only new or unfixed issues.

### S6. Structured data extraction (runtime C, usually a workflow and not an agent)

```
 Documents ─▶ bucket ─▶ extraction worker
                        ├─ Messages API call with ONE tool "extract_invoice"
                        │    (JSON Schema; tool_choice forces that tool)
                        ├─ validator in code: schema + semantic checks
                        │    (line items sum to stated total? dates sane?)
                        ├─ on failure: retry with the doc + bad output + the
                        │    specific errors  (unless the info isn't in the doc)
                        ├─ low confidence / ambiguous ─▶ human review queue
                        └─ OK ─▶ database
 Nightly backlog ─▶ Message Batches API (50% cheaper, ≤24 h, custom_id per doc)
```

### S7. Conversational assistant (runtime C)

A chat backend holds the history and sends the full history on every turn. Critical facts are pinned at the top, long histories get summarised carefully (exact numbers and dates are kept), and tool output is trimmed before it goes back into context.

---

## 5. "Where does X live?" cheat sheet

| Thing | Lives in |
|---|---|
| System prompt (your app) | Service repo (string or `prompts/*.md`), shipped with each deploy |
| Team conventions for Claude Code | `CLAUDE.md` at project level or `.claude/rules/`, committed to git |
| Personal preferences | `~/.claude/CLAUDE.md`, `~/.claude.json` (never shared) |
| Tool *definitions* (name, description, schema) | Your code (local tools) or the MCP server |
| Tool *implementation* | Your service, or the MCP server process |
| Rules that must hold | Hooks, preconditions, tool-side validation (code) |
| Conversation memory | Your state store; you re-send it every turn |
| Secrets | Env vars / secret manager / CI secrets, referenced as `${VAR}` |
| Team MCP servers | `.mcp.json` (project, in git) |
| Experimental MCP servers | `~/.claude.json` (user) |
| Review standards for CI | `CLAUDE.md` + the prompt in the workflow file |
| Reusable team prompt / workflow | `.claude/commands/` or `.claude/skills/` (in git) |

---

**Next:** do the homework in [`../homework/`](../homework/), starting with `01-build-support-agent.md`, where you run this exact S1 architecture against the real API.
