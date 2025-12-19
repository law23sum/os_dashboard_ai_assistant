# Architecture Decisions & Rationale Log

## 2025-12-10 — Diagnostics Layer & Guard Rails

**Context**  
Version 1000 demands provable reliability across personal/enterprise/government environments. React/Electron crashes previously surfaced as blank windows with no telemetry, starving the AI auto-fix workflow and complicating compliance reviews.

**Decision**  
1. **Runtime Diagnostics API** – Introduced `backend_api/routers/runtime_diagnostics.py` with a beacon-friendly `/api/runtime/diagnostics` endpoint. The route writes append-only JSON lines, is overridable via `OSDASH_RUNTIME_LOG`, and can be ingested by future observability backends.  
2. **Client Error Boundary & SDK** – Added `AppErrorBoundary` plus `frontend/src/utils/runtimeDiagnostics.ts` to capture window errors, unhandled Promise rejections, and boot-time anomalies. Events use `navigator.sendBeacon` when possible to avoid losing data during crashes.  
3. **Auto-Fix Enforcement** – Updated `scripts/ai_auto_fix.py` to automatically run high-signal desktop regression suites (Electron launcher + port guard) so the AI fixer always has actionable tests without additional manual flags.  
4. **Documentation Trail** – Authored `docs/FUTURE_VERSION_1000_BLUEPRINT.md`, `FEATURES_CHANGELOG.md`, and this log so every architectural pivot remains auditable and tethered to the Technical Spec Sheet (v6).

**Consequences**  
- Diagnostics data now exists for every surface, enabling upcoming observability dashboards, capsule-ledger root cause tracing, and AI-driven remediation.  
- Error boundaries prevent catastrophic UX regressions while signaling issues to backend operators.  
- Auto-fix orchestrations gain deterministic tests, aligning with the goal of automated self-repair across all git-managed projects.  
- Future work must extend diagnostics persistence into SQLite/OLAP stores and surface admin tooling, but the foundational plumbing is in place.
