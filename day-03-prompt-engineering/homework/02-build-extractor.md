# Day 3 homework, part 2: a live invoice extractor (75 min)

This is the exam's Scenario 6 (structured data extraction) and part 1 of the guide's official Exercise 3, running on the real API. One script sends a document to Claude and gets back a structured record through a `record_invoice` tool. Six documents in `extractor/documents/` are deliberately varied:

| Document | What makes it hard |
|---|---|
| `d1-formal-invoice` | Nothing. It's the control case. |
| `d2-email-narrative` | Prose email, "€3,040", "no VAT", "within 30 days" but no due date |
| `d3-informal-receipt` | US date `09/14/26`, no invoice number, no tax line |
| `d4-german-conference` | German dates `3. September 2026` / `17.09.2026`, `690,00 EUR`, conference ticket fits no category |
| `d5-vendor-math-error` | The vendor's subtotal is wrong (items sum to 105, printed 115), and no currency appears anywhere |
| `d6-ambiguous-charge` | "Misc. charges per our agreement": you can't tell what was bought |

Out of the box the extractor makes the mistakes the exam asks about: it invents values, forces documents into wrong categories, and quietly turns a non-answer into a blank record.

## Files

| File | Role | Layer |
|---|---|---|
| `schema.py` | The `record_invoice` tool and its JSON schema | schema |
| `prompts/system.md` | The system prompt | prompt |
| `extract.py` | Sends one document, reads the `tool_use` input | host code |
| `validate.py` | Semantic checks in plain code | validator |
| `checks.py` | Runs all six documents and grades them against `expected.json` | — |
| `test_offline.py` | Free tests for exercises 1, 3 and 4 | — |

## Setup

Same venv as before: `C:\venvs\ccarf\Scripts\Activate.ps1`. Then:

```powershell
cd day-03-prompt-engineering\homework\extractor
copy ..\..\..\day-01-deployment-mental-model\homework\support-agent\.env .env
pip install -r requirements.txt     # already installed if you use the same venv
```

**Cost:** one or two small calls per document, so a full `checks.py` run is 6–12 calls. That's cheaper than Day 2. `python checks.py d4` runs one document.

## Step 1: baseline (10 min)

```powershell
python check_schema.py    # free: the schema is valid JSON Schema
python test_offline.py    # free: 18 of 23 fail on purpose
python checks.py          # live
python extract.py documents\d6-ambiguous-charge.txt
```

Before reading the results, predict what the starter will put in `currency` for d5 and in `issue_date` for d6. Neither document has that value.

## Step 2: four fixes, four layers

Do them in this order. Run `check_schema.py` after every schema edit, `test_offline.py` after each code fix, and `checks.py` after exercises 1 and 2.

1. **Schema** (`schema.py`, exam 4.3). Make fields a document may lack nullable, including line-item `quantity` and `unit_price`. Add `"other"` + a `category_detail` field and `"unclear"` to the category. Give every field a description that says what goes in it and in what format. The docstring has the strict-mode rules.
2. **Prompt** (`prompts/system.md`, exam 4.1, 4.2). Write it **from a blank page**. Delete the starter text rather than editing around it. It must have:
   - one line saying what the records are for and why a wrong value is worse than a null
   - explicit rules: copy what's printed and don't correct it; when to use null; tax 0 vs null; when a currency is known; when to use `other` vs `unclear`
   - normalisation rules for dates (how to tell US from European order) and amounts (`690,00`, `€3,040`)
   - **two** few-shot examples, each with a `Why:` line naming the alternative it rejected. They must **not** be copies of the six test documents, or you're testing memory instead of the prompt.
3. **Host code** (`extract.py`, exam 4.3). Handle a reply with no tool call: ask once more, then fail loudly. The docstring lists exactly what to return.
4. **Validator** (`validate.py`, exam 4.3). Implement `check_semantics`. d5 is the document it exists for: the record is schema-valid, and the vendor's arithmetic is still wrong.

**Target:** `test_offline.py` 23/23 and `checks.py` 6/6. A run can vary, so if one document fails, rerun only that one before changing the prompt.

**If the API returns `400 ... JSON schema is invalid`,** run `python check_schema.py`. It's free and prints the exact field that's wrong. The usual cause is a Python `None` where JSON needs the string `"null"`.

## Step 3: notes and push

In `extractor/NOTES.md`, write one line per document that failed in the baseline: which field was wrong, which layer fixed it, and the exam rule. Then:

```powershell
git add -A ; git status     # .env must NOT be listed
git commit -m "Day 3 extractor" ; git push
```

The reference solution is in `../answers/extractor-solution/`. Open it after you've had a real attempt.

Then take the quiz in `03-quiz.md`.
