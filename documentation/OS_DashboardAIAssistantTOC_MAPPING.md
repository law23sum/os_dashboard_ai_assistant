# OS Dashboard AI Assistant — Spec Mapping

This note links the latest code additions to the canonical requirements in `OS DashboardAIAssistantTOC.txt`.

## 1.7 Driver-Aware Orchestrator
- **System telemetry endpoint** (`ai_os/app/system_monitor.py`) fulfills 1.7.2/1.7.4 by exposing OS stats for the presentation layer and control planes.
- **React dashboard cards** (`dashboard.js`) surface those stats per 1.7.2 and align with the human-in-the-loop UX requirements.

## 5.x Driver Architecture
- `system_monitor.py` implements the OS driver visibility layer (5.2/5.3) with psutil, ready for containerized or bare-metal deployments.
- `ai_proxy.py` represents the SaaS/model driver portion of 5.6 by abstracting the OpenAI endpoint.

## 0.x Mission & Personas
- `ai_proxy.py` provides the lightweight persona dialog loop (0.5/0.6) so personas like Chris/AIC can interface with the orchestrator without relying on the full assistant core yet.

## 6.x Observability & Data Plane
- The telemetry payload attaches `spec_refs` for downstream governance/observability tooling as described in 6.6.

## Spec Registry Guardrails
- `assistant_core/spec_registry.py` parses `OS DashboardAIAssistantTOC.txt` and offers helpers to validate section identifiers.
- Core services register themselves with the registry so we can trace runtime behavior back to chapters (e.g., `ai_os/app/system_monitor.py` for 1.7.2/6.6, `ai_os/app/ai_proxy.py` for 0.5/0.6/1.7.3/5.6, `assistant_core/cognitive_framework.py` for 0.5/4.x, `assistant_core/security/governance_engine.py` for 2.3/10.x/11.5 + 14.x, `assistant_core/automation_orchestrator.py` for 2.2/7.13/8.10/8.13/14.1/14.3, `assistant_core/task_automation.py` for 3.4/7.2.2/8.12, `assistant_core/ai_services_api.py` for 1.7.3/2.2/5.6/8.10/9.18, and `assistant_core/failure_registry.py` for 14.1‑14.7).
- Tests under `tests/test_spec_registry.py` ensure the parser understands nested identifiers like `17.3.9.a` and fails fast when an invalid section is referenced.

## 14.x Failure Modes, Risk & Resilience
- `assistant_core/failure_registry.py` encodes the failure taxonomy, detection signals, recovery capsules, and risk scoring described in Section 14 (planes/layers/scopes/severity/root causes).
- `assistant_core/security/governance_engine.py` emits failure events on policy violations, feeds HyperDaemon risk recommendations (14.7), and provides recovery capsules (`capsule.governance.policy.rollback`).
- `assistant_core/automation_orchestrator.py` registers detection signals for action timeouts/errors and records control-plane failures with workflow/driver recovery capsules.
- FastAPI exposes `/failures` (`ai_os/app/main.py`) so observability dashboards (Section 11) can query registry summaries directly.
- Metrics exposed via `get_governance_metrics()` include failure summaries, detection signals, and HyperDaemon recommendations so Observability (Section 11) and Policy Engine (Section 10) consumers can reason about risk posture.
- Tests under `tests/test_failure_registry.py` cover the registry and detection-signal summaries.

## Usage
- The FastAPI service now exposes `/system`, `/ai/ask`, and `/failures`. Each endpoint embeds `spec_refs` arrays or returns registry summaries so automated compliance checks can verify coverage.
- Front-end consumers reference these endpoints, ensuring each UI feature is directly traceable to the canon spec.

Update this file whenever a new feature or service is added so compliance remains auditable.
