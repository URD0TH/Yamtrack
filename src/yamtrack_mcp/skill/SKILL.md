---
name: yamtrack-mcp-workflow
description: Specialized workflows for Yamtrack media tracking via MCP — search, track, update, and query media through AI assistants (OpenCode, VS Code, Hermes, Claude Desktop).
---

# Yamtrack MCP Workflows

Automated media tracking and research for Yamtrack through its Model Context Protocol server.

## Endpoint & Transports

The MCP server speaks **Streamable HTTP** at `/mcp` — uvicorn on port `8002`, also proxied by nginx at `:8000/mcp/`.

- **HTTP** (`http://<host>:8002/mcp`): for HTTP-capable clients (OpenCode, VS Code, Hermes).
- **stdio**: launch the server directly with `python manage.py run_mcp` (or `uv run python src/manage.py run_mcp`). Used by stdio-only clients via a bridge, or by clients running in the same environment.

> When calling the endpoint directly (e.g. `curl`), send `Accept: application/json, text/event-stream`; otherwise nginx returns `406`.

## Authentication

Send the JWT in the `Authorization` header: `Authorization: Bearer <token>`. Read-only tools (`search_media`, `get_details`) work without a token; everything else requires it.

**Get a token** from the REST API with your account credentials:

```bash
curl -X POST https://your-yamtrack-instance.com/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"your-username","password":"your-password"}'
```

Use the `access` field of the response. Tokens expire; re-run when you get auth errors.

**Self-hosted / no account handy** — mint one inside the container (it shares the API `SECRET`, so the MCP server accepts it):

```bash
docker exec -i yamtrack uv run python -c "
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
u = get_user_model().objects.first()  # or .get(username='...')
print(str(AccessToken.for_user(u)))
"
```

For stdio, pass the token via the `YAMTRACK_JWT` env var or the `--token` argument. Status messages are written to **stderr** so they don't corrupt the stdio JSON-RPC stream.

## Client Configuration

### OpenCode

`opencode.json` (project root or `~/.config/opencode/opencode.json`):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "yamtrack": {
        "type": "remote",
        "url": "http://localhost:8002/mcp",
        "oauth": false,
        "enabled": true,
        "headers": { "Authorization": "Bearer <your-jwt-token>" }
      }
    }
  }
}
```

Set `"oauth": false` so OpenCode uses the static header instead of OAuth discovery. Interpolate with `"Bearer {env:YAMTRACK_JWT}"`.

### VS Code

`.vscode/mcp.json` (workspace) or user profile — `servers` key, `type: "http"`:

```json
{
  "servers": {
    "yamtrack": {
      "type": "http",
      "url": "http://localhost:8002/mcp",
      "headers": { "Authorization": "Bearer <your-jwt-token>" }
    }
  }
}
```

Use `${input:yamtrack-token}` in the header value to be prompted.

### Hermes

`~/.hermes/config.yaml` under `mcp_servers` (YAML). Hermes speaks both stdio and HTTP:

```yaml
mcp_servers:
  yamtrack:
    url: "http://localhost:8002/mcp"
    headers:
      Authorization: "Bearer <your-jwt-token>"
```

### Claude Desktop

`claude_desktop_config.json` is stdio-only and silently drops `url` / `type:"http"` entries. Bridge a local HTTP server with `mcp-remote` (Node.js 18+):

```json
{
  "mcpServers": {
    "yamtrack": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:8002/mcp", "--transport", "http-only"],
      "env": { "MCP_REMOTE_HEADERS": "Authorization: Bearer <your-jwt-token>" }
    }
  }
}
```

For a remote HTTPS instance, use **Settings → Connectors → Add custom connector** and paste `https://your-yamtrack-instance.com/mcp/`.

## Tools

- `search_media` — Search external providers.
- `get_details` — Metadata + tracking status.
- `list_tracked_media` — List the user's tracked media.
- `get_home` — Dashboard (in-progress / planning).
- `get_history` — Change history for an item.
- `create_entry` — Start tracking new media.
- `update_entry` — Update status/score/progress/notes.
- `update_progress` — Increase/decrease progress.
- `update_score` — Update score (0-10).
- `get_statistics` — Aggregated stats for a date range.

See `references/mcp_tools.md` for full input schemas.

## Workflows

### Research and Track
Search for media and start tracking it in "Planning" status if not already present.
**Location**: `skill/scripts/workflows/research_and_track.py`

### Batch Statistics
Aggregate stats across timeframes for comparison.
**Location**: `skill/scripts/workflows/batch_stats.py`

```python
from skill.scripts.workflows.batch_stats import get_stats_range
stats = await get_stats_range(start_date="2025-01-01", end_date="2025-12-31")
```

## Dev Scripts

Validation scripts in `skill/scripts/` (not deployed) hit the running container over HTTP — they do NOT mutate it:

- `mcp_client.py` — minimal HTTP client.
- `mcp_introspector.py` — dump tool schemas to `introspection.json` (generated dev artifact; the curated reference is `references/mcp_tools.md`).
- `mcp_smoke_test.py` — smoke test; reads `YAMTRACK_JWT` from the environment.
