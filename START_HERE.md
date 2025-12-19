# OS Dashboard AI Assistant - Quick Start Guide

## 🚀 Unified Launch System

This project now has a **unified launcher** that combines all services into a single entry point!

### Quick Start

#### Option 1: Desktop Application (Recommended)
```bash
python unified_launcher.py --mode desktop
```

#### Option 2: Web Browser
```bash
python unified_launcher.py --mode browser
```

#### Option 3: Server Only
```bash
python unified_launcher.py --mode server --port 8800
```

#### Option 4: SDLC Automation
```bash
python unified_launcher.py --mode sdlc
```

### What's New?

✅ **All API Endpoints Working** - No more 404 errors!
- `/api/runtime/diagnostics` - Runtime diagnostics
- `/api/personas` - Persona management
- `/api/search/status` - Search status
- `/api/operations/summary` - Operations summary
- `/api/templates` - Document templates
- `/api/audit/summary` - Audit logs
- And many more!

✅ **Single Entry Point** - One command to start everything

✅ **SDLC Automation** - End-to-end development lifecycle automation
- Code generation
- Testing
- Quality checks
- Build
- Deployment preparation

### Available Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `desktop` | Launch PyWebView desktop app | Local development with native window |
| `browser` | Launch in default browser | Development and testing |
| `server` | API server only | Production deployment |
| `sdlc` | Run SDLC automation | CI/CD pipeline |
| `all` | All services + monitoring | Full stack development |

### SDLC Automation Features

Run comprehensive SDLC automation:

```bash
# Full pipeline
python sdlc_automation.py

# Skip tests
python sdlc_automation.py --skip-tests

# Skip frontend build
python sdlc_automation.py --skip-frontend

# Generate documentation
python sdlc_automation.py --generate-docs
```

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  Unified Launcher                        │
│                (unified_launcher.py)                     │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
    ┌────▼────┐ ┌───▼────┐ ┌───▼─────┐
    │ FastAPI │ │  React │ │  SDLC   │
    │ Backend │ │   UI   │ │ Engine  │
    └─────────┘ └────────┘ └─────────┘
         │           │           │
    ┌────▼───────────▼───────────▼────┐
    │      SQLite Database             │
    │   (assistant_hub.db)             │
    └──────────────────────────────────┘
```

### Data Flow

1. **Frontend** makes API calls to backend
2. **Backend** (FastAPI) processes requests
3. **Routers** handle specific endpoints:
   - Runtime diagnostics
   - Personas
   - Search
   - Templates
   - Audit
   - AI systems
   - Network monitoring
   - Security
   - And more!
4. **Database** stores all application data
5. **SDLC Engine** automates development tasks

### Configuration

#### Environment Variables

```bash
# API Server
export API_HOST=127.0.0.1
export API_PORT=8800

# Database
export DB_PATH=/path/to/assistant_hub.db

# SSL (optional)
export CERT_PATH=/path/to/cert.pem
export KEY_PATH=/path/to/key.pem
```

#### Custom Configuration

Edit `config/config.yaml` to customize:
- Themes
- Default views
- Data preferences
- Security settings
- API endpoints

### Troubleshooting

#### 404 Errors

**Fixed!** All missing endpoints have been implemented:
- ✅ `/api/runtime/diagnostics` 
- ✅ `/api/personas`
- ✅ `/api/search/status`
- ✅ `/api/operations/summary`
- ✅ `/api/templates`
- ✅ `/api/audit/summary`
- ✅ `/api/audit/logs`

#### Port Already in Use

```bash
# Use a different port
python unified_launcher.py --port 8801
```

#### Module Import Errors

```bash
# Install dependencies
pip install -r requirements.txt
```

#### Frontend Not Building

```bash
# Build frontend manually
cd frontend
npm install
npm run build
cd ..
```

### Development Workflow

1. **Start Development Server**
   ```bash
   python unified_launcher.py --mode browser
   ```

2. **Run Tests**
   ```bash
   python sdlc_automation.py
   ```

3. **Make Changes**
   - Edit backend: `assistant_hub/` or `backend_api/`
   - Edit frontend: `frontend/src/`

4. **Rebuild & Test**
   ```bash
   python sdlc_automation.py
   ```

5. **Deploy**
   ```bash
   python sdlc_automation.py --deploy-staging
   ```

### API Documentation

Once the server is running, visit:
- API Docs: http://localhost:8800/api/docs
- ReDoc: http://localhost:8800/api/redoc

### Project Structure

```
/workspace/
├── unified_launcher.py          # Single entry point
├── sdlc_automation.py           # SDLC automation
├── assistant_hub/               # Core backend
│   ├── api/
│   │   └── server.py            # Main FastAPI app
│   └── ...
├── backend_api/                 # API routers
│   └── routers/
│       ├── runtime_diagnostics.py
│       ├── personas.py
│       ├── search.py
│       ├── templates.py
│       ├── audit.py
│       └── ...
├── frontend/                    # React UI
│   ├── src/
│   └── dist/
├── config/                      # Configuration
└── tests/                       # Test suite
```

### Next Steps

1. ✅ All API endpoints working
2. ✅ Unified launcher created
3. ✅ SDLC automation implemented
4. 📋 Add more tests
5. 📋 Enhance monitoring
6. 📋 Add CI/CD integration

### Support

For issues or questions:
1. Check logs in `logs/` directory
2. Run diagnostics: `python sdlc_automation.py`
3. Review API docs: http://localhost:8800/api/docs

### License

See LICENSE file for details.

---

**Made with ❤️ by the OS Dashboard AI Assistant Team**