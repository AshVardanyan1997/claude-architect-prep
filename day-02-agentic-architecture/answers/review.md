# Day 2 review (graded 2026-10-04)

## Quiz: 14/15

All three multiple-response items (2, 7, 13) are fully right. The only miss is **Q4**: you picked C (cache synthesis), the answer is A (let the coordinator choose which subagents a query needs). You already logged it in `error-log.md`. The rule: caching treats the symptom, and the defect is a coordinator that always runs the full pipeline.

## Build: `test_offline.py` 8/8 PASS

The two code exercises are correct.

- **Exercise 3, structured errors (`sources.py`).** Correct. A timeout is `transient` and retryable, an unknown ID is `validation` and not retryable, both say what was attempted, and both say what to do next.
- **Exercise 4, parallel delegations (`coordinator.py`).** Correct. `pool.map` keeps results in the same order as the calls, so every `tool_use_id` still matches. Remove the unused `import os`.

The live run (`python checks.py`) needs your key, so I couldn't run it. Paste the summary line when you do.

## The two prompt exercises have real defects

**1. The synthesis prompt contradicts itself** (`agents.py:30-32`). You kept the old line "choose the most reliable one so the reader gets a single clear answer" and added "keep conflicting numbers side by side" after it. When two instructions conflict, the model picks one, and you can't predict which one. This is probably why the 38%/22% check fails on some runs. **Rule: when you fix a prompt, delete the instruction you're replacing. Don't append the fix next to it.**

**2. The search prompt also contradicts itself** (`agents.py:21-23`). "Summarize in a few paragraphs" sits next to "return a specific structure". Name the format exactly, for example one `<finding>` per claim with these fields. Also ask for a gaps list: sources it couldn't read, and subtopics where it found nothing. Without that, S5's timeout never reaches the coordinator.

**3. The coordinator prompt is goals and structure. Good.** The sections are the right ones: decomposition, quality bar, context passing, parallelism and refinement. Three gaps:

- **No definition of coverage.** "Identify the topics" doesn't tell it what complete looks like. Write the criterion: *every major area the topic plausibly covers (for creative industries: visual art, design, music, writing, film…)*. Coverage is what exercise 1 is testing.
- **"Never pass all the reports to synthesize agent before quality checks"** reads as "filter the findings". That's the opposite of quiz Q7. Say instead: *pass the complete findings, with their sources, in the synthesis task, because synthesis can't see anything else.*
- **It never says to end the turn.** Add one line, such as: *When synthesis returns a report that meets the quality bar, return it as your final answer.*

**4. NOTES.md** is two lines. One of them is the Q4 rule, which belongs in the error log. Use it to record what changed between the starter run and your fixed run: the coverage, the citation count and the elapsed time.

## Day 1 fixes (commit 5532a72)

Credit first: you rewrote the system prompt in your own words. That was the point of the exercise. These are the regressions:

| Where | Problem | Why it matters on the exam |
|---|---|---|
| `system.md` policy 4 | "No price matching is allowed" now **refuses** price matching. But your own example still says to **escalate** it as a policy gap. | Policy gap → escalate. Writing a refusal rule you weren't given is the prompt inventing policy. |
| `system.md` escalation 1 | "Do it immediately, before looking anything up" is gone. | An explicit request for a human is honoured at once (task 5.2). |
| `system.md` escalation 3 | "Tried twice" became "multiple times". | Vague thresholds give unpredictable behaviour. Keep criteria explicit. |
| `system.md` | `estalate_to_human` is misspelled. | A tool name has to match exactly in the prompt. |
| `get_customer` description | It still says "verify all attributes ID, email, name". The two John Smiths share a name, so the name can't tell them apart. | Say *ask the customer for their email or ZIP code*. |
| `lookup_order` description | "If no order found return nothing" and "multiple orders with the same id" describe what the tool's code does, not what the model should do. | A description tells the model when to call the tool and what comes back. Put backend behaviour in the code. |
| `hooks.py` | Not changed. C-101 can still refund B2210, which belongs to C-301. | Add an ownership check: the order's `customer_id` must equal `verified_customer_id`. |

## Score card

| Area | Grade |
|---|---|
| Quiz | 14/15 |
| Code fixes (exercises 3, 4) | Full marks |
| Prompt writing (exercises 1, 2, Day 1 rewrite) | Partial. The structure is right. The defects are contradictions, vague criteria, and invented policy. |

Day 3 targets exactly this: writing explicit criteria, removing the instruction a fix replaces, and few-shot examples.
