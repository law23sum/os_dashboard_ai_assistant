# Reusable Code Patterns from OpenAI Assistants Quickstart

## Overview

This document provides specific code patterns from the OpenAI Assistants Quickstart that can be adapted for the OS Dashboard AI Assistant project, aligned with technical specifications v6.

---

## Pattern 1: Streaming Chat Interface

### Source: `app/components/chat.tsx`

**Current Project Gap**: Chat interfaces exist but lack real-time streaming updates.

**Reusable Pattern**:
```typescript
// Event-driven streaming handler
const handleReadableStream = (stream: AssistantStream) => {
  // Text streaming
  stream.on("textCreated", handleTextCreated);
  stream.on("textDelta", handleTextDelta);
  
  // Code interpreter streaming
  stream.on("toolCallCreated", toolCallCreated);
  stream.on("toolCallDelta", toolCallDelta);
  
  // Function calling
  stream.on("event", (event) => {
    if (event.event === "thread.run.requires_action")
      handleRequiresAction(event);
    if (event.event === "thread.run.completed")
      handleRunCompleted();
  });
};
```

**Adaptation for FastAPI + React**:
```python
# backend_api/routers/chat.py
from fastapi.responses import StreamingResponse
import json

@router.post("/chat/stream")
async def stream_chat(message: ChatMessageCreate):
    async def event_generator():
        # Create assistant run
        run = await create_assistant_run(message)
        
        # Stream events
        async for event in stream_assistant_events(run):
            if event.type == "text.delta":
                yield f"data: {json.dumps({'type': 'text_delta', 'content': event.delta})}\n\n"
            elif event.type == "tool_call.delta":
                yield f"data: {json.dumps({'type': 'tool_delta', 'content': event.delta})}\n\n"
            elif event.type == "run.requires_action":
                yield f"data: {json.dumps({'type': 'requires_action', 'data': event.data})}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

```typescript
// frontend/src/hooks/useStreamingChat.ts
export const useStreamingChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  
  const sendMessage = async (content: string) => {
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
    
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          
          if (data.type === 'text_delta') {
            setMessages(prev => {
              const last = prev[prev.length - 1];
              return [...prev.slice(0, -1), {
                ...last,
                content: last.content + data.content
              }];
            });
          }
        }
      }
    }
  };
  
  return { messages, sendMessage };
};
```

**Tech Spec Alignment**: Section 1.7.3 (Intent Model & Context Assembly), Section 1.7.4 (Driver-Aware Planning Loop)

---

## Pattern 2: Thread-Based Conversation Management

### Source: `app/api/assistants/threads/route.ts`

**Current Project Gap**: Conversations are stored but not isolated by thread/context.

**Reusable Pattern**:
```typescript
// Thread creation
export async function POST() {
  const thread = await openai.beta.threads.create();
  return Response.json({ threadId: thread.id });
}
```

**Adaptation for Current Project**:
```python
# backend_api/routers/threads.py
from sqlalchemy.orm import Session
from assistant_hub.db import Thread, ChatMessage

@router.post("/threads", response_model=ThreadResponse)
async def create_thread(
    project_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a new conversation thread.
    
    Maps to Tech Spec Section 3.7 (Project Ledger, Events, Timelines)
    """
    thread = Thread(
        project_id=project_id,
        created_at=datetime.utcnow()
    )
    db.add(thread)
    db.commit()
    db.refresh(thread)
    
    # Log to Project Ledger
    await log_to_ledger(
        event_type="thread.created",
        thread_id=thread.id,
        project_id=project_id
    )
    
    return ThreadResponse(id=thread.id, created_at=thread.created_at)
```

**Database Schema Addition**:
```python
# assistant_hub/db.py
class Thread(Base):
    __tablename__ = "threads"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    persona = Column(String, default="Chris")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="thread")
    project = relationship("Project", back_populates="threads")

class ChatMessage(Base):
    # ... existing fields ...
    thread_id = Column(String, ForeignKey("threads.id"), nullable=True)
    thread = relationship("Thread", back_populates="messages")
```

**Tech Spec Alignment**: Section 3.7 (Project Ledger), Section 11.5 (Record Auditor & Logbook)

---

## Pattern 3: Function Calling / Tool Integration

### Source: `app/api/assistants/threads/[threadId]/actions/route.ts`

**Current Project Gap**: Tool system exists but lacks standardized function calling interface.

**Reusable Pattern**:
```typescript
// Tool output submission
export async function POST(request, { params: { threadId } }) {
  const { toolCallOutputs, runId } = await request.json();
  
  const stream = openai.beta.threads.runs.submitToolOutputsStream(
    threadId,
    runId,
    { tool_outputs: toolCallOutputs }
  );
  
  return new Response(stream.toReadableStream());
}
```

**Adaptation for Driver Architecture**:
```python
# assistant_core/tool_executor.py
from typing import Dict, Any, List
from assistant_core.drivers import DriverRegistry

class ToolExecutor:
    """Executes tools/drivers with standardized interface.
    
    Maps to Tech Spec Section 5.1 (Driver Taxonomy & Design Principles)
    """
    
    def __init__(self):
        self.driver_registry = DriverRegistry()
    
    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool/driver with validation and logging."""
        
        # Get driver from registry
        driver = self.driver_registry.get_driver(tool_name)
        if not driver:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Validate arguments against driver schema
        validated_args = driver.validate_arguments(arguments)
        
        # Check policy/permissions
        if not await self._check_permissions(driver, context):
            raise PermissionError(f"Not authorized to use {tool_name}")
        
        # Execute driver
        try:
            result = await driver.execute(validated_args, context)
            
            # Log to Project Ledger
            await self._log_execution(
                tool_name=tool_name,
                arguments=validated_args,
                result=result,
                context=context
            )
            
            return {
                "output": result,
                "tool_call_id": context.get("tool_call_id"),
                "status": "success"
            }
        except Exception as e:
            # Log error
            await self._log_execution(
                tool_name=tool_name,
                arguments=validated_args,
                error=str(e),
                context=context
            )
            raise

# backend_api/routers/tools.py
@router.post("/tools/execute")
async def execute_tool(
    request: ToolExecuteRequest,
    user: AuthUser = Depends(get_current_user)
):
    """Execute a tool/driver call.
    
    Maps to Tech Spec Section 8.10 (Workflow Engine & Orchestration)
    """
    executor = ToolExecutor()
    
    result = await executor.execute_tool(
        tool_name=request.tool_name,
        arguments=request.arguments,
        context={
            "user_id": user.id,
            "thread_id": request.thread_id,
            "tool_call_id": request.tool_call_id
        }
    )
    
    return result
```

**Tech Spec Alignment**: Section 5.1-5.14 (Driver Architecture), Section 8.10 (Workflow Engine)

---

## Pattern 4: File Search & Vector Store

### Source: `app/api/assistants/files/route.tsx`

**Current Project Gap**: No vector store or semantic search capabilities.

**Reusable Pattern**:
```typescript
// Vector store management
const getOrCreateVectorStore = async () => {
  const assistant = await openai.beta.assistants.retrieve(assistantId);
  
  if (assistant.tool_resources?.file_search?.vector_store_ids?.length > 0) {
    return assistant.tool_resources.file_search.vector_store_ids[0];
  }
  
  const vectorStore = await openai.beta.vectorStores.create({
    name: "sample-assistant-vector-store",
  });
  
  await openai.beta.assistants.update(assistantId, {
    tool_resources: {
      file_search: {
        vector_store_ids: [vectorStore.id],
      },
    },
  });
  
  return vectorStore.id;
};
```

**Adaptation for CIR Store**:
```python
# assistant_core/vector_store.py
from typing import List, Optional
import chromadb  # or pinecone, weaviate, etc.

class VectorStoreService:
    """Manages vector stores for semantic search.
    
    Maps to Tech Spec Section 6.2 (CIR Store, Document Indexing)
    """
    
    def __init__(self):
        self.client = chromadb.Client()
        self.collections: Dict[str, Collection] = {}
    
    async def get_or_create_vector_store(
        self,
        project_id: str,
        store_name: Optional[str] = None
    ) -> str:
        """Get or create a vector store for a project."""
        store_name = store_name or f"project_{project_id}_vectors"
        
        if store_name not in self.collections:
            self.collections[store_name] = self.client.get_or_create_collection(
                name=store_name,
                metadata={"project_id": project_id}
            )
        
        return store_name
    
    async def add_file(
        self,
        store_name: str,
        file_id: str,
        content: str,
        metadata: Dict[str, Any]
    ):
        """Add file to vector store with automatic chunking."""
        # Chunk content for better retrieval
        chunks = self._chunk_content(content, chunk_size=1000)
        
        # Generate embeddings
        embeddings = await self._generate_embeddings(chunks)
        
        # Add to collection
        self.collections[store_name].add(
            ids=[f"{file_id}_{i}" for i in range(len(chunks))],
            embeddings=embeddings,
            documents=chunks,
            metadatas=[{**metadata, "chunk_index": i} for i in range(len(chunks))]
        )
    
    async def search(
        self,
        store_name: str,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Semantic search in vector store."""
        query_embedding = await self._generate_embeddings([query])
        
        results = self.collections[store_name].query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        
        return [
            {
                "file_id": result["ids"][0].split("_")[0],
                "content": result["documents"][0],
                "metadata": result["metadatas"][0],
                "score": result["distances"][0]
            }
            for result in zip(
                results["ids"],
                results["documents"],
                results["metadatas"],
                results["distances"]
            )
        ]

# backend_api/routers/files.py
@router.post("/files/upload")
async def upload_file(
    file: UploadFile,
    project_id: str,
    vector_store: VectorStoreService = Depends(get_vector_store)
):
    """Upload file and add to vector store.
    
    Maps to Tech Spec Section 6.5 (Search & Retrieval Services)
    """
    # Save file
    file_id = await save_file(file, project_id)
    
    # Read content
    content = await read_file_content(file_id)
    
    # Add to vector store
    store_name = await vector_store.get_or_create_vector_store(project_id)
    await vector_store.add_file(
        store_name=store_name,
        file_id=file_id,
        content=content,
        metadata={
            "project_id": project_id,
            "filename": file.filename,
            "uploaded_at": datetime.utcnow().isoformat()
        }
    )
    
    # Log to CIR Store
    await add_to_cir_store(file_id, content, project_id)
    
    return {"file_id": file_id, "status": "indexed"}
```

**Tech Spec Alignment**: Section 6.2 (CIR Store), Section 6.5 (Search & Retrieval)

---

## Pattern 5: Message State Management

### Source: `app/components/chat.tsx` (lines 217-248)

**Reusable Pattern**:
```typescript
// Incremental message updates
const appendToLastMessage = (text) => {
  setMessages((prevMessages) => {
    const lastMessage = prevMessages[prevMessages.length - 1];
    const updatedLastMessage = {
      ...lastMessage,
      text: lastMessage.text + text,
    };
    return [...prevMessages.slice(0, -1), updatedLastMessage];
  });
};

const appendMessage = (role, text) => {
  setMessages((prevMessages) => [...prevMessages, { role, text }]);
};
```

**Adaptation for React Frontend**:
```typescript
// frontend/src/hooks/useMessageState.ts
import { useState, useCallback } from 'react';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  thread_id?: string;
}

export const useMessageState = (initialMessages: Message[] = []) => {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  
  const appendMessage = useCallback((role: Message['role'], content: string) => {
    const newMessage: Message = {
      id: crypto.randomUUID(),
      role,
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
  }, []);
  
  const appendToLastMessage = useCallback((content: string) => {
    setMessages(prev => {
      if (prev.length === 0) {
        return [{ 
          id: crypto.randomUUID(),
          role: 'assistant',
          content,
          timestamp: new Date()
        }];
      }
      
      const lastMessage = prev[prev.length - 1];
      const updatedLastMessage = {
        ...lastMessage,
        content: lastMessage.content + content
      };
      
      return [...prev.slice(0, -1), updatedLastMessage];
    });
  }, []);
  
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);
  
  return {
    messages,
    appendMessage,
    appendToLastMessage,
    clearMessages
  };
};
```

---

## Pattern 6: Assistant Configuration Management

### Source: `app/assistant-config.ts`

**Reusable Pattern**:
```typescript
export let assistantId = "";

if (assistantId === "") {
  assistantId = process.env.OPENAI_ASSISTANT_ID;
}
```

**Adaptation for Multi-Persona System**:
```python
# assistant_core/persona_config.py
from typing import Dict, Optional
from dataclasses import dataclass
import os

@dataclass
class PersonaConfig:
    """Configuration for a persona/assistant.
    
    Maps to Tech Spec Section 0.5 (Cognitive Agents & Personas)
    """
    name: str
    assistant_id: Optional[str] = None
    model: str = "gpt-5.2"
    system_prompt: str = ""
    tools: List[str] = None
    temperature: float = 0.7
    
    def __post_init__(self):
        if self.assistant_id is None:
            self.assistant_id = os.getenv(f"OPENAI_ASSISTANT_ID_{self.name.upper()}")
        if self.tools is None:
            self.tools = []

class PersonaRegistry:
    """Registry for persona configurations."""
    
    def __init__(self):
        self.personas: Dict[str, PersonaConfig] = {
            "Chris": PersonaConfig(
                name="Chris",
                model="gpt-5-mini",
                system_prompt="You are Chris, the primary user persona..."
            ),
            "AIC": PersonaConfig(
                name="AIC",
                model="gpt-5.2-pro",
                system_prompt="You are AIC, the meta-governor..."
            ),
            "Aria": PersonaConfig(
                name="Aria",
                model="gpt-5.1-codex-max",
                system_prompt="You are Aria, the emotional/symbolic muse..."
            ),
            "Sora": PersonaConfig(
                name="Sora",
                model="gpt-5.2",
                system_prompt="You are Sora, the structural architect..."
            )
        }
    
    def get_persona(self, name: str) -> PersonaConfig:
        """Get persona configuration."""
        return self.personas.get(name, self.personas["Chris"])
    
    def register_persona(self, config: PersonaConfig):
        """Register a new persona."""
        self.personas[config.name] = config
```

**Tech Spec Alignment**: Section 0.5 (Cognitive Agents & Personas)

---

## Integration Checklist

### Phase 1: Streaming Chat (High Priority)
- [ ] Implement SSE streaming in FastAPI
- [ ] Create `useStreamingChat` React hook
- [ ] Update chat components to use streaming
- [ ] Add event handlers for text deltas
- [ ] Test with long-running responses

### Phase 2: Thread Management (High Priority)
- [ ] Add Thread model to database
- [ ] Create thread API endpoints
- [ ] Update chat UI for thread selection
- [ ] Integrate with Project Ledger
- [ ] Add thread-based message filtering

### Phase 3: Enhanced Tool System (Medium Priority)
- [ ] Create ToolExecutor class
- [ ] Implement tool schema validation
- [ ] Add tool output streaming
- [ ] Integrate with Driver Registry
- [ ] Add tool execution logging

### Phase 4: Vector Store (Medium Priority)
- [ ] Choose vector database (ChromaDB/Pinecone/Weaviate)
- [ ] Implement VectorStoreService
- [ ] Add file upload with indexing
- [ ] Create semantic search API
- [ ] Integrate with CIR Store

### Phase 5: Persona Configuration (Low Priority)
- [ ] Create PersonaRegistry
- [ ] Add persona-specific configurations
- [ ] Implement persona switching
- [ ] Add persona-specific tools
- [ ] Update UI for persona selection

---

## Notes

1. **Not Direct Copy**: These patterns should be adapted, not copied exactly. The OpenAI quickstart uses Next.js and TypeScript, while the current project uses FastAPI and Python backend with React frontend.

2. **Architecture Alignment**: All adaptations maintain alignment with Technical Specifications v6, particularly:
   - Driver Architecture (Section 5)
   - Project Ledger (Section 3.7)
   - CIR Store (Section 6.2)
   - Personas (Section 0.5)

3. **Incremental Implementation**: Implement patterns incrementally, starting with high-priority items (streaming, threads) before moving to medium-priority features.

4. **Testing**: Each pattern should be thoroughly tested before integration, especially streaming and tool execution.


