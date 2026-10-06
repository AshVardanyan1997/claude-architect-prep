# acme-shop (practice repo)

A tiny shop backend used to practise configuring Claude Code for a team. The
Python code is deliberately small. The interesting parts are the configuration
files around it:

| Path | What it is |
|---|---|
| `CLAUDE.md` | Project instructions every teammate's Claude Code loads |
| `.claude/rules/` | Topic rules (you create this) |
| `.claude/skills/dep-report/` | A project skill |
| `.mcp.json` | Project MCP servers, shared with the team through git |
| `mcp_server/orders_server.py` | A small MCP server over the orders API |
| `verify.py` | Free checker for the exercises. Run `python verify.py` |
