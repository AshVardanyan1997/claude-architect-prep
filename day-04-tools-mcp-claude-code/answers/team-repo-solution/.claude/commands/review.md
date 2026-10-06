Review the uncommitted changes (`git diff HEAD`) against this repo's CLAUDE.md and `.claude/rules/`.

Report only: bugs that change behaviour, violations of a written rule (quote the rule), and missing tests
for new branches. Skip style that ruff already enforces.

For each finding give file:line, the issue, and a suggested fix. If nothing qualifies, say "No findings".
