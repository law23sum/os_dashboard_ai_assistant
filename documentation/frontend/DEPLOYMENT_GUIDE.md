# Deployment Guide

## Overview

This guide covers deploying the OS Dashboard AI Assistant for both web browsers and desktop applications across all major operating systems.

## Prerequisites

- Node.js 16+ and npm
- Python 3.8+ (for backend)
- Backend server running on port 8000

## Development Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development

```bash
npm run dev
```

Choose your mode:
- **1** = Web Browser (http://localhost:5173)
- **2** = Desktop App (Electron)

Or use environment variables:
```bash
DEV_MODE=web npm run dev      # Web only
DEV_MODE=desktop npm run dev  # Desktop only
```

## Production Builds

### Web Deployment

**Build:**
```bash
npm run build:web
```

**Output:** `frontend/dist/` directory

**Deploy to:**
- Vercel: `vercel --prod`
- Netlify: `netlify deploy --prod`
- Any static hosting service

**Requirements:**
- Backend API must be accessible
- Set `VITE_API_BASE_URL` environment variable if backend is on different domain
- Configure CORS on backend to allow your domain

### Desktop App Deployment

#### Linux

**Build:**
```bash
npm run build:desktop:linux
```

**Outputs in `dist-electron/`:**
- `OS Dashboard AI Assistant-*.AppImage` - Portable app
- `OS Dashboard AI Assistant_*.deb` - Debian/Ubuntu package
- `OS Dashboard AI Assistant-*.rpm` - Red Hat/Fedora package

**Distribution:**
- AppImage: Make executable and distribute
- DEB: `sudo dpkg -i *.deb`
- RPM: `sudo rpm -i *.rpm`

#### Windows

**Build:**
```bash
npm run build:desktop:windows
```

**Outputs in `dist-electron/`:**
- `OS Dashboard AI Assistant Setup *.exe` - NSIS installer
- `OS Dashboard AI Assistant-*.exe` - Portable executable

**Distribution:**
- Installer: Run Setup.exe for installation
- Portable: Run executable directly (no installation)

#### macOS

**Build:**
```bash
npm run build:desktop:mac
```

**Outputs in `dist-electron/`:**
- `OS Dashboard AI Assistant-*.dmg` - Disk image
- `OS Dashboard AI Assistant-*.zip` - Archive

**Distribution:**
- DMG: Mount and drag to Applications
- ZIP: Extract and move to Applications

**Note:** macOS builds require code signing for distribution outside App Store. See [Code Signing](#code-signing) section.

#### All Platforms

**Build everything:**
```bash
npm run build:all
```

This creates installers for all platforms in `dist-electron/`.

## Code Signing (Optional but Recommended)

### macOS

1. Get Apple Developer certificate
2. Update `electron-builder.yml`:
```yaml
mac:
  identity: "Developer ID Application: Your Name"
```

### Windows

1. Get code signing certificate
2. Update `electron-builder.yml`:
```yaml
win:
  certificateFile: "path/to/certificate.pfx"
  certificatePassword: "password"
```

### Linux

Code signing not typically required for Linux distributions.

## Environment Configuration

### Development

Create `.env.local`:
```env
VITE_API_BASE_URL=http://localhost:8000
DEV_MODE=web
```

### Production

Set environment variables in your deployment platform:
- `VITE_API_BASE_URL` - Backend API URL
- `NODE_ENV=production`

## Backend Requirements

The frontend requires a backend API running. Ensure:

1. **Backend is running:**
   ```bash
   uvicorn ai_os.app.main:app --reload
   ```

2. **CORS is configured** to allow your frontend domain

3. **API endpoints are available:**
   - `/api/dashboard/stats`
   - `/api/tasks/`
   - `/api/projects/`
   - `/api/settings`
   - And other endpoints as needed

## Troubleshooting

### Build Fails

1. **Clear cache:**
   ```bash
   rm -rf node_modules dist dist-electron
   npm install
   ```

2. **Check Node version:**
   ```bash
   node --version  # Should be 16+
   ```

3. **Check Electron version:**
   ```bash
   npm list electron
   ```

### Desktop App Won't Launch

1. Check Electron logs in console
2. Verify `dist/index.html` exists
3. Check that backend is accessible
4. Review `electron/main.cjs` for errors

### Web Build Not Working

1. Check browser console for errors
2. Verify API base URL is correct
3. Check CORS settings on backend
4. Verify all assets are loading

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && npm install
      - run: cd frontend && npm run build:web
      - run: cd frontend && npm run build:all
      - uses: actions/upload-artifact@v3
        with:
          name: dist
          path: frontend/dist-electron/
```

## Distribution

### Web
- Deploy `dist/` to static hosting
- Configure environment variables
- Set up API proxy if needed

### Desktop
- Upload installers to release page
- Provide download links
- Include installation instructions
- Consider auto-update mechanism

## Security Considerations

1. **API Keys:** Never commit API keys to repository
2. **Environment Variables:** Use `.env` files (not committed)
3. **Code Signing:** Sign desktop apps for trust
4. **HTTPS:** Use HTTPS for production web deployments
5. **CORS:** Configure CORS properly on backend

## Performance Optimization

1. **Bundle Size:** Already optimized with code splitting
2. **Lazy Loading:** Routes are code-split automatically
3. **Caching:** Configure appropriate cache headers
4. **CDN:** Use CDN for static assets in production

## Support

For issues:
1. Check `TROUBLESHOOTING.md`
2. Review browser/Electron console logs
3. Verify backend is running and accessible
4. Check network tab for failed requests

