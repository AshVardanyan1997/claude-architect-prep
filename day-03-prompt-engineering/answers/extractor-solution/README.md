# Reference solution: invoice extractor

One way to solve the four exercises. Compare it with yours after a real attempt.

| Exercise | File | What changed |
|---|---|---|
| 1. Schema | `schema.py` | Nullable fields via `anyOf [..., null]`, `"other"` + `category_detail`, `"unclear"`, dates as `format: date`, a description on every field |
| 2. Prompt | `prompts/system.md` | Purpose and cost of a wrong value, 7 explicit rules, normalisation rules, 2 few-shot examples with `Why:` lines |
| 3. Host code | `extract.py` | No tool call → append the reply, ask once more, then `record: None` + an error. Refusals are reported. |
| 4. Validator | `validate.py` | Line maths, sums, dates, `other` without detail, all None-safe with a 0.01 tolerance |

`python test_offline.py` passes 23/23. Run `python checks.py` with your `.env` copied here.
