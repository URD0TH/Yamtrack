import os
import anyio
from functools import partial

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from yamtrack_mcp.auth import jwt_auth_middleware  # noqa: E402
from yamtrack_mcp.core import mcp  # noqa: E402
from mcp.server.streamable_http import StreamableHTTPServerTransport, GET_STREAM_KEY, MCP_SESSION_ID_HEADER, CONTENT_TYPE_SSE, SESSION_ID_PATTERN

_mcp_app = mcp.streamable_http_app()

# --- MONKEYPATCH START ---
async def patched_handle_get_request(self, request, send) -> None:
    from starlette.responses import Response
    from http import HTTPStatus
    from mcp.shared.message import ServerMessageMetadata, JSONRPCMessage, SessionMessage
    from mcp.types import JSONRPCResponse, JSONRPCError
    from mcp.server.streamable_http import EventMessage, SSEEvent, REQUEST_STREAM_BUFFER_SIZE
    from sse_starlette import EventSourceResponse

    accept_header = request.headers.get("accept", "")
    accept_types = [m.strip() for m in accept_header.split(",")]
    has_json = any(m.startswith("application/json") for m in accept_types)
    has_sse = any(m.startswith("text/event-stream") for m in accept_types)
    
    if not (has_json and has_sse):
        response = Response(
            '{"jsonrpc":"2.0","id":"server-error","error":{"code":-32600,"message":"Not Acceptable"}}',
            status_code=406,
            headers={"Content-Type": "application/json"}
        )
        await response(request.scope, request.receive, send)
        return

    session_id = request.headers.get(MCP_SESSION_ID_HEADER)
    if session_id and not SESSION_ID_PATTERN.fullmatch(session_id):
        response = Response(
            '{"jsonrpc":"2.0","id":"server-error","error":{"code":-32600,"message":"Bad Request: Invalid session ID"}}',
            status_code=400,
            headers={"Content-Type": "application/json"}
        )
        await response(request.scope, request.receive, send)
        return
        
    stream_key = session_id if session_id else GET_STREAM_KEY

    if stream_key in self._request_streams:
        response = Response(
            '{"jsonrpc":"2.0","id":"server-error","error":{"code":-32602,"message":"Conflict: Only one SSE stream is allowed per session"}}',
            status_code=409,
            headers={"Content-Type": "application/json"}
        )
        await response(request.scope, request.receive, send)
        return

    sse_stream_writer, sse_stream_reader = anyio.create_memory_object_stream[SSEEvent](0)
    self._sse_stream_writers[stream_key] = sse_stream_writer
    self._request_streams[stream_key] = anyio.create_memory_object_stream[EventMessage](16)
    request_stream_reader = self._request_streams[stream_key][1]

    headers = {
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        "Content-Type": CONTENT_TYPE_SSE,
    }
    if self.mcp_session_id:
        headers[MCP_SESSION_ID_HEADER] = self.mcp_session_id

    response = EventSourceResponse(
        content=sse_stream_reader,
        data_sender_callable=partial(self._run_sse_writer, stream_key, sse_stream_writer, request_stream_reader, None),
        headers=headers,
    )
    await response(request.scope, request.receive, send)

StreamableHTTPServerTransport._handle_get_request = patched_handle_get_request
# --- MONKEYPATCH END ---

async def app(scope, receive, send):
    await jwt_auth_middleware(scope, receive, send, _mcp_app)
