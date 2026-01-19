# GUI Nav Registry Update Report

## Observed Snapshot
- Source: `frontend/public/gui_nav.latest.json`
- Converted snapshot: `contracts/gui/gui_nav.observed.json`
- Counts (observed)
  - Personal: 13 platforms, 93 categories, 508 features
  - Business/Team: 13 platforms, 93 categories, 508 features
  - Enterprise: 13 platforms, 89 categories, 394 features

## Target Snapshot
- Registry: `contracts/gui/gui_nav.latest.json`
- Target copy: `contracts/gui/gui_nav.target.json`
- Counts (target)
  - Personal: 13 platforms, 93 categories, 508 features
  - Business/Team: 13 platforms, 93 categories, 508 features
  - Enterprise: 13 platforms, 89 categories, 394 features

## Additions
- Contract registry files
  - `contracts/gui/gui_nav.latest.json`
  - `contracts/gui/gui_nav.schema.json`
  - `contracts/gui/gui_nav.laws.json`
  - `contracts/gui/gui_nav.observed.json`
  - `contracts/gui/gui_nav.target.json`
- Structural tiers (data model)
  - `contracts/structure/structural_tiers.latest.json`
- Missing platform/route coverage in registry (examples)
  - `/dashboard`, `/mission`, `/governance`, `/ai`, `/admin`, `/workspaces`, `/drivers`, `/simulations`, `/roadmap`
  - `/ai/tooling-lab`, `/docs/reference`, `/operations`, `/roadmap/future-capabilities`, `/future`, `/governance/security`
- Category minimums
  - Auto-added `Overview`, `Runbook`, `Evidence` features where categories had <3 features (routes use `/{platform}/{category}/...`).

## Changes
- Registry-first pipeline
  - `scripts/build_gui_nav_registry.py` builds the contract registry from legacy nav + seed + auto-fill.
  - `scripts/sync_gui_nav_legacy.py` regenerates legacy nav JSONs for runtime compatibility.
  - `scripts/generate_ia_manifest_from_gui_nav.js` now reads the contract registry.
- Validation gates
  - `scripts/validate_gui_nav.js` validates contract registry, platform order, category/feature minimums, and route coverage.
- Self-linking + events
  - `frontend/src/domain/projections.ts` publishes ledger events + projection updates and subscribes via SSE.
  - `ai_os/app/main.py` adds `/api/ledger/events`, `/api/ledger/projections`, `/api/ledger/stream`.
  - `frontend/src/lib/apiClient.ts` adds `X-Request-Id`, `X-Tenant-Id`, `X-Workspace-Id`, `X-Idempotency-Key` headers.
- Feature scaffolding
  - `frontend/src/components/templates/FeaturePageTemplate.tsx` now includes Related panel, edition breadcrumb, and projection subscription.
  - `frontend/src/navigation/NavRouteRenderer.tsx` wraps non-template feature routes to guarantee Parameters/Execute/Results.
  - `frontend/src/navigation/routeComponentMeta.ts` generated to avoid double-wrapping template pages.
- Page contracts
  - `frontend/src/domain/page-contracts.json` generated from registry (routes, projections, emits).

## How to Test
1. Validate registry + routing:
   - `node scripts/validate_gui_nav.js`
2. Regenerate nav artifacts (if registry changes):
   - `python scripts/build_gui_nav_registry.py`
   - `python scripts/sync_gui_nav_legacy.py`
   - `node scripts/generate_ia_manifest_from_gui_nav.js`
   - `python scripts/generate_page_contracts.py`
3. Run backend + frontend:
   - `python -m uvicorn ai_os.app.main:app --reload`
   - `npm run --prefix frontend dev`
4. Cross-page projection demo:
   - Open `/core/dashboard` and `/core/master-stack` in two tabs.
   - Trigger Run in one tab and watch the other update via projection stream.

## Notes
- Legacy `/work` remains a category home route and is allowlisted in validation.
- Legacy routes under `/legacy/*` are preserved via registry conversion.
