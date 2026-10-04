"""Run the extractor on every document and grade it against expected.json.

Run:  python checks.py              (all six documents)
      python checks.py d3           (only documents whose name starts with d3)

Cost: one or two API calls per document, so a full run is about 6–12 small calls.
"""

import json
import sys
from pathlib import Path

from extract import extract
from validate import check_semantics

HERE = Path(__file__).parent
EXPECTED = {k: v for k, v in json.loads((HERE / "expected.json").read_text()).items() if not k.startswith("_")}


def matches(actual, rule):
    if isinstance(rule, dict):
        if "one_of" in rule:
            return any(matches(actual, r) for r in rule["one_of"])
        if "not_null" in rule:
            return actual is not None
        if "contains" in rule:
            return isinstance(actual, str) and rule["contains"] in actual.lower()
    if isinstance(rule, (int, float)) and isinstance(actual, (int, float)):
        return abs(actual - rule) < 0.005
    if isinstance(rule, str) and isinstance(actual, str):
        return actual.strip() == rule
    return actual == rule


def grade(name, record):
    rules = EXPECTED[name]
    failures = []
    for field, rule in rules.items():
        if field == "line_amounts":
            amounts = [i.get("amount") for i in record.get("line_items", [])]
            if len(amounts) != len(rule) or not all(matches(a, r) for a, r in zip(amounts, rule)):
                failures.append(f"line_items amounts: got {amounts}, expected {rule}")
        elif field == "semantic_errors":
            flagged = bool(check_semantics(record))
            if flagged != rule:
                failures.append(f"validate.py {'flagged' if flagged else 'did not flag'} this record "
                                f"(expected {'a problem' if rule else 'no problems'})")
        elif not matches(record.get(field), rule):
            failures.append(f"{field}: got {json.dumps(record.get(field))}, expected {json.dumps(rule)}")
    return failures


def main():
    prefix = sys.argv[1] if len(sys.argv) > 1 else ""
    names = [n for n in EXPECTED if n.startswith(prefix)]
    passed = 0
    for name in names:
        result = extract((HERE / "documents" / f"{name}.txt").read_text())
        if result["record"] is None:
            print(f"FAIL  {name}: no record ({result['error']})")
            continue
        failures = grade(name, result["record"])
        problems = check_semantics(result["record"])
        if failures:
            print(f"FAIL  {name}")
            for f in failures:
                print(f"        - {f}")
        else:
            passed += 1
            print(f"PASS  {name}")
        if problems:
            print(f"        validator: {'; '.join(problems)}")
    print(f"\n{passed}/{len(names)} documents fully correct")


if __name__ == "__main__":
    main()
