"""JWT authentication for MCP server.

Provides contextvar-based auth shared by both stdio and HTTP transports.
"""

import contextvars
import logging

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)

User = get_user_model()

current_user: contextvars.ContextVar = contextvars.ContextVar(
    "mcp_current_user", default=None
)


def get_current_user():
    """Return the authenticated user from current context, or None."""
    return current_user.get()


def get_user_from_jwt(token: str):
    """Validate a JWT token and return the user, or None if invalid."""
    if not token:
        return None
    try:
        access_token = AccessToken(token)
        return User.objects.get(id=access_token["user_id"])
    except (TokenError, User.DoesNotExist) as exc:
        logger.warning("MCP auth failed: %s", exc)
        return None


async def jwt_auth_middleware(scope, receive, send, next_app):
    """ASGI middleware that validates JWT from Authorization header."""
    if scope["type"] != "http":
        await next_app(scope, receive, send)
        return

    headers = {k.decode(): v.decode() for k, v in scope.get("headers", [])}
    auth = headers.get("authorization", "")

    user = None
    if auth.startswith("Bearer "):
        user = await sync_to_async(get_user_from_jwt)(auth.removeprefix("Bearer "))

    token = current_user.set(user)
    try:
        await next_app(scope, receive, send)
    finally:
        current_user.reset(token)
