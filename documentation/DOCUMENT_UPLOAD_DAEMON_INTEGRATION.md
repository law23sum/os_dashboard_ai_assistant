# Document Upload + Git Daemon Automation Integration

## Overview

This document explains how the **Cognitive Daemon System** (git daemon automation) integrates with the **Document Upload Feature** to provide automatic versioning, monitoring, and intelligent processing of uploaded documents.

## Integration Points

### 1. Automatic Git Versioning on Upload

**Current State**: Uploaded documents are stored in filesystem but NOT automatically committed to Git.

**Integration Opportunity**: Add Git auto-commit when documents are uploaded.

#### Implementation

Modify `document_manager.py` to auto-commit uploaded files:

```python
from ..versioning import enqueue_commit

def upload_document(...):
    # ... existing upload code ...
    
    # After successful upload, auto-commit to Git
    if success:
        enqueue_commit(
            paths=[str(dest_path)],
            actor="User",  # or "Aria" if AI-assisted
            tag="document-upload",
            reason=f"Upload {doc_type} document '{safe_filename}' to project '{project_name}'"
        )
```

**Benefits**:
- Every uploaded document is automatically versioned
- Full audit trail of who uploaded what and when
- Can revert accidental uploads
- Track document history over time

### 2. Daemon Monitoring of Uploaded Documents

**Current State**: `FileSystemMonitor` watches `documents/` directory but doesn't specifically track uploaded documents.

**Integration Opportunity**: Enhance monitors to detect and process uploaded documents.

#### Enhanced FileSystemMonitor

The daemon's `FileSystemMonitor` can be enhanced to:

1. **Detect New Uploads**: Monitor `{DATA_DIR}/documents/` for newly uploaded files
2. **Process Documents**: Trigger AI processing (summarization, task extraction, etc.)
3. **Link to Projects**: Automatically associate documents with projects via `note_links`
4. **Generate Metadata**: Auto-generate descriptions, tags, summaries

#### Example Enhancement

```python
class FileSystemMonitor(BaseMonitor):
    def check(self, state: AssistantState, settings: Settings) -> List[Dict[str, Any]]:
        findings = []
        
        # Check for newly uploaded documents
        documents_dir = Path(DATA_DIR) / "documents"
        if documents_dir.exists():
            # Check all project subdirectories
            for project_dir in documents_dir.iterdir():
                if not project_dir.is_dir():
                    continue
                
                for doc_type_dir in project_dir.iterdir():
                    if not doc_type_dir.is_dir():
                        continue
                    
                    # Check for files modified in last hour (new uploads)
                    for file_path in doc_type_dir.glob("*"):
                        if file_path.is_file():
                            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                            if (datetime.now() - mtime).total_seconds() < 3600:
                                # Check if already in note_links
                                from ..document_manager import get_project_documents
                                existing = get_project_documents(
                                    self.conn, 
                                    project_name=project_dir.name,
                                    doc_type=doc_type_dir.name
                                )
                                
                                # If not in database, suggest processing
                                file_rel = f"{project_dir.name}/{doc_type_dir.name}/{file_path.name}"
                                if not any(doc["external_id"] == file_rel for doc in existing):
                                    findings.append({
                                        "type": "new_uploaded_document",
                                        "severity": "info",
                                        "project": project_dir.name,
                                        "doc_type": doc_type_dir.name,
                                        "path": str(file_path),
                                        "reason": f"New uploaded document detected: {file_path.name}",
                                    })
        
        return findings
```

### 3. Auto-Processing of Uploaded Documents

**Integration Opportunity**: Automatically process uploaded documents based on type.

#### AutoDraftService Enhancement

The `AutoDraftService` can be enhanced to:

1. **Extract Tasks from PDFs**: Auto-extract tasks from uploaded PDFs
2. **Summarize Documents**: Generate summaries for Word/PDF documents
3. **Index Content**: Extract key information for search/discovery
4. **Link to Tasks**: Automatically link documents to related tasks

#### Example Implementation

```python
class AutoDraftService(BaseAutomator):
    def process_findings(self, findings: Dict[str, List], state: AssistantState, settings: Settings) -> List[str]:
        actions = []
        
        # Process new uploaded documents
        for finding in findings.get("filesystem", []):
            if finding.get("type") == "new_uploaded_document":
                try:
                    action = self._process_uploaded_document(finding, state, settings)
                    if action:
                        actions.append(action)
                except Exception as e:
                    print(f"[AutoDraftService] Error processing document: {e}")
        
        return actions
    
    def _process_uploaded_document(self, finding: Dict, state: AssistantState, settings: Settings) -> Optional[str]:
        """Process a newly uploaded document."""
        doc_type = finding.get("doc_type")
        file_path = finding.get("path")
        project_name = finding.get("project")
        
        if doc_type == "pdf":
            # Extract tasks from PDF
            from ..file_task_extraction import extract_and_create_tasks_from_file
            tasks = extract_and_create_tasks_from_file(
                self.conn,
                file_path,
                project_name,
                owner="Aria"  # Auto-extracted by AI
            )
            
            # Auto-commit the extraction
            from ..versioning import enqueue_commit
            enqueue_commit(
                paths=[file_path],
                actor="Aria",
                tag="auto-extract",
                reason=f"Auto-extracted {len(tasks)} tasks from uploaded PDF"
            )
            
            return f"Extracted {len(tasks)} tasks from {Path(file_path).name}"
        
        elif doc_type == "word":
            # Generate summary
            # (Would use WordService to summarize)
            return f"Processed Word document: {Path(file_path).name}"
        
        return None
```

### 4. Document Update Detection

**Integration Opportunity**: Monitor uploaded documents for changes and auto-update metadata.

#### OutdatedContentMonitor Enhancement

The `OutdatedContentMonitor` can:

1. **Detect Modified Uploads**: Find uploaded documents that have been edited externally
2. **Update Metadata**: Refresh file size, modification date in database
3. **Version Changes**: Auto-commit changes to Git when files are modified
4. **Sync Status**: Track when documents need re-processing

### 5. Project Document Organization

**Integration Opportunity**: Automatically organize and link documents to projects.

#### WorkflowExecutor Enhancement

The `WorkflowExecutor` can:

1. **Create Project Document Index**: Auto-generate index of all project documents
2. **Link Related Documents**: Connect documents that reference each other
3. **Generate Project Reports**: Create summaries of all project documents
4. **Maintain Document Hierarchy**: Organize documents by type, date, importance

## Complete Integration Flow

### Upload Flow with Daemon Integration

```
1. User uploads document
   ↓
2. File saved to {DATA_DIR}/documents/{project}/{type}/{filename}
   ↓
3. Database link created in note_links table
   ↓
4. Git auto-commit triggered (NEW)
   ↓
5. FileSystemMonitor detects new file (within 60 seconds)
   ↓
6. AutoDraftService processes document:
   - PDF → Extract tasks
   - Word → Generate summary
   - Excel → Analyze data
   ↓
7. Results auto-committed to Git
   ↓
8. User notified of processing results
```

### Monitoring Flow

```
Every 60 seconds:
1. FileSystemMonitor checks documents/ directory
   ↓
2. Detects new/modified uploaded documents
   ↓
3. Checks if documents are in note_links table
   ↓
4. If missing, creates database link
   ↓
5. Triggers appropriate processing:
   - Task extraction for PDFs
   - Summarization for Word docs
   - Analysis for Excel files
   ↓
6. All changes auto-committed to Git
```

## Implementation Recommendations

### Phase 1: Git Auto-Commit (Immediate)

**Priority**: High  
**Effort**: Low  
**Impact**: High

Add Git auto-commit to `upload_document()` function:

```python
# In document_manager.py
from ..versioning import enqueue_commit

def upload_document(...):
    # ... existing code ...
    
    if success:
        # Auto-commit uploaded file
        enqueue_commit(
            paths=[str(dest_path)],
            actor="User",
            tag="document-upload",
            reason=f"Upload {doc_type} '{safe_filename}' to '{project_name}'"
        )
```

### Phase 2: Enhanced Monitoring (Short-term)

**Priority**: Medium  
**Effort**: Medium  
**Impact**: Medium

Enhance `FileSystemMonitor` to:
- Detect uploaded documents in `documents/` directory
- Check against `note_links` table
- Flag missing links for processing

### Phase 3: Auto-Processing (Medium-term)

**Priority**: Medium  
**Effort**: High  
**Impact**: High

Enhance `AutoDraftService` to:
- Auto-extract tasks from PDFs
- Generate summaries for Word docs
- Analyze Excel workbooks
- All with Git auto-commit

### Phase 4: Document Intelligence (Long-term)

**Priority**: Low  
**Effort**: Very High  
**Impact**: Very High

Add AI-powered features:
- Document relationship detection
- Cross-document knowledge synthesis
- Intelligent document organization
- Predictive document suggestions

## Git Commit Strategy for Uploaded Documents

### Commit Message Format

```
[document-upload] User auto-commit @ 2024-12-06T10:30:00 - Upload pdf 'report.pdf' to 'MyProject'
```

### Tag Options

- `document-upload` - User uploaded document
- `auto-extract` - Tasks extracted from document
- `auto-summarize` - Document summarized
- `auto-process` - Document processed by daemon

### Actor Options

- `User` - Manual upload by user
- `Aria` - AI-assisted upload or processing
- `AIC` - Audit/validation action
- `Sora` - Archive/organization action

## Benefits of Integration

### 1. Complete Audit Trail
- Every document upload is tracked in Git
- Full history of document changes
- Can revert any upload or modification

### 2. Automatic Processing
- Documents automatically processed by daemon
- Tasks extracted without user intervention
- Summaries generated automatically

### 3. Intelligent Organization
- Documents automatically linked to projects
- Metadata auto-generated
- Relationships discovered

### 4. Proactive Monitoring
- Daemon detects new uploads automatically
- Processes documents in background
- Notifies user of results

### 5. Version Safety
- All changes versioned in Git
- Never lose document history
- Full reversibility

## Example Scenarios

### Scenario 1: Upload PDF with Auto-Task Extraction

1. User uploads `project_plan.pdf` to "MyProject"
2. File saved to `documents/MyProject/pdf/project_plan.pdf`
3. Git commit: `[document-upload] User auto-commit @ ... - Upload pdf 'project_plan.pdf' to 'MyProject'`
4. Daemon detects new file (within 60 seconds)
5. AutoDraftService extracts tasks from PDF
6. 15 tasks created in database
7. Git commit: `[auto-extract] Aria auto-commit @ ... - Auto-extracted 15 tasks from uploaded PDF`
8. User sees notification: "15 tasks extracted from project_plan.pdf"

### Scenario 2: Upload Word Doc with Auto-Summarization

1. User uploads `meeting_notes.docx` to "TeamProject"
2. File saved and Git committed
3. Daemon detects new file
4. AutoDraftService generates summary
5. Summary saved as `meeting_notes_summary.txt`
6. Git commit: `[auto-summarize] Aria auto-commit @ ... - Generated summary for meeting_notes.docx`
7. Summary linked to original document in database

### Scenario 3: Document Modified Externally

1. User edits `report.docx` with external editor
2. File modification time updated
3. Daemon detects change (FileSystemMonitor)
4. OutdatedContentMonitor flags document
5. AutoUpdateService refreshes metadata
6. Git commit: `[auto-update] Aria auto-commit @ ... - Updated metadata for report.docx`

## Configuration

### Enable/Disable Features

```python
# In settings or config
DAEMON_AUTO_COMMIT_UPLOADS = True
DAEMON_AUTO_PROCESS_UPLOADS = True
DAEMON_AUTO_EXTRACT_TASKS = True
DAEMON_AUTO_SUMMARIZE = True
```

### Git Integration Settings

```python
# Track uploaded documents in Git
GIT_TRACK_UPLOADED_DOCS = True

# Auto-commit on upload
GIT_AUTO_COMMIT_UPLOADS = True

# Commit actor for uploads
GIT_UPLOAD_ACTOR = "User"  # or "Aria" for AI-assisted
```

## Conclusion

The integration between Document Upload and Git Daemon Automation creates a **powerful, self-managing document system**:

✅ **Automatic Versioning** - Every upload tracked in Git  
✅ **Intelligent Processing** - Documents auto-processed by daemon  
✅ **Proactive Monitoring** - System detects and handles new uploads  
✅ **Complete Audit Trail** - Full history of all document operations  
✅ **Zero Manual Work** - System handles organization and processing automatically  

This transforms document management from a manual task into an **automated, intelligent, fully-governed system**.



