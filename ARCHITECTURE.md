# System Architecture - Unified Data & SDLC Automation

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Browser    │  │   Desktop    │  │   CLI        │              │
│  │   (React)    │  │  (PyWebView) │  │   (Python)   │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
└─────────┼──────────────────┼──────────────────┼────────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────────┐
│                    UNIFIED LAUNCHER                                   │
│                  (unified_launcher.py)                                │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Modes: desktop | browser | server | sdlc | all               │ │
│  └────────────────────────────────────────────────────────────────┘ │
└────────────────┬──────────────────────────┬──────────────────────────┘
                 │                          │
     ┌───────────┴───────────┐    ┌─────────▼─────────┐
     │                       │    │                    │
┌────▼──────┐          ┌────▼────▼──┐          ┌─────▼──────┐
│   SDLC    │          │  FastAPI   │          │  Data      │
│  Engine   │          │  Backend   │          │  Monitor   │
└───────────┘          └─────┬──────┘          └────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───┐   ┌──────▼──────┐   ┌──▼────────┐
     │  Routers   │   │   Core      │   │  Services │
     │  Layer     │   │   Logic     │   │  Layer    │
     └────────────┘   └─────────────┘   └───────────┘
```

## SDLC Automation Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│                    SDLC AUTOMATION                            │
│                  (sdlc_automation.py)                         │
└───────────────┬──────────────────────────────────────────────┘
                │
    ┌───────────┴───────────┐
    │                       │
┌───▼─────────────────┐    │    ┌────────────────────────────┐
│  Phase 1-3:         │    │    │  Phase 4-6:                │
│  • Pre-flight       │────┼───▶│  • Testing                 │
│  • Code Gen         │    │    │  • Quality Checks          │
│  • Dependencies     │    │    │  • Frontend Build          │
└─────────────────────┘    │    └────────────────────────────┘
                           │
                           │    ┌────────────────────────────┐
                           └───▶│  Phase 7-10:               │
                                │  • Backend Build           │
                                │  • Documentation           │
                                │  • Packaging               │
                                │  • Deployment Prep         │
                                └────────────────────────────┘
```

## API Router Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
│                    (create_app())                            │
└──────────────┬──────────────────────────────────────────────┘
               │
    ┌──────────┴────────────┐
    │  StripPrefixMiddleware │  (/api prefix handling)
    └──────────┬────────────┘
               │
    ┌──────────▼────────────┐
    │ CorrelationIdMiddleware│  (Request tracking)
    └──────────┬────────────┘
               │
    ┌──────────▼────────────────────────────────────┐
    │              ROUTERS                           │
    ├────────────────────────────────────────────────┤
    │ ✅ runtime_router     (/runtime/diagnostics)   │
    │ ✅ personas_router    (/personas)              │
    │ ✅ search_router      (/search/status)         │
    │ ✅ templates_router   (/templates)             │
    │ ✅ audit_router       (/audit/*)               │
    │ ✅ ai_systems_router  (/ai/*)                  │
    │ ✅ autofix_router     (/autofix/*)             │
    │ ✅ security_router    (/security/*)            │
    │ ✅ network_router     (/network/*)             │
    │ ✅ workflows_router   (/workflows/*)           │
    │ ... and 15+ more routers ...                   │
    └────────────────────────────────────────────────┘
```

## Data Flow

```
┌────────┐      HTTP         ┌──────────┐     SQL      ┌──────────┐
│ Client ├──────Request──────▶│ FastAPI  ├─────Query────▶│ SQLite   │
│ (React)│                    │ Backend  │              │ Database │
└────┬───┘                    └────┬─────┘              └────┬─────┘
     │                             │                          │
     │        JSON Response        │        Data Results      │
     │◀────────────────────────────┤◀─────────────────────────┘
     │                             │
     └─────────Render UI───────────┘
```

## Request Lifecycle

```
1. Client Request
   │
   ├─▶ Browser/Desktop UI sends HTTP request
   │
   └─▶ Example: GET /api/operations/summary

2. Middleware Processing
   │
   ├─▶ StripPrefixMiddleware strips /api prefix
   │   (Request becomes: GET /operations/summary)
   │
   └─▶ CorrelationIdMiddleware adds tracking ID

3. Router Dispatch
   │
   ├─▶ FastAPI routes to correct handler
   │   (operations_summary() function)
   │
   └─▶ Handler processes request

4. Data Access
   │
   ├─▶ Connect to SQLite database
   │
   ├─▶ Execute queries
   │
   └─▶ Fetch results

5. Response Generation
   │
   ├─▶ Format data as JSON
   │
   ├─▶ Add headers (correlation ID, timing)
   │
   └─▶ Return response to client

6. Client Rendering
   │
   └─▶ React UI updates with new data
```

## Component Interactions

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPONENT DIAGRAM                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Frontend  │────────▶│   Backend   │────────▶│  Database   │
│   (React)   │◀────────│  (FastAPI)  │◀────────│  (SQLite)   │
└─────────────┘         └──────┬──────┘         └─────────────┘
                               │
                    ┌──────────┼──────────┐
                    │          │          │
            ┌───────▼───┐  ┌───▼───┐  ┌──▼─────┐
            │  Routers  │  │  AI   │  │ Integ. │
            │  (25+)    │  │ Core  │  │ Gateway│
            └───────────┘  └───────┘  └────────┘
```

## Deployment Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   DEPLOYMENT OPTIONS                      │
└──────────────────────────────────────────────────────────┘

1. Development Mode
   ┌─────────────────────────┐
   │  python unified_launcher│
   │  --mode browser         │
   └─────────────────────────┘
   • Local development
   • Hot reload enabled
   • Debug mode on

2. Production Mode
   ┌─────────────────────────┐
   │  python unified_launcher│
   │  --mode server          │
   │  --host 0.0.0.0         │
   │  --port 80              │
   └─────────────────────────┘
   • Optimized builds
   • Security hardening
   • Performance monitoring

3. Docker Container
   ┌─────────────────────────┐
   │  docker-compose up      │
   └─────────────────────────┘
   • Containerized deployment
   • Easy scaling
   • Isolated environment

4. Cloud Deployment
   ┌─────────────────────────┐
   │  ./deploy-aws.sh        │
   └─────────────────────────┘
   • AWS/Azure/GCP
   • Load balancing
   • Auto-scaling
```

## Security Layer

```
┌──────────────────────────────────────────────────────────┐
│                    SECURITY FEATURES                      │
├──────────────────────────────────────────────────────────┤
│  • CORS middleware (configurable origins)                │
│  • SSL/TLS support (optional certificates)               │
│  • Correlation ID tracking (request tracing)             │
│  • Input validation (Pydantic models)                    │
│  • SQL injection prevention (parameterized queries)      │
│  • XSS protection (Content Security Policy)              │
│  • Rate limiting (configurable per endpoint)             │
│  • Authentication (JWT tokens)                           │
│  • Authorization (role-based access control)             │
└──────────────────────────────────────────────────────────┘
```

## Monitoring & Observability

```
┌──────────────────────────────────────────────────────────┐
│                  OBSERVABILITY STACK                      │
├──────────────────────────────────────────────────────────┤
│  Logging Layer:                                          │
│  ├─ Application logs (logs/backend_server.log)           │
│  ├─ Runtime diagnostics (logs/runtime_diagnostics.log)   │
│  └─ Access logs (Uvicorn default)                        │
│                                                           │
│  Metrics Layer:                                          │
│  ├─ Request duration (x-response-time-ms header)         │
│  ├─ Operation counts (/operations/summary)               │
│  └─ System stats (/system endpoint)                      │
│                                                           │
│  Tracing Layer:                                          │
│  ├─ Correlation IDs (x-correlation-id header)            │
│  ├─ Request chains (parent-child relationships)          │
│  └─ Error tracking (runtime diagnostics)                 │
└──────────────────────────────────────────────────────────┘
```

## Key Design Principles

1. **Single Source of Truth**
   - One unified launcher for all modes
   - Consistent configuration
   - Centralized logging

2. **Fail-Fast Philosophy**
   - Pre-flight checks
   - Early validation
   - Clear error messages

3. **Progressive Enhancement**
   - Core features always work
   - Advanced features optional
   - Graceful degradation

4. **Developer Experience**
   - Simple commands
   - Clear documentation
   - Fast feedback loops

5. **Production Ready**
   - Comprehensive testing
   - Security hardening
   - Performance optimization

## Technology Stack

```
Frontend:
├─ React 18+
├─ TypeScript
├─ TanStack Query (data fetching)
├─ Tailwind CSS (styling)
└─ Vite (build tool)

Backend:
├─ Python 3.11+
├─ FastAPI (web framework)
├─ Uvicorn (ASGI server)
├─ Pydantic (data validation)
└─ SQLite (database)

Development:
├─ pytest (testing)
├─ ESLint (linting)
├─ Prettier (formatting)
└─ Git (version control)

Deployment:
├─ Docker (containerization)
├─ GitHub Actions (CI/CD)
├─ AWS/Azure/GCP (cloud)
└─ Nginx (reverse proxy)
```

---

**Last Updated:** December 19, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
