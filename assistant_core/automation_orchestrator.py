#!/usr/bin/env python3
"""
Intelligent Automation and Workflow Orchestration System

Integrated with OS Dashboard AI Assistant for comprehensive workflow automation.
Combines AI agents, task management, document processing, and scheduling into orchestrated workflows.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

from assistant_core.failure_registry import (
    FailureLayer,
    FailurePlane,
    FailureRegistry,
    FailureRootCause,
    FailureScope,
    FailureSeverity,
    get_failure_registry,
)
from assistant_core.spec_registry import get_default_registry

# Import Task from GUI db since it's not in core db
try:
    from assistant_hub_gui.assistant_hub.db import (
        Task,
        db_insert_task,
        PERSONAS,
        PRIORITY_OPTIONS,
        STATUS_OPTIONS,
    )
except ImportError:
    # Fallback for when GUI not available
    Task = None
    db_insert_task = None
    PERSONAS = ["Chris", "AIC", "Aria", "Sora"]
    PRIORITY_OPTIONS = ["LOW", "MEDIUM", "HIGH", "CRITICAL", "URGENT"]
    STATUS_OPTIONS = ["TODO", "IN_PROGRESS", "DONE", "CANCELLED"]
# Optional imports - gracefully handle missing dependencies
try:
    from .ai import generate_ai_reply, get_agent_model

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    generate_ai_reply = None
    get_agent_model = None

try:
    from .task_automation import process_recurring_tasks

    TASK_AUTOMATION_AVAILABLE = True
except ImportError:
    TASK_AUTOMATION_AVAILABLE = False
    process_recurring_tasks = None

try:
    from .sync_scheduler import create_default_scheduler

    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    create_default_scheduler = None

try:
    from .ai_task_creation import extract_tasks_from_text

    TASK_EXTRACTION_AVAILABLE = True
except ImportError:
    TASK_EXTRACTION_AVAILABLE = False
    extract_tasks_from_text = None

from config.logging_config import setup_logger


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING = "waiting"


class TriggerType(Enum):
    TIME_BASED = "time_based"
    EVENT_BASED = "event_based"
    CONDITION_BASED = "condition_based"
    USER_INITIATED = "user_initiated"
    AI_SUGGESTED = "ai_suggested"
    DEPENDENCY_BASED = "dependency_based"


class ActionType(Enum):
    API_CALL = "api_call"
    EMAIL_SEND = "email_send"
    FILE_OPERATION = "file_operation"
    DATA_PROCESSING = "data_processing"
    NOTIFICATION = "notification"
    TASK_CREATION = "task_creation"
    REPORT_GENERATION = "report_generation"
    SYSTEM_COMMAND = "system_command"
    AI_ANALYSIS = "ai_analysis"
    WORKFLOW_TRIGGER = "workflow_trigger"
    AGENT_INTERACTION = "agent_interaction"  # OS Dashboard specific
    DOCUMENT_PROCESSING = "document_processing"  # OS Dashboard specific


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5


@dataclass
class WorkflowTrigger:
    """Workflow trigger configuration"""

    trigger_id: str
    trigger_type: TriggerType
    conditions: Dict[str, Any]
    schedule_config: Optional[Dict[str, Any]] = None
    event_filters: Optional[Dict[str, Any]] = None
    enabled: bool = True


@dataclass
class WorkflowAction:
    """Individual workflow action"""

    action_id: str
    action_type: ActionType
    name: str
    description: str
    parameters: Dict[str, Any]
    retry_config: Dict[str, Any]
    timeout_seconds: int = 300
    depends_on: List[str] = None
    condition: Optional[str] = None
    enabled: bool = True


@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""

    workflow_id: str
    name: str
    description: str
    version: str
    triggers: List[WorkflowTrigger]
    actions: List[WorkflowAction]
    variables: Dict[str, Any]
    settings: Dict[str, Any]
    priority: Priority
    owner: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    enabled: bool = True


@dataclass
class WorkflowExecution:
    """Workflow execution instance"""

    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    triggered_by: str
    trigger_data: Dict[str, Any]
    start_time: datetime
    end_time: Optional[datetime]
    current_action: Optional[str]
    completed_actions: List[str]
    failed_actions: List[str]
    execution_context: Dict[str, Any]
    error_message: Optional[str]
    retry_count: int = 0
    progress_percentage: float = 0.0


@dataclass
class AutomationRule:
    """Intelligent automation rule"""

    rule_id: str
    name: str
    description: str
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    priority: Priority
    confidence_threshold: float
    learning_enabled: bool
    success_rate: float
    usage_count: int
    created_at: datetime
    last_used: Optional[datetime]
    enabled: bool = True


class AutomationOrchestrator:
    """
    Intelligent automation and workflow orchestration system integrated with OS Dashboard AI Assistant.
    Provides comprehensive workflow automation combining AI agents, task management, and document processing.
    """

    def __init__(
        self,
        app_state=None,
        failure_registry: Optional[FailureRegistry] = None,
    ):
        self.logger = setup_logger("AutomationOrchestrator")
        self.app_state = app_state
        self.failure_registry = failure_registry or get_failure_registry()

        # Core storage
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.automation_rules: Dict[str, AutomationRule] = {}

        # Runtime management
        self.active_executions: Dict[str, asyncio.Task] = {}
        self.trigger_handlers: Dict[TriggerType, Callable] = {}
        self.action_handlers: Dict[ActionType, Callable] = {}

        # AI and learning
        self.execution_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {}
        self.optimization_suggestions: List[Dict[str, Any]] = []

        # Configuration
        self.config = {
            "max_concurrent_executions": 10,  # Lower for OS Dashboard
            "default_timeout": 1800,  # 30 minutes
            "retry_max_attempts": 3,
            "retry_delay_seconds": 30,
            "learning_enabled": True,
            "auto_optimization": True,
            "proactive_suggestions": True,
            "performance_monitoring": True,
        }

        # Event system
        self.event_queue = asyncio.Queue()
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)

        # OS Dashboard specific integrations
        self.ai_agents_available = ["Aria", "AIC", "Sora"]
        self.task_creation_available = True
        self.document_processing_available = True
        self.failure_registry.register_recovery_plan(
            "automation_workflow_recovery",
            capsule_id="capsule.control.workflow.recovery",
            description="Regenerate automation plan, replay successful steps, and run compensations for failed actions.",
            tags=["14.3.3", "control"],
        )

    async def initialize(self):
        """Initialize automation system"""
        await self._setup_trigger_handlers()
        await self._setup_action_handlers()
        await self._load_workflows()
        await self._load_automation_rules()

        # Start background tasks
        asyncio.create_task(self._event_processor())
        asyncio.create_task(self._execution_monitor())
        asyncio.create_task(self._performance_analyzer())
        asyncio.create_task(self._optimization_engine())

        # Start scheduler (integrate with existing sync_scheduler if available)
        self._start_scheduler()

        self.logger.info("Automation Orchestrator initialized")

    # Setup Methods

    async def _setup_trigger_handlers(self):
        """Setup trigger handlers"""
        self.trigger_handlers = {
            TriggerType.TIME_BASED: self._handle_time_trigger,
            TriggerType.EVENT_BASED: self._handle_event_trigger,
            TriggerType.CONDITION_BASED: self._handle_condition_trigger,
            TriggerType.USER_INITIATED: self._handle_user_trigger,
            TriggerType.AI_SUGGESTED: self._handle_ai_trigger,
            TriggerType.DEPENDENCY_BASED: self._handle_dependency_trigger,
        }

    async def _setup_action_handlers(self):
        """Setup action handlers"""
        self.action_handlers = {
            ActionType.API_CALL: self._handle_api_call,
            ActionType.EMAIL_SEND: self._handle_email_send,
            ActionType.FILE_OPERATION: self._handle_file_operation,
            ActionType.DATA_PROCESSING: self._handle_data_processing,
            ActionType.NOTIFICATION: self._handle_notification,
            ActionType.TASK_CREATION: self._handle_task_creation,
            ActionType.REPORT_GENERATION: self._handle_report_generation,
            ActionType.SYSTEM_COMMAND: self._handle_system_command,
            ActionType.AI_ANALYSIS: self._handle_ai_analysis,
            ActionType.WORKFLOW_TRIGGER: self._handle_workflow_trigger,
            ActionType.AGENT_INTERACTION: self._handle_agent_interaction,
            ActionType.DOCUMENT_PROCESSING: self._handle_document_processing,
        }

    # Workflow Management

    async def create_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """Create new workflow"""
        try:
            workflow_id = str(uuid.uuid4())

            # Parse triggers
            triggers = []
            for trigger_data in workflow_data.get("triggers", []):
                trigger = WorkflowTrigger(
                    trigger_id=str(uuid.uuid4()),
                    trigger_type=TriggerType(trigger_data["type"]),
                    conditions=trigger_data.get("conditions", {}),
                    schedule_config=trigger_data.get("schedule_config"),
                    event_filters=trigger_data.get("event_filters"),
                    enabled=trigger_data.get("enabled", True),
                )
                triggers.append(trigger)

            # Parse actions
            actions = []
            for action_data in workflow_data.get("actions", []):
                action = WorkflowAction(
                    action_id=str(uuid.uuid4()),
                    action_type=ActionType(action_data["type"]),
                    name=action_data["name"],
                    description=action_data.get("description", ""),
                    parameters=action_data.get("parameters", {}),
                    retry_config=action_data.get(
                        "retry_config", {"max_attempts": 3, "delay_seconds": 30}
                    ),
                    timeout_seconds=action_data.get("timeout_seconds", 300),
                    depends_on=action_data.get("depends_on", []),
                    condition=action_data.get("condition"),
                    enabled=action_data.get("enabled", True),
                )
                actions.append(action)

            # Create workflow
            workflow = WorkflowDefinition(
                workflow_id=workflow_id,
                name=workflow_data["name"],
                description=workflow_data.get("description", ""),
                version=workflow_data.get("version", "1.0"),
                triggers=triggers,
                actions=actions,
                variables=workflow_data.get("variables", {}),
                settings=workflow_data.get("settings", {}),
                priority=Priority(workflow_data.get("priority", 2)),
                owner=workflow_data.get("owner", "system"),
                tags=workflow_data.get("tags", []),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                enabled=workflow_data.get("enabled", True),
            )

            self.workflows[workflow_id] = workflow
            await self._register_workflow_triggers(workflow)

            self.logger.info(f"Workflow created: {workflow.name} ({workflow_id})")
            return workflow_id

        except Exception as e:
            self.logger.error(f"Workflow creation failed: {e}")
            raise

    async def trigger_workflow(
        self,
        workflow_id: str,
        trigger_data: Dict[str, Any] = None,
        triggered_by: str = "manual",
    ) -> str:
        """Manually trigger workflow execution"""
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                raise Exception(f"Workflow {workflow_id} not found")

            if not workflow.enabled:
                raise Exception(f"Workflow {workflow_id} is disabled")

            # Check concurrent execution limits
            active_count = len(
                [
                    e
                    for e in self.executions.values()
                    if e.status == WorkflowStatus.RUNNING
                ]
            )

            if active_count >= self.config["max_concurrent_executions"]:
                raise Exception("Maximum concurrent executions reached")

            # Create execution
            execution_id = str(uuid.uuid4())
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow_id,
                status=WorkflowStatus.PENDING,
                triggered_by=triggered_by,
                trigger_data=trigger_data or {},
                start_time=datetime.now(),
                end_time=None,
                current_action=None,
                completed_actions=[],
                failed_actions=[],
                execution_context=workflow.variables.copy(),
                error_message=None,
            )

            self.executions[execution_id] = execution

            # Start execution
            task = asyncio.create_task(self._execute_workflow(execution))
            self.active_executions[execution_id] = task

            self.logger.info(f"Workflow triggered: {workflow.name} ({execution_id})")
            return execution_id

        except Exception as e:
            self.logger.error(f"Workflow trigger failed: {e}")
            raise

    async def _execute_workflow(self, execution: WorkflowExecution):
        """Execute workflow instance"""
        try:
            workflow = self.workflows[execution.workflow_id]
            execution.status = WorkflowStatus.RUNNING

            self.logger.info(f"Starting workflow execution: {execution.execution_id}")

            # Build action dependency graph
            action_graph = self._build_action_graph(workflow.actions)

            # Execute actions in dependency order
            completed_actions = set()

            while len(completed_actions) < len(workflow.actions):
                # Find actions ready to execute
                ready_actions = []
                for action in workflow.actions:
                    if (
                        action.action_id not in completed_actions
                        and action.enabled
                        and self._action_dependencies_met(action, completed_actions)
                    ):
                        ready_actions.append(action)

                if not ready_actions:
                    # Check for circular dependencies or other issues
                    remaining_actions = [
                        a
                        for a in workflow.actions
                        if a.action_id not in completed_actions
                    ]
                    if remaining_actions:
                        raise Exception(
                            "Circular dependency or unmet conditions detected"
                        )
                    break

                # Execute ready actions (can be parallel if no dependencies between them)
                execution_tasks = []
                for action in ready_actions:
                    # Check action condition
                    if action.condition and not self._evaluate_condition(
                        action.condition, execution.execution_context
                    ):
                        completed_actions.add(action.action_id)
                        continue

                    execution.current_action = action.action_id
                    task = asyncio.create_task(self._execute_action(action, execution))
                    execution_tasks.append((action.action_id, task))

                # Wait for all tasks to complete
                for action_id, task in execution_tasks:
                    try:
                        result = await task
                        execution.completed_actions.append(action_id)
                        completed_actions.add(action_id)

                        # Update execution context with action results
                        if result:
                            execution.execution_context[
                                f"action_{action_id}_result"
                            ] = result

                    except Exception as e:
                        execution.failed_actions.append(action_id)
                        self.logger.error(f"Action {action_id} failed: {e}")

                        # Check if workflow should continue or fail
                        action = next(
                            a for a in workflow.actions if a.action_id == action_id
                        )
                        if action.retry_config.get("required", True):
                            raise Exception(f"Required action {action_id} failed: {e}")

                # Update progress
                execution.progress_percentage = (
                    len(completed_actions) / len(workflow.actions)
                ) * 100

            # Workflow completed successfully
            execution.status = WorkflowStatus.COMPLETED
            execution.end_time = datetime.now()
            execution.progress_percentage = 100.0

            # Record execution history
            await self._record_execution_history(execution, workflow)

            self.logger.info(f"Workflow execution completed: {execution.execution_id}")

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.end_time = datetime.now()
            execution.error_message = str(e)

            self.logger.error(
                f"Workflow execution failed: {execution.execution_id} - {e}"
            )
            self._record_workflow_failure(execution, str(e))

        finally:
            # Clean up
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]

            # Emit execution completed event
            await self._emit_event(
                "workflow_execution_completed",
                {
                    "execution_id": execution.execution_id,
                    "workflow_id": execution.workflow_id,
                    "status": execution.status.value,
                    "duration": (
                        execution.end_time - execution.start_time
                    ).total_seconds()
                    if execution.end_time
                    else None,
                },
            )

    async def _execute_action(
        self, action: WorkflowAction, execution: WorkflowExecution
    ) -> Any:
        """Execute individual action"""
        try:
            self.logger.debug(f"Executing action: {action.name} ({action.action_id})")

            # Get action handler
            handler = self.action_handlers.get(action.action_type)
            if not handler:
                raise Exception(f"No handler for action type: {action.action_type}")

            # Execute with timeout and retry
            max_attempts = action.retry_config.get("max_attempts", 3)
            delay_seconds = action.retry_config.get("delay_seconds", 30)

            for attempt in range(max_attempts):
                try:
                    # Execute action with timeout
                    result = await asyncio.wait_for(
                        handler(action, execution), timeout=action.timeout_seconds
                    )

                    self.logger.debug(f"Action completed: {action.name}")
                    return result

                except asyncio.TimeoutError:
                    self._ingest_action_signal(
                        "timeout", action, execution, attempt + 1, max_attempts
                    )
                    if attempt < max_attempts - 1:
                        self.logger.warning(
                            f"Action {action.name} timed out, retrying..."
                        )
                        await asyncio.sleep(delay_seconds)
                        continue
                    else:
                        raise Exception(
                            f"Action {action.name} timed out after {max_attempts} attempts"
                        )

                except Exception as e:
                    self._ingest_action_signal(
                        "error", action, execution, attempt + 1, max_attempts
                    )
                    if attempt < max_attempts - 1:
                        self.logger.warning(
                            f"Action {action.name} failed, retrying: {e}"
                        )
                        await asyncio.sleep(delay_seconds)
                        continue
                    else:
                        raise

        except Exception as e:
            self.logger.error(f"Action execution failed: {action.name} - {e}")
            self._record_action_failure(action, execution, str(e))
            raise

    # Action Handlers - Extended for OS Dashboard Integration

    async def _setup_action_handlers(self):
        """Setup action handlers"""
        self.action_handlers = {
            ActionType.API_CALL: self._handle_api_call,
            ActionType.EMAIL_SEND: self._handle_email_send,
            ActionType.FILE_OPERATION: self._handle_file_operation,
            ActionType.DATA_PROCESSING: self._handle_data_processing,
            ActionType.NOTIFICATION: self._handle_notification,
            ActionType.TASK_CREATION: self._handle_task_creation,
            ActionType.REPORT_GENERATION: self._handle_report_generation,
            ActionType.SYSTEM_COMMAND: self._handle_system_command,
            ActionType.AI_ANALYSIS: self._handle_ai_analysis,
            ActionType.WORKFLOW_TRIGGER: self._handle_workflow_trigger,
            ActionType.AGENT_INTERACTION: self._handle_agent_interaction,  # OS Dashboard specific
            ActionType.DOCUMENT_PROCESSING: self._handle_document_processing,  # OS Dashboard specific
        }

    async def _handle_agent_interaction(
        self, action: WorkflowAction, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Handle AI agent interaction - OS Dashboard specific"""
        try:
            params = action.parameters
            agent_name = params["agent"]  # Aria, AIC, or Sora
            prompt = self._replace_variables(
                params["prompt"], execution.execution_context
            )
            context_data = params.get("context_data", {})

            if agent_name not in self.ai_agents_available:
                raise Exception(f"Agent {agent_name} not available")

            # Prepare conversation context
            conversation_history = []
            if "conversation_context" in execution.execution_context:
                conversation_history = execution.execution_context[
                    "conversation_context"
                ]

            # Generate AI response using existing AI system
            try:
                (
                    response_text,
                    error,
                    tool_calls,
                ) = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: generate_ai_reply(
                        history=conversation_history,
                        persona=agent_name,
                        prompt=prompt,
                        system_prompt=params.get("system_prompt", ""),
                        model=get_agent_model(agent_name),
                        temperature=params.get("temperature", 0.7),
                        max_tokens=params.get("max_tokens", 1000),
                    ),
                )

                if error:
                    raise Exception(f"AI response failed: {error}")

                result = {
                    "agent": agent_name,
                    "prompt": prompt,
                    "response": response_text,
                    "tool_calls": tool_calls,
                    "timestamp": datetime.now().isoformat(),
                }

                # Update conversation context
                execution.execution_context[
                    "conversation_context"
                ] = conversation_history + [
                    {"role": "user", "content": prompt, "persona": "workflow"},
                    {
                        "role": "assistant",
                        "content": response_text,
                        "persona": agent_name,
                    },
                ]

                return result

            except Exception as e:
                self.logger.error(f"Agent interaction failed: {e}")
                raise

        except Exception as e:
            self.logger.error(f"Agent interaction action failed: {e}")
            raise

    async def _handle_document_processing(
        self, action: WorkflowAction, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Handle document processing - OS Dashboard specific"""
        try:
            params = action.parameters
            operation = params["operation"]  # analyze, summarize, extract_tasks, etc.
            file_path = self._replace_variables(
                params["file_path"], execution.execution_context
            )

            # Use existing document processing capabilities
            if operation == "extract_tasks":
                # Use existing task extraction
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tasks = extract_tasks_from_text(
                    content,
                    default_project=params.get("project", "General"),
                    default_owner=params.get("owner", "workflow"),
                )

                result = {
                    "operation": operation,
                    "file_path": file_path,
                    "extracted_tasks": len(tasks),
                    "tasks": [asdict(task) for task in tasks],
                }

                return result

            elif operation == "summarize":
                # Use AI agent for summarization
                summary_prompt = f"Please summarize the following document content:\n\n{content[:4000]}..."

                # Trigger agent interaction
                agent_action = WorkflowAction(
                    action_id=str(uuid.uuid4()),
                    action_type=ActionType.AGENT_INTERACTION,
                    name="Document Summarization",
                    description="Generate document summary",
                    parameters={
                        "agent": "AIC",
                        "prompt": summary_prompt,
                        "temperature": 0.3,
                    },
                    retry_config={"max_attempts": 2, "delay_seconds": 10},
                )

                summary_result = await self._handle_agent_interaction(
                    agent_action, execution
                )
                return {
                    "operation": operation,
                    "file_path": file_path,
                    "summary": summary_result["response"],
                }

            else:
                raise Exception(f"Unsupported document operation: {operation}")

        except Exception as e:
            self.logger.error(f"Document processing failed: {e}")
            raise

    async def _handle_task_creation(
        self, action: WorkflowAction, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Handle task creation - Enhanced for OS Dashboard"""
        try:
            params = action.parameters

            # Create task using existing database
            task_data = {
                "title": self._replace_variables(
                    params["title"], execution.execution_context
                ),
                "description": self._replace_variables(
                    params.get("description", ""), execution.execution_context
                ),
                "project": params.get("project", "General"),
                "priority": params.get("priority", "medium"),
                "due_date": params.get("due_date"),
                "owner": params.get("owner", "workflow"),
                "status": "TODO",
                "created_at": datetime.now().isoformat(),
                "depends_on": params.get("depends_on"),
                "template_id": params.get("template_id"),
            }

            # Only create actual task if Task class is available
            if Task and db_insert_task:
                task = Task(
                    id=0,
                    title=task_data["title"],
                    project=task_data["project"],
                    status=task_data["status"],
                    priority=task_data["priority"],
                    due_date=task_data["due_date"] or "",
                    notes=task_data["description"],
                    owner=task_data["owner"],
                    created_at=datetime.now().isoformat(),
                    depends_on=task_data.get("depends_on"),
                    recurrence_pattern=None,
                    recurrence_end=None,
                    time_estimated=None,
                    time_logged=None,
                    template_id=task_data.get("template_id"),
                )

                if self.app_state and hasattr(self.app_state, "conn"):
                    task.id = db_insert_task(self.app_state.conn, task)
                else:
                    task.id = (
                        len(execution.execution_context.get("created_tasks", [])) + 1
                    )

                # Track created tasks
                if "created_tasks" not in execution.execution_context:
                    execution.execution_context["created_tasks"] = []
                execution.execution_context["created_tasks"].append(asdict(task))

                result = {
                    "task_id": task.id,
                    "title": task.title,
                    "project": task.project,
                    "priority": task.priority,
                    "created_at": task.created_at,
                }

                self.logger.info(f"Task created via workflow: {task.title}")
            else:
                # Fallback: just simulate task creation
                task_id = len(execution.execution_context.get("created_tasks", [])) + 1

                # Track simulated tasks
                if "created_tasks" not in execution.execution_context:
                    execution.execution_context["created_tasks"] = []
                execution.execution_context["created_tasks"].append(task_data)

                result = {
                    "task_id": task_id,
                    "title": task_data["title"],
                    "project": task_data["project"],
                    "priority": task_data["priority"],
                    "status": "simulated",
                }

                self.logger.info(
                    f"Task creation simulated (no database available): {task_data['title']}"
                )

            return result

        except Exception as e:
            self.logger.error(f"Task creation failed: {e}")
            raise

    # Placeholder implementations for other action types
    async def _handle_api_call(
        self, action: WorkflowAction, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Handle API call action"""
        # Implementation similar to original
        params = action.parameters
        return {
            "status": "simulated",
            "message": f'API call to {params.get("url", "unknown")}',
        }

    async def _handle_email_send(
        self, action: WorkflowAction, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Handle email send action"""
        params = action.parameters
        return {
            "recipient": params.get("to"),
            "subject": params.get("subject"),
            "status": "simulated",
        }

    async def _handle_file_operation(
        self, action: WorkflowAction, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Handle file operation action"""
        params = action.parameters
        return {
            "operation": params.get("operation"),
            "file_path": params.get("file_path"),
            "status": "simulated",
        }

    async def _handle_data_processing(
        self, action: WorkflowAction, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Handle data processing action"""
        params = action.parameters
        return {"operation": params.get("operation"), "status": "simulated"}

    async def _handle_notification(
        self, action: WorkflowAction, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Handle notification action"""
        params = action.parameters
        return {
            "type": params.get("type", "info"),
            "message": params.get("message"),
            "status": "sent",
        }

    async def _handle_report_generation(
        self, action: WorkflowAction, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Handle report generation action"""
        params = action.parameters
        return {
            "report_type": params.get("type"),
            "title": params.get("title"),
            "status": "generated",
        }

    async def _handle_system_command(
        self, action: WorkflowAction, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Handle system command action"""
        params = action.parameters
        return {"command": params.get("command"), "status": "simulated"}

    async def _handle_ai_analysis(
        self, action: WorkflowAction, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Handle AI analysis action"""
        params = action.parameters
        return {
            "analysis_type": params.get("analysis_type"),
            "confidence": 0.85,
            "status": "completed",
        }

    async def _handle_workflow_trigger(
        self, action: WorkflowAction, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Handle workflow trigger action"""
        params = action.parameters
        target_workflow_id = params["workflow_id"]

        new_execution_id = await self.trigger_workflow(
            target_workflow_id,
            {"triggered_by_workflow": execution.execution_id},
            f"workflow_{execution.workflow_id}",
        )

        return {
            "triggered_workflow_id": target_workflow_id,
            "new_execution_id": new_execution_id,
        }

    # Trigger Handlers

    async def _handle_time_trigger(
        self,
        workflow: WorkflowDefinition,
        trigger: WorkflowTrigger,
        event_data: Dict[str, Any],
    ):
        """Handle time-based trigger"""
        pass  # Simplified

    async def _handle_event_trigger(
        self,
        workflow: WorkflowDefinition,
        trigger: WorkflowTrigger,
        event_data: Dict[str, Any],
    ):
        """Handle event-based trigger"""
        pass  # Simplified

    async def _handle_condition_trigger(
        self,
        workflow: WorkflowDefinition,
        trigger: WorkflowTrigger,
        event_data: Dict[str, Any],
    ):
        """Handle condition-based trigger"""
        pass  # Simplified

    async def _handle_user_trigger(
        self,
        workflow: WorkflowDefinition,
        trigger: WorkflowTrigger,
        event_data: Dict[str, Any],
    ):
        """Handle user-initiated trigger"""
        pass  # Simplified

    async def _handle_ai_trigger(
        self,
        workflow: WorkflowDefinition,
        trigger: WorkflowTrigger,
        event_data: Dict[str, Any],
    ):
        """Handle AI-suggested trigger"""
        pass  # Simplified

    async def _handle_dependency_trigger(
        self,
        workflow: WorkflowDefinition,
        trigger: WorkflowTrigger,
        event_data: Dict[str, Any],
    ):
        """Handle dependency-based trigger"""
        pass  # Simplified

    def _replace_variables(self, text: str, context: Dict[str, Any]) -> str:
        """Replace variables in text with context values"""
        try:
            if not isinstance(text, str):
                return text

            import re

            # Replace ${variable} patterns
            def replace_var(match):
                var_name = match.group(1)
                return str(context.get(var_name, match.group(0)))

            return re.sub(r"\$\{([^}]+)\}", replace_var, text)

        except Exception as e:
            self.logger.warning(f"Variable replacement failed: {e}")
            return text

    # Event System Integration

    async def _emit_event(self, event_type: str, event_data: Dict[str, Any]):
        """Emit event to event system"""
        try:
            event = {
                "event_id": str(uuid.uuid4()),
                "event_type": event_type,
                "data": event_data,
                "timestamp": datetime.now().isoformat(),
            }

            await self.event_queue.put(event)

            # Also emit to GUI if available
            if self.app_state and hasattr(self.app_state, "emit_event"):
                await self.app_state.emit_event(event_type, event_data)

        except Exception as e:
            self.logger.error(f"Event emission failed: {e}")

    # Automation Rules

    async def create_automation_rule(self, rule_data: Dict[str, Any]) -> str:
        """Create intelligent automation rule"""
        try:
            rule_id = str(uuid.uuid4())

            rule = AutomationRule(
                rule_id=rule_id,
                name=rule_data["name"],
                description=rule_data.get("description", ""),
                conditions=rule_data["conditions"],
                actions=rule_data["actions"],
                priority=Priority(rule_data.get("priority", 2)),
                confidence_threshold=rule_data.get("confidence_threshold", 0.8),
                learning_enabled=rule_data.get("learning_enabled", True),
                success_rate=1.0,
                usage_count=0,
                created_at=datetime.now(),
                last_used=None,
                enabled=rule_data.get("enabled", True),
            )

            self.automation_rules[rule_id] = rule

            self.logger.info(f"Automation rule created: {rule.name} ({rule_id})")
            return rule_id

        except Exception as e:
            self.logger.error(f"Automation rule creation failed: {e}")
            raise

    async def evaluate_automation_rules(
        self, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Evaluate automation rules against context"""
        try:
            suggestions = []

            for rule in self.automation_rules.values():
                if not rule.enabled:
                    continue

                # Evaluate rule conditions
                confidence = self._evaluate_rule_conditions(rule.conditions, context)

                if confidence >= rule.confidence_threshold:
                    suggestion = {
                        "rule_id": rule.rule_id,
                        "rule_name": rule.name,
                        "confidence": confidence,
                        "priority": rule.priority.value,
                        "actions": rule.actions,
                        "success_rate": rule.success_rate,
                    }
                    suggestions.append(suggestion)

            # Sort by priority and confidence
            suggestions.sort(
                key=lambda x: (x["priority"], x["confidence"]), reverse=True
            )

            return suggestions

        except Exception as e:
            self.logger.error(f"Automation rule evaluation failed: {e}")
            return []

    def _evaluate_rule_conditions(
        self, conditions: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> float:
        """Evaluate rule conditions and return confidence score"""
        try:
            if not conditions:
                return 0.0

            total_confidence = 0.0

            for condition in conditions:
                condition_type = condition.get("type")

                if condition_type == "value_match":
                    field = condition["field"]
                    expected_value = condition["value"]
                    actual_value = context.get(field)

                    if actual_value == expected_value:
                        total_confidence += condition.get("weight", 1.0)

                elif condition_type == "range_check":
                    field = condition["field"]
                    min_value = condition.get("min_value")
                    max_value = condition.get("max_value")
                    actual_value = context.get(field)

                    if (
                        actual_value is not None
                        and (min_value is None or actual_value >= min_value)
                        and (max_value is None or actual_value <= max_value)
                    ):
                        total_confidence += condition.get("weight", 1.0)

                elif condition_type == "pattern_match":
                    field = condition["field"]
                    pattern = condition["pattern"]
                    actual_value = str(context.get(field, ""))

                    import re

                    if re.search(pattern, actual_value):
                        total_confidence += condition.get("weight", 1.0)

            # Normalize confidence
            max_confidence = sum(c.get("weight", 1.0) for c in conditions)
            return total_confidence / max_confidence if max_confidence > 0 else 0.0

        except Exception as e:
            self.logger.error(f"Rule condition evaluation failed: {e}")
            return 0.0

    # Scheduler Integration

    def _start_scheduler(self):
        """Start the scheduler thread"""
        # Integrate with existing sync_scheduler if available
        try:
            if self.app_state and hasattr(self.app_state, "scheduler"):
                # Use existing scheduler
                self.logger.info("Using existing sync_scheduler")
            else:
                # Fallback to basic scheduler
                self.logger.info("Using basic scheduler fallback")
        except Exception as e:
            self.logger.error(f"Scheduler integration failed: {e}")

    # Sample Workflows

    async def create_sample_workflows(self):
        """Create sample workflows demonstrating OS Dashboard integration"""
        try:
            # Sample 1: Daily AI-Powered Task Review
            daily_review_workflow = {
                "name": "Daily Task Review & Optimization",
                "description": "AI-powered daily task review and optimization",
                "triggers": [
                    {
                        "type": "time_based",
                        "schedule_config": {"type": "daily", "time": "09:00"},
                    }
                ],
                "actions": [
                    {
                        "type": "agent_interaction",
                        "name": "Analyze Task Patterns",
                        "parameters": {
                            "agent": "AIC",
                            "prompt": "Analyze my recent task completion patterns and identify optimization opportunities.",
                            "context_data": {"analysis_type": "productivity"},
                        },
                    },
                    {
                        "type": "task_creation",
                        "name": "Create Optimization Tasks",
                        "parameters": {
                            "title": "Implement Task Optimization: ${action_analyze_task_patterns_result_insights_0}",
                            "description": "Based on AI analysis: ${action_analyze_task_patterns_result_response}",
                            "priority": "medium",
                            "project": "Productivity",
                        },
                        "depends_on": ["analyze_task_patterns"],
                    },
                    {
                        "type": "notification",
                        "name": "Send Daily Summary",
                        "parameters": {
                            "type": "daily_summary",
                            "title": "Daily Task Optimization Report",
                            "message": "AIC has analyzed your tasks and created optimization suggestions.",
                            "recipient": "user",
                        },
                    },
                ],
                "variables": {"user_name": "Chris", "analysis_depth": "comprehensive"},
                "priority": 3,
                "tags": ["productivity", "ai-powered", "daily"],
            }

            # Sample 2: Document Processing Workflow
            doc_processing_workflow = {
                "name": "Smart Document Processing",
                "description": "Automatically process uploaded documents and extract actionable items",
                "triggers": [
                    {
                        "type": "event_based",
                        "event_filters": {"event_type": "document_uploaded"},
                    }
                ],
                "actions": [
                    {
                        "type": "document_processing",
                        "name": "Extract Tasks from Document",
                        "parameters": {
                            "operation": "extract_tasks",
                            "file_path": "${event_data_file_path}",
                            "project": "${event_data_project}",
                            "owner": "${event_data_owner}",
                        },
                    },
                    {
                        "type": "agent_interaction",
                        "name": "Summarize Document",
                        "parameters": {
                            "agent": "Aria",
                            "prompt": "Please provide a comprehensive summary of this document and highlight key action items.",
                            "context_data": {
                                "document_path": "${event_data_file_path}"
                            },
                        },
                    },
                    {
                        "type": "task_creation",
                        "name": "Create Summary Task",
                        "parameters": {
                            "title": "Document Summary: ${event_data_file_name}",
                            "description": "${action_summarize_document_result_response}",
                            "priority": "medium",
                            "project": "${event_data_project}",
                        },
                        "depends_on": ["summarize_document"],
                    },
                ],
                "variables": {},
                "priority": 2,
                "tags": ["documents", "automation", "ai-processing"],
            }

            # Create the sample workflows
            workflow1_id = await self.create_workflow(daily_review_workflow)
            workflow2_id = await self.create_workflow(doc_processing_workflow)

            self.logger.info(
                f"Created sample workflows: {workflow1_id}, {workflow2_id}"
            )
            return [workflow1_id, workflow2_id]

        except Exception as e:
            self.logger.error(f"Sample workflow creation failed: {e}")
            return []

    # API Methods

    async def get_system_dashboard(self) -> Dict[str, Any]:
        """Get automation system dashboard data"""
        try:
            current_time = datetime.now()

            # Active executions
            active_executions = [
                e
                for e in self.executions.values()
                if e.status == WorkflowStatus.RUNNING
            ]

            # Recent executions (last 24 hours)
            recent_executions = [
                e
                for e in self.executions.values()
                if (current_time - e.start_time).total_seconds() < 86400
            ]

            # Success rate
            completed_recent = [
                e
                for e in recent_executions
                if e.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]
            ]

            success_rate = 0.0
            if completed_recent:
                successful = len(
                    [
                        e
                        for e in completed_recent
                        if e.status == WorkflowStatus.COMPLETED
                    ]
                )
                success_rate = successful / len(completed_recent)

            return {
                "timestamp": current_time.isoformat(),
                "workflows": {
                    "total": len(self.workflows),
                    "enabled": len([w for w in self.workflows.values() if w.enabled]),
                    "disabled": len(
                        [w for w in self.workflows.values() if not w.enabled]
                    ),
                },
                "executions": {
                    "active": len(active_executions),
                    "recent_24h": len(recent_executions),
                    "success_rate_24h": success_rate,
                    "total": len(self.executions),
                },
                "automation_rules": {
                    "total": len(self.automation_rules),
                    "enabled": len(
                        [r for r in self.automation_rules.values() if r.enabled]
                    ),
                },
                "performance": self.performance_metrics,
                "optimization_suggestions": len(self.optimization_suggestions),
                "system_health": "healthy"
                if success_rate > 0.8
                else "warning"
                if success_rate > 0.6
                else "critical",
            }

        except Exception as e:
            self.logger.error(f"System dashboard generation failed: {e}")
            return {"error": str(e)}

    async def shutdown(self):
        """Shutdown automation system"""
        # Cancel active executions
        for execution_id in list(self.active_executions.keys()):
            await self.cancel_execution(execution_id)

        self.logger.info("Automation Orchestrator shutdown complete")

    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel running execution"""
        try:
            execution = self.executions.get(execution_id)
            if not execution:
                return False

            if execution.status != WorkflowStatus.RUNNING:
                return False

            # Cancel the task
            task = self.active_executions.get(execution_id)
            if task:
                task.cancel()
                del self.active_executions[execution_id]

            # Update execution status
            execution.status = WorkflowStatus.CANCELLED
            execution.end_time = datetime.now()

            self.logger.info(f"Execution cancelled: {execution_id}")
            return True

        except Exception as e:
            self.logger.error(f"Execution cancellation failed: {e}")
            return False

    # Placeholder implementations for compatibility
    def _build_action_graph(self, actions):
        graph = {}
        for action in actions:
            graph[action.action_id] = action.depends_on or []
        return graph

    def _ingest_action_signal(
        self,
        signal_type: str,
        action: WorkflowAction,
        execution: WorkflowExecution,
        attempt: int,
        max_attempts: int,
    ) -> None:
        if not self.failure_registry:
            return
        self.failure_registry.ingest_signal(
            source="automation_orchestrator",
            metric=f"action_{signal_type}_{action.action_type.value}",
            value=attempt,
            threshold=max_attempts,
            workflow_id=execution.workflow_id,
            action_id=action.action_id,
        )

    def _record_action_failure(
        self, action: WorkflowAction, execution: WorkflowExecution, reason: str
    ) -> None:
        if not self.failure_registry:
            return
        root_cause_map = {
            ActionType.SYSTEM_COMMAND: FailureRootCause.RESOURCE_EXHAUSTION,
            ActionType.FILE_OPERATION: FailureRootCause.DEPENDENCY_FAILURE,
            ActionType.DATA_PROCESSING: FailureRootCause.DEPENDENCY_FAILURE,
            ActionType.DOCUMENT_PROCESSING: FailureRootCause.DATA_CORRUPTION,
            ActionType.AGENT_INTERACTION: FailureRootCause.COGNITIVE_MISALIGNMENT,
        }
        root_cause = root_cause_map.get(
            action.action_type, FailureRootCause.DEPENDENCY_FAILURE
        )
        severity = (
            FailureSeverity.SEV2
            if action.retry_config.get("required", True)
            else FailureSeverity.SEV3
        )
        scope = (
            FailureScope.TENANT
            if execution.execution_context.get("tenant_id")
            else FailureScope.PROJECT
        )
        recovery_plan = (
            "driver_failover"
            if action.action_type
            in {
                ActionType.SYSTEM_COMMAND,
                ActionType.FILE_OPERATION,
                ActionType.DOCUMENT_PROCESSING,
            }
            else "automation_workflow_recovery"
        )
        self.failure_registry.record_event(
            plane=FailurePlane.CONTROL,
            layer=FailureLayer.DOMAIN,
            scope=scope,
            severity=severity,
            root_cause=root_cause,
            description=f"Workflow action '{action.name}' failed: {reason}",
            metadata={
                "workflow_id": execution.workflow_id,
                "action_id": action.action_id,
                "action_type": action.action_type.value,
            },
            recovery_plan=recovery_plan,
            risk_inputs={
                "impact": 4 if severity == FailureSeverity.SEV2 else 3,
                "likelihood": 3,
                "scope": 3 if scope == FailureScope.TENANT else 2,
                "control_strength": 3,
            },
        )

    def _record_workflow_failure(
        self, execution: WorkflowExecution, reason: str
    ) -> None:
        if not self.failure_registry:
            return
        scope = (
            FailureScope.TENANT
            if execution.execution_context.get("tenant_id")
            else FailureScope.PROJECT
        )
        self.failure_registry.record_event(
            plane=FailurePlane.CONTROL,
            layer=FailureLayer.DOMAIN,
            scope=scope,
            severity=FailureSeverity.SEV2
            if execution.failed_actions
            else FailureSeverity.SEV3,
            root_cause=FailureRootCause.DEPENDENCY_FAILURE,
            description=f"Workflow {execution.workflow_id} failed: {reason}",
            metadata={
                "workflow_id": execution.workflow_id,
                "failed_actions": execution.failed_actions,
            },
            recovery_plan="workflow_retry",
            risk_inputs={
                "impact": 4,
                "likelihood": 3,
                "scope": 3 if scope == FailureScope.TENANT else 2,
                "control_strength": 3,
            },
        )

    def _action_dependencies_met(self, action, completed_actions):
        if not action.depends_on:
            return True
        return all(dep_id in completed_actions for dep_id in action.depends_on)

    def _evaluate_condition(self, condition, context):
        return True  # Simplified

    async def _register_workflow_triggers(self, workflow):
        pass  # Simplified

    async def _record_execution_history(self, execution, workflow):
        pass  # Simplified

    async def _event_processor(self):
        pass  # Simplified

    async def _execution_monitor(self):
        pass  # Simplified

    async def _performance_analyzer(self):
        pass  # Simplified

    async def _optimization_engine(self):
        pass  # Simplified

    async def _load_workflows(self):
        pass  # Simplified

    async def _load_automation_rules(self):
        pass  # Simplified


_spec_registry = get_default_registry()
_spec_registry.register_feature(
    "assistant_core.automation_orchestrator",
    sections=["2.2", "7.13", "8.10", "8.13", "14.1", "14.3"],
    metadata={
        "module": __name__,
        "capability": "workflow_orchestration_engine",
    },
)
