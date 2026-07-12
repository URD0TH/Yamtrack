"""Smoke test for the Yamtrack MCP server over Streamable HTTP.

Requires a running container exposing the MCP server on :8002
(e.g. `docker compose -f compose.yml up -d`).

Usage:
    export YAMTRACK_JWT="<valid access token>"
    python src/yamtrack_mcp/skill/scripts/mcp_smoke_test.py
"""

import asyncio
import os

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

MCP_URL = os.environ.get("MCP_URL", "http://localhost:8002/mcp")
TOKEN = os.environ.get("YAMTRACK_JWT")

if not TOKEN:
    msg = "Set YAMTRACK_JWT to a valid access token (docker exec yamtrack ...)"
    raise SystemExit(msg)


async def main():
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with streamablehttp_client(MCP_URL, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("TOOLS:", [t.name for t in tools.tools])
            result = await session.call_tool(
                "list_tracked_media", {"status": "In progress"}
            )
            print("RESULT:", result.content[0].text[:500])


if __name__ == "__main__":
    asyncio.run(main())
