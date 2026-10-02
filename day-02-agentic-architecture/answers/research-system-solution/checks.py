"""Run the full system on the exam's own example topic and grade the report.

Run:  python checks.py            (with the live trace)
      python checks.py --quiet

Rough cost: about 20–40 API calls per run on the default model. My estimate is
somewhere around a few tens of US cents per run, so fix several things between
runs rather than rerunning after every small change. EFFORT=low in .env is cheaper.
"""

import re
import sys

from coordinator import research

TOPIC = "impact of AI on creative industries"


def overlapped(trace):
    """True if two delegations ran at the same time (one started before another ended)."""
    starts = sorted(e["t"] for e in trace if e["kind"] == "delegate-start")
    ends = sorted(e["t"] for e in trace if e["kind"] == "delegate-end")
    return any(s2 < e1 for s2, e1 in zip(starts[1:], ends[:-1]))


def main():
    verbose = "--quiet" not in sys.argv
    report, trace, elapsed = research(TOPIC, verbose)
    text = report.lower()
    multi_delegate_turns = sum(1 for e in trace if e["agent"] == "coordinator" and e["kind"] == "turn"
                               and not e["detail"].startswith("1 "))
    cited = sorted(set(re.findall(r"\bS[1-8]\b", report)))

    checks = [
        ("coverage: music, writing and film are all covered (exam 1.2)",
         all(any(w in text for w in group) for group in
             (["music", "musician"], ["writing", "writer", "publish", "author"], ["film", "screen", "studio"]))),
        ("provenance: at least 5 different sources cited by id, e.g. [S3] (exam 5.6)", len(cited) >= 5),
        ("conflict kept: both 38% and 22% appear, with their sources (exam 5.6)",
         "38%" in report and "22%" in report),
        ("gap reported: the unreachable source S5 is flagged, not silently skipped (exam 5.3)",
         "s5" in text and bool(re.search(r"unavailable|could not|couldn't|timed out|time out|unreachable|gap", text))),
        ("parallel: the coordinator asked for several delegations in one response (exam 1.3)",
         multi_delegate_turns > 0),
        ("parallel: those delegations actually ran at the same time (exam 1.3)", overlapped(trace)),
    ]

    print("\n" + "=" * 70 + "\nREPORT\n" + "=" * 70 + f"\n{report}\n" + "=" * 70)
    for desc, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {desc}")
    print(f"\ncited sources: {cited}   elapsed: {elapsed:.0f}s   "
          f"subagents spawned: {sum(1 for e in trace if e['kind'] == 'delegate-start')}")
    print(f"{sum(ok for _, ok in checks)}/{len(checks)} passed")


if __name__ == "__main__":
    main()
