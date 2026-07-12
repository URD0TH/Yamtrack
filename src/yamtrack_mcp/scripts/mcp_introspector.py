import json
import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def introspect(config_path, output_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    all_tools = []
    for server in config['servers']:
        params = StdioServerParameters(
            command=server['command'][0],
            args=server['command'][1:],
            env=None
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_result = await session.list_tools()
                for tool in tools_result.tools:
                    all_tools.append({
                        "server": server['name'],
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    })
    
    with open(output_path, 'w') as f:
        json.dump(all_tools, f, indent=2)
    print(f"Introspection complete. Found {len(all_tools)} tools.")

if __name__ == "__main__":
    asyncio.run(introspect(sys.argv[1], sys.argv[2]))
