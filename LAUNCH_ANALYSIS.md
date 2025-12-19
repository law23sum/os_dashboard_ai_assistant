# Launch Commands Analysis & Configuration Guide

## Executive Summary

Your commands are **partially correct** but there are **redundant API servers** and **port configuration inconsistencies** that need to be addressed.

## Your Commands Analysis

### Current Commands
```bash
# Terminal 1: Backend API
uvicorn assistant_hub.api.server:create_app --factory --reload --host 127.0.0.1 --port 8000

# Terminal 2: Orchestrator with UI
./launch_orchestrator.sh --ui

# Terminal 3: Frontend
npm run dev
```

### Issues Identified

1. **Port Mismatch**: Frontend Vite config defaults to `http://localhost:8070` but your backend runs on `8000`
2. **Redundant API Servers**: Two separate FastAPI applications exist:
   - `assistant_hub/api/server.py` (port 8000)
   - `backend_api/main.py` (port 8000)
3. **Orchestrator Launch**: `launch_orchestrator.sh --ui` already launches `start_ui.py`, which starts its own backend, causing conflicts

---

## Correct Launch Methods

### Method 1: Unified Launcher (RECOMMENDED)

**Single Command:**
```bash
python start_ui.py --mode web
```

This automatically:
- Starts FastAPI backend on `127.0.0.1:8000`
- Starts Vite dev server on `localhost:5173`
- Configures proxy correctly
- Handles SSL if certificates exist

**With Orchestrator:**
```bash
OSDASH_ENABLE_ORCHESTRATOR=1 python start_ui.py --mode web
```

### Method 2: Orchestrator Script

**Single Command:**
```bash
./launch_orchestrator.sh --ui
```

This:
- Launches master orchestrator
- Starts `start_ui.py` (which handles backend + frontend)
- Opens dashboard at `http://localhost:5173/ai/orchestrator`

**Note**: Don't run additional backend/frontend commands when using this method.

### Method 3: Manual Component Launch

**Terminal 1 - Backend:**
```bash
uvicorn assistant_hub.api.server:create_app --factory --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
VITE_API_TARGET=http://localhost:8000 npm run dev:web
```

**Terminal 3 - Orchestrator (optional):**
```bash
python os_dashboard_ai_assistant.py --root ~/Projects
```

### Method 4: Docker

**Build and Run:**
```bash
docker build -t os-dashboard-ai-assistant .
docker run -p 8000:8000 os-dashboard-ai-assistant
```

**With docker-compose:**
```bash
docker-compose up
```

---

## Port Configuration Reference

### Standard Ports

| Component | Port | Host | Environment Variable |
|-----------|------|------|---------------------|
| **Backend API** | `8000` | `127.0.0.1` | `OSDASH_API_PORT` |
| **Frontend (Vite)** | `5173` | `localhost` | N/A |
| **Legacy API** | `8070` | `127.0.0.1` | `ASSISTANT_HUB_API_PORT` |
| **Webview Build** | `8800` | `127.0.0.1` | N/A |

### Configuration Files

**Frontend Vite Config** (`frontend/vite.config.ts`):
```typescript
const apiTarget = process.env.VITE_API_TARGET || "http://localhost:8070";
```

**Issue**: Defaults to `8070` but should be `8000` for consistency.

**Backend** (`start_ui.py`):
```python
DEFAULT_API_HOST = "127.0.0.1"
DEFAULT_API_PORT = 8000
```

---

## Redundant API Servers Analysis

### Problem: Two FastAPI Applications

#### 1. `assistant_hub/api/server.py`
- **Location**: `assistant_hub/api/server.py`
- **Entry Point**: `assistant_hub.api.server:create_app`
- **Port**: 8000 (default)
- **Purpose**: Main API server for React frontend
- **Routes**: `/api/*`, `/writer/*`, `/dashboard/*`, `/projects/*`, etc.

#### 2. `backend_api/main.py`
- **Location**: `backend_api/main.py`
- **Entry Point**: `backend_api.main:app`
- **Port**: 8000 (default, auto-finds available port)
- **Purpose**: Alternative API server with similar routes
- **Routes**: `/api/*` (duplicate routes)

### Recommendation

**Consolidate to ONE API server:**

1. **Primary**: Use `assistant_hub/api/server.py` (already integrated with React frontend)
2. **Deprecate**: `backend_api/main.py` (or merge its unique routes into primary)

**Action Items:**
- [ ] Audit routes in both servers
- [ ] Merge unique routes from `backend_api/main.py` into `assistant_hub/api/server.py`
- [ ] Update all references to use single entry point
- [ ] Update documentation

---

## Corrected Launch Commands by Environment

### Local Development

**Option A - Unified (Recommended):**
```bash
python start_ui.py --mode web
```

**Option B - With Orchestrator:**
```bash
./launch_orchestrator.sh --ui
```

**Option C - Manual:**
```bash
# Terminal 1
uvicorn assistant_hub.api.server:create_app --factory --reload --host 127.0.0.1 --port 8000

# Terminal 2
cd frontend && VITE_API_TARGET=http://localhost:8000 npm run dev:web
```

### Docker

```bash
# Build
docker build -t os-dashboard-ai-assistant .

# Run
docker run -p 8000:8000 -p 5173:5173 os-dashboard-ai-assistant

# Or with compose
docker-compose up
```

### Production

```bash
# Build frontend
cd frontend && npm run build:web

# Serve with FastAPI
uvicorn assistant_hub.api.server:create_app --factory --host 0.0.0.0 --port 8000
```

---

## IP Address & Port Configuration Fixes

### Issue 1: Frontend Proxy Target

**Current** (`frontend/vite.config.ts`):
```typescript
const apiTarget = process.env.VITE_API_TARGET || "http://localhost:8070";
```

**Should be**:
```typescript
const apiTarget = process.env.VITE_API_TARGET || "http://localhost:8000";
```

### Issue 2: CORS Configuration

Both API servers have CORS configured, but ensure consistency:

**`assistant_hub/api/server.py`** (lines 335-354):
- Allows: `localhost:5173`, `127.0.0.1:5173`, `localhost:5174`
- ✅ Correct

**`backend_api/main.py`** (lines 35-46):
- Allows: `localhost:5173`, `127.0.0.1:5173`, `localhost:5174`
- ✅ Correct

### Issue 3: Host Binding

**Development**: Use `127.0.0.1` (localhost only)
**Docker/Production**: Use `0.0.0.0` (all interfaces)

---

## Recommended Fixes

### 1. Fix Frontend Vite Config

Update `frontend/vite.config.ts`:
```typescript
// Change line 10 from:
const apiTarget = process.env.VITE_API_TARGET || "http://localhost:8070";

// To:
const apiTarget = process.env.VITE_API_TARGET || "http://localhost:8000";
```

### 2. Consolidate API Servers

Create migration plan:
1. Identify unique routes in `backend_api/main.py`
2. Merge into `assistant_hub/api/server.py`
3. Update all launch scripts to use single entry point
4. Deprecate `backend_api/main.py`

### 3. Standardize Port Configuration

Create `.env.example`:
```bash
# API Configuration
OSDASH_API_HOST=127.0.0.1
OSDASH_API_PORT=8000
VITE_API_TARGET=http://localhost:8000

# Frontend
VITE_DEV_SERVER_PORT=5173
```

### 4. Update Documentation

- Update README.md with correct commands
- Add troubleshooting section for port conflicts
- Document single API server architecture

---

## Quick Reference: Correct Commands

### ✅ RECOMMENDED (Single Command)
```bash
python start_ui.py --mode web
```

### ✅ With Orchestrator
```bash
./launch_orchestrator.sh --ui
```

### ✅ Manual (3 Terminals)
```bash
# Terminal 1
uvicorn assistant_hub.api.server:create_app --factory --reload --host 127.0.0.1 --port 8000

# Terminal 2
cd frontend && VITE_API_TARGET=http://localhost:8000 npm run dev:web

# Terminal 3 (optional)
python os_dashboard_ai_assistant.py
```

### ✅ Docker
```bash
docker-compose up
```

---

## Troubleshooting

### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Frontend Can't Connect to Backend
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check VITE_API_TARGET matches backend port
3. Verify CORS allows frontend origin

### Multiple Backend Instances
- Only run ONE backend server
- Use `start_ui.py` which manages this automatically

---

## Summary

**Your commands need these fixes:**

1. ✅ Backend command is correct
2. ⚠️ Frontend needs `VITE_API_TARGET=http://localhost:8000`
3. ⚠️ Don't run `launch_orchestrator.sh --ui` AND manual commands together
4. ⚠️ Two redundant API servers exist - consolidate to one

**Best Practice**: Use `python start_ui.py --mode web` for development.
