---
name: dep-report
description: Report where a third-party package is used in this repo and what would break if it were removed or upgraded.
context: fork
allowed-tools: Read, Grep, Glob, 
argument-hint: "[package_name]"
---

Find every import and use of the package named in $ARGUMENTS.

1. Use Grep to find import statements for it, then Read each file that imports it.
2. List each call site as file:line with the function used.
3. Say which call sites would break on a major-version upgrade, and why.

Return the report only. Don't edit any file.
