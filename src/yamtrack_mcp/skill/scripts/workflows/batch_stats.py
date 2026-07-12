import asyncio
import json
from mcp_client import call_mcp_tool

async def get_stats_range(start_date: str = "2025-01-01", end_date: str = "2025-12-31"):
    """Fetch aggregated statistics for a specific range."""
    result = await call_mcp_tool('yamtrack', 'get_statistics', {
        'start_date': start_date,
        'end_date': end_date
    })
    return json.loads(result.content[0].text)

if __name__ == "__main__":
    print(asyncio.run(get_stats_range()))
