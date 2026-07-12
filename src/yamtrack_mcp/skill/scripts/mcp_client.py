import json
import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.sessions = {}
        self.exit_stack = []

    async def connect(self):
        for server in self.config['servers']:
            params = StdioServerParameters(
                command=server['command'][0],
                args=server['command'][1:],
                env=os.environ.copy()
            )
            stdio_transport = stdio_client(params)
            read, write = await stdio_transport.__aenter__()
            self.exit_stack.append(stdio_transport)
            session = ClientSession(read, write)
            await session.__aenter__()
            self.exit_stack.append(session)
            await session.initialize()
            self.sessions[server['name']] = session

    async def call_tool(self, server_name, tool_name, arguments=None):
        session = self.sessions.get(server_name)
        if not session:
            raise ValueError(f"Server {server_name} not connected")
        return await session.call_tool(tool_name, arguments or {})

    async def disconnect(self):
        for item in reversed(self.exit_stack):
            await item.__aexit__(None, None, None)

async def call_mcp_tool(server_name, tool_name, arguments=None):
    config_path = os.path.join(os.path.dirname(__file__), '../mcp_config.json')
    client = MCPClient(config_path)
    await client.connect()
    try:
        result = await client.call_tool(server_name, tool_name, arguments)
        return result
    finally:
        await client.disconnect()
