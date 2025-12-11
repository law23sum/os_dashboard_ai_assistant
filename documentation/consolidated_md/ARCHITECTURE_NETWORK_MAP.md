# OS Dashboard AI Assistant - Architecture Network Map

## Overview
This document maps the relationships between classes, functions, scripts, and daemons according to the Canon Technical Specification (OS DashboardAIAssistantTOC.txt).

## Architecture Layers (Per Spec Section 1.1)

### 1. Presentation Layer
- **GUI Components**: `assistant_hub_gui/assistant_hub/gui.py`
  - `AssistantGUI` - Main window
  - Connects to: Application Layer, Cognitive Layer
  
### 2. Application Layer  
- **Core Orchestrator**: `assistant_core/automation_orchestrator.py`
  - `AutomationOrchestrator` - Workflow orchestration
  - Connects to: Cognitive Layer, Domain Layer, Infrastructure Layer

- **AI Services**: `assistant_core/ai_services_api.py`
  - `AIServiceType` - Service types enum
  - Connects to: Model Layer, Cognitive Layer

### 3. Cognitive / Reasoning Layer (Spec Section 4)
- **Cognitive Framework**: `assistant_core/cognitive_framework.py`
  - `CognitiveFrameworkManager` - Main manager
  - `CognitivePersona` - Persona instances (Chris, AIC, Aria, Sora)
  - `PersonaType`, `PersonaCapability`, `PersonaStrategy`
  - `DaemonRuntime` - Daemon execution runtime
  - `CognitiveDaemon` (ABC) - Base daemon class
  - `EchoDaemon`, `OracleDaemon`, `CriticDaemon` - Specific daemons
  - `TheoreticalReasoningFramework` - TRF implementation
  - `ProjectIntelligence` - Per-project intelligence
  - Connects to: Domain Layer, Driver Layer

- **Daemon System**: `assistant_core/daemon/cognitive_daemon.py`
  - `CognitiveDaemon` - Active daemon orchestrator
  - `DocumentMonitor`, `TaskMonitor`, `IntegrationMonitor`, etc.
  - `AutoDraftService`, `AutoUpdateService`, `AutoSuggestService`
  - Connects to: Domain Layer, Infrastructure Layer

### 4. Domain / Model Layer (Spec Section 3)
- **Domain Models**: `assistant_core/domain/models.py`
  - `Project`, `Task`, `User`, etc.
  - Connects to: Infrastructure Layer (Storage)

- **CIR Schema**: `assistant_core/cir/schema.py`
  - `CIRDocument`, `DocumentMetadata`, `Section`, etc.
  - Connects to: Storage Layer, Presentation Layer

### 5. Infrastructure Layer (Spec Section 6)
- **Storage**: SQLite via `assistant_hub_gui/assistant_hub/db.py`
  - `init_db()`, `load_state()`, `save_state()`
  - Connects to: All layers

- **Versioning**: `assistant_hub_gui/assistant_hub/versioning/git_manager.py`
  - `GitManager` - Git operations
  - Connects to: Domain Layer, Storage Layer

### 6. Driver Architecture (Spec Section 5)
- **Driver System**: `assistant_core/driver_architecture.py`
  - `DriverRegistry` - Driver management
  - `DriverScheduler` - Execution scheduling
  - `BaseDriver` (ABC) - Base driver class
  - `FilesystemDriver`, `ProcessDriver`, `PipDriver`, `GitDriver`
  - Connects to: Cognitive Layer, Infrastructure Layer

## Planes Architecture (Spec Section 2)

### Data Plane
- **Storage**: SQLite database
- **CIR Store**: Document representation
- **Indices**: Search, vector indices (future)

### Control Plane
- **Orchestrator**: `AutomationOrchestrator`
- **Daemons**: `DaemonRuntime` + individual daemons
- **Workflows**: `WorkflowEngine` in `assistant_core/daemon/workflow_orchestration.py`

### Governance Plane
- **Policy Engine**: `assistant_core/security/governance_engine.py`
- **Compliance**: `ComplianceFramework` enum
- **Auth**: `assistant_core/security/auth_manager.py`

## Component Relationships

### Cognitive Framework → GUI
```
CognitiveFrameworkManager
  ├── Personas (Chris, AIC, Aria, Sora)
  ├── DaemonRuntime
  │   ├── EchoDaemon
  │   ├── OracleDaemon
  │   └── CriticDaemon
  ├── TheoreticalReasoningFramework
  └── ProjectIntelligence (per project)
      └── CognitivePersona instances
```

### GUI → Cognitive Framework
```
AssistantGUI
  ├── cognitive_manager: CognitiveFrameworkManager
  ├── cognitive_status: Dict (personas, daemons, reasoning)
  ├── cognitive_reasoning_history: List[Dict]
  └── Methods:
      ├── _initialize_cognitive_framework()
      ├── _refresh_cognitive_status()
      ├── _run_cognitive_reasoning()
      └── _render_ai_os_daemon_view()
```

### Driver System → Cognitive Framework
```
DriverRegistry
  └── Drivers (Filesystem, Process, Pip, Git)
      └── Used by:
          ├── Daemons (for system operations)
          ├── Workflows (for automation)
          └── Personas (for task execution)
```

### Daemon System → Domain Layer
```
CognitiveDaemon (daemon/cognitive_daemon.py)
  ├── Monitors:
  │   ├── DocumentMonitor → db.documents
  │   ├── TaskMonitor → db.tasks
  │   └── IntegrationMonitor → db.integrations
  └── Automators:
      ├── AutoDraftService → CIR documents
      └── AutoUpdateService → Domain models
```

## Missing Connections (Gaps Identified)

1. **GUI ↔ Cognitive Framework**: Connection removed, needs restoration
2. **Driver System ↔ Cognitive Framework**: Not fully integrated
3. **Planes Architecture**: Data/Control/Governance planes not explicitly separated
4. **Project Intelligence**: Not connected to GUI project views
5. **Reasoning Framework**: GUI removed reasoning UI, needs restoration
6. **Daemon Runtime**: GUI daemon view simplified, missing full integration

## Data Flow Examples

### User Chat Message Flow
```
GUI.on_send_chat_message()
  → ConversationManager.process_message()
    → CognitiveFrameworkManager.reason_about() [if enabled]
      → TheoreticalReasoningFramework.reason()
        → ReasoningTrace with steps
    → AI Service (OpenAI/ChatGPT)
      → Response
    → GUI.display_response()
```

### Daemon Execution Flow
```
DaemonRuntime._run_loop()
  → CognitiveDaemon.execute()
    → DriverRegistry.execute_capability() [if needed]
      → DriverScheduler.submit_request()
        → BaseDriver.execute()
    → Domain Layer updates (db, CIR, etc.)
    → DaemonExecution result
```

### Project Intelligence Flow
```
ProjectIntelligence.analyze_project()
  → CognitivePersona instances
  → TheoreticalReasoningFramework.reason()
  → Insights → Domain Layer
  → GUI project views
```

