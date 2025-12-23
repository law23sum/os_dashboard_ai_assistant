# Frontend-Backend API Connection Guide

## Overview

The frontend and backend are now fully connected via a comprehensive API service layer. This document outlines the connection architecture, API services, and UI improvements.

## Architecture

### Connection Flow

```
Frontend (React/TypeScript) 
  ↓
API Service Layer (services/api.ts)
  ↓
API Client (lib/apiClient.ts)
  ↓
Vite Proxy (vite.config.ts)
  ↓
Backend API (FastAPI - backend_api/main.py)
  ↓
Routers (backend_api/routers/*.py)
```

### Key Components

1. **API Service Layer** (`frontend/src/services/api.ts`)
   - Centralized API methods for all endpoints
   - Type-safe API calls
   - Consistent error handling

2. **API Client** (`frontend/src/lib/apiClient.ts`)
   - Base HTTP client with authentication
   - Request/response interceptors
   - Error parsing and handling

3. **Vite Proxy** (`frontend/vite.config.ts`)
   - Proxies `/api/*` requests to backend
   - Handles CORS and WebSocket connections

4. **Backend API** (`backend_api/main.py`)
   - FastAPI application
   - CORS middleware configured
   - Multiple router modules

## API Services

### Available Services

All services are exported from `frontend/src/services/api.ts`:

```typescript
import api from '../services/api'

// Tasks
const tasks = await api.tasks.list()
await api.tasks.create({ title: 'New task' })
await api.tasks.update(id, { status: 'DONE' })
await api.tasks.delete(id)

// Projects
const projects = await api.projects.list()
await api.projects.create({ name: 'New Project' })

// Chat
const messages = await api.chat.list('AIC')
const response = await api.chat.send({
  persona: 'AIC',
  model_provider: 'openai',
  content: 'Hello!'
})

// Dashboard
const stats = await api.dashboard.getStats()
const systemStatus = await api.dashboard.getSystemStatus()

// Documents
const documents = await api.documents.list()
await api.documents.create({ title: 'New Doc' })

// Settings
const settings = await api.settings.get()
await api.settings.update({ theme: 'dark' })

// Integrations
const integrations = await api.integrations.list()
await api.integrations.connect('github')

// Analytics
const metrics = await api.analytics.getMetrics()

// Search
const results = await api.search.search('query')

// Workspace
const health = await api.workspace.getHealth()
await api.workspace.scan()

// Terminal
await api.terminal.execute('ls -la', '/path/to/cwd')

// AI Systems
const response = await api.ai.ask('What is AI?')
const personas = await api.ai.getPersonas()
```

## UI Components

### New UI Components

All components are in `frontend/src/components/ui/`:

1. **Button** (`Button.tsx`)
   - Variants: primary, secondary, outline, ghost, danger
   - Sizes: sm, md, lg
   - Loading states
   - Icon support

2. **Card** (`Card.tsx`)
   - Variants: default, outlined, elevated
   - Padding options
   - Sub-components: CardHeader, CardTitle, CardDescription, CardContent, CardFooter

3. **Input** (`Input.tsx`)
   - Error states
   - Labels and helper text
   - Left/right icons

4. **Spinner** (`Spinner.tsx`)
   - Sizes: sm, md, lg
   - Optional text

5. **Alert** (`Alert.tsx`)
   - Variants: info, success, warning, error
   - Dismissible
   - Icons

6. **Badge** (`Badge.tsx`)
   - Variants: default, primary, success, warning, error, info
   - Sizes: sm, md, lg

7. **PageWrapper** (`PageWrapper.tsx`)
   - Unified loading/error/empty states
   - Consistent UX across pages

### Usage Examples

```typescript
import Button from '../components/ui/Button'
import Card, { CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import Input from '../components/ui/Input'
import Alert from '../components/ui/Alert'
import PageWrapper from '../components/ui/PageWrapper'

// Button
<Button variant="primary" size="md" isLoading={isLoading}>
  Submit
</Button>

// Card
<Card variant="elevated" padding="lg">
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content</CardContent>
</Card>

// Input
<Input
  label="Email"
  error={errors.email}
  helperText="Enter your email address"
  leftIcon={<Mail />}
/>

// Alert
<Alert variant="success" title="Success" onClose={() => setShow(false)}>
  Operation completed successfully
</Alert>

// PageWrapper
<PageWrapper
  isLoading={isLoading}
  error={error}
  isEmpty={data.length === 0}
  emptyTitle="No tasks"
  emptyDescription="Create your first task to get started"
>
  {/* Page content */}
</PageWrapper>
```

## Backend Endpoints

### Core Endpoints

All endpoints are prefixed with `/api`:

- **Tasks**: `/api/tasks`
- **Projects**: `/api/projects`
- **Chat**: `/api/chat`
- **Dashboard**: `/api/dashboard`
- **Documents**: `/api/documents`
- **Settings**: `/api/settings`
- **Integrations**: `/api/integrations`
- **Analytics**: `/api/analytics`
- **Search**: `/api/search`
- **Workspace**: `/api/workspace`
- **Terminal**: `/api/terminal`
- **AI Systems**: `/api/ai`

### Authentication

Authentication is handled via Bearer tokens:

```typescript
// Token is automatically included in requests via apiClient
const token = localStorage.getItem('access_token')
// Authorization: Bearer <token>
```

## Configuration

### Environment Variables

```bash
# Frontend (.env)
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_TARGET=http://localhost:8000

# Backend
OPENAI_API_KEY=your_key
DATABASE_URL=sqlite:///./app.db
```

### Vite Proxy Configuration

The proxy is configured in `vite.config.ts`:

```typescript
proxy: {
  "/api": {
    target: "http://localhost:8000",
    changeOrigin: true,
    secure: false,
  },
  // ... other proxies
}
```

## Error Handling

### API Error Handling

The API client automatically handles errors:

```typescript
try {
  const tasks = await api.tasks.list()
} catch (error) {
  // Error is automatically parsed and formatted
  console.error(error.message) // "Request failed (404)"
}
```

### UI Error States

Use `PageWrapper` for consistent error handling:

```typescript
<PageWrapper
  error={error}
  isLoading={isLoading}
>
  {/* Content */}
</PageWrapper>
```

## Best Practices

### 1. Use the API Service Layer

✅ **Good:**
```typescript
import api from '../services/api'
const tasks = await api.tasks.list()
```

❌ **Bad:**
```typescript
const response = await fetch('/api/tasks')
```

### 2. Use TypeScript Types

✅ **Good:**
```typescript
import type { Task } from '../types'
const tasks: Task[] = await api.tasks.list()
```

### 3. Handle Loading States

✅ **Good:**
```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['tasks'],
  queryFn: api.tasks.list,
})

return (
  <PageWrapper isLoading={isLoading} error={error}>
    {/* Content */}
  </PageWrapper>
)
```

### 4. Use UI Components

✅ **Good:**
```typescript
import Button from '../components/ui/Button'
<Button variant="primary" isLoading={isSubmitting}>
  Submit
</Button>
```

## Migration Guide

### Migrating Existing Pages

1. **Replace direct API calls:**
   ```typescript
   // Before
   const { data } = await apiClient.get(apiPath('tasks'))
   
   // After
   const tasks = await api.tasks.list()
   ```

2. **Add PageWrapper:**
   ```typescript
   // Before
   if (isLoading) return <div>Loading...</div>
   if (error) return <div>Error: {error}</div>
   
   // After
   <PageWrapper isLoading={isLoading} error={error}>
     {/* Content */}
   </PageWrapper>
   ```

3. **Use UI Components:**
   ```typescript
   // Before
   <button className="px-4 py-2 bg-blue-600">Submit</button>
   
   // After
   <Button variant="primary">Submit</Button>
   ```

## Testing

### Testing API Connections

1. Start the backend:
   ```bash
   cd backend_api
   uvicorn main:app --reload --port 8000
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Check API connection:
   - Open browser DevTools
   - Check Network tab for `/api/*` requests
   - Verify responses are successful

### Common Issues

1. **CORS Errors:**
   - Ensure backend CORS middleware is configured
   - Check `allow_origins` includes frontend URL

2. **404 Errors:**
   - Verify backend routes are registered
   - Check API path matches backend route

3. **Authentication Errors:**
   - Verify token is stored in localStorage
   - Check token is included in request headers

## Next Steps

1. **Add More API Endpoints:**
   - Extend `services/api.ts` with new endpoints
   - Add corresponding backend routes

2. **Enhance UI Components:**
   - Add more variants and options
   - Create compound components

3. **Add Real-time Features:**
   - WebSocket connections
   - Server-sent events

4. **Improve Error Handling:**
   - Retry logic
   - Offline support
   - Error boundaries

## Summary

✅ **Completed:**
- Comprehensive API service layer
- Enhanced UI components
- Unified error handling
- Type-safe API calls
- Consistent UX patterns

✅ **Benefits:**
- Centralized API management
- Better error handling
- Improved developer experience
- Consistent UI/UX
- Type safety

The frontend and backend are now fully connected with a robust, scalable architecture that improves both developer experience and user experience.


