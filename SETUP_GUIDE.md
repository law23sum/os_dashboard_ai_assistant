# Setup Guide - OS Dashboard AI Assistant

## Quick Start

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

Key dependencies added:
- `passlib[bcrypt]` - Password hashing
- `python-pptx` - PowerPoint file handling
- All other dependencies already in requirements.txt

### 2. Create Admin Account
```bash
python scripts/create_admin_account.py
```

This creates:
- **Admin user**: `admin` / `admin123`
- **Test user**: `testuser` / `test123`

### 3. Start Backend Server
```bash
python backend_api/main.py
```

Server starts on `http://localhost:8000`

### 4. Start Frontend (in separate terminal)
```bash
cd frontend
npm install
npm run dev
```

Frontend starts on `http://localhost:5173`

### 5. Access Application
- **Login**: http://localhost:5173/login
- **Admin Dashboard**: http://localhost:5173/admin
- **Default Credentials**: See `ADMIN_CREDENTIALS.md`

## Features Overview

### ✅ Authentication System
- Login/Signup pages
- JWT token-based authentication
- Password hashing with bcrypt
- User session management

### ✅ Admin Interface
- Django-style admin dashboard
- View all database tables and schemas
- Browse table data
- User management
- Audit logs

### ✅ Version Control
- Hidden button/tab for version control
- Create document snapshots
- Compare multiple versions
- Diff visualization (text, binary, JSON)
- Merge suggestions

### ✅ Document Viewer
- Multiple format tabs (top right section):
  - Binary view
  - Hexadecimal view
  - Image viewer
  - PDF viewer
  - PowerPoint viewer
  - Excel/CSV viewer
  - JSON viewer
  - Text viewer

### ✅ AI Integration
- Sees whole directory structure
- Analyzes uploaded files
- Generates AI instructions based on file analysis
- Context-aware suggestions

### ✅ Unified Logging
- Combines all thread logs
- Ordered by timestamp
- Real-time streaming (SSE)
- Filtering and search

### ✅ Admin Dashboard
- Holistic system overview
- Dummy data users view
- Production users view
- Real-time statistics
- Database inspection

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Current user

### Admin (requires admin token)
- `GET /api/admin/overview` - System overview
- `GET /api/admin/tables` - List tables
- `GET /api/admin/tables/{name}/data` - Table data
- `GET /api/admin/users` - List users
- `GET /api/admin/audit-logs` - Audit logs

### Version Control
- `POST /api/versions/documents/{id}/versions` - Create version
- `GET /api/versions/documents/{id}/versions` - List versions
- `GET /api/versions/documents/{id}/versions/compare` - Compare

### Unified Logging
- `GET /api/logs/logs` - Get logs
- `GET /api/logs/stats` - Statistics
- `GET /api/logs/stream` - Stream (SSE)

### Document Viewer
- `GET /api/viewer/documents/{id}/view/{type}` - Get view

### AI Integration
- `GET /api/ai-integration/directory/analyze` - Analyze directory
- `POST /api/ai-integration/files/{id}/analyze` - Analyze file
- `GET /api/ai-integration/files/{id}/instructions` - Get instructions

## File Structure

```
/workspace
├── backend_api/
│   ├── routers/
│   │   ├── auth.py              # Authentication
│   │   ├── admin.py             # Admin interface
│   │   ├── version_control.py   # Version control
│   │   ├── unified_logging.py   # Unified logging
│   │   ├── document_viewer.py   # Document viewer
│   │   └── ai_integration.py    # AI integration
│   └── main.py                  # Main app (updated)
├── frontend/src/
│   ├── pages/
│   │   ├── Login.tsx            # Login page
│   │   ├── Signup.tsx           # Signup page
│   │   └── Admin.tsx            # Admin dashboard
│   ├── components/
│   │   ├── VersionControl.tsx   # Version control UI
│   │   └── DocumentViewer.tsx   # Document viewer UI
│   └── api/
│       └── client.ts            # API client helper
├── scripts/
│   └── create_admin_account.py # Admin creation script
├── ADMIN_CREDENTIALS.md         # Admin credentials
├── FEATURE_INTEGRATION_SUMMARY.md # Feature summary
└── SETUP_GUIDE.md              # This file
```

## Security Notes

1. **Change Default Password**: Immediately change `admin123` after first login
2. **JWT Tokens**: Tokens expire after 7 days
3. **HTTPS**: Use HTTPS in production
4. **Environment Variables**: Store SECRET_KEY in environment variable in production
5. **Database**: SQLite is fine for development, use PostgreSQL for production

## Troubleshooting

### Import Errors
If you see import errors, ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Authentication Issues
- Check that admin account was created: `python scripts/create_admin_account.py`
- Verify JWT token in localStorage
- Check backend logs for errors

### Frontend Not Loading
- Ensure backend is running on port 8000
- Check CORS settings in `backend_api/main.py`
- Verify API_BASE in frontend environment

### Database Issues
- Database is created automatically on first run
- Location: `assistant_hub_gui/assistant_hub/assistant_hub.db`
- Can be reset by deleting the database file

## Next Steps

1. ✅ Change admin password
2. ✅ Configure production environment
3. ✅ Set up SSL certificates
4. ✅ Configure database backups
5. ✅ Set up monitoring

## Support

For issues or questions, refer to:
- `FEATURE_INTEGRATION_SUMMARY.md` - Detailed feature documentation
- `ADMIN_CREDENTIALS.md` - Admin account information
- `ARCHITECTURE_OVERVIEW.md` - System architecture
