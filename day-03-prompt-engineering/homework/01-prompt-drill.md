# Day 3 homework, part 1: rewrite five bad prompts (25 min, blank page)

Each prompt below comes from one of the exam's scenarios and has the defects the exam marks wrong. For each one:

1. **Name the defect** in one line, using the lesson's words (vague adjective, confidence filtering, no skip criteria, forces fabrication, contradiction, no output format, wrong layer…).
2. **Rewrite it** in a file `homework/prompt-drill.md`. Keep each rewrite under 15 lines, and add one few-shot example where the lesson says examples are the fix.
3. **Name the layer.** If part of the requirement must *always* hold, say which part belongs in code (hook, schema, validator) rather than the prompt.

Don't open `../answers/prompt-drill-answers.md` until all five are written. Then compare and log what you missed in `error-log.md`.

---

**P1. Claude Code in CI, PR review** (`claude -p` in a GitHub Action)

> Review this pull request and point out any problems you find. Be thorough, but only report issues you are highly confident about. Keep comments professional.
> 

**P2. Customer support agent, escalation** (system prompt)

> If the customer seems really upset or the problem is complicated, escalate to a human. Otherwise try your best to help them.

**P3. Structured extraction, research papers** (system prompt; the output goes through an `extract_paper` tool)

> Extract the paper's metadata: title, authors, year, venue, sample size and funding source. Every field is required, so make sure you fill them all in. Output valid JSON.

**P4. Code generation with Claude Code, tests** (a custom slash command)

> Write good unit tests for the function I give you. Make them comprehensive.

**P5. Multi-agent research, synthesis subagent** (subagent system prompt)

> Summarise the findings you're given into a short report. Resolve any contradictions between sources so the reader gets one clear answer, and keep all the important details.

---

**Self-check before you look at the answers.** For each rewrite, ask:

- Could two different people read it and make the same decision on an edge case?
- Does it say what to **skip**, not only what to do?
- Is there anything the model is forced to produce when the input doesn't support it?
- Do any two lines contradict each other?
