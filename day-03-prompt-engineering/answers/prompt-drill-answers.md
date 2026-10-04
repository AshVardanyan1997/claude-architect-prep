# Day 3 prompt drill: answers

These are reference rewrites, not the only right ones. Grade yours on whether it fixes the named defects.

---

## P1. CI PR review

**Defects:** "be thorough" plus "only report issues you are highly confident about" is confidence filtering (task 4.1). There are no criteria for what to report or skip, and no output format.

```text
Review the diff in <diff>. Report only these:
- bugs: code whose behaviour differs from what its name, comment or caller expects
- security: injection, secrets in code, missing auth checks, unsafe deserialisation
- a comment whose claim contradicts what the code does
Skip: style, naming, formatting, and any pattern used the same way elsewhere in the repo.

Severity:
- critical: data loss, security hole, crash on a normal path. e.g. `query = f"... {user_input}"`
- major: wrong result on a normal path. e.g. off-by-one in a pagination loop
- minor: wrong only on an edge case. e.g. no handling of an empty list that callers never pass
Report each finding as: file:line, issue, severity, suggested fix. If nothing qualifies, return an empty list.
```

**Layer:** in CI, enforce the format with `--output-format json --json-schema` (Day 4), not with prompt wording.

## P2. Support escalation

**Defects:** "seems really upset" relies on sentiment, which the guide calls an unreliable escalation signal (task 5.2). "Complicated" is vague, and "try your best" adds nothing.

```text
Escalate with escalate_to_human when any of these is true:
1. The customer asks for a human. Do it at once, before investigating.
2. The request needs an exception to policy, or the policy doesn't cover it.
3. You can't make progress after two attempts.
Don't escalate because the customer is upset or the request has several parts. If it's within policy, resolve it.

Example: "This is ridiculous, I've waited a week!" (order in transit, no request for a human)
Why: frustration alone isn't a trigger. Give the status and offer what policy allows.
```

**Layer:** hard limits, such as refunds over $500, belong in a hook. The prompt only covers judgment.

## P3. Paper extraction

**Defects:** "every field is required, so fill them all in" **forces fabrication** of sample size and funding, which many papers lack (task 4.3). "Output valid JSON" is the weakest structured-output method when a tool is already available.

```text
Extract metadata from the paper in <paper> by calling extract_paper once.
- Copy values as printed. Use null for anything the paper doesn't state; never estimate.
- sample_size: the number of participants or items analysed, from the methods or results. Null for theoretical papers.
- funding: from the acknowledgements or funding statement. Null if there isn't one.
- year and venue: from the header or citation line. If only a preprint server appears, the venue is that server.

Example: a paper whose methods say "we surveyed 1,204 nurses" with no funding statement
Why: the sample size is in prose, not a table, so it still counts. No statement means null, not "none".
→ sample_size: 1204, funding: null
```

**Layer:** in the **schema**, make `sample_size` and `funding` nullable. That's the real fix; the prompt explains when to use null. `tool_use` + schema replaces "output valid JSON".

## P4. Test generation

**Defects:** "good" and "comprehensive" are adjectives, with no criteria for what to cover, what to skip or what format to use.

```text
Write pytest tests for the function in <code>.
Cover: each branch (each if/else and early return), boundary values for every numeric or length parameter,
and every error the function raises.
Skip: tests for trivial getters, and tests that only re-check the implementation line by line.
Follow the fixtures and naming in tests/conftest.py. One behaviour per test, named test_<function>_<behaviour>.

Example: for `def discount(total): return 0 if total < 100 else total * 0.1`
Why: the branch boundary is 100, so test both sides of it, not two random values.
→ test_discount_below_threshold (99.99 → 0), test_discount_at_threshold (100 → 10.0)
```

**Layer:** if the team always wants this, put the conventions in project `CLAUDE.md` or `.claude/rules/` (Day 5), not in each prompt.

## P5. Synthesis subagent

**Defects:** "resolve contradictions so the reader gets one clear answer" **destroys provenance** (task 5.6). "Short" contradicts "keep all the important details".

```text
Write a report from the findings in <findings>. You can't search, so use only what's given.
- Cite every claim with its source id, e.g. [S3].
- When sources disagree, give both values side by side with their sources and what each measured.
  Don't choose between them.
- End with "Coverage and gaps": sources that couldn't be read, and subtopics with no findings.
Length: one paragraph per subtopic.
```

**Layer:** the coordinator must pass the complete, structured findings in the task (Day 2). A prompt can't cite what it was never given.

---

## The pattern across all five

Every bad prompt used an **adjective where a criterion belonged** (thorough, upset, good, comprehensive, clear). Three also had a **hidden force**: "only if highly confident", "fill them all in", "one clear answer". That pushes the model to drop true findings, invent values or erase conflicts.
