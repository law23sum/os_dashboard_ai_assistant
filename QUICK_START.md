# OS Dashboard - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or 3.11
- Node.js 20+
- Docker & Docker Compose (optional but recommended)
- Git

---

## Option 1: Docker Compose (Recommended)

The easiest way to get everything running:

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/swagger
```

**That's it!** Everything is configured and ready to go.

---

## Option 2: Manual Setup

### Backend Setup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.local .env

# 3. Initialize database (automatic on first run)

# 4. Start the backend
python -m uvicorn backend_api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start dev server
npm run dev
```

---

## 🗄️ Restoring Your Missing Projects

The database currently has only 3 projects. If you had ~50 projects before:

### Check for Backups

```bash
# List available backups
curl http://localhost:8000/api/data/backups

# Restore from a backup
curl -X POST http://localhost:8000/api/data/restore \
  -H "Content-Type: application/json" \
  -d '{"backup_file": "backup_YYYYMMDD_HHMMSS.db", "overwrite": false}'
```

### Create a Backup Now

```bash
# Create backup of current data
curl -X POST http://localhost:8000/api/data/backup

# Check data statistics
curl http://localhost:8000/api/data/stats
```

### Import from JSON Export

If you have a JSON export:

```bash
curl -X POST http://localhost:8000/api/data/import-json \
  -F "file=@your_export.json"
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=backend_api --cov-report=html

# Run only E2E tests
pytest tests/ -v -m e2e

# View coverage report
open htmlcov/index.html  # macOS
```

---

## 📊 Verifying the Installation

### Check Backend Health

```bash
curl http://localhost:8000/api/health
# Should return: {"status": "ok", ...}
```

### Check Data Statistics

```bash
curl http://localhost:8000/api/data/stats
# Shows: projects count, tasks count, database size, etc.
```

### Access API Documentation

Visit: http://localhost:8000/swagger

---

## 🗺️ Navigation Structure

The UI now uses a **hybrid tree-network topology**:

### Tree Structure (Categories)
1. **Core Workspaces** - Projects, Tasks, Dev, Writer, Security
2. **AI & Intelligence** - AI Copilot, Chat, Reasoning, Capsules
3. **Research & Simulation** - Research Hub, MLOps, Computer Vision
4. **Operations** - Monitoring, Network, AIOps
5. **Integrations** - API Connectors, Office Tools
6. **Management** - Settings, Billing, Tools
7. **Future Capabilities** - Future Deck, Documentation

### Network Structure (Platforms)
- Each category contains multiple platforms
- Each platform has features ordered by complexity:
  - 🟢 Simple (beginner-friendly)
  - 🔵 Intermediate (standard usage)
  - 🟡 Advanced (power users)
  - 🔴 Expert (specialized techniques)

---

## 🔧 Common Tasks

### Create a New Project

Via API:
```bash
curl -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My New Project",
    "description": "Project description",
    "status": "active",
    "priority": "HIGH"
  }'
```

Via UI:
1. Navigate to Projects page
2. Click "New Project" button
3. Fill in details
4. Click "Create Project"

### View Project Intelligence

```bash
curl http://localhost:8000/api/projects/intelligence
```

Returns health scores, risk levels, and completion ratios for all projects.

### Check TRF Metrics

```bash
curl http://localhost:8000/api/projects/YOUR_PROJECT_NAME/trf
```

Returns Entropy, Resonance, and Continuity metrics per Technical Spec §4.6.

---

## 🐛 Troubleshooting

### Port Already in Use

If port 8000 or 5173 is in use:

```bash
# Backend
python -m uvicorn backend_api.main:app --reload --port 8001

# Frontend
cd frontend && npm run dev -- --port 5174
```

### Database Locked Error

```bash
# Stop all running instances
pkill -f uvicorn
pkill -f "npm run dev"

# Restart
docker-compose -f docker-compose.dev.yml up
```

### Module Not Found Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or in Docker
docker-compose -f docker-compose.dev.yml build --no-cache
```

---

## 📚 Key Files & Directories

```
/workspace/
├── backend_api/           # Backend API
│   ├── routers/           # API endpoints
│   │   ├── projects.py    # Projects CRUD + Intelligence + TRF
│   │   └── data_management.py  # Backup/Restore
│   └── main.py            # FastAPI app
├── frontend/
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── lib/           # Utilities
│   │   │   └── navigationStructure.ts  # Navigation tree
│   │   └── components/
│   │       └── NavigationTree.tsx      # Navigation UI
│   └── package.json
├── tests/
│   ├── conftest.py        # Test fixtures
│   └── e2e/               # End-to-end tests
├── .env.local             # Local environment variables
├── docker-compose.dev.yml # Docker development setup
└── IMPLEMENTATION_SUMMARY.md  # Detailed documentation
```

---

## 🚢 Deployment Options

### Local Development
```bash
docker-compose -f docker-compose.dev.yml up
```

### Alpha/Beta Environment
```bash
# Set environment
export ENVIRONMENT=alpha

# Load alpha config
source .env.alpha

# Deploy
docker-compose up -d
```

### Production (Kubernetes)
```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -n osdash-production
```

See `IMPLEMENTATION_SUMMARY.md` for detailed deployment instructions.

---

## 📖 Documentation

- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`
- **Technical Spec v6**: `Technical Spec Sheet (Version 6 Latest Version).txt`
- **Architecture Blueprint**: `OSD_ARCHITECTURE_BLUEPRINT.md`
- **API Docs**: http://localhost:8000/swagger (when running)

---

## 🆘 Getting Help

1. **Check Logs**:
   ```bash
   # Docker
   docker-compose -f docker-compose.dev.yml logs -f
   
   # Manual
   tail -f logs/local.log
   ```

2. **Run Diagnostics**:
   ```bash
   python scripts/check_spec_coverage.py
   ```

3. **Check System Health**:
   ```bash
   curl http://localhost:8000/api/health
   curl http://localhost:8000/api/data/stats
   ```

4. **Review Tests**:
   ```bash
   pytest tests/ -v --tb=short
   ```

---

## ✅ Next Steps

1. ✅ Start the application (Docker Compose or manual)
2. ✅ Verify it's running (health check)
3. ✅ Check data statistics
4. ✅ Restore missing projects (if needed)
5. ✅ Explore the new navigation structure
6. ✅ Run tests to verify functionality
7. ✅ Review `IMPLEMENTATION_SUMMARY.md` for details

---

## 🎯 Quick Commands Cheatsheet

```bash
# Start everything
docker-compose -f docker-compose.dev.yml up

# Stop everything
docker-compose -f docker-compose.dev.yml down

# View logs
docker-compose -f docker-compose.dev.yml logs -f backend

# Run tests
pytest tests/ -v

# Create backup
curl -X POST http://localhost:8000/api/data/backup

# Check coverage
python scripts/check_spec_coverage.py

# Build for production
docker-compose build
```

---

**🎉 You're all set!** The system is now production-ready with full backup/restore capabilities, comprehensive testing, and aligned with Technical Spec v6.

For questions or issues, check the logs or consult `IMPLEMENTATION_SUMMARY.md`.
