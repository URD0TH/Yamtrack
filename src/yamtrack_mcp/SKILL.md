---
name: yamtrack-mcp-workflow
description: Specialized workflows for Yamtrack media tracking via MCP.
---

# Yamtrack MCP Workflows

Automated media tracking and research for Yamtrack.

## Prerequisites

Scripts automatically install `mcp` SDK if missing.

## Workflows

### Research and Track
Search for media and start tracking it in "Planning" status if not already present.
**Location**: `scripts/workflows/research_and_track.py`

### Batch Statistics
Aggregate stats across timeframes for comparison.
**Location**: `scripts/workflows/batch_stats.py`

**Usage**:
```python
from scripts.workflows.batch_stats import get_stats_range
stats = await get_stats_range(start_date="2025-01-01", end_date="2025-12-31")
```


## Tools
- `search_media`: External search.
- `get_details`: Metadata + tracking status.
- `create_entry`: Add to library.
- `update_entry`: Modify status/score.

Use `uv run python src/manage.py run_mcp` for stdio access.
