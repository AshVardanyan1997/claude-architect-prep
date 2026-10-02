"""Shared pieces: the API client and one generic agent loop used by every agent.

Every agent in this system (coordinator and subagents) is the same loop with a
different system prompt and toolset. That's all an "agent definition" is.
"""

import json
import os
import threading
import time

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = os.environ.get("MODEL", "claude-opus-5-5")
EFFORT = os.environ.get("EFFORT", "medium")
MAX_ROUNDS = 15  # safety net only; loops end on stop_reason

client = anthropic.Anthropic()
_print_lock = threading.Lock()


def log(trace: list, agent: str, kind: str, detail: str, verbose: bool = True):
    entry = {"t": time.time(), "agent": agent, "kind": kind, "detail": detail}
    trace.append(entry)
    if verbose:
        with _print_lock:
            print(f"  [{agent}:{kind}] {detail[:160]}")


def run_agent(name: str, system: str, tools: list, user_content: str, execute_tools, trace: list,
              verbose: bool = True) -> str:
    """Run one agent's loop until stop_reason is end_turn. Returns its final text.

    execute_tools(tool_use_blocks) must return a list of tool_result blocks, one per call,
    in any order. It decides HOW the calls run (one by one, or in parallel).
    """
    messages = [{"role": "user", "content": user_content}]
    for _ in range(MAX_ROUNDS):
        kwargs = dict(model=MODEL, max_tokens=16000, system=system, messages=messages,
                      output_config={"effort": EFFORT},
                      betas=["server-side-fallback-2026-07-01"], fallbacks="default")
        if tools:
            kwargs["tools"] = tools
        response = client.beta.messages.create(**kwargs)
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            return "".join(b.text for b in response.content if b.type == "text")
        if response.stop_reason != "tool_use":
            log(trace, name, "stop", response.stop_reason, verbose)
            return f"(stopped: {response.stop_reason})"

        calls = [b for b in response.content if b.type == "tool_use"]
        log(trace, name, "turn", f"{len(calls)} tool call(s) in one response", verbose)
        messages.append({"role": "user", "content": execute_tools(calls)})
    return "(stopped: too many rounds)"


def tool_result(tool_use_id: str, result) -> dict:
    is_error = isinstance(result, dict) and bool(result.get("isError"))
    return {"type": "tool_result", "tool_use_id": tool_use_id,
            "content": result if isinstance(result, str) else json.dumps(result), "is_error": is_error}
