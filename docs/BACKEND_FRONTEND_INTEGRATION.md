# Backend-Frontend Integration Guide

## Overview

The codebase now has full integration between:
- **Python FastAPI Backend** (`backend_api/`)
- **React Frontend** (`frontend/`)
- **Next.js Quickstart** (`openai-assistants-quickstart/`)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│  (frontend/) - Main application UI                      │
│  - Pages: Dashboard, Chat, Projects, etc.               │
│  - Components: Layout, Navigation, etc.                  │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP/REST API
                   │ /api/*
┌──────────────────▼──────────────────────────────────────┐
│              Python FastAPI Backend                      │
│  (backend_api/) - REST API Server                       │
│  - Routers: chat, projects, tasks, etc.                 │
│  - Responses API: /api/responses/*                      │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ (Optional)
┌──────────────────▼──────────────────────────────────────┐
│          Next.js Quickstart (Optional)                  │
│  (openai-assistants-quickstart/)                        │
│  - Can use Python backend via USE_PYTHON_BACKEND=true   │
│  - Or use OpenAI directly                               │
└─────────────────────────────────────────────────────────┘
```

## API Endpoints

### Main Backend API

**Base URL**: `http://localhost:8000/api`

#### Chat Endpoints
- `GET /api/chat/` - Get chat history
- `POST /api/chat/` - Send message
- `DELETE /api/chat/` - Clear history
- `WS /api/chat/ws` - WebSocket for real-time chat

#### Responses API (New)
- `POST /api/responses/conversations` - Create conversation
- `GET /api/responses/conversations/{id}` - Get conversation
- `POST /api/responses/responses` - Create response (streaming supported)

#### Other Endpoints
- `GET /api/projects` - List projects
- `GET /api/tasks` - List tasks
- `GET /api/dashboard/summary` - Dashboard data
- And many more...

### Frontend API Client

The frontend uses a centralized API client:

```typescript
// frontend/src/lib/apiClient.ts
import apiClient, { apiPath } from '../lib/apiClient'

// Usage
const { data } = await apiClient.get(apiPath('chat/'))
const { data } = await apiClient.post(apiPath('chat/'), payload)
```

## Integration Points

### 1. Responses API Bridge

**File**: `backend_api/routers/responses_api.py`

This router bridges the Responses API format to the internal chat system:

- Converts Responses API format to internal ChatMessage format
- Handles streaming responses
- Manages conversations
- Supports tool calls (code interpreter, file search, functions)

### 2. Next.js Quickstart Integration

**Files**: 
- `openai-assistants-quickstart/app/api/assistants/threads/route.ts`
- `openai-assistants-quickstart/app/api/assistants/threads/[threadId]/messages/route.ts`

The Next.js app can now use the Python backend by setting:

```bash
USE_PYTHON_BACKEND=true
PYTHON_BACKEND_URL=http://localhost:8000
```

### 3. Frontend Responses Chat Page

**File**: `frontend/src/pages/ResponsesChat.tsx`

A new modern chat interface that:
- Uses the Responses API
- Supports streaming
- Shows tool calls
- Has improved UX/UI

**Route**: `/chat/responses`

## Configuration

### Environment Variables

#### Frontend (Vite)
```bash
# .env.local
VITE_API_BASE_URL=http://localhost:8000/api
```

#### Next.js Quickstart
```bash
# .env.local
USE_PYTHON_BACKEND=true
PYTHON_BACKEND_URL=http://localhost:8000
OPENAI_API_KEY=sk-...
OPENAI_PROMPT_ID=prompt_...
```

#### Backend
```bash
# No special config needed
# Runs on http://localhost:8000 by default
```

## Usage Examples

### Using Responses API from Frontend

```typescript
// Create conversation
const { data } = await apiClient.post(apiPath('responses/conversations'), {
  metadata: { created_at: new Date().toISOString() }
})

// Send message with streaming
const response = await fetch(apiPath('responses/responses'), {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'gpt-4o',
    input: [{
      role: 'user',
      content: [{ type: 'input_text', text: 'Hello!' }]
    }],
    conversation: conversationId,
    store: true,
    stream: true,
  })
})

// Stream response
const reader = response.body?.getReader()
// ... handle streaming
```

### Using Traditional Chat API

```typescript
// Send message
const { data } = await apiClient.post(apiPath('chat/'), {
  persona: 'AIC',
  content: 'Hello!',
  role: 'user',
  kind: 'chat'
})
```

## Development Workflow

### 1. Start Backend

```bash
# Terminal 1
cd /path/to/project
python -m uvicorn backend_api.main:app --reload --port 8000
```

### 2. Start Frontend

```bash
# Terminal 2
cd frontend
npm run dev
```

### 3. (Optional) Start Next.js Quickstart

```bash
# Terminal 3
cd openai-assistants-quickstart
npm run dev
```

## Testing Integration

### Test Backend Health

```bash
curl http://localhost:8000/api/health
```

### Test Responses API

```bash
# Create conversation
curl -X POST http://localhost:8000/api/responses/conversations \
  -H "Content-Type: application/json" \
  -d '{"metadata": {}}'

# Send message
curl -X POST http://localhost:8000/api/responses/responses \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "input": [{
      "role": "user",
      "content": [{"type": "input_text", "text": "Hello!"}]
    }],
    "conversation": "conv_...",
    "store": true
  }'
```

## Troubleshooting

### CORS Issues

The backend has CORS configured for:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Next.js)
- `http://localhost:8000` (Backend)

If you need additional origins, update `backend_api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        # Add your origin here
    ],
    # ...
)
```

### API Not Responding

1. Check backend is running: `curl http://localhost:8000/api/health`
2. Check frontend proxy config in `frontend/vite.config.ts`
3. Check browser console for errors
4. Check network tab for failed requests

### Streaming Not Working

1. Ensure `stream: true` in request
2. Check response headers include `text/event-stream`
3. Verify SSE format in response
4. Check browser console for parsing errors

## Next Steps

1. **Enhanced Streaming**: Improve streaming performance
2. **Tool Integration**: Better tool call visualization
3. **Error Handling**: More robust error handling
4. **Caching**: Add response caching
5. **Rate Limiting**: Implement rate limiting
6. **Authentication**: Add auth to Responses API endpoints

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Query Documentation](https://tanstack.com/query)
- [Responses API Guide](./ASSISTANTS_MIGRATION.md)
- [Frontend API Client](../frontend/src/lib/apiClient.ts)


