# Architectural Decisions

Updated: 2025-02-17

- **Primary scope**: Focus implementation on `os_dashboard_ai_assistant` repo; archive/reference repos remain mapped but untouched until prioritized. Documented in ARCHITECTURE_OVERVIEW and backlog.
- **CLI consolidation**: Expose workspace automation through `osdash scan|test|run|doctor` using existing harness/workspace utilities rather than duplicating scripts. Keeps single entry point for DevEx.
- **Import normalization**: Swapped fragile relative imports in CLI commands to absolute `assistant_hub.*` to support package execution and testing. Prevents import errors during workspace orchestration.
- **Spec authority**: Treated `Technical Spec Sheet (Version 6 Latest Version)` as canonical; legacy docs only for lineage. Gaps resolved by choosing simplest secure default (auth middleware, pagination, structured logging).
- **Doc outputs**: Canonical spec/blueprint/risks/TODO/decisions stored under `OS_Dashboard_AI_Assistant/` for easy discovery; mirrors spec numbering for future automation.
- **Security-first defaults**: Future endpoints will require bearer/API-key auth, emit correlation IDs, and enforce pagination/timeouts; SQLite retained for dev while preparing migration to Postgres.
