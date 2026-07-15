# Yamtrack — DOX Root

- DOX is highly performant [AGENTS.md](http://AGENTS.md) hierarchy installed here

- Agent must follow DOX instructions across any edits

## Project

- Self-hosted media tracker (Django 5.2, Python 3.12+) for movies, TV, anime, manga, games, books, comics, board games.
- Package manager: `uv`. Run everything through `uv run ...`.
- Tests: `pytest` (`DJANGO_SETTINGS_MODULE=config.test_settings`, see `pytest.ini`). Run from `src/`.
- Lint/format: `ruff` (check + format), `djlint` (templates). Pre-commit runs all hooks (`uv run pre-commit run --all-files`).
- Migrations must be committed: `uv run python src/manage.py makemigrations --check`.
- Background jobs: Celery + Redis + django-celery-beat. Result backend: Django DB.
- Auth: django-allauth (social + OIDC) for the web app. REST API/MCP: static per-user API key only (no JWT).
- Docs site built with zensical (`uv run zensical serve`), sources in `docs/`.

## Core Contract

- [AGENTS.md](http://AGENTS.md) files are binding work contracts for their subtrees

- Work products, source materials, instructions, records, assets, and durable docs must stay understandable from the nearest applicable [AGENTS.md](http://AGENTS.md) plus every parent [AGENTS.md](http://AGENTS.md) above it

## Hard Boundaries

- **NEVER do anything the user did not ask for.** Only execute explicitly requested tasks. If unsure whether a task is in scope, STOP and ask before acting — do not infer, assume, or "helpfully" add unrequested work (e.g. do not commit/force-add files, edit docs, or run commands beyond the literal request). When in doubt, ask.
- The `AGENTS.md` files are intentionally git-ignored (see `.gitignore`). They must **not** be committed or force-added (`git add -f`) to the repository. Keep them local.

## Read Before Editing

1. Read the root [AGENTS.md](http://AGENTS.md)

2. Identify every file or folder you expect to touch

3. Walk from the repository root to each target path

4. Read every [AGENTS.md](http://AGENTS.md) found along each route

5. If a parent [AGENTS.md](http://AGENTS.md) lists a child [AGENTS.md](http://AGENTS.md) whose scope contains the path, read that child and continue from there

6. Use the nearest [AGENTS.md](http://AGENTS.md) as the local contract and parent docs for repo-wide rules

7. If docs conflict, the closer doc controls local work details, but no child doc may weaken DOX

Do not rely on memory. Re-read the applicable DOX chain in the current session before editing.

## Update After Editing

Every meaningful change requires a DOX pass before the task is done.

Update the closest owning [AGENTS.md](http://AGENTS.md) when a change affects:

- purpose, scope, ownership, or responsibilities

- durable structure, contracts, workflows, or operating rules

- required inputs, outputs, permissions, constraints, side effects, or artifacts

- user preferences about behavior, communication, process, organization, or quality

- [AGENTS.md](http://AGENTS.md) creation, deletion, move, rename, or index contents

Update parent docs when parent-level structure, ownership, workflow, or child index changes. Update child docs when parent changes alter local rules. Remove stale or contradictory text immediately. Small edits that do not change behavior or contracts may leave docs unchanged, but the DOX pass still must happen.

## Hierarchy

- Root [AGENTS.md](http://AGENTS.md) is the DOX rail: project-wide instructions, global preferences, durable workflow rules, and the top-level Child DOX Index

- Child [AGENTS.md](http://AGENTS.md) files own domain-specific instructions and their own Child DOX Index

- Each parent explains what its direct children cover and what stays owned by the parent

- The closer a doc is to the work, the more specific and practical it must be

## Child Doc Shape

- Create a child [AGENTS.md](http://AGENTS.md) when a folder becomes a durable boundary with its own purpose, rules, responsibilities, workflow, materials, or quality standards

- Work Guidance must reflect the current standards of the project or user instructions; if there are no specific standards or instructions yet, leave it empty

- Verification must reflect an existing check; if no verification framework exists yet, leave it empty and update it when one exists

Default section order:

- Purpose

- Ownership

- Local Contracts

- Work Guidance

- Verification

- Child DOX Index

## Style

- Keep docs concise, current, and operational

- Document stable contracts, not diary entries

- Put broad rules in parent docs and concrete details in child docs

- Prefer direct bullets with explicit names

- Do not duplicate rules across many files unless each scope needs a local version

- Delete stale notes instead of explaining history

- Trim obvious statements, repeated rules, misplaced detail, and warnings for risks that no longer exist

## Closeout

1. Re-check changed paths against the DOX chain

2. Update nearest owning docs and any affected parents or children

3. Refresh every affected Child DOX Index

4. Remove stale or contradictory text

5. Run existing verification when relevant

6. Report any docs intentionally left unchanged and why

## User Preferences

- Respond in Spanish (user requested). Code, comments, commit messages, and PRs stay in English.

When the user requests a durable behavior change, record it here or in the relevant child [AGENTS.md](http://AGENTS.md)

## Child DOX Index

- `src/config/` — Django settings, URLs, Celery, deployment config. See `src/config/AGENTS.md`.
- `src/app/` — Core tracking app: models, views, providers, statistics, history. See `src/app/AGENTS.md`.
- `src/app/providers/` — External metadata providers (TMDB, MAL, IGDB, etc.). See `src/app/providers/AGENTS.md`.
- `src/api/` — REST API (DRF, API-key auth). See `src/api/AGENTS.md`.
- `src/events/` — Calendar feeds and release notifications. See `src/events/AGENTS.md`.
- `src/integrations/` — Imports, exports, and media-server webhooks. See `src/integrations/AGENTS.md`.
- `src/lists/` — User-created media lists. See `src/lists/AGENTS.md`.
- `src/users/` — Accounts, profiles, auth flows. See `src/users/AGENTS.md`.
- `mcp/` — Standalone TypeScript stdio MCP server for the REST API; git submodule of `yamtrack-mcp`. See `mcp/AGENTS.md`.
- `docs/` — Documentation site sources. See `docs/AGENTS.md`.
- `wiki/` — GitHub wiki submodule (external repo `Yamtrack.wiki.git`); user-facing API and MCP docs. See `wiki/AGENTS.md`.