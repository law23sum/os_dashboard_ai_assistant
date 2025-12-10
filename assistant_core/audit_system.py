"""

Audit and Governance System with Git Integration

Provides comprehensive audit trails, compliance tracking, and version control integration

"""

import asyncio

from typing import List, Dict, Any, Optional, Union, Callable

from datetime import datetime, timedelta

from dataclasses import dataclass, asdict

from enum import Enum

import json

import hashlib

import uuid

from pathlib import Path

import logging

import subprocess

from config.logging_config import setup_logger

from assistant_core.cir.schema import (
    CIRDocument,
    ContentType,
    SourceSystem,
    ProvenanceEvent as Provenance,
)
from api_connectors.universal_connector import (
    BaseConnector,
    OperationResult,
    GitConnector,
)


class AuditEventType(Enum):
    """Types of audit events"""

    RESOURCE_READ = "resource_read"
    RESOURCE_WRITE = "resource_write"
    RESOURCE_CREATE = "resource_create"
    RESOURCE_DELETE = "resource_delete"
    WORKFLOW_EXECUTE = "workflow_execute"
    SEARCH_QUERY = "search_query"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PERMISSION_CHANGE = "permission_change"
    SYSTEM_CONFIG = "system_config"
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"
    COMPLIANCE_CHECK = "compliance_check"
    SECURITY_EVENT = "security_event"


class AuditLevel(Enum):
    """Audit event severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""

    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    CUSTOM = "custom"


@dataclass
@dataclass
class AuditEvent:
    """Individual audit event record"""

    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    action: str
    details: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    connector_name: Optional[str] = None
    resource_id: Optional[str] = None
    level: AuditLevel = AuditLevel.INFO
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    data_hash: Optional[str] = None

    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


@dataclass
class ComplianceRule:
    """Compliance rule definition"""

    rule_id: str
    framework: ComplianceFramework
    name: str
    description: str
    rule_type: str  # 'data_retention', 'access_control', 'encryption', etc.
    config: Dict[str, Any]
    enabled: bool = True
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class ComplianceViolation:
    """Compliance violation record"""

    violation_id: str
    rule_id: str
    event_id: str
    severity: AuditLevel
    description: str
    detected_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    def __post_init__(self):
        if not self.violation_id:
            self.violation_id = str(uuid.uuid4())
        if not self.detected_at:
            self.detected_at = datetime.utcnow()


@dataclass
class DataLineage:
    """Data lineage tracking"""

    lineage_id: str
    resource_id: str
    connector_name: str
    source_resources: List[str]
    transformations: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        if not self.lineage_id:
            self.lineage_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.updated_at:
            self.updated_at = datetime.utcnow()


class AuditStorage:
    """Storage backend for audit events"""

    def __init__(self, storage_path: str = "audit_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        # Create subdirectories
        (self.storage_path / "events").mkdir(exist_ok=True)
        (self.storage_path / "compliance").mkdir(exist_ok=True)
        (self.storage_path / "lineage").mkdir(exist_ok=True)

        self.events_cache = {}  # In-memory cache for recent events
        self.cache_size = 10000

    async def store_event(self, event: AuditEvent):
        """Store audit event"""
        # Store in daily files for efficient querying
        date_str = event.timestamp.strftime("%Y-%m-%d")
        events_file = self.storage_path / "events" / f"{date_str}.jsonl"

        # Serialize event
        event_data = asdict(event)
        event_data["timestamp"] = event.timestamp.isoformat()
        event_data["event_type"] = event.event_type.value  # Convert enum to string
        event_data["level"] = event.level.value  # Convert enum to string

        # Append to file
        with open(events_file, "a") as f:
            f.write(json.dumps(event_data) + "\n")

        # Add to cache
        self.events_cache[event.event_id] = event

        # Trim cache if too large
        if len(self.events_cache) > self.cache_size:
            # Remove oldest entries
            sorted_events = sorted(
                self.events_cache.items(), key=lambda x: x[1].timestamp
            )
            for event_id, _ in sorted_events[: len(sorted_events) - self.cache_size]:
                del self.events_cache[event_id]

    async def get_events(
        self, start_date: datetime, end_date: datetime, filters: Dict[str, Any] = None
    ) -> List[AuditEvent]:
        """Retrieve audit events within date range"""
        events = []

        # Generate list of dates to check
        current_date = start_date.date()
        end_date_only = end_date.date()

        while current_date <= end_date_only:
            date_str = current_date.strftime("%Y-%m-%d")
            events_file = self.storage_path / "events" / f"{date_str}.jsonl"

            if events_file.exists():
                with open(events_file, "r") as f:
                    for line in f:
                        try:
                            event_data = json.loads(line.strip())
                            event = self._deserialize_event(event_data)

                            # Check if event is within time range
                            if start_date <= event.timestamp <= end_date:
                                # Apply filters
                                if self._event_matches_filters(event, filters):
                                    events.append(event)
                        except Exception:
                            continue

            current_date += timedelta(days=1)

        return events

    async def store_compliance_rule(self, rule: ComplianceRule):
        """Store compliance rule"""
        rules_file = self.storage_path / "compliance" / "rules.json"

        # Load existing rules
        rules = {}
        if rules_file.exists():
            with open(rules_file, "r") as f:
                rules = json.load(f)

        # Add/update rule
        rule_data = asdict(rule)
        rule_data["created_at"] = rule.created_at.isoformat()
        rule_data["framework"] = rule.framework.value  # Convert enum to string
        rules[rule.rule_id] = rule_data

        # Save rules
        with open(rules_file, "w") as f:
            json.dump(rules, f, indent=2)

    async def get_compliance_rules(
        self, framework: ComplianceFramework = None
    ) -> List[ComplianceRule]:
        """Get compliance rules"""
        rules_file = self.storage_path / "compliance" / "rules.json"

        if not rules_file.exists():
            return []

        with open(rules_file, "r") as f:
            rules_data = json.load(f)

        rules = []
        for rule_data in rules_data.values():
            rule = self._deserialize_compliance_rule(rule_data)
            if framework is None or rule.framework == framework:
                rules.append(rule)

        return rules

    async def store_violation(self, violation: ComplianceViolation):
        """Store compliance violation"""
        violations_file = self.storage_path / "compliance" / "violations.jsonl"

        violation_data = asdict(violation)
        violation_data["detected_at"] = violation.detected_at.isoformat()
        violation_data["severity"] = violation.severity.value  # Convert enum to string
        if violation.resolved_at:
            violation_data["resolved_at"] = violation.resolved_at.isoformat()

        with open(violations_file, "a") as f:
            f.write(json.dumps(violation_data) + "\n")

    async def store_lineage(self, lineage: DataLineage):
        """Store data lineage"""
        lineage_file = self.storage_path / "lineage" / f"{lineage.resource_id}.json"

        lineage_data = asdict(lineage)
        lineage_data["created_at"] = lineage.created_at.isoformat()
        lineage_data["updated_at"] = lineage.updated_at.isoformat()

        with open(lineage_file, "w") as f:
            json.dump(lineage_data, f, indent=2)

    def _deserialize_event(self, data: Dict[str, Any]) -> AuditEvent:
        """Deserialize audit event from JSON data"""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        data["event_type"] = AuditEventType(data["event_type"])
        data["level"] = AuditLevel(data["level"])
        return AuditEvent(**data)

    def _deserialize_compliance_rule(self, data: Dict[str, Any]) -> ComplianceRule:
        """Deserialize compliance rule from JSON data"""
        data["framework"] = ComplianceFramework(data["framework"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return ComplianceRule(**data)

    def _event_matches_filters(
        self, event: AuditEvent, filters: Dict[str, Any]
    ) -> bool:
        """Check if event matches the given filters"""
        if not filters:
            return True

        for key, value in filters.items():
            if key == "event_type" and event.event_type != AuditEventType(value):
                return False
            elif key == "user_id" and event.user_id != value:
                return False
            elif key == "connector_name" and event.connector_name != value:
                return False
            elif key == "level" and event.level != AuditLevel(value):
                return False
            elif key == "success" and event.success != value:
                return False

        return True


class ComplianceEngine:
    """Compliance monitoring and enforcement engine"""

    def __init__(self, storage: AuditStorage):
        self.storage = storage
        self.rules: Dict[str, ComplianceRule] = {}
        self.violations: List[ComplianceViolation] = []
        self.logger = setup_logger(__name__)

    async def load_rules(self):
        """Load compliance rules from storage"""
        rules = await self.storage.get_compliance_rules()
        self.rules = {rule.rule_id: rule for rule in rules}

    async def add_rule(self, rule: ComplianceRule):
        """Add new compliance rule"""
        await self.storage.store_compliance_rule(rule)
        self.rules[rule.rule_id] = rule

    async def check_compliance(self, event: AuditEvent) -> List[ComplianceViolation]:
        """Check event against compliance rules"""
        violations = []

        for rule in self.rules.values():
            if not rule.enabled:
                continue

            violation = await self._check_rule(rule, event)
            if violation:
                violations.append(violation)
                await self.storage.store_violation(violation)
                self.violations.append(violation)

        return violations

    async def _check_rule(
        self, rule: ComplianceRule, event: AuditEvent
    ) -> Optional[ComplianceViolation]:
        """Check a specific rule against an event"""
        if rule.rule_type == "data_retention":
            return await self._check_data_retention(rule, event)
        elif rule.rule_type == "access_control":
            return await self._check_access_control(rule, event)
        elif rule.rule_type == "encryption":
            return await self._check_encryption(rule, event)
        elif rule.rule_type == "data_export":
            return await self._check_data_export(rule, event)
        elif rule.rule_type == "sensitive_data":
            return await self._check_sensitive_data(rule, event)

        return None

    async def _check_data_retention(
        self, rule: ComplianceRule, event: AuditEvent
    ) -> Optional[ComplianceViolation]:
        """Check data retention compliance"""
        if event.event_type not in [
            AuditEventType.RESOURCE_CREATE,
            AuditEventType.RESOURCE_WRITE,
        ]:
            return None

        max_retention_days = rule.config.get("max_retention_days")
        if not max_retention_days:
            return None

        # Check if data is older than retention period
        retention_cutoff = datetime.utcnow() - timedelta(days=max_retention_days)

        if event.timestamp < retention_cutoff:
            return ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                event_id=event.event_id,
                severity=AuditLevel.WARNING,
                description=f"Data retention violation: Resource {event.resource_id} exceeds {max_retention_days} day retention policy",
            )

        return None

    async def _check_access_control(
        self, rule: ComplianceRule, event: AuditEvent
    ) -> Optional[ComplianceViolation]:
        """Check access control compliance"""
        if event.event_type not in [
            AuditEventType.RESOURCE_READ,
            AuditEventType.RESOURCE_WRITE,
        ]:
            return None

        # Check for unauthorized access patterns
        allowed_users = rule.config.get("allowed_users", [])
        restricted_resources = rule.config.get("restricted_resources", [])

        if allowed_users and event.user_id not in allowed_users:
            if any(
                pattern in (event.resource_id or "") for pattern in restricted_resources
            ):
                return ComplianceViolation(
                    violation_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    event_id=event.event_id,
                    severity=AuditLevel.ERROR,
                    description=f"Access control violation: User {event.user_id} accessed restricted resource {event.resource_id}",
                )

        return None

    async def _check_encryption(
        self, rule: ComplianceRule, event: AuditEvent
    ) -> Optional[ComplianceViolation]:
        """Check encryption compliance"""
        if event.event_type != AuditEventType.DATA_EXPORT:
            return None

        require_encryption = rule.config.get("require_encryption", True)
        if require_encryption and not event.details.get("encrypted", False):
            return ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                event_id=event.event_id,
                severity=AuditLevel.CRITICAL,
                description="Encryption violation: Unencrypted data export detected",
            )

        return None

    async def _check_data_export(
        self, rule: ComplianceRule, event: AuditEvent
    ) -> Optional[ComplianceViolation]:
        """Check data export compliance"""
        if event.event_type != AuditEventType.DATA_EXPORT:
            return None

        max_export_size = rule.config.get("max_export_size_mb")
        if max_export_size:
            export_size_mb = event.details.get("size_mb", 0)
            if export_size_mb > max_export_size:
                return ComplianceViolation(
                    violation_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    event_id=event.event_id,
                    severity=AuditLevel.WARNING,
                    description=f"Data export size violation: {export_size_mb}MB exceeds limit of {max_export_size}MB",
                )

        return None

    async def _check_sensitive_data(
        self, rule: ComplianceRule, event: AuditEvent
    ) -> Optional[ComplianceViolation]:
        """Check sensitive data handling compliance"""
        sensitive_patterns = rule.config.get("sensitive_patterns", [])
        if not sensitive_patterns:
            return None

        # Check event details for sensitive data patterns
        event_text = json.dumps(event.details).lower()

        for pattern in sensitive_patterns:
            if pattern.lower() in event_text:
                return ComplianceViolation(
                    violation_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    event_id=event.event_id,
                    severity=AuditLevel.ERROR,
                    description=f"Sensitive data violation: Pattern '{pattern}' detected in event",
                )

        return None


class GitIntegration:
    """Git integration for audit trail versioning"""

    def __init__(
        self, git_connector: GitConnector, audit_repo_path: str = "audit_repository"
    ):
        self.git_connector = git_connector
        self.audit_repo_path = Path(audit_repo_path)
        self.logger = setup_logger(__name__)

    async def initialize_repository(self):
        """Initialize audit repository"""
        if not self.audit_repo_path.exists():
            self.audit_repo_path.mkdir(parents=True)

            # Initialize git repository
            import subprocess

            subprocess.run(["git", "init"], cwd=self.audit_repo_path)
            subprocess.run(
                ["git", "config", "user.name", "OS Dashboard Audit System"],
                cwd=self.audit_repo_path,
            )
            subprocess.run(
                ["git", "config", "user.email", "audit@osdashboard.local"],
                cwd=self.audit_repo_path,
            )

    async def commit_audit_data(self, date: datetime, description: str = None):
        """Commit audit data for a specific date"""
        try:
            date_str = date.strftime("%Y-%m-%d")
            commit_message = description or f"Audit data for {date_str}"

            # Stage all changes
            import subprocess

            subprocess.run(["git", "add", "."], cwd=self.audit_repo_path)

            # Commit changes
            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.audit_repo_path,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self.logger.info(f"Committed audit data: {commit_message}")
                return True
            else:
                self.logger.warning(f"No changes to commit for {date_str}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to commit audit data: {e}")
            return False

    async def create_audit_branch(self, branch_name: str, base_date: datetime):
        """Create audit branch for specific investigation"""
        try:
            import subprocess

            # Create and checkout new branch
            subprocess.run(
                ["git", "checkout", "-b", branch_name], cwd=self.audit_repo_path
            )

            # Add investigation metadata
            metadata = {
                "branch_name": branch_name,
                "created_at": datetime.utcnow().isoformat(),
                "base_date": base_date.isoformat(),
                "purpose": "audit_investigation",
            }

            metadata_file = self.audit_repo_path / f"investigation_{branch_name}.json"
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            # Commit metadata
            subprocess.run(["git", "add", str(metadata_file)], cwd=self.audit_repo_path)
            subprocess.run(
                ["git", "commit", "-m", f"Start audit investigation: {branch_name}"],
                cwd=self.audit_repo_path,
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to create audit branch: {e}")
            return False

    async def get_audit_history(self, file_path: str) -> List[Dict[str, Any]]:
        """Get git history for audit file"""
        try:
            import subprocess

            result = subprocess.run(
                [
                    "git",
                    "log",
                    "--pretty=format:%H|%an|%ad|%s",
                    "--date=iso",
                    "--",
                    file_path,
                ],
                cwd=self.audit_repo_path,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                return []

            history = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split("|", 3)
                    if len(parts) == 4:
                        history.append(
                            {
                                "commit_hash": parts[0],
                                "author": parts[1],
                                "date": parts[2],
                                "message": parts[3],
                            }
                        )

            return history

        except Exception as e:
            self.logger.error(f"Failed to get audit history: {e}")
            return []


class AuditSystem:
    """Main audit and governance system"""

    def __init__(
        self, storage_path: str = "audit_data", git_repo_path: str = "audit_repository"
    ):
        self.storage = AuditStorage(storage_path)
        self.compliance_engine = ComplianceEngine(self.storage)
        self.git_integration = None
        self.connectors: Dict[str, BaseConnector] = {}
        self.lineage_tracker = {}
        self.logger = setup_logger(__name__)

        # Event hooks
        self.event_hooks: List[Callable] = []

    async def initialize(
        self, enable_git: bool = True, git_connector: GitConnector = None
    ):
        """Initialize audit system"""
        await self.compliance_engine.load_rules()

        if enable_git and git_connector:
            self.git_integration = GitIntegration(git_connector)
            await self.git_integration.initialize_repository()

        self.logger.info("Audit system initialized")

    def register_connector(self, name: str, connector: BaseConnector):
        """Register connector for audit tracking"""
        self.connectors[name] = connector

    def add_event_hook(self, hook: Callable[[AuditEvent], None]):
        """Add event hook for custom processing"""
        self.event_hooks.append(hook)

    async def log_event(
        self,
        event_type: AuditEventType,
        action: str,
        user_id: str = None,
        connector_name: str = None,
        resource_id: str = None,
        details: Dict[str, Any] = None,
        level: AuditLevel = AuditLevel.INFO,
        **kwargs,
    ) -> str:
        """Log audit event"""
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            connector_name=connector_name,
            resource_id=resource_id,
            action=action,
            details=details or {},
            level=level,
            **kwargs,
        )

        # Store event
        await self.storage.store_event(event)

        # Check compliance
        violations = await self.compliance_engine.check_compliance(event)
        if violations:
            self.logger.warning(
                f"Compliance violations detected for event {event.event_id}: {len(violations)}"
            )

        # Call event hooks
        for hook in self.event_hooks:
            try:
                await hook(event) if asyncio.iscoroutinefunction(hook) else hook(event)
            except Exception as e:
                self.logger.error(f"Event hook failed: {e}")

        return event.event_id

    async def track_data_lineage(
        self,
        resource_id: str,
        connector_name: str,
        source_resources: List[str] = None,
        transformations: List[Dict[str, Any]] = None,
    ):
        """Track data lineage"""
        lineage = DataLineage(
            lineage_id=str(uuid.uuid4()),
            resource_id=resource_id,
            connector_name=connector_name,
            source_resources=source_resources or [],
            transformations=transformations or [],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        await self.storage.store_lineage(lineage)
        self.lineage_tracker[resource_id] = lineage

    async def get_audit_trail(
        self, start_date: datetime, end_date: datetime, filters: Dict[str, Any] = None
    ) -> List[AuditEvent]:
        """Get audit trail for date range"""
        return await self.storage.get_events(start_date, end_date, filters)

    async def generate_compliance_report(
        self, framework: ComplianceFramework, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Generate compliance report"""
        # Get relevant events
        events = await self.get_audit_trail(start_date, end_date)

        # Get compliance rules for framework
        rules = await self.storage.get_compliance_rules(framework)

        # Analyze compliance
        total_events = len(events)
        violation_count = 0
        rule_violations = {}

        for event in events:
            violations = await self.compliance_engine.check_compliance(event)
            violation_count += len(violations)

            for violation in violations:
                if violation.rule_id not in rule_violations:
                    rule_violations[violation.rule_id] = 0
                rule_violations[violation.rule_id] += 1

        # Calculate compliance score
        compliance_score = (
            ((total_events - violation_count) / total_events * 100)
            if total_events > 0
            else 100
        )

        report = {
            "framework": framework.value,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "summary": {
                "total_events": total_events,
                "total_violations": violation_count,
                "compliance_score": round(compliance_score, 2),
                "rules_evaluated": len(rules),
            },
            "rule_violations": rule_violations,
            "recommendations": self._generate_compliance_recommendations(
                rule_violations, rules
            ),
        }

        return report

    async def export_audit_data(
        self,
        start_date: datetime,
        end_date: datetime,
        format: str = "json",
        encrypt: bool = True,
    ) -> str:
        """Export audit data"""
        events = await self.get_audit_trail(start_date, end_date)

        # Log export event
        await self.log_event(
            AuditEventType.DATA_EXPORT,
            "export_audit_data",
            details={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "format": format,
                "encrypted": encrypt,
                "event_count": len(events),
                "size_mb": len(json.dumps([asdict(e) for e in events])) / (1024 * 1024),
            },
        )

        # Export data
        if format == "json":
            export_data = [asdict(event) for event in events]
            # Convert datetime objects to ISO strings
            for event_data in export_data:
                event_data["timestamp"] = event_data["timestamp"].isoformat()

            export_content = json.dumps(export_data, indent=2)

        elif format == "csv":
            import csv
            import io

            output = io.StringIO()
            if events:
                fieldnames = asdict(events[0]).keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()

                for event in events:
                    event_dict = asdict(event)
                    event_dict["timestamp"] = event.timestamp.isoformat()
                    writer.writerow(event_dict)

            export_content = output.getvalue()

        else:
            raise ValueError(f"Unsupported export format: {format}")

        # Save export file
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"audit_export_{timestamp}.{format}"
        export_path = self.storage.storage_path / filename

        if encrypt:
            # Simple encryption (in production, use proper encryption)
            export_content = self._encrypt_content(export_content)
            filename += ".encrypted"
            export_path = self.storage.storage_path / filename

        with open(export_path, "w") as f:
            f.write(export_content)

        return str(export_path)

    async def daily_audit_commit(self, date: datetime = None):
        """Commit daily audit data to git"""
        if not self.git_integration:
            return False

        if date is None:
            date = datetime.utcnow() - timedelta(days=1)  # Previous day

        return await self.git_integration.commit_audit_data(date)

    def _generate_compliance_recommendations(
        self, violations: Dict[str, int], rules: List[ComplianceRule]
    ) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []

        # Find most violated rules
        if violations:
            most_violated = max(violations.items(), key=lambda x: x[1])
            rule_id, count = most_violated

            # Find the rule
            rule = next((r for r in rules if r.rule_id == rule_id), None)
            if rule:
                recommendations.append(
                    f"Address frequent violations of rule '{rule.name}' ({count} violations)"
                )

        # General recommendations
        if len(violations) > 0:
            recommendations.append("Review and update access control policies")
            recommendations.append(
                "Implement additional monitoring for sensitive operations"
            )
            recommendations.append("Provide compliance training to users")

        return recommendations

    def _encrypt_content(self, content: str) -> str:
        """Simple content encryption (placeholder)"""
        # In production, use proper encryption like Fernet
        import base64

        return base64.b64encode(content.encode()).decode()

    async def get_system_statistics(self) -> Dict[str, Any]:
        """Get audit system statistics"""
        # Get recent events (last 30 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        recent_events = await self.get_audit_trail(start_date, end_date)

        # Event type distribution
        event_type_counts = {}
        for event in recent_events:
            event_type = event.event_type.value
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1

        # Compliance statistics
        total_rules = len(self.compliance_engine.rules)
        active_rules = sum(
            1 for rule in self.compliance_engine.rules.values() if rule.enabled
        )

        return {
            "total_events_30_days": len(recent_events),
            "event_type_distribution": event_type_counts,
            "compliance_rules": {"total": total_rules, "active": active_rules},
            "registered_connectors": len(self.connectors),
            "data_lineage_tracked": len(self.lineage_tracker),
            "git_integration_enabled": self.git_integration is not None,
        }
