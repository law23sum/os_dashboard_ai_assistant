# Workflow Orchestration Engine

This directory contains workflow definitions for the OS Dashboard AI Assistant's daemon framework. Workflows are JSON files that define automated processes triggered by various events in the system.

## Workflow Structure

Each workflow JSON file contains:

```json
{
  "workflow_id": "unique-identifier",
  "name": "Human readable name",
  "description": "What this workflow does",
  "enabled": true,
  "variables": {
    "key": "value"
  },
  "triggers": [
    {
      "trigger_type": "event_type",
      "config": {
        "specific": "configuration"
      },
      "enabled": true
    }
  ],
  "actions": [
    {
      "action_id": "unique_action_id",
      "action_type": "read_resource|write_resource|transform_data|conditional|send_notification",
      "config": {
        "action_specific": "configuration"
      },
      "depends_on": ["other_action_ids"],
      "retry_count": 3,
      "timeout_seconds": 300
    }
  ]
}
```

## Trigger Types

- `schedule`: Time-based triggers
- `file_change`: File system change events
- `webhook`: HTTP webhook events
- `manual`: Manual trigger
- `connector_event`: Events from API connectors
- `system_event`: Internal system events

## Action Types

- `read_resource`: Read data from connectors
- `write_resource`: Write data to connectors
- `create_resource`: Create new resources
- `delete_resource`: Delete resources
- `transform_data`: Transform data between formats
- `send_notification`: Send notifications
- `execute_script`: Execute scripts
- `wait`: Wait for conditions
- `conditional`: Conditional logic
- `loop`: Loop constructs

## Variable Substitution

Use `${variable_name}` syntax for variable substitution:

- `${trigger_event.field}`: Access trigger event data
- `${action_results.action_id.field}`: Access results from previous actions
- `${workflow_variables.key}`: Access workflow variables
- `${context.field}`: Access execution context

## Available Connectors

- `filesystem`: Local file system operations
- `git`: Git repository operations
- `microsoft_graph`: Microsoft Office 365 services
- `openai`: OpenAI API integration
- `pdf`: PDF document processing
- `office_files`: Office document processing

## Example Workflows

1. **Document Processing**: Automatically processes uploaded documents
2. **Project Milestones**: Triggers on project completion milestones
3. **Urgent Tasks**: Escalates tasks approaching due dates

## Usage

Workflows are automatically loaded by the WorkflowEngine when it starts. The engine monitors for trigger events and executes matching workflows asynchronously.

To create a new workflow:

1. Create a new JSON file in this directory
2. Define triggers, actions, and dependencies
3. Test with sample events
4. Enable the workflow

## Monitoring

Use the WorkflowEngine's `get_workflow_statistics()` method to monitor:

- Total workflows and enabled count
- Execution statistics
- Recent activity
- Queue status
