# acme-shop

<!-- EXERCISE 1 (exam 3.1, 3.3). This file is loaded into EVERY session, for
every teammate, whatever file they're editing. Split it:
  - keep only universal rules here (short)
  - API conventions   -> .claude/rules/api.md      loaded only for src/api/**
  - test conventions  -> .claude/rules/testing.md  loaded only for test files,
    which live in several folders (so a folder CLAUDE.md is the wrong tool)
  - billing standards -> src/billing/CLAUDE.md that @imports docs/billing-standards.md
  - the personal preference at the bottom isn't a team rule: where does it go?
Delete this comment when you're done. -->

## Universal
- Python 3.12. Format with ruff. Type hints on every public function.
- Never commit secrets. Credentials come from environment variables.
- Run `pytest -q` before saying a change is done.

## API conventions
- Every handler returns `{"data": ...}` on success or `{"error": {"code", "message"}}` on failure.
- Error codes are snake_case: not_found, invalid_input, forbidden.
- Never raise from a handler; return the error shape.

## Testing conventions
- Test files are named `test_<module>.py` and sit next to the module they test.
- One behaviour per test, named `test_<function>_<behaviour>`.
- No network in unit tests; use the fixtures in `tests/fixtures/`.

## Billing
- See docs/billing-standards.md. Money must be Decimal in new code.

## Me
- I prefer short answers, and explain things to me in Armenian when I ask "why".
