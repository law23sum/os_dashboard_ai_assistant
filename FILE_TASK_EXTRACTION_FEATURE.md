# File Task Extraction Feature

## Overview

This feature allows you to upload a file for a specific project, and the system will automatically extract tasks from the file content using AI, then create them in the todo list organized by sequence order.

## How It Works

1. **Select a Project**: In the Projects tab, select the project you want to add tasks to
2. **Upload File**: Click the "📁 Upload File & Extract Tasks" button
3. **AI Extraction**: The system uses AI to analyze the file and extract:
   - Task titles
   - Sequence/order numbers
   - Priorities
   - Additional notes/context
   - Dependencies between tasks
4. **Task Creation**: Tasks are automatically created in the database, organized by sequence
5. **Dependencies**: Tasks are linked sequentially (each task depends on the previous one) to maintain order

## Supported File Types

- Text files (`.txt`)
- Markdown (`.md`)
- PDF (`.pdf`)
- Word documents (`.docx`)
- Rich Text Format (`.rtf`)
- CSV (`.csv`)
- Any text-readable file

## Features

### AI-Powered Extraction
- Uses GPT-4o-mini to intelligently extract tasks from documents
- Understands context and structure
- Extracts sequence numbers, priorities, and dependencies

### Sequential Organization
- Tasks are created in the order they appear in the document
- Each task depends on the previous one to maintain sequence
- Sequence numbers are stored in task notes

### Fallback Mode
- If AI is unavailable, uses regex-based pattern matching
- Extracts bullet points, numbered lists, TODO items, etc.
- Still maintains sequence order

## Usage Example

1. Open the **Projects** tab
2. Select a project (e.g., "Portfolio Strategist MVP")
3. Scroll down to the "📄 Extract Tasks from File" section
4. Click "📁 Upload File & Extract Tasks"
5. Select your file (e.g., a project plan document)
6. Wait for extraction (status updates shown)
7. Review the created tasks in the Tasks tab

## What Gets Extracted

The AI looks for:
- Task titles and descriptions
- Sequence/step numbers
- Priority indicators (HIGH, MEDIUM, LOW, CRITICAL)
- Dependencies between tasks
- Additional context and notes

## Task Properties

Each extracted task includes:
- **Title**: Extracted from the document
- **Project**: Automatically set to the selected project
- **Status**: Set to "TODO"
- **Priority**: Extracted or defaults to "MEDIUM"
- **Owner**: Set to the active persona
- **Notes**: Includes sequence number and any additional context
- **Dependencies**: Sequential dependencies to maintain order

## Status Messages

- **"Extracting tasks..."** (blue): Processing in progress
- **"✓ X tasks extracted"** (green): Success
- **"No tasks found in file"** (orange): No tasks could be extracted
- **"Error extracting tasks"** (red): An error occurred

## Technical Details

### Files Created
- `assistant_hub/file_task_extraction.py`: Core extraction logic
- UI integration in `assistant_hub/gui.py`: Projects tab upload section

### AI Prompt
The system sends the file content to GPT-4o-mini with a prompt asking it to:
- Extract all tasks, action items, or to-do items
- Return them as JSON with sequence numbers
- Identify priorities and dependencies
- Maintain the original order

### Fallback Extraction
If AI is unavailable, the system uses regex patterns to find:
- Bullet points (`-`, `*`, `•`)
- Numbered lists (`1.`, `2.`, etc.)
- TODO markers
- Step/Phase/Stage indicators

## Limitations

1. **File Size**: Large files are truncated to 8000 characters for AI processing
2. **Binary Files**: Binary files (images, executables) cannot be processed
3. **Complex Formats**: PDF and Word documents need proper text extraction
4. **AI Dependency**: Best results require OpenAI API key configured

## Future Enhancements

- Support for more file formats
- Better PDF text extraction
- Image OCR for scanned documents
- Custom extraction rules per project
- Batch file processing
- Preview before creating tasks

