"""Host code: send one document to Claude and read back the structured record.

Run:  python extract.py documents/d3-informal-receipt.txt

EXERCISE 3 (exam task 4.3): with tool_choice "auto", the model MAY answer in
plain text instead of calling the tool. Look at what this code does then: it
tries to parse JSON out of prose, and if that fails it returns an empty record
with no error, so a downstream system would book a blank invoice. Fix it:
  - never parse the text as the record
  - if there's no record_invoice call, append the response and ask once more,
    saying the tool wasn't called
  - if the second attempt also has no call, return {"record": None, "error": "..."}
  - return {"record": None, "error": "refused"} when stop_reason is "refusal"
"""

import json
import re
import sys
from pathlib import Path

from common import EFFORT, MODEL, make_client
from schema import EXTRACT_TOOL

SYSTEM_PROMPT = re.sub(r"<!--.*?-->", "", (Path(__file__).parent / "prompts" / "system.md").read_text(),
                       flags=re.S).strip()
TOOL_NAME = EXTRACT_TOOL["name"]


def _create(client, messages):
    # The exam's answer for "guarantee a tool call" is tool_choice "any" or a forced tool.
    # Current models reject both with a 400, so this uses "auto". That makes exercise 3 necessary.
    return client.beta.messages.create(
        model=MODEL, max_tokens=8000, system=SYSTEM_PROMPT, messages=messages,
        tools=[EXTRACT_TOOL], tool_choice={"type": "auto"},
        output_config={"effort": EFFORT},
        betas=["server-side-fallback-2026-07-01"], fallbacks="default",
    )


def extract(document: str, client=None) -> dict:
    """Returns {"record": dict or None, "error": str or None, "attempts": int}."""
    client = client or make_client()
    messages = [{"role": "user", "content": f"<document>\n{document}\n</document>"}]
    response = _create(client, messages)
    for block in response.content:
        if block.type == "tool_use":
            return {"record": dict(block.input), "error": None, "attempts": 1}
    # TODO(exercise 3): this hides the failure.
    text = "".join(b.text for b in response.content if b.type == "text")
    try:
        return {"record": json.loads(text), "error": None, "attempts": 1}
    except json.JSONDecodeError:
        return {"record": {}, "error": None, "attempts": 1}


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "documents/d1-formal-invoice.txt"
    print(json.dumps(extract(Path(path).read_text()), indent=2))
