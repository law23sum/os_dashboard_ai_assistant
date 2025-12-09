"""End-to-end style tests for salvaged advanced features."""

import unittest
from datetime import datetime, timedelta

from assistant_core.advanced_productivity import (
    CalendarEvent,
    CrossAppSyncLite,
    EmailIntelligenceEngine,
    OfficeAutomationLite,
    ProductivitySuite,
    SmartCalendarOptimizer,
)
from assistant_core.advanced_productivity import EmailPriority, EmailCategory


class TestEmailIntelligence(unittest.TestCase):
    def test_email_analysis_sets_priority_and_category(self):
        engine = EmailIntelligenceEngine()
        email = {"subject": "Urgent meeting request", "body": "Please join ASAP", "from": "team@example.com"}

        insight = engine.analyze_email(email)

        self.assertEqual(insight.priority, EmailPriority.URGENT)
        self.assertEqual(insight.category, EmailCategory.MEETING)
        self.assertTrue(insight.action_required)
        self.assertIsNotNone(insight.suggested_response)


class TestSmartCalendar(unittest.TestCase):
    def test_detects_overlap_and_buffer_conflicts(self):
        optimizer = SmartCalendarOptimizer()
        now = datetime.utcnow()
        events = [
            CalendarEvent(id="1", title="Standup", start_time=now, end_time=now + timedelta(minutes=30)),
            CalendarEvent(id="2", title="Planning", start_time=now + timedelta(minutes=20), end_time=now + timedelta(minutes=70)),
            CalendarEvent(id="3", title="Retro", start_time=now + timedelta(minutes=75), end_time=now + timedelta(minutes=95)),
        ]

        conflicts = optimizer.detect_conflicts(events)
        self.assertGreater(len(conflicts), 0)
        self.assertTrue(any(c.conflict_type.name in {"OVERLAP", "BACK_TO_BACK"} for c in conflicts))


class TestCrossAppSync(unittest.TestCase):
    def test_calendar_to_task_mapping(self):
        sync = CrossAppSyncLite()
        now = datetime.utcnow().isoformat()
        data = [{"title": "Finish doc", "start_time": now, "description": "task", "event_type": "task"}]

        result = sync.execute_rule("Calendar to Task Sync", data)

        self.assertEqual(result["synced_records"], 1)
        mapped = result["records"][0]
        self.assertEqual(mapped["subject"], "Finish doc")
        self.assertIn("due_date", mapped)


class TestOfficeAutomation(unittest.TestCase):
    def test_renders_meeting_template(self):
        office = OfficeAutomationLite()
        content = office.render_template(
            "meeting_notes",
            {
                "meeting_title": "Weekly Sync",
                "date": "2024-01-01",
                "attendees": "Team",
                "duration": "60m",
                "agenda": "Status",
                "discussion": "- item",
                "action_items": "- do thing",
                "next_steps": "Follow up",
            },
        )

        self.assertIn("Weekly Sync", content)
        self.assertIn("Status", content)
        self.assertIn("Follow up", content)


class TestProductivitySuite(unittest.TestCase):
    def test_run_e2e_returns_dashboard(self):
        suite = ProductivitySuite()
        result = suite.run_e2e()

        self.assertIn("email", result)
        self.assertIn("calendar", result)
        self.assertIn("dashboard_html", result)
        self.assertTrue(result["dashboard_html"].startswith("<div class='dashboard'>"))
        self.assertGreaterEqual(result["calendar"]["conflicts_found"], 0)


if __name__ == "__main__":
    unittest.main()


