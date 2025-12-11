# Hybrid Desktop/Web Architecture

This document describes the architecture for the OS Dashboard AI Assistant, which runs as both a web application and a desktop application (Electron).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React/TypeScript)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Web App    │  │ Desktop App  │  │ Shared Code  │     │
│  │  (Browser)   │  │  (Electron)  │  │   (Common)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                  │            │
│         └──────────────────┼──────────────────┘            │
│                            │                               │
│              ┌─────────────┴─────────────┐                │
│              │   Platform Detection      │                │
│              │   (utils/platform.ts)     │                │
│              └─────────────┬─────────────┘                │
└────────────────────────────┼───────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
    ┌───────────▼──────────┐  ┌──────────▼──────────┐
    │   FastAPI Backend    │  │  Electron Main      │
    │   (Python)           │  │  (Node.js)          │
    └──────────────────────┘  └─────────────────────┘
```

## Directory Structure

```
os_dashboard_ai_assistant/
├── frontend/                 # React/TypeScript frontend
│   ├── src/
│   │   ├── components/      # Shared React components
│   │   ├── pages/           # Page components
│   │   ├── utils/           # Utility functions
│   │   │   └── platform.ts  # Platform detection
│   │   ├── hooks/           # React hooks
│   │   │   └── usePlatform.ts
│   │   └── api.ts           # API client (works for both)
│   ├── electron/            # Electron-specific code
│   │   ├── main.js          # Main process
│   │   ├── preload.js       # Preload script
│   │   └── icons/           # App icons
│   ├── dist/                # Web build output
│   └── dist-electron/       # Desktop build output
│
├── backend_api/             # FastAPI backend
│   ├── main.py
│   └── routers/
│
├── start_ui.py          # Unified launcher (React web + desktop)
└── scripts/
    └── build.py         # Build script (all platforms)
```

## Code Sharing Strategy

### Shared Code
- **React Components**: All UI components work in both web and desktop
- **API Client**: Single API client that works for both (uses fetch/axios)
- **Business Logic**: All business logic is shared
- **Styling**: CSS/TS styles work in both environments

### Platform-Specific Code
- **File Dialogs**: Use Electron's dialog API in desktop, HTML5 file input in web
- **System Integration**: Electron-specific features (native menus, notifications, etc.)
- **Window Management**: Electron-specific window controls

## Platform Detection

The `platform.ts` utility provides:

```typescript
const platform = usePlatform();
// Returns:
// - isElectron: boolean
// - isWeb: boolean
// - isMac/isWindows/isLinux: boolean
// - platform: string
```

## Launch Modes

### Development

```bash
# Interactive launch (asks React web vs desktop, plus build previews)
./start_ui.py

# Or directly call the frontend scripts:
cd frontend
npm run dev:web      # Web only
npm run dev:desktop  # Desktop (starts web server + Electron)
```

### Production Build

```bash
# Interactive build (asks which targets)
python scripts/build.py

# Or directly:
cd frontend
npm run build:web              # Web static files
npm run build:desktop:win      # Windows executable
npm run build:desktop:mac      # macOS app
npm run build:desktop:linux    # Linux AppImage/deb/rpm
npm run build:desktop:all      # All desktop platforms
```

## Build Targets

### Web
- **Output**: `frontend/dist/`
- **Deploy**: Static files to any web server (Nginx, Apache, CDN, etc.)
- **Requirements**: Backend API must be accessible

### Desktop - Windows
- **Output**: `frontend/dist-electron/`
- **Formats**: NSIS installer, portable executable
- **Requirements**: Build on Windows or use CI/CD

### Desktop - macOS
- **Output**: `frontend/dist-electron/`
- **Formats**: DMG, ZIP
- **Requirements**: Build on macOS or use CI/CD

### Desktop - Linux
- **Output**: `frontend/dist-electron/`
- **Formats**: AppImage, DEB, RPM
- **Requirements**: Build on Linux or use Docker

## API Communication

Both web and desktop versions communicate with the same FastAPI backend:

- **Web**: Direct HTTP/WS to backend (via proxy in dev, direct URL in prod)
- **Desktop**: HTTP/WS to localhost backend or remote backend URL

The backend can run:
1. Locally (localhost:8000)
2. On a remote server
3. Bundled with the desktop app (advanced)

## Platform-Specific Features

### Desktop (Electron)
- Native file dialogs
- System tray integration
- Native notifications
- Auto-updater support
- Menu bar integration
- Window management

### Web
- Responsive design
- Browser-based file uploads
- PWA support (can be added)
- Works on any device with a browser

## Deployment

### Web Deployment
1. Build: `npm run build:web`
2. Deploy `dist/` folder to web server
3. Configure backend API URL in environment variables
4. Set up reverse proxy for API if needed

### Desktop Deployment
1. Build for target platform: `npm run build:desktop:win/mac/linux`
2. Distribute installer/executable from `dist-electron/`
3. Users run executable (backend must be accessible)

### CI/CD Setup
See `.github/workflows/build.yml` for automated builds on:
- Push to main: Build web + all desktop platforms
- Pull requests: Build and test web version
- Tags: Create release with all platform builds

## Development Workflow

1. **Start Backend**: `cd backend_api && python main.py`
2. **Choose Mode**: Run `./start_ui.py`
3. **Develop**: Edit React code in `frontend/src/`
4. **Test**: Test in both web and desktop modes
5. **Build**: Use `python scripts/build.py` for production builds

## Future Enhancements

- [ ] PWA support for web version
- [ ] Offline mode for desktop
- [ ] Auto-updater for desktop app
- [ ] Code signing for desktop apps
- [ ] App Store distribution
- [ ] Backend bundled with desktop app option
