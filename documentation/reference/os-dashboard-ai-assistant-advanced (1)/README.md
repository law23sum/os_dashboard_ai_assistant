# OS Dashboard AI Assistant Software

A comprehensive Python-based AI assistant that integrates with multiple productivity applications and services including Git, ChatGPT, Microsoft Office (Word, PowerPoint, Excel, OneNote), Apple Calendar, Gmail, and Adobe services.

## Features

### 🤖 AI Integration
- **OpenAI/ChatGPT**: Chat completions, embeddings, image analysis, function calling, assistants
- **Conversation Management**: System prompts, conversation history, temperature control

### 📊 Microsoft Office Integration
- **Word**: Create, read, and manage documents
- **PowerPoint**: Create presentations with slides
- **Excel**: Create workbooks, update worksheets, manage data
- **OneNote**: Create pages, manage notebooks
- **OneDrive**: File upload, download, and management

### 📧 Communication
- **Gmail**: Send emails, read messages, manage attachments
- **Google Calendar**: Create events, manage calendars, get upcoming events

### 📅 Calendar Management
- **Google Calendar**: Full calendar management
- **Apple Calendar**: CalDAV integration for Apple ecosystem

### 🔧 Development Tools
- **GitHub**: Repository management, issues, pull requests, file operations
- **Local Git**: Clone, commit, push, pull, status checking

### 📄 Document Processing
- **Adobe PDF Services**: Extract text, create PDFs, combine/split documents
- **Creative Cloud**: Asset management (placeholder for future implementation)

## Installation

1. **Clone the repository**:
```bash
git clone <your-repo-url>
cd os-dashboard-ai-assistant
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up configuration**:
```bash
cp .env.template .env
# Edit .env with your API credentials
```

## Configuration

### Required API Credentials

#### OpenAI
- Get API key from [OpenAI Platform](https://platform.openai.com/)
- Set `OPENAI_API_KEY` in `.env`

#### Microsoft Graph API
1. Register app in [Azure Portal](https://portal.azure.com/)
2. Get Client ID, Client Secret, and Tenant ID
3. Set permissions for Microsoft Graph API
4. Configure redirect URI

#### Google APIs
1. Create project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail and Calendar APIs
3. Create OAuth 2.0 credentials
4. Download `credentials.json`

#### GitHub
1. Generate Personal Access Token in GitHub Settings
2. Set `GITHUB_TOKEN` in `.env`

#### Adobe PDF Services
1. Create account at [Adobe Developer Console](https://developer.adobe.com/)
2. Create PDF Services credentials
3. Download private key file

#### Apple Calendar (CalDAV)
1. Enable two-factor authentication for Apple ID
2. Generate app-specific password
3. Use iCloud CalDAV URL: `https://caldav.icloud.com/`

## Usage

### Basic Usage

```python
import asyncio
from api_manager import get_api_manager

async def main():
    # Initialize API manager
    api_manager = await get_api_manager()
    await api_manager.initialize()
    
    # Chat with AI
    response = await api_manager.chat_completion("Hello, how can you help me?")
    print(response)
    
    # Send email
    await api_manager.send_email(
        to="recipient@example.com",
        subject="Test Email",
        body="This is a test email from the AI assistant."
    )
    
    # Create calendar event
    from datetime import datetime, timedelta
    tomorrow = datetime.now() + timedelta(days=1)
    await api_manager.create_calendar_event(
        title="Meeting",
        start_time=tomorrow,
        end_time=tomorrow + timedelta(hours=1),
        description="Important meeting"
    )
    
    # Create Word document
    await api_manager.create_document(
        title="Project Report",
        content="This is the project report content.",
        doc_type="word"
    )
    
    # Cleanup
    await api_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

### Interactive Mode

```bash
python main.py interactive
```

Available commands:
- `chat <message>` - Chat with AI
- `email <to> <subject> <body>` - Send email
- `calendar <title> <description>` - Create calendar event
- `status` - Check API status
- `quit` - Exit

### Individual API Usage

#### OpenAI Client
```python
from apis.openai_client import OpenAIClient

client = OpenAIClient()
await client.initialize()

# Chat completion
response = await client.chat_completion("Explain quantum computing")

# Generate embeddings
embeddings = await client.generate_embeddings(["text1", "text2"])

# Image analysis
analysis = await client.analyze_image("https://example.com/image.jpg")
```

#### Microsoft Client
```python
from apis.microsoft_client import MicrosoftClient

client = MicrosoftClient()
await client.initialize()

# Create Word document
doc = await client.create_word_document("Title", "Content")

# Create Excel workbook
workbook = await client.create_excel_workbook("Budget", [{"name": "Sheet1", "data": "..."}])

# List OneDrive files
files = await client.list_files()
```

#### Google Client
```python
from apis.google_client import GoogleClient

client = GoogleClient()
await client.initialize()

# Send email
await client.send_email("to@example.com", "Subject", "Body")

# Get emails
emails = await client.get_emails("is:unread", max_results=10)

# Create calendar event
event = await client.create_calendar_event("Meeting", start_time, end_time)
```

#### Git Client
```python
from apis.git_client import GitClient

client = GitClient()
await client.initialize()

# Get repositories
repos = await client.get_repositories()

# Create repository
repo = await client.create_repository("new-repo", "Description")

# Clone repository
await client.clone_repository("https://github.com/user/repo.git", "./local-repo")
```

## API Reference

### APIManager

Main class that coordinates all API integrations.

#### Methods

- `initialize()` - Initialize all API clients
- `get_status()` - Get status of all API connections
- `chat_completion(message, **kwargs)` - Send message to ChatGPT
- `create_document(title, content, doc_type)` - Create Office document
- `send_email(to, subject, body, attachments)` - Send email via Gmail
- `create_calendar_event(title, start_time, end_time, description, service)` - Create calendar event
- `git_operations(operation, **kwargs)` - Perform Git operations
- `process_pdf(file_path, operation)` - Process PDF with Adobe services
- `shutdown()` - Gracefully shutdown all clients

### Configuration

All configuration is managed through environment variables and the `config.py` module.

#### Key Settings

- `OPENAI_API_KEY` - OpenAI API key
- `MICROSOFT_CLIENT_ID` - Microsoft Graph client ID
- `GOOGLE_CREDENTIALS_FILE` - Google OAuth credentials file
- `GITHUB_TOKEN` - GitHub personal access token
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

## Error Handling

The system includes comprehensive error handling:

- **Connection Errors**: Automatic retry with exponential backoff
- **Authentication Errors**: Clear error messages with setup instructions
- **Rate Limiting**: Automatic throttling and queue management
- **Validation**: Input validation for all API calls

## Logging

Structured logging with color-coded output:

```python
from logger import setup_logger

logger = setup_logger("MyComponent")
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
```

## Security

- **Credential Management**: Environment variables and secure storage
- **Token Refresh**: Automatic OAuth token refresh
- **Encryption**: Secure credential storage using keyring
- **Validation**: Input sanitization and validation

## Development

### Adding New APIs

1. Create new client in `apis/` directory
2. Implement required methods: `initialize()`, `health_check()`, `shutdown()`
3. Add client to `APIManager` in `api_manager.py`
4. Update configuration in `config.py`
5. Add examples in `main.py`

### Testing

```bash
# Run basic functionality test
python main.py

# Run interactive mode
python main.py interactive

# Test specific API
python -c "
import asyncio
from apis.openai_client import OpenAIClient

async def test():
    client = OpenAIClient()
    await client.initialize()
    response = await client.chat_completion('Hello!')
    print(response)

asyncio.run(test())
"
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify API credentials in `.env`
   - Check token expiration
   - Ensure proper permissions

2. **Import Errors**
   - Install missing dependencies: `pip install -r requirements.txt`
   - Check Python version compatibility

3. **Connection Issues**
   - Verify internet connectivity
   - Check firewall settings
   - Validate API endpoints

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python main.py
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## Support

For issues and questions:
- Create GitHub issue
- Check documentation
- Review error logs with DEBUG level