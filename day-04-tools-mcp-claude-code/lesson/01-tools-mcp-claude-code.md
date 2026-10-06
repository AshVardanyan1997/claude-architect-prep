# Day 4 lesson: Tools & MCP (18%) and Claude Code configuration (20%)

Together these are about 23 of the 60 questions. On the mock you got 7/11 and 9/12. Most misses in these domains come from one thing: **knowing which file or layer owns a behaviour, and who it applies to.** So this lesson starts with a map.

---

## 0. The map: where every Claude Code file lives, and who it reaches

```
 YOUR MACHINE ONLY (never in git)              THE REPO (shared with the team through git)
 ─────────────────────────────────            ─────────────────────────────────────────────
 ~/.claude/CLAUDE.md      your preferences     CLAUDE.md or .claude/CLAUDE.md   project rules, always loaded
 ~/.claude/commands/      your commands        src/billing/CLAUDE.md            loaded when working in that folder
 ~/.claude/skills/        your skills          .claude/rules/*.md + paths:      loaded when editing matching files
 ~/.claude.json           your MCP servers     .claude/commands/*.md            /commands for everyone
   (claude mcp add --scope user)               .claude/skills/<name>/SKILL.md   skills for everyone
 environment variables    the real secrets     .mcp.json                        team MCP servers, ${VAR} for secrets
```

Three questions settle most items in Domain 3:

1. **Who should get it?** Only me → `~/…`. The whole team → the repo.
2. **When should it load?** Always → `CLAUDE.md`. Only for some files → `.claude/rules/` with `paths:`. Only when someone asks → a skill or command.
3. **Is it a secret?** Then it goes in an environment variable, referenced as `${VAR}` in `.mcp.json`. Never the literal value.

**Classic trap:** "A new teammate's Claude ignores our conventions." The conventions are in someone's `~/.claude/CLAUDE.md`, which is user-level and never shared. Move them to the project `CLAUDE.md`. Check what's actually loaded with **`/memory`**.

---

## 1. Domain 3: Claude Code configuration

### 3.1 CLAUDE.md hierarchy

- **Levels:** user (`~/.claude/CLAUDE.md`), project (`CLAUDE.md` at the root, or `.claude/CLAUDE.md`), and directory (`sub/dir/CLAUDE.md`). They combine; they don't replace each other.
- **`@path` imports** keep files modular. A package's CLAUDE.md can `@import` only the standards files relevant to it (`@../../docs/billing-standards.md`).
- **`.claude/rules/`** splits a monolithic CLAUDE.md into topic files (`testing.md`, `api-conventions.md`, `deployment.md`).
- **`/memory`** shows which memory files are loaded. Use it to diagnose "it behaves differently for me and for my teammate".

### 3.3 Path-specific rules

```markdown
---
paths: ["**/*.test.tsx"]
---
Use React Testing Library. One behaviour per test...
```

- A rule loads **only when Claude edits a matching file**, so there's less irrelevant context and fewer tokens.
- **Rule vs directory CLAUDE.md:** if the convention follows a *file type* spread across many folders (tests, migrations, Terraform), use a glob rule. If it belongs to *one folder*, a directory CLAUDE.md is fine.

### 3.2 Commands and skills

| | Project (team) | Personal |
|---|---|---|
| Commands | `.claude/commands/review.md` → `/review` | `~/.claude/commands/` |
| Skills | `.claude/skills/<name>/SKILL.md` | `~/.claude/skills/`, **under a different name** so you don't shadow the team's |

The SKILL.md frontmatter fields the exam names:

| Field | What it does | Use when |
|---|---|---|
| `context: fork` | Runs the skill in an isolated sub-agent, and only its result returns to the conversation | Verbose output (codebase analysis) or exploratory work (brainstorming) |
| `allowed-tools: Read, Grep, Glob` | Restricts which tools the skill may use | Preventing destructive actions |
| `argument-hint: "[package]"` | Prompts for the argument when it's missing | A skill that needs a parameter |

**Skill vs CLAUDE.md:** CLAUDE.md holds universal standards that are *always* loaded. A skill is an *on-demand* workflow for a specific task.

### 3.4 Plan mode vs direct execution

| Use **plan mode** | Use **direct execution** |
|---|---|
| Architectural decisions, several valid approaches | A clear, well-scoped change |
| Large or multi-file changes (a library migration touching 45+ files) | A single-file bug fix with a clear stack trace |
| Unfamiliar code you need to explore safely before committing | Adding one validation check to one function |

- **Combine them:** plan the migration, then execute the plan directly.
- **Explore subagent:** for a verbose discovery phase, so file dumps don't exhaust the main context. Only a summary comes back.

### 3.5 Iterative refinement

- If prose descriptions are interpreted inconsistently, give **2–3 concrete input → output examples** (the same idea as Day 3's few-shot).
- **Test-driven iteration:** write the tests first (expected behaviour, edge cases, performance), then share the failures.
- **Interview pattern:** have Claude ask *you* questions first (cache invalidation? failure modes?) before it builds in an unfamiliar domain.
- **Interacting problems go in one message.** Independent problems can be fixed one at a time.

---

## 2. Domain 2: Tool design and MCP

### 2.1 Tool descriptions

- **The description is how the model chooses a tool.** Minimal or overlapping descriptions ("Analyzes content" vs "Analyzes documents") cause misrouting.
- A good description gives: what the tool is for, the input format **with an example**, what it returns, edge cases, and **when to use the other tool instead**.
- **Fixes, in order:** rewrite the description → rename the tool (`analyze_content` → `extract_web_results`) → split a generic tool into purpose-specific ones (`extract_data_points`, `summarize_content`, `verify_claim_against_source`).
- **Check the system prompt too.** A keyword-heavy instruction ("always *analyse* the content first") can pull the model toward the wrong tool even when the descriptions are good.

### 2.2 Structured errors

```json
isError: true
{"errorCategory": "transient", "isRetryable": true,
 "message": "Carrier timed out. Retry once; if it fails again, tell the user it's temporarily unavailable."}
```

| Category | Example | Retry? |
|---|---|---|
| transient | timeout, service unavailable | yes |
| validation | bad input format, unknown ID | no, fix the input |
| business | over the refund limit, a policy violation | no; give a customer-friendly explanation |
| permission | the key lacks access | no; escalate |

- A generic "Operation failed" **prevents a correct recovery decision**: the agent can't tell retry from give up.
- **An empty result is not an error.** "No orders match" is a successful query.
- **In multi-agent systems** (Day 2): a subagent retries transient failures locally, and passes up only what it can't fix, together with partial results and what it attempted.

### 2.3 Distributing tools

- **4–5 tools per agent, not 18.** More tools make selection less reliable.
- **Scope tools to the role:** a synthesis agent with search tools will misuse them. A narrow cross-role tool for a frequent need (`verify_fact`) is fine.
- Replace generic tools with constrained ones: `fetch_url` becomes `load_document`, which validates that the URL is a document.
- `tool_choice`: see Day 3 (`auto` / `any` / forced).

### 2.4 MCP in Claude Code

- **`.mcp.json`** (project, in git) holds shared team servers, with `${GITHUB_TOKEN}` expansion for secrets. **`~/.claude.json`** (user) holds personal or experimental servers, added with `claude mcp add --scope user`.
- Tools from **all** configured servers are discovered at connection and available **at the same time**.
- If the agent prefers Grep over your MCP tool, **improve the MCP tool's description**: say what it can do that the built-in tools can't.
- **For standard integrations like Jira, use an existing community server.** Build a custom one only for team-specific workflows.
- **MCP resources** expose content catalogs (issue summaries, documentation trees, database schemas), so the agent can see what exists without exploratory tool calls.
- Hosting and deploying MCP servers is **out of scope** for the exam.

### 2.5 Built-in tools

| Need | Tool |
|---|---|
| Find files by name or extension (`**/*.test.tsx`) | **Glob** |
| Find text inside files (callers of a function, an error message) | **Grep** |
| Change one unique piece of text | **Edit** |
| Edit fails because the anchor text isn't unique | **Read** the whole file, then **Write** it |
| Understand unfamiliar code | Grep for the entry points, then Read and follow the imports. Don't read everything up front. |
| Trace a function used through wrapper modules | List the exported names first, then Grep for each one |

**Bash is the fallback, not the first pick.** When a built-in tool fits, the exam picks it over `sed`/`grep` in Bash: Grep to find the occurrences, then Edit each one. A blanket `sed` can't be reviewed change by change and hits every match, including comments and fixtures. (You missed this one on the mock.)

---

## 3. Cheat sheet: phrase in the stem → answer

| The stem says… | Pick… |
|---|---|
| a new teammate doesn't get the conventions | move them from `~/.claude/CLAUDE.md` to the project CLAUDE.md; check with `/memory` |
| conventions for test files spread across the repo | `.claude/rules/testing.md` with `paths: ["**/*.test.*"]` |
| CLAUDE.md is huge and mostly irrelevant to each task | split it into `.claude/rules/` topic files with `paths:` |
| each package needs different standards docs | `@import` in each package's CLAUDE.md |
| a skill's output floods the conversation | `context: fork` |
| a skill must not modify files | `allowed-tools` restricted to read-only tools |
| a personal tweak to a team skill | a copy in `~/.claude/skills/` under a **different name** |
| a team-wide command | `.claude/commands/` (in git) |
| a migration across 45 files, or choosing between designs | plan mode, then execute |
| a one-line fix with a stack trace | direct execution |
| the token is in `.mcp.json` | `${ENV_VAR}` expansion |
| an experimental server only for me | `~/.claude.json` (user scope) |
| the agent uses Grep instead of the MCP tool | improve the MCP tool's description |
| two tools with near-identical descriptions | rename and differentiate, or split |
| "Operation failed" everywhere | errorCategory + isRetryable + a message |
| an agent with 18 tools picks the wrong ones | scope it to the 4–5 its role needs |
| Edit fails on non-unique text | Read + Write |
| replace a string across files: Bash `sed` or Grep + Edit? | Grep + Edit |
