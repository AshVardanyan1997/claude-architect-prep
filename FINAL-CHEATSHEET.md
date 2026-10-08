# Final cheat sheet (read tomorrow morning, 15 min)

## Your personal traps (from the mock and the error log)

1. **Bash is the last resort.** Grep finds text, Glob finds files, Edit changes unique text, and Read + Write is the fallback when Edit fails. Never `sed`. (Mock Q05, and the Day 4 drill again.)
2. **"Root cause" → pick a cause, not a fix.** If the tool descriptions are good and routing is still wrong, look for **system-prompt wording** that primes the wrong tool. (Q24, Q56)
3. **Ask "what caused this?" before "what blocks this?".** Hooks and forced `tool_choice` are for must-never rules. A vague instruction or description gets made **specific**, in the place where it lives. (Q12, Q51)
4. **Few-shot teaches judgment, not coverage.** 2–4 examples on ambiguous cases, each with *why*. Not a dictionary, and not 20 examples. (Q40, Q46)
5. **Coordinator sizing.** Delegate what's big or would flood the coordinator's context; do small, scoped work directly. Only run the subagents a query needs. (Q27, Day 2 Q4)
6. **An empty result is a success.** Errors are for access failures. If the tool already returns the right shape, the agent is the part to fix. (Q20)

## The 8 rules that settle "two answers look right"

1. Guarantee vs encourage: a rule that *must* hold goes in code (a hook or precondition). Everything else goes in the prompt.
2. Fix it at the layer that owns it: tool description, CLAUDE.md, rules, schema, validator.
3. Subagents inherit nothing. Pass complete, structured findings.
4. Structured beats generic: error objects, handoffs, output schemas.
5. The simplest thing that works: a fixed pipeline beats an agent, batch beats sync, split tools beat a mega-tool.
6. Explicit criteria and examples beat adjectives ("be careful", "high confidence").
7. Proportionate first step: a cheap fix before new machinery.
8. Self-reported confidence and sentiment aren't escalation signals.

## Domain quick facts

**D1 Agentic (27%):** continue on `stop_reason == "tool_use"` and stop on `"end_turn"`; never parse text or rely on a hard iteration cap. Hub-and-spoke: the coordinator decomposes, so a narrow report means the decomposition was narrow. Parallel = several `Task` calls in **one** response. Goals + quality criteria, not step lists. Resume when context is mostly valid and say what changed; start fresh with a summary when tool results are stale. `fork_session` = compare approaches from the same point.

**D2 Tools/MCP (18%):** description = selection: purpose, input with example, output, when to use the other tool. Overlap → rename or split. Errors: `errorCategory` (transient / validation / business / permission) + `isRetryable` + message. 4–5 tools per agent; narrow cross-role tools are fine. `.mcp.json` = team, `${VAR}` for secrets; `~/.claude.json` = personal. MCP tool ignored for Grep → improve its description. Resources = content catalogs. Use a community server for standard integrations like Jira.

**D3 Claude Code (20%):** `~/.claude/CLAUDE.md` is personal and not shared; check with `/memory`. Use `.claude/rules/*.md` + `paths:` globs for conventions spread across folders. `@import` pulls in package-specific docs. Commands live in `.claude/commands/` (team) or `~/.claude/commands/`. Skill frontmatter: `context: fork` (isolation), `allowed-tools` (restrict), `argument-hint`. A personal variant goes in `~/.claude/skills/` under another name. Plan mode for multi-file work or several valid designs; direct execution for a clear, scoped fix. The Explore subagent holds verbose discovery. Iteration: I/O examples, tests first, the interview pattern; put interacting issues in **one** message.

**D3.6 CI:** `claude -p` (non-interactive, so it doesn't hang). `--output-format json --json-schema` gives parseable findings for PR comments. CLAUDE.md supplies the CI context (test standards, fixtures, review criteria). On a re-run, include the prior findings and report only new or unresolved ones. Give it the existing tests so it doesn't duplicate them. **Use an independent instance to review generated code.**

**D4 Prompts & output (20%):**
- Explicit criteria; temporarily disable a high-false-positive category; define each severity level with a code example.
- `tool_use` + JSON schema kills *syntax* errors but not *semantic* ones.
- `tool_choice`: `auto` may return text, `any` must call some tool, `{"type": "tool", "name": …}` must call that one.
- Nullable fields where the source may lack data; `"other"` + detail; `"unclear"`; normalisation rules in the prompt.
- **Retry with error feedback:** send the document + the failed extraction + the specific error. Retrying is **useless when the information isn't in the source**. Extract `calculated_total` next to `stated_total`, and use a `conflict_detected` flag.
- `detected_pattern` field → lets you analyse why developers dismiss findings.
- **Batch API:** 50% cheaper, up to 24 h, no latency SLA, **no multi-turn tool calls**, `custom_id` to match results, resubmit only failures (chunk the oversized ones). Use it for overnight or weekly jobs, **never** for blocking pre-merge checks. SLA maths: 24 h of processing inside a 30 h SLA → submit every 4 h. Refine the prompt on a sample first.
- **Review:** self-review in the same session is weak, so use an independent instance. For large reviews, run per-file passes plus a cross-file integration pass.

**D5 Context & reliability (15%, your strongest):** a case-facts block; trim verbose tool output; escalate on an explicit human request, a policy gap or no progress, not on sentiment; propagate structured errors with partial results; keep claim→source provenance and conflicting values side by side.

## In the exam room

- Read the last line of the stem first: *root cause*, *first step*, *most effective*, *select TWO*.
- Eliminate options that act on a different component from the one asked about.
- Flag and move on after 2 minutes. 60 questions in 120 minutes.
