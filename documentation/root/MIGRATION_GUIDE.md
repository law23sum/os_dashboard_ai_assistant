# Migration Guide: Tkinter to React/TypeScript

This guide documents the migration from Python Tkinter GUI to a unified React/TypeScript stack that works on both web browsers and desktop applications.

## Architecture Overview

### Shared Codebase
- **Frontend**: React + TypeScript + Vite
- **Desktop**: Electron wrapper around React app
- **Web**: Direct Vite dev server / production build
- **Backend**: Python FastAPI/Flask (unchanged)

### Key Principles
1. **Single Codebase**: All UI code is shared between web and desktop
2. **Platform Detection**: Use `usePlatform()` hook to detect environment
3. **HTML Preservation**: All existing HTML pages are preserved and accessible
4. **Progressive Migration**: Migrate tabs one at a time, keeping Tkinter version until complete

## Project Structure

```
frontend/
├── src/
│   ├── pages/           # React page components (replaces Tkinter tabs)
│   ├── components/      # Shared React components
│   ├── hooks/          # Custom hooks (usePlatform, etc.)
│   ├── lib/            # API clients and utilities
│   └── utils/          # Shared utilities
├── electron/           # Electron main process files
├── scripts/           # Build and dev scripts
└── dist/              # Production builds

ui/                    # Legacy HTML pages (preserved)
docs/                  # Documentation HTML (preserved)
```

## Development Workflow

### Starting Development

```bash
cd frontend
npm install
npm run dev
```

The dev launcher will prompt you to choose:
1. **Web Browser** - Runs on http://localhost:5173
2. **Desktop App** - Launches Electron with hot reload

You can also set `DEV_MODE=web` or `DEV_MODE=desktop` environment variable to skip the prompt.

### Remembering Last Choice

The dev launcher remembers your last choice in `.dev-config.json`. Press Enter to use the last mode.

## Migration Status

### ✅ Completed
- [x] MLOps Platform tab
- [x] Personalization & Recommendations tab
- [x] Collaboration Intelligence tab
- [x] Intelligent Monitoring tab
- [x] Dashboard page
- [x] Tasks page
- [x] Projects page
- [x] Chat page
- [x] Integrations page
- [x] Analytics page
- [x] Settings page
- [x] AI Ops page
- [x] Documentation viewer (preserves HTML pages)

### 🔄 In Progress
- [ ] Complete remaining Tkinter tabs migration
- [ ] Enhanced error handling
- [ ] Offline mode support

### 📋 TODO
- [ ] Migrate all remaining Tkinter features
- [ ] Add comprehensive testing
- [ ] Performance optimization
- [ ] Accessibility improvements

## Building for Production

### Web Build
```bash
npm run build:web
```
Output: `frontend/dist/` - Deploy to any static hosting

### Desktop Builds

**Linux:**
```bash
npm run build:desktop:linux
```
Outputs: AppImage, DEB, RPM packages

**Windows:**
```bash
npm run build:desktop:windows
```
Outputs: NSIS installer, portable executable

**macOS:**
```bash
npm run build:desktop:mac
```
Outputs: DMG, ZIP

**All Platforms:**
```bash
npm run build:all
```

## Preserving HTML Pages

All existing HTML pages are preserved and accessible through the `/docs` route:

- `/docs` - Lists all available documentation
- `/docs/{page}` - Displays specific HTML page

The Docs component automatically searches for HTML files in:
- `/docs/`
- `/ui/`
- API endpoint `/api/docs/{page}`

## Platform Detection

Use the `usePlatform()` hook to detect the environment:

```typescript
import { usePlatform } from '../hooks/usePlatform'

function MyComponent() {
  const { isElectron, isWeb, platform } = usePlatform()
  
  if (isElectron) {
    // Desktop-specific code
  } else {
    // Web-specific code
  }
}
```

## API Integration

All API calls go through the shared `apiClient`:

```typescript
import apiClient, { apiPath } from '../lib/apiClient'

const response = await apiClient.post(apiPath('ai/services/mlops'), data)
```

The API client automatically handles:
- Base URL configuration
- Authentication
- Error handling
- Request/response transformation

## Component Migration Pattern

### Before (Tkinter)
```python
def _build_mlops_tab(self):
    frame = ttk.Frame(self.notebook)
    # ... Tkinter widgets
```

### After (React)
```typescript
export default function MLOps() {
  const [state, setState] = useState(...)
  // ... React components
  return <div>...</div>
}
```

## Testing

```bash
# Run tests (when implemented)
npm test

# E2E tests (when implemented)
npm run test:e2e
```

## Deployment

### Web
1. Build: `npm run build:web`
2. Deploy `dist/` folder to static hosting (Vercel, Netlify, etc.)

### Desktop
1. Build for target platform: `npm run build:desktop:{platform}`
2. Distribute installer from `dist-electron/`

## Troubleshooting

### Dev server won't start
- Check if port 5173 is available
- Try `npm run dev:web-only` directly

### Electron won't launch
- Ensure web server is running first
- Check `electron/main.cjs` configuration

### API calls failing
- Verify backend is running on port 8000
- Check `vite.config.ts` proxy settings

## Next Steps

1. Continue migrating remaining Tkinter tabs
2. Add comprehensive error boundaries
3. Implement offline mode
4. Add automated testing
5. Performance profiling and optimization

## Resources

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Electron Documentation](https://www.electronjs.org/docs)
- [Vite Guide](https://vitejs.dev/guide/)

