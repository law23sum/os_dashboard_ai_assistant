"""
Web-based dashboard UI components for OS Dashboard AI Assistant
"""
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from api_manager import APIManager
from advanced.email_intelligence import AdvancedEmailIntelligence
from advanced.smart_calendar import SmartCalendarManager
from advanced.office_automation import AdvancedOfficeAutomation
from advanced.git_workflow_automation import AdvancedGitWorkflowAutomation
from workflows.cross_app_sync import CrossAppSynchronization
from logger import setup_logger

@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    id: str
    title: str
    type: str
    size: str  # small, medium, large
    data_source: str
    refresh_interval: int  # seconds
    config: Dict[str, Any] = None

class DashboardUIGenerator:
    """Generate web-based dashboard UI components"""
    
    def __init__(self, api_manager: APIManager):
        self.api_manager = api_manager
        self.logger = setup_logger("DashboardUI")
        self.widgets = []
        self.themes = {}
        
    async def initialize(self):
        """Initialize dashboard UI system"""
        await self._load_widget_templates()
        await self._load_themes()
        self.logger.info("Dashboard UI system initialized")
    
    async def _load_widget_templates(self):
        """Load widget templates"""
        self.widget_templates = {
            "email_summary": {
                "title": "Email Summary",
                "type": "card",
                "data_source": "email_intelligence",
                "template": """
                <div class="widget-card email-summary">
                    <h3>📧 Email Summary</h3>
                    <div class="stats">
                        <div class="stat">
                            <span class="number">{{unread_count}}</span>
                            <span class="label">Unread</span>
                        </div>
                        <div class="stat">
                            <span class="number">{{urgent_count}}</span>
                            <span class="label">Urgent</span>
                        </div>
                        <div class="stat">
                            <span class="number">{{action_required}}</span>
                            <span class="label">Action Required</span>
                        </div>
                    </div>
                    <div class="recent-emails">
                        {{#each recent_emails}}
                        <div class="email-item priority-{{priority}}">
                            <span class="sender">{{from}}</span>
                            <span class="subject">{{subject}}</span>
                            <span class="time">{{time}}</span>
                        </div>
                        {{/each}}
                    </div>
                </div>
                """
            },
            "calendar_overview": {
                "title": "Calendar Overview",
                "type": "timeline",
                "data_source": "smart_calendar",
                "template": """
                <div class="widget-card calendar-overview">
                    <h3>📅 Today's Schedule</h3>
                    <div class="timeline">
                        {{#each events}}
                        <div class="event-item">
                            <div class="time">{{start_time}}</div>
                            <div class="event-details">
                                <div class="title">{{title}}</div>
                                <div class="location">{{location}}</div>
                                <div class="attendees">{{attendee_count}} attendees</div>
                            </div>
                        </div>
                        {{/each}}
                    </div>
                    <div class="calendar-stats">
                        <span>{{total_meetings}} meetings today</span>
                        <span>{{free_time}} hours free</span>
                    </div>
                </div>
                """
            },
            "project_health": {
                "title": "Project Health",
                "type": "metrics",
                "data_source": "git_automation",
                "template": """
                <div class="widget-card project-health">
                    <h3>🚀 Project Health</h3>
                    <div class="health-score">
                        <div class="score-circle score-{{health_level}}">
                            <span class="score">{{health_score}}</span>
                            <span class="max">/10</span>
                        </div>
                    </div>
                    <div class="metrics">
                        <div class="metric">
                            <span class="icon">📊</span>
                            <span class="label">Code Quality</span>
                            <span class="value">{{code_quality}}</span>
                        </div>
                        <div class="metric">
                            <span class="icon">🐛</span>
                            <span class="label">Open Issues</span>
                            <span class="value">{{open_issues}}</span>
                        </div>
                        <div class="metric">
                            <span class="icon">🔄</span>
                            <span class="label">Recent Commits</span>
                            <span class="value">{{recent_commits}}</span>
                        </div>
                    </div>
                </div>
                """
            },
            "ai_insights": {
                "title": "AI Insights",
                "type": "insights",
                "data_source": "ai_analysis",
                "template": """
                <div class="widget-card ai-insights">
                    <h3>🤖 AI Insights</h3>
                    <div class="insights-list">
                        {{#each insights}}
                        <div class="insight-item priority-{{priority}}">
                            <div class="insight-icon">{{icon}}</div>
                            <div class="insight-content">
                                <div class="insight-title">{{title}}</div>
                                <div class="insight-description">{{description}}</div>
                                <div class="insight-action">{{action}}</div>
                            </div>
                        </div>
                        {{/each}}
                    </div>
                </div>
                """
            },
            "productivity_metrics": {
                "title": "Productivity Metrics",
                "type": "chart",
                "data_source": "productivity_analysis",
                "template": """
                <div class="widget-card productivity-metrics">
                    <h3>📈 Productivity Metrics</h3>
                    <div class="chart-container">
                        <canvas id="productivity-chart-{{widget_id}}"></canvas>
                    </div>
                    <div class="productivity-stats">
                        <div class="stat">
                            <span class="label">Focus Time</span>
                            <span class="value">{{focus_time}}h</span>
                        </div>
                        <div class="stat">
                            <span class="label">Meeting Time</span>
                            <span class="value">{{meeting_time}}h</span>
                        </div>
                        <div class="stat">
                            <span class="label">Efficiency</span>
                            <span class="value">{{efficiency}}%</span>
                        </div>
                    </div>
                </div>
                """
            },
            "sync_status": {
                "title": "Sync Status",
                "type": "status",
                "data_source": "cross_app_sync",
                "template": """
                <div class="widget-card sync-status">
                    <h3>🔄 Sync Status</h3>
                    <div class="sync-overview">
                        <div class="sync-health status-{{sync_health}}">
                            <span class="status-indicator"></span>
                            <span class="status-text">{{sync_health_text}}</span>
                        </div>
                    </div>
                    <div class="sync-rules">
                        {{#each sync_rules}}
                        <div class="sync-rule status-{{status}}">
                            <span class="rule-name">{{name}}</span>
                            <span class="last-sync">{{last_sync}}</span>
                            <span class="status-badge">{{status}}</span>
                        </div>
                        {{/each}}
                    </div>
                </div>
                """
            }
        }
    
    async def _load_themes(self):
        """Load dashboard themes"""
        self.themes = {
            "modern_dark": {
                "name": "Modern Dark",
                "css": """
                :root {
                    --primary-color: #2563eb;
                    --secondary-color: #64748b;
                    --background-color: #0f172a;
                    --surface-color: #1e293b;
                    --text-primary: #f8fafc;
                    --text-secondary: #cbd5e1;
                    --border-color: #334155;
                    --success-color: #10b981;
                    --warning-color: #f59e0b;
                    --error-color: #ef4444;
                }
                
                body {
                    background-color: var(--background-color);
                    color: var(--text-primary);
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                    margin: 0;
                    padding: 0;
                }
                
                .dashboard-container {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 1.5rem;
                    padding: 2rem;
                    max-width: 1400px;
                    margin: 0 auto;
                }
                
                .widget-card {
                    background: var(--surface-color);
                    border-radius: 12px;
                    padding: 1.5rem;
                    border: 1px solid var(--border-color);
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                }
                
                .widget-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px -5px rgba(0, 0, 0, 0.2);
                }
                
                .widget-card h3 {
                    margin: 0 0 1rem 0;
                    font-size: 1.125rem;
                    font-weight: 600;
                    color: var(--text-primary);
                }
                
                .stats {
                    display: flex;
                    gap: 1rem;
                    margin-bottom: 1.5rem;
                }
                
                .stat {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    padding: 0.75rem;
                    background: rgba(37, 99, 235, 0.1);
                    border-radius: 8px;
                    flex: 1;
                }
                
                .stat .number {
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: var(--primary-color);
                }
                
                .stat .label {
                    font-size: 0.75rem;
                    color: var(--text-secondary);
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }
                
                .email-item, .event-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 0.75rem;
                    margin-bottom: 0.5rem;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 6px;
                    border-left: 3px solid var(--secondary-color);
                }
                
                .priority-urgent {
                    border-left-color: var(--error-color);
                }
                
                .priority-high {
                    border-left-color: var(--warning-color);
                }
                
                .priority-medium {
                    border-left-color: var(--primary-color);
                }
                
                .priority-low {
                    border-left-color: var(--success-color);
                }
                
                .health-score {
                    display: flex;
                    justify-content: center;
                    margin-bottom: 1.5rem;
                }
                
                .score-circle {
                    width: 80px;
                    height: 80px;
                    border-radius: 50%;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    border: 3px solid;
                    position: relative;
                }
                
                .score-excellent { border-color: var(--success-color); }
                .score-good { border-color: var(--primary-color); }
                .score-fair { border-color: var(--warning-color); }
                .score-poor { border-color: var(--error-color); }
                
                .score {
                    font-size: 1.5rem;
                    font-weight: 700;
                }
                
                .max {
                    font-size: 0.75rem;
                    color: var(--text-secondary);
                }
                
                .metrics {
                    display: flex;
                    flex-direction: column;
                    gap: 0.75rem;
                }
                
                .metric {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    padding: 0.5rem;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 6px;
                }
                
                .metric .icon {
                    font-size: 1.25rem;
                }
                
                .metric .label {
                    flex: 1;
                    color: var(--text-secondary);
                }
                
                .metric .value {
                    font-weight: 600;
                    color: var(--text-primary);
                }
                
                .chart-container {
                    height: 200px;
                    margin-bottom: 1rem;
                }
                
                .sync-health {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    margin-bottom: 1rem;
                    padding: 0.75rem;
                    border-radius: 6px;
                }
                
                .status-healthy {
                    background: rgba(16, 185, 129, 0.1);
                    color: var(--success-color);
                }
                
                .status-issues {
                    background: rgba(245, 158, 11, 0.1);
                    color: var(--warning-color);
                }
                
                .status-critical {
                    background: rgba(239, 68, 68, 0.1);
                    color: var(--error-color);
                }
                
                .status-indicator {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: currentColor;
                }
                
                .sync-rule {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 0.5rem;
                    margin-bottom: 0.5rem;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 4px;
                }
                
                .status-badge {
                    padding: 0.25rem 0.5rem;
                    border-radius: 4px;
                    font-size: 0.75rem;
                    font-weight: 500;
                    text-transform: uppercase;
                }
                
                .insight-item {
                    display: flex;
                    gap: 0.75rem;
                    padding: 1rem;
                    margin-bottom: 0.75rem;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 8px;
                    border-left: 3px solid var(--primary-color);
                }
                
                .insight-icon {
                    font-size: 1.5rem;
                    flex-shrink: 0;
                }
                
                .insight-content {
                    flex: 1;
                }
                
                .insight-title {
                    font-weight: 600;
                    margin-bottom: 0.25rem;
                }
                
                .insight-description {
                    color: var(--text-secondary);
                    font-size: 0.875rem;
                    margin-bottom: 0.5rem;
                }
                
                .insight-action {
                    font-size: 0.75rem;
                    color: var(--primary-color);
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }
                """
            },
            "light_professional": {
                "name": "Light Professional",
                "css": """
                :root {
                    --primary-color: #3b82f6;
                    --secondary-color: #6b7280;
                    --background-color: #f9fafb;
                    --surface-color: #ffffff;
                    --text-primary: #111827;
                    --text-secondary: #6b7280;
                    --border-color: #e5e7eb;
                    --success-color: #059669;
                    --warning-color: #d97706;
                    --error-color: #dc2626;
                }
                
                body {
                    background-color: var(--background-color);
                    color: var(--text-primary);
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                    margin: 0;
                    padding: 0;
                }
                
                .dashboard-container {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 1.5rem;
                    padding: 2rem;
                    max-width: 1400px;
                    margin: 0 auto;
                }
                
                .widget-card {
                    background: var(--surface-color);
                    border-radius: 8px;
                    padding: 1.5rem;
                    border: 1px solid var(--border-color);
                    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                }
                
                .widget-card:hover {
                    transform: translateY(-1px);
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                }
                """
            }
        }
    
    async def generate_dashboard_html(self, widgets: List[DashboardWidget], 
                                    theme: str = "modern_dark") -> str:
        """Generate complete dashboard HTML"""
        try:
            # Get widget data
            widget_data = {}
            for widget in widgets:
                data = await self._get_widget_data(widget)
                widget_data[widget.id] = data
            
            # Generate HTML
            html = await self._build_dashboard_html(widgets, widget_data, theme)
            
            return html
            
        except Exception as e:
            self.logger.error(f"Dashboard HTML generation failed: {e}")
            raise
    
    async def _get_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for specific widget"""
        data_source = widget.data_source
        
        if data_source == "email_intelligence":
            return await self._get_email_data()
        elif data_source == "smart_calendar":
            return await self._get_calendar_data()
        elif data_source == "git_automation":
            return await self._get_project_health_data()
        elif data_source == "ai_analysis":
            return await self._get_ai_insights_data()
        elif data_source == "productivity_analysis":
            return await self._get_productivity_data()
        elif data_source == "cross_app_sync":
            return await self._get_sync_status_data()
        else:
            return {"error": f"Unknown data source: {data_source}"}
    
    async def _get_email_data(self) -> Dict[str, Any]:
        """Get email intelligence data"""
        try:
            if "google" in self.api_manager.clients:
                emails = await self.api_manager.clients["google"].get_emails("is:unread", max_results=10)
                
                # Simulate email analysis
                urgent_count = len([e for e in emails if "urgent" in e.get("subject", "").lower()])
                action_required = len([e for e in emails if any(word in e.get("subject", "").lower() 
                                                              for word in ["action", "request", "please"])])
                
                return {
                    "unread_count": len(emails),
                    "urgent_count": urgent_count,
                    "action_required": action_required,
                    "recent_emails": [
                        {
                            "from": email.get("from", "Unknown")[:20],
                            "subject": email.get("subject", "No Subject")[:30],
                            "time": email.get("date", "")[:10],
                            "priority": "urgent" if "urgent" in email.get("subject", "").lower() else "medium"
                        }
                        for email in emails[:5]
                    ]
                }
            else:
                return {"unread_count": 0, "urgent_count": 0, "action_required": 0, "recent_emails": []}
                
        except Exception as e:
            self.logger.error(f"Failed to get email data: {e}")
            return {"unread_count": 0, "urgent_count": 0, "action_required": 0, "recent_emails": []}
    
    async def _get_calendar_data(self) -> Dict[str, Any]:
        """Get calendar data"""
        try:
            if "google" in self.api_manager.clients:
                events = await self.api_manager.clients["google"].get_calendar_events(max_results=10)
                
                today_events = [
                    event for event in events
                    if datetime.fromisoformat(event["start_time"].replace('Z', '+00:00')).date() == datetime.now().date()
                ]
                
                total_meeting_time = sum([
                    (datetime.fromisoformat(event["end_time"].replace('Z', '+00:00')) - 
                     datetime.fromisoformat(event["start_time"].replace('Z', '+00:00'))).total_seconds() / 3600
                    for event in today_events
                ])
                
                free_time = 8 - total_meeting_time  # Assuming 8-hour workday
                
                return {
                    "events": [
                        {
                            "title": event["title"],
                            "start_time": datetime.fromisoformat(event["start_time"].replace('Z', '+00:00')).strftime("%H:%M"),
                            "location": "Online",  # Simplified
                            "attendee_count": 3  # Simplified
                        }
                        for event in today_events[:5]
                    ],
                    "total_meetings": len(today_events),
                    "free_time": max(0, free_time)
                }
            else:
                return {"events": [], "total_meetings": 0, "free_time": 8}
                
        except Exception as e:
            self.logger.error(f"Failed to get calendar data: {e}")
            return {"events": [], "total_meetings": 0, "free_time": 8}
    
    async def _get_project_health_data(self) -> Dict[str, Any]:
        """Get project health data"""
        try:
            if "git" in self.api_manager.clients:
                repos = await self.api_manager.clients["git"].get_repositories()
                
                if repos:
                    # Get issues for first repository
                    issues = await self.api_manager.clients["git"].get_issues(
                        repos[0]["full_name"], state="open"
                    )
                    
                    # Calculate health score (simplified)
                    health_score = max(1, min(10, 10 - len(issues) * 0.5))
                    
                    if health_score >= 8:
                        health_level = "excellent"
                    elif health_score >= 6:
                        health_level = "good"
                    elif health_score >= 4:
                        health_level = "fair"
                    else:
                        health_level = "poor"
                    
                    return {
                        "health_score": round(health_score, 1),
                        "health_level": health_level,
                        "code_quality": "Good",
                        "open_issues": len(issues),
                        "recent_commits": 15  # Simplified
                    }
                else:
                    return {
                        "health_score": 7.0,
                        "health_level": "good",
                        "code_quality": "Unknown",
                        "open_issues": 0,
                        "recent_commits": 0
                    }
            else:
                return {
                    "health_score": 5.0,
                    "health_level": "fair",
                    "code_quality": "Unknown",
                    "open_issues": 0,
                    "recent_commits": 0
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get project health data: {e}")
            return {
                "health_score": 5.0,
                "health_level": "fair",
                "code_quality": "Error",
                "open_issues": 0,
                "recent_commits": 0
            }
    
    async def _get_ai_insights_data(self) -> Dict[str, Any]:
        """Get AI insights data"""
        try:
            # Generate AI insights based on available data
            insights = [
                {
                    "icon": "⚡",
                    "title": "High Email Volume",
                    "description": "You have 15 unread emails with 3 marked as urgent",
                    "action": "Review urgent emails",
                    "priority": "high"
                },
                {
                    "icon": "📅",
                    "title": "Back-to-back Meetings",
                    "description": "You have 4 consecutive meetings this afternoon",
                    "action": "Add buffer time",
                    "priority": "medium"
                },
                {
                    "icon": "🚀",
                    "title": "Code Quality Improvement",
                    "description": "Recent commits show improved test coverage",
                    "action": "Continue current practices",
                    "priority": "low"
                }
            ]
            
            return {"insights": insights}
            
        except Exception as e:
            self.logger.error(f"Failed to get AI insights data: {e}")
            return {"insights": []}
    
    async def _get_productivity_data(self) -> Dict[str, Any]:
        """Get productivity metrics data"""
        try:
            # Simulate productivity analysis
            return {
                "focus_time": 4.5,
                "meeting_time": 3.0,
                "efficiency": 78,
                "chart_data": {
                    "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
                    "datasets": [{
                        "label": "Focus Time",
                        "data": [4, 5, 3, 6, 4.5],
                        "backgroundColor": "rgba(59, 130, 246, 0.5)"
                    }]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get productivity data: {e}")
            return {"focus_time": 0, "meeting_time": 0, "efficiency": 0}
    
    async def _get_sync_status_data(self) -> Dict[str, Any]:
        """Get synchronization status data"""
        try:
            # Simulate sync status
            return {
                "sync_health": "healthy",
                "sync_health_text": "All systems operational",
                "sync_rules": [
                    {
                        "name": "Calendar to Tasks",
                        "status": "completed",
                        "last_sync": "2 min ago"
                    },
                    {
                        "name": "Email to CRM",
                        "status": "completed",
                        "last_sync": "1 hour ago"
                    },
                    {
                        "name": "Git to Project",
                        "status": "running",
                        "last_sync": "Running..."
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get sync status data: {e}")
            return {"sync_health": "unknown", "sync_health_text": "Status unavailable", "sync_rules": []}
    
    async def _build_dashboard_html(self, widgets: List[DashboardWidget], 
                                  widget_data: Dict[str, Any], theme: str) -> str:
        """Build complete dashboard HTML"""
        theme_css = self.themes.get(theme, self.themes["modern_dark"])["css"]
        
        # Generate widget HTML
        widgets_html = ""
        for widget in widgets:
            widget_html = await self._render_widget(widget, widget_data.get(widget.id, {}))
            widgets_html += widget_html
        
        # Complete HTML template
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>OS Dashboard AI Assistant</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                {theme_css}
            </style>
        </head>
        <body>
            <div class="dashboard-header">
                <h1>🤖 OS Dashboard AI Assistant</h1>
                <div class="last-updated">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
            
            <div class="dashboard-container">
                {widgets_html}
            </div>
            
            <script>
                // Auto-refresh dashboard
                setTimeout(() => {{
                    window.location.reload();
                }}, 300000); // Refresh every 5 minutes
                
                // Initialize charts
                {await self._generate_chart_scripts(widgets, widget_data)}
            </script>
        </body>
        </html>
        """
        
        return html
    
    async def _render_widget(self, widget: DashboardWidget, data: Dict[str, Any]) -> str:
        """Render individual widget HTML"""
        template = self.widget_templates.get(widget.type, {}).get("template", "")
        
        if not template:
            return f'<div class="widget-card"><h3>{widget.title}</h3><p>Widget type not found</p></div>'
        
        # Simple template rendering (in production, use a proper template engine)
        rendered = template
        
        # Replace data placeholders
        for key, value in data.items():
            if isinstance(value, list):
                # Handle list data (like recent_emails, events)
                list_html = ""
                for item in value:
                    if isinstance(item, dict):
                        item_html = template
                        for item_key, item_value in item.items():
                            item_html = item_html.replace(f"{{{{{item_key}}}}}", str(item_value))
                        list_html += item_html
                rendered = rendered.replace(f"{{{{#each {key}}}}}.*?{{{{/each}}}}", list_html)
            else:
                rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        
        # Add widget ID for JavaScript targeting
        rendered = rendered.replace("{{widget_id}}", widget.id)
        
        return rendered
    
    async def _generate_chart_scripts(self, widgets: List[DashboardWidget], 
                                    widget_data: Dict[str, Any]) -> str:
        """Generate JavaScript for charts"""
        scripts = ""
        
        for widget in widgets:
            if widget.type == "chart" or "chart" in widget.type:
                data = widget_data.get(widget.id, {})
                chart_data = data.get("chart_data", {})
                
                if chart_data:
                    scripts += f"""
                    const ctx_{widget.id} = document.getElementById('productivity-chart-{widget.id}');
                    if (ctx_{widget.id}) {{
                        new Chart(ctx_{widget.id}, {{
                            type: 'line',
                            data: {json.dumps(chart_data)},
                            options: {{
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {{
                                    legend: {{
                                        display: false
                                    }}
                                }},
                                scales: {{
                                    y: {{
                                        beginAtZero: true,
                                        grid: {{
                                            color: 'rgba(255, 255, 255, 0.1)'
                                        }},
                                        ticks: {{
                                            color: 'rgba(255, 255, 255, 0.7)'
                                        }}
                                    }},
                                    x: {{
                                        grid: {{
                                            color: 'rgba(255, 255, 255, 0.1)'
                                        }},
                                        ticks: {{
                                            color: 'rgba(255, 255, 255, 0.7)'
                                        }}
                                    }}
                                }}
                            }}
                        }});
                    }}
                    """
        
        return scripts
    
    async def create_default_dashboard(self) -> List[DashboardWidget]:
        """Create default dashboard configuration"""
        return [
            DashboardWidget(
                id="email_summary",
                title="Email Summary",
                type="email_summary",
                size="medium",
                data_source="email_intelligence",
                refresh_interval=300
            ),
            DashboardWidget(
                id="calendar_overview",
                title="Calendar Overview",
                type="calendar_overview",
                size="medium",
                data_source="smart_calendar",
                refresh_interval=300
            ),
            DashboardWidget(
                id="project_health",
                title="Project Health",
                type="project_health",
                size="medium",
                data_source="git_automation",
                refresh_interval=600
            ),
            DashboardWidget(
                id="ai_insights",
                title="AI Insights",
                type="ai_insights",
                size="large",
                data_source="ai_analysis",
                refresh_interval=900
            ),
            DashboardWidget(
                id="productivity_metrics",
                title="Productivity Metrics",
                type="productivity_metrics",
                size="medium",
                data_source="productivity_analysis",
                refresh_interval=600
            ),
            DashboardWidget(
                id="sync_status",
                title="Sync Status",
                type="sync_status",
                size="small",
                data_source="cross_app_sync",
                refresh_interval=180
            )
        ]
    
    async def save_dashboard_to_file(self, widgets: List[DashboardWidget], 
                                   theme: str = "modern_dark", 
                                   filename: str = "dashboard.html") -> str:
        """Save dashboard to HTML file"""
        try:
            html = await self.generate_dashboard_html(widgets, theme)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
            
            self.logger.info(f"Dashboard saved to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to save dashboard: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown dashboard UI system"""
        self.logger.info("Dashboard UI system shutdown")