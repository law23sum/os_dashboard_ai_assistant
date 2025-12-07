# OneDrive Integration - OS Dashboard AI Assistant

## Overview

A complete OneDrive integration has been added to the OS Dashboard AI Assistant, allowing users to access, sync, upload, and manage files stored in Microsoft OneDrive through the Microsoft Graph API.

## Features

### Core Capabilities

1. **File Listing**: List files and folders in OneDrive
2. **File Download**: Download files from OneDrive to local storage
3. **File Upload**: Upload local files to OneDrive (supports large files with chunked upload)
4. **Folder Management**: Create folders, navigate directory structure
5. **File Search**: Search for files by name
6. **File Sync**: Sync OneDrive folders to local disk
7. **File Metadata**: Get detailed information about files (size, dates, etc.)
8. **File Deletion**: Delete files from OneDrive

### Integration Features

- **BaseIntegration Compatible**: Follows the standard integration pattern
- **GUI Integration**: Automatically appears in the Integrations tab
- **Status Tracking**: Shows connection status and sync information
- **Database Recording**: Records OneDrive items in the external_items table
- **Error Handling**: Graceful error handling with informative messages

## Architecture

### Components

1. **OneDriveClient** (`onedrive/client.py`)
   - Low-level Microsoft Graph API client
   - Handles all API calls to OneDrive
   - Supports authentication via GraphClient

2. **OneDriveService** (`onedrive/service.py`)
   - High-level service operations
   - Provides convenient methods for common operations
   - Handles local sync directory management

3. **OneDriveIntegration** (`onedrive_integration.py`)
   - GUI integration wrapper
   - Extends BaseIntegration
   - Provides sync and status functionality

## Usage

### Basic Usage

```python
from assistant_hub.integrations.msgraph import GraphClient
from assistant_hub.integrations.onedrive import OneDriveClient, OneDriveService

# Create client
graph_client = GraphClient()
onedrive_client = OneDriveClient(graph_client)

# List files in a folder
files = onedrive_client.list_drive_items("/Documents")

# Download a file
file_content = onedrive_client.download_file("item_id_here")
with open("local_file.txt", "wb") as f:
    f.write(file_content)

# Upload a file
result = onedrive_client.upload_file("local_file.txt", "/Documents/remote_file.txt")
```

### Service Usage

```python
from assistant_hub.integrations.onedrive.service import OneDriveService
from assistant_hub.integrations.msgraph import GraphClient
from assistant_hub.integrations.onedrive import OneDriveClient

# Create service
graph_client = GraphClient()
client = OneDriveClient(graph_client)
service = OneDriveService(local_sync_root="~/onedrive_sync", client=client)

# Sync a folder to local
synced_files = service.sync_folder_to_local("/Documents", "/local/docs")

# Search for files
results = service.search_files("project", file_extensions=[".docx", ".pdf"])

# List files with filter
docx_files = service.list_files("/Documents", file_extensions=[".docx"])
```

### Integration Usage (GUI)

The OneDrive integration automatically appears in the Integrations tab:

1. **Authentication**: Uses existing Microsoft Graph credentials
2. **Sync**: Click "Sync" to sync OneDrive files to the database
3. **Status**: Shows connection status and item count
4. **Error Messages**: Displays authentication or sync errors

## API Methods

### OneDriveClient

- `list_drive_items(folder_path, drive="me")` - List items in a folder
- `get_item(item_id, drive="me")` - Get item details
- `download_file(item_id, drive="me")` - Download file content
- `upload_file(local_path, remote_path, drive="me", overwrite=False)` - Upload file
- `create_folder(folder_path, drive="me")` - Create folder
- `delete_item(item_id, drive="me")` - Delete item
- `search_items(query, drive="me")` - Search for items
- `get_drive_info(drive="me")` - Get drive information

### OneDriveService

- `sync_folder_to_local(remote_folder, local_folder, drive="me")` - Sync folder
- `upload_local_file(local_path, remote_path, drive="me", overwrite=False)` - Upload file
- `list_files(folder_path, file_extensions, drive="me")` - List files
- `search_files(query, file_extensions, drive="me")` - Search files
- `get_file_info(item_id, drive="me")` - Get file info
- `create_folder(folder_path, drive="me")` - Create folder
- `delete_file(item_id, drive="me")` - Delete file

### OneDriveIntegration

- `authenticate()` - Authenticate with Microsoft Graph
- `sync()` - Sync OneDrive files to database
- `get_status()` - Get integration status
- `download_file(item_id, local_path)` - Download file
- `upload_file(local_path, remote_path, overwrite=False)` - Upload file

## Authentication

OneDrive integration uses Microsoft Graph API authentication:

1. **Credentials**: Uses existing Microsoft Graph credentials (same as OneNote, Excel, Word)
2. **Permissions Required**:
   - `Files.Read` - Read files
   - `Files.ReadWrite` - Read and write files
   - `Files.ReadWrite.All` - Full access (if needed)
3. **Token Management**: Handled automatically by GraphClient

## File Path Handling

OneDrive uses a path-based system:
- Root: `/` or empty string
- Folders: `/Documents`, `/Desktop`, etc.
- Files: `/Documents/file.txt`
- Paths are normalized automatically

## Large File Support

Files larger than 4MB are automatically uploaded using chunked upload sessions:
- Automatic chunk size: 320KB
- Progress tracking available
- Resume support for failed uploads

## Error Handling

The integration handles common errors:
- **401 Unauthorized**: Authentication required
- **404 Not Found**: File/folder doesn't exist
- **409 Conflict**: File already exists (when overwrite=False)
- **Network Errors**: Timeout and retry handling

## Database Integration

OneDrive items are recorded in the `external_items` table with:
- `source_name`: "OneDrive"
- `source_kind`: "onedrive"
- `item_kind`: "file" or "folder"
- `data`: JSON with file metadata (size, dates, URLs, etc.)

## Sync Behavior

When syncing, the integration:
1. Lists items in common folders (`/Documents`, `/Desktop`, `/Pictures`)
2. Records each item in the database
3. Includes metadata (size, dates, web URL)
4. Limits root items to first 50 to avoid overwhelming the database

## Local Sync Directory

By default, synced files are stored in:
- `~/.assistant_hub/onedrive_sync/`

This can be customized when creating the service.

## Integration with Existing Features

OneDrive integration works seamlessly with:
- **Cognitive Daemon**: Can monitor OneDrive for changes
- **File Task Extraction**: Can extract tasks from OneDrive documents
- **Document Templates**: Can save templates to OneDrive
- **Analytics**: OneDrive file counts included in analytics

## Future Enhancements

Potential future improvements:
- Real-time sync notifications
- Selective folder sync
- File versioning support
- Conflict resolution UI
- Batch operations
- Share link generation
- Permission management

## Files Created

1. `assistant_hub/integrations/onedrive/__init__.py` - Package initialization
2. `assistant_hub/integrations/onedrive/client.py` - Graph API client (400+ lines)
3. `assistant_hub/integrations/onedrive/service.py` - High-level service (200+ lines)
4. `assistant_hub/integrations/onedrive_integration.py` - GUI integration wrapper (150+ lines)

## Dependencies

- `requests` - For HTTP requests
- Microsoft Graph API credentials (same as OneNote/Excel/Word)
- Existing `GraphClient` and `GraphAuth` infrastructure

## Testing

To test the integration:

1. Ensure Microsoft Graph credentials are configured
2. Go to Integrations tab in GUI
3. Find "OneDrive" in the list
4. Click "Sync" to test authentication and sync
5. Check status shows connected and item count

## Notes

- OneDrive integration uses the same authentication as other Microsoft 365 integrations
- Files are synced to database, not automatically downloaded (use download_file for that)
- Large file uploads use chunked upload automatically
- Path-based access is more reliable than ID-based for user-facing operations

