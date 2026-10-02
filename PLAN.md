# CCA Foundations: 7-day plan (Fri Oct 2 → exam Fri Oct 9)

## Where you stand

- Last score 680, pass 720. The scale is 100–1000 over 60 questions, so the gap is roughly 3–4 more correct answers (inferred; Anthropic doesn't publish the scaling). You don't need new breadth. You need fewer "two answers look right" losses.
- Your two weak spots map onto the exam like this:
  - **"Where does this agent actually live?"** This hits every scenario question, because the right answer often depends on *which layer* should own a behaviour (prompt vs hook vs tool vs CI config vs CLAUDE.md).
  - **Prompt engineering & structured output** is a full domain at 20%.

## What the exam covers (checked against the official Exam Guide v1.0, July 2026)

| # | Domain | Weight | ≈ Qs of 60 |
|---|---|---|---|
| 1 | Agentic architecture & orchestration | 27% | 16 |
| 2 | Tool design & MCP integration | 18% | 11 |
| 3 | Claude Code configuration & workflows | 20% | 12 |
| 4 | Prompt engineering & structured output | 20% | 12 |
| 5 | Context management & reliability | 15% | 9 |

**Format:** 60 items in 120 min, proctored by Pearson VUE. Most items are multiple-choice, but some are **multiple-response**, and each of those states how many answers to pick, so read the stem for "select two". The questions sit under **4 scenarios drawn from a bank of 6**: customer support resolution agent, code generation with Claude Code, multi-agent research system, developer productivity with Claude (built on the Agent SDK), Claude Code for CI, and structured data extraction.

**Your old score report** shows percent-correct per domain (guide §10). If you still have it, send me those five numbers and I'll shift time toward the weakest domains.

**Out of scope** (guide §17): deploying or hosting MCP servers (infra, networking, containers), specific AWS/GCP/Azure configs, auth and key rotation, rate limits and pricing maths, streaming, prompt-caching details, vision, computer use, embeddings and fine-tuning. The deployment picture in the Day 1 lesson is there so you can reason about *which layer owns a behaviour*. The exam won't test Kubernetes.

**Official extras to use:** the guide's 12 sample questions (§9) and its 4 preparation exercises (§8). The builds below follow those exercises. The guide says the sample questions come from an official practice test, so if Skilljar offers it, take it on Day 6 instead of my mock.

## The daily rhythm (~2.5–3 h/day)

1. **Notes (40 min).** Read the day's note. Every note has deployment diagrams, because that's your gap.
2. **Build (60–75 min).** A small, runnable piece of Python that calls the real Claude API with your key, which lives in a git-ignored `.env`. Each build ships with scripted scenarios that show PASS/FAIL, plus free unit tests for the parts that must be deterministic. A run costs a few cents.
3. **Quiz (30 min).** 12–15 scenario questions, timed at 2 min each, with some multiple-response items from Day 2 on. Answer keys are in separate files.
4. **Error log (15 min).** For every miss, write one line in `error-log.md`: *what I picked → why it's wrong → the rule.* Day 7 is built from this file.

## Day by day

| Day | Date | Focus | Build | Quiz |
|---|---|---|---|---|
| 1 | Fri Oct 2 | **Deployment mental model.** Where the code, prompts, config, tools, state and secrets of each scenario live and run. Workflow vs agent. | **Official Exercise 1, live:** run a support agent on the real API, then fix its tool descriptions, refund hooks and escalation prompt until 6/6 scenarios pass. | Q1: deployment & ownership (12) + the guide's 12 sample Qs (§9) |
| 2 | Sat Oct 3 | **D1 Agentic architecture (27%).** Agent loop & `stop_reason`, hub-and-spoke, `Task`/subagents and isolated context, hooks vs prompts, decomposition, sessions (`--resume`, `fork_session`). | **Official Exercise 4, live:** a coordinator with 2 subagents (`Task`-style delegation), parallel calls in one turn, structured errors from a simulated timeout, and claim→source provenance. Extend Day 1's agent with multi-concern requests. | Q2 (15) |
| 3 | Sun Oct 4 | **D4 Prompt engineering, part 1 (weak spot).** Explicit criteria vs vague, few-shot (2–4 targeted, with rationale), XML structure, `tool_use` + JSON Schema, `tool_choice` auto/any/forced, nullable fields, `"other"`/`"unclear"` enums. | **Official Exercise 3, part 1:** an extraction tool with required/optional/nullable fields and an `"other"` + detail enum, forced via `tool_choice`, plus a validator. Rewrite 5 bad prompts into good ones. | Q3 (15) |
| 4 | Mon Oct 5 | **D4 part 2 + CI/CD.** Validation-retry with concrete errors (and when retry is useless), semantic vs syntax errors, Batch API (50%, ≤24 h, `custom_id`, no multi-turn tools), multi-pass and independent review, `claude -p`, `--output-format json`, `--json-schema`. | **Exercise 3, part 2:** a validation-retry loop and a batch plan (custom_id, SLA maths). Then a GitHub Actions review job: `claude -p` with explicit criteria, `--output-format json --json-schema`, and an independent reviewer pass. | Q4 (15) |
| 5 | Tue Oct 6 | **D3 Claude Code config (20%) + D2 Tools & MCP (18%).** CLAUDE.md hierarchy, `@path`, `.claude/rules/` with `paths:`, commands vs skills (`context: fork`, `allowed-tools`), plan mode vs direct, `.mcp.json` vs `~/.claude.json`, env-var secrets, tool descriptions, tool count per agent, `isError` + error categories. | **Official Exercise 2:** a project CLAUDE.md, `.claude/rules/` with `paths:` globs, a skill with `context: fork` + `allowed-tools`, `.mcp.json` with `${ENV}` alongside a personal server in `~/.claude.json`, and plan mode vs direct on three tasks. | Q5 (15) |
| 6 | Wed Oct 7 | **D5 Context & reliability (15%) + full mock.** Case-facts block, trimming tool output, lost-in-the-middle, escalation triggers, error propagation, provenance, stratified sampling. Then a **timed 60-question mock exam** (120 min). | No build. Mock exam under real conditions (the official practice test if Skilljar has it), with multiple-response items included. | Mock 1 (60) |
| 7 | Thu Oct 8 | **Consolidate.** Review mock misses and the error log. Re-drill your weakest domain with 20 targeted questions. Read the one-page cheat sheet. Stop by evening. | None | Targeted (20) |
| — | Fri Oct 9 | **Exam.** Skim the cheat sheet, answer every question, flag and return. | | |

## Rules that settle most "two answers look right" questions

These come up again and again. Each later day goes deeper on them.

1. **Guarantee vs encourage.** If a business rule *must* hold (refund limits, identity verification before payment), the answer is code: a hook, precondition or tool-side check. Prompt wording only makes the behaviour likely.
2. **Fix it at the layer that owns it.** Tool misrouting gets fixed in the tool description, not the system prompt. A team convention goes in project CLAUDE.md, not user-level. A secret goes in an env var, not `.mcp.json`.
3. **Subagents don't inherit context.** Whatever they need goes in their prompt.
4. **Structured beats generic.** That applies to error objects (category, retryable, partial results), handoff summaries and output schemas.
5. **Prefer the simplest thing that works.** A fixed pipeline beats a dynamic agent when the steps are known. Batch beats sync when nobody is waiting. Splitting tools beats a mega-tool.
6. **Explicit criteria and examples beat adjectives.** "Be more careful" and "only high-confidence" are almost always the wrong answer.
7. **Pick the proportionate first step.** In the official samples, a routing classifier, a separately trained ML model or a merged mega-tool lose to "fix the description" or "add explicit criteria with few-shot examples". Heavier machinery is right only once the cheap fix has been tried or a guarantee is needed (rule 1).
8. **Self-reported confidence and sentiment are unreliable signals** for escalation. Confidence only becomes useful when it's calibrated against labelled data.

## Where things are

See the [README](README.md) for the repo layout. Each day has its own folder with `lesson/`, `homework/` and `answers/`. Folders for days 2–7 are added as each day comes.
