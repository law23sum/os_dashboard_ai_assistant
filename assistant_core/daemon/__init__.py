"""Daemon framework for continuous background automation.

This module implements the core daemon architecture that makes the OS
truly active - monitoring, automating, drafting, updating, and governing
all knowledge work without being asked.
"""

from .cognitive_daemon import CognitiveDaemon, start_daemon_system, stop_daemon_system
from .monitors import (
    DocumentMonitor,
    TaskMonitor,
    IntegrationMonitor,
    FileSystemMonitor,
    OutdatedContentMonitor,
)
from .automators import (
    AutoDraftService,
    AutoUpdateService,
    AutoSuggestService,
    WorkflowExecutor,
)
from .workflow_orchestration import (
    WorkflowEngine,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowAction,
    WorkflowTrigger,
    WorkflowStatus,
    ActionType,
    TriggerType,
    WorkflowActionExecutor,
    ReadResourceExecutor,
    WriteResourceExecutor,
    TransformDataExecutor,
    ConditionalExecutor,
)

__all__ = [
    "CognitiveDaemon",
    "start_daemon_system",
    "stop_daemon_system",
    "DocumentMonitor",
    "TaskMonitor",
    "IntegrationMonitor",
    "FileSystemMonitor",
    "OutdatedContentMonitor",
    "AutoDraftService",
    "AutoUpdateService",
    "AutoSuggestService",
    "WorkflowExecutor",
    "WorkflowEngine",
    "WorkflowDefinition",
    "WorkflowExecution",
    "WorkflowAction",
    "WorkflowTrigger",
    "WorkflowStatus",
    "ActionType",
    "TriggerType",
    "WorkflowActionExecutor",
    "ReadResourceExecutor",
    "WriteResourceExecutor",
    "TransformDataExecutor",
    "ConditionalExecutor",
]

