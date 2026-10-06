# acme-shop

Rules every session needs, whatever file is open. Topic rules live in `.claude/rules/`
and load only for matching files; billing has its own `src/billing/CLAUDE.md`.

- Python 3.12. Format with ruff. Type hints on every public function.
- Never commit secrets. Credentials come from environment variables.
- Run `pytest -q` before saying a change is done.
