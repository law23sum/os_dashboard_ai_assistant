# Quick Start Guide - OS Dashboard AI Assistant

Get up and running in 5 minutes! 🚀

## Prerequisites

- **Node.js** 18+ ([Download](https://nodejs.org/))
- **Python** 3.9+ ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/os_dashboard_ai_assistant.git
cd os_dashboard_ai_assistant
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 3. Launch the App

```bash
python run.py
```

You'll see an interactive menu:

```
🚀 OS Dashboard AI Assistant — Unified Launcher
==================================================================

📋 Available Launch Modes:

  🌐 1) React · Web Dev (FastAPI + Vite) ⭐ (default)
  🖥️ 2) React · Desktop Dev (FastAPI + Electron)
  📦 3) Serve built React in browser
  📦 4) Serve built React in desktop shell

------------------------------------------------------------------
💡 Tip: Set OSDASH_UI_MODE or DEV_MODE env var to skip this prompt
------------------------------------------------------------------

👉 Enter your choice (1-4 or press Enter for default):
```

**Choose option 1** (or just press Enter) to launch in web browser mode.

### 4. Access the Dashboard

The app will automatically open in your browser at:
```
http://localhost:5173
```

The API server runs at:
```
http://localhost:8071
```

## Usage

### Web Browser Mode (Recommended for Development)

```bash
python run.py --mode web
# or
DEV_MODE=web python run.py
```

**Features:**
- ✅ Hot module replacement (instant updates)
- ✅ React DevTools support
- ✅ Chrome DevTools debugging
- ✅ Responsive design testing

### Desktop App Mode

```bash
python run.py --mode desktop
# or
DEV_MODE=desktop python run.py
```

**Features:**
- ✅ Native window controls
- ✅ System tray integration
- ✅ File system access
- ✅ Offline support

### Legacy Tkinter GUI

```bash
python run.py --legacy
```

**Note:** The Tkinter GUI is deprecated but still available for reference.

## Navigation

### Main Sections

- **Dashboard** (`/`) - Overview and quick stats
- **Tasks** (`/tasks`) - Task management
- **Projects** (`/projects`) - Project tracking
- **Chat** (`/chat`) - AI conversation interface
- **Research** (`/research`) - Research workspace

### AI Features

- **AI Operations** (`/ai/operations`) - AI ops dashboard
- **AI OS** (`/ai/os`) - AI operating system
- **Advanced AI** (`/ai/advanced`) - Advanced AI features
- **MLOps** (`/ai/mlops`) - ML operations
- **Neural Arch Search** (`/ai/nas`) - Architecture search
- **Security** (`/ai/security`) - AI security monitoring
- **Edge Computing** (`/ai/edge-computing`) - Edge deployment
- **Workflows** (`/ai/workflows`) - Workflow orchestration

### Tools & Utilities

- **Writer** (`/work/writer`) - Document editor
- **Templates** (`/work/templates`) - Task templates
- **Tools** (`/work/tools`) - Terminal and utilities
- **Analytics** (`/analytics`) - Analytics dashboard
- **Settings** (`/settings`) - Application settings

## Building for Production

### Web Build

```bash
cd frontend
npm run build:web
```

Output: `frontend/dist/`

Deploy to:
- Vercel: `vercel deploy`
- Netlify: `netlify deploy --prod`
- AWS S3: `aws s3 sync dist/ s3://your-bucket/`

### Desktop Build

```bash
# Build for current platform
cd frontend
npm run build:desktop

# Or use the unified script for all platforms
cd ..
./build-all-platforms.sh all
```

Output: `frontend/dist-electron/`

## Troubleshooting

### Port Already in Use

If port 5173 or 8071 is already in use:

```bash
# Find and kill the process (macOS/Linux)
lsof -ti:5173 | xargs kill -9
lsof -ti:8071 | xargs kill -9

# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### Module Not Found

```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install

# Python dependencies
pip install -r requirements.txt --force-reinstall
```

### Build Errors

```bash
# Clear build cache
cd frontend
rm -rf dist dist-electron node_modules/.vite

# Rebuild
npm install
npm run build
```

### White Screen on Launch

```bash
# Clear application cache
# macOS
rm -rf ~/Library/Application\ Support/os-dashboard/

# Linux
rm -rf ~/.config/os-dashboard/

# Windows
del /s /q %APPDATA%\os-dashboard\
```

## Development Tips

### Hot Reload

Changes to React components automatically reload in the browser. No need to restart!

### API Changes

If you modify the Python backend, the FastAPI server will auto-reload.

### Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_URL=http://localhost:8071
VITE_APP_ENV=development
VITE_ENABLE_DEBUG=true
```

### Debugging

**Web:**
- Open Chrome DevTools (F12)
- Install React DevTools extension
- Check Console for errors

**Desktop:**
- Enable Electron DevTools
- Check logs in terminal
- Use `console.log()` for debugging

## Next Steps

- 📖 Read the [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment
- 🎨 Check [THEME_GUIDE.md](./THEME_GUIDE.md) for customization
- 🏗️ Review [ARCHITECTURE_NETWORK_MAP.md](./ARCHITECTURE_NETWORK_MAP.md) for system design
- 📝 See [MIGRATION_COMPLETE_SUMMARY.md](./MIGRATION_COMPLETE_SUMMARY.md) for feature list

## Getting Help

- 🐛 [Report bugs](https://github.com/your-org/os_dashboard_ai_assistant/issues)
- 💬 [Ask questions](https://github.com/your-org/os_dashboard_ai_assistant/discussions)
- 📚 [Read docs](./README.md)

## License

See [LICENSE](./LICENSE) file for details.

---

**Happy coding!** 🎉

