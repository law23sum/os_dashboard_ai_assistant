# Deployment Guide

This guide covers deploying the OS Dashboard AI Assistant for both web browser and desktop executables across Linux, Windows, and macOS.

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- For desktop builds: Electron Builder dependencies
  - macOS: Xcode Command Line Tools
  - Windows: Windows SDK (for code signing)
  - Linux: Standard build tools

## Building for Web Browser

### Development Build

```bash
cd frontend
npm install
npm run dev:web
```

This starts the Vite dev server at `http://localhost:5173` with hot reload.

### Production Build

```bash
cd frontend
npm install
npm run build:web
```

This creates optimized static files in `frontend/dist/` that can be:
- Served by FastAPI backend (mounted at `/app`)
- Deployed to static hosting (Vercel, Netlify, AWS S3, etc.)
- Served via CDN

### Deploying Web Build

#### Option 1: FastAPI Backend (Recommended)

The FastAPI backend automatically serves the built React app:

```bash
# Build the frontend
cd frontend && npm run build:web

# Start the backend (it will serve frontend/dist at /app)
python -m uvicorn assistant_hub.api.server:create_app --factory --host 0.0.0.0 --port 8000
```

#### Option 2: Static Hosting

Upload `frontend/dist/` to your static hosting provider:

- **Vercel**: `vercel deploy frontend/dist`
- **Netlify**: `netlify deploy --dir=frontend/dist`
- **AWS S3**: Use AWS CLI or console to upload `frontend/dist/`

## Building Desktop Executables

### All Platforms

```bash
cd frontend
npm install
npm run build:desktop:all
```

This builds installers for Linux, Windows, and macOS in `frontend/dist-electron/`.

### Platform-Specific Builds

#### Linux

```bash
npm run build:desktop:linux
```

Creates:
- `AppImage` (portable)
- `DEB` package (Debian/Ubuntu)
- `RPM` package (Fedora/RHEL)

#### Windows

```bash
npm run build:desktop:windows
```

Creates:
- `NSIS` installer (`.exe`)
- Portable executable (`.exe`)

#### macOS

```bash
npm run build:desktop:mac
```

Creates:
- `DMG` disk image
- `ZIP` archive

### Code Signing (Optional but Recommended)

#### macOS

1. Get an Apple Developer certificate
2. Update `electron-builder.yml` with your certificate details:

```yaml
mac:
  identity: "Developer ID Application: Your Name"
  hardenedRuntime: true
  gatekeeperAssess: false
```

3. Build with signing:
```bash
CSC_LINK=/path/to/certificate.p12 CSC_KEY_PASSWORD=password npm run build:desktop:mac
```

#### Windows

1. Get a code signing certificate
2. Update `electron-builder.yml`:

```yaml
win:
  certificateFile: /path/to/certificate.pfx
  certificatePassword: password
```

3. Build with signing:
```bash
CSC_LINK=/path/to/certificate.pfx CSC_KEY_PASSWORD=password npm run build:desktop:windows
```

## Single Entry Point

The project uses a single entry point (`run.py`) that prompts for mode selection:

```bash
python run.py
```

Options:
1. React · Web Dev (FastAPI + Vite)
2. React · Desktop Dev (FastAPI + Electron)
3. Serve Web Build (FastAPI + `frontend/dist/`)
4. Serve Desktop Build (pywebview shell)

### Skip Prompt (for CI/CD)

Set environment variable:

```bash
OSDASH_UI_MODE=web python run.py
# or
DEV_MODE=desktop python run.py
```

Or use CLI flag:

```bash
python run.py --mode web
python run.py --mode desktop
python run.py --mode web-build
python run.py --mode desktop-build
```

## Shared Code Structure

Code is shared between desktop and web through:

- `frontend/src/shared/` - Shared utilities
- `frontend/src/lib/apiClient.ts` - Unified API client
- `frontend/src/theme/` - Shared theme system
- `frontend/src/components/` - Shared React components

Both Electron and browser builds use the same React bundle, ensuring feature parity.

## Deployment Checklist

### Web Deployment

- [ ] Run `npm run build:web`
- [ ] Test production build locally (`npm run preview`)
- [ ] Configure backend API URL in environment variables
- [ ] Deploy `frontend/dist/` to hosting provider
- [ ] Configure CORS if needed
- [ ] Set up SSL certificate
- [ ] Test all routes and API endpoints

### Desktop Deployment

- [ ] Run `npm run build:desktop:all` or platform-specific build
- [ ] Test installer on target platform
- [ ] Code sign executables (recommended)
- [ ] Test auto-update mechanism (if configured)
- [ ] Create release notes
- [ ] Upload to distribution platform (GitHub Releases, etc.)

### Cross-Platform Testing

- [ ] Test on Linux (Ubuntu/Debian)
- [ ] Test on Windows 10/11
- [ ] Test on macOS (Intel and Apple Silicon)
- [ ] Verify theme consistency across platforms
- [ ] Test API connectivity
- [ ] Verify file system access (desktop only)

## Environment Variables

### Development

```bash
# Backend API URL (default: http://localhost:8000)
VITE_API_BASE_URL=http://localhost:8000

# UI Mode (web, desktop, web-build, desktop-build)
OSDASH_UI_MODE=web
```

### Production

```bash
# Backend API URL
VITE_API_BASE_URL=https://api.yourdomain.com

# Enable production optimizations
NODE_ENV=production
```

## Troubleshooting

### Build Failures

- Ensure Node.js 18+ is installed
- Clear `node_modules` and reinstall: `rm -rf node_modules package-lock.json && npm install`
- Check Electron Builder logs in `frontend/dist-electron/`

### Runtime Issues

- Check browser console (web) or Electron DevTools (desktop)
- Verify API connectivity
- Check CORS settings if API is on different domain
- Review FastAPI logs for backend errors

### Platform-Specific Issues

#### macOS
- May need to allow unsigned app in System Preferences > Security
- Gatekeeper may block unsigned apps

#### Windows
- Antivirus may flag unsigned executables
- May need to run as administrator for certain operations

#### Linux
- May need to install dependencies: `sudo apt-get install libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2`
- AppImage may need execute permission: `chmod +x AppImage`

## Additional Resources

- [Electron Builder Documentation](https://www.electron.build/)
- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html)
- [FastAPI Static Files](https://fastapi.tiangolo.com/tutorial/static-files/)

