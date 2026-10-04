"""Host code: send one document to Claude and read back the structured record.

Run:  python extract.py documents/d3-informal-receipt.txt
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
    # Current models reject both with a 400, so this uses "auto" and checks in code (below).
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
    for attempt in (1, 2):
        response = _create(client, messages)
        if response.stop_reason == "refusal":
            return {"record": None, "error": "refused", "attempts": attempt}
        calls = [b for b in response.content if b.type == "tool_use" and b.name == TOOL_NAME]
        if calls:
            return {"record": dict(calls[0].input), "error": None, "attempts": attempt}
        # "auto" let the model answer in text. Don't parse that text; ask once more, then give up loudly.
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": f"You didn't call {TOOL_NAME}. Call it now with the data "
                                                    "from the document, using null for anything it doesn't state."})
    return {"record": None, "error": f"no {TOOL_NAME} call after 2 attempts", "attempts": 2}


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "documents/d1-formal-invoice.txt"
    print(json.dumps(extract(Path(path).read_text()), indent=2))
