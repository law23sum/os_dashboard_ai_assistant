# OS Dashboard AI Assistant - Deployment Guide

## Overview

This guide covers deployment strategies for both web and desktop versions of the OS Dashboard AI Assistant across all major operating systems.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Web Deployment](#web-deployment)
3. [Desktop Deployment](#desktop-deployment)
4. [Build Scripts](#build-scripts)
5. [Platform-Specific Notes](#platform-specific-notes)
6. [CI/CD Integration](#cicd-integration)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Development Environment

- **Node.js**: 18.x or higher
- **npm**: 9.x or higher
- **Python**: 3.9 or higher
- **Git**: Latest version

### Platform-Specific Requirements

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get install build-essential libssl-dev

# Fedora/RHEL
sudo dnf install gcc gcc-c++ make openssl-devel
```

#### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Windows
- Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/)
- Install [Python for Windows](https://www.python.org/downloads/windows/)
- Install [Node.js for Windows](https://nodejs.org/en/download/)

## Web Deployment

### Development Server

```bash
# Start development server
python run.py --mode web

# Or directly with npm
cd frontend
npm run dev:web
```

The development server runs on `http://localhost:5173` with hot module replacement (HMR).

### Production Build

```bash
# Build for production
cd frontend
npm run build:web

# Output: frontend/dist/
```

### Deployment Targets

#### Static Hosting (Vercel, Netlify, etc.)

1. **Build the app**:
   ```bash
   cd frontend && npm run build:web
   ```

2. **Configure deployment**:
   - **Root directory**: `frontend`
   - **Build command**: `npm run build:web`
   - **Output directory**: `dist`
   - **Install command**: `npm install`

3. **Environment variables**:
   ```env
   VITE_API_URL=https://your-api-domain.com
   VITE_APP_ENV=production
   ```

#### Docker Deployment

```dockerfile
# Dockerfile for web deployment
FROM node:18-alpine AS builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build:web

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run:
```bash
docker build -t os-dashboard-web .
docker run -p 80:80 os-dashboard-web
```

#### AWS S3 + CloudFront

```bash
# Build
cd frontend && npm run build:web

# Upload to S3
aws s3 sync dist/ s3://your-bucket-name/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

## Desktop Deployment

### Build All Platforms

```bash
# Use the unified build script
./build-all-platforms.sh all

# Or build specific platforms
./build-all-platforms.sh linux
./build-all-platforms.sh windows
./build-all-platforms.sh mac
```

### Platform-Specific Builds

#### Linux

```bash
cd frontend
npm run build:desktop:linux
```

**Output formats**:
- AppImage: `dist-electron/*.AppImage`
- DEB: `dist-electron/*.deb`
- RPM: `dist-electron/*.rpm`

**Installation**:
```bash
# AppImage
chmod +x OS-Dashboard-*.AppImage
./OS-Dashboard-*.AppImage

# DEB
sudo dpkg -i os-dashboard_*.deb

# RPM
sudo rpm -i os-dashboard-*.rpm
```

#### Windows

```bash
cd frontend
npm run build:desktop:windows
```

**Output formats**:
- NSIS Installer: `dist-electron/*-Setup.exe`
- Portable: `dist-electron/*-Portable.exe`

**Installation**:
- Run the Setup.exe installer
- Or extract and run the portable version

#### macOS

```bash
cd frontend
npm run build:desktop:mac
```

**Output formats**:
- DMG: `dist-electron/*.dmg`
- ZIP: `dist-electron/*.zip`

**Installation**:
```bash
# Mount DMG and drag to Applications
open OS-Dashboard-*.dmg

# Or extract ZIP
unzip OS-Dashboard-*.zip
mv "OS Dashboard.app" /Applications/
```

**Code Signing** (for distribution):
```bash
# Sign the app
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" "OS Dashboard.app"

# Notarize with Apple
xcrun notarytool submit OS-Dashboard-*.dmg --keychain-profile "AC_PASSWORD"
```

## Build Scripts

### Unified Build Script

The `build-all-platforms.sh` script provides a comprehensive build system:

```bash
# Build everything
./build-all-platforms.sh all

# Build specific target
./build-all-platforms.sh [web|desktop|linux|windows|mac|backend]
```

**Features**:
- ✅ Dependency checking
- ✅ Multi-platform support
- ✅ Automatic archiving
- ✅ Build manifest generation
- ✅ Error handling

### Custom Build Configuration

Edit `frontend/electron-builder.yml` to customize build settings:

```yaml
appId: com.osdashboard.app
productName: OS Dashboard AI Assistant
directories:
  output: dist-electron
files:
  - dist/**/*
  - electron/**/*
mac:
  category: public.app-category.developer-tools
  target:
    - dmg
    - zip
win:
  target:
    - nsis
    - portable
linux:
  target:
    - AppImage
    - deb
    - rpm
  category: Development
```

## Platform-Specific Notes

### Linux

**Desktop Integration**:
```bash
# Create desktop entry
cat > ~/.local/share/applications/os-dashboard.desktop << EOF
[Desktop Entry]
Name=OS Dashboard AI Assistant
Exec=/path/to/os-dashboard
Icon=/path/to/icon.png
Type=Application
Categories=Development;Utility;
EOF
```

**Auto-start**:
```bash
cp ~/.local/share/applications/os-dashboard.desktop ~/.config/autostart/
```

### Windows

**Registry Settings**:
```powershell
# Add to startup (PowerShell)
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\OS Dashboard.lnk")
$Shortcut.TargetPath = "C:\Program Files\OS Dashboard\OS Dashboard.exe"
$Shortcut.Save()
```

**Firewall Rules**:
```powershell
# Allow through Windows Firewall
New-NetFirewallRule -DisplayName "OS Dashboard" -Direction Inbound -Program "C:\Program Files\OS Dashboard\OS Dashboard.exe" -Action Allow
```

### macOS

**Gatekeeper**:
```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine "/Applications/OS Dashboard.app"
```

**Launch Agent**:
```xml
<!-- ~/Library/LaunchAgents/com.osdashboard.app.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.osdashboard.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Applications/OS Dashboard.app/Contents/MacOS/OS Dashboard</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/build.yml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Build
        run: |
          cd frontend
          npm run build:desktop
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.os }}-build
          path: frontend/dist-electron/*
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - build
  - deploy

build:web:
  stage: build
  image: node:18
  script:
    - cd frontend
    - npm ci
    - npm run build:web
  artifacts:
    paths:
      - frontend/dist/

build:desktop:
  stage: build
  parallel:
    matrix:
      - PLATFORM: [linux, windows, mac]
  script:
    - cd frontend
    - npm ci
    - npm run build:desktop:$PLATFORM
  artifacts:
    paths:
      - frontend/dist-electron/
```

## Troubleshooting

### Common Issues

#### Build Failures

**Problem**: `npm run build` fails with memory error
```bash
# Solution: Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

**Problem**: Electron build fails on Linux
```bash
# Solution: Install missing dependencies
sudo apt-get install libgtk-3-0 libnotify4 libnss3 libxss1 libxtst6 xdg-utils
```

#### Runtime Issues

**Problem**: App won't start on macOS
```bash
# Solution: Check for quarantine attribute
xattr -d com.apple.quarantine "/Applications/OS Dashboard.app"
```

**Problem**: White screen on startup
```bash
# Solution: Clear application cache
# Linux: rm -rf ~/.config/os-dashboard/
# macOS: rm -rf ~/Library/Application\ Support/os-dashboard/
# Windows: del /s /q %APPDATA%\os-dashboard\
```

### Debug Mode

Enable debug logging:

```bash
# Set environment variable
export DEBUG=os-dashboard:*

# Or in Electron
export ELECTRON_ENABLE_LOGGING=1
```

### Performance Optimization

**Web**:
- Enable gzip compression on server
- Use CDN for static assets
- Implement service worker for caching

**Desktop**:
- Reduce bundle size with code splitting
- Use native modules where possible
- Implement lazy loading for heavy components

## Security Considerations

### Web Deployment

- Use HTTPS only
- Implement Content Security Policy (CSP)
- Enable CORS restrictions
- Use environment variables for secrets
- Implement rate limiting

### Desktop Deployment

- Code sign all executables
- Implement auto-updates securely
- Validate all external resources
- Use secure IPC communication
- Implement application sandboxing

## Monitoring & Analytics

### Web

```javascript
// Add analytics tracking
import { analytics } from './lib/analytics'

analytics.track('page_view', {
  page: window.location.pathname
})
```

### Desktop

```javascript
// Electron crash reporting
const { crashReporter } = require('electron')

crashReporter.start({
  productName: 'OS Dashboard',
  companyName: 'Your Company',
  submitURL: 'https://your-crash-server.com/submit',
  uploadToServer: true
})
```

## Support

For deployment issues:
- Check [GitHub Issues](https://github.com/your-repo/issues)
- Review [Documentation](./README.md)
- Contact support team

## License

See [LICENSE](./LICENSE) file for details.

