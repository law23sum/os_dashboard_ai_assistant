# OS Dashboard Future Feature Log (v1000 roadmap)

This log captures “next-thousand” concepts so we can keep a running history of
major capabilities. Each entry should describe *why* the feature matters,
roughly how it works, and the user impact. Append new entries as future updates
land.

## 2025-12-12 · Sir Chief Fellow Director Principal Software Solutions Systems Engineer Architect

### 1. AI Copilot Console
- **Goal**: unify Tkinter AI tabs (chat, personas, daemon control, writer,
  reasoning, driver throttles, orchestrator buttons) into a single React view.
- **Status**: first pass shipped (`/ai/copilot`). Parity exists for persona
  switching, chat triage, writer drafts, ops ledger, reasoning snapshots, AI OS
  start/stop controls, daemon toggles, and driver admission sliders.
- **Impact**: React desktop + web builds now offer the same high-touch control
  room experience as the legacy shell.

### 2. Assistants API CLI bridge
- **Goal**: reproduce the OpenAI “Assistants API Overview” notebook flow as a
  command-line workflow so engineers can test code interpreter, file search,
  and function-calling without copy/pasting.
- **Status**: `scripts/assistants_demo.py` added; README documents usage.
- **Impact**: local experimentation matches the docs; outputs feed back into the
  shared personas/workspaces.

### 3. Assistants CLI telemetry widget
- **Goal**: surface Assistants CLI work inside the React Copilot console until
  backend APIs exist for storing threads/runs.
- **Status**: `/ai/copilot` now ships an “Assistants CLI Activity” panel with a form
  that logs question, tools, status, and notes; entries persist to `localStorage`.
- **Impact**: desktop/web shells mirror the Tkinter logbook, so operators always
  remember which tools/runs need follow-up even when the backend isn’t running.

### 4. Future Planning Slots
- **Hyper-Assistants integration**: extend `/ai/copilot` with a panel that
  lists active assistant threads and run statuses, so CLI workflows appear in
  the GUI automatically.
- **Ops Auto-Fix hooks**: wire `scripts/ai_auto_fix.py` into launch scripts so
  each project run automatically tails logs/tests and loops corrections via AI.
