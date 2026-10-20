"""
STEP 11 · Lesson 11 · Your tools, served over MCP

The same three tools from Step 04 become an MCP server. Any MCP host (Claude Desktop,
VS Code, Cursor, your own agent) can now discover and call them. Nothing about the tools
changed; only the boundary did. That is the point of a protocol.

Run the server:   python step11_mcp_server.py
Test it:          npx @modelcontextprotocol/inspector python step11_mcp_server.py
Add to Claude Desktop (claude_desktop_config.json):
  {"mcpServers": {"field-agent": {"command": "python", "args": ["C:/path/to/field-agent/step11_mcp_server.py"]}}}
"""
from mcp.server.fastmcp import FastMCP

import step04_tools as t

mcp = FastMCP("field-agent")

# Wrap the existing functions: the docstrings become the tool descriptions again.
mcp.tool()(t.get_current_time)
mcp.tool()(t.calculate)
mcp.tool()(t.read_file)


@mcp.resource("notes://index")
def notes_index() -> str:
    """List of the note files this agent can read."""
    return "\n".join(p.name for p in (t.SANDBOX / "notes").glob("*.md"))


@mcp.prompt()
def research_brief(topic: str) -> str:
    """A reusable prompt that asks for a sourced brief on a topic."""
    return f"Research '{topic}' using the notes resource first. Cite passage ids. Keep it under 150 words."


if __name__ == "__main__":
    mcp.run()  # stdio transport: the host launches this process and talks over stdin/stdout
