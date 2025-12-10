# Queue / Stack Map – OS Dashboard AI Assistant

This map visualizes how front-end surfaces, middleware queues, and backend daemons
cooperate across the planes defined in `OS DashboardAIAssistantTOC.txt`.

```
[frontend/src/App.tsx (React SPA)]
      ↓ fetch (/system, /ai/ask, /search, /operations, /projects, /billing, /planes)
[FastAPI app (ai_os/app/main.py)]
      ↓                                                         ↓
[System Monitor | AI Proxy | Orchestrator | Audit Log | Change Engine]
      ↓                           ↓               ↓             ↓
[EventBus] → [Orchestrator] → [RegulationIngestDaemon] → [Connectors (PDF, Word, Notes)]
                                          ↓
                               [InMemoryVectorIndex + Embedder]
                                          ↓
                                    [CIR / Storage layer]
```

### Queue Layer
- **EventBus / Orchestrator / Daemons** (`ai_os/app/orchestration`) form the control-plane
  queue. `RegulationIngestDaemon` listens for `/pdfs/regulations` events and fans out to
  connectors + index updates.
- **AuditLog** now records every `/notes` and `/pdfs/regulations` request, and
  `ChangeEngine` computes diffs so governance/billing planes can queue reviews later.

### Stack Layer
- **Presentation stack**: `frontend/src/App.tsx` (React + TypeScript) → FastAPI endpoints.
- **Application stack**: FastAPI routes → connectors → storage/index → governance.
- **Infrastructure stack**: psutil OS driver (`system_monitor.py`), OpenAI proxy (`ai_proxy.py`), vector index, and future DB bindings.

### Identified Holes (now tracked)
| Component | Current State | Planned Hook |
| --- | --- | --- |
| Legacy CLI + `ui/` web shell | Not hitting FastAPI | Keep only for air-gapped demos; new default is `frontend/`. See `documentation/DEAD_CODE_LINKAGE.md`. |
| Additional connectors (Git, Excel, PowerPoint, Filesystem) | Not registered with orchestrator yet | Next step: add FastAPI endpoints per connector and register daemons that ingest their events. |
| ChangeEngine outputs | Newly wired for `/notes` and `/pdfs/regulations`; other write paths still pending | Extend daemons + upcoming workspace APIs to reuse `build_write_payload`. |

Maintain this map whenever new daemons, queues, or presentation surfaces are added so
front–middle–back flows stay explicitly documented.
