# URL Route Structure

This document describes the hierarchical URL structure from root to children.

## Route Hierarchy

```
/ (root)
├── /dashboard                    # Dashboard (alias for /)
├── /tasks                        # Tasks management
├── /projects                     # Projects management
├── /chat                         # AI Chat interface
├── /research                     # Research workspace
│
├── /work/                        # Work & Writing section
│   ├── /work/templates           # Task templates
│   ├── /work/writer              # Writer workspace
│   └── /work/tools               # Tools & Terminal
│
├── /ai/                          # AI & Automation section
│   ├── /ai/operations            # AI Operations monitoring
│   ├── /ai/os                    # AI OS orchestrator
│   ├── /ai/advanced              # Advanced AI engine
│   └── /ai/mlops                 # MLOps interface
│
├── /integrations/                # Integrations section
│   ├── /integrations             # Integrations overview
│   └── /integrations/api-connectors  # API Connectors management
│
├── /analytics                    # Analytics dashboard
├── /search                       # Search engine
├── /audit                        # Audit & compliance
├── /monitoring                   # System monitoring
├── /collaboration                # Collaboration features
├── /personalization              # Personalization settings
│
├── /docs/                        # Documentation section
│   ├── /docs                     # Documentation index
│   └── /docs/:page               # Individual documentation pages
│
└── /settings                     # Settings & preferences
```

## Legacy Route Redirects

For backward compatibility, the following legacy routes redirect to the new hierarchical structure:

- `/templates` → `/work/templates`
- `/writer` → `/work/writer`
- `/tools` → `/work/tools`
- `/ai-ops` → `/ai/operations`
- `/ai-os` → `/ai/os`
- `/advanced-ai` → `/ai/advanced`
- `/mlops` → `/ai/mlops`
- `/api-connectors` → `/integrations/api-connectors`

## URL Pattern Rules

1. **Root Level**: Core features accessible directly from root
   - `/`, `/tasks`, `/projects`, `/chat`, `/research`

2. **Section Hierarchy**: Related features grouped under a parent path
   - `/work/*` - All work-related tools
   - `/ai/*` - All AI-related features
   - `/integrations/*` - All integration features
   - `/docs/*` - All documentation

3. **Path Naming**:
   - Use kebab-case for multi-word paths: `/api-connectors`
   - Use singular nouns: `/project` not `/projects` (though `/projects` is used for consistency)
   - Be descriptive: `/ai/operations` not `/ai/ops`

4. **Breadcrumb Navigation**:
   - Automatically generated from URL path
   - Shows: Dashboard / Section / Subsection / Page
   - Example: `Dashboard / AI / Operations`

## Navigation Behavior

- **Dropdown Menus**: Sections with children show dropdown menus on hover/click
- **Active States**: Current page and parent sections are highlighted
- **Breadcrumbs**: Shown for all pages except the root dashboard

