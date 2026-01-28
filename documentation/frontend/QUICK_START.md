# Quick Start Guide

## 🚀 Development

```bash
cd frontend
npm install
npm run dev
```

Choose your mode:
- **1** = Web Browser (http://localhost:5173)
- **2** = Desktop App (Electron)

## 📦 Build Commands

```bash
# Web only
npm run build:web

# Desktop - All platforms
npm run build:all

# Desktop - Specific platform
npm run build:desktop:linux
npm run build:desktop:windows
npm run build:desktop:mac
```

## 🎯 Key Routes

- `/` - Dashboard
- `/mlops` - MLOps Platform
- `/personalization` - Recommendations
- `/collaboration` - Team Intelligence
- `/monitoring` - System Monitoring
- `/docs` - Preserved HTML pages

## 🔧 Environment Variables

```bash
# Skip dev launcher prompt
DEV_MODE=web npm run dev
DEV_MODE=desktop npm run dev

# Custom API URL (defaults to relative /api)
VITE_API_BASE_URL=http://localhost:8000/api npm run dev
```

## 📝 Notes

- Backend must be running on port 8000 (serving `/api/*` routes)
- Web and desktop share the same codebase
- All HTML pages preserved in `/docs`
- Platform detection via `usePlatform()` hook
