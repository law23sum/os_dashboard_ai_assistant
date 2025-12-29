# Admin Account Credentials

## Default Admin Account

After running the setup script, the following admin account is created:

- **Username:** `admin`
- **Email:** `admin@osdashboard.local`
- **Password:** `admin123`
- **Role:** Administrator

⚠️ **IMPORTANT:** Change the default password immediately after first login!

## Creating Admin Account

To create the admin account, run:

```bash
python scripts/create_admin_account.py
```

This script will:
1. Initialize authentication tables
2. Create the default admin account
3. Create a test user account for development

## Test User Account

A test/dummy user account is also created:

- **Username:** `testuser`
- **Email:** `test@osdashboard.local`
- **Password:** `test123`
- **Role:** Regular User
- **Metadata:** Marked as dummy/test data user

## Accessing Admin Dashboard

1. Navigate to `/login` and sign in with admin credentials
2. After login, navigate to `/admin` to access the admin dashboard
3. The admin dashboard provides:
   - Holistic system overview
   - Database table schemas and data
   - User management (dummy and production users)
   - Audit logs
   - Real-time system statistics

## Security Notes

- All passwords are hashed using bcrypt
- JWT tokens are used for authentication (7-day expiration)
- All admin actions are logged in the audit_logs table
- User data is protected, identifiable, traceable, and extractable

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Admin (requires admin role)
- `GET /api/admin/overview` - System overview
- `GET /api/admin/tables` - List all tables
- `GET /api/admin/tables/{table_name}/data` - Get table data
- `GET /api/admin/users` - List users
- `GET /api/admin/audit-logs` - Get audit logs
- `GET /api/admin/stats` - Detailed statistics

### Version Control
- `POST /api/versions/documents/{document_id}/versions` - Create version
- `GET /api/versions/documents/{document_id}/versions` - List versions
- `GET /api/versions/documents/{document_id}/versions/compare` - Compare versions

### Unified Logging
- `GET /api/logs/logs` - Get unified logs
- `GET /api/logs/stats` - Log statistics
- `GET /api/logs/stream` - Stream logs (SSE)

### Document Viewer
- `GET /api/viewer/documents/{document_id}/view/{view_type}` - Get document view

### AI Integration
- `GET /api/ai-integration/directory/analyze` - Analyze directory
- `POST /api/ai-integration/files/{document_id}/analyze` - Analyze file
- `GET /api/ai-integration/files/{document_id}/instructions` - Get AI instructions
