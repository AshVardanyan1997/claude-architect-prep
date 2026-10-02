# Day 2 homework, part 1: prompt drill (20 min, blank page)

Prompt engineering is one of your two weak spots, and on Day 1 the system prompt came straight from the reference solution. Today you write from a blank page. **Don't open `answers/` until you've written both parts.** Writing a mediocre prompt yourself and then comparing teaches more than reading a good one.

## Part A: fix your Day 1 tool descriptions (8 min)

Open `day-01-deployment-mental-model/homework/support-agent/tools.py` and rewrite the `get_customer` and `lookup_order` descriptions. Check each one against this rubric:

| # | A good tool description… | Your Day 1 version |
|---|---|---|
| 1 | says what the tool is **for**, in one sentence | partly |
| 2 | gives the **input format with an example** ('C-101', 'maria@example.com', 'A1002') | no |
| 3 | says what it **returns**, including the awkward cases (several matches, not found) | no |
| 4 | says **when not to use it**, and which tool to use instead | no |
| 5 | talks to the **model choosing the tool**, not to the code running it ("return nothing" is an implementation note) | no |
| 6 | is valid Python: adjacent string literals join **with no space**, so end each one with a space | no |

Rerun `python scenarios.py 4` (the two John Smiths) to see the effect. Then commit.

## Part B: write the coordinator's system prompt (12 min)

In today's build, `COORDINATOR_PROMPT` in `research-system/coordinator.py` is a fixed procedure that only researches visual arts. Write a replacement on paper or in a scratch file *before* you run anything. It must cover:

1. **The goal**, stated as an outcome (a report covering the whole topic), not as steps.
2. **Decomposition:** how the coordinator should find all the areas of a topic, and split them so search agents don't overlap.
3. **The quality bar** the coordinator checks the report against: coverage, citations, conflicts kept, gaps named.
4. **Context passing:** subagents remember nothing, so what exactly must go into the synthesis task?
5. **Parallelism:** independent searches go in one response.
6. **Refinement:** what the coordinator does if the draft report has a thin area.

Use XML-style sections (`<goal>`, `<quality_bar>`…) if it helps you structure it. Keep it under 25 lines. Long prompts aren't better prompts.

**Self-check before you run it.** For each line, ask: *if I deleted this line, would the behaviour change?* If not, delete it.

Then go to `02-build-research-system.md` and use your prompt as exercise 1.
