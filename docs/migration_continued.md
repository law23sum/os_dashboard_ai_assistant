# Migration Continued: Tkinter to React/TypeScript

This document tracks the continued migration from Python Tkinter-only features to React/TypeScript/JavaScript/CSS/HTML5, ensuring the display can be accessed from both desktop and web browser with shared code.

## Completed Tasks

### ✅ Theme System Enhancement

- **Extracted exact Tkinter color palette** from `assistant_hub_gui/assistant_hub/gui.py`
- **Created comprehensive theme system** with:
  - CSS variables matching Tkinter colors exactly
  - Tailwind integration with `osd-*` color tokens
  - Dark and light theme support
  - Semantic colors (success, error, warning, info)

**Files Updated:**
- `frontend/src/theme/colors.ts` - Exact Tkinter color values
- `frontend/src/index.css` - CSS variables with Tkinter colors
- `frontend/tailwind.config.js` - Tailwind theme integration
- `frontend/electron/main.cjs` - Electron window background color

### ✅ HTML Pages Migration

- **Created Documentation component** to display HTML pages from `docs/` directory
- **Added routes** for all HTML pages:
  - `/docs/index.html`
  - `/docs/dashboard.html`
  - `/docs/projects.html`
  - `/docs/settings.html`
  - `/docs/billing.html`
  - `/docs/ai_capabilities.html`
  - Future pages (future_meta, future_god, etc.)

**Files Created:**
- `frontend/src/pages/Documentation.tsx` - Component to render HTML pages
- Updated `frontend/src/App.tsx` - Added routes for HTML pages

**Files Updated:**
- `frontend/src/pages/Docs.tsx` - Enhanced to list and display HTML pages

### ✅ Single Entry Point Enhancement

- **Enhanced `start_ui.py`** to properly prompt for desktop vs web mode
- **Improved prompt clarity** with better descriptions
- **Maintained backward compatibility** with environment variables and CLI flags

**Files Updated:**
- `start_ui.py` - Enhanced prompt with clearer descriptions

### ✅ Deployment Configurations

- **Created comprehensive deployment guide** (`frontend/DEPLOYMENT.md`)
- **Configured Electron Builder** for all platforms:
  - Linux: AppImage, DEB, RPM
  - Windows: NSIS installer, portable executable
  - macOS: DMG, ZIP
- **Set up code signing** instructions for macOS and Windows

**Files Created:**
- `frontend/DEPLOYMENT.md` - Complete deployment guide

**Files Updated:**
- `frontend/electron-builder.yml` - Already configured for all platforms

### ✅ Shared Code Structure

- **Created shared utilities** (`frontend/src/shared/utils.ts`)
- **Platform detection utilities** for desktop vs web
- **Common functions** used by both platforms:
  - Date formatting
  - Debounce/throttle
  - Clipboard operations
  - JSON parsing

**Files Created:**
- `frontend/src/shared/utils.ts` - Shared utilities between desktop and web

### ✅ Project Ledger & Spec Alignment

- **Crafted the `ProjectLedgerPanel`** in React so the Tkinter ledger view and the new unified front end read from the same `/api/projects/ledger` feed, automatically filtering per project and surfacing the hash chain.
- **Captured spec alignment** by calling out `Technical Spec Sheet (Version 6 Latest Version).pdf` sections §3.7, §6.3, §8.7 directly in the UI, showing integrity status, and linking to the doc for auditors.
- **Expanded the type system** with `ProjectLedgerEvent` and added the ledger filter + refresh flow so desktop and browser both rely on the same contract.

**Files Updated:**
- `frontend/src/pages/Projects.tsx` – ledger UI + ledger filtering logic
- `frontend/src/types/index.ts` – ledger event shape

## Theme Colors (Tkinter-Inspired)

### Dark Theme
```typescript
background: '#050914'      // Deep navy background
surface: '#0f172a'          // Primary surface (cards, panels)
surfaceAlt: '#17213c'       // Secondary surface (alternate cards)
border: '#1f293b'           // Borders and dividers
text: '#f8fafc'             // Primary text (light)
muted: '#94a3b8'            // Secondary text, placeholders
accent: '#6366f1'           // Primary accent (indigo)
accentHover: '#7c3aed'      // Accent hover state (purple)
pill: '#1f2b46'             // Pill/badge background
```

### Light Theme
```typescript
background: '#f4f6fb'       // Light background
surface: '#ffffff'           // White surface
surfaceAlt: '#f7f9fd'        // Light alternate surface
border: '#dfe3eb'           // Light border
text: '#1f2937'              // Dark text
muted: '#64748b'            // Muted text
accent: '#6366f1'            // Indigo accent
accentHover: '#4f46e5'      // Darker indigo on hover
pill: '#edf2ff'             // Light pill background
```

## Architecture

### Single Entry Point
```
run.py
  └── start_ui.py (prompts for mode)
      ├── web (React + Vite dev server)
      ├── desktop (React + Electron)
      ├── web-build (FastAPI + built React)
      └── desktop-build (pywebview + built React)
```

### Shared Code Structure
```
frontend/src/
  ├── shared/          # Shared utilities (desktop + web)
  ├── lib/             # Shared API client
  ├── theme/           # Shared theme system
  ├── components/      # Shared React components
  └── pages/           # Page components (shared)
```

### Build Outputs
```
frontend/
  ├── dist/            # Web build (static files)
  └── dist-electron/   # Desktop builds
      ├── linux/       # AppImage, DEB, RPM
      ├── win/         # NSIS, portable
      └── mac/          # DMG, ZIP
```

## Remaining Tasks

### 🔄 In Progress

1. **Project Intelligence & TRF Surface (Spec §4.5–§4.8)**
   - Rebuild the energy cards, risk heuristics, and TRF trace viewer so the React surface can expose the same reasoning insights the Tkinter console referenced.
   - Tie the FastAPI backend (and the `Technical Spec Sheet` definitions) into the new UI to show project health, persona status, and TRF inference logs.

2. **Driver Scheduling Instrumentation (Spec §5.12 / §12.5)**
   - Surface queue / throttle / admission control metrics inside the AIOps panel with the same guardrail semantics described in the spec.
   - Feed those metrics through the API so both Electron and browser builds show consistent backpressure controls.

3. **Collaboration & Federation Primitives (Spec §7.12)**
   - Extend the shared ledger, project memberships, and role-aware filters so multi-user state, shared annotations, and regulator-friendly views are available in both user experiences.
   - Ensure `TECH_SPEC_GAP_LOG.md` entries for multi-tenant federation are noted and resumed once foundational APIs exist.

### 📋 Pending

1. **Evidence Pack / Audit Export**
   - Automate generating ledger-backed evidence packs (Spec §8.17 / §11.6) that bundle artifacts for regulators, then preview them in the React panel before producing PDF/ZIP outputs.

2. **Project Intelligence Documentation & Migration Guide**
   - Document how the React/Tk surfaces reuse the canonical spec, including sample flows from `OS DashboardAIAssistantTOC.txt` and the Technical Spec PDF, so new contributors can trace features back to requirements.

3. **Cross-Platform Verification**
   - Continue exercising the integration flow across Linux, Windows, and macOS builds, ensuring the shared code path (React + FastAPI) behaves identically whether surfaced via Electron or a browser tab.

## Usage

### Development

```bash
# Single entry point (prompts for mode)
python run.py

# Or specify mode directly
python run.py --mode web
python run.py --mode desktop
```

### Production Builds

```bash
# Web build
cd frontend && npm run build:web

# Desktop builds
cd frontend && npm run build:desktop:all
# Or platform-specific:
npm run build:desktop:linux
npm run build:desktop:windows
npm run build:desktop:mac
```

## Key Features

✅ **Single Codebase** - React components shared between desktop and web  
✅ **Tkinter Theme** - Exact color matching with Tkinter GUI  
✅ **HTML Pages Preserved** - All docs/ HTML pages accessible  
✅ **Single Entry Point** - Unified launcher with mode selection  
✅ **Cross-Platform** - Linux, Windows, macOS support  
✅ **Deployment Ready** - Configurations for web and desktop  

## Notes

- The theme system ensures visual consistency between Tkinter and React surfaces
- All HTML pages from `docs/` are preserved and accessible via React routes
- Shared utilities eliminate code duplication between desktop and web
- Electron and browser builds use the same React bundle for feature parity

