# Remaining TODOs (Codex Sentinel)

Generated at: `2025-12-11T22:34:59Z`

## os_dashboard_ai_assistant
- Repo: `/Users/chrisdixon/Projects/os_dashboard_ai_assistant`
- Scanned files: **1184**
- Total TODO markers: **245**
- Breakdown: FIXME=2, TODO=240, XXX=3

### Sample hits (capped)
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/db.py:25` **TODO** — STATUS_OPTIONS = ["TODO", "IN_PROGRESS", "BLOCKED", "DONE"]
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/db.py:71` **TODO** — status: str = "TODO"
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/db.py:451` **TODO** — status = (r["status"] or "TODO").upper()
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/db.py:453` **TODO** — status = "TODO"
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/suggestions.py:136` **TODO** — if task.status == "TODO" and task.priority in ["HIGH", "CRITICAL"]:
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/suggestions.py:146` **TODO** — "message": f"High priority task #{task.id} has been TODO for {days_old} days",
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/ai_task_creation.py:17` **TODO** — # Examples: "Create a task to...", "I need to...", "TODO: ...", "Task: ..."
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/ai_task_creation.py:20` **TODO** — r"todo:\s*(.+?)(?:\.|$|due|priority)",
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/ai_task_creation.py:112` **TODO** — status="TODO",
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/file_task_extraction.py:126` **TODO** — status="TODO",
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/file_task_extraction.py:157` **TODO** — r"(?:^|\n)\s*(?:TODO|TASK|ACTION):\s*(.+?)(?:\n|$)",
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/file_task_extraction.py:175` **TODO** — status="TODO",
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/export_import.py:146` **TODO** — status=row.get("Status", "TODO").strip().upper(),
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/export_import.py:195` **TODO** — status=task_data.get("status", "TODO").strip().upper(),
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/task_templates.py:98` **TODO** — status="TODO",
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/task_automation.py:37` **TODO** — status="TODO",
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/analytics.py:15` **TODO** — todo = len([t for t in state.tasks if t.status == "TODO"])
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/analytics.py:24` **TODO** — "todo": todo,
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/analytics.py:43` **TODO** — "todo": len([t for t in project_tasks if t.status == "TODO"]),
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/analytics.py:131` **TODO** — report.append(f"  TODO: {task_stats['todo']}")
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/demo_seed.py:58` **TODO** — "status": "TODO",
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/demo_seed.py:66` **TODO** — "status": "TODO",
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/gui.py:1460` **TODO** — self.status_combo.set("TODO")
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/gui.py:1498` **TODO** — status = "TODO"
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/gui.py:4111` **TODO** — lines.append(f"  ☐ TODO: {task_stats['todo']}")
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/core/api_server.py:91` **TODO** — status = row["status"] or "TODO"
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/core/api_server.py:385` **TODO** — "TODO",
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/core/routing.py:63` **TODO** — re.compile(r"new.*todo", re.IGNORECASE),
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/daemon/monitors.py:86` **TODO** — task.status == "TODO"
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/assistant_hub/api/server.py:679` **TODO** — status=(payload.status or "TODO").upper(),
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/ui/gui.py:1036` **TODO** — self.status_combo.set("TODO")
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/ui/gui.py:1074` **TODO** — status = "TODO"
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/ui/gui.py:2891` **TODO** — lines.append(f"  ☐ TODO: {task_stats['todo']}")
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/documentation/UI_MIGRATION_STATUS.md:14` **TODO** — | AI Console / Chat | `/chat` → `frontend/src/pages/Chat.tsx` | 🔄 Compose/send now flows through `/api/chat` so the “Compose Message” panel…
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/documentation/IMPLEMENTATION_SUMMARY.md:161` **TODO** — - "TODO: Fix the bug in the login system"
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/documentation/FILE_TASK_EXTRACTION_FEATURE.md:5` **TODO** — This feature allows you to upload a file for a specific project, and the system will automatically extract tasks from the file content usin…
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/documentation/FILE_TASK_EXTRACTION_FEATURE.md:44` **TODO** — - Extracts bullet points, numbered lists, TODO items, etc.
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/documentation/FILE_TASK_EXTRACTION_FEATURE.md:71` **TODO** — - **Status**: Set to "TODO"
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/documentation/FILE_TASK_EXTRACTION_FEATURE.md:101` **TODO** — - TODO markers
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/documentation/AI_OFFICE_AGENT_REALTIME.md:547` **TODO** — # TODO: call into specific handlers
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/documentation/FUTURE_FEATURE_PORTFOLIO.md:18` **TODO** — - Buttons for copying summaries and adding TODO boards to keep planning lightweight.
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/documentation/FEATURE_OPPORTUNITIES.md:261` **TODO** — - Import from other task managers (Todoist, Asana)
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/documentation/OS_DashboardAIAssistantTOC.md:27` **TODO** — ### 0.10 Open Questions / TODOs
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/documentation/OS_DashboardAIAssistantTOC.md:53` **TODO** — ### 1.8 Open Questions / TODOs
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/documentation/OS_DashboardAIAssistantTOC.md:145` **TODO** — - `DOCUMENT_TEMPLATES_AND_AUTOMATION.md`, `documentation/config/samples/*.md`, `DOCUMENT_UPLOAD_IMPLEMENTATION.md`, and `AWS_COST_ESTIMATE.…
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/documentation/root/MIGRATION_GUIDE.md:79` **TODO** — ### 📋 TODO
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/frontend/package-lock.json:5710` **XXX** — "integrity": "sha512-YZo3K82SD7Riyi0E1EQPojLz7kpepnSQI9IyPbHHg1XXXevb5dJI7tpyN2ADxGcQbHG7vcyRHk0cbwqcQriUtg==",
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/frontend/public/docs/IMPLEMENTATION_SUMMARY.md:161` **TODO** — - "TODO: Fix the bug in the login system"
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/frontend/public/docs/FILE_TASK_EXTRACTION_FEATURE.md:5` **TODO** — This feature allows you to upload a file for a specific project, and the system will automatically extract tasks from the file content usin…
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/frontend/public/docs/FILE_TASK_EXTRACTION_FEATURE.md:44` **TODO** — - Extracts bullet points, numbered lists, TODO items, etc.
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/frontend/public/docs/FILE_TASK_EXTRACTION_FEATURE.md:71` **TODO** — - **Status**: Set to "TODO"
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/frontend/public/docs/FILE_TASK_EXTRACTION_FEATURE.md:101` **TODO** — - TODO markers
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/frontend/public/docs/NETWORK_MONITORING.md:47` **TODO** — - Wire the watchdog output into Codex Sentinel so automation can open TODOs whenever suspicious activity spikes.
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/frontend/public/docs/AI_OFFICE_AGENT_REALTIME.md:547` **TODO** — # TODO: call into specific handlers
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/frontend/public/docs/FUTURE_FEATURE_PORTFOLIO.md:18` **TODO** — - Buttons for copying summaries and adding TODO boards to keep planning lightweight.
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/frontend/public/docs/FEATURE_OPPORTUNITIES.md:261` **TODO** — - Import from other task managers (Todoist, Asana)
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/frontend/public/docs/v1000_sequential_task_queue.md:8` **TODO** — 3. **Bootstrap ops hub** – finalize `~/OS_Dashboard_AI_Assistant` structure (logs/, reports/, TODO.md, automation configs).
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/frontend/public/docs/v1000_sequential_task_queue.md:26` **TODO** — 15. **TODO curation** – append unresolved items to `~/OS_Dashboard_AI_Assistant/TODO.md` with owners, blockers, and links.
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/frontend/public/docs/v1000_sequential_task_queue.md:27` **TODO** — 16. **Codex baton pass** – before finishing a session, spawn/notify the next Codex context using the fresh TODO slice and any advisory note…
- `/Users/chrisdixon/Projects/os_dashboard_ai_assistant/frontend/src/types/index.ts:580` **TODO** — todo: number

