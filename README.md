# OS Dashboard AI Assistant Scaffold

This repository now ships an installable scaffold for the "osdash" CLI and a minimal agent/integration architecture. The package is intentionally lightweight so you can extend each module at your own pace while still being able to run end-to-end commands.

## Install

```bash
pip install .
```

## CLI usage

Example commands after installation:

- `osdash projects list` – show known projects from the JSON state file.
- `osdash projects add <name>` – add a project to the state file.
- `osdash onenote notebooks` – list stub OneNote notebooks via the Graph stub.
- `osdash excel workbooks` – show Graph stub workbook metadata.
- `osdash excel summarize-local <path>` – summarize a local Excel workbook (pandas required).
- `osdash word summarize-local <path>` – summarize a local Word document.
- `osdash software defaults` – check where git, Word, Excel, and PDF viewers are installed.
- `osdash software locate <name>` – look up a specific executable and optional aliases.
- `osdash chat <agent> <message>` – send a message to one of the scaffolded agents (aic, aria, sora).
- `osdash workflow-clean-notebook <path>` – run the example notebook cleaning workflow prompt.
- `osdash workflow-knowledge-pipeline <notes_path>` – convert raw notes into a structured Markdown brief, log the action to the audit file, and optionally commit the generated deliverable when run inside a git repo.

## Package layout

- `assistant_hub/config.py` – environment-driven configuration for OpenAI and Microsoft Graph.
- `assistant_hub/core/` – lightweight models, JSON state store, router, and scheduler stub.
- `assistant_hub/ai/` – OpenAI wrapper, prompts, tool registry, agents, and a sample workflow.
- `assistant_hub/integrations/` – stub clients/services for Graph, OneNote, Excel, Word, and filesystem helpers.
- `assistant_hub/versioning/` – simple git helpers plus a background commit queue stub.
- `assistant_hub/ui/terminal/cli.py` – `osdash` Click-based entry point exposing demo commands.
- `assistant_hub/ui/gui/app.py` – lightweight GUI for locating installed software.
- `assistant_hub/data/state.json` – default JSON state used by the CLI.
- `assistant_hub/document_templates.py` – governed template catalog with multi-format samples (CSV/JSON/PDF/XLSX/DOCX/TXT/PPTX) covering briefs, proposals, compliance reports, patient summaries, risk assessments, regulatory filings, engineering specs, technical documents, product updates, and operational manuals.

Use this baseline to plug in real API calls, prompt orchestration, and richer state handling.

## Template-driven deliverables

The template catalog enforces that every AI edit is tracked, every change is diffed, every document has version history, every operation is timestamped, every action is reversible, and every output is accountable. It aligns the stack so OneNote serves as structured memory, Word is the formatted deliverable engine, Excel is the analytical substrate, Git preserves lineage, ChatGPT is the reasoning center, daemons form the active cortex, and AIC/Sora/Aria guide knowledge formation. Daemons can notice missing documents, draft proposals, update reports, summarize notebooks, analyze spreadsheets, reorganize folders, update tasks, alert when content is outdated, track version history, suggest improvements, predict next steps, and execute workflows.

## Vision

Read the high-level vision for how the OS Dashboard AI Assistant grows into a governed, end-to-end cognitive operating system in [VISION.md](VISION.md). For a deeper dive into the structural, societal, economic, and cognitive impacts of the platform, see the accompanying [GLOBAL_IMPACT_WHITE_PAPER.md](GLOBAL_IMPACT_WHITE_PAPER.md).
