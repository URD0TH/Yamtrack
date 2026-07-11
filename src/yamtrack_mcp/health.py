import dataclasses
import socket
from typing import override

from health_check.base import HealthCheck  # type: ignore[import-untyped]
from health_check.exceptions import ServiceUnavailable  # type: ignore[import-untyped]


@dataclasses.dataclass
class MCPHealthCheck(HealthCheck):
    """Check that the MCP uvicorn process is listening on its port."""

    host: str = "127.0.0.1"
    port: int = 8002

    @override
    async def run(self) -> None:
        """Connect to the MCP server port to verify it is running."""
        conn_err = "MCP: Connection refused"
        os_err = "MCP: Connection error"
        try:
            sock = socket.create_connection((self.host, self.port), timeout=5)
            sock.close()
        except ConnectionRefusedError as e:
            raise ServiceUnavailable(conn_err) from e
        except OSError as e:
            raise ServiceUnavailable(os_err) from e
