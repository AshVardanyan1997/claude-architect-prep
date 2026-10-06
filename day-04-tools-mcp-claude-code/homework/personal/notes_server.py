"""Your personal, experimental MCP server. It lives OUTSIDE the team repo.

Register it for yourself only (it goes in ~/.claude.json, never in git):

    claude mcp add --scope user notes -- python C:\\full\\path\\to\\notes_server.py
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("notes")
NOTES = {"exam": "CCAR-F on Friday 2026-10-09. Pass mark 720.", "rule": "Fix it at the layer that owns it."}


@mcp.tool()
def read_note(topic: str) -> str:
    """Read one of my personal study notes by topic: 'exam' or 'rule'. Returns the note text,
    or a list of available topics if the topic doesn't exist."""
    return NOTES.get(topic.strip().lower(), f"No note '{topic}'. Topics: {', '.join(NOTES)}")


if __name__ == "__main__":
    mcp.run()
