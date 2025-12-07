# OS Dashboard Assistant Architecture Skeleton

This repository now includes scaffolded layers to support the unified vision
outlined for Excel, OneNote, Word, Git-based versioning, and AI agents:

## Layers
- **AI Layer (`ai_layer/`)**: shared OpenAI client, persona prompts for AIC/Sora/Aria,
  reusable tools (summaries, HTML rewrite, pandas code generation), and example
  workflows coordinating integrations with git history.
- **Integrations (`integrations/`)**: modular clients and services for
  Microsoft Graph (OneNote/Excel/Word), local file-system helpers, and
  higher-level services that pair platform APIs with AI transforms.
- **Versioning (`versioning/`)**: git manager plus async queue so every
  AI-authored file change can be staged and committed automatically.

## Extending
- Wire these services into the existing GUI/terminal by instantiating the
  services and invoking workflows such as `NotebookCleanupWorkflow` or
  `ExcelSummaryWorkflow`.
- Daemons or schedulers should call integrations and push paths into
  `versioning.git_async.enqueue_commit` to maintain a transparent history of
  AI actions.
