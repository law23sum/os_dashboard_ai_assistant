# OS Dashboard AI Assistant Platform

Enterprise-grade autonomous workflows, professional content generation, and advanced system operations for multi-source data intelligence.

---

## Key Features

### Advanced Autonomous Workflows
- Multi-source intelligence with real-time web scraping and content extraction.
- Batch data processing across multiple APIs with cross-reference verification.
- Automated pipelines that clean, transform, and validate diverse datasets.
- Intelligent task management with dependency awareness and retry logic.

### Professional-Grade Content Generation
- Interactive HTML presentations with responsive layouts, charts, and animations.
- Excel dashboards featuring live data connections, conditional formatting, and native charts.
- Word documents with complex layouts, tables, and professional formatting.
- End-to-end web application deployment with custom domains.

### System-Level Operations
- Full Linux environment control, including package installation and environment setup.
- Process management with monitoring, logging, and background task control.
- Network services with public port exposure and managed services.
- Advanced file processing spanning PDF extraction, conversions, and archive handling.
- Real-time Office collaboration router bridging Office add-ins and AI feedback loops with resilient fallbacks (`assistant_core/integrations/office_realtime.py`).

### Specialized Intelligence
- Automated content validation and overflow detection.
- Accessibility compliance checks and reporting.
- Formatting validation with consistency enforcement and professional standards.
- Batch verification with cross-file error reporting.

### Concurrent Operations
- Parallel processing with intelligent batching across three to five simultaneous searches.
- Managed background tasks with progress monitoring.
- Dynamic worker pools for resource optimization and performance tuning.
- Fault-tolerant execution with automatic retries and graceful degradation.

### Advanced Integration
- Office add-in embedding for Excel dashboards with task pane support.
- Static site deployment to Vercel, Netlify, AWS, and GitHub Pages.
- API integrations with live data feeds and webhook support.
- Cross-platform compatibility spanning Windows, macOS, Linux, and mobile.

### Enterprise Security & Governance
- Policy/governance engine with compliance frameworks, audit trails, and data classification.
- Encryption service with key management, RSA/AES primitives, and usage logging.
- Authentication & RBAC manager supporting multiple auth providers and session controls.
- Security monitor with threat detection, anomaly analysis, and incident workflows.
- Billing and usage fabric for plan management, metering, and invoicing.

---

## Installation

### Prerequisites
- Python 3.8+
- `pip`
- Git (development workflow)

### Quick Install
```bash
# Clone the repository
git clone https://github.com/ai-assistant/os-dashboard-platform.git
cd os-dashboard-platform

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Development Install
```bash
pip install -e ".[dev,ml,cloud,monitoring]"
pytest tests/
black src/
flake8 src/
```

---

## Quick Start

### Launch the Dashboard
```bash
os-dashboard
# or
python -m src.dashboard.main_interface
```

### Run the Demo Suite
```bash
python examples/demo_usage.py
# Generates presentations, Excel dashboards, Word reports, and deployment artifacts
```

### Data Collection Example
```python
from src.intelligence.data_collector import SyncDataCollector, DataSource

collector = SyncDataCollector()
sources = [
    DataSource(
        name="news_api",
        url="https://api.example.com/news",
        source_type="api",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
    ),
    DataSource(
        name="company_website",
        url="https://company.com/data",
        source_type="web",
    ),
]

results = collector.collect_data(sources)
print(f"Collected {len(results)} datasets")
```

### Content Generation Example
```python
from src.content.generators import PresentationGenerator, ContentConfig

config = ContentConfig(
    title="Business Intelligence Report",
    author="AI Assistant",
    theme="professional",
)

generator = PresentationGenerator(config)
generator.add_title_slide("Q4 Results", "Performance Analysis")
generator.add_content_slide(
    "Key Metrics",
    [
        "Revenue increased 25%",
        "Customer satisfaction: 94%",
        "Market share expanded to 15%",
    ],
)

html_output = generator.generate_html("presentation.html")
```

### System Operations Example
```python
from src.system.operations import SystemOperationsController

controller = SystemOperationsController()
result = controller.execute_command("ls -la /workspace")
print(f"Command output: {result['stdout']}")

install_result = controller.install_package("nodejs", "apt")
print(f"Installation: {'Success' if install_result['success'] else 'Failed'}")

port_result = controller.expose_port(8000, "dashboard_service")
print(f"Service available at: {port_result['public_url']}")
```

### Concurrent Processing Example
```python
from src.operations.concurrent_manager import ConcurrentOperationsManager, ConcurrentTask

manager = ConcurrentOperationsManager(max_workers=10)
tasks = [
    ConcurrentTask(
        name=f"process_data_{i}",
        function=process_data_function,
        args=(data_batch,),
        priority=2,
    )
    for i, data_batch in enumerate(data_batches)
]

batch_id = manager.create_batch_operation("data_processing", tasks)
results = manager.execute_batch_sync(batch_id)
print(f"Processed {results['successful_tasks']} tasks successfully")
```

### Monitor Real-Time Sessions
1. Launch the dashboard via `os-dashboard` or `python -m src.dashboard.main_interface`.
2. Navigate to **Tools → Real-Time Sessions** to inspect connected Office add-ins, their active documents, and the router's AI event log.
3. Set `AI_SERVICE_URL` to your processing endpoint or rely on the built-in simulator exposed by `assistant_core/integrations/office_realtime.py` for local testing.

---

## Architecture

```
src/
├── core/                     # Base agent and workflow management
│   └── base_agent.py         # Task execution and dependency management
├── intelligence/
│   ├── data_collector.py     # Multi-source data intelligence
│   └── quality_assurance.py  # Content validation and accessibility
├── content/
│   └── generators.py         # HTML, Excel, Word document creation
├── system/
│   └── operations.py         # Process management and network services
├── operations/
│   └── concurrent_manager.py # Parallel execution and batch operations
├── integrations/
│   ├── advanced_systems.py   # Deployment and Office integration
│   └── office_realtime.py    # WebSocket router for Office add-ins
├── security/
│   ├── encryption_service.py # Key management and cryptography
│   ├── governance_engine.py  # Policy and compliance management
│   ├── billing_system.py     # Usage metering and invoicing
│   ├── auth_manager.py       # Authentication and RBAC
│   └── security_monitor.py   # Threat detection and incident response
└── dashboard/
    └── main_interface.py     # GUI dashboard application
```

### Data Flow
- Input sources → Data collector → Intelligent extraction.
- Raw data → Quality assurance → Validated content.
- Content requirements → Generators → Professional outputs.
- System commands → Operations controller → Executed tasks.
- Batch operations → Concurrent manager → Parallel results.
- Generated content → Integration systems → Deployed applications.

---

## Configuration

The full platform template lives in `config/default_config.yaml`. Copy or trim this into
`config/config.yaml` (or point `--config` to another path) to override defaults without
editing the primary file.

### Environment Variables
```bash
export DATA_COLLECTOR_MAX_WORKERS=10
export DATA_COLLECTOR_TIMEOUT=30
export DATA_COLLECTOR_RATE_LIMIT=1.0
export CONTENT_OUTPUT_DIR="./output"
export CONTENT_DEFAULT_THEME="professional"
export CONTENT_AUTO_OPTIMIZE=true
export SYSTEM_MAX_PROCESSES=8
export SYSTEM_WORKSPACE_DIR="./workspace"
export SYSTEM_LOG_LEVEL="INFO"
export DEPLOYMENT_PLATFORM="vercel"
export DEPLOYMENT_AUTO_DEPLOY=false
export DEPLOYMENT_CUSTOM_DOMAIN=""
export AI_SERVICE_URL="http://localhost:8000"
```

### Configuration File (`config.yaml`)
```yaml
dashboard:
  title: "OS Dashboard AI Assistant Platform"
  theme: "professional"
  auto_save: true
  max_workers: 10
  workspace_dir: "./workspace"

data_collection:
  max_concurrent: 10
  timeout: 30
  rate_limit: 1.0
  cache_enabled: true
  cache_ttl: 3600

content_generation:
  output_dir: "./output"
  default_theme: "professional"
  auto_optimize: true
  include_metadata: true

quality_assurance:
  strict_validation: true
  accessibility_level: "AA"
  performance_checks: true
  cross_browser_testing: false

deployment:
  default_platform: "vercel"
  auto_deploy: false
  custom_domains: []
  ssl_enabled: true
```

---

## Advanced Usage

### Custom Workflow Creation
```python
from src.core.base_agent import WorkflowBuilder, Priority

workflow = WorkflowBuilder()
workflow.add_task("collect_data", "Gather market data", Priority.HIGH)
workflow.add_task("analyze_data", "Process and analyze", Priority.MEDIUM, ["collect_data"])
workflow.add_task("generate_report", "Create presentation", Priority.MEDIUM, ["analyze_data"])
workflow.add_task("deploy_report", "Deploy to production", Priority.LOW, ["generate_report"])

tasks = workflow.build()
```

### Custom Content Validators
```python
from src.intelligence.quality_assurance import ContentValidator, ValidationRule

def validate_brand_compliance(content, content_type):
    brand_keywords = ["company_name", "brand_color", "logo"]
    return ValidationResult(...)

validator = ContentValidator()
validator.add_rule(
    ValidationRule(
        name="brand_compliance",
        description="Check brand compliance",
        rule_type="function",
        function=validate_brand_compliance,
    )
)
```

### Integration with External APIs
```python
from src.integrations.advanced_systems import APIIntegrationManager

api_manager = APIIntegrationManager()
connection_id = api_manager.register_api_connection(
    name="salesforce",
    base_url="https://api.salesforce.com",
    auth_config={"bearer": "your_token"},
    rate_limit=2.0,
)

feed_id = api_manager.create_live_data_feed(
    connection_id=connection_id,
    endpoint="/data/v1/accounts",
    refresh_interval=300,
)

data = api_manager.get_live_data(feed_id)
```

---

## Testing

```bash
pytest tests/
pytest --cov=src tests/
pytest tests/test_data_collection.py
pytest tests/test_content_generation.py
pytest tests/test_system_operations.py
python tests/performance/load_test.py
python -m memory_profiler tests/performance/memory_test.py
python tests/performance/concurrent_test.py
```

---

## Deployment

### Production Deployment
```bash
python setup.py sdist bdist_wheel
twine upload dist/*
docker build -t os-dashboard-ai .
docker run -p 8000:8000 os-dashboard-ai
```

### Cloud Deployment
```bash
# AWS
aws configure
python deploy/aws_deploy.py

# Google Cloud
gcloud auth login
python deploy/gcp_deploy.py

# Azure
az login
python deploy/azure_deploy.py
```

---

## Documentation
- API Reference
- User Guide
- Developer Guide
- Examples
- FAQ

---

## Contributing
1. Fork and clone the repository.
2. Create and activate a virtual environment.
3. Install development dependencies via `pip install -e ".[dev]"`.
4. Install pre-commit hooks using `pre-commit install`.
5. Run `pytest tests/` before opening a pull request.

### Code Style
- Follow PEP 8.
- Run Black for formatting.
- Add type hints and comprehensive docstrings.
- Maintain 90%+ test coverage.

---

## License
MIT License (see `LICENSE`).

---

## Acknowledgments
- Beautiful Soup for HTML parsing.
- Pandas for data manipulation.
- Jinja2 for templating.
- OpenPyXL for Excel automation.
- python-docx for Word generation.
- psutil for system monitoring.
- aiohttp for asynchronous HTTP.

---

## Support
- GitHub Issues for bugs and feature requests.
- Documentation portal for guides and references.
- Community Discord.
- Email: team@ai-assistant-platform.com

---

## Roadmap
- **Version 1.1 (Q2 2024)**: ML integration, dashboard customization, real-time collaboration, mobile companion.
- **Version 1.2 (Q3 2024)**: Voice commands, advanced AI content, enterprise SSO, expanded security.
- **Version 2.0 (Q4 2024)**: Cloud-native architecture, microservices, advanced AI workflows, enterprise marketplace.

Built with passion by the AI Assistant Platform Team.
