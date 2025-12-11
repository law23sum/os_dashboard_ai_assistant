"""
Lightweight implementations of the advanced productivity features found in the
reference folder. These classes are adapted to run locally without external
APIs so we can exercise the end-to-end flows in tests.

Features included (salvaged and simplified from reference code):
- Email intelligence (priority/category/sentiment plus suggested response)
- Smart calendar conflict detection and schedule insights
- Office automation templates and AI-style meeting note generation
- Git workflow health analysis and changelog generation
- Cross-application synchronization with field mapping and transformations
- Dashboard builder that stitches the above outputs together
"""

from __future__ import annotations

import json
import re
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


# ---------------------------------------------------------------------------
# Email Intelligence (salvaged from reference/advanced/email_intelligence.py)
# ---------------------------------------------------------------------------


class EmailPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class EmailCategory(Enum):
    WORK = "work"
    PERSONAL = "personal"
    MARKETING = "marketing"
    NEWSLETTER = "newsletter"
    SUPPORT = "support"
    MEETING = "meeting"
    ACTION_REQUIRED = "action_required"
    FYI = "fyi"


@dataclass
class EmailInsight:
    priority: EmailPriority
    category: EmailCategory
    sentiment: str
    action_required: bool
    estimated_response_time: int
    key_topics: List[str] = field(default_factory=list)
    suggested_response: Optional[str] = None
    confidence_score: float = 0.7


class EmailIntelligenceEngine:
    """AI-inspired email processing without remote API calls."""

    def __init__(self):
        self.templates = {
            "support_acknowledgment": "Thanks for reaching out. We received your request and will follow up shortly.",
            "default": "Thank you for the email. I'll review this and respond soon.",
        }

    def analyze_email(self, email_data: Dict[str, Any]) -> EmailInsight:
        subject = email_data.get("subject", "")
        body = email_data.get("body", "")
        sender = email_data.get("from", "")

        # Heuristic analysis adapted from reference fallback parser
        content_lower = f"{subject} {body}".lower()

        if any(word in content_lower for word in ["urgent", "asap", "immediately"]):
            priority = EmailPriority.URGENT
        elif any(word in content_lower for word in ["important", "priority"]):
            priority = EmailPriority.HIGH
        elif any(word in content_lower for word in ["fyi", "update"]):
            priority = EmailPriority.LOW
        else:
            priority = EmailPriority.MEDIUM

        if any(word in content_lower for word in ["meeting", "schedule", "calendar"]):
            category = EmailCategory.MEETING
        elif any(word in content_lower for word in ["newsletter", "unsubscribe"]):
            category = EmailCategory.NEWSLETTER
        elif any(word in content_lower for word in ["support", "help", "issue"]):
            category = EmailCategory.SUPPORT
        elif any(
            word in content_lower for word in ["action", "please", "need", "request"]
        ):
            category = EmailCategory.ACTION_REQUIRED
        else:
            category = EmailCategory.WORK

        sentiment = (
            "positive"
            if any(word in content_lower for word in ["thank", "great", "awesome"])
            else "neutral"
        )
        action_required = category in {
            EmailCategory.ACTION_REQUIRED,
            EmailCategory.MEETING,
            EmailCategory.SUPPORT,
        }
        response_time = (
            30 if priority in {EmailPriority.URGENT, EmailPriority.HIGH} else 90
        )
        topics = self._extract_topics(subject, body)

        insight = EmailInsight(
            priority=priority,
            category=category,
            sentiment=sentiment,
            action_required=action_required,
            estimated_response_time=response_time,
            key_topics=topics,
            confidence_score=0.78 if priority == EmailPriority.URGENT else 0.65,
        )

        if action_required:
            insight.suggested_response = self._generate_response(email_data, insight)

        return insight

    def process_inbox(self, emails: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        processed = []
        categories: Dict[str, List[Dict[str, Any]]] = {}
        urgent = []
        action_required = []

        for email in emails:
            insight = self.analyze_email(email)
            record = {
                "email": email,
                "insight": insight,
                "processed_at": datetime.utcnow().isoformat(),
            }
            processed.append(record)

            categories.setdefault(insight.category.value, []).append(record)
            if insight.priority == EmailPriority.URGENT:
                urgent.append(record)
            if insight.action_required:
                action_required.append(record)

        summary = {
            "total": len(processed),
            "by_category": {k: len(v) for k, v in categories.items()},
            "urgent": len(urgent),
            "action_required": len(action_required),
        }

        summary_text = (
            f"Processed {summary['total']} emails | "
            f"Urgent: {summary['urgent']} | Action required: {summary['action_required']}"
        )

        return {
            "processed": processed,
            "categories": categories,
            "summary": summary,
            "summary_text": summary_text,
        }

    def _extract_topics(self, subject: str, body: str) -> List[str]:
        tokens = re.findall(r"[a-zA-Z]{4,}", f"{subject} {body}".lower())
        common = []
        for token in tokens:
            if token not in common and tokens.count(token) > 1:
                common.append(token)
        return common[:5]

    def _generate_response(self, email: Dict[str, Any], insight: EmailInsight) -> str:
        if insight.category == EmailCategory.SUPPORT:
            template = self.templates["support_acknowledgment"]
        else:
            template = self.templates["default"]

        sender = email.get("from", "there")
        return f"Hi {sender}, {template}"


# ---------------------------------------------------------------------------
# Smart Calendar (salvaged from reference/advanced/smart_calendar.py)
# ---------------------------------------------------------------------------


class EventType(Enum):
    MEETING = "meeting"
    APPOINTMENT = "appointment"
    TASK = "task"
    BREAK = "break"
    TRAVEL = "travel"
    PERSONAL = "personal"
    WORK = "work"
    FOCUS_TIME = "focus_time"


class ConflictType(Enum):
    OVERLAP = "overlap"
    BACK_TO_BACK = "back_to_back"
    WORKLOAD = "workload"
    PREFERENCE = "preference"


@dataclass
class CalendarEvent:
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    description: str = ""
    location: str = ""
    attendees: List[str] = field(default_factory=list)
    event_type: EventType = EventType.MEETING
    priority: int = 5
    travel_time: int = 0
    ai_generated: bool = False


@dataclass
class SchedulingConflict:
    conflict_type: ConflictType
    events: List[CalendarEvent]
    severity: int
    suggestion: str
    auto_resolvable: bool = False


@dataclass
class SchedulingPreferences:
    work_hours_start: int = 9
    work_hours_end: int = 17
    buffer_minutes: int = 15
    max_meetings_per_day: int = 8
    lunch_start: int = 12
    lunch_end: int = 13


class SmartCalendarOptimizer:
    """Detect conflicts and suggest improvements using local logic."""

    def __init__(self, preferences: Optional[SchedulingPreferences] = None):
        self.preferences = preferences or SchedulingPreferences()

    def detect_conflicts(
        self, events: Sequence[CalendarEvent]
    ) -> List[SchedulingConflict]:
        conflicts: List[SchedulingConflict] = []
        events_sorted = sorted(events, key=lambda e: e.start_time)

        # Overlaps
        for i, current in enumerate(events_sorted):
            for other in events_sorted[i + 1 :]:
                if current.end_time <= other.start_time:
                    break
                conflicts.append(
                    SchedulingConflict(
                        conflict_type=ConflictType.OVERLAP,
                        events=[current, other],
                        severity=9,
                        suggestion=f"Reschedule '{current.title}' or '{other.title}' to remove overlap",
                        auto_resolvable=False,
                    )
                )

        # Back-to-back without buffer
        for first, second in zip(events_sorted, events_sorted[1:]):
            gap = (second.start_time - first.end_time).total_seconds() / 60
            if 0 <= gap < (self.preferences.buffer_minutes + first.travel_time):
                missing = (self.preferences.buffer_minutes + first.travel_time) - gap
                conflicts.append(
                    SchedulingConflict(
                        conflict_type=ConflictType.BACK_TO_BACK,
                        events=[first, second],
                        severity=6,
                        suggestion=f"Add {missing:.0f} minutes buffer before '{second.title}'",
                        auto_resolvable=True,
                    )
                )

        # Workload per day
        by_day: Dict[str, List[CalendarEvent]] = {}
        for event in events_sorted:
            key = event.start_time.date().isoformat()
            by_day.setdefault(key, []).append(event)
        for day, day_events in by_day.items():
            if len(day_events) > self.preferences.max_meetings_per_day:
                conflicts.append(
                    SchedulingConflict(
                        conflict_type=ConflictType.WORKLOAD,
                        events=day_events,
                        severity=7,
                        suggestion=f"{day} has {len(day_events)} meetings (max {self.preferences.max_meetings_per_day})",
                        auto_resolvable=False,
                    )
                )

        # Preference violations (outside work hours or during lunch)
        for event in events_sorted:
            hour = event.start_time.hour
            if (
                hour < self.preferences.work_hours_start
                or hour >= self.preferences.work_hours_end
            ):
                conflicts.append(
                    SchedulingConflict(
                        conflict_type=ConflictType.PREFERENCE,
                        events=[event],
                        severity=4,
                        suggestion="Event is outside preferred work hours",
                        auto_resolvable=True,
                    )
                )
            if self.preferences.lunch_start <= hour < self.preferences.lunch_end:
                conflicts.append(
                    SchedulingConflict(
                        conflict_type=ConflictType.PREFERENCE,
                        events=[event],
                        severity=3,
                        suggestion="Event overlaps lunch window",
                        auto_resolvable=True,
                    )
                )

        return conflicts

    def summarize_day(self, events: Sequence[CalendarEvent]) -> Dict[str, Any]:
        if not events:
            return {"total_meetings": 0, "focus_time_hours": 8, "busy_hours": 0}

        duration_hours = (
            sum((e.end_time - e.start_time).total_seconds() for e in events) / 3600
        )
        focus_time = max(
            0,
            (self.preferences.work_hours_end - self.preferences.work_hours_start)
            - duration_hours,
        )

        return {
            "total_meetings": len(events),
            "busy_hours": round(duration_hours, 2),
            "focus_time_hours": round(focus_time, 2),
        }


# ---------------------------------------------------------------------------
# Office Automation (salvaged from reference/advanced/office_automation.py)
# ---------------------------------------------------------------------------


@dataclass
class DocumentTemplate:
    name: str
    type: str
    template_content: str
    variables: List[str]
    description: str


class OfficeAutomationLite:
    """Template rendering and meeting note generation without Microsoft APIs."""

    def __init__(self):
        self.templates = self._load_templates()

    def render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        content = self.templates[template_name].template_content
        for key, value in variables.items():
            content = content.replace(f"{{{key}}}", str(value))
        return content.strip()

    def generate_meeting_notes(
        self, transcript: str, meeting_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Simplified extraction (mirrors reference fallback)
        lines = [l.strip() for l in transcript.splitlines() if l.strip()]
        action_items = [l for l in lines if l.lower().startswith("action")]
        discussion = [l for l in lines if l not in action_items]

        variables = {
            "meeting_title": meeting_info.get("title", "Meeting"),
            "date": meeting_info.get("date", datetime.utcnow().date().isoformat()),
            "attendees": meeting_info.get("attendees", "Unknown"),
            "duration": meeting_info.get("duration", "60m"),
            "agenda": meeting_info.get("agenda", "n/a"),
            "discussion": "\n".join(f"- {d}" for d in discussion) or "None captured",
            "action_items": "\n".join(f"- {a}" for a in action_items)
            or "None captured",
            "next_steps": meeting_info.get("next_steps", "Follow up with attendees"),
        }

        document = self.render_template("meeting_notes", variables)
        return {
            "document": document,
            "extracted_info": {"action_items": action_items, "discussion": discussion},
        }

    def _load_templates(self) -> Dict[str, DocumentTemplate]:
        return {
            "meeting_notes": DocumentTemplate(
                name="Meeting Notes",
                type="word",
                template_content=(
                    "# Meeting Notes - {meeting_title}\n\n"
                    "**Date:** {date}\n"
                    "**Attendees:** {attendees}\n"
                    "**Duration:** {duration}\n\n"
                    "## Agenda\n"
                    "{agenda}\n\n"
                    "## Discussion Points\n"
                    "{discussion}\n\n"
                    "## Action Items\n"
                    "{action_items}\n\n"
                    "## Next Steps\n"
                    "{next_steps}\n"
                ),
                variables=[
                    "meeting_title",
                    "date",
                    "attendees",
                    "duration",
                    "agenda",
                    "discussion",
                    "action_items",
                    "next_steps",
                ],
                description="Standard meeting notes template from reference",
            )
        }


# ---------------------------------------------------------------------------
# Git Workflow Automation (salvaged from reference/advanced/git_workflow_automation.py)
# ---------------------------------------------------------------------------


@dataclass
class CodeAnalysis:
    quality_score: float
    complexity_score: float
    maintainability: str
    security_issues: List[str]
    performance_issues: List[str]
    suggestions: List[str]
    test_coverage_estimate: float


class GitWorkflowAutomationLite:
    """Static analysis style heuristics inspired by reference Git automation."""

    def analyze_code_changes(self, changes: Dict[str, Any]) -> CodeAnalysis:
        files_changed = changes.get("files_changed", 0)
        total_lines = changes.get("total_lines", 0)
        file_types = changes.get("file_types", [])

        complexity_score = min(10.0, 3 + files_changed * 0.5 + (total_lines / 500))
        quality_score = max(4.0, 10.0 - complexity_score * 0.6)
        maintainability = "good" if quality_score >= 7 else "fair"

        suggestions = []
        if files_changed > 10:
            suggestions.append("Consider breaking changes into smaller PRs.")
        if total_lines > 1000:
            suggestions.append("Large change detected; add regression tests.")
        if ".py" in file_types:
            suggestions.append("Run linters and formatters for Python changes.")

        security_issues = (
            ["Review authentication paths"]
            if "auth" in json.dumps(changes).lower()
            else []
        )
        performance_issues = ["Profile heavy loops"] if total_lines > 800 else []

        return CodeAnalysis(
            quality_score=round(quality_score, 2),
            complexity_score=round(complexity_score, 2),
            maintainability=maintainability,
            security_issues=security_issues,
            performance_issues=performance_issues,
            suggestions=suggestions,
            test_coverage_estimate=round(max(40.0, 95.0 - files_changed * 2), 2),
        )

    def generate_changelog(self, commits: Sequence[Dict[str, Any]]) -> str:
        entries = []
        for commit in commits:
            message = commit.get("message", "update").strip()
            sha = commit.get("sha", "")[:7]
            entries.append(f"- {message} ({sha})")
        return "\n".join(entries)

    def project_health(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        analysis = self.analyze_code_changes(changes)
        health_score = statistics.mean(
            [analysis.quality_score, 10 - analysis.complexity_score]
        )
        return {
            "health_score": round(health_score, 2),
            "open_issues": changes.get("open_issues", 0),
            "recent_commits": changes.get("recent_commits", 0),
            "code_quality": analysis.maintainability,
        }


# ---------------------------------------------------------------------------
# Cross-App Synchronization (salvaged from reference/workflows/cross_app_sync.py)
# ---------------------------------------------------------------------------


@dataclass
class SyncRule:
    name: str
    source_app: str
    target_app: str
    data_type: str
    field_mapping: Dict[str, str]
    transformations: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


class CrossAppSyncLite:
    """Field mapping and transformation utilities inspired by reference sync rules."""

    def __init__(self):
        self.rules = self._default_rules()

    def execute_rule(
        self, rule_name: str, source_data: Sequence[Dict[str, Any]]
    ) -> Dict[str, Any]:
        rule = next((r for r in self.rules if r.name == rule_name), None)
        if not rule:
            raise ValueError(f"Sync rule '{rule_name}' not found")
        if not rule.enabled:
            return {"status": "disabled", "records": []}

        filtered = [
            item for item in source_data if self._matches_filters(item, rule.filters)
        ]
        transformed = self._apply_transformations(filtered, rule.transformations)
        mapped = [self._map_fields(item, rule.field_mapping) for item in transformed]

        return {
            "rule": rule.name,
            "source_records": len(source_data),
            "synced_records": len(mapped),
            "records": mapped,
        }

    def _matches_filters(self, item: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        for key, value in filters.items():
            if item.get(key) != value:
                return False
        return True

    def _apply_transformations(
        self, data: Sequence[Dict[str, Any]], transformations: Sequence[str]
    ) -> List[Dict[str, Any]]:
        result = [dict(item) for item in data]
        for t in transformations:
            if t == "convert_datetime_format":
                for item in result:
                    for key, val in list(item.items()):
                        if isinstance(val, str) and re.match(
                            r"\d{4}-\d{2}-\d{2}T", val
                        ):
                            item[key] = datetime.fromisoformat(
                                val.replace("Z", "+00:00")
                            ).strftime("%Y-%m-%d %H:%M:%S")
            elif t == "deduplicate":
                seen = set()
                unique = []
                for item in result:
                    marker = json.dumps(item, sort_keys=True)
                    if marker not in seen:
                        unique.append(item)
                        seen.add(marker)
                result = unique
        return result

    def _map_fields(
        self, item: Dict[str, Any], mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        mapped = {}
        for source, target in mapping.items():
            if source in item:
                mapped[target] = item[source]
        return mapped

    def _default_rules(self) -> List[SyncRule]:
        return [
            SyncRule(
                name="Calendar to Task Sync",
                source_app="calendar",
                target_app="tasks",
                data_type="events",
                field_mapping={
                    "title": "subject",
                    "start_time": "due_date",
                    "description": "body",
                },
                transformations=["convert_datetime_format"],
                filters={"event_type": "task"},
            )
        ]


# ---------------------------------------------------------------------------
# Dashboard Builder (salvaged from reference/ui/dashboard_components.py)
# ---------------------------------------------------------------------------


class DashboardBuilder:
    """Generate a compact HTML summary for e2e verification."""

    def build_dashboard(
        self,
        email_summary: Dict[str, Any],
        calendar_summary: Dict[str, Any],
        git_health: Dict[str, Any],
        sync_result: Dict[str, Any],
    ) -> str:
        widgets = [
            f"<section id='email'><h3>Email Summary</h3><p>{email_summary['summary_text']}</p></section>",
            (
                "<section id='calendar'><h3>Calendar</h3>"
                f"<p>Meetings: {calendar_summary['total_meetings']} | Busy: {calendar_summary['busy_hours']}h | "
                f"Focus: {calendar_summary['focus_time_hours']}h</p></section>"
            ),
            (
                "<section id='git'><h3>Project Health</h3>"
                f"<p>Health: {git_health['health_score']} / Code quality: {git_health['code_quality']}</p></section>"
            ),
            (
                "<section id='sync'><h3>Sync</h3>"
                f"<p>Rule '{sync_result['rule']}' synced {sync_result['synced_records']} of "
                f"{sync_result['source_records']} records.</p></section>"
            ),
        ]
        return "<div class='dashboard'>" + "".join(widgets) + "</div>"


# ---------------------------------------------------------------------------
# End-to-end helper
# ---------------------------------------------------------------------------


class ProductivitySuite:
    """Bundles the salvaged components to run an end-to-end demo in tests."""

    def __init__(self):
        self.email = EmailIntelligenceEngine()
        self.calendar = SmartCalendarOptimizer()
        self.office = OfficeAutomationLite()
        self.git = GitWorkflowAutomationLite()
        self.sync = CrossAppSyncLite()
        self.dashboard = DashboardBuilder()

    def run_e2e(self) -> Dict[str, Any]:
        # Sample inputs kept small for test performance
        emails = [
            {
                "subject": "Urgent meeting request",
                "body": "Please join ASAP to discuss launch",
                "from": "product@corp",
            },
            {
                "subject": "Weekly newsletter",
                "body": "Unsubscribe if not interested",
                "from": "news@corp",
            },
        ]
        email_result = self.email.process_inbox(emails)

        now = datetime.utcnow()
        events = [
            CalendarEvent(
                id="1",
                title="Standup",
                start_time=now,
                end_time=now + timedelta(minutes=30),
            ),
            CalendarEvent(
                id="2",
                title="Design review",
                start_time=now + timedelta(minutes=20),
                end_time=now + timedelta(minutes=80),
            ),
        ]
        conflicts = self.calendar.detect_conflicts(events)
        calendar_summary = self.calendar.summarize_day(events)
        calendar_summary["conflicts_found"] = len(conflicts)

        transcript = (
            "Discussion: roadmap updates\nAction: send summary\nAction: prepare slides"
        )
        meeting_doc = self.office.generate_meeting_notes(
            transcript, {"title": "Weekly Sync", "attendees": "Team"}
        )

        git_changes = {
            "files_changed": 4,
            "total_lines": 320,
            "file_types": [".py"],
            "recent_commits": 3,
        }
        git_health = self.git.project_health(git_changes)

        sync_data = [
            {
                "title": "Finish report",
                "start_time": now.isoformat(),
                "description": "task item",
                "event_type": "task",
            },
            {
                "title": "Team lunch",
                "start_time": now.isoformat(),
                "description": "social",
                "event_type": "personal",
            },
        ]
        sync_result = self.sync.execute_rule("Calendar to Task Sync", sync_data)

        dashboard_html = self.dashboard.build_dashboard(
            email_result, calendar_summary, git_health, sync_result
        )

        return {
            "email": email_result,
            "calendar": calendar_summary,
            "conflicts": conflicts,
            "meeting_doc": meeting_doc,
            "git": git_health,
            "sync": sync_result,
            "dashboard_html": dashboard_html,
        }
