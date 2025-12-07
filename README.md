# OS Dashboard AI Assistant

A comprehensive AI-powered operating system dashboard that integrates with external services to provide intelligent task management, document processing, and workflow automation.

## Project Structure

```
├── assistant_core/           # Primary application logic (The "Brain")
│   ├── ai_manager.py         # AI interaction handling
│   ├── data_aggregator.py    # Data processing and normalization
│   ├── dashboard_engine.py   # Dashboard state management
│   ├── ai/                   # AI agents and workflows
│   ├── core/                 # Core application components
│   └── daemon/               # Background processes
├── api_connectors/           # Modular wrappers for external services
│   ├── git_client.py         # Git repository operations
│   ├── google_client.py      # Google APIs (Gmail, Calendar)
│   ├── ms_graph_client.py    # Microsoft Graph APIs
│   └── integrations/         # All service integrations
├── ui/                       # UI components (deprecated web UI removed)
│   └── terminal/             # CLI interface components
├── tests/                    # Unit and integration tests
├── config/                   # Configuration and secrets management
│   ├── config.yaml           # Application configuration
│   └── credentials/          # OAuth tokens and API keys
├── utils/                    # Helper functions
│   ├── auth_helpers.py       # Token management
│   └── file_parsers.py       # File processing utilities
├── marketplace/              # Plugin marketplace (created on first run)
│   ├── plugins/             # Available plugin packages
│   └── installed/           # Installed plugin instances
├── main.py                   # Application entry point
├── plugin_manager.py         # Plugin management CLI
├── security_monitor.py       # Security monitoring and compliance CLI
├── settings.py               # Global application settings
└── requirements.txt          # Python dependencies
```

## Install

```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
# Start the main application
python main.py

# Start the web dashboard
python ui/main.py
```

### Configuration

1. Copy configuration files and set up credentials:
   ```bash
   # Create config directory structure
   mkdir -p config/credentials

   # Copy and edit configuration
   cp config/config.yaml config/config.local.yaml
   # Edit config.local.yaml with your settings
   ```

2. Set up API credentials:
   - Google APIs: Place `client_secret.json` in `config/credentials/`
   - Microsoft Graph: Configure client ID, tenant ID, and secret in config
   - OpenAI: Set API key in environment or config

## Key Components

### Assistant Core
- **AI Manager**: Handles all interactions with LLM services (OpenAI, Anthropic)
- **Data Aggregator**: Normalizes data from various sources into common formats
- **Dashboard Engine**: Manages application state and prepares display data

### API Connectors
- **Google Client**: Gmail and Google Calendar integration
- **MS Graph Client**: Word, Excel, OneNote, and OneDrive integration
- **Git Client**: Local repository operations and management

### UI Components
- **Terminal Interface**: Command-line tools and utilities

### Security Framework
- **Enterprise Security**: Comprehensive security controls and threat detection
- **Compliance Monitoring**: GDPR, HIPAA, SOX, PCI-DSS, ISO27001, SOC2, CCPA, NIST frameworks
- **Audit Logging**: Complete audit trails for all system activities
- **Data Protection**: Automatic data classification and encryption
- **Access Control**: Role-based access control with policy enforcement
- **Threat Detection**: Real-time threat analysis and incident response

### Plugin System
- **Plugin Marketplace**: Secure third-party plugin distribution
- **Plugin Types**: Integration, Widget, Automation, Analytics, Notification, Security, Utility
- **Security Scanning**: Automatic security analysis of plugin code
- **Plugin Management**: Install, enable, disable, and uninstall plugins
- **Review System**: Community ratings and reviews for plugins

## Development

### Running Tests

```bash
pytest tests/
```

### Plugin Management

The system includes a comprehensive plugin marketplace for extending functionality:

```bash
# List available plugins
python plugin_manager.py list

# Search plugins by type or keyword
python plugin_manager.py list --query "weather" --type integration

# Show detailed plugin information
python plugin_manager.py show weather-integration

# Install a plugin
python plugin_manager.py install weather-integration

# Install specific version
python plugin_manager.py install weather-integration --version 1.0.0

# Uninstall a plugin
python plugin_manager.py uninstall weather-integration

# View marketplace statistics
python plugin_manager.py stats
```

### Security Monitoring

The system includes enterprise-grade security and compliance monitoring:

```bash
# View security dashboard
python security_monitor.py dashboard

# Run compliance assessment
python security_monitor.py compliance gdpr

# Check security incidents
python security_monitor.py incidents

# View audit logs
python security_monitor.py audit --user "username" --days 7

# Analyze threats from log data
python security_monitor.py analyze-threats access.log
```

### Adding New Integrations

1. Create a new client in `api_connectors/`
2. Implement the required interface methods
3. Add configuration in `config/config.yaml`
4. Update the data aggregator to handle the new data source

### Extending the Application

The web UI has been removed. For extending the application:

1. Modify the GUI in `assistant_hub_gui/assistant_hub/gui.py`
2. Extend `assistant_core/dashboard_engine.py` for new data processing
3. Update integrations in `api_connectors/` for new API endpoints

### Developing Plugins

Create custom plugins to extend the OS Dashboard:

1. **Choose Plugin Type**:
   - `IntegrationPlugin`: External service integrations
   - `WidgetPlugin`: Dashboard widgets
   - `AutomationPlugin`: Workflow automation
   - `AnalyticsPlugin`: Data analysis tools

2. **Plugin Structure**:
   ```
   my-plugin/
   ├── manifest.yaml    # Plugin metadata and configuration
   └── main.py         # Plugin implementation
   ```

3. **Example Manifest**:
   ```yaml
   id: "my-plugin"
   name: "My Custom Plugin"
   version: "1.0.0"
   type: "integration"
   entry_point: "main.py"
   config_schema:
     api_key:
       type: "string"
       required: true
   ```

4. **Plugin Security**:
   - Plugins are automatically scanned for security issues
   - High-risk plugins require manual approval
   - Plugins run in isolated environments

## Template-driven deliverables

The template catalog enforces that every AI edit is tracked, every change is diffed, every document has version history, every operation is timestamped, every action is reversible, and every output is accountable. It aligns the stack so OneNote serves as structured memory, Word is the formatted deliverable engine, Excel is the analytical substrate, Git preserves lineage, ChatGPT is the reasoning center, daemons form the active cortex, and AIC/Sora/Aria guide knowledge formation. Daemons can notice missing documents, draft proposals, update reports, summarize notebooks, analyze spreadsheets, reorganize folders, update tasks, alert when content is outdated, track version history, suggest improvements, predict next steps, and execute workflows.

## Vision

Read the high-level vision for how the OS Dashboard AI Assistant grows into a governed, end-to-end cognitive operating system in [VISION.md](VISION.md). For a deeper dive into the structural, societal, economic, and cognitive impacts of the platform, see the accompanying [GLOBAL_IMPACT_WHITE_PAPER.md](GLOBAL_IMPACT_WHITE_PAPER.md).
