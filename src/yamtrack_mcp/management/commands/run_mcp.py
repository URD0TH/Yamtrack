"""Django management command to run the MCP server over stdio."""

import logging
import os

from django.core.management.base import BaseCommand, CommandParser

from yamtrack_mcp.auth import current_user, get_user_from_token
from yamtrack_mcp.core import mcp

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Run the Yamtrack MCP server over stdio for local MCP clients."""

    help = "Run the Yamtrack MCP server over stdio (for local MCP clients)"

    def add_arguments(self, parser: CommandParser):
        """Add --token argument for JWT auth."""
        parser.add_argument(
            "--token",
            type=str,
            help="JWT token for authentication (or set YAMTRACK_JWT env var)",
        )

    def handle(self, *_args, **options):
        """Run the MCP server over stdio with optional JWT auth."""
        token = options["token"] or os.environ.get("YAMTRACK_JWT")
        if token:
            user = get_user_from_token(token)
            if user:
                current_user.set(user)
                self.stderr.write(f"MCP stdio authenticated as {user.email}")
            else:
                self.stderr.write("MCP stdio: invalid token, running without auth")
        else:
            msg = "MCP stdio running without authentication (read-only tools)"
            self.stderr.write(msg)

        mcp.run(transport="stdio")
