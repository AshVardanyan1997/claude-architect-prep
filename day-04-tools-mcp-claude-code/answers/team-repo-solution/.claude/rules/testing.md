---
paths: ["**/test_*.py"]
---

# Testing conventions

- Test files are named `test_<module>.py` and sit next to the module they test.
- One behaviour per test, named `test_<function>_<behaviour>`.
- No network in unit tests; use the fixtures in `tests/fixtures/`.
