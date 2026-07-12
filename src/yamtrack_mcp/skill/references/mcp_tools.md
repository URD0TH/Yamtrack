# MCP Tools Reference

Reference for the Yamtrack MCP server tools. All tools require a JWT except the read-only ones noted.

## search_media

Search external providers for media.

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | yes | — | Search query. |
| `media_type` | string | no | `tv` | `tv`, `movie`, `anime`, `manga`, `game`, `book`, `comic`, `boardgame`. |
| `page` | integer | no | `1` | Result page. |
| `source` | string \| null | no | `null` | Restrict to a source (e.g. `tmdb`). |

## get_details

Get metadata for a media item from an external provider.

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `source` | string | yes | — | Provider (`tmdb`, `mal`, `igdb`, ...). |
| `media_type` | string | yes | — | Media type. |
| `media_id` | string | yes | — | Provider media id. |
| `season_number` | integer \| null | no | `null` | Season (for tv/anime). |

## list_tracked_media

List media tracked by the authenticated user.

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `media_type` | string \| null | no | `null` | Filter by media type. |
| `status` | string | no | `All` | `All`, `Completed`, `In progress`, `Planning`, `Paused`, `Dropped`. |
| `sort` | string \| null | no | `null` | Sort key. |
| `search` | string | no | `""` | Free-text filter. |

## create_entry

Start tracking a new media item from an external provider.

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `media_id` | string | yes | — | Provider media id. |
| `source` | string | yes | — | Provider. |
| `media_type` | string | yes | — | Media type. |
| `status` | string \| null | no | `null` | Defaults to `Completed` if omitted. |
| `score` | number \| null | no | `null` | 0–10. |
| `progress` | integer | no | `0` | Progress count. |
| `notes` | string | no | `""` | Free-text note. |

## update_entry

Update status, score, progress, or notes for a tracked item.

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `media_type` | string | yes | — | Media type. |
| `instance_id` | integer | yes | — | Tracked item id. |
| `status` | string \| null | no | `null` | New status. |
| `score` | number \| null | no | `null` | 0–10. |
| `progress` | integer \| null | no | `null` | Progress count. |
| `notes` | string \| null | no | `null` | Free-text note. |

## update_progress

Increase or decrease progress on a tracked item.

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `media_type` | string | yes | — | Media type. |
| `instance_id` | integer | yes | — | Tracked item id. |
| `operation` | string | yes | — | `increase` or `decrease`. |

## update_score

Update the score (0–10) for a tracked item.

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `media_type` | string | yes | — | Media type. |
| `instance_id` | integer | yes | — | Tracked item id. |
| `score` | number | yes | — | 0–10. |

## get_home

Dashboard data: in-progress and planning media.

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `sort` | string | no | `upcoming` | Sort key. |

## get_statistics

Aggregated statistics for the authenticated user.

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `start_date` | string \| null | no | `null` | `YYYY-MM-DD`. Use `all` for no filter. |
| `end_date` | string \| null | no | `null` | `YYYY-MM-DD`. Use `all` for no filter. |

Defaults to the last 365 days.

## get_history

Change history for a tracked media item.

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `source` | string | yes | — | Provider. |
| `media_type` | string | yes | — | Media type. |
| `media_id` | string | yes | — | Provider media id. |
| `season_number` | integer \| null | no | `null` | Season. |
| `episode_number` | integer \| null | no | `null` | Episode. |
