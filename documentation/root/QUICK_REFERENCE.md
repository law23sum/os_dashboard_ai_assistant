# Quick Reference Guide

## 🚀 Launch Commands

### Development
```bash
# Interactive mode selection
python run.py

# Web development (browser + hot reload)
python run.py --mode web

# Desktop development (Electron + hot reload)
python run.py --mode desktop

# Legacy Tkinter GUI
python run.py --legacy
```

### Production
```bash
# Serve web build
python run.py --mode web-build

# Serve desktop build
python run.py --mode desktop-build
```

## 🏗️ Build Commands

### Web
```bash
./scripts/build_web.sh
# Output: frontend/dist/
```

### Desktop
```bash
./scripts/build_desktop.sh
# Output: frontend/dist-electron/
```

### All Targets
```bash
./scripts/build_all.sh
```

## 📂 Key Directories

```
frontend/src/
├── pages/          # 27 React page components
├── components/     # Shared UI components
├── hooks/          # Custom React hooks
├── lib/            # API client
├── theme/          # Tkinter-inspired theme
└── utils/          # Utilities

assistant_hub/api/
└── server.py       # FastAPI backend with all routes

scripts/
├── build_web.sh    # Build for web
├── build_desktop.sh # Build for desktop
└── build_all.sh    # Build everything
```

## 🎨 Theme Colors

```css
--tk-bg-darker: #020617;
--tk-bg-dark: #1b1b1f;
--tk-accent-blue: #4facfe;
--tk-accent-purple: #667eea;
--tk-accent-green: #38a3a5;
```

## 🔌 API Endpoints

### Core
- `GET /health` - Health check
- `GET /system` - System stats
- `GET /settings` - User settings
- `PUT /settings` - Update settings

### Data
- `GET /tasks` - List tasks
- `POST /tasks` - Create task
- `GET /projects` - List projects
- `POST /projects` - Create project

### AI
- `POST /ai/ask` - Chat with AI
- `POST /intelligence/nas` - Neural Architecture Search
- `POST /security/threats` - Security Threat Detection
- `POST /edge/operations` - Edge Computing
- `POST /workflows/orchestrate` - Workflow Orchestration

### Workspace
- `GET /writer/snapshot` - Writer workspace
- `GET /research/workspace` - Research workspace
- `GET /dashboard/summary` - Dashboard data

## 🌐 URLs

### Development
- Web: http://localhost:5173
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Production
- Web: http://localhost:8800
- API: http://localhost:8000

## 📱 Platform Detection

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

## 🎯 Component Pattern

```typescript
import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'

export default function MyPage() {
  const [data, setData] = useState('')
  
  const mutation = useMutation({
    mutationFn: async (payload) => {
      const response = await apiClient.post(apiPath('endpoint'), payload)
      return response.data
    },
    onSuccess: (data) => {
      setData(data)
      toast.success('Success!')
    },
    onError: (error) => {
      toast.error(`Error: ${error.message}`)
    },
  })
  
  return (
    <div className="px-4 py-6">
      {/* Your UI */}
    </div>
  )
}
```

## 🔧 Environment Variables

```bash
# Skip interactive prompt
export OSDASH_UI_MODE=web
export DEV_MODE=desktop

# API configuration
export API_BASE_URL=http://localhost:8000
```

## 📦 Package Management

```bash
# Frontend
cd frontend
npm install
npm run dev
npm run build

# Backend
pip install -r requirements.txt
python -m assistant_hub.api.server
```

## 🐛 Troubleshooting

### Build fails
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### API not responding
```bash
# Check if backend is running
curl http://localhost:8000/health

# Start backend manually
python -m assistant_hub.api.server
```

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

## 📚 Documentation

- `COMPLETE_MIGRATION_GUIDE.md` - Full migration guide
- `MIGRATION_COMPLETE_SUMMARY.md` - Migration summary
- `README.md` - Project overview
- `frontend/QUICK_START.md` - Frontend guide
- `frontend/THEME.md` - Theme documentation

## ✅ Migration Status

**Status:** ✅ 100% Complete

- ✅ All 27 Tkinter tabs migrated
- ✅ Cross-platform support (Web, Linux, Windows, macOS)
- ✅ Single entry point
- ✅ Unified API backend
- ✅ Build scripts
- ✅ Complete documentation

## 🎉 Ready to Use!

```bash
# Start developing
python run.py

# Build for production
./scripts/build_all.sh

# Deploy and enjoy!
```

