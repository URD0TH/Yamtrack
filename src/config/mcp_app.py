"""ASGI entrypoint for the Yamtrack MCP server (Streamable HTTP)."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from yamtrack_mcp.auth import jwt_auth_middleware  # noqa: E402
from yamtrack_mcp.core import mcp  # noqa: E402

_mcp_app = mcp.streamable_http_app()


async def app(scope, receive, send):
    """ASGI app: MCP Streamable HTTP wrapped with JWT auth middleware."""
    await jwt_auth_middleware(scope, receive, send, _mcp_app)
