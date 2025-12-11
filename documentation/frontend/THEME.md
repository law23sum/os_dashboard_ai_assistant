# React Theme (Tkinter Palette)

The Tkinter cockpit defines two palettes in `assistant_hub_gui/assistant_hub/gui.py`
(`_build_color_palette`). We mirror those values in `frontend/src/theme/tokens.json`
and surface them as CSS variables (`--osd-*`) so both the browser and Electron builds
share the same look. FastAPI serves the exact bundle for `/app` and the desktop shells,
so this single source of truth keeps every surface visually consistent.

| Token | Dark | Light | Usage |
| --- | --- | --- | --- |
| `background` | `#050914` | `#f4f6fb` | Root background gradient |
| `backgroundAlt` | `#0f172a` | `#ffffff` | Secondary background / hero |
| `surface` | `#17213c` | `#ffffff` | Glass panels |
| `surfaceAlt` | `#1f2b46` | `#edf2ff` | Pills, badges |
| `border` | `#1f293b` | `#dfe3eb` | Panel borders |
| `outline` | `#334155` | `#cbd5f5` | Input outlines, grid lines |
| `text` | `#f8fafc` | `#1f2937` | Primary typography |
| `muted` | `#94a3b8` | `#64748b` | Secondary typography |
| `accent` / `accentHover` | `#6366f1` / `#7c3aed` | `#6366f1` / `#4f46e5` | Primary CTAs |
| `accentSoft` | `rgba(99,102,241,0.15)` | `rgba(99,102,241,0.12)` | Active pills, hover fills |
| `accentBlue` | `#4facfe` | `#4facfe` | Gradients, charts |
| `accentPurple` | `#9d7bff` | `#7c3aed` | Text highlights |
| `accentGreen` | `#38a3a5` | `#2fb48c` | Success badges |
| `pill` | `#1f2b46` | `#edf2ff` | Status chips |
| `glow` | `rgba(99,102,241,0.2)` | `rgba(99,102,241,0.15)` | Drop shadows |
| `nav` / `dropdown` | `rgba(5,9,20,0.85)` / `rgba(5,9,20,0.95)` | `rgba(255,255,255,0.92)` / `0.98` | Glass nav + menus |

Each token maps to a CSS custom property (`--osd-background`, `--osd-accentSoft`, etc.)
in `frontend/src/index.css`. `applyTheme` writes those vars at runtime so the user’s
selection (stored via the FastAPI settings endpoint) swaps palettes instantly.

## Component Guidelines

- **Cards/Panels**: `background: var(--osd-surface)` with `backdrop-filter: blur(18px)`
  and `border: 1px solid var(--osd-border)` mirrors the Tkinter frosted panes.
- **Buttons**: Primary buttons use the accent gradients defined in
  `theme/tokens.json.gradients.primary`. Secondary buttons reuse `--osd-surfaceAlt`.
- **Navigation**: Active pills rely on `--osd-accentSoft` + `--osd-glow` to recreate the
  Tk neon hover states.
- **Badges**: Map statuses to the accent trio (`Blue/Purple/Green`) so colors remain
  consistent across Tkinter, browser, and desktop shells.

## Tailwind Integration

Tailwind pulls values through CSS variables, so utility classes like
`bg-[color:var(--osd-surface)]` or `text-[color:var(--osd-text)]` stay in sync with the
theme tokens. When adding new tokens, record them in `theme/tokens.json`, rerun the app,
and both the Vite dev server and the packaged desktop build will immediately inherit the
Tk palette without duplicating hex values.
