# OS Dashboard AI Assistant - Theme Guide

## Overview

The React/TypeScript frontend uses a **Tkinter-inspired glass theme** that maintains visual consistency with the legacy Python GUI while providing a modern, polished experience across web browsers and desktop applications.

## Design Philosophy

### Glass Morphism + Neon Accents
- **Frosted glass panels** with backdrop blur for depth
- **Subtle gradients** and soft glows for visual interest
- **Neon accent colors** inspired by the Tkinter ttkbootstrap theme
- **Dark-first design** optimized for extended use

### Color Palette

All colors are defined as CSS custom properties in `frontend/src/index.css` and can be accessed via `var(--osd-*)`.

#### Dark Theme (Default)
| Token | Hex | Usage |
|-------|-----|-------|
| `--osd-background` | `#050914` | App root background |
| `--osd-backgroundAlt` | `#0f172a` | Secondary backgrounds |
| `--osd-surface` | `#17213c` | Card/panel surfaces |
| `--osd-surfaceAlt` | `#1f2b46` | Alternate surfaces |
| `--osd-border` | `#1f293b` | Borders and dividers |
| `--osd-outline` | `#334155` | Input outlines |
| `--osd-text` | `#f8fafc` | Primary text |
| `--osd-muted` | `#94a3b8` | Secondary text, placeholders |
| `--osd-accent` | `#6366f1` | Primary accent (indigo) |
| `--osd-accentHover` | `#7c3aed` | Hover state (purple) |
| `--osd-accentBlue` | `#4facfe` | Blue accent |
| `--osd-accentGreen` | `#38a3a5` | Green accent (success) |
| `--osd-accentPurple` | `#9d7bff` | Purple accent |
| `--osd-pill` | `#1f2b46` | Badge/pill background |
| `--osd-glow` | `rgba(99, 102, 241, 0.2)` | Glow effects |

#### Light Theme
| Token | Hex | Usage |
|-------|-----|-------|
| `--osd-background` | `#f4f6fb` | App root background |
| `--osd-backgroundAlt` | `#ffffff` | Secondary backgrounds |
| `--osd-surface` | `#ffffff` | Card/panel surfaces |
| `--osd-surfaceAlt` | `#f7f9fd` | Alternate surfaces |
| `--osd-border` | `#dfe3eb` | Borders and dividers |
| `--osd-text` | `#1f2937` | Primary text |
| `--osd-muted` | `#64748b` | Secondary text |
| `--osd-accent` | `#6366f1` | Primary accent |
| `--osd-pill` | `#edf2ff` | Badge/pill background |

#### Semantic Colors (Both Themes)
| Token | Hex | Usage |
|-------|-----|-------|
| `--osd-success` | `#10b981` | Success states, completed tasks |
| `--osd-error` | `#ef4444` | Error states, failed operations |
| `--osd-warning` | `#f59e0b` | Warning states, pending items |
| `--osd-info` | `#3b82f6` | Informational states |

## Component Styling

### Navigation
```css
.osd-nav {
  background: var(--osd-nav);
  backdrop-filter: blur(16px);
}

.osd-nav-link {
  /* Pill-shaped nav items */
  border-radius: 999px;
  color: var(--osd-muted);
  transition: all 0.2s ease;
}

.osd-nav-link--active {
  color: var(--osd-text);
  background: var(--osd-accentSoft);
  box-shadow: 0 0 20px var(--osd-glow);
}
```

### Cards & Panels
```css
.glass-panel {
  background: radial-gradient(circle at top, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid var(--osd-border);
  border-radius: 20px;
  box-shadow: 0 30px 60px rgba(2, 6, 23, 0.45);
  backdrop-filter: blur(18px);
}
```

### Buttons
```css
.cv-btn-primary {
  background: linear-gradient(120deg, #6366f1, #8b5cf6);
  color: white;
  box-shadow: 0 15px 30px rgba(99, 102, 241, 0.35);
}

.cv-btn-ghost {
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: var(--osd-text);
}
```

### Pills & Badges
```css
.pill {
  background: var(--osd-pill);
  border-radius: 999px;
  padding: 0.2rem 0.85rem;
  font-size: 0.75rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
```

## Typography

### Font Stack
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### Hierarchy
- **Page Title**: 2xl (1.5rem), font-bold
- **Section Header**: lg (1.125rem), font-medium
- **Body Text**: base (1rem), font-normal
- **Small Text**: sm (0.875rem), font-normal
- **Micro Text**: xs (0.75rem), font-medium

### Special Text Styles
```css
.glass-gradient-text {
  background: linear-gradient(120deg, var(--osd-accentPurple), var(--osd-accent), var(--osd-accentBlue));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.eyebrow-text {
  letter-spacing: 0.45em;
  text-transform: uppercase;
  font-size: 0.68rem;
  color: rgba(255, 255, 255, 0.6);
}
```

## Layout Patterns

### Dashboard Grid
```tsx
<div className="glass-grid glass-grid--two">
  <div className="glass-panel">
    {/* Content */}
  </div>
</div>
```

### Metric Display
```tsx
<div className="glass-metric">
  <span className="glass-metric__label">Tasks Completed</span>
  <span className="glass-metric__value">42</span>
</div>
```

## Responsive Design

### Breakpoints (Tailwind)
- **sm**: 640px
- **md**: 768px
- **lg**: 1024px
- **xl**: 1280px
- **2xl**: 1536px

### Mobile Considerations
- Navigation collapses to hamburger menu on small screens
- Grid layouts stack vertically on mobile
- Touch targets are minimum 44x44px
- Dropdowns convert to bottom sheets on mobile

## Theme Switching

The theme can be switched programmatically:

```typescript
import { applyTheme, lightTheme, darkTheme } from './theme'

// Apply dark theme (default)
applyTheme(darkTheme)

// Apply light theme
applyTheme(lightTheme)
```

Theme preference is stored in:
- **Web**: localStorage
- **Desktop**: Application settings file

## Accessibility

### Contrast Ratios
- **Normal text**: 4.5:1 minimum (WCAG AA)
- **Large text**: 3:1 minimum (WCAG AA)
- **Interactive elements**: 3:1 minimum

### Focus States
All interactive elements have visible focus indicators:
```css
.focus\:ring-primary-500:focus {
  --tw-ring-color: var(--osd-accent);
  outline: 2px solid var(--osd-accent);
  outline-offset: 2px;
}
```

### Screen Reader Support
- Semantic HTML5 elements
- ARIA labels where needed
- Skip navigation links
- Keyboard navigation support

## Animation & Transitions

### Standard Timing
```css
transition: all 0.2s ease;
```

### Hover Effects
```css
.sample-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.2);
}
```

### Loading States
```tsx
<div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
```

## Platform-Specific Considerations

### Web Browser
- Uses Vite dev server in development
- Served from FastAPI in production
- Supports all modern browsers (Chrome, Firefox, Safari, Edge)
- Progressive Web App (PWA) ready

### Desktop (Electron)
- Native window controls
- File system access
- System tray integration
- Auto-updates support
- Platform-specific styling (macOS, Windows, Linux)

### Desktop (PyWebView)
- Lightweight alternative to Electron
- Uses system WebView
- Smaller bundle size
- Limited to Python backend integration

## Best Practices

### Do's ✅
- Use CSS custom properties for colors
- Follow the established component patterns
- Maintain consistent spacing (multiples of 4px)
- Use semantic HTML elements
- Test on both light and dark themes
- Ensure keyboard accessibility

### Don'ts ❌
- Don't hardcode color values
- Don't use inline styles (use Tailwind utilities)
- Don't create new color tokens without documentation
- Don't break the glass aesthetic
- Don't forget mobile responsiveness
- Don't skip accessibility testing

## Migration from Tkinter

When migrating features from the Tkinter GUI:

1. **Colors**: Map Tkinter colors to CSS custom properties
2. **Layout**: Convert grid/pack layouts to Flexbox/Grid
3. **Widgets**: Use React components instead of Tk widgets
4. **State**: Use React hooks instead of Tk variables
5. **Events**: Use React event handlers instead of Tk bindings

### Tkinter → React Component Mapping

| Tkinter Widget | React Equivalent |
|----------------|------------------|
| `tk.Label` | `<span>` or `<p>` |
| `tk.Button` | `<button>` with Tailwind classes |
| `tk.Entry` | `<input>` |
| `tk.Text` | `<textarea>` |
| `tk.Frame` | `<div>` |
| `ttk.Notebook` | React Router + Layout |
| `tk.Listbox` | `<ul>` + `<li>` or custom component |
| `ttk.Treeview` | Custom tree component |
| `tk.Canvas` | `<canvas>` or SVG |

## Resources

- **Tailwind CSS**: https://tailwindcss.com/docs
- **Lucide Icons**: https://lucide.dev/
- **React Query**: https://tanstack.com/query/latest
- **React Router**: https://reactrouter.com/

## Maintenance

### Adding New Colors
1. Define in `:root` and `[data-theme='light']` in `index.css`
2. Document in this guide
3. Update `colors.ts` if needed
4. Test in both themes

### Updating Components
1. Maintain glass aesthetic
2. Test responsiveness
3. Verify accessibility
4. Update documentation

### Theme Versioning
Current version: **v1.0.0**

Breaking changes require major version bump.

