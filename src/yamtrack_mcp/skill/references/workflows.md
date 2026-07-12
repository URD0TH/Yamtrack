# Workflows Reference

Detailed behavior of the packaged workflows in `skill/scripts/workflows/`. Both are async coroutines that call the MCP tools documented in [mcp_tools.md](mcp_tools.md).

## research_and_track

Search for media and start tracking it in **Planning** status — but only if it is not already tracked.

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | yes | — | Search query. |
| `media_type` | string | no | `tv` | `tv`, `movie`, `anime`, `manga`, `game`, `book`, `comic`, `boardgame`. |

### Steps

1. Call `search_media(query, media_type)` and take the **first** result (`media_id`, `source`). If there are no results, return `"No results found."`.
2. Call `get_details(media_id, media_type, source)`. If the response already contains a `tracking` entry, return early with status `already_tracking` (no duplicate is created).
3. Otherwise call `create_entry(media_id, source, media_type, status="Planning")`.

### Returns

A dict with one of:

- `{"status": "already_tracking", "title": ..., "tracking": ...}`
- `{"status": "created", "details": ...}`

### Example

```python
from skill.scripts.workflows.research_and_track import research_and_track

result = await research_and_track("Dune", media_type="movie")
```

## batch_stats

Fetch aggregated statistics for a date range (defaults to the full year 2025).

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `start_date` | string | no | `2025-01-01` | `YYYY-MM-DD`. |
| `end_date` | string | no | `2025-12-31` | `YYYY-MM-DD`. |

### Steps

1. Call `get_statistics(start_date, end_date)` and return the parsed JSON response.

### Returns

The aggregated statistics object returned by `get_statistics`.

### Example

```python
from skill.scripts.workflows.batch_stats import get_stats_range

stats = await get_stats_range(start_date="2025-01-01", end_date="2025-12-31")
```
