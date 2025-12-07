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
├── ui/                       # Frontend/Dashboard files
│   ├── index.html            # Main dashboard view
│   ├── dashboard_app.py      # Flask web application
│   ├── assets/               # CSS, JS, images
│   └── terminal/             # CLI interface components
├── tests/                    # Unit and integration tests
├── config/                   # Configuration and secrets management
│   ├── config.yaml           # Application configuration
│   └── credentials/          # OAuth tokens and API keys
├── utils/                    # Helper functions
│   ├── auth_helpers.py       # Token management
│   └── file_parsers.py       # File processing utilities
├── main.py                   # Application entry point
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
- **Web Dashboard**: Flask-based responsive web interface
- **Terminal Interface**: Command-line tools and utilities

## Development

### Running Tests

```bash
pytest tests/
```

### Adding New Integrations

1. Create a new client in `api_connectors/`
2. Implement the required interface methods
3. Add configuration in `config/config.yaml`
4. Update the data aggregator to handle the new data source

### Extending the Dashboard

1. Modify `ui/index.html` for new UI components
2. Update `ui/dashboard_app.py` for new API endpoints
3. Extend `assistant_core/dashboard_engine.py` for new data processing

## Template-driven deliverables

The template catalog enforces that every AI edit is tracked, every change is diffed, every document has version history, every operation is timestamped, every action is reversible, and every output is accountable. It aligns the stack so OneNote serves as structured memory, Word is the formatted deliverable engine, Excel is the analytical substrate, Git preserves lineage, ChatGPT is the reasoning center, daemons form the active cortex, and AIC/Sora/Aria guide knowledge formation. Daemons can notice missing documents, draft proposals, update reports, summarize notebooks, analyze spreadsheets, reorganize folders, update tasks, alert when content is outdated, track version history, suggest improvements, predict next steps, and execute workflows.

## Vision

Read the high-level vision for how the OS Dashboard AI Assistant grows into a governed, end-to-end cognitive operating system in [VISION.md](VISION.md). For a deeper dive into the structural, societal, economic, and cognitive impacts of the platform, see the accompanying [GLOBAL_IMPACT_WHITE_PAPER.md](GLOBAL_IMPACT_WHITE_PAPER.md).
