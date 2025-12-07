# OS Dashboard AI Assistant

This repository provides the evolving OS Dashboard AI assistant that coordinates
multiple AI personas (AIC, Sora, Aria), integrations, and a GUI/terminal
interface. The codebase now formalizes the architecture for connecting to
OneNote, Excel, Word, and other services through a modular integrations layer
backed by automatic git versioning.

## Architecture at a Glance

- **Core OS**: projects, tasks, scheduler, and routing that keep agent runs
  organized.
- **Integrations Layer**: pluggable clients for Microsoft Graph (OneNote,
  Excel, Word), local filesystem helpers, and existing calendar/email/github
  connectors.
- **AI Layer**: persona prompts and tool workflows (ready to be wired into the
  new integrations for summarization, cleanup, and drafting).
- **Versioning Layer**: background git helpers that stage and commit every
  AI-driven mutation for a durable audit trail.
- **Interface Layer**: GUI/TUI entry points in `assistant_hub_gui` that call
  into the services above.

## New Integration Skeletons

The `assistant_hub/integrations` package now includes Microsoft Graph-ready
clients and local fallbacks:

- **OneNote** (`onenote/`): list notebooks/sections/pages, fetch or update page
  HTML, mirror cloud pages to disk, and prepare placeholder cleanups/summaries.
- **Excel** (`excel/`): Graph-based workbook/sheet/range helpers, lightweight
  local workbook utilities, and helpers to export ranges or attach summary
  files.
- **Word** (`word/`): download/upload Word documents over Graph and create
  local revision files for AI drafts.
- **Filesystem** (`filesystem/`): discover tracked files across the workspace.
- **Graph core** (`msgraph/`): shared auth + REST wrapper for Microsoft Graph.

Each service is intentionally thin so UI commands or daemons can orchestrate
AI prompts separately.

## Git Auto-Versioning

The new `assistant_hub/versioning` package provides:

- `GitManager` for staging/committing with actor metadata.
- `git_autocommit` helpers used by integrations after they write to disk.
- `git_async` queue for non-blocking background commits so UI/agents remain
  responsive.

This makes it easy to log every AI-generated change—whether mirroring a cloud
note or creating an Excel summary—directly into git with standardized commit
messages.
