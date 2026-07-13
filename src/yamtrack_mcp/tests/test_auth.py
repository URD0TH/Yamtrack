"""Tests for MCP token authentication."""

import pytest

from users.models import User

from yamtrack_mcp.auth import get_user_from_token

pytestmark = pytest.mark.django_db


def test_static_token_authenticates():
    """The user's static token (User.token) authenticates like an API key."""
    user = User.objects.create_user(username="mcp", password="x")
    assert get_user_from_token(user.token) == user


def test_invalid_token_rejected():
    """An unknown token returns None, keeping tools read-only."""
    User.objects.create_user(username="mcp", password="x")
    assert get_user_from_token("not-a-real-token") is None


def test_empty_token_rejected():
    """An empty token returns None."""
    assert get_user_from_token("") is None
