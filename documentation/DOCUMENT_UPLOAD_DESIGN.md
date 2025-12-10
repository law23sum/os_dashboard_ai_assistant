# Document Upload Feature - Design Document

## Executive Summary

This document outlines the design for adding file upload functionality to each document type tab (OneNote, Excel, Word, PDF) with project-based organization and Git integration.

## Storage Strategy: Hybrid Approach (Recommended)

### Decision: Metadata in Database, Files in Filesystem

**Why not Database (BLOB storage)?**
- ❌ Database bloat with large files (PDFs, Excel workbooks can be 10-100MB+)
- ❌ Poor performance for file operations
- ❌ Git cannot track binary blobs in SQLite
- ❌ Difficult to edit files with external tools
- ❌ Backup/restore becomes complex

**Why not Cloud-only?**
- ❌ Requires internet connection
- ❌ Limited control over files
- ❌ Harder to integrate with Git

**Why Hybrid (Metadata in DB, Files in FS)?**
- ✅ Scalable for large files
- ✅ Fast file operations
- ✅ Git can track files in filesystem
- ✅ External editors can access files
- ✅ Easy backup/restore
- ✅ Project-based organization
- ✅ Leverages existing `note_links` table

## Architecture

### File Storage Structure

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

### Database Schema

**Existing `note_links` table** (already supports this):
```sql
CREATE TABLE note_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,           -- Project name
    integration_type TEXT NOT NULL,     -- "local_onenote", "local_excel", "local_word", "local_pdf"
    external_id TEXT NOT NULL,           -- Relative path: "{project}/{type}/{filename}"
    title TEXT,                          -- Display name
    description TEXT,                   -- Optional description
    created_at TEXT,
    last_synced TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(name)
)
```

### Metadata Storage

For each uploaded file, store:
- **File path**: Relative to `{DATA_DIR}/documents/`
- **File size**: For display
- **Modified date**: For display and sync
- **Project association**: Via `project_id` in `note_links`
- **Document type**: Via `integration_type`

## Git Integration Strategy

### Option 1: Track in Git (Recommended for small files)
- Add `documents/` to Git repository
- Track text-based files (markdown, config files)
- Use `.gitattributes` to handle binary files properly
- **Pros**: Full version control, easy collaboration
- **Cons**: Repository size grows with files

### Option 2: Gitignore Large Files
- Add `documents/**/*.{pdf,xlsx,docx,one}` to `.gitignore`
- Track only metadata in Git
- **Pros**: Keeps repo small
- **Cons**: Files not versioned

### Option 3: Git LFS (Large File Storage)
- Use Git LFS for large binary files
- **Pros**: Version control for large files
- **Cons**: Requires Git LFS setup, additional complexity

### Recommendation: **Option 1 with Smart Filtering**

- Track small files (< 5MB) in Git
- Add large files to `.gitignore`
- Provide option to manually add files to Git if needed
- Store file size in metadata to make decisions

## Implementation Plan

### Phase 1: Core Upload Functionality
1. Add "Upload File" button to each document tab
2. File picker dialog for each document type
3. Save files to project-specific directories
4. Create `note_links` entries for uploaded files
5. Refresh document list after upload

### Phase 2: Project Integration
1. Show uploaded documents in project view
2. Link documents to projects during upload
3. Filter documents by project
4. Quick access to project documents

### Phase 3: Git Integration
1. Detect if file should be tracked in Git
2. Option to add to Git on upload
3. Show Git status for tracked files
4. Commit changes when files are updated

### Phase 4: Advanced Features
1. File versioning (keep old versions)
2. File metadata editing
3. Bulk upload
4. Drag-and-drop support

## User Experience Flow

### Upload Flow
1. User navigates to document tab (e.g., "PDF Documents")
2. Clicks "📤 Upload File" button
3. File picker opens (filtered by document type)
4. User selects file and optionally selects project
5. File is copied to `{DATA_DIR}/documents/{project}/{type}/`
6. Metadata saved to `note_links` table
7. Document list refreshes to show new file
8. Success message displayed

### Project Document Access
1. User navigates to Projects tab
2. Selects a project
3. Sees "Documents" section showing all linked documents
4. Can click to open/view document
5. Can remove document link (optionally delete file)

## File Management Functions

### Required Functions
- `upload_document(file_path, project_name, doc_type)` → Save file and create link
- `get_project_documents(project_name, doc_type=None)` → Get all documents for project
- `delete_document(link_id, delete_file=False)` → Remove link and optionally delete file
- `get_document_path(link_id)` → Get full path to document file
- `update_document_metadata(link_id, title, description)` → Update link metadata

### Database Functions
- `db_create_note_link(conn, project_id, integration_type, external_id, title, description)`
- `db_get_note_links(conn, project_id=None, integration_type=None)`
- `db_delete_note_link(conn, link_id)`
- `db_update_note_link(conn, link_id, title, description)`

## Error Handling

- File already exists → Prompt to overwrite or rename
- Invalid file type → Show error, reject upload
- Project doesn't exist → Create project or use "General"
- Disk full → Show error, rollback
- Permission denied → Show error, suggest fix

## Security Considerations

- Validate file types (extension and MIME type)
- Sanitize filenames (remove path traversal attempts)
- Limit file size (configurable, default 100MB)
- Check disk space before upload
- Validate project names

## Future Enhancements

1. **Cloud Sync**: Sync uploaded files to OneDrive/Google Drive
2. **File Preview**: Show thumbnails/previews in document list
3. **Search**: Full-text search across documents
4. **Tags**: Add tags to documents for better organization
5. **Sharing**: Share documents between projects
6. **Version History**: Keep multiple versions of documents

## Migration Path

- Existing cloud documents remain in `external_items` table
- New local uploads use `note_links` table
- Can migrate cloud documents to local storage if needed
- Both systems can coexist



