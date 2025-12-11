# Installation Guide - OS Dashboard AI Assistant Platform

## Quick Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (optional, for development)

### 1. Extract and Setup
```bash
# Extract the zip file
unzip os-dashboard-ai-assistant-platform.zip
cd os-dashboard-ai-assistant-platform

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Install the platform package
pip install -e .
```

### 3. Launch the Platform
```bash
# Start the GUI Dashboard
python main.py --mode dashboard

# Or run the demo
python examples/demo_usage.py

# Or use command line interface
python main.py --mode cli
```

## Detailed Installation Options

### Development Installation
```bash
# Install with development dependencies
pip install -e ".[dev,ml,cloud,monitoring]"

# Run tests
pytest tests/

# Format code
black src/
flake8 src/
```

### Docker Installation
```bash
# Build Docker image
docker build -t os-dashboard-ai .

# Run container
docker run -p 8000:8000 os-dashboard-ai
```

### Cloud Deployment
```bash
# AWS deployment
aws configure
python deploy/aws_deploy.py

# Google Cloud deployment
gcloud auth login
python deploy/gcp_deploy.py
```

## Configuration

### Environment Variables
```bash
export DATA_COLLECTOR_MAX_WORKERS=10
export CONTENT_OUTPUT_DIR="./output"
export SYSTEM_WORKSPACE_DIR="./workspace"
```

### Configuration File
Edit `config/default_config.yaml` to customize settings.

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed
2. **Permission Errors**: Run with appropriate permissions
3. **Port Conflicts**: Change default ports in configuration

### Support
- GitHub Issues: Report bugs and request features
- Documentation: Read the full documentation
- Email: team@ai-assistant-platform.com

## Next Steps
1. Read the README.md for detailed usage instructions
2. Run the demo to see all features in action
3. Explore the examples/ directory for code samples
4. Check the documentation for advanced configuration