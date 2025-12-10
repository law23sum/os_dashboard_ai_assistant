"""Core domain models derived from the Canon Technical Specification."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union


# ---------------------------------------------------------------------------
# 3.1 Users, Tenants, Identity & Roles
# ---------------------------------------------------------------------------
class UserRole(Enum):
    """User roles in the system."""

    ADMIN = "admin"
    USER = "user"
    DEVELOPER = "developer"
    ANALYST = "analyst"
    VIEWER = "viewer"
    REGULATOR = "regulator"
    PARTNER = "partner"


class TenantType(Enum):
    """Types of tenants in the system."""

    INDIVIDUAL = "individual"
    ORGANIZATION = "organization"
    ENTERPRISE = "enterprise"
    GOVERNMENT = "government"
    ACADEMIC = "academic"


@dataclass
class User:
    """Core user entity - 3.1 Users, Tenants, Identity & Roles."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    full_name: str = ""
    roles: Set[UserRole] = field(default_factory=set)
    tenant_id: str = ""
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: Optional[datetime] = None
    is_active: bool = True

    def has_role(self, role: UserRole) -> bool:
        return role in self.roles

    def add_role(self, role: UserRole) -> None:
        self.roles.add(role)

    def remove_role(self, role: UserRole) -> None:
        self.roles.discard(role)


@dataclass
class Tenant:
    """Tenant entity for multi-tenancy support."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    tenant_type: TenantType = TenantType.INDIVIDUAL
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    parent_tenant_id: Optional[str] = None


# ---------------------------------------------------------------------------
# 3.2 Identity & Driver Scopes
# ---------------------------------------------------------------------------
class DriverScope(Enum):
    """Driver execution scopes."""

    USER = "user"
    WORKSPACE = "workspace"
    TENANT = "tenant"
    CAPSULE = "capsule"
    GLOBAL = "global"


@dataclass
class IdentityScope:
    """Identity and driver scopes - 3.2."""

    scope_type: DriverScope
    scope_id: str
    permissions: Set[str] = field(default_factory=set)
    constraints: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 3.3 Projects, Workspaces, Domains & Environment Profiles
# ---------------------------------------------------------------------------
class ProjectStatus(Enum):
    """Project lifecycle states."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"


class WorkspaceType(Enum):
    """Types of workspaces."""

    MASTER_STACK = "master_stack"
    DEV_DEVOPS = "dev_devops"
    RESEARCH_SIMULATION = "research_simulation"
    WRITER = "writer"
    ARCHIVE_CONTINUITY = "archive_continuity"
    CYBERSECURITY = "cybersecurity"
    BUSINESS_FINANCE = "business_finance"
    RECORD_AUDITOR = "record_auditor"
    OPERATOR_SRE = "operator_sre"
    DIGITAL_TWIN = "digital_twin"


@dataclass
class EnvironmentProfile:
    """Environment configuration profile - 3.9."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    environment_type: str = ""
    configuration: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0.0"


@dataclass
class Project:
    """Core project entity - 3.3."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    status: ProjectStatus = ProjectStatus.DRAFT
    owner_id: str = ""
    tenant_id: str = ""
    workspace_type: WorkspaceType = WorkspaceType.MASTER_STACK
    environment_profile_id: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    due_date: Optional[datetime] = None

    def update_timestamp(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class Workspace:
    """Workspace abstraction - 7.1."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    workspace_type: WorkspaceType = WorkspaceType.MASTER_STACK
    project_id: str = ""
    configuration: Dict[str, Any] = field(default_factory=dict)
    active_environment: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# 3.4 Task Model
# ---------------------------------------------------------------------------
class TaskStatus(Enum):
    """Task lifecycle states."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Task:
    """Core task entity - 3.4."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    project_id: str = ""
    owner_id: str = ""
    assignee_id: Optional[str] = None
    persona_owner: Optional[str] = None
    agent_owner: Optional[str] = None
    parent_task_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def mark_completed(self) -> None:
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now(timezone.utc)
        self.update_timestamp()

    def update_timestamp(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# 3.6 CIR (Canonical Internal Representation)
# ---------------------------------------------------------------------------
class CIRBlockType(Enum):
    """Types of CIR blocks."""

    TEXT = "text"
    CODE = "code"
    IMAGE = "image"
    TABLE = "table"
    LINK = "link"
    METADATA = "metadata"
    STRUCTURED_DATA = "structured_data"


@dataclass
class CIRBlock:
    """Individual block in a CIR document - 3.6."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    block_type: CIRBlockType = CIRBlockType.TEXT
    content: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    position: int = 0
    parent_block_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CIRDocument:
    """Canonical Internal Representation document - 3.6."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    source_path: Optional[str] = None
    source_type: str = ""
    blocks: List[CIRBlock] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_block(self, block: CIRBlock) -> None:
        block.position = len(self.blocks)
        self.blocks.append(block)
        self.update_timestamp()

    def update_timestamp(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# 3.7 Project Ledger, Events, Timelines & Causal Graph
# ---------------------------------------------------------------------------
class EventType(Enum):
    """Types of events in the project ledger."""

    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    CAPSULE_EXECUTED = "capsule_executed"
    DRIVER_INVOKED = "driver_invoked"
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"


@dataclass
class ProjectEvent:
    """Individual event in the project ledger - 3.7."""

    event_type: EventType
    project_id: str
    user_id: Optional[str] = None
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hash_chain_prev: Optional[str] = None
    hash_chain_current: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.hash_chain_current:
            self.hash_chain_current = self._calculate_hash()

    def _calculate_hash(self) -> str:
        content = (
            f"{self.id}{self.event_type.value}{self.project_id}"
            f"{self.timestamp.isoformat()}"
        )
        if self.hash_chain_prev:
            content += self.hash_chain_prev
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass
class ProjectLedger:
    """Project ledger with hash-chained events - 3.7."""

    project_id: str
    events: List[ProjectEvent] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_event(self, event: ProjectEvent) -> None:
        if self.events:
            event.hash_chain_prev = self.events[-1].hash_chain_current
        event.hash_chain_current = event._calculate_hash()
        self.events.append(event)

    def verify_integrity(self) -> bool:
        for idx, event in enumerate(self.events):
            if idx > 0 and event.hash_chain_prev != self.events[idx - 1].hash_chain_current:
                return False
            if event.hash_chain_current != event._calculate_hash():
                return False
        return True


# ---------------------------------------------------------------------------
# 3.8 Knowledge Capsules, Capsule Packs & Capsule Graph
# ---------------------------------------------------------------------------
class CapsuleType(Enum):
    """Types of capsules - 8.1."""

    TEMPLATE = "template"
    ANALYTICAL = "analytical"
    EXECUTABLE = "executable"
    INFRASTRUCTURE = "infrastructure"
    COMPOSITE = "composite"
    TEST = "test"


class CapsuleStatus(Enum):
    """Capsule lifecycle states - 8.4."""

    DESIGN = "design"
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"


@dataclass
class CapsuleManifest:
    """Capsule manifest with metadata - 8.3."""

    name: str
    version: str
    description: str
    capsule_type: CapsuleType
    dependencies: List[str] = field(default_factory=list)
    driver_dependencies: List[str] = field(default_factory=list)
    environment_requirements: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    tests: List[str] = field(default_factory=list)


@dataclass
class KnowledgeCapsule:
    """Knowledge capsule entity - 3.8."""

    manifest: CapsuleManifest
    content: Any = None
    status: CapsuleStatus = CapsuleStatus.DESIGN
    owner_id: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    usage_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None

    def publish(self) -> None:
        self.status = CapsuleStatus.PUBLISHED
        self.published_at = datetime.now(timezone.utc)
        self.update_timestamp()

    def update_timestamp(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class CapsulePack:
    """Collection of related capsules."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    capsule_ids: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# 3.11 Policies, Policy Packs & Governance Artifacts
# ---------------------------------------------------------------------------
class PolicyType(Enum):
    """Types of policies."""

    ACCESS_CONTROL = "access_control"
    BUDGET_LIMIT = "budget_limit"
    RESOURCE_QUOTA = "resource_quota"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    DATA_GOVERNANCE = "data_governance"


@dataclass
class Policy:
    """Policy definition - 3.11."""

    name: str
    policy_type: PolicyType
    description: str = ""
    rules: Dict[str, Any] = field(default_factory=dict)
    scope: Optional[IdentityScope] = None
    is_active: bool = True
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PolicyPack:
    """Collection of related policies."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    policy_ids: List[str] = field(default_factory=list)
    compliance_framework: Optional[str] = None
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# 3.12 Usage Records, Cost Entities & Billing Surfaces
# ---------------------------------------------------------------------------
class UsageType(Enum):
    """Types of usage records."""

    COMPUTE_TIME = "compute_time"
    STORAGE_USAGE = "storage_usage"
    API_CALLS = "api_calls"
    MODEL_INFERENCE = "model_inference"
    DRIVER_EXECUTION = "driver_execution"
    CAPSULE_RUN = "capsule_run"


@dataclass
class UsageRecord:
    """Usage tracking record - 3.12."""

    usage_type: UsageType
    entity_id: str
    entity_type: str
    quantity: float
    unit: str
    cost: Optional[float] = None
    currency: str = "USD"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 3.13 Digital Twins, Cognitive Twins, Knowledge Atlas
# ---------------------------------------------------------------------------
class TwinType(Enum):
    """Types of digital twins."""

    SYSTEM_TWIN = "system_twin"
    DEVICE_TWIN = "device_twin"
    PROCESS_TWIN = "process_twin"
    ORGANIZATION_TWIN = "organization_twin"
    COGNITIVE_TWIN = "cognitive_twin"


@dataclass
class DigitalTwin:
    """Digital twin entity - 3.13."""

    name: str
    twin_type: TwinType
    real_world_entity_id: str
    model_definition: Dict[str, Any] = field(default_factory=dict)
    current_state: Dict[str, Any] = field(default_factory=dict)
    historical_states: List[Dict[str, Any]] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_state(self, new_state: Dict[str, Any]) -> None:
        self.historical_states.append(
            {"state": self.current_state.copy(), "timestamp": self.updated_at.isoformat()}
        )
        self.current_state = new_state
        self.updated_at = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Utility functions for domain models
# ---------------------------------------------------------------------------
class DomainModelRegistry:
    """Registry/helpers for domain model serialization/deserialization."""

    @staticmethod
    def serialize_model(model: Any) -> Dict[str, Any]:
        if hasattr(model, "__dataclass_fields__"):
            result = asdict(model)
            for key, value in result.items():
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, set):
                    result[key] = list(value)
                elif isinstance(value, Enum):
                    result[key] = value.value
            return result
        return {}

    @staticmethod
    def deserialize_model(model_class: type, data: Dict[str, Any]) -> Any:
        fields = getattr(model_class, "__dataclass_fields__", {})
        for field_name, field_def in fields.items():
            if field_name not in data:
                continue
            value = data[field_name]
            origin = getattr(field_def.type, "__origin__", None)
            if field_def.type is datetime or origin is Union:
                if isinstance(value, str):
                    try:
                        data[field_name] = datetime.fromisoformat(value)
                    except ValueError:
                        pass
            elif isinstance(field_def.type, type) and issubclass(field_def.type, Enum):
                if isinstance(value, str):
                    data[field_name] = field_def.type(value)
            elif field_def.type in {set, Set} or origin is set:
                if isinstance(value, list):
                    data[field_name] = set(value)
        return model_class(**data)


__all__ = [
    "User",
    "Tenant",
    "UserRole",
    "TenantType",
    "Project",
    "Workspace",
    "ProjectStatus",
    "WorkspaceType",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "CIRDocument",
    "CIRBlock",
    "CIRBlockType",
    "ProjectEvent",
    "ProjectLedger",
    "EventType",
    "KnowledgeCapsule",
    "CapsulePack",
    "CapsuleType",
    "CapsuleStatus",
    "CapsuleManifest",
    "Policy",
    "PolicyPack",
    "PolicyType",
    "UsageRecord",
    "UsageType",
    "DigitalTwin",
    "TwinType",
    "EnvironmentProfile",
    "IdentityScope",
    "DriverScope",
    "DomainModelRegistry",
]
