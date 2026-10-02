"""Tool definitions sent to Claude, and the dispatcher that runs them.

EXERCISE 1 (exam task 2.1): the descriptions of get_customer and lookup_order
are deliberately weak. Rewrite them so each says what the tool is for, what
input it expects, an example, and when NOT to use it. Then rerun the scenarios.

SOLUTION: see the two rewritten descriptions below.
"""

import json

import backend

TOOLS = [
    {
        "name": "get_customer",
        "description": (
            "Find a customer account and verify who you're talking to. Input `query` is ONE of: a "
            "customer ID like 'C-101', an email address, or a full name. Returns all matching "
            "accounts. A name can match several people; if match_count > 1, ask the customer for "
            "their email or ZIP and search again, never pick one. Use this before any order or "
            "account action, and for account questions (email, address, tier). Don't use it for "
            "order status; use lookup_order."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "lookup_order",
        "description": (
            "Get one order's details: item, amount, status, delivery date, return window. Input "
            "`order_id` looks like 'A1002' (letter + 4 digits). Use for order status, returns and "
            "refund eligibility. Don't use it to identify the customer; use get_customer. If it "
            "returns a transient error you may retry once; a validation error means ask the "
            "customer to check the number."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "process_refund",
        "description": (
            "Issue a refund for a delivered order. Only use after the customer is verified "
            "and the order is confirmed to belong to them. amount is in USD and must not "
            "exceed the order total."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "amount": {"type": "number"},
                "reason": {"type": "string"},
            },
            "required": ["order_id", "amount", "reason"],
        },
    },
    {
        "name": "escalate_to_human",
        "description": (
            "Hand the case to a human agent. The human can't see this conversation, so the "
            "handoff must stand on its own. Use when the customer asks for a human, when "
            "policy is silent or needs an exception, or when you can't make progress."
        ),
        "strict": True,
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "customer_id": {"type": ["string", "null"], "description": "Verified customer ID, or null if not verified."},
                "issue_summary": {"type": "string"},
                "root_cause": {"type": "string"},
                "steps_taken": {"type": "array", "items": {"type": "string"}},
                "amount_involved": {"type": ["number", "null"]},
                "recommended_action": {"type": "string"},
            },
            "required": ["customer_id", "issue_summary", "root_cause", "steps_taken",
                         "amount_involved", "recommended_action"],
        },
    },
]


def run_tool(name: str, tool_input: dict) -> dict:
    if name == "get_customer":
        return backend.get_customer(**tool_input)
    if name == "lookup_order":
        return backend.lookup_order(**tool_input)
    if name == "process_refund":
        return backend.process_refund(**tool_input)
    if name == "escalate_to_human":
        return backend.escalate_to_human(tool_input)
    return {"isError": True, "errorCategory": "validation", "isRetryable": False,
            "message": f"Unknown tool {name}"}


def to_tool_result(tool_use_id: str, result: dict) -> dict:
    """Package a tool's dict result as a tool_result block for the next request."""
    return {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": json.dumps(result),
        "is_error": bool(result.get("isError")),
    }
