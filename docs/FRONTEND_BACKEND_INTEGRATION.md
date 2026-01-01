# Frontend-Backend Integration with GPT-5.2 Features

This document describes the complete integration between the frontend and backend, including all GPT-5.2 features.

## Overview

The frontend and backend are now fully connected via REST APIs, with comprehensive support for GPT-5.2 features including:
- Reasoning effort levels (none, low, medium, high, xhigh)
- Verbosity control (low, medium, high)
- Tool call preambles
- Apply patch tool
- Allowed tools configuration
- Previous response ID for chain of thought passing

## Architecture

### Backend API (`backend_api/`)

**Main Entry Point:** `backend_api/main.py`
- FastAPI application with CORS middleware
- All routes prefixed with `/api`
- Health check endpoint at `/api/health`

**Chat Router:** `backend_api/routers/chat.py`
- `POST /api/chat/` - Send message with GPT-5.2 parameters
- `GET /api/chat/` - Get chat history
- `DELETE /api/chat/` - Clear chat history
- `WebSocket /api/chat/ws` - Real-time chat (future)

**GPT-5.2 Parameters Supported:**
```python
{
  "persona": "Chris",
  "model_provider": "openai",
  "content": "User message",
  "attachments": ["doc_id"],
  "reasoning_effort": "none|low|medium|high|xhigh",
  "verbosity": "low|medium|high",
  "previous_response_id": "response_id",
  "enable_preambles": false,
  "enable_apply_patch": false,
  "allowed_tools": ["execute_command", "read_file"],
  "custom_tools": [...]
}
```

### Frontend (`frontend/`)

**API Client:** `frontend/src/api.ts`
- Centralized API client with error handling
- GPT-5.2 chat endpoints:
  ```typescript
  API.chat.send({
    persona, model_provider, content, attachments,
    reasoning_effort, verbosity, previous_response_id,
    enable_preambles, enable_apply_patch, allowed_tools
  })
  ```

**Chat Page:** `frontend/src/pages/Chat.tsx`
- Full-featured chat interface
- Integrated GPT-5.2 settings panel
- Document attachment support
- Real-time message updates

**GPT-5.2 Settings Component:** `frontend/src/components/GPT52Settings.tsx`
- Collapsible settings panel
- Visual controls for all GPT-5.2 features
- Tool selector for allowed tools
- Helpful descriptions and tooltips

## API Flow

### Sending a Message

1. **User types message** in Chat page
2. **Frontend collects GPT-5.2 settings** from GPT52Settings component
3. **Frontend calls** `API.chat.send()` with all parameters
4. **Backend receives** request at `/api/chat/`
5. **Backend validates** persona, role, and parameters
6. **Backend calls** `generate_ai_reply()` from `assistant_core.ai`
7. **Backend sets environment variables** for GPT-5.2 features
8. **Backend generates AI reply** using OpenAI Responses API
9. **Backend saves** both user message and AI reply to database
10. **Backend returns** both messages in response
11. **Frontend updates** UI with new messages

### Multi-turn Conversations

1. **First message:** No `previous_response_id`
2. **Backend generates** response and returns `response_id` (in future)
3. **Frontend stores** `previous_response_id`
4. **Subsequent messages:** Include `previous_response_id`
5. **Backend passes** CoT from previous turn to model
6. **Result:** Fewer reasoning tokens, lower latency, better context

## GPT-5.2 Features Implementation

### 1. Reasoning Effort

**Backend:** Sets `ASSISTANT_HUB_REASONING_EFFORT` environment variable
**Frontend:** Dropdown selector with 5 levels
**API Parameter:** `reasoning_effort: "none" | "low" | "medium" | "high" | "xhigh"`

### 2. Verbosity

**Backend:** Sets `ASSISTANT_HUB_TEXT_VERBOSITY` environment variable
**Frontend:** Three-button selector
**API Parameter:** `verbosity: "low" | "medium" | "high"`

### 3. Tool Call Preambles

**Backend:** Adds instruction to system prompt
**Frontend:** Toggle checkbox
**API Parameter:** `enable_preambles: boolean`

### 4. Apply Patch Tool

**Backend:** Sets `ASSISTANT_HUB_ENABLE_APPLY_PATCH` environment variable
**Frontend:** Toggle checkbox
**API Parameter:** `enable_apply_patch: boolean`

### 5. Allowed Tools

**Backend:** Sets `ASSISTANT_HUB_ALLOWED_TOOLS` as JSON array
**Frontend:** Multi-select tool selector
**API Parameter:** `allowed_tools: string[]`

### 6. Previous Response ID

**Backend:** Passes to `previous_response_id` in API call
**Frontend:** Stores from previous response (future: extract from API)
**API Parameter:** `previous_response_id: string | undefined`

## UI/UX Improvements

### Modern Design
- Gradient backgrounds with backdrop blur
- Smooth transitions and animations
- Consistent color scheme (slate-900 primary)
- Responsive layout with proper spacing

### GPT-5.2 Settings Panel
- Collapsible design to save space
- Visual indicators for selected options
- Helpful descriptions for each setting
- Tool selector with checkboxes
- Info panel explaining features

### Chat Interface
- Split-panel layout (chat + documents)
- Resizable panels with drag handles
- Collapsible sections
- Smooth scrolling to latest messages
- Copy-to-clipboard functionality
- Persona and model provider selectors

### Visual Feedback
- Loading states during API calls
- Success/error toasts
- Active connection indicator
- Message timestamps
- Avatar indicators for personas

## Environment Variables

The backend uses these environment variables for GPT-5.2 features:

```bash
ASSISTANT_HUB_REASONING_EFFORT=none|low|medium|high|xhigh
ASSISTANT_HUB_TEXT_VERBOSITY=low|medium|high
ASSISTANT_HUB_ENABLE_APPLY_PATCH=true|false
ASSISTANT_HUB_ALLOWED_TOOLS=["tool1","tool2"]  # JSON array
ASSISTANT_HUB_TOOL_CHOICE_MODE=auto|required
```

These are set temporarily per-request when GPT-5.2 parameters are provided.

## Testing

### Manual Testing

1. **Start backend:**
   ```bash
   cd backend_api
   python -m uvicorn main:app --reload
   ```

2. **Start frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test GPT-5.2 features:**
   - Open Chat page
   - Expand GPT-5.2 Settings
   - Change reasoning effort and verbosity
   - Enable preambles and apply patch
   - Select allowed tools
   - Send a message
   - Verify settings are applied

### API Testing

```bash
# Send message with GPT-5.2 features
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "persona": "Sora",
    "model_provider": "openai",
    "content": "Hello!",
    "reasoning_effort": "medium",
    "verbosity": "high",
    "enable_preambles": true
  }'
```

## Future Enhancements

1. **WebSocket Support:** Real-time streaming responses
2. **Response ID Extraction:** Properly extract and use `previous_response_id` from API responses
3. **Custom Tools UI:** Visual editor for creating custom tools
4. **CFG Grammar Editor:** UI for defining context-free grammars
5. **Settings Persistence:** Save GPT-5.2 preferences per user
6. **Analytics:** Track reasoning effort vs. response quality
7. **A/B Testing:** Compare different reasoning/verbosity settings

## Troubleshooting

### Frontend can't connect to backend
- Check CORS settings in `backend_api/main.py`
- Verify API base URL in `frontend/vite.config.ts`
- Check backend is running on correct port

### GPT-5.2 settings not applying
- Verify environment variables are being set in backend
- Check API request includes all parameters
- Review backend logs for errors

### Tools not working
- Ensure `enable_shell` is true in backend
- Check tool definitions in `get_shell_functions()`
- Verify allowed_tools array format

## References

- [GPT-5.2 Features Documentation](./GPT5.2_FEATURES.md)
- [Backend API Documentation](http://localhost:8000/swagger)
- [Frontend API Client](../frontend/src/api.ts)




