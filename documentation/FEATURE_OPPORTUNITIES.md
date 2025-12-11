# Feature Opportunities - OS Dashboard AI Assistant

This document identifies areas in the codebase where new features are implied or can be added.

## 1. External Data Integration System ⭐ HIGH PRIORITY

### Location: `assistant_hub/db.py`

**Infrastructure Already Exists:**
- Database tables: `external_sources` and `external_items`
- Functions: `ensure_external_source()`, `record_external_item()`, `load_external_connections()`, `save_external_connections()`
- Data class: `ExternalConnection`

**Missing Implementation:**
- No actual integration modules for external services
- No UI to manage external connections
- No sync functionality

**Features to Add:**

#### 1.1 Google Calendar Integration
- **File to create:** `assistant_hub/integrations/google_calendar.py`
- **Functionality:**
  - OAuth2 authentication flow
  - Sync calendar events to `external_items` table
  - Convert events to tasks automatically
  - Display upcoming events on dashboard
  - Two-way sync (create events from tasks)

#### 1.2 Gmail/Email Integration
- **File to create:** `assistant_hub/integrations/gmail.py`
- **Functionality:**
  - OAuth2 authentication
  - Fetch emails and store in `external_items`
  - Convert important emails to tasks
  - Search and filter emails
  - Link emails to projects/tasks

#### 1.3 GitHub Integration
- **File to create:** `assistant_hub/integrations/github.py`
- **Functionality:**
  - Personal access token authentication
  - Sync issues, PRs, commits
  - Convert GitHub issues to tasks
  - Link code changes to projects
  - Display repository activity

#### 1.4 Notes/Knowledge Base Integration
- **File to create:** `assistant_hub/integrations/notes.py`
- **Functionality:**
  - Local file system scanning (Markdown, text files)
  - Index notes in `external_items`
  - Full-text search
  - Link notes to tasks/projects
  - AI-powered note summarization

#### 1.5 External Connections Management UI
- **Location:** Add new tab in `gui.py`: `_build_integrations_tab()`
- **Functionality:**
  - List all external connections
  - Add/remove connections
  - Configure sync settings
  - View sync status and last sync time
  - Manual sync trigger
  - Display external items (events, emails, etc.)

---

## 2. Data Preferences System ⭐ MEDIUM PRIORITY

### Location: `assistant_hub/db.py` (Settings), `gui.py` (Settings tab)

**Already Exists:**
- `DEFAULT_FETCH_PREFERENCES` with keys: `notes`, `calendar`, `mail`, `files`
- Settings UI checkboxes for these preferences
- Settings are saved/loaded

**Missing Implementation:**
- Preferences are saved but never used
- No actual fetching/syncing based on preferences

**Features to Add:**

#### 2.1 Preference-Based Sync Scheduler
- **File to create:** `assistant_hub/sync_scheduler.py`
- **Functionality:**
  - Background thread that checks preferences
  - Only syncs enabled data sources
  - Configurable sync intervals
  - Respects user preferences

#### 2.2 Dashboard Integration
- **Location:** `gui.py` - `refresh_dashboard()`
- **Functionality:**
  - Show external items based on preferences
  - Display calendar events if `calendar: True`
  - Show recent emails if `mail: True`
  - Display file attachments if `files: True`

---

## 3. Security Status Enhancement ⭐ MEDIUM PRIORITY

### Location: `assistant_hub/db.py`, `gui.py` (Dashboard)

**Already Exists:**
- `SecurityStatus` dataclass
- Security status display on dashboard
- Connection to "mac_guard" source

**Missing Implementation:**
- No actual security monitoring
- Status is static/offline
- No real-time updates

**Features to Add:**

#### 3.1 Security Monitoring Module
- **File to create:** `assistant_hub/security/monitor.py`
- **Functionality:**
  - System security checks (macOS)
  - Firewall status
  - Antivirus status
  - Network security
  - File system integrity checks
  - Real-time threat detection

#### 3.2 Security Dashboard
- **Location:** Expand `cyber_box` in `gui.py`
- **Functionality:**
  - Detailed security metrics
  - Threat alerts
  - Security recommendations
  - Historical security logs

---

## 4. Task Automation Features ⭐ HIGH PRIORITY

### Location: `assistant_hub/gui.py`, `assistant_hub/db.py`

**Missing Implementation:**
- No task templates
- No recurring tasks
- No task dependencies
- No task time tracking

**Features to Add:**

#### 4.1 Task Templates
- **File to create:** `assistant_hub/task_templates.py`
- **Functionality:**
  - Pre-defined task templates
  - Quick task creation from templates
  - Template library management

#### 4.2 Recurring Tasks
- **Location:** Add to `Task` dataclass and database
- **Functionality:**
  - Recurrence patterns (daily, weekly, monthly)
  - Auto-generate next occurrence
  - Recurrence rules (RRULE-like)

#### 4.3 Task Dependencies
- **Location:** Add `depends_on` field to `Task`
- **Functionality:**
  - Block tasks until dependencies complete
  - Visual dependency graph
  - Automatic status updates

#### 4.4 Time Tracking
- **Location:** Add `time_logged` field to `Task`
- **Functionality:**
  - Start/stop timer
  - Manual time entry
  - Time reports per project
  - Time estimates vs actual

---

## 5. Advanced Dashboard Features ⭐ MEDIUM PRIORITY

### Location: `gui.py` - `_build_dashboard_tab()`

**Features to Add:**

#### 5.1 Calendar View
- **Functionality:**
  - Monthly/weekly calendar view
  - Tasks displayed on calendar
  - Drag-and-drop task scheduling
  - Integration with external calendar events

#### 5.2 Analytics & Reports
- **File to create:** `assistant_hub/analytics.py`
- **Functionality:**
  - Task completion trends
  - Project progress charts
  - Time spent analysis
  - Productivity metrics
  - Export reports (PDF, CSV)

#### 5.3 Smart Suggestions
- **File to create:** `assistant_hub/suggestions.py`
- **Functionality:**
  - AI-powered task prioritization
  - Deadline reminders
  - Workload balancing suggestions
  - Project health indicators

---

## 6. AI Assistant Enhancements ⭐ HIGH PRIORITY

### Location: `assistant_hub/ai.py`, `gui.py` (Chat tab)

**Features to Add:**

#### 6.1 Task Creation from Chat
- **Functionality:**
  - AI can create tasks from conversation
  - Natural language task parsing
  - Auto-assign to projects
  - Extract due dates and priorities

#### 6.2 Project Insights
- **Functionality:**
  - AI analysis of project status
  - Risk identification
  - Resource recommendations
  - Progress predictions

#### 6.3 Code Analysis Tools
- **File to create:** `assistant_hub/tools/code_analysis.py`
- **Functionality:**
  - Code review assistance
  - Bug detection
  - Performance analysis
  - Documentation generation

---

## 7. Export & Import Features ⭐ LOW PRIORITY

### Location: New module

**Features to Add:**

#### 7.1 Data Export
- **File to create:** `assistant_hub/export.py`
- **Functionality:**
  - Export tasks to CSV/JSON
  - Export projects to JSON
  - Full database backup
  - Export chat history

#### 7.2 Data Import
- **File to create:** `assistant_hub/import.py`
- **Functionality:**
  - Import from CSV/JSON
  - Import from other task managers (Todoist, Asana)
  - Bulk task creation
  - Merge external data

---

## 8. Collaboration Features ⭐ MEDIUM PRIORITY

### Location: New module

**Features to Add:**

#### 8.1 Multi-User Support
- **Location:** Extend database schema
- **Functionality:**
  - User accounts
  - Task sharing
  - Project collaboration
  - Activity logs

#### 8.2 Comments & Discussions
- **Location:** Add to `Task` and `Project`
- **Functionality:**
  - Comments on tasks
  - Project discussions
  - @mentions
  - Notification system

---

## 9. Mobile/Web API ⭐ LOW PRIORITY

### Location: New module

**Features to Add:**

#### 9.1 REST API
- **File to create:** `assistant_hub/api/server.py`
- **Functionality:**
  - RESTful API for tasks/projects
  - Authentication
  - Webhook support
  - Mobile app backend

#### 9.2 Web Dashboard
- **File to create:** `assistant_hub/web/`
- **Functionality:**
  - Web-based UI
  - Responsive design
  - Real-time updates
  - Cross-platform access

---

## Implementation Priority Recommendations

1. **High Priority:**
   - External Data Integration (Google Calendar, Gmail)
   - Task Automation (recurring tasks, dependencies)
   - AI Task Creation from Chat

2. **Medium Priority:**
   - Data Preferences Integration
   - Security Monitoring
   - Analytics & Reports
   - External Connections Management UI

3. **Low Priority:**
   - Export/Import
   - Collaboration Features
   - Mobile/Web API

---

## Quick Start: Adding Your First Integration

To add a new external integration:

1. Create `assistant_hub/integrations/your_service.py`
2. Implement authentication (OAuth2, API key, etc.)
3. Create sync function that calls `record_external_item()`
4. Add UI in `gui.py` - `_build_integrations_tab()`
5. Add sync scheduler in `sync_scheduler.py`
6. Update settings to include new service

Example structure:
```python
# assistant_hub/integrations/google_calendar.py
from ..db import init_db, record_external_item

def sync_calendar_events(conn):
    # Fetch events from Google Calendar API
    events = fetch_google_calendar_events()
    
    for event in events:
        record_external_item(
            conn,
            source_name="Google Calendar",
            source_kind="calendar",
            external_id=event['id'],
            item_kind="event",
            title=event['summary'],
            data=event
        )
```

---

## Notes

- All database infrastructure is ready for external integrations
- Settings system supports preference-based syncing
- GUI framework (ttkbootstrap) supports modern UI additions
- AI assistant can be extended with new tools/functions
- Security status system has placeholder for real monitoring

