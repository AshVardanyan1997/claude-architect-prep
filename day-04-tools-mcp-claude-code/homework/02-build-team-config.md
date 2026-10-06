# Day 4 homework, part 2: configure Claude Code for a team (75 min)

This is the guide's official Exercise 2. `team-repo/` is a tiny shop backend ("acme-shop"). The Python code barely matters. What matters is the configuration around it, which is wrong in the ways the exam asks about:

| Starting state | Exam task |
|---|---|
| One `CLAUDE.md` mixes universal rules, API rules, test rules and a personal preference | 3.1, 3.3 |
| The `dep-report` skill floods the main conversation and could write files | 3.2 |
| `.mcp.json` has a token pasted into it, committed to git | 2.4 |
| The MCP server has two overlapping tools called `get_data` and `get_info`, and every error is "Operation failed" | 2.1, 2.2 |

Parts A to C are **free**: you edit files and `verify.py` checks them. Part D uses **Claude Code** with your API key, so it costs a few cents.

## Setup

```powershell
C:\venvs\ccarf\Scripts\Activate.ps1
cd day-04-tools-mcp-claude-code\homework\team-repo
pip install -r requirements.txt       # the MCP Python SDK
python verify.py                      # free: 3 of 24 pass at the start
```

Part D needs Claude Code. If `claude --version` doesn't work, install it with `irm https://claude.ai/install.ps1 | iex` in PowerShell. When it asks how to sign in, choose your API key.

## Part A: CLAUDE.md and rules (20 min, exercise 1)

The comment at the top of `CLAUDE.md` lists what goes where. Create:

- `.claude/rules/api.md` with frontmatter `paths:` so it loads only for `src/api/**`
- `.claude/rules/testing.md` with a `paths:` glob matching test files **in any folder**. Ask yourself why a `src/api/CLAUDE.md` would be the wrong tool here.
- `src/billing/CLAUDE.md`, which pulls in `docs/billing-standards.md` with an `@` import (the path is relative to the file doing the importing)
- your personal line about answers in Armenian goes in **your** `~/.claude/CLAUDE.md` (on Windows, `C:\Users\<you>\.claude\CLAUDE.md`). It doesn't go in the repo.

Frontmatter looks like this:

```markdown
---
paths: ["some/glob/**/*"]
---
```

## Part B: a skill and a command (10 min, exercise 2)

- In `.claude/skills/dep-report/SKILL.md`, add the three frontmatter fields its comment describes.
- Create `.claude/commands/review.md`, a project slash command the whole team gets through git. It should review the uncommitted diff against the repo's rules. Write it with explicit report/skip criteria and an output format (Day 3).

## Part C: MCP config and the MCP server (25 min, exercises 3 and 4)

1. In `.mcp.json`, replace the pasted token with environment-variable expansion: `"${ORDERS_API_TOKEN}"`. The real value comes from your shell, never from git.
2. In `mcp_server/orders_server.py`, follow the docstring: rename the tools, write descriptions that tell them apart, raise structured errors, and return an empty list for a search with no matches.

Run `python verify.py` until it shows 24/24.

## Part D: watch it work in Claude Code (20 min, live)

In PowerShell, from `team-repo`:

```powershell
$env:ORDERS_API_TOKEN = "any-value-works"     # stands in for a real secret
claude mcp add --scope user notes -- python "$PWD\..\personal\notes_server.py"
claude
```

On first start, Claude Code asks you to approve the project's `.mcp.json` server. Say yes. Then, inside Claude Code:

1. `/memory`: which CLAUDE.md files are loaded? Is the billing one in the list yet? (3.1)
2. `/mcp`: both `orders` (project scope, from `.mcp.json`) and `notes` (user scope, from `~/.claude.json`) should be listed together. (2.4)
3. Ask: *"What's the status of order B2210?"* Does it call `lookup_order` rather than grepping the repo? What does it tell you after the transient error? (2.1, 2.2)
4. Ask: *"Add a test to src/billing/test_invoice.py for an empty invoice."* Before it edits, ask it which rules from `.claude/rules/` it's following. The testing rule should appear; the API rule shouldn't. (3.3)
5. Type `/dep-report` with no argument and see the hint. Then run `/dep-report pytest`. The report should come back as a summary, without the file reads filling your conversation. (3.2)
6. **Plan mode vs direct** (3.4). Press Shift+Tab to toggle plan mode. For each task, decide first, then try it:
   - *"`invoice_total` raises KeyError: 'unit_price' when a line is a free item with no unit_price. Treat a missing price as 0."* (one function, clear cause)
   - *"Migrate all money handling from float to Decimal across the repo."* (many files, ordering matters)
   - *"Add caching to the orders API."* (several valid designs; also try *"interview me about the requirements first"*, task 3.5)

   You don't have to let it finish the big ones. Seeing the plan is enough.

Type `/exit` when you're done. To remove the personal server afterwards: `claude mcp remove notes -s user`.

## Notes and push

In `team-repo/NOTES.md`, write one line for each Part D step: what you saw, and the exam rule it shows. Then:

```powershell
git add -A ; git status     # no .env, and no real token anywhere
git commit -m "Day 4 team config" ; git push
```

The reference solution is in `../answers/team-repo-solution/`.
