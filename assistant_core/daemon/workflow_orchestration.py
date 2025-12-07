"""
Daemon Framework and Orchestration Engine

Provides automated workflows, event-driven processing, and system orchestration

"""

import asyncio

from typing import List, Dict, Any, Optional, Callable, Union

from datetime import datetime, timedelta

from dataclasses import dataclass, asdict

from enum import Enum

import json

import uuid

from pathlib import Path

import logging

from abc import ABC, abstractmethod



from ..cir.schema import CIRDocument, ContentType, SourceSystem

from ...api_connectors.universal_connector import BaseConnector, OperationResult





class TriggerType(Enum):

    """Types of workflow triggers"""

    SCHEDULE = "schedule"

    FILE_CHANGE = "file_change"

    WEBHOOK = "webhook"

    MANUAL = "manual"

    CONNECTOR_EVENT = "connector_event"

    SYSTEM_EVENT = "system_event"





class WorkflowStatus(Enum):

    """Workflow execution status"""

    PENDING = "pending"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"

    PAUSED = "paused"





class ActionType(Enum):

    """Types of workflow actions"""

    READ_RESOURCE = "read_resource"

    WRITE_RESOURCE = "write_resource"

    CREATE_RESOURCE = "create_resource"

    DELETE_RESOURCE = "delete_resource"

    TRANSFORM_DATA = "transform_data"

    SEND_NOTIFICATION = "send_notification"

    EXECUTE_SCRIPT = "execute_script"

    WAIT = "wait"

    CONDITIONAL = "conditional"

    LOOP = "loop"





@dataclass

class WorkflowTrigger:

    """Workflow trigger configuration"""

    trigger_type: TriggerType

    config: Dict[str, Any]

    enabled: bool = True



    def matches_event(self, event: Dict[str, Any]) -> bool:

        """Check if this trigger matches the given event"""

        if not self.enabled:

            return False



        if self.trigger_type == TriggerType.SCHEDULE:

            # Schedule triggers are handled separately

            return False



        elif self.trigger_type == TriggerType.FILE_CHANGE:

            return (

                event.get('type') == 'file_change' and

                event.get('path', '').startswith(self.config.get('watch_path', ''))

            )



        elif self.trigger_type == TriggerType.WEBHOOK:

            return (

                event.get('type') == 'webhook' and

                event.get('endpoint') == self.config.get('endpoint')

            )



        elif self.trigger_type == TriggerType.CONNECTOR_EVENT:

            return (

                event.get('type') == 'connector_event' and

                event.get('connector') == self.config.get('connector') and

                event.get('event_type') == self.config.get('event_type')

            )



        return False





@dataclass

class WorkflowAction:

    """Individual workflow action"""

    action_id: str

    action_type: ActionType

    config: Dict[str, Any]

    depends_on: List[str] = None

    retry_count: int = 3

    timeout_seconds: int = 300



    def __post_init__(self):

        if self.depends_on is None:

            self.depends_on = []





@dataclass

class WorkflowDefinition:

    """Complete workflow definition"""

    workflow_id: str

    name: str

    description: str

    triggers: List[WorkflowTrigger]

    actions: List[WorkflowAction]

    variables: Dict[str, Any] = None

    enabled: bool = True

    created_at: datetime = None

    updated_at: datetime = None



    def __post_init__(self):

        if self.variables is None:

            self.variables = {}

        if self.created_at is None:

            self.created_at = datetime.utcnow()

        if self.updated_at is None:

            self.updated_at = datetime.utcnow()





@dataclass

class WorkflowExecution:

    """Workflow execution instance"""

    execution_id: str

    workflow_id: str

    status: WorkflowStatus

    started_at: datetime

    completed_at: Optional[datetime] = None

    trigger_event: Dict[str, Any] = None

    context: Dict[str, Any] = None

    action_results: Dict[str, Any] = None

    error_message: Optional[str] = None



    def __post_init__(self):

        if self.trigger_event is None:

            self.trigger_event = {}

        if self.context is None:

            self.context = {}

        if self.action_results is None:

            self.action_results = {}





class WorkflowActionExecutor(ABC):

    """Base class for workflow action executors"""



    @abstractmethod

    async def execute(self, action: WorkflowAction, context: Dict[str, Any],

                     connectors: Dict[str, BaseConnector]) -> Dict[str, Any]:

        """Execute the action and return results"""

        pass





class ReadResourceExecutor(WorkflowActionExecutor):

    """Executor for reading resources from connectors"""



    async def execute(self, action: WorkflowAction, context: Dict[str, Any],

                     connectors: Dict[str, BaseConnector]) -> Dict[str, Any]:

        connector_name = action.config.get('connector')

        resource_id = action.config.get('resource_id')



        if not connector_name or not resource_id:

            raise ValueError("Connector and resource_id required for read_resource action")



        if connector_name not in connectors:

            raise ValueError(f"Connector {connector_name} not available")



        connector = connectors[connector_name]



        # Substitute variables in resource_id

        resource_id = self._substitute_variables(resource_id, context)



        result = await connector.read_resource(resource_id, action.config.get('options', {}))



        if not result.success:

            raise Exception(f"Failed to read resource: {result.error}")



        return {

            'resource_id': resource_id,

            'content': result.data,

            'connector': connector_name

        }



    def _substitute_variables(self, text: str, context: Dict[str, Any]) -> str:

        """Substitute variables in text using context"""

        for key, value in context.items():

            text = text.replace(f"${{{key}}}", str(value))

        return text





class WriteResourceExecutor(WorkflowActionExecutor):

    """Executor for writing resources to connectors"""



    async def execute(self, action: WorkflowAction, context: Dict[str, Any],

                     connectors: Dict[str, BaseConnector]) -> Dict[str, Any]:

        connector_name = action.config.get('connector')

        resource_id = action.config.get('resource_id')

        content_source = action.config.get('content_source')  # Action ID to get content from



        if not connector_name or not resource_id:

            raise ValueError("Connector and resource_id required for write_resource action")



        if connector_name not in connectors:

            raise ValueError(f"Connector {connector_name} not available")



        # Get content from previous action or context

        if content_source and content_source in context.get('action_results', {}):

            content = context['action_results'][content_source].get('content')

        else:

            content = action.config.get('content')



        if not content:

            raise ValueError("No content provided for write_resource action")



        connector = connectors[connector_name]



        # Substitute variables

        resource_id = self._substitute_variables(resource_id, context)



        result = await connector.write_resource(resource_id, content, action.config.get('options', {}))



        if not result.success:

            raise Exception(f"Failed to write resource: {result.error}")



        return {

            'resource_id': resource_id,

            'result': result.data,

            'connector': connector_name

        }



    def _substitute_variables(self, text: str, context: Dict[str, Any]) -> str:

        """Substitute variables in text using context"""

        for key, value in context.items():

            text = text.replace(f"${{{key}}}", str(value))

        return text





class TransformDataExecutor(WorkflowActionExecutor):

    """Executor for data transformation actions"""



    async def execute(self, action: WorkflowAction, context: Dict[str, Any],

                     connectors: Dict[str, BaseConnector]) -> Dict[str, Any]:

        transform_type = action.config.get('transform_type')

        source_action = action.config.get('source_action')



        if not source_action or source_action not in context.get('action_results', {}):

            raise ValueError("Source action not found for transform_data")



        source_data = context['action_results'][source_action]



        if transform_type == 'extract_text':

            # Extract text from CIR document

            if isinstance(source_data.get('content'), CIRDocument):

                transformed_data = source_data['content'].get_all_text()

            else:

                transformed_data = str(source_data.get('content', ''))



        elif transform_type == 'json_extract':

            # Extract specific fields from JSON

            fields = action.config.get('fields', [])

            source_content = source_data.get('content')



            if isinstance(source_content, dict):

                transformed_data = {field: source_content.get(field) for field in fields}

            else:

                transformed_data = {}



        elif transform_type == 'format_template':

            # Format using template

            template = action.config.get('template', '')

            template_vars = {**context, **source_data}

            transformed_data = template.format(**template_vars)



        else:

            raise ValueError(f"Unknown transform type: {transform_type}")



        return {

            'transformed_data': transformed_data,

            'source_action': source_action,

            'transform_type': transform_type

        }





class ConditionalExecutor(WorkflowActionExecutor):

    """Executor for conditional logic"""



    async def execute(self, action: WorkflowAction, context: Dict[str, Any],

                     connectors: Dict[str, BaseConnector]) -> Dict[str, Any]:

        condition = action.config.get('condition')

        condition_type = action.config.get('condition_type', 'simple')



        if condition_type == 'simple':

            # Simple variable comparison

            left = self._get_value(action.config.get('left'), context)

            operator = action.config.get('operator', '==')

            right = self._get_value(action.config.get('right'), context)



            result = self._evaluate_condition(left, operator, right)



        elif condition_type == 'expression':

            # Python expression evaluation (be careful with security)

            result = self._evaluate_expression(condition, context)



        else:

            raise ValueError(f"Unknown condition type: {condition_type}")



        return {

            'condition_result': result,

            'condition': condition,

            'condition_type': condition_type

        }



    def _get_value(self, value_config: Any, context: Dict[str, Any]) -> Any:

        """Get value from config, which can be literal or reference"""

        if isinstance(value_config, dict):

            if 'action_result' in value_config:

                action_id = value_config['action_result']

                field = value_config.get('field')



                if action_id in context.get('action_results', {}):

                    result = context['action_results'][action_id]

                    return result.get(field) if field else result



            elif 'context' in value_config:

                return context.get(value_config['context'])





        return value_config



    def _evaluate_condition(self, left: Any, operator: str, right: Any) -> bool:

        """Evaluate simple condition"""

        if operator == '==':

            return left == right

        elif operator == '!=':

            return left != right

        elif operator == '<':

            return left < right

        elif operator == '>':

            return left > right

        elif operator == '<=':

            return left <= right

        elif operator == '>=':

            return left >= right

        elif operator == 'in':

            return left in right

        elif operator == 'contains':

            return str(right) in str(left)

        else:

            return False



    def _evaluate_expression(self, expression: str, context: Dict[str, Any]) -> bool:

        """Evaluate Python expression (restricted)"""

        # This is a simplified and potentially unsafe implementation

        # In production, use a proper expression evaluator with sandboxing

        try:

            # Create safe namespace

            namespace = {

                'context': context,

                'action_results': context.get('action_results', {}),

                # Add safe built-ins

                'len': len,

                'str': str,

                'int': int,

                'float': float,

                'bool': bool,

            }



            return bool(eval(expression, {"__builtins__": {}}, namespace))

        except Exception:

            return False





class WorkflowEngine:

    """Main workflow orchestration engine"""



    def __init__(self, config_path: str = "workflows"):

        self.config_path = Path(config_path)

        self.config_path.mkdir(exist_ok=True)



        self.workflows: Dict[str, WorkflowDefinition] = {}

        self.executions: Dict[str, WorkflowExecution] = {}

        self.connectors: Dict[str, BaseConnector] = {}



        # Action executors

        self.executors = {

            ActionType.READ_RESOURCE: ReadResourceExecutor(),

            ActionType.WRITE_RESOURCE: WriteResourceExecutor(),

            ActionType.TRANSFORM_DATA: TransformDataExecutor(),

            ActionType.CONDITIONAL: ConditionalExecutor(),

        }



        # Background tasks

        self.scheduler_task = None

        self.event_processor_task = None

        self.event_queue = asyncio.Queue()



        self.logger = logging.getLogger(__name__)



    async def start(self):

        """Start the workflow engine"""

        # Load workflows

        await self.load_workflows()



        # Start background tasks

        self.scheduler_task = asyncio.create_task(self._scheduler_loop())

        self.event_processor_task = asyncio.create_task(self._event_processor_loop())



        self.logger.info("Workflow engine started")



    async def stop(self):

        """Stop the workflow engine"""

        # Cancel background tasks

        if self.scheduler_task:

            self.scheduler_task.cancel()

            try:

                await self.scheduler_task

            except asyncio.CancelledError:

                pass



        if self.event_processor_task:

            self.event_processor_task.cancel()

            try:

                await self.event_processor_task

            except asyncio.CancelledError:

                pass



        self.logger.info("Workflow engine stopped")



    def register_connector(self, name: str, connector: BaseConnector):

        """Register a connector for use in workflows"""

        self.connectors[name] = connector



    async def load_workflows(self):

        """Load workflow definitions from disk"""

        for workflow_file in self.config_path.glob("*.json"):

            try:

                with open(workflow_file, 'r') as f:

                    workflow_data = json.load(f)



                workflow = self._deserialize_workflow(workflow_data)

                self.workflows[workflow.workflow_id] = workflow



                self.logger.info(f"Loaded workflow: {workflow.name}")



            except Exception as e:

                self.logger.error(f"Failed to load workflow {workflow_file}: {e}")



    async def save_workflow(self, workflow: WorkflowDefinition):

        """Save workflow definition to disk"""

        workflow_file = self.config_path / f"{workflow.workflow_id}.json"



        try:

            workflow_data = self._serialize_workflow(workflow)



            with open(workflow_file, 'w') as f:

                json.dump(workflow_data, f, indent=2, default=str)



            self.workflows[workflow.workflow_id] = workflow

            self.logger.info(f"Saved workflow: {workflow.name}")



        except Exception as e:

            self.logger.error(f"Failed to save workflow {workflow.workflow_id}: {e}")

            raise



    async def delete_workflow(self, workflow_id: str):

        """Delete workflow definition"""

        workflow_file = self.config_path / f"{workflow_id}.json"



        if workflow_file.exists():

            workflow_file.unlink()



        if workflow_id in self.workflows:

            del self.workflows[workflow_id]



        self.logger.info(f"Deleted workflow: {workflow_id}")



    async def trigger_workflow(self, workflow_id: str, event: Dict[str, Any] = None) -> str:

        """Manually trigger a workflow"""

        if workflow_id not in self.workflows:

            raise ValueError(f"Workflow {workflow_id} not found")



        workflow = self.workflows[workflow_id]



        if not workflow.enabled:

            raise ValueError(f"Workflow {workflow_id} is disabled")



        execution_id = str(uuid.uuid4())

        execution = WorkflowExecution(

            execution_id=execution_id,

            workflow_id=workflow_id,

            status=WorkflowStatus.PENDING,

            started_at=datetime.utcnow(),

            trigger_event=event or {'type': 'manual'},

            context={'workflow_variables': workflow.variables}

        )



        self.executions[execution_id] = execution



        # Start execution

        asyncio.create_task(self._execute_workflow(execution))



        return execution_id



    async def emit_event(self, event: Dict[str, Any]):

        """Emit an event that may trigger workflows"""

        await self.event_queue.put(event)



    async def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:

        """Get execution status"""

        return self.executions.get(execution_id)



    async def cancel_execution(self, execution_id: str):

        """Cancel a running execution"""

        if execution_id in self.executions:

            execution = self.executions[execution_id]

            if execution.status == WorkflowStatus.RUNNING:

                execution.status = WorkflowStatus.CANCELLED

                execution.completed_at = datetime.utcnow()



    async def _scheduler_loop(self):

        """Background scheduler for time-based triggers"""

        try:

            while True:

                current_time = datetime.utcnow()



                for workflow in self.workflows.values():

                    if not workflow.enabled:

                        continue



                    for trigger in workflow.triggers:

                        if trigger.trigger_type == TriggerType.SCHEDULE and trigger.enabled:

                            if self._should_trigger_schedule(trigger, current_time):

                                await self.trigger_workflow(

                                    workflow.workflow_id,

                                    {'type': 'schedule', 'time': current_time}

                                )



                # Check every minute

                await asyncio.sleep(60)



        except asyncio.CancelledError:

            raise

        except Exception as e:

            self.logger.error(f"Scheduler loop error: {e}")

            await asyncio.sleep(60)  # Continue after error



    async def _event_processor_loop(self):

        """Background event processor"""

        try:

            while True:

                event = await self.event_queue.get()



                # Find workflows that should be triggered by this event

                for workflow in self.workflows.values():

                    if not workflow.enabled:

                        continue



                    for trigger in workflow.triggers:

                        if trigger.matches_event(event):

                            await self.trigger_workflow(workflow.workflow_id, event)



        except asyncio.CancelledError:

            raise

        except Exception as e:

            self.logger.error(f"Event processor error: {e}")

            await asyncio.sleep(1)  # Continue after error



    async def _execute_workflow(self, execution: WorkflowExecution):

        """Execute a workflow"""

        try:

            execution.status = WorkflowStatus.RUNNING

            workflow = self.workflows[execution.workflow_id]



            self.logger.info(f"Starting workflow execution: {execution.execution_id}")



            # Build dependency graph

            dependency_graph = self._build_dependency_graph(workflow.actions)



            # Execute actions in dependency order

            completed_actions = set()



            while len(completed_actions) < len(workflow.actions):

                # Find actions that can be executed (dependencies satisfied)

                ready_actions = [

                    action for action in workflow.actions

                    if action.action_id not in completed_actions and

                    all(dep in completed_actions for dep in action.depends_on)

                ]



                if not ready_actions:

                    raise Exception("Circular dependency or unresolvable dependencies")



                # Execute ready actions in parallel

                tasks = []

                for action in ready_actions:

                    task = asyncio.create_task(self._execute_action(action, execution))

                    tasks.append((action.action_id, task))



                # Wait for all tasks to complete

                for action_id, task in tasks:

                    try:

                        result = await task

                        execution.action_results[action_id] = result

                        completed_actions.add(action_id)



                    except Exception as e:

                        self.logger.error(f"Action {action_id} failed: {e}")

                        execution.status = WorkflowStatus.FAILED

                        execution.error_message = str(e)

                        execution.completed_at = datetime.utcnow()

                        return



            # Workflow completed successfully

            execution.status = WorkflowStatus.COMPLETED

            execution.completed_at = datetime.utcnow()



            self.logger.info(f"Workflow execution completed: {execution.execution_id}")



        except Exception as e:

            self.logger.error(f"Workflow execution failed: {e}")

            execution.status = WorkflowStatus.FAILED

            execution.error_message = str(e)

            execution.completed_at = datetime.utcnow()



    async def _execute_action(self, action: WorkflowAction, execution: WorkflowExecution) -> Dict[str, Any]:

        """Execute a single action"""

        if action.action_type not in self.executors:

            raise ValueError(f"No executor for action type: {action.action_type}")



        executor = self.executors[action.action_type]



        # Prepare context

        context = {

            **execution.context,

            'action_results': execution.action_results,

            'trigger_event': execution.trigger_event,

            'execution_id': execution.execution_id,

            'workflow_id': execution.workflow_id

        }



        # Execute with timeout and retries

        for attempt in range(action.retry_count + 1):

            try:

                result = await asyncio.wait_for(

                    executor.execute(action, context, self.connectors),

                    timeout=action.timeout_seconds

                )

                return result



            except asyncio.TimeoutError:

                if attempt == action.retry_count:

                    raise Exception(f"Action {action.action_id} timed out after {action.timeout_seconds} seconds")

                await asyncio.sleep(2 ** attempt)  # Exponential backoff



            except Exception as e:

                if attempt == action.retry_count:

                    raise

                await asyncio.sleep(2 ** attempt)  # Exponential backoff



    def _build_dependency_graph(self, actions: List[WorkflowAction]) -> Dict[str, List[str]]:

        """Build dependency graph for actions"""

        graph = {}



        for action in actions:

            graph[action.action_id] = action.depends_on.copy()



        return graph



    def _should_trigger_schedule(self, trigger: WorkflowTrigger, current_time: datetime) -> bool:

        """Check if schedule trigger should fire"""

        schedule_type = trigger.config.get('schedule_type', 'interval')



        if schedule_type == 'interval':

            interval_seconds = trigger.config.get('interval_seconds', 3600)

            last_run = trigger.config.get('last_run')



            if not last_run:

                trigger.config['last_run'] = current_time.isoformat()

                return True



            last_run_time = datetime.fromisoformat(last_run)

            if (current_time - last_run_time).total_seconds() >= interval_seconds:

                trigger.config['last_run'] = current_time.isoformat()

                return True



        elif schedule_type == 'cron':

            # Simplified cron implementation

            # In production, use a proper cron library

            cron_expr = trigger.config.get('cron_expression', '0 * * * *')  # Every hour

            # This would need proper cron parsing

            pass



        return False



    def _serialize_workflow(self, workflow: WorkflowDefinition) -> Dict[str, Any]:

        """Serialize workflow to JSON-compatible dict"""

        return {

            'workflow_id': workflow.workflow_id,

            'name': workflow.name,

            'description': workflow.description,

            'enabled': workflow.enabled,

            'created_at': workflow.created_at.isoformat(),

            'updated_at': workflow.updated_at.isoformat(),

            'variables': workflow.variables,

            'triggers': [

                {

                    'trigger_type': trigger.trigger_type.value,

                    'config': trigger.config,

                    'enabled': trigger.enabled

                }

                for trigger in workflow.triggers

            ],

            'actions': [

                {

                    'action_id': action.action_id,

                    'action_type': action.action_type.value,

                    'config': action.config,

                    'depends_on': action.depends_on,

                    'retry_count': action.retry_count,

                    'timeout_seconds': action.timeout_seconds

                }

                for action in workflow.actions

            ]

        }



    def _deserialize_workflow(self, data: Dict[str, Any]) -> WorkflowDefinition:

        """Deserialize workflow from JSON-compatible dict"""

        triggers = [

            WorkflowTrigger(

                trigger_type=TriggerType(t['trigger_type']),

                config=t['config'],

                enabled=t.get('enabled', True)

            )

            for t in data.get('triggers', [])

        ]



        actions = [

            WorkflowAction(

                action_id=a['action_id'],

                action_type=ActionType(a['action_type']),

                config=a['config'],

                depends_on=a.get('depends_on', []),

                retry_count=a.get('retry_count', 3),

                timeout_seconds=a.get('timeout_seconds', 300)

            )

            for a in data.get('actions', [])

        ]



        return WorkflowDefinition(

            workflow_id=data['workflow_id'],

            name=data['name'],

            description=data['description'],

            triggers=triggers,

            actions=actions,

            variables=data.get('variables', {}),

            enabled=data.get('enabled', True),

            created_at=datetime.fromisoformat(data['created_at']),

            updated_at=datetime.fromisoformat(data['updated_at'])

        )



    async def get_workflow_statistics(self) -> Dict[str, Any]:

        """Get workflow engine statistics"""

        total_workflows = len(self.workflows)

        enabled_workflows = sum(1 for w in self.workflows.values() if w.enabled)



        # Execution statistics

        total_executions = len(self.executions)

        status_counts = {}

        for status in WorkflowStatus:

            status_counts[status.value] = sum(

                1 for e in self.executions.values() if e.status == status

            )



        # Recent executions (last 24 hours)

        recent_cutoff = datetime.utcnow() - timedelta(hours=24)

        recent_executions = [

            e for e in self.executions.values()

            if e.started_at > recent_cutoff

        ]



        return {

            'total_workflows': total_workflows,

            'enabled_workflows': enabled_workflows,

            'total_executions': total_executions,

            'execution_status_counts': status_counts,

            'recent_executions_24h': len(recent_executions),

            'registered_connectors': len(self.connectors),

            'queue_size': self.event_queue.qsize()

        }
