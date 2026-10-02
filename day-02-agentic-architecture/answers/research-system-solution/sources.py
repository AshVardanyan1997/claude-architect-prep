"""The search subagent's tools, over a small local corpus (corpus.json).

The corpus is fake but deliberately messy, like the real web: two credible
sources disagree on a statistic, and one source is down.

EXERCISE 3 (exam tasks 2.2 and 5.3): read_source swallows failures. Look at
what it does when the fetch times out, then fix it.
"""

import json
from pathlib import Path

CORPUS = {s["id"]: s for s in json.loads((Path(__file__).parent / "corpus.json").read_text())}
UNREACHABLE = {"S5"}  # this publisher's server is down for the whole run

TOOLS = [
    {
        "name": "search_corpus",
        "description": (
            "Search the research library by keywords. Input `query`: a few keywords, e.g. "
            "'music AI production'. Returns matching sources with id, title, domain and "
            "publication date, but not their content; call read_source to read one. An empty "
            "list means nothing matched, so try broader or different keywords."
        ),
        "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    },
    {
        "name": "read_source",
        "description": (
            "Read the full text of one source by id, e.g. 'S3'. Use after search_corpus. "
            "Returns title, publisher, publication date and text."
        ),
        "input_schema": {"type": "object", "properties": {"source_id": {"type": "string"}},
                         "required": ["source_id"]},
    },
]


def search_corpus(query: str) -> dict:
    words = [w for w in query.lower().split() if len(w) > 2 and w not in ("and", "the", "for")]
    hits = []
    for s in CORPUS.values():
        haystack = f"{s['title']} {s['domain']} {s['text']}".lower()
        if any(w in haystack for w in words):
            hits.append({k: s[k] for k in ("id", "title", "domain", "published")})
    return {"query": query, "results": hits}


class SourceTimeout(Exception):
    pass


def _fetch(source_id: str) -> dict:
    if source_id in UNREACHABLE:
        raise SourceTimeout(f"{source_id}: publisher server did not respond within 10s")
    if source_id not in CORPUS:
        raise KeyError(source_id)
    return CORPUS[source_id]


def read_source(source_id: str) -> dict:
    source_id = source_id.strip().upper()
    try:
        return _fetch(source_id)
    except SourceTimeout as exc:
        return {"isError": True, "errorCategory": "transient", "isRetryable": True,
                "attempted": {"tool": "read_source", "source_id": source_id},
                "message": f"Timed out reading {source_id}: {exc}. Retry once; if it fails again, "
                           "report this source as unavailable and continue with the others."}
    except KeyError:
        return {"isError": True, "errorCategory": "validation", "isRetryable": False,
                "attempted": {"tool": "read_source", "source_id": source_id},
                "message": f"No source with id {source_id}. Use an id returned by search_corpus."}


def run(name: str, tool_input: dict):
    if name == "search_corpus":
        return search_corpus(**tool_input)
    if name == "read_source":
        return read_source(**tool_input)
    return {"isError": True, "errorCategory": "validation", "isRetryable": False, "message": f"Unknown tool {name}"}
