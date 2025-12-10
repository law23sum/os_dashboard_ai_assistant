# Document Upload Feature - Implementation Summary

## Overview

Successfully implemented file upload functionality for all document type tabs (OneNote, Excel, Word, PDF) with project-based organization and local filesystem storage.

## Architecture Decision: Hybrid Storage

**Chosen Approach:** Metadata in Database, Files in Filesystem

### Why This Approach?

1. **Scalability**: Files can be large (PDFs, Excel workbooks), storing in DB would bloat it
2. **Performance**: File system is faster for file operations
3. **Git Integration**: Git can track files in filesystem (with smart filtering)
4. **External Editing**: Users can edit files with external tools
5. **Project Organization**: Files organized by project in directory structure
6. **Existing Infrastructure**: Leverages existing `note_links` table

## File Storage Structure

```
{DATA_DIR}/documents/
├── {project_name}/
│   ├── onenote/
│   │   └── {filename}.one
│   ├── excel/
│   │   └── {filename}.xlsx
│   ├── word/
│   │   └── {filename}.docx
│   └── pdf/
│       └── {filename}.pdf
└── General/
    ├── onenote/
    ├── excel/
    ├── word/
    └── pdf/
```

## Implementation Details

### 1. Database Functions (`db.py`)

Added functions for managing note links:
- `db_create_note_link()` - Create a document link
- `db_get_note_links()` - Get links (with optional filters)
- `db_get_note_link()` - Get single link by ID
- `db_update_note_link()` - Update link metadata
- `db_delete_note_link()` - Delete a link

### 2. Document Manager Module (`document_manager.py`)

New module providing:
- `upload_document()` - Upload file and create database link
- `get_project_documents()` - Get all documents for a project/type
- `get_document_path()` - Get full file path for a link
- `delete_document()` - Delete link and optionally file
- `format_file_size()` - Human-readable file size formatting
- File validation and sanitization functions

### 3. GUI Updates (`gui.py`)

**Added Upload Buttons:**
- "📤 Upload File" button added to each document tab:
  - OneNote Notebooks
  - Excel Workbooks
  - Word Documents
  - PDF Documents

**Upload Flow:**
1. User clicks "Upload File" button
2. File picker opens (filtered by document type)
3. User selects file
4. Project selection dialog appears
5. File is copied to project directory
6. Database link is created
7. Document list refreshes

**Enhanced Refresh Functions:**
- All refresh functions now show both:
  - **Cloud documents** (from OneDrive/Microsoft Graph)
  - **Local documents** (uploaded files) - marked with 📁 icon
- Status shows count of both types

### 4. Database Schema

Uses existing `note_links` table:
```sql
CREATE TABLE note_links (
    id INTEGER PRIMARY KEY,
    project_id TEXT NOT NULL,           -- Project name
    integration_type TEXT NOT NULL,     -- "local_onenote", "local_excel", "local_word", "local_pdf"
    external_id TEXT NOT NULL,           -- Relative path: "{project}/{type}/{filename}"
    title TEXT,                          -- Display name
    description TEXT,                   -- Optional description
    created_at TEXT,
    last_synced TEXT
)
```

## Supported File Types

- **OneNote**: `.one`, `.onepkg`
- **Excel**: `.xlsx`, `.xls`, `.xlsm`, `.xlsb`
- **Word**: `.docx`, `.doc`, `.rtf`
- **PDF**: `.pdf`

## Features

### ✅ Implemented

1. **File Upload**
   - Upload files for each document type
   - Project selection during upload
   - File validation (type and extension)
   - Filename sanitization
   - Automatic project creation if needed

2. **Document Display**
   - Shows both cloud and local documents
   - Visual distinction (📁 icon for local files)
   - File size and modification date display
   - Status messages with counts

3. **Project Organization**
   - Files organized by project in filesystem
   - Database links maintain project associations
   - Easy access to project documents

4. **Error Handling**
   - File type validation
   - File existence checks
   - Permission error handling
   - User-friendly error messages

## Git Integration Strategy

### Current Implementation

Files are stored in `{DATA_DIR}/documents/` which is typically:
- Inside the project directory (if `ASSISTANT_HUB_DATA_DIR` not set)
- Outside the project directory (if `ASSISTANT_HUB_DATA_DIR` is set)

### Recommendations

1. **For Small Files (< 5MB)**: Track in Git
   - Add to repository
   - Full version control

2. **For Large Files**: Add to `.gitignore`
   - Add pattern: `documents/**/*.{pdf,xlsx,docx,one}`
   - Keeps repository size manageable

3. **Hybrid Approach** (Recommended):
   - Track metadata and small files
   - Ignore large binary files
   - Use Git LFS for important large files if needed

### Example `.gitignore` Entry

```
# Large document files
documents/**/*.pdf
documents/**/*.xlsx
documents/**/*.docx
documents/**/*.one
documents/**/*.onepkg

# But keep small text files
!documents/**/*.md
!documents/**/*.txt
```

## Usage

### Uploading a Document

1. Navigate to **Tools** tab
2. Select document type tab (e.g., "PDF Documents")
3. Click **"📤 Upload File"** button
4. Select file from file picker
5. Choose project from dropdown
6. Click **"Upload"**
7. Document appears in list (marked with 📁)

### Viewing Documents

- **Cloud documents**: Shown normally
- **Local documents**: Shown with 📁 icon prefix
- Status bar shows: "✅ Loaded X document(s) (Y cloud, Z local)"

### Project Document Access

Documents are automatically linked to projects via the `note_links` table. To view all documents for a project:

```python
from assistant_hub.document_manager import get_project_documents

# Get all documents for a project
docs = get_project_documents(conn, project_name="My Project")

# Get only PDFs for a project
pdfs = get_project_documents(conn, project_name="My Project", doc_type="pdf")
```

## Future Enhancements

1. **Project Document View**: Add section in Projects tab showing all linked documents
2. **File Preview**: Show thumbnails/previews in document list
3. **File Versioning**: Keep old versions when files are updated
4. **Bulk Upload**: Upload multiple files at once
5. **Drag-and-Drop**: Support drag-and-drop file uploads
6. **Git Integration UI**: Option to add files to Git during upload
7. **File Search**: Search across all documents
8. **Document Tags**: Add tags for better organization

## Files Modified/Created

### Created
- `assistant_hub_gui/assistant_hub/document_manager.py` - Document management module
- `DOCUMENT_UPLOAD_DESIGN.md` - Design document
- `DOCUMENT_UPLOAD_IMPLEMENTATION.md` - This file

### Modified
- `assistant_hub_gui/assistant_hub/db.py` - Added note_links database functions
- `assistant_hub_gui/assistant_hub/gui.py` - Added upload buttons and handlers, updated refresh functions

## Testing

To test the implementation:

1. **Upload Test**:
   - Go to Tools > PDF Documents
   - Click "Upload File"
   - Select a PDF file
   - Choose a project
   - Verify file appears in list

2. **Project Organization**:
   - Upload files to different projects
   - Check `{DATA_DIR}/documents/` directory structure
   - Verify files are in correct project folders

3. **Refresh Test**:
   - Upload a file
   - Click "Refresh Documents"
   - Verify both cloud and local files appear

## Notes

- Files are copied (not moved) during upload
- Original files remain in their original location
- Project names are sanitized for filesystem safety
- Filenames are sanitized to prevent path traversal
- Database links use relative paths for portability



