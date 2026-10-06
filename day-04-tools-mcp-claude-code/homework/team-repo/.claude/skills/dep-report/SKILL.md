---
name: dep-report
description: Report where a third-party package is used in this repo and what would break if it were removed or upgraded.
# EXERCISE 2 (exam 3.2): this skill reads many files and prints a long report.
# Add three frontmatter fields:
#   - one that runs it in an isolated sub-agent, so the report doesn't fill the main conversation
#   - one that limits it to read-only tools (Read, Grep, Glob)
#   - one that tells the developer what argument to pass when they type /dep-report with none
# Then delete these comment lines.
---

Find every import and use of the package named in $ARGUMENTS.

1. Use Grep to find import statements for it, then Read each file that imports it.
2. List each call site as file:line with the function used.
3. Say which call sites would break on a major-version upgrade, and why.

Return the report only. Don't edit any file.
