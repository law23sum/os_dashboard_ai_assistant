# Quick Reference Card

## 🚀 Starting the Application

### Simplest Way (Recommended)
```bash
# Linux/macOS
./start.sh browser

# Windows  
start.bat browser
```

### Using Unified Launcher
```bash
# Browser mode (default)
python unified_launcher.py

# Desktop application
python unified_launcher.py --mode desktop

# Server only
python unified_launcher.py --mode server --port 8800

# SDLC automation
python unified_launcher.py --mode sdlc
```

## 🔧 Common Commands

### Verify Setup
```bash
python verify_setup.py
```

### Run SDLC Pipeline
```bash
python sdlc_automation.py
```

### Run Tests Only
```bash
python sdlc_automation.py --skip-lint --skip-frontend
```

## 📍 Key URLs

| Service | URL |
|---------|-----|
| Web Application | http://localhost:8800/app/ |
| API Documentation | http://localhost:8800/api/docs |
| ReDoc API Docs | http://localhost:8800/api/redoc |
| Health Check | http://localhost:8800/health |

## 🔍 Troubleshooting

### Check Logs
```bash
tail -f logs/backend_server.log
tail -f logs/runtime_diagnostics.log
```

### Verify All Endpoints Work
```bash
python verify_setup.py
```

### Test API Endpoint
```bash
curl http://localhost:8800/health
```

## 📂 Important Files

| File | Purpose |
|------|---------|
| `unified_launcher.py` | Main entry point |
| `sdlc_automation.py` | SDLC automation |
| `START_HERE.md` | Full documentation |
| `verify_setup.py` | Setup verification |
| `start.sh` / `start.bat` | Simple startup scripts |

## ✅ All Fixed Endpoints

Previously returning 404, now working:
- ✅ `/api/runtime/diagnostics`
- ✅ `/api/personas`  
- ✅ `/api/search/status`
- ✅ `/api/operations/summary`
- ✅ `/api/templates`
- ✅ `/api/audit/summary`
- ✅ `/api/audit/logs`

## 🎯 Quick Tips

1. **Always start here**: `./start.sh browser`
2. **Check setup**: `python verify_setup.py`
3. **Run full SDLC**: `python sdlc_automation.py`
4. **View API docs**: http://localhost:8800/api/docs
5. **Check logs**: `tail -f logs/backend_server.log`

## 🆘 Need Help?

1. Read: `START_HERE.md`
2. Check: `IMPLEMENTATION_SUMMARY.md`
3. Verify: `python verify_setup.py`
4. Test: `python sdlc_automation.py`

---

**Remember**: Everything now works through ONE unified entry point! 🎉
