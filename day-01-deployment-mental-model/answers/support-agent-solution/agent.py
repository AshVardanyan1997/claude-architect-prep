"""The support agent: a manual agentic loop over the Claude Messages API.

This file is the "host process" from the Day 1 lesson. It owns the loop, runs
the tools, applies the hooks, and keeps the conversation state. Claude only
proposes the next step.

Run a live chat:   python agent.py
"""

import json
import os
import re
from pathlib import Path

import anthropic
from dotenv import load_dotenv

import hooks
from tools import TOOLS, run_tool, to_tool_result

load_dotenv()

MODEL = os.environ.get("MODEL", "claude-opus-5-5")
EFFORT = os.environ.get("EFFORT", "medium")
MAX_TOOL_ROUNDS = 10  # a safety net only; the loop normally ends on stop_reason (exam task 1.1)

SYSTEM_PROMPT = re.sub(r"<!--.*?-->", "", (Path(__file__).parent / "prompts" / "system.md").read_text(),
                       flags=re.S).strip()

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment / .env


def new_conversation() -> dict:
    """Everything the host keeps per conversation. The API itself is stateless."""
    return {"messages": [], "state": {}, "trace": []}


def _log(convo: dict, kind: str, detail: str, verbose: bool):
    convo["trace"].append((kind, detail))
    if verbose:
        print(f"  [{kind}] {detail}")


def send(convo: dict, user_text: str, verbose: bool = True) -> str:
    """Add one customer message and run the loop until Claude has a reply for them."""
    convo["messages"].append({"role": "user", "content": user_text})

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=convo["messages"],
            output_config={"effort": EFFORT},
            # If a safety classifier declines, retry on Anthropic's recommended fallback model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        # Append the whole content (thinking, text, tool_use), never just the text.
        convo["messages"].append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            return "".join(b.text for b in response.content if b.type == "text")

        if response.stop_reason in ("max_tokens", "refusal"):
            _log(convo, "stop", response.stop_reason, verbose)
            return f"(stopped: {response.stop_reason})"

        # stop_reason == "tool_use": run every requested tool, return all results in ONE user message.
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            _log(convo, "tool", f"{block.name} {json.dumps(block.input)}", verbose)
            allowed, reason = hooks.before_tool(block.name, block.input, convo["state"])
            if not allowed:
                _log(convo, "blocked", f"{block.name}: {reason}", verbose)
                result = {"isError": True, "errorCategory": "business", "isRetryable": False, "message": reason}
            else:
                result = run_tool(block.name, block.input)
                result = hooks.after_tool(block.name, block.input, result, convo["state"])
            _log(convo, "result", json.dumps(result)[:200], verbose)
            results.append(to_tool_result(block.id, result))
        convo["messages"].append({"role": "user", "content": results})

    return "(stopped: too many tool rounds)"


if __name__ == "__main__":
    print(f"Northwind support ({MODEL}, effort={EFFORT}). Ctrl+C to quit.\n")
    convo = new_conversation()
    while True:
        try:
            text = input("customer> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text:
            print(f"\nagent> {send(convo, text)}\n")
            print(f"  state: {convo['state']}\n")
