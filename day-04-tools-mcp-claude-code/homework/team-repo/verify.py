"""Free checker for the Day 4 exercises. No API calls.

Run from the team-repo folder:  python verify.py
Exercise 4 starts the MCP server for real and calls its tools the way Claude Code would.
"""

import asyncio
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
results = []


def check(name, condition):
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}  {name}")


def read(path):
    p = ROOT / path
    return p.read_text(encoding="utf-8") if p.exists() else ""


def frontmatter(text):
    """Parse simple YAML frontmatter: `key: value`, `key: [a, b]` and `- item` lists."""
    m = re.match(r"\A---\s*\n(.*?)\n---", text, re.S)
    data, key = {}, None
    for line in (m.group(1).splitlines() if m else []):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item = re.match(r"\s+-\s*(.+)", line)
        if item and key:
            data.setdefault(key, [])
            if isinstance(data[key], list):
                data[key].append(item.group(1).strip().strip("\"'"))
            continue
        kv = re.match(r"([\w-]+):\s*(.*)", line)
        if kv:
            key, value = kv.group(1), kv.group(2).strip()
            if value.startswith("["):
                data[key] = [v.strip().strip("\"'") for v in value.strip("[]").split(",") if v.strip()]
            elif value:
                data[key] = value.strip("\"'")
    return data


def glob_match(pattern, path):
    regex = ""
    i = 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            regex, i = regex + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            regex, i = regex + ".*", i + 2
        elif pattern[i] == "*":
            regex, i = regex + "[^/]*", i + 1
        elif pattern[i] == "?":
            regex, i = regex + "[^/]", i + 1
        else:
            regex, i = regex + re.escape(pattern[i]), i + 1
    return re.fullmatch(regex, path) is not None


def any_glob(patterns, path):
    if isinstance(patterns, str):
        patterns = [patterns]
    return any(glob_match(p, path) for p in patterns or [])


print("Exercise 1: CLAUDE.md hierarchy and path rules (exam 3.1, 3.3)")
root_md = read("CLAUDE.md")
check("root CLAUDE.md no longer contains the API or testing conventions",
      root_md and "snake_case" not in root_md and "test_<module>" not in root_md)
check("the personal preference is gone from the shared CLAUDE.md (it belongs in ~/.claude/CLAUDE.md)",
      root_md and "Armenian" not in root_md)
check("the exercise comment is deleted", root_md and "EXERCISE 1" not in root_md)
api = frontmatter(read(".claude/rules/api.md"))
check(".claude/rules/api.md has paths that match src/api/orders.py",
      any_glob(api.get("paths"), "src/api/orders.py"))
check("…and don't match src/billing/invoice.py", not any_glob(api.get("paths"), "src/billing/invoice.py"))
testing = frontmatter(read(".claude/rules/testing.md"))
tests = ["src/api/test_orders.py", "src/billing/test_invoice.py", "src/new_pkg/deep/test_x.py"]
check(".claude/rules/testing.md has paths that match test files in ANY folder",
      all(any_glob(testing.get("paths"), t) for t in tests))
check("…and don't match non-test code", not any_glob(testing.get("paths"), "src/api/orders.py"))
billing_md = read("src/billing/CLAUDE.md")
imports = re.findall(r"@(\S+)", billing_md)
check("src/billing/CLAUDE.md @imports docs/billing-standards.md",
      any((ROOT / "src/billing" / p).resolve() == (ROOT / "docs/billing-standards.md").resolve() for p in imports))

print("\nExercise 2: a skill and a command (exam 3.2)")
skill_text = read(".claude/skills/dep-report/SKILL.md")
skill = frontmatter(skill_text)
check("dep-report has context: fork", skill.get("context") == "fork")
tools = skill.get("allowed-tools", [])
tools = [t.strip() for t in (tools.split(",") if isinstance(tools, str) else tools)]
check("dep-report allowed-tools is read-only: Read, Grep, Glob, and no Write, Edit or Bash",
      {"Read", "Grep", "Glob"} <= set(tools) and not {"Write", "Edit", "Bash"} & set(tools))
check("dep-report has an argument-hint", bool(skill.get("argument-hint")))
check("the exercise comments are deleted", skill_text and "EXERCISE 2" not in skill_text)
check(".claude/commands/review.md exists and isn't empty (a project command the whole team gets)",
      len(read(".claude/commands/review.md").strip()) > 40)

print("\nExercise 3: MCP configuration (exam 2.4)")
try:
    server = json.loads(read(".mcp.json"))["mcpServers"]["orders"]
except (json.JSONDecodeError, KeyError):
    server = {}
token = server.get("env", {}).get("ORDERS_API_TOKEN", "")
check(".mcp.json still configures the orders server", bool(server))
check(".mcp.json passes the token by environment variable expansion, ${ORDERS_API_TOKEN}",
      token == "${ORDERS_API_TOKEN}")

print("\nExercise 4: the MCP server's tools and errors (exam 2.1, 2.2)")


async def exercise_4():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async def session_call(env, calls):
        params = StdioServerParameters(command=sys.executable, args=[str(ROOT / "mcp_server/orders_server.py")],
                                       env=env)
        async with stdio_client(params, errlog=open(os.devnull, "w")) as (r, w), ClientSession(r, w) as s:
            await s.initialize()
            listed = (await s.list_tools()).tools
            out = []
            for name, args in calls:
                if name not in {t.name for t in listed}:
                    out.append(None)
                    continue
                res = await s.call_tool(name, args)
                text = res.content[0].text if res.content else ""
                try:  # FastMCP prefixes error text with "Error executing tool <name>: "
                    body = json.loads(text[text.find("{"):] if res.isError and "{" in text else text)
                except json.JSONDecodeError:
                    body = text
                out.append((res.isError, body))
            return listed, out

    with_token = {**os.environ, "ORDERS_API_TOKEN": "test-token"}
    no_token = {k: v for k, v in os.environ.items() if k != "ORDERS_API_TOKEN"}
    listed, (ok, timeout, missing, empty) = await session_call(with_token, [
        ("lookup_order", {"order_id": "A1002"}),
        ("lookup_order", {"order_id": "B2210"}),
        ("lookup_order", {"order_id": "Z9999"}),
        ("search_orders", {"customer_id": "C-999"}),
    ])
    _, (denied,) = await session_call(no_token, [("lookup_order", {"order_id": "A1002"})])

    names = {t.name: (t.description or "") for t in listed}
    check("tools are named lookup_order and search_orders; get_data and get_info are gone",
          {"lookup_order", "search_orders"} <= set(names) and not {"get_data", "get_info"} & set(names))
    check("each description is specific: 150+ characters and gives an example ID",
          all(len(names.get(n, "")) >= 150 and re.search(r"[AC]-?\d", names.get(n, ""))
              for n in ("lookup_order", "search_orders")))
    check("each description says when to use the other tool",
          "search_orders" in names.get("lookup_order", "") and "lookup_order" in names.get("search_orders", ""))

    def err(r):
        return r[1] if r and r[0] and isinstance(r[1], dict) else {}

    check("a working lookup succeeds", ok is not None and ok[0] is False)
    check("a carrier timeout is isError, errorCategory transient, isRetryable true",
          err(timeout).get("errorCategory") == "transient" and err(timeout).get("isRetryable") is True)
    check("an unknown order ID is isError, validation, isRetryable false",
          err(missing).get("errorCategory") == "validation" and err(missing).get("isRetryable") is False)
    check("a missing token is isError, permission, isRetryable false",
          err(denied).get("errorCategory") == "permission" and err(denied).get("isRetryable") is False)
    check("every error has a message saying what to do next",
          all(len(str(err(r).get("message", ""))) > 20 for r in (timeout, missing, denied)))
    check("a search with no matches is a normal empty result, not an error",
          empty is not None and empty[0] is False and empty[1] in ([], {"orders": []}))


try:
    asyncio.run(exercise_4())
except ModuleNotFoundError:
    print("SKIP  the mcp package isn't installed: run  pip install -r requirements.txt")

print(f"\n{sum(results)}/{len(results)} passed")
