import asyncio
import json
from mcp_client import call_mcp_tool

async def research_and_track(query: str, media_type: str = "tv"):
    """
    Workflow: Search for media, get details, and if not tracked, track it.
    """
    # 1. Search
    search_results = await call_mcp_tool('yamtrack', 'search_media', {
        'query': query,
        'media_type': media_type
    })
    
    results = json.loads(search_results.content[0].text)
    if not results:
        return "No results found."

    first_result = results[0]
    media_id = first_result['id']
    source = first_result['source']

    # 2. Get Details (Check if already tracking)
    details_result = await call_mcp_tool('yamtrack', 'get_details', {
        'media_id': str(media_id),
        'media_type': media_type,
        'source': source
    })
    
    details = json.loads(details_result.content[0].text)
    
    if 'tracking' in details:
        return {
            "status": "already_tracking",
            "title": details['title'],
            "tracking": details['tracking']
        }

    # 3. Create Entry
    create_result = await call_mcp_tool('yamtrack', 'create_entry', {
        'media_id': str(media_id),
        'source': source,
        'media_type': media_type,
        'status': 'Planning'
    })
    
    return {
        "status": "created",
        "details": json.loads(create_result.content[0].text)
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        asyncio.run(research_and_track(sys.argv[1]))
