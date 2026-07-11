import dataclasses
import socket

from health_check.base import HealthCheck
from health_check.exceptions import ServiceUnavailable


@dataclasses.dataclass
class MCPHealthCheck(HealthCheck):
    """Check that the MCP uvicorn process is listening on its port."""

    host: str = "127.0.0.1"
    port: int = 8002

    async def run(self):
        """Connect to the MCP server port to verify it is running."""
        conn_err = "MCP: Connection refused"
        os_err = "MCP: Connection error"
        try:
            s = socket.create_connection((self.host, self.port), timeout=5)
            s.close()
        except ConnectionRefusedError as e:
            raise ServiceUnavailable(conn_err) from e
        except OSError as e:
            raise ServiceUnavailable(os_err) from e
