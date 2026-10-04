# Day 3 lesson: prompt engineering and structured output, part 1

This covers exam tasks **4.1 explicit criteria**, **4.2 few-shot** and **4.3 structured output with tool use and JSON schemas**. Day 4 covers 4.4–4.6: validation-retry loops, batch processing and multi-pass review.

Domain 4 is 20% of the exam, about 12 questions. Two scenarios lean on it most: **structured data extraction** (scenario 6) and **Claude Code in CI** (code review prompts).

---

## 0. Where an extraction system lives

Start with the picture, because that's your weak spot. "A structured data extraction system" on the exam is ordinary backend code that your company runs. It isn't a chat. Nobody is typing.

```
  your infrastructure                                              Anthropic
 ┌───────────────────────────────────────────────────────────┐
 │ storage (S3, inbox, upload folder)                        │
 │    │ new document                                         │
 │    ▼                                                      │
 │ extraction job (a worker, a cron job or a queue consumer) │
 │  ├─ prompts/system.md   ← criteria, normalisation rules,  │
 │  │                         few-shot examples              │      ┌──────────────┐
 │  ├─ schema.py           ← the tool's JSON schema ─────────┼────► │ Messages API │
 │  ├─ extract.py          ← sends doc, reads tool_use input ◄┼───── │ (the model)  │
 │  └─ validate.py         ← semantic checks in plain code   │      └──────────────┘
 │    │ valid record                 │ problems              │
 │    ▼                              ▼                       │
 │ database / ERP                 human review queue         │
 └───────────────────────────────────────────────────────────┘
```

Know which layer owns each concern. That's what the exam questions test.

| Concern | Layer | Why |
|---|---|---|
| JSON parses, fields exist, enum values are legal | **schema** (tool `input_schema`, `strict: true`) | The API guarantees it. That's deterministic. |
| What counts as "absent", how to read a date, when to use "other" | **prompt** (criteria + few-shot) | It's judgment, so the model needs rules and examples. |
| Numbers add up, due date after issue date | **validator code** | The schema can't express it, and the model can't be trusted to check its own work. |
| What happens when no record comes back | **host code** | Only your code can refuse to write a blank record. |

The same picture applies to scenario 5, Claude Code in CI. The "prompt" is the `claude -p "..."` text in the workflow YAML (or a file it points to), and the "schema" is `--json-schema`. Day 4 covers that.

---

## 1. Explicit criteria beat adjectives (task 4.1)

The model can't act on an adjective. It can act on a rule that says what to report and what to skip.

| Vague (wrong on the exam) | Explicit (right) |
|---|---|
| "Check that comments are accurate." | "Flag a comment only when the behaviour it claims contradicts what the code does." |
| "Be conservative." / "Only report high-confidence findings." | "Report: bugs that change behaviour, security issues. Skip: style, naming, patterns used consistently elsewhere in this repo." |
| "Rate severity." | "Critical: data loss or security hole, e.g. `<code>`. Major: wrong result on a normal path, e.g. `<code>`. Minor: wrong only on an edge case, e.g. `<code>`." |

Three exam rules come from this:

1. **Confidence filtering doesn't fix precision.** "Only high-confidence" leaves the false positives in place, because the model is confident about them too. The fix is categorical criteria.
2. **False positives destroy trust in the whole tool.** If one category (say, style) is noisy, developers start ignoring the accurate categories too.
3. **The first step is to turn off the noisy category.** Disable the high-false-positive category temporarily, so trust recovers, while you improve its criteria. Keep the categories that work.

**Severity consistency:** define each level with criteria *and a concrete code example*. Labels alone ("high/medium/low") produce inconsistent classification.

---

## 2. Few-shot examples (task 4.2)

**When:** detailed instructions alone still give inconsistent output. That covers inconsistent format, inconsistent judgment on ambiguous cases, and empty or invented fields on unusual documents. Few-shot examples are the guide's named fix for each of these.

**How (the guide's own numbers):**

- Use **2–4 targeted examples**, not 20. Spend them on the *ambiguous* cases, not the easy ones.
- **Show the reasoning:** why this action and not the plausible alternative. That reasoning is what lets the model *generalise* to new patterns instead of matching only the cases you listed.
- **Show the exact output format** you want (location, issue, severity, suggested fix). Examples teach format more reliably than a description.
- **Show what's acceptable as well as what's wrong.** An example of a pattern that *looks* suspicious but is fine reduces false positives.
- **Show varied document structures** in extraction: inline citations vs a bibliography, a table vs a narrative email, a methodology section vs details spread through the text. This fixes required fields coming back null or invented on unfamiliar layouts.

Example from today's build (one of two):

```
Document: "Invoice 2231 from Rentall, dated May 2 2026. ... Tax: none. ... Terms: Net 15."
Why: "Net 15" is a term, not a printed date, so due_date is null. "Tax: none" means
tax is 0, not null. Equipment hire isn't goods, services or travel, so it's "other".
record_invoice: {"invoice_number": "2231", "due_date": null, "payment_terms": "Net 15",
                 "tax_amount": 0, "category": "other", "category_detail": "equipment rental", ...}
```

Notice that each example covers **several** ambiguities at once, and the `Why:` line names the alternative it rejected.

---

## 3. Structuring a prompt

The guide doesn't list this as its own task, but every good answer above is easier to write this way:

- **Wrap the input in XML tags** (`<document>…</document>`, `<diff>…</diff>`). The model can't confuse data with instructions, and a prompt injection inside the document is less likely to work.
- **Group instructions by purpose:** `<rules>`, `<examples>`, `<output_format>`.
- **Lead with the goal and the cost of being wrong.** "Downstream code books every record, so a wrong value costs more than a null" changes behaviour more than "be accurate".
- **No contradictions.** When you fix a prompt, delete the instruction you're replacing. Two conflicting rules mean the model picks one unpredictably. (That was the Day 2 synthesis prompt.)
- **The deletion test:** if removing a line wouldn't change behaviour, remove it.

---

## 4. Structured output with tool use (task 4.3)

### Reliability ladder

| Approach | JSON syntax errors | Missing or extra fields | Semantic errors |
|---|---|---|---|
| "Respond in JSON" in the prompt | possible | possible | possible |
| `tool_use` with a JSON schema | **eliminated** (guide's claim) | rare | possible |
| … plus `strict: true` | eliminated | eliminated: input is validated against the schema | **still possible** |

**Semantic errors are never eliminated by a schema:** line items that don't sum to the total, a value in the wrong field, a plausible but invented date. That's why validator code exists (Day 4 adds retry).

### The tool *is* the output format

You define a tool such as `record_invoice` whose `input_schema` is the record you want. Claude "calls" it, and your code reads `block.input` from the `tool_use` block. Nothing executes. It's a typed envelope.

### `tool_choice` (memorise this table)

| Setting | What the model must do | Use when |
|---|---|---|
| `{"type": "auto"}` | Anything. It **may reply in text** and call no tool. | Normal agent turns |
| `{"type": "any"}` | Call **some** tool, its choice | Several extraction schemas (invoice, receipt, contract) and the document type is unknown, but you need structured output |
| `{"type": "tool", "name": "extract_metadata"}` | Call **that** tool | A specific extraction must run first, e.g. before enrichment steps |

> **API reality vs exam.** Claude Opus 5.5, Sonnet 5.5 and Fable 5.1 return a 400 for `any` and forced `tool` choice. The current API pattern is `auto` + `strict: true` + an instruction to call the tool + **host code that checks a call happened**. You build that today. **On the exam, answer as the guide describes:** `any` / forced.

### Schema design

- **Required vs nullable.** If the source may not contain a field, make it nullable. A required non-null field *forces* the model to put something there, and that something is invented. In strict mode every property is listed as required, so "optional" is expressed as `anyOf: [{type: string}, {type: null}]`.
- **0 vs null are different facts.** "No VAT charged" means `tax_amount: 0`. "Tax not mentioned" means `null`. Say so in the prompt.
- **`enum` + `"other"` + a detail string** for categories that grow: the enum stays clean for downstream code, and new cases are captured instead of being forced into a wrong bucket.
- **`"unclear"`** for genuinely ambiguous input, so the model doesn't have to guess.
- **Normalisation rules go in the prompt, next to the strict schema.** The schema can say "YYYY-MM-DD", but only the prompt can say "`17.09.2026` is day.month" or "`690,00` uses a comma for decimals".

---

## 5. Cheat sheet: phrase in the stem → answer

| The stem says… | Pick… | Not… |
|---|---|---|
| too many false positives, developers ignore the tool | explicit report/skip criteria; temporarily disable the noisy category | "be conservative", confidence thresholds, a bigger model |
| severity labels inconsistent | criteria + a code example per level | more labels, self-rated confidence |
| format still inconsistent despite detailed instructions | 2–4 few-shot examples showing the format | longer instructions, capital letters |
| wrong call on ambiguous cases | few-shot with reasoning for the choice vs the alternative | a rule per case |
| fields null or invented on unusual layouts | few-shot examples of the varied structures; nullable fields | making fields required |
| JSON sometimes malformed | `tool_use` + JSON schema | "respond only in JSON", regex repair |
| guarantee a tool call, type unknown | `tool_choice: "any"` | `auto` |
| a specific extraction must run first | forced `{"type": "tool", "name": …}` | `any` |
| values don't add up / wrong field, yet schema-valid | semantic validation in code (then retry, Day 4) | a stricter schema |
| new categories keep appearing | enum + `"other"` + detail string | free-text category |
| dates or units in mixed formats | normalisation rules in the prompt with the schema | removing the field |

---

## 6. How today's build maps to these tasks

| Exercise | Layer | Task |
|---|---|---|
| 1. Nullable fields, `other` + detail, `unclear`, field descriptions | schema (`schema.py`) | 4.3 |
| 2. Criteria, normalisation rules, 2 few-shot examples | prompt (`prompts/system.md`) | 4.1, 4.2, 4.3 |
| 3. No tool call → ask again → fail loudly | host code (`extract.py`) | 4.3 (`tool_choice`) |
| 4. Sums, dates, `other` without detail | validator code (`validate.py`) | 4.3 (semantic vs syntax) |
