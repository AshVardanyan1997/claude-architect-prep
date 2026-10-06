# Reference solution: team config

| Exercise | Files | What changed |
|---|---|---|
| 1 | `CLAUDE.md`, `.claude/rules/api.md`, `.claude/rules/testing.md`, `src/billing/CLAUDE.md` | Root keeps 3 universal rules. API and test rules load by `paths:` glob. Billing `@imports` the shared standards doc. The personal line moved to `~/.claude/CLAUDE.md` (not in the repo). |
| 2 | `.claude/skills/dep-report/SKILL.md`, `.claude/commands/review.md` | `context: fork`, read-only `allowed-tools`, `argument-hint`. `/review` has report/skip criteria and an output format. |
| 3 | `.mcp.json` | `"${ORDERS_API_TOKEN}"` instead of the literal token |
| 4 | `mcp_server/orders_server.py` | `lookup_order` / `search_orders` with descriptions that point at each other, a `ToolError` carrying JSON (`errorCategory`, `isRetryable`, `message`), an empty list for no matches, and an `orders://statuses` resource |

`python verify.py` passes 24/24.
