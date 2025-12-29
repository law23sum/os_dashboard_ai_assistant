# Assistants API Deprecation Status

**Last Updated**: 2025-01-27  
**Deprecation Deadline**: August 26, 2026  
**Migration Guide**: https://platform.openai.com/docs/assistants/migration

## Executive Summary

OpenAI has deprecated the Assistants API in favor of the Responses API. The main codebase has been successfully migrated, but the `openai-assistants-quickstart/` directory still uses the deprecated API.

## Migration Status

### ✅ Fully Migrated (Main Codebase)

The following components have been migrated to the Responses API:

1. **Core AI Functions**
   - `assistant_core/ai.py` - Uses `client.responses.create()`
   - `assistant_hub/ai.py` - Uses Responses API
   - `assistant_hub_gui/assistant_hub/ai.py` - Uses Responses API

2. **Client Libraries**
   - `assistant_core/ai_layer/openai_client.py` - Responses API client
   - `assistant_hub/ai_layer/openai_client.py` - Responses API client
   - `assistant_hub_gui/assistant_hub/ai_layer/openai_client.py` - Responses API client

3. **Helper Functions**
   - `assistant_core/conversation_helpers.py` - Conversation management
   - Migration utilities for threads → conversations

4. **Demo Scripts**
   - `scripts/responses_demo.py` - New Responses API demo (replaces `assistants_demo.py`)

5. **Documentation**
   - `docs/ASSISTANTS_MIGRATION.md` - Comprehensive migration guide
   - `docs/ENHANCED_CAPABILITIES.md` - New features documentation

### ✅ Migrated (Quickstart Directory)

**`openai-assistants-quickstart/`** - Next.js quickstart template

**Status**: ✅ **FULLY MIGRATED** to Responses API (January 2025)

#### Migration Summary:

1. **API Routes** (TypeScript/Next.js):
   - ✅ `app/api/assistants/threads/route.ts` - Migrated to `conversations.create()`
   - ✅ `app/api/assistants/threads/[threadId]/messages/route.ts` - Migrated to `responses.create()` with streaming
   - ✅ `app/api/assistants/threads/[threadId]/actions/route.ts` - Migrated to `responses.create()` with tool outputs
   - ✅ `app/api/assistants/files/route.tsx` - Updated for Responses API (vector stores still used)
   - ⚠️ `app/api/assistants/route.ts` - Deprecated but kept for legacy support with warnings

2. **Frontend Components**:
   - ✅ `app/components/chat.tsx` - Migrated to Responses API streaming (custom SSE handler)
   - ✅ `app/components/warnings.tsx` - Updated to show prompt ID guidance

3. **Configuration**:
   - ✅ `app/assistant-config.ts` - Added `promptId` support, kept `assistantId` for legacy

4. **Documentation**:
   - ✅ `README.md` - Updated with migration instructions
   - ✅ `MIGRATION_NOTES.md` - Detailed migration documentation

## Key API Changes

| Assistants API (Deprecated) | Responses API (Current) |
|------------------------------|-------------------------|
| `beta.assistants.create()` | Create Prompts in dashboard |
| `beta.threads.create()` | `conversations.create()` |
| `beta.threads.runs.create()` | `responses.create()` |
| `beta.threads.runs.stream()` | `responses.create(stream=True)` |
| `beta.threads.runs.submitToolOutputs()` | New `responses.create()` with tool outputs |
| `AssistantStream` | Responses API streaming |

## Migration Requirements for Quickstart

### 1. Replace Assistants with Prompts

**Before:**
```typescript
const assistant = await openai.beta.assistants.create({
  instructions: "You are a helpful assistant.",
  model: "gpt-4o",
  tools: [...]
});
```

**After:**
- Create prompt in OpenAI Dashboard
- Reference by ID: `prompt: { id: "prompt_123" }`

### 2. Replace Threads with Conversations

**Before:**
```typescript
const thread = await openai.beta.threads.create();
```

**After:**
```typescript
const conversation = await openai.conversations.create();
```

### 3. Replace Runs with Responses

**Before:**
```typescript
const stream = openai.beta.threads.runs.stream(threadId, {
  assistant_id: assistantId,
});
```

**After:**
```typescript
const response = await openai.responses.create({
  prompt: { id: promptId },
  input: [{ role: "user", content: [{ type: "input_text", text: message }] }],
  conversation: conversationId,
  store: true,
  stream: true,
});
```

### 4. Update Tool Handling

**Before:**
```typescript
await openai.beta.threads.runs.submitToolOutputsStream(
  threadId,
  runId,
  { tool_outputs: toolCallOutputs }
);
```

**After:**
```typescript
await openai.responses.create({
  conversation: conversationId,
  input: [{
    role: "tool",
    content: toolCallOutputs.map(output => ({
      type: "tool_output",
      tool_call_id: output.tool_call_id,
      output: output.output
    }))
  }],
  store: true,
});
```

### 5. Update Streaming

The Responses API uses a different streaming format. The `AssistantStream` class needs to be replaced with Responses API streaming handlers.

## Recommended Actions

### Immediate (Before Q2 2026)

1. ✅ **Main codebase migration** - COMPLETE
2. ✅ **Migrate quickstart directory** - COMPLETE (January 2025)
3. ✅ **Add deprecation warnings** - COMPLETE
4. ✅ **Update documentation** - COMPLETE

### Before August 2026

1. Complete quickstart migration
2. Remove all deprecated API calls
3. Update all examples and documentation
4. Test thoroughly with Responses API

## Resources

- [Official Migration Guide](https://platform.openai.com/docs/assistants/migration)
- [Responses API Documentation](https://platform.openai.com/docs/api-reference/responses)
- [Conversations API Documentation](https://platform.openai.com/docs/api-reference/conversations)
- [Internal Migration Guide](./ASSISTANTS_MIGRATION.md)
- [Enhanced Capabilities Guide](./ENHANCED_CAPABILITIES.md)

## Testing

After migration, test the following:

1. ✅ Basic chat functionality
2. ✅ Function calling
3. ✅ Code interpreter
4. ✅ File search
5. ✅ Streaming responses
6. ✅ Multi-turn conversations
7. ✅ Tool output submission

## Notes

- The main codebase maintains backward compatibility with `previous_response_id` pattern
- `create_assistant()` methods still exist but emit deprecation warnings
- The quickstart directory is a reference implementation and may not be actively used in production

