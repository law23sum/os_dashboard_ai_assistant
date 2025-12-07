"""
Tests for the Audit and Governance System
"""

import unittest
import asyncio
import tempfile
from datetime import datetime, timedelta

from assistant_core.audit_system import (
    AuditSystem,
    AuditEvent,
    AuditEventType,
    AuditLevel,
    ComplianceFramework,
    ComplianceRule,
    DataLineage
)


class TestAuditSystem(unittest.TestCase):
    """Test cases for the audit system"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.audit_system = AuditSystem(storage_path=self.temp_dir)

    async def asyncSetUp(self):
        """Async set up"""
        await self.audit_system.initialize(enable_git=False)

    def test_log_event(self):
        """Test logging audit events"""
        async def run_test():
            await self.asyncSetUp()
            event_id = await self.audit_system.log_event(
                event_type=AuditEventType.USER_LOGIN,
                action="test_login",
                user_id="test_user",
                session_id="session_123",
                details={"ip": "127.0.0.1"}
            )

            self.assertIsNotNone(event_id)
            self.assertIsInstance(event_id, str)

        asyncio.run(run_test())

    def test_get_audit_trail(self):
        """Test retrieving audit trail"""
        async def run_test():
            await self.asyncSetUp()
            # Log some events
            start_date = datetime.utcnow() - timedelta(hours=1)
            await self.audit_system.log_event(
                AuditEventType.USER_LOGIN,
                "login",
                user_id="user1",
                session_id="session_123"
            )
            await self.audit_system.log_event(
                AuditEventType.RESOURCE_READ,
                "read_file",
                user_id="user1",
                session_id="session_123",
                resource_id="file.txt"
            )
            end_date = datetime.utcnow() + timedelta(hours=1)

            # Retrieve events
            events = await self.audit_system.get_audit_trail(start_date, end_date)

            self.assertEqual(len(events), 2)
            self.assertEqual(events[0].event_type, AuditEventType.USER_LOGIN)
            self.assertEqual(events[1].event_type, AuditEventType.RESOURCE_READ)

        asyncio.run(run_test())

    def test_event_filters(self):
        """Test event filtering"""
        async def run_test():
            await self.asyncSetUp()
            start_date = datetime.utcnow() - timedelta(hours=1)

            await self.audit_system.log_event(
                AuditEventType.USER_LOGIN,
                "login",
                user_id="user1",
                session_id="session_123"
            )
            await self.audit_system.log_event(
                AuditEventType.USER_LOGIN,
                "login",
                user_id="user2",
                session_id="session_456"
            )

            end_date = datetime.utcnow() + timedelta(hours=1)

            # Filter by user
            events = await self.audit_system.get_audit_trail(
                start_date, end_date,
                filters={"user_id": "user1"}
            )

            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].user_id, "user1")

        asyncio.run(run_test())

    def test_data_lineage_tracking(self):
        """Test data lineage tracking"""
        async def run_test():
            await self.asyncSetUp()
            await self.audit_system.track_data_lineage(
                resource_id="processed_data.csv",
                connector_name="file_connector",
                source_resources=["raw_data.csv", "config.json"],
                transformations=[
                    {"type": "filter", "params": {"column": "status", "value": "active"}},
                    {"type": "aggregate", "params": {"group_by": "category"}}
                ]
            )

            # Check that lineage was tracked
            self.assertIn("processed_data.csv", self.audit_system.lineage_tracker)
            lineage = self.audit_system.lineage_tracker["processed_data.csv"]
            self.assertEqual(lineage.connector_name, "file_connector")
            self.assertEqual(len(lineage.source_resources), 2)
            self.assertEqual(len(lineage.transformations), 2)

        asyncio.run(run_test())

    def test_compliance_rule_creation(self):
        """Test compliance rule creation"""
        async def run_test():
            await self.asyncSetUp()
            rule = ComplianceRule(
                rule_id="test_rule_001",
                framework=ComplianceFramework.GDPR,
                name="Test Data Retention Rule",
                description="Test rule for data retention",
                rule_type="data_retention",
                config={"max_retention_days": 365}
            )

            await self.audit_system.compliance_engine.add_rule(rule)

            # Check rule was added
            self.assertIn(rule.rule_id, self.audit_system.compliance_engine.rules)
            self.assertEqual(
                self.audit_system.compliance_engine.rules[rule.rule_id].name,
                "Test Data Retention Rule"
            )

        asyncio.run(run_test())

    def test_system_statistics(self):
        """Test system statistics generation"""
        async def run_test():
            await self.asyncSetUp()
            # Log some events
            await self.audit_system.log_event(AuditEventType.USER_LOGIN, "login", user_id="user1", session_id="session_123")
            await self.audit_system.log_event(AuditEventType.RESOURCE_READ, "read", user_id="user1", session_id="session_123")

            stats = await self.audit_system.get_system_statistics()

            self.assertIn("total_events_30_days", stats)
            self.assertIn("event_type_distribution", stats)
            self.assertIn("compliance_rules", stats)
            self.assertEqual(stats["total_events_30_days"], 2)
            self.assertIn("user_login", stats["event_type_distribution"])
            self.assertIn("resource_read", stats["event_type_distribution"])

        asyncio.run(run_test())


class TestAuditStorage(unittest.TestCase):
    """Test cases for audit storage"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        from assistant_core.audit_system import AuditStorage
        self.storage = AuditStorage(self.temp_dir)

    def test_event_storage_and_retrieval(self):
        """Test storing and retrieving events"""
        async def run_test():
            event = AuditEvent(
                event_id="test_event_001",
                event_type=AuditEventType.USER_LOGIN,
                timestamp=datetime.utcnow(),
                user_id="test_user",
                session_id="session_123",
                action="login",
                details={"success": True}
            )

            # Store event
            await self.storage.store_event(event)

            # Retrieve events
            start_date = datetime.utcnow() - timedelta(hours=1)
            end_date = datetime.utcnow() + timedelta(hours=1)
            events = await self.storage.get_events(start_date, end_date)

            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].event_id, "test_event_001")
            self.assertEqual(events[0].user_id, "test_user")

        asyncio.run(run_test())


class TestComplianceEngine(unittest.TestCase):
    """Test cases for compliance engine"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        from assistant_core.audit_system import AuditStorage, ComplianceEngine
        self.storage = AuditStorage(self.temp_dir)
        self.compliance_engine = ComplianceEngine(self.storage)

    def test_compliance_rule_validation(self):
        """Test compliance rule validation"""
        async def run_test():
            await self.compliance_engine.load_rules()

            event = AuditEvent(
                event_id="test_event",
                event_type=AuditEventType.RESOURCE_READ,
                timestamp=datetime.utcnow(),
                user_id="unauthorized_user",
                session_id="session_123",
                connector_name="test_connector",
                action="read",
                resource_id="sensitive_file.txt",
                details={}
            )

            # Add a test rule
            rule = ComplianceRule(
                rule_id="access_test",
                framework=ComplianceFramework.GDPR,
                name="Access Control Test",
                description="Test access control",
                rule_type="access_control",
                config={
                    "allowed_users": ["authorized_user"],
                    "restricted_resources": ["sensitive_file.txt"]
                }
            )

            await self.compliance_engine.add_rule(rule)

            # Check compliance
            violations = await self.compliance_engine.check_compliance(event)

            self.assertEqual(len(violations), 1)
            self.assertEqual(violations[0].rule_id, "access_test")
            self.assertIn("access control violation", violations[0].description.lower())

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
