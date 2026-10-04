# Day 3 quiz: Prompt engineering and structured output, part 1 (15 questions, 30 min)

Three questions are **multiple-response**: the question says how many to pick, and you need all of them right to score it. Mark your answers like you did on Day 2. Answers are in `../answers/quiz-answers.md`. Log misses in `../../error-log.md`.

---

**1.** A CI review job's prompt says "Check that code comments are accurate." Developers complain that most flagged comments are fine. Which change best reduces false positives?

- A. Add "Only flag comments you are highly confident are wrong"
- B. Change the instruction to "Flag a comment only when the behaviour it describes contradicts what the code actually does"
- C. Run the review twice and report only comments both runs flag
- D. Lower the temperature of the review call

**2.** A team adds "Be conservative and only report high-confidence findings" to its review prompt. False positives barely change. Why?

- A. The model ignores instructions placed at the end of a prompt
- B. Confidence instructions only work with extended thinking enabled
- C. The prompt needs to repeat the instruction in capital letters
- D. General confidence instructions don't define which issues to report or skip, so the model stays confident about the same false positives

**3.** An automated reviewer reports five categories. The "style" category has a very high false-positive rate, and developers have started ignoring *all* findings, including accurate security ones. What's the best first step?

- A. Temporarily disable the style category to restore trust, while improving its criteria
- B. Add a confidence score to every finding and hide those below 0.8
- C. Switch the reviewer to a larger model
- D. Merge all five categories into one "issues" list

**4.** The same code issue is labelled "high" in one PR review and "low" in another. The prompt defines severity as "high, medium or low, based on impact". What makes classification consistent?

- A. Add a fourth level, "critical"
- B. Ask the model to explain its reasoning before choosing a label
- C. Define explicit criteria for each severity level, each with a concrete code example
- D. Have the model output a numeric severity score instead of a label

**5.** An agent's review comments vary in structure: some list the file and line, some don't, and some omit a suggested fix. The instructions already describe the format in detail. What's most effective?

- A. Repeat the format description at the start and the end of the prompt
- B. Add a few examples showing findings in the exact format: location, issue, severity, suggested fix
- C. Post-process the comments with regex to extract the fields
- D. Ask the model to double-check its formatting before answering

**6. (Select TWO.)** You're adding few-shot examples to improve how an agent handles ambiguous requests. Which choices make them most effective?

- A. Include 20 or more examples so that every case is covered
- B. Focus 2–4 examples on the ambiguous cases rather than the typical ones
- C. Use examples copied from the evaluation set, so performance is measured on known cases
- D. Show the reasoning for why one action was chosen over a plausible alternative
- E. Use only clear-cut examples, so the model isn't confused

**7.** An extraction pipeline handles research papers. When the sample size appears in a methodology section, it's extracted correctly; when it's embedded in the results narrative, the field comes back null. What's the most effective fix?

- A. Add few-shot examples showing correct extraction from papers with different structures
- B. Make the field required so the model can't return null
- C. Split each paper into sections and send each one separately
- D. Tell the model to "look carefully in all sections"

**8.** A pipeline asks Claude to "respond only with valid JSON matching this structure". About 2% of responses fail to parse. What's the most reliable fix?

- A. Retry automatically whenever parsing fails
- B. Repair the JSON with a tolerant parser
- C. Define an extraction tool whose input is a JSON schema, and read the structured data from the `tool_use` block
- D. Add "Do not include any text outside the JSON" to the prompt

**9.** A system receives invoices, receipts and contracts, with one extraction tool for each. The document type isn't known in advance, and every document must produce structured output. Which `tool_choice` fits?

- A. `{"type": "auto"}`
- B. `{"type": "tool", "name": "extract_invoice"}`
- C. `{"type": "none"}`
- D. `{"type": "any"}`

**10.** A pipeline must always run `extract_metadata` before any enrichment tools are called. How do you guarantee that on the first request?

- A. Put `extract_metadata` first in the tools list
- B. Set `tool_choice` to `{"type": "tool", "name": "extract_metadata"}`
- C. Set `tool_choice` to `{"type": "any"}`
- D. Say in the system prompt that `extract_metadata` must be called first

**11.** Many supplier invoices have no due date, but the extraction often returns plausible-looking due dates for them anyway. The schema marks `due_date` as a required string. What's the best fix?

- A. Make `due_date` nullable and tell the model to use null when the document doesn't state one
- B. Add a validator that rejects due dates more than 90 days after the issue date
- C. Add "never make up dates" to the system prompt and keep the field required
- D. Remove the `due_date` field from the schema

**12.** An extraction uses `tool_use` with a strict JSON schema. Every response parses and validates, yet some invoices have line items that don't add up to the total. What explains this?

- A. Strict mode is only applied to the first tool call in a conversation
- B. The schema needs `minimum` constraints on the amounts
- C. Strict schemas eliminate syntax errors but not semantic errors, so the arithmetic needs a separate validation step
- D. The model needs a higher `max_tokens` to finish the calculation

**13. (Select TWO.)** A `document_type` field uses an enum of 6 types. New kinds of documents keep arriving, and the model forces them into the closest wrong type. Which schema changes help?

- A. Add an `"other"` enum value together with a `document_type_detail` string field
- B. Replace the enum with a free-text string so any type can be recorded
- C. Expand the enum to every document type you can think of, over 100 values
- D. Make the field required so it's never empty
- E. Add an `"unclear"` value for documents whose type genuinely can't be determined

**14.** Source documents give dates as "3. September 2026", "09/14/26" and "2026-09-03". You already use a strict schema with a date field. The model sometimes swaps day and month. What should you add?

- A. A second model call that checks every date
- B. Format normalisation rules in the prompt, such as how to tell US from European date order, alongside the strict schema
- C. A required `date_format` field the model fills in with its own guess
- D. Remove the date field and store the raw text

**15. (Select TWO.)** Which statements about `tool_choice` are correct?

- A. `"auto"` guarantees the model makes exactly one tool call
- B. With `"auto"`, the model may answer in plain text and call no tool
- C. `"any"` makes the model call one specific tool that you name
- D. `{"type": "tool", "name": "x"}` makes the model call the tool named `x`
- E. Forcing a tool also guarantees that its values are semantically correct
