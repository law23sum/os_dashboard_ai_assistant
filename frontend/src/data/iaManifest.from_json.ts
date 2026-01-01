/**
 * Complete IA Manifest - Generated from gui_nav.latest.json
 * Single Source of Truth for all 519 pages
 */

export type ActorScope = 'personal' | 'enterprise' | 'both'

export interface IAFeature {
  id: string
  label: string
  route: string
  componentPath: string
  bestCommit: 'stable' | 'increments' | 'backup'
  actorScope: ActorScope
  order: number
  isNew?: boolean
}

export interface IACategory {
  id: string
  label: string
  homeRoute: string
  homeComponentPath: string
  homeBestCommit: 'stable' | 'increments' | 'backup'
  features: IAFeature[]
  actorScope: ActorScope
  order: number
}

export interface IAPlatform {
  id: string
  label: string
  path: string
  categories: IACategory[]
  actorScope: ActorScope
  order: number
}

export const iaManifest: IAPlatform[] = [
  {
    "id": "mission-control",
    "label": "Mission Control",
    "path": "/dashboard",
    "actorScope": "personal",
    "order": 1,
    "categories": [
      {
        "id": "mission-control-core-flight-deck",
        "label": "Core Flight Deck",
        "homeRoute": "/dashboard/core-flight-deck",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 1,
        "features": [
          {
            "id": "mission-control-core-flight-deck-projects",
            "label": "Projects",
            "route": "/dashboard/flight-deck/projects",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-control-core-flight-deck-tasks",
            "label": "Tasks",
            "route": "/dashboard/flight-deck/tasks",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-control-core-flight-deck-dashboard",
            "label": "Dashboard",
            "route": "/dashboard/flight-deck",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-control-core-flight-deck-project-templates",
            "label": "Project Templates",
            "route": "/dashboard/core-flight-deck/templates",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-control-core-flight-deck-project-members-and-roles",
            "label": "Project Members & Roles",
            "route": "/dashboard/core-flight-deck/members",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-control-core-flight-deck-project-settings",
            "label": "Project Settings",
            "route": "/dashboard/core-flight-deck/settings",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-control-core-flight-deck-task-board-kanban",
            "label": "Task Board (Kanban)",
            "route": "/dashboard/core-flight-deck/board",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-control-core-flight-deck-task-automation-and-rules",
            "label": "Task Automation & Rules",
            "route": "/dashboard/core-flight-deck/automation",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-control-core-flight-deck-task-analytics",
            "label": "Task Analytics",
            "route": "/dashboard/core-flight-deck/analytics",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-control-core-flight-deck-activity-feed",
            "label": "Activity Feed",
            "route": "/dashboard/core-flight-deck/activity",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-control-core-flight-deck-notifications-center",
            "label": "Notifications Center",
            "route": "/dashboard/core-flight-deck/notifications",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-control-core-flight-deck-work-queue-inbox",
            "label": "Work Queue / Inbox",
            "route": "/dashboard/core-flight-deck/inbox",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-control-core-flight-deck-calendar-timeline",
            "label": "Calendar / Timeline",
            "route": "/dashboard/core-flight-deck/timeline",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "mission-control-engagement-and-persona-surfaces",
        "label": "Engagement & Persona Surfaces",
        "homeRoute": "/dashboard/engagement-persona-surfaces",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 2,
        "features": [
          {
            "id": "mission-control-engagement-and-persona-surfaces-chat",
            "label": "Chat",
            "route": "/dashboard/engagement/chat",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-control-engagement-and-persona-surfaces-collaboration",
            "label": "Collaboration",
            "route": "/dashboard/engagement/collaboration",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-control-engagement-and-persona-surfaces-personalization",
            "label": "Personalization",
            "route": "/dashboard/engagement/personalization",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-control-engagement-and-persona-surfaces-search-and-discovery",
            "label": "Search & Discovery",
            "route": "/dashboard/engagement/search",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-control-engagement-and-persona-surfaces-conversation-library",
            "label": "Conversation Library",
            "route": "/dashboard/engagement-persona-surfaces/library",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-control-engagement-and-persona-surfaces-saved-searches-and-alerts",
            "label": "Saved Searches & Alerts",
            "route": "/dashboard/engagement-persona-surfaces/saved",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-control-engagement-and-persona-surfaces-shared-spaces-channels",
            "label": "Shared Spaces / Channels",
            "route": "/dashboard/engagement-persona-surfaces/channels",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-control-engagement-and-persona-surfaces-mentions-and-presence",
            "label": "Mentions & Presence",
            "route": "/dashboard/engagement-persona-surfaces/presence",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-control-engagement-and-persona-surfaces-prompt-macro-library",
            "label": "Prompt / Macro Library",
            "route": "/dashboard/engagement-persona-surfaces/macros",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-control-engagement-and-persona-surfaces-preference-profiles",
            "label": "Preference Profiles",
            "route": "/dashboard/engagement-persona-surfaces/profiles",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      }
    ]
  },
  {
    "id": "workspaces",
    "label": "Workspaces",
    "path": "/workspaces",
    "actorScope": "both",
    "order": 2,
    "categories": [
      {
        "id": "workspaces-dev-and-devops-workspace",
        "label": "Dev & DevOps Workspace",
        "homeRoute": "/workspaces/dev-devops-workspace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 1,
        "features": [
          {
            "id": "workspaces-dev-and-devops-workspace-commit-task-generator",
            "label": "Commit \u2192 Task Generator",
            "route": "/workspaces/dev/commit-tasks",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-dev-and-devops-workspace-code-merge-advisor",
            "label": "Code Merge Advisor",
            "route": "/workspaces/dev/merge-advisor",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-dev-and-devops-workspace-code-review-queue",
            "label": "Code Review Queue",
            "route": "/workspaces/dev/reviews",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-dev-and-devops-workspace-ci-cd-integration",
            "label": "CI/CD Integration",
            "route": "/workspaces/dev/cicd",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-dev-and-devops-workspace-developer-tools",
            "label": "Developer Tools",
            "route": "/workspaces/dev/tools",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-dev-and-devops-workspace-dev-workspace",
            "label": "Dev Workspace",
            "route": "/workspaces/dev",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-dev-and-devops-workspace-repo-and-branch-browser",
            "label": "Repo & Branch Browser",
            "route": "/workspaces/dev/repos",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-dev-and-devops-workspace-build-test-insights",
            "label": "Build/Test Insights",
            "route": "/workspaces/dev/build-insights",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-dev-and-devops-workspace-dependency-updates",
            "label": "Dependency Updates",
            "route": "/workspaces/dev/deps",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-dev-and-devops-workspace-release-notes-generator",
            "label": "Release Notes Generator",
            "route": "/workspaces/dev/release-notes",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-dev-and-devops-workspace-local-environment-health",
            "label": "Local Environment Health",
            "route": "/workspaces/dev/env-health",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "workspaces-research-and-simulation-workspace",
        "label": "Research & Simulation Workspace",
        "homeRoute": "/workspaces/research-simulation-workspace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 2,
        "features": [
          {
            "id": "workspaces-research-and-simulation-workspace-unified-research-lab",
            "label": "Unified Research Lab",
            "route": "/workspaces/research/lab",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-research-and-simulation-workspace-experiment-design",
            "label": "Experiment Design",
            "route": "/workspaces/research/experiments",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-research-and-simulation-workspace-simulation-workbench",
            "label": "Simulation Workbench",
            "route": "/workspaces/research/simulation",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-research-and-simulation-workspace-model-validation",
            "label": "Model Validation",
            "route": "/workspaces/research/validation",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-research-and-simulation-workspace-digital-twin-builder",
            "label": "Digital Twin Builder",
            "route": "/workspaces/research/digital-twins",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-research-and-simulation-workspace-hpc-orchestrator",
            "label": "HPC Orchestrator",
            "route": "/workspaces/research/hpc",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-research-and-simulation-workspace-research-hub",
            "label": "Research Hub",
            "route": "/workspaces/research",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-research-and-simulation-workspace-dataset-registry",
            "label": "Dataset Registry",
            "route": "/workspaces/research/datasets",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-research-and-simulation-workspace-notebook-lab-notes",
            "label": "Notebook / Lab Notes",
            "route": "/workspaces/research/notes",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-research-and-simulation-workspace-experiment-tracking",
            "label": "Experiment Tracking",
            "route": "/workspaces/research/tracking",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-research-and-simulation-workspace-reproducibility-packs",
            "label": "Reproducibility Packs",
            "route": "/workspaces/research/reproducibility",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-research-and-simulation-workspace-results-publishing",
            "label": "Results Publishing",
            "route": "/workspaces/research/publishing",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "workspaces-writer-workspace",
        "label": "Writer Workspace",
        "homeRoute": "/workspaces/writer-workspace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 3,
        "features": [
          {
            "id": "workspaces-writer-workspace-templates",
            "label": "Templates",
            "route": "/workspaces/writer/templates",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-writer-workspace-canon-and-lore",
            "label": "Canon & Lore",
            "route": "/workspaces/writer/canon",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-writer-workspace-narrative-guidance",
            "label": "Narrative Guidance",
            "route": "/workspaces/writer/narrative",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-writer-workspace-story-qa-and-continuity",
            "label": "Story QA & Continuity",
            "route": "/workspaces/writer/qa",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-writer-workspace-export-and-publishing",
            "label": "Export & Publishing",
            "route": "/workspaces/writer/publishing",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-writer-workspace-writer-workstation",
            "label": "Writer Workstation",
            "route": "/workspaces/writer",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-writer-workspace-style-guide-manager",
            "label": "Style Guide Manager",
            "route": "/workspaces/writer/style-guide",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-writer-workspace-versioning-and-change-log",
            "label": "Versioning & Change Log",
            "route": "/workspaces/writer/versioning",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-writer-workspace-citations-and-references",
            "label": "Citations & References",
            "route": "/workspaces/writer/citations",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-writer-workspace-originality-check",
            "label": "Originality Check",
            "route": "/workspaces/writer/originality",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "workspaces-cybersecurity-workspace",
        "label": "Cybersecurity Workspace",
        "homeRoute": "/workspaces/cybersecurity-workspace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 4,
        "features": [
          {
            "id": "workspaces-cybersecurity-workspace-threat-modeling",
            "label": "Threat Modeling",
            "route": "/workspaces/cyber/threat-modeling",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-cybersecurity-workspace-findings-and-triage",
            "label": "Findings & Triage",
            "route": "/workspaces/cyber/findings",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-cybersecurity-workspace-auto-remediation",
            "label": "Auto-Remediation",
            "route": "/workspaces/cyber/auto-remediation",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-cybersecurity-workspace-incident-commander",
            "label": "Incident Commander",
            "route": "/workspaces/cyber/incidents",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-cybersecurity-workspace-security-guardian",
            "label": "Security Guardian",
            "route": "/workspaces/cyber",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-cybersecurity-workspace-policy-as-code-checks",
            "label": "Policy-as-Code Checks",
            "route": "/workspaces/cyber/policy-checks",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-cybersecurity-workspace-vulnerability-scan-integrations",
            "label": "Vulnerability Scan Integrations",
            "route": "/workspaces/cyber/scanners",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-cybersecurity-workspace-threat-intel-feeds",
            "label": "Threat Intel Feeds",
            "route": "/workspaces/cyber/intel",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-cybersecurity-workspace-playbooks-and-runbooks",
            "label": "Playbooks & Runbooks",
            "route": "/workspaces/cyber/playbooks",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "workspaces-business-and-finance-workspace",
        "label": "Business & Finance Workspace",
        "homeRoute": "/workspaces/business-finance-workspace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 5,
        "features": [
          {
            "id": "workspaces-business-and-finance-workspace-budget-planner",
            "label": "Budget Planner",
            "route": "/workspaces/finance/budgets",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-business-and-finance-workspace-strategy-simulation",
            "label": "Strategy Simulation",
            "route": "/workspaces/finance/scenarios",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-business-and-finance-workspace-business-console",
            "label": "Business Console",
            "route": "/workspaces/finance",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-business-and-finance-workspace-kpi-dashboard",
            "label": "KPI Dashboard",
            "route": "/workspaces/finance/kpis",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-business-and-finance-workspace-forecasting-lab",
            "label": "Forecasting Lab",
            "route": "/workspaces/finance/forecasting",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-business-and-finance-workspace-risk-register",
            "label": "Risk Register",
            "route": "/workspaces/finance/risk",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-business-and-finance-workspace-report-generator",
            "label": "Report Generator",
            "route": "/workspaces/finance/reports",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "workspaces-operator-and-sre-workspace",
        "label": "Operator & SRE Workspace",
        "homeRoute": "/workspaces/operator-sre-workspace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 6,
        "features": [
          {
            "id": "workspaces-operator-and-sre-workspace-health-and-drift-monitors",
            "label": "Health & Drift Monitors",
            "route": "/workspaces/sre/health",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-operator-and-sre-workspace-reliability-dashboard",
            "label": "Reliability Dashboard",
            "route": "/workspaces/sre/reliability",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-operator-and-sre-workspace-runbook-library",
            "label": "Runbook Library",
            "route": "/workspaces/sre/runbooks",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-operator-and-sre-workspace-sandbox-management",
            "label": "Sandbox Management",
            "route": "/workspaces/sre/sandbox",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-operator-and-sre-workspace-incident-timeline",
            "label": "Incident Timeline",
            "route": "/workspaces/sre/incidents",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-operator-and-sre-workspace-sre-workspace",
            "label": "SRE Workspace",
            "route": "/workspaces/sre",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-operator-and-sre-workspace-change-management",
            "label": "Change Management",
            "route": "/workspaces/sre/changes",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-operator-and-sre-workspace-capacity-and-cost-insights",
            "label": "Capacity & Cost Insights",
            "route": "/workspaces/sre/capacity-cost",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-operator-and-sre-workspace-maintenance-windows",
            "label": "Maintenance Windows",
            "route": "/workspaces/sre/maintenance",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "workspaces-archive-and-continuity-workspace",
        "label": "Archive & Continuity Workspace",
        "homeRoute": "/workspaces/archive-continuity-workspace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 7,
        "features": [
          {
            "id": "workspaces-archive-and-continuity-workspace-snapshot-manager",
            "label": "Snapshot Manager",
            "route": "/workspaces/archive/snapshots",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-archive-and-continuity-workspace-restore-and-export",
            "label": "Restore & Export",
            "route": "/workspaces/archive/restore",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-archive-and-continuity-workspace-archive-workspace",
            "label": "Archive Workspace",
            "route": "/workspaces/archive",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-archive-and-continuity-workspace-retention-policies",
            "label": "Retention Policies",
            "route": "/workspaces/archive/retention",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-archive-and-continuity-workspace-temporal-reconstruction",
            "label": "Temporal Reconstruction",
            "route": "/workspaces/archive/time-travel",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "workspaces-digital-twin-and-enterprise-twin-workspace",
        "label": "Digital Twin & Enterprise Twin Workspace",
        "homeRoute": "/workspaces/digital-twin-enterprise-twin-workspace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 8,
        "features": [
          {
            "id": "workspaces-digital-twin-and-enterprise-twin-workspace-enterprise-twin",
            "label": "Enterprise Twin",
            "route": "/workspaces/twins/enterprise",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-digital-twin-and-enterprise-twin-workspace-reality-twin-mesh",
            "label": "Reality Twin Mesh",
            "route": "/workspaces/twins/reality-mesh",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-digital-twin-and-enterprise-twin-workspace-scenario-runner",
            "label": "Scenario Runner",
            "route": "/workspaces/twins/scenarios",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-digital-twin-and-enterprise-twin-workspace-twin-templates",
            "label": "Twin Templates",
            "route": "/workspaces/twins/templates",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-digital-twin-and-enterprise-twin-workspace-twin-governance",
            "label": "Twin Governance",
            "route": "/workspaces/twins/governance",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-digital-twin-and-enterprise-twin-workspace-data-feeds-and-sync",
            "label": "Data Feeds & Sync",
            "route": "/workspaces/twins/feeds",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-digital-twin-and-enterprise-twin-workspace-digital-twin-builder",
            "label": "Digital Twin Builder",
            "route": "/workspaces/twins",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "workspaces-master-stack-and-project-management-engine",
        "label": "Master Stack & Project Management Engine",
        "homeRoute": "/pms",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 9,
        "features": [
          {
            "id": "workspaces-master-stack-and-project-management-engine-projects",
            "label": "Projects",
            "route": "/pms/projects",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-master-stack-and-project-management-engine-runs",
            "label": "Runs",
            "route": "/pms/runs",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-master-stack-and-project-management-engine-documents",
            "label": "Documents",
            "route": "/pms/documents",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-master-stack-and-project-management-engine-journal",
            "label": "Journal",
            "route": "/pms/journal",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-master-stack-and-project-management-engine-finance",
            "label": "Finance",
            "route": "/pms/finance",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-master-stack-and-project-management-engine-audit",
            "label": "Audit",
            "route": "/pms/audit",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-master-stack-and-project-management-engine-settings",
            "label": "Settings",
            "route": "/pms/settings",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "workspaces-record-auditor-and-logbook-workspace",
        "label": "Record Auditor & Logbook Workspace",
        "homeRoute": "/workspaces/record-auditor-logbook-workspace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 10,
        "features": [
          {
            "id": "workspaces-record-auditor-and-logbook-workspace-immutable-logbook-viewer",
            "label": "Immutable Logbook Viewer",
            "route": "/workspaces/auditor/logbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-record-auditor-and-logbook-workspace-evidence-trails",
            "label": "Evidence Trails",
            "route": "/workspaces/auditor/evidence",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-record-auditor-and-logbook-workspace-regulator-views",
            "label": "Regulator Views",
            "route": "/workspaces/auditor/regulator",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workspaces-record-auditor-and-logbook-workspace-evidence-requests",
            "label": "Evidence Requests",
            "route": "/workspaces/auditor/requests",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-record-auditor-and-logbook-workspace-audit-reports",
            "label": "Audit Reports",
            "route": "/workspaces/auditor/reports",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "workspaces-record-auditor-and-logbook-workspace-controls-mapping",
            "label": "Controls Mapping",
            "route": "/workspaces/auditor/controls",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      }
    ]
  },
  {
    "id": "ai-fabric",
    "label": "AI Fabric",
    "path": "/ai",
    "actorScope": "personal",
    "order": 3,
    "categories": [
      {
        "id": "ai-fabric-driver-fabric-and-system-execution",
        "label": "Driver Fabric & System Execution",
        "homeRoute": "/ai/driver-fabric-system-execution",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 1,
        "features": [
          {
            "id": "ai-fabric-driver-fabric-and-system-execution-os-drivers",
            "label": "OS Drivers",
            "route": "/ai/drivers/os",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-driver-fabric-and-system-execution-hardware-drivers",
            "label": "Hardware Drivers",
            "route": "/ai/drivers/hardware",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-driver-fabric-and-system-execution-data-drivers",
            "label": "Data Drivers",
            "route": "/ai/drivers/data",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-driver-fabric-and-system-execution-sandbox-and-testbed",
            "label": "Sandbox & Testbed",
            "route": "/ai/drivers/sandbox",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-driver-fabric-and-system-execution-driver-registry",
            "label": "Driver Registry",
            "route": "/ai/drivers",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-driver-fabric-and-system-execution-driver-test-harness",
            "label": "Driver Test Harness",
            "route": "/ai/drivers/testing",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-driver-fabric-and-system-execution-driver-health-and-telemetry",
            "label": "Driver Health & Telemetry",
            "route": "/ai/drivers/health",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-driver-fabric-and-system-execution-driver-permissions-and-sandboxing",
            "label": "Driver Permissions & Sandboxing",
            "route": "/ai/drivers/permissions",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-driver-fabric-and-system-execution-driver-versioning-and-deprecation",
            "label": "Driver Versioning & Deprecation",
            "route": "/ai/drivers/versioning",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-driver-fabric-and-system-execution-package-and-env-drivers",
            "label": "Package & Env Drivers",
            "route": "/ai/drivers/package",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-driver-fabric-and-system-execution-software-and-saas-drivers",
            "label": "Software & SaaS Drivers",
            "route": "/ai/drivers/software",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-driver-fabric-and-system-execution-research-and-simulation-drivers",
            "label": "Research & Simulation Drivers",
            "route": "/ai/drivers/research",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-driver-fabric-and-system-execution-ai-os-control",
            "label": "AI OS Control",
            "route": "/ai/os",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-driver-fabric-and-system-execution-ai-operations",
            "label": "AI Operations",
            "route": "/ai/operations",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "ai-fabric-capsules-and-workflow-automation",
        "label": "Capsules & Workflow Automation",
        "homeRoute": "/ai/capsules-workflow-automation",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 2,
        "features": [
          {
            "id": "ai-fabric-capsules-and-workflow-automation-project-ledger",
            "label": "Project Ledger",
            "route": "/ai/capsules/ledger",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-capsules-and-workflow-automation-lineage-and-replay",
            "label": "Lineage & Replay",
            "route": "/ai/capsules/lineage",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-capsules-and-workflow-automation-operator-studio",
            "label": "Operator Studio",
            "route": "/ai/capsules/operator-studio",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-capsules-and-workflow-automation-capsule-templates",
            "label": "Capsule Templates",
            "route": "/ai/capsules/templates",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-capsules-and-workflow-automation-my-stack-capsules",
            "label": "My Stack Capsules",
            "route": "/ai/capsules/my-stack",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-capsules-and-workflow-automation-capsule-builder",
            "label": "Capsule Builder",
            "route": "/ai/capsules/builder",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-capsules-and-workflow-automation-capsule-runtime-settings",
            "label": "Capsule Runtime Settings",
            "route": "/ai/capsules/runtime",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-capsules-and-workflow-automation-secrets-and-inputs",
            "label": "Secrets & Inputs",
            "route": "/ai/capsules/secrets",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-capsules-and-workflow-automation-capsule-marketplace",
            "label": "Capsule Marketplace",
            "route": "/ai/capsules",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-capsules-and-workflow-automation-approval-and-publishing",
            "label": "Approval & Publishing",
            "route": "/ai/capsules/publishing",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-capsules-and-workflow-automation-workflow-orchestrator",
            "label": "Workflow Orchestrator",
            "route": "/ai/workflows",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-capsules-and-workflow-automation-scheduling-and-triggers",
            "label": "Scheduling & Triggers",
            "route": "/ai/workflows/triggers",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-capsules-and-workflow-automation-workflow-observability",
            "label": "Workflow Observability",
            "route": "/ai/workflows/observability",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-capsules-and-workflow-automation-auto-fix-console",
            "label": "Auto-Fix Console",
            "route": "/ai/autofix",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "ai-fabric-intent-processing",
        "label": "Intent Processing",
        "homeRoute": "/ai/intent-processing",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 3,
        "features": [
          {
            "id": "ai-fabric-intent-processing-intent-processor",
            "label": "Intent Processor",
            "route": "/ai/intents",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-intent-processing-intent-taxonomy-and-routing-rules",
            "label": "Intent Taxonomy & Routing Rules",
            "route": "/ai/intents/taxonomy",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-intent-processing-intent-logs-and-replay",
            "label": "Intent Logs & Replay",
            "route": "/ai/intents/logs",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-intent-processing-systems-map",
            "label": "Systems Map",
            "route": "/ai/systems",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-intent-processing-system-dependency-graph",
            "label": "System Dependency Graph",
            "route": "/ai/systems/graph",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-intent-processing-capability-registry",
            "label": "Capability Registry",
            "route": "/ai/capabilities",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "ai-fabric-edge-and-vision",
        "label": "Edge & Vision",
        "homeRoute": "/ai/edge-vision",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 4,
        "features": [
          {
            "id": "ai-fabric-edge-and-vision-edge-computing",
            "label": "Edge Computing",
            "route": "/ai/edge",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-edge-and-vision-device-registry",
            "label": "Device Registry",
            "route": "/ai/edge/devices",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-edge-and-vision-model-packaging-and-deployment",
            "label": "Model Packaging & Deployment",
            "route": "/ai/edge/deploy",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-edge-and-vision-computer-vision",
            "label": "Computer Vision",
            "route": "/ai/vision",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-edge-and-vision-camera-stream-integrations",
            "label": "Camera/Stream Integrations",
            "route": "/ai/vision/streams",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-edge-and-vision-vision-pipelines",
            "label": "Vision Pipelines",
            "route": "/ai/vision/pipelines",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-edge-and-vision-annotation-and-labeling",
            "label": "Annotation & Labeling",
            "route": "/ai/vision/labeling",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "ai-fabric-cognitive-agents-and-reasoning",
        "label": "Cognitive Agents & Reasoning",
        "homeRoute": "/ai/cognitive-agents-reasoning",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 5,
        "features": [
          {
            "id": "ai-fabric-cognitive-agents-and-reasoning-ai-copilot",
            "label": "AI Copilot",
            "route": "/ai/copilot",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-cognitive-agents-and-reasoning-personas-and-agents",
            "label": "Personas & Agents",
            "route": "/ai/personas",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-cognitive-agents-and-reasoning-prompt-instruction-library",
            "label": "Prompt/Instruction Library",
            "route": "/ai/prompts",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-cognitive-agents-and-reasoning-project-intelligence",
            "label": "Project Intelligence",
            "route": "/ai/project-intelligence",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-cognitive-agents-and-reasoning-evaluation-and-benchmarks",
            "label": "Evaluation & Benchmarks",
            "route": "/ai/evals",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-cognitive-agents-and-reasoning-model-router-policy",
            "label": "Model Router / Policy",
            "route": "/ai/routing",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-cognitive-agents-and-reasoning-advanced-ai-engine",
            "label": "Advanced AI Engine",
            "route": "/ai/advanced",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-cognitive-agents-and-reasoning-daemon-framework",
            "label": "Daemon Framework",
            "route": "/ai/daemons",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-cognitive-agents-and-reasoning-theoretical-reasoning-framework",
            "label": "Theoretical Reasoning Framework",
            "route": "/ai/trf",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-cognitive-agents-and-reasoning-safety-and-alignment-overview",
            "label": "Safety & Alignment Overview",
            "route": "/ai/safety",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-cognitive-agents-and-reasoning-agent-registry-and-lifecycle",
            "label": "Agent Registry & Lifecycle",
            "route": "/ai/agents/registry",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "ai-fabric-mlops-and-neural-architecture",
        "label": "MLOps & Neural Architecture",
        "homeRoute": "/ai/mlops-neural-architecture",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 6,
        "features": [
          {
            "id": "ai-fabric-mlops-and-neural-architecture-mlops",
            "label": "MLOps",
            "route": "/ai/mlops",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-mlops-and-neural-architecture-model-registry",
            "label": "Model Registry",
            "route": "/ai/mlops/models",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-mlops-and-neural-architecture-dataset-and-feature-store",
            "label": "Dataset & Feature Store",
            "route": "/ai/mlops/data",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-mlops-and-neural-architecture-training-pipelines",
            "label": "Training Pipelines",
            "route": "/ai/mlops/pipelines",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-mlops-and-neural-architecture-deployment-and-serving",
            "label": "Deployment & Serving",
            "route": "/ai/mlops/serving",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-mlops-and-neural-architecture-drift-monitoring",
            "label": "Drift Monitoring",
            "route": "/ai/mlops/drift",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-mlops-and-neural-architecture-governance-gates",
            "label": "Governance Gates",
            "route": "/ai/mlops/approvals",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "ai-fabric-mlops-and-neural-architecture-nas-console",
            "label": "NAS Console",
            "route": "/ai/nas",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-mlops-and-neural-architecture-experiment-console",
            "label": "Experiment Console",
            "route": "/ai/nas/experiments",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "ai-fabric-mlops-and-neural-architecture-nas-simulator",
            "label": "NAS Simulator",
            "route": "/ai/nas/simulator",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          }
        ]
      }
    ]
  },
  {
    "id": "data-knowledge",
    "label": "Data & Knowledge",
    "path": "/data",
    "actorScope": "personal",
    "order": 4,
    "categories": [
      {
        "id": "data-knowledge-observability-stores",
        "label": "Observability Stores",
        "homeRoute": "/data/observability-stores",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 1,
        "features": [
          {
            "id": "data-knowledge-observability-stores-observability-stores-overview",
            "label": "Observability Stores Overview",
            "route": "/data/observability",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "data-knowledge-observability-stores-retention-and-tiering",
            "label": "Retention & Tiering",
            "route": "/data/observability/tiering",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "data-knowledge-observability-stores-export-and-integrations",
            "label": "Export & Integrations",
            "route": "/data/observability/export",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "data-knowledge-observability-stores-metrics-store",
            "label": "Metrics Store",
            "route": "/data/metrics",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "data-knowledge-observability-stores-logs-store",
            "label": "Logs Store",
            "route": "/data/logs",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "data-knowledge-observability-stores-traces-store",
            "label": "Traces Store",
            "route": "/data/traces",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "data-knowledge-archive-and-backup",
        "label": "Archive & Backup",
        "homeRoute": "/data/archive",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 2,
        "features": []
      },
      {
        "id": "data-knowledge-multi-region-and-replication",
        "label": "Multi-Region & Replication",
        "homeRoute": "/data/replication",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 3,
        "features": []
      },
      {
        "id": "data-knowledge-core-data-stores",
        "label": "Core Data Stores",
        "homeRoute": "/data/core-data-stores",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 4,
        "features": [
          {
            "id": "data-knowledge-core-data-stores-data-overview",
            "label": "Data Overview",
            "route": "/data/core-data-stores/data",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "data-knowledge-core-data-stores-cir-store",
            "label": "CIR Store",
            "route": "/data/cir",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "data-knowledge-core-data-stores-capsule-store",
            "label": "Capsule Store",
            "route": "/data/capsules",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "data-knowledge-core-data-stores-project-ledger",
            "label": "Project Ledger",
            "route": "/data/ledger",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "data-knowledge-core-data-stores-binary-artifacts",
            "label": "Binary Artifacts",
            "route": "/data/artifacts",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "data-knowledge-core-data-stores-schema-and-ontology",
            "label": "Schema & Ontology",
            "route": "/data/schema",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "data-knowledge-core-data-stores-ingestion-pipelines",
            "label": "Ingestion Pipelines",
            "route": "/data/ingestion",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "data-knowledge-core-data-stores-data-lineage",
            "label": "Data Lineage",
            "route": "/data/lineage",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "data-knowledge-core-data-stores-data-quality-checks",
            "label": "Data Quality Checks",
            "route": "/data/quality",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "data-knowledge-data-protection",
        "label": "Data Protection",
        "homeRoute": "/data/data-protection",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 5,
        "features": [
          {
            "id": "data-knowledge-data-protection-encryption-and-keys",
            "label": "Encryption & Keys",
            "route": "/data/encryption",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "data-knowledge-data-protection-key-rotation-and-kms-integrations",
            "label": "Key Rotation & KMS Integrations",
            "route": "/data/encryption/rotation",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "data-knowledge-data-protection-integrity-protections",
            "label": "Integrity Protections",
            "route": "/data/integrity",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "data-knowledge-replication-and-dr",
        "label": "Replication & DR",
        "homeRoute": "/data/replication-dr",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 6,
        "features": [
          {
            "id": "data-knowledge-replication-and-dr-consistency-models",
            "label": "Consistency Models",
            "route": "/data/consistency",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "data-knowledge-replication-and-dr-failover-controls",
            "label": "Failover Controls",
            "route": "/data/dr/failover",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "data-knowledge-replication-and-dr-dr-drill-planner",
            "label": "DR Drill Planner",
            "route": "/data/dr/drills",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "data-knowledge-indices-and-search",
        "label": "Indices & Search",
        "homeRoute": "/data/indices-search",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 7,
        "features": [
          {
            "id": "data-knowledge-indices-and-search-indices-overview",
            "label": "Indices Overview",
            "route": "/data/indices",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "data-knowledge-indices-and-search-index-management",
            "label": "Index Management",
            "route": "/data/indices/manage",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "data-knowledge-indices-and-search-full-text-search",
            "label": "Full-Text Search",
            "route": "/data/indices/fulltext",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "data-knowledge-indices-and-search-semantic-vector-search",
            "label": "Semantic/Vector Search",
            "route": "/data/indices/semantic",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "data-knowledge-indices-and-search-embeddings-management",
            "label": "Embeddings Management",
            "route": "/data/indices/embeddings",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "data-knowledge-indices-and-search-graph-index",
            "label": "Graph Index",
            "route": "/data/indices/graph",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "data-knowledge-indices-and-search-relevance-tuning",
            "label": "Relevance Tuning",
            "route": "/data/indices/tuning",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "data-knowledge-indices-and-search-query-console",
            "label": "Query Console",
            "route": "/data/query",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "data-knowledge-archive-and-retention",
        "label": "Archive & Retention",
        "homeRoute": "/data/archive-retention",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 8,
        "features": [
          {
            "id": "data-knowledge-archive-and-retention-backup-and-retention",
            "label": "Backup & Retention",
            "route": "/data/backup",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "data-knowledge-archive-and-retention-retention-policy-builder",
            "label": "Retention Policy Builder",
            "route": "/data/retention/policies",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "data-knowledge-archive-and-retention-legal-hold",
            "label": "Legal Hold",
            "route": "/data/legal-hold",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "data-knowledge-archive-and-retention-restore-testing",
            "label": "Restore Testing",
            "route": "/data/restore-testing",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      }
    ]
  },
  {
    "id": "drivers-integrations",
    "label": "Drivers & Integrations",
    "path": "/drivers",
    "actorScope": "personal",
    "order": 5,
    "categories": [
      {
        "id": "drivers-integrations-driver-registry",
        "label": "Driver Registry",
        "homeRoute": "/drivers/registry",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 1,
        "features": []
      },
      {
        "id": "drivers-integrations-software-and-saas-drivers",
        "label": "Software & SaaS Drivers",
        "homeRoute": "/drivers/integrations/productivity",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 2,
        "features": [
          {
            "id": "drivers-integrations-software-and-saas-drivers-code-hosts-and-ci-cd",
            "label": "Code Hosts & CI/CD",
            "route": "/drivers/integrations/code",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "drivers-integrations-software-and-saas-drivers-finance-and-banking",
            "label": "Finance & Banking",
            "route": "/drivers/integrations/finance",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "drivers-integrations-software-and-saas-drivers-research-data-sources",
            "label": "Research Data Sources",
            "route": "/drivers/integrations/research",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "drivers-integrations-software-and-saas-drivers-legacy-and-mainframe",
            "label": "Legacy & Mainframe",
            "route": "/drivers/integrations/legacy",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "drivers-integrations-software-and-saas-drivers-cloud-providers",
            "label": "Cloud Providers",
            "route": "/drivers/integrations/cloud",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "drivers-integrations-marketplace",
        "label": "Marketplace",
        "homeRoute": "/drivers/marketplace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 3,
        "features": [
          {
            "id": "drivers-integrations-marketplace-reviews-and-ratings",
            "label": "Reviews & Ratings",
            "route": "/drivers/marketplace/reviews",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "drivers-integrations-marketplace-security-review-pipeline",
            "label": "Security Review Pipeline",
            "route": "/drivers/marketplace/security-review",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "drivers-integrations-driver-registry-and-management",
        "label": "Driver Registry & Management",
        "homeRoute": "/drivers/driver-registry-management",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 4,
        "features": [
          {
            "id": "drivers-integrations-driver-registry-and-management-overview",
            "label": "Overview",
            "route": "/drivers/driver-registry-management/drivers",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "drivers-integrations-driver-registry-and-management-driver-sdk",
            "label": "Driver SDK",
            "route": "/drivers/sdk",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "drivers-integrations-driver-registry-and-management-driver-testing-and-validation",
            "label": "Driver Testing & Validation",
            "route": "/drivers/testing",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "drivers-integrations-driver-registry-and-management-runtime-permissions",
            "label": "Runtime Permissions",
            "route": "/drivers/permissions",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "drivers-integrations-driver-registry-and-management-versioning-and-deprecation",
            "label": "Versioning & Deprecation",
            "route": "/drivers/versioning",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "drivers-integrations-driver-registry-and-management-driver-analytics",
            "label": "Driver Analytics",
            "route": "/drivers/analytics",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "drivers-integrations-driver-registry-and-management-publishing-flow",
            "label": "Publishing Flow",
            "route": "/drivers/publishing",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "drivers-integrations-driver-packs-and-marketplace",
        "label": "Driver Packs & Marketplace",
        "homeRoute": "/drivers/driver-packs-marketplace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 5,
        "features": [
          {
            "id": "drivers-integrations-driver-packs-and-marketplace-driver-packs",
            "label": "Driver Packs",
            "route": "/drivers/packs",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "drivers-integrations-driver-packs-and-marketplace-pack-builder",
            "label": "Pack Builder",
            "route": "/drivers/packs/builder",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "drivers-integrations-driver-packs-and-marketplace-vertical-editions",
            "label": "Vertical Editions",
            "route": "/drivers/vertical-editions",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "drivers-integrations-driver-packs-and-marketplace-enterprise-app-store",
            "label": "Enterprise App Store",
            "route": "/drivers/enterprise-store",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "drivers-integrations-driver-packs-and-marketplace-licensing-and-entitlements",
            "label": "Licensing & Entitlements",
            "route": "/drivers/licensing",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "drivers-integrations-risk-and-governance",
        "label": "Risk & Governance",
        "homeRoute": "/drivers/risk-governance",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 6,
        "features": [
          {
            "id": "drivers-integrations-risk-and-governance-third-party-risk",
            "label": "Third-Party Risk",
            "route": "/drivers/risk",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "drivers-integrations-risk-and-governance-vendor-inventory",
            "label": "Vendor Inventory",
            "route": "/drivers/risk/vendors",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "drivers-integrations-risk-and-governance-risk-assessments",
            "label": "Risk Assessments",
            "route": "/drivers/risk/assessments",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "drivers-integrations-risk-and-governance-remediation-tracker",
            "label": "Remediation Tracker",
            "route": "/drivers/risk/remediation",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "drivers-integrations-risk-and-governance-exceptions-and-approvals",
            "label": "Exceptions & Approvals",
            "route": "/drivers/risk/exceptions",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "drivers-integrations-connectors-and-integrations",
        "label": "Connectors & Integrations",
        "homeRoute": "/drivers/connectors-integrations",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 7,
        "features": [
          {
            "id": "drivers-integrations-connectors-and-integrations-connectors-overview",
            "label": "Connectors Overview",
            "route": "/drivers/connectors-integrations/connectors",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "drivers-integrations-connectors-and-integrations-credential-vault",
            "label": "Credential Vault",
            "route": "/drivers/connectors-integrations/credentials",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "drivers-integrations-connectors-and-integrations-api-connectors",
            "label": "API Connectors",
            "route": "/drivers/connectors-integrations/api-connectors",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "drivers-integrations-connectors-and-integrations-mcp-gateway",
            "label": "MCP Gateway",
            "route": "/drivers/connectors-integrations/mcp-gateway",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "drivers-integrations-connectors-and-integrations-office-realtime",
            "label": "Office Realtime",
            "route": "/drivers/connectors-integrations/office",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "drivers-integrations-connectors-and-integrations-webhooks-and-events",
            "label": "Webhooks & Events",
            "route": "/drivers/connectors-integrations/webhooks",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "drivers-integrations-connectors-and-integrations-data-mapping-and-transformations",
            "label": "Data Mapping & Transformations",
            "route": "/drivers/connectors-integrations/mappings",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "drivers-integrations-connectors-and-integrations-connector-health",
            "label": "Connector Health",
            "route": "/drivers/connectors-integrations/health",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "drivers-integrations-connectors-and-integrations-rate-limits-and-quotas",
            "label": "Rate Limits & Quotas",
            "route": "/drivers/connectors-integrations/rate-limits",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      }
    ]
  },
  {
    "id": "docs-spec",
    "label": "Docs & Spec",
    "path": "/docs",
    "actorScope": "personal",
    "order": 6,
    "categories": [
      {
        "id": "docs-spec-getting-started",
        "label": "Getting Started",
        "homeRoute": "/docs/getting-started",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 1,
        "features": []
      },
      {
        "id": "docs-spec-api-reference",
        "label": "API Reference",
        "homeRoute": "/docs/api",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 2,
        "features": [
          {
            "id": "docs-spec-api-reference-sdks",
            "label": "SDKs",
            "route": "/docs/api/sdks",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "docs-spec-api-reference-auth-and-rate-limits",
            "label": "Auth & Rate Limits",
            "route": "/docs/api/auth",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "docs-spec-api-reference-webhooks",
            "label": "Webhooks",
            "route": "/docs/api/webhooks",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "docs-spec-api-reference-api-reference",
            "label": "API Reference",
            "route": "/docs/api-reference",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "docs-spec-reference-artifacts",
        "label": "Reference Artifacts",
        "homeRoute": "/docs/reference-artifacts",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 3,
        "features": [
          {
            "id": "docs-spec-reference-artifacts-capsule-manifests",
            "label": "Capsule Manifests",
            "route": "/docs/reference/capsules",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "docs-spec-reference-artifacts-driver-manifests",
            "label": "Driver Manifests",
            "route": "/docs/reference/drivers",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "docs-spec-reference-artifacts-policy-examples",
            "label": "Policy Examples",
            "route": "/docs/reference/policies",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "docs-spec-reference-artifacts-evidence-pack-templates",
            "label": "Evidence Pack Templates",
            "route": "/docs/reference/evidence",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "docs-spec-reference-artifacts-data-schemas",
            "label": "Data Schemas",
            "route": "/docs/reference/data",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "docs-spec-reference-artifacts-ui-component-library",
            "label": "UI Component Library",
            "route": "/docs/reference/ui",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "docs-spec-documentation-hub",
        "label": "Documentation Hub",
        "homeRoute": "/docs/documentation-hub",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 4,
        "features": [
          {
            "id": "docs-spec-documentation-hub-docs-hub",
            "label": "Docs Hub",
            "route": "/docs/documentation-hub/docs",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "docs-spec-documentation-hub-tutorials",
            "label": "Tutorials",
            "route": "/docs/tutorials",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "docs-spec-documentation-hub-glossary",
            "label": "Glossary",
            "route": "/docs/glossary",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "docs-spec-documentation-hub-technical-spec-sheet",
            "label": "Technical Spec Sheet",
            "route": "/docs/spec-sheet",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "docs-spec-documentation-hub-ssot-technical-docs",
            "label": "SSOT Technical Docs",
            "route": "/docs/documentation-hub/ssot-technical-docs",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "docs-spec-documentation-hub-release-notes",
            "label": "Release Notes",
            "route": "/docs/release-notes",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "docs-spec-migration-and-integration",
        "label": "Migration & Integration",
        "homeRoute": "/docs/migration-integration",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "personal",
        "order": 5,
        "features": [
          {
            "id": "docs-spec-migration-and-integration-migration-continued",
            "label": "Migration Continued",
            "route": "/docs/migration_continued.md",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "docs-spec-migration-and-integration-migration-guides",
            "label": "Migration Guides",
            "route": "/docs/migration",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "docs-spec-migration-and-integration-integration-guides",
            "label": "Integration Guides",
            "route": "/docs/integrations",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "docs-spec-migration-and-integration-deployment-guides",
            "label": "Deployment Guides",
            "route": "/docs/deployment",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          }
        ]
      }
    ]
  },
  {
    "id": "settings-admin",
    "label": "Settings & Admin",
    "path": "/settings",
    "actorScope": "both",
    "order": 7,
    "categories": [
      {
        "id": "settings-admin-user-and-tenant-settings",
        "label": "User & Tenant Settings",
        "homeRoute": "/settings/enterprise/user-tenant",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "settings-admin-user-and-tenant-settings-settings",
            "label": "Settings",
            "route": "/settings/user-tenant-settings/settings",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": false
          },
          {
            "id": "settings-admin-user-and-tenant-settings-user-profile",
            "label": "User Profile",
            "route": "/settings/profile",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "settings-admin-user-and-tenant-settings-preferences",
            "label": "Preferences",
            "route": "/settings/preferences",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "settings-admin-user-and-tenant-settings-notifications",
            "label": "Notifications",
            "route": "/settings/notifications",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "settings-admin-user-and-tenant-settings-integrations-credentials",
            "label": "Integrations Credentials",
            "route": "/settings/credentials",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "settings-admin-user-and-tenant-settings-api-keys",
            "label": "API Keys",
            "route": "/settings/api-keys",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "personal",
            "order": 1,
            "isNew": true
          },
          {
            "id": "settings-admin-user-and-tenant-settings-team-and-members",
            "label": "Team & Members",
            "route": "/settings/team",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7,
            "isNew": true
          },
          {
            "id": "settings-admin-user-and-tenant-settings-tenancy-and-org-settings",
            "label": "Tenancy & Org Settings",
            "route": "/settings/tenant",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7,
            "isNew": true
          },
          {
            "id": "settings-admin-user-and-tenant-settings-audit-settings",
            "label": "Audit Settings",
            "route": "/settings/audit",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7,
            "isNew": true
          }
        ]
      }
    ]
  },
  {
    "id": "mission-architecture",
    "label": "Mission & Architecture",
    "path": "/mission",
    "actorScope": "enterprise",
    "order": 8,
    "categories": [
      {
        "id": "mission-architecture-mission-and-identity",
        "label": "Mission & Identity",
        "homeRoute": "/mission/mission-identity",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 1,
        "features": [
          {
            "id": "mission-architecture-mission-and-identity-identity-and-roles",
            "label": "Identity & Roles",
            "route": "/mission/identity",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-architecture-mission-and-identity-mission-and-scope",
            "label": "Mission & Scope",
            "route": "/mission/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-architecture-mission-and-identity-use-cases-map",
            "label": "Use Cases Map",
            "route": "/mission/use-cases",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-architecture-mission-and-identity-system-boundaries-and-non-goals",
            "label": "System Boundaries & Non-Goals",
            "route": "/mission/non-goals",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-architecture-mission-and-identity-terminology-glossary",
            "label": "Terminology Glossary",
            "route": "/mission/glossary",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-architecture-mission-and-identity-deployment-modes",
            "label": "Deployment Modes",
            "route": "/mission/modes",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-architecture-mission-and-identity-reference-architectures-by-edition",
            "label": "Reference Architectures by Edition",
            "route": "/mission/reference-architectures",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-architecture-mission-and-identity-ai-driver-stack",
            "label": "AI + Driver Stack",
            "route": "/mission/ai-stack",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-architecture-mission-and-identity-model-provider-layer",
            "label": "Model Provider Layer",
            "route": "/mission/models",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-architecture-mission-and-identity-daemon-families",
            "label": "Daemon Families",
            "route": "/mission/daemons",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "mission-architecture-architecture-and-principles",
        "label": "Architecture & Principles",
        "homeRoute": "/mission/architecture-principles",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 2,
        "features": [
          {
            "id": "mission-architecture-architecture-and-principles-architecture-overview",
            "label": "Architecture Overview",
            "route": "/mission/architecture",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-architecture-architecture-and-principles-architectural-principles",
            "label": "Architectural Principles",
            "route": "/mission/principles",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-architecture-architecture-and-principles-major-components",
            "label": "Major Components",
            "route": "/mission/components",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-architecture-architecture-and-principles-driver-aware-orchestrator",
            "label": "Driver-Aware Orchestrator",
            "route": "/mission/orchestrator",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-architecture-architecture-and-principles-component-mapping",
            "label": "Component Mapping",
            "route": "/mission/mapping",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-architecture-architecture-and-principles-data-model-and-contracts",
            "label": "Data Model & Contracts",
            "route": "/mission/contracts",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-architecture-architecture-and-principles-extensibility-points",
            "label": "Extensibility Points",
            "route": "/mission/extensibility",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-architecture-architecture-and-principles-threat-model-summary",
            "label": "Threat Model Summary",
            "route": "/mission/threat-model",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-architecture-architecture-and-principles-performance-targets",
            "label": "Performance Targets",
            "route": "/mission/performance-targets",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "mission-architecture-planes-architecture",
        "label": "Planes Architecture",
        "homeRoute": "/mission/planes-architecture",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 3,
        "features": [
          {
            "id": "mission-architecture-planes-architecture-data-plane",
            "label": "Data Plane",
            "route": "/mission/planes/data",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-architecture-planes-architecture-control-plane",
            "label": "Control Plane",
            "route": "/mission/planes/control",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-architecture-planes-architecture-governance-plane",
            "label": "Governance Plane",
            "route": "/mission/planes/governance",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-architecture-planes-architecture-cross-plane-flows",
            "label": "Cross-Plane Flows",
            "route": "/mission/planes/cross-plane",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "mission-architecture-planes-architecture-failure-domains-by-plane",
            "label": "Failure Domains by Plane",
            "route": "/mission/planes/failure-domains",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-architecture-planes-architecture-planes-overview",
            "label": "Planes Overview",
            "route": "/mission/planes",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "mission-architecture-planes-architecture-plane-apis-and-event-contracts",
            "label": "Plane APIs & Event Contracts",
            "route": "/mission/planes/contracts",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      }
    ]
  },
  {
    "id": "governance-security",
    "label": "Governance & Security",
    "path": "/governance",
    "actorScope": "enterprise",
    "order": 9,
    "categories": [
      {
        "id": "governance-security-policy-and-governance-engine",
        "label": "Policy & Governance Engine",
        "homeRoute": "/governance/policy-governance-engine",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 1,
        "features": [
          {
            "id": "governance-security-policy-and-governance-engine-policy-dsl",
            "label": "Policy DSL",
            "route": "/governance/policy/dsl",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-policy-and-governance-engine-policy-simulator",
            "label": "Policy Simulator",
            "route": "/governance/policy/simulator",
            "componentPath": "frontend/src/pages/governance/policy/PolicySimulator.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-policy-and-governance-engine-policy-engine",
            "label": "Policy Engine",
            "route": "/governance/policy",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-policy-and-governance-engine-policy-library-and-templates",
            "label": "Policy Library & Templates",
            "route": "/governance/policy/library",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "governance-security-policy-and-governance-engine-safety-harnesses",
            "label": "Safety Harnesses",
            "route": "/governance/policy/safety",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-policy-and-governance-engine-policy-versioning-and-approvals",
            "label": "Policy Versioning & Approvals",
            "route": "/governance/policy/versioning",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "governance-security-policy-and-governance-engine-enforcement-points-map",
            "label": "Enforcement Points Map",
            "route": "/governance/policy/enforcement",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "governance-security-policy-and-governance-engine-exceptions-and-waivers",
            "label": "Exceptions & Waivers",
            "route": "/governance/policy/exceptions",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "governance-security-identity-and-access",
        "label": "Identity & Access",
        "homeRoute": "/governance/identity-access",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 2,
        "features": [
          {
            "id": "governance-security-identity-and-access-sso-saml-oidc-settings",
            "label": "SSO/SAML/OIDC Settings",
            "route": "/governance/identity/sso",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "governance-security-identity-and-access-identity-and-roles",
            "label": "Identity & Roles",
            "route": "/governance/identity",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-identity-and-access-authentication",
            "label": "Authentication",
            "route": "/governance/identity/auth",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-identity-and-access-scim-provisioning",
            "label": "SCIM Provisioning",
            "route": "/governance/identity/scim",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "governance-security-identity-and-access-rbac-abac",
            "label": "RBAC/ABAC",
            "route": "/governance/identity/rbac",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-identity-and-access-api-keys-and-tokens",
            "label": "API Keys & Tokens",
            "route": "/governance/identity/api-keys",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "governance-security-identity-and-access-session-management",
            "label": "Session Management",
            "route": "/governance/identity/sessions",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "governance-security-identity-and-access-access-reviews",
            "label": "Access Reviews",
            "route": "/governance/identity/reviews",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "governance-security-compliance-packs",
        "label": "Compliance Packs",
        "homeRoute": "/governance/compliance",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 3,
        "features": [
          {
            "id": "governance-security-compliance-packs-control-framework-mapping",
            "label": "Control Framework Mapping",
            "route": "/governance/compliance/controls",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "governance-security-compliance-packs-audit-readiness-dashboard",
            "label": "Audit Readiness Dashboard",
            "route": "/governance/compliance/readiness",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "governance-security-regulator-fabric",
        "label": "Regulator Fabric",
        "homeRoute": "/governance/regulator",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 4,
        "features": [
          {
            "id": "governance-security-regulator-fabric-regulator-tenancy",
            "label": "Regulator Tenancy",
            "route": "/governance/regulator/tenancy",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-regulator-fabric-evidence-access",
            "label": "Evidence Access",
            "route": "/governance/regulator/evidence",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-regulator-fabric-evidence-request-workflow",
            "label": "Evidence Request Workflow",
            "route": "/governance/regulator/requests",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "governance-security-security-monitoring",
        "label": "Security Monitoring",
        "homeRoute": "/governance/security/monitoring",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 5,
        "features": [
          {
            "id": "governance-security-security-monitoring-alignment-monitor",
            "label": "Alignment Monitor",
            "route": "/governance/security/alignment",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-security-monitoring-incident-response",
            "label": "Incident Response",
            "route": "/governance/security/incidents",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-security-monitoring-alerts-and-rules",
            "label": "Alerts & Rules",
            "route": "/governance/security/alerts",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "governance-security-security-monitoring-threat-detection",
            "label": "Threat Detection",
            "route": "/governance/security/detection",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "governance-security-security-monitoring-risk-scoring",
            "label": "Risk Scoring",
            "route": "/governance/security/risk",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-security-monitoring-forensics-and-evidence",
            "label": "Forensics & Evidence",
            "route": "/governance/security/forensics",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "governance-security-security-monitoring-vulnerability-management",
            "label": "Vulnerability Management",
            "route": "/governance/security/vuln",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "governance-security-ai-billing-and-cost-governance",
        "label": "AI Billing & Cost Governance",
        "homeRoute": "/governance/ai-billing-cost-governance",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 6,
        "features": [
          {
            "id": "governance-security-ai-billing-and-cost-governance-billing-and-usage",
            "label": "Billing & Usage",
            "route": "/governance/billing",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-ai-billing-and-cost-governance-usage-fabric",
            "label": "Usage Fabric",
            "route": "/governance/billing/usage",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-ai-billing-and-cost-governance-budgets-and-quotas",
            "label": "Budgets & Quotas",
            "route": "/governance/billing/budgets",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-ai-billing-and-cost-governance-cost-guardrails",
            "label": "Cost Guardrails",
            "route": "/governance/billing/guardrails",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-ai-billing-and-cost-governance-billing-optimizer",
            "label": "Billing Optimizer",
            "route": "/governance/billing/optimizer",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-ai-billing-and-cost-governance-chargeback-showback-reports",
            "label": "Chargeback/Showback Reports",
            "route": "/governance/billing/chargeback",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "governance-security-ai-billing-and-cost-governance-forecasting",
            "label": "Forecasting",
            "route": "/governance/billing/forecasting",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "governance-security-ai-billing-and-cost-governance-provider-rate-cards",
            "label": "Provider Rate Cards",
            "route": "/governance/billing/rates",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "governance-security-ai-billing-and-cost-governance-multi-tenant-billing",
            "label": "Multi-Tenant Billing",
            "route": "/governance/billing/multi-tenant",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "governance-security-compliance-and-regulator-fabric",
        "label": "Compliance & Regulator Fabric",
        "homeRoute": "/governance/compliance-regulator-fabric",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 7,
        "features": []
      },
      {
        "id": "governance-security-security-monitoring-and-response",
        "label": "Security Monitoring & Response",
        "homeRoute": "/governance/security-monitoring-response",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 8,
        "features": []
      },
      {
        "id": "governance-security-data-protection-and-classification",
        "label": "Data Protection & Classification",
        "homeRoute": "/governance/data-protection-classification",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 9,
        "features": [
          {
            "id": "governance-security-data-protection-and-classification-data-protection",
            "label": "Data Protection",
            "route": "/governance/data-protection",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-data-protection-and-classification-data-classification",
            "label": "Data Classification",
            "route": "/governance/data-protection/classification",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-data-protection-and-classification-data-masking",
            "label": "Data Masking",
            "route": "/governance/data-protection/masking",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "governance-security-data-protection-and-classification-tokenization",
            "label": "Tokenization",
            "route": "/governance/data-protection/tokenization",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "governance-security-data-protection-and-classification-dlp-rules",
            "label": "DLP Rules",
            "route": "/governance/data-protection/dlp",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "governance-security-data-protection-and-classification-data-residency",
            "label": "Data Residency",
            "route": "/governance/data-protection/residency",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          }
        ]
      }
    ]
  },
  {
    "id": "observability-evidence",
    "label": "Observability & Evidence",
    "path": "/observability",
    "actorScope": "enterprise",
    "order": 10,
    "categories": [
      {
        "id": "observability-evidence-evidence-packs",
        "label": "Evidence Packs",
        "homeRoute": "/observability/evidence",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 1,
        "features": [
          {
            "id": "observability-evidence-evidence-packs-export-for-auditors",
            "label": "Export for Auditors",
            "route": "/observability/evidence/export",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "observability-evidence-evidence-packs-evidence-queries",
            "label": "Evidence Queries",
            "route": "/observability/evidence/query",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "observability-evidence-metrics-and-telemetry",
        "label": "Metrics & Telemetry",
        "homeRoute": "/observability/metrics",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 2,
        "features": [
          {
            "id": "observability-evidence-metrics-and-telemetry-metric-explorer",
            "label": "Metric Explorer",
            "route": "/observability/metrics/explorer",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "observability-evidence-health-and-monitoring",
        "label": "Health & Monitoring",
        "homeRoute": "/observability/health",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 3,
        "features": []
      },
      {
        "id": "observability-evidence-record-auditor-and-logbook",
        "label": "Record Auditor & Logbook",
        "homeRoute": "/observability/record-auditor-logbook",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 4,
        "features": [
          {
            "id": "observability-evidence-record-auditor-and-logbook-record-auditor",
            "label": "Record Auditor",
            "route": "/observability/record-auditor",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "observability-evidence-record-auditor-and-logbook-logbook-timeline",
            "label": "Logbook Timeline",
            "route": "/observability/record-auditor/timeline",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "observability-evidence-record-auditor-and-logbook-audit-evidence",
            "label": "Audit Evidence",
            "route": "/observability/audit",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "observability-evidence-record-auditor-and-logbook-evidence-builder",
            "label": "Evidence Builder",
            "route": "/observability/record-auditor-logbook/builder",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "observability-evidence-evidence-and-audit",
        "label": "Evidence & Audit",
        "homeRoute": "/observability/evidence-audit",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 5,
        "features": [
          {
            "id": "observability-evidence-evidence-and-audit-audit-logs",
            "label": "Audit Logs",
            "route": "/observability/audit-logs",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "observability-evidence-evidence-and-audit-retention-policies",
            "label": "Retention Policies",
            "route": "/observability/retention",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "observability-evidence-logging-and-tracing",
        "label": "Logging & Tracing",
        "homeRoute": "/observability/logging-tracing",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 6,
        "features": [
          {
            "id": "observability-evidence-logging-and-tracing-structured-logging",
            "label": "Structured Logging",
            "route": "/observability/logging",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "observability-evidence-logging-and-tracing-log-explorer",
            "label": "Log Explorer",
            "route": "/observability/logging/explorer",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "observability-evidence-logging-and-tracing-distributed-tracing",
            "label": "Distributed Tracing",
            "route": "/observability/tracing",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "observability-evidence-logging-and-tracing-trace-explorer",
            "label": "Trace Explorer",
            "route": "/observability/tracing/explorer",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "observability-evidence-logging-and-tracing-correlation-and-context",
            "label": "Correlation & Context",
            "route": "/observability/correlation",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "observability-evidence-temporal-backtesting-and-replay",
        "label": "Temporal Backtesting & Replay",
        "homeRoute": "/observability/temporal-backtesting-replay",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 7,
        "features": [
          {
            "id": "observability-evidence-temporal-backtesting-and-replay-replay-engine",
            "label": "Replay Engine",
            "route": "/observability/replay",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "observability-evidence-temporal-backtesting-and-replay-scenario-library",
            "label": "Scenario Library",
            "route": "/observability/replay/scenarios",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "observability-evidence-temporal-backtesting-and-replay-determinism-checks",
            "label": "Determinism Checks",
            "route": "/observability/replay/determinism",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "observability-evidence-temporal-backtesting-and-replay-temporal-backtesting",
            "label": "Temporal Backtesting",
            "route": "/observability/backtesting",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "observability-evidence-health-and-self-healing",
        "label": "Health & Self-Healing",
        "homeRoute": "/observability/health-self-healing",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 8,
        "features": [
          {
            "id": "observability-evidence-health-and-self-healing-drift-detection",
            "label": "Drift Detection",
            "route": "/observability/drift",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "observability-evidence-health-and-self-healing-runbooks",
            "label": "Runbooks",
            "route": "/observability/runbooks",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "observability-evidence-health-and-self-healing-self-healing",
            "label": "Self-Healing",
            "route": "/observability/self-healing",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "observability-evidence-health-and-self-healing-automated-rollbacks",
            "label": "Automated Rollbacks",
            "route": "/observability/rollbacks",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "observability-evidence-dashboards-and-alerting",
        "label": "Dashboards & Alerting",
        "homeRoute": "/observability/dashboards-alerting",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 9,
        "features": [
          {
            "id": "observability-evidence-dashboards-and-alerting-dashboards",
            "label": "Dashboards",
            "route": "/observability/dashboards",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "observability-evidence-dashboards-and-alerting-dashboard-builder",
            "label": "Dashboard Builder",
            "route": "/observability/dashboards/builder",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "observability-evidence-dashboards-and-alerting-alerting",
            "label": "Alerting",
            "route": "/observability/alerting",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "observability-evidence-dashboards-and-alerting-alert-rules",
            "label": "Alert Rules",
            "route": "/observability/alerting/rules",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "observability-evidence-dashboards-and-alerting-notification-channels",
            "label": "Notification Channels",
            "route": "/observability/alerting/channels",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "observability-evidence-telemetry-and-metrics",
        "label": "Telemetry & Metrics",
        "homeRoute": "/observability/telemetry-metrics",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 10,
        "features": [
          {
            "id": "observability-evidence-telemetry-and-metrics-observability-overview",
            "label": "Observability Overview",
            "route": "/observability/telemetry-metrics/observability",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "observability-evidence-telemetry-and-metrics-monitoring",
            "label": "Monitoring",
            "route": "/observability/monitoring",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "observability-evidence-telemetry-and-metrics-analytics",
            "label": "Analytics",
            "route": "/observability/analytics",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "observability-evidence-telemetry-and-metrics-slis-and-slos",
            "label": "SLIs & SLOs",
            "route": "/observability/slis",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "observability-evidence-telemetry-and-metrics-slo-burn-rates",
            "label": "SLO Burn Rates",
            "route": "/observability/slis/burn",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "observability-evidence-telemetry-and-metrics-anomaly-detection",
            "label": "Anomaly Detection",
            "route": "/observability/anomalies",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      }
    ]
  },
  {
    "id": "operations-infrastructure",
    "label": "Operations & Infrastructure",
    "path": "/operations",
    "actorScope": "enterprise",
    "order": 11,
    "categories": [
      {
        "id": "operations-infrastructure-performance-and-scalability",
        "label": "Performance & Scalability",
        "homeRoute": "/operations/performance-scalability",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 1,
        "features": [
          {
            "id": "operations-infrastructure-performance-and-scalability-performance",
            "label": "Performance",
            "route": "/operations/performance",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-performance-and-scalability-scaling-strategies",
            "label": "Scaling Strategies",
            "route": "/operations/scaling",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-performance-and-scalability-capacity-planning",
            "label": "Capacity Planning",
            "route": "/operations/capacity",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-performance-and-scalability-load-testing",
            "label": "Load Testing",
            "route": "/operations/load-testing",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "operations-infrastructure-performance-and-scalability-backpressure-and-throttling",
            "label": "Backpressure & Throttling",
            "route": "/operations/backpressure",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-performance-and-scalability-reliability-patterns",
            "label": "Reliability Patterns",
            "route": "/operations/reliability",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-performance-and-scalability-driver-performance",
            "label": "Driver Performance",
            "route": "/operations/driver-performance",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-performance-and-scalability-cost-performance-tradeoffs",
            "label": "Cost/Performance Tradeoffs",
            "route": "/operations/cost-performance",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "operations-infrastructure-deployment-models",
        "label": "Deployment Models",
        "homeRoute": "/operations/deployment-models",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 2,
        "features": [
          {
            "id": "operations-infrastructure-deployment-models-local-mode",
            "label": "Local Mode",
            "route": "/operations/deployment/local",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-deployment-models-cloud-enterprise",
            "label": "Cloud/Enterprise",
            "route": "/operations/deployment/cloud",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-deployment-models-hybrid-and-edge",
            "label": "Hybrid & Edge",
            "route": "/operations/deployment/hybrid",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-deployment-models-blue-green-and-canary",
            "label": "Blue/Green & Canary",
            "route": "/operations/deployment/canary",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "operations-infrastructure-deployment-models-deployment-modes",
            "label": "Deployment Modes",
            "route": "/operations/deployment",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-deployment-models-kubernetes-deployment",
            "label": "Kubernetes Deployment",
            "route": "/operations/deployment/k8s",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "operations-infrastructure-deployment-models-airgapped-deployment",
            "label": "Airgapped Deployment",
            "route": "/operations/deployment/airgap",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "operations-infrastructure-deployment-models-upgrade-channels",
            "label": "Upgrade Channels",
            "route": "/operations/deployment/channels",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "operations-infrastructure-upgrades-and-migration",
        "label": "Upgrades & Migration",
        "homeRoute": "/operations/upgrades-migration",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 3,
        "features": [
          {
            "id": "operations-infrastructure-upgrades-and-migration-upgrades",
            "label": "Upgrades",
            "route": "/operations/upgrades",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-upgrades-and-migration-change-logs-and-release-notes",
            "label": "Change Logs & Release Notes",
            "route": "/operations/releases",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "operations-infrastructure-upgrades-and-migration-compatibility-matrix",
            "label": "Compatibility Matrix",
            "route": "/operations/compatibility",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "operations-infrastructure-upgrades-and-migration-migration",
            "label": "Migration",
            "route": "/operations/migration",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-upgrades-and-migration-rollback-strategy",
            "label": "Rollback Strategy",
            "route": "/operations/rollback",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "operations-infrastructure-failure-modes-and-resilience",
        "label": "Failure Modes & Resilience",
        "homeRoute": "/operations/failure-modes-resilience",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 4,
        "features": [
          {
            "id": "operations-infrastructure-failure-modes-and-resilience-failure-modes",
            "label": "Failure Modes",
            "route": "/operations/failure",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-failure-modes-and-resilience-detection-mechanisms",
            "label": "Detection Mechanisms",
            "route": "/operations/detection",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-failure-modes-and-resilience-recovery-strategies",
            "label": "Recovery Strategies",
            "route": "/operations/recovery",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-failure-modes-and-resilience-data-loss-protection",
            "label": "Data Loss Protection",
            "route": "/operations/data-protection",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-failure-modes-and-resilience-business-continuity-and-dr",
            "label": "Business Continuity & DR",
            "route": "/operations/bc-dr",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-failure-modes-and-resilience-dr-drills",
            "label": "DR Drills",
            "route": "/operations/bc-dr/drills",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "operations-infrastructure-failure-modes-and-resilience-security-incidents",
            "label": "Security Incidents",
            "route": "/operations/security-incidents",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-failure-modes-and-resilience-chaos-engineering",
            "label": "Chaos Engineering",
            "route": "/operations/chaos",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "operations-infrastructure-failure-modes-and-resilience-postmortems",
            "label": "Postmortems",
            "route": "/operations/postmortems",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "operations-infrastructure-infrastructure-and-topology",
        "label": "Infrastructure & Topology",
        "homeRoute": "/operations/infrastructure-topology",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 5,
        "features": [
          {
            "id": "operations-infrastructure-infrastructure-and-topology-configuration-management",
            "label": "Configuration Management",
            "route": "/operations/config",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-infrastructure-and-topology-secrets-and-configuration-vault",
            "label": "Secrets & Configuration Vault",
            "route": "/operations/secrets",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "operations-infrastructure-infrastructure-and-topology-compute-cluster-management",
            "label": "Compute/Cluster Management",
            "route": "/operations/cluster",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "operations-infrastructure-infrastructure-and-topology-network-topology",
            "label": "Network Topology",
            "route": "/operations/topology",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-infrastructure-and-topology-network-monitoring",
            "label": "Network Monitoring",
            "route": "/operations/infrastructure-topology/network",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-infrastructure-and-topology-storage-topology",
            "label": "Storage Topology",
            "route": "/operations/storage",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-infrastructure-and-topology-queues-and-search",
            "label": "Queues & Search",
            "route": "/operations/queues",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-infrastructure-and-topology-service-dependencies",
            "label": "Service Dependencies",
            "route": "/operations/dependencies",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "operations-infrastructure-infrastructure-and-topology-multi-region-and-dr",
            "label": "Multi-Region & DR",
            "route": "/operations/multi-region",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "operations-infrastructure-infrastructure-and-topology-hpc-integration",
            "label": "HPC Integration",
            "route": "/operations/hpc",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          }
        ]
      }
    ]
  },
  {
    "id": "vision-meta-stack",
    "label": "Vision & Meta-Stack",
    "path": "/vision",
    "actorScope": "enterprise",
    "order": 12,
    "categories": [
      {
        "id": "vision-meta-stack-core-os-engines",
        "label": "Core OS Engines",
        "homeRoute": "/vision/core-os",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 1,
        "features": [
          {
            "id": "vision-meta-stack-core-os-engines-core-os-engines",
            "label": "Core OS Engines",
            "route": "/vision/core-os-engines",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "vision-meta-stack-core-os-engines-capability-matrix",
            "label": "Capability Matrix",
            "route": "/vision/core-os-engines/matrix",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "vision-meta-stack-advanced-capabilities",
        "label": "Advanced Capabilities",
        "homeRoute": "/vision/advanced",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 2,
        "features": []
      },
      {
        "id": "vision-meta-stack-super-capabilities",
        "label": "Super Capabilities",
        "homeRoute": "/vision/super",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 3,
        "features": [
          {
            "id": "vision-meta-stack-super-capabilities-super-capabilities",
            "label": "Super Capabilities",
            "route": "/vision/super-capabilities",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "vision-meta-stack-super-capabilities-capability-matrix",
            "label": "Capability Matrix",
            "route": "/vision/super-capabilities/matrix",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "vision-meta-stack-hyper-capabilities",
        "label": "Hyper Capabilities",
        "homeRoute": "/vision/hyper",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 4,
        "features": []
      },
      {
        "id": "vision-meta-stack-ultra-capabilities",
        "label": "Ultra Capabilities",
        "homeRoute": "/vision/ultra",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 5,
        "features": []
      },
      {
        "id": "vision-meta-stack-supreme-capabilities",
        "label": "Supreme Capabilities",
        "homeRoute": "/vision/supreme",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 6,
        "features": [
          {
            "id": "vision-meta-stack-supreme-capabilities-capability-matrix",
            "label": "Capability Matrix",
            "route": "/vision/supreme/matrix",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "vision-meta-stack-ascend-capabilities",
        "label": "Ascend Capabilities",
        "homeRoute": "/vision/ascend",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 7,
        "features": [
          {
            "id": "vision-meta-stack-ascend-capabilities-capability-matrix",
            "label": "Capability Matrix",
            "route": "/vision/ascend/matrix",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "vision-meta-stack-advanced-horizons",
        "label": "Advanced Horizons",
        "homeRoute": "/vision/advanced-horizons",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 8,
        "features": [
          {
            "id": "vision-meta-stack-advanced-horizons-capability-matrix",
            "label": "Capability Matrix",
            "route": "/vision/advanced-horizons/matrix",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "vision-meta-stack-advanced-horizons-advanced-horizons",
            "label": "Advanced Horizons",
            "route": "/future/advanced",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "vision-meta-stack-meta-envelope",
        "label": "Meta Envelope",
        "homeRoute": "/vision/meta-envelope",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 9,
        "features": [
          {
            "id": "vision-meta-stack-meta-envelope-meta-envelope",
            "label": "Meta Envelope",
            "route": "/vision/meta",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "vision-meta-stack-meta-envelope-capability-matrix",
            "label": "Capability Matrix",
            "route": "/vision/meta-envelope/matrix",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "vision-meta-stack-hyper-network",
        "label": "Hyper Network",
        "homeRoute": "/vision/hyper-network",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 10,
        "features": [
          {
            "id": "vision-meta-stack-hyper-network-capability-matrix",
            "label": "Capability Matrix",
            "route": "/vision/hyper-network/matrix",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "vision-meta-stack-hyper-network-hyper-network",
            "label": "Hyper Network",
            "route": "/future/hyper",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "vision-meta-stack-supreme",
        "label": "Supreme",
        "homeRoute": "/future/supreme",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 11,
        "features": [
          {
            "id": "vision-meta-stack-supreme-capability-matrix",
            "label": "Capability Matrix",
            "route": "/future/supreme/matrix",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "vision-meta-stack-vision-deck-hub",
        "label": "Vision Deck Hub",
        "homeRoute": "/vision/vision-deck-hub",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 12,
        "features": [
          {
            "id": "vision-meta-stack-vision-deck-hub-vision-deck-hub",
            "label": "Vision Deck Hub",
            "route": "/vision/vision-deck-hub/vision",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "vision-meta-stack-vision-deck-hub-vision-roadmap",
            "label": "Vision Roadmap",
            "route": "/vision/roadmap",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "vision-meta-stack-vision-deck-hub-vision-glossary",
            "label": "Vision Glossary",
            "route": "/vision/glossary",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      },
      {
        "id": "vision-meta-stack-ultra-scale",
        "label": "Ultra Scale",
        "homeRoute": "/vision/ultra-scale",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 13,
        "features": [
          {
            "id": "vision-meta-stack-ultra-scale-capability-matrix",
            "label": "Capability Matrix",
            "route": "/vision/ultra-scale/matrix",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "vision-meta-stack-ultra-scale-ultra-scale",
            "label": "Ultra Scale",
            "route": "/future/ultra",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "vision-meta-stack-ascend",
        "label": "Ascend",
        "homeRoute": "/future/ascend",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 14,
        "features": [
          {
            "id": "vision-meta-stack-ascend-capability-matrix",
            "label": "Capability Matrix",
            "route": "/future/ascend/matrix",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          }
        ]
      }
    ]
  },
  {
    "id": "roadmap-risks",
    "label": "Roadmap & Risks",
    "path": "/roadmap",
    "actorScope": "enterprise",
    "order": 13,
    "categories": [
      {
        "id": "roadmap-risks-future-capabilities",
        "label": "Future Capabilities",
        "homeRoute": "/roadmap/future",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 1,
        "features": []
      },
      {
        "id": "roadmap-risks-risk-register",
        "label": "Risk Register",
        "homeRoute": "/roadmap/risks",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 2,
        "features": []
      },
      {
        "id": "roadmap-risks-open-questions",
        "label": "Open Questions",
        "homeRoute": "/roadmap/questions",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 3,
        "features": []
      },
      {
        "id": "roadmap-risks-roadmap-and-planning",
        "label": "Roadmap & Planning",
        "homeRoute": "/roadmap/roadmap-planning",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 4,
        "features": [
          {
            "id": "roadmap-risks-roadmap-and-planning-roadmap-overview",
            "label": "Roadmap Overview",
            "route": "/roadmap/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "roadmap-risks-roadmap-and-planning-phased-delivery",
            "label": "Phased Delivery",
            "route": "/roadmap/phases",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "roadmap-risks-roadmap-and-planning-milestones",
            "label": "Milestones",
            "route": "/roadmap/milestones",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "roadmap-risks-spec-maintenance",
        "label": "Spec Maintenance",
        "homeRoute": "/roadmap/spec-maintenance",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 5,
        "features": [
          {
            "id": "roadmap-risks-spec-maintenance-spec-versioning",
            "label": "Spec Versioning",
            "route": "/roadmap/spec",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "roadmap-risks-spec-maintenance-deprecations",
            "label": "Deprecations",
            "route": "/roadmap/deprecations",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "roadmap-risks-spec-maintenance-backward-compatibility-commitments",
            "label": "Backward Compatibility Commitments",
            "route": "/roadmap/compatibility",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": true
          },
          {
            "id": "roadmap-risks-spec-maintenance-future-capabilities",
            "label": "Future Capabilities",
            "route": "/roadmap/future-capabilities",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          }
        ]
      },
      {
        "id": "roadmap-risks-risks-and-decisions",
        "label": "Risks & Decisions",
        "homeRoute": "/roadmap/risks-decisions",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 6,
        "features": [
          {
            "id": "roadmap-risks-risks-and-decisions-decision-log",
            "label": "Decision Log",
            "route": "/roadmap/decisions",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "roadmap-risks-risks-and-decisions-known-gaps",
            "label": "Known Gaps",
            "route": "/roadmap/gaps",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          }
        ]
      }
    ]
  }
]

export const legacyRedirects: Record<string, string> = {
  "/projects": "/mission-control/core-flight-deck/projects",
  "/tasks": "/mission-control/core-flight-deck/tasks",
  "/": "/mission-control/core-flight-deck",
  "/projects/templates": "/mission-control/core-flight-deck/templates",
  "/projects/members": "/mission-control/core-flight-deck/members",
  "/projects/settings": "/mission-control/core-flight-deck/settings",
  "/tasks/board": "/mission-control/core-flight-deck/board",
  "/tasks/automation": "/mission-control/core-flight-deck/automation",
  "/tasks/analytics": "/mission-control/core-flight-deck/analytics",
  "/activity": "/mission-control/core-flight-deck/activity",
  "/notifications": "/mission-control/core-flight-deck/notifications",
  "/inbox": "/mission-control/core-flight-deck/inbox",
  "/timeline": "/mission-control/core-flight-deck/timeline",
  "/chat": "/mission-control/engagement-and-persona-surfaces/chat",
  "/collaboration": "/mission-control/engagement-and-persona-surfaces/collaboration",
  "/personalization": "/mission-control/engagement-and-persona-surfaces/personalization",
  "/search": "/mission-control/engagement-and-persona-surfaces/search",
  "/chat/library": "/mission-control/engagement-and-persona-surfaces/library",
  "/search/saved": "/mission-control/engagement-and-persona-surfaces/saved",
  "/collaboration/channels": "/mission-control/engagement-and-persona-surfaces/channels",
  "/collaboration/presence": "/mission-control/engagement-and-persona-surfaces/presence",
  "/personalization/macros": "/mission-control/engagement-and-persona-surfaces/macros",
  "/personalization/profiles": "/mission-control/engagement-and-persona-surfaces/profiles",
  "/work/tools": "/workspaces/dev-and-devops-workspace/tools",
  "/research": "/workspaces/research-and-simulation-workspace/research",
  "/work/templates": "/workspaces/writer-workspace/templates",
  "/work/writer": "/workspaces/writer-workspace/writer",
  "/ai/security": "/workspaces/cybersecurity-workspace/security",
  "/data": "/data-and-knowledge/core-data-stores/data",
  "/integrations": "/drivers-and-integrations/driver-registry-and-management/integrations",
  "/integrations/connectors": "/drivers-and-integrations/connectors-and-integrations/connectors",
  "/integrations/credentials": "/drivers-and-integrations/connectors-and-integrations/credentials",
  "/integrations/api-connectors": "/drivers-and-integrations/connectors-and-integrations/api-connectors",
  "/integrations/mcp-gateway": "/drivers/connectors-integrations/mcp-gateway",
  "/integrations/office": "/drivers-and-integrations/connectors-and-integrations/office",
  "/integrations/webhooks": "/drivers-and-integrations/connectors-and-integrations/webhooks",
  "/integrations/mappings": "/drivers-and-integrations/connectors-and-integrations/mappings",
  "/integrations/health": "/drivers-and-integrations/connectors-and-integrations/health",
  "/integrations/rate-limits": "/drivers-and-integrations/connectors-and-integrations/rate-limits",
  "/docs": "/docs-and-spec/documentation-hub/docs",
  "/settings": "/settings-and-admin/user-and-tenant-settings/settings",
  "/billing": "/governance-and-security/ai-billing-and-cost-governance/billing",
  "/audit": "/observability-and-evidence/record-auditor-and-logbook/audit",
  "/audit/builder": "/observability-and-evidence/record-auditor-and-logbook/builder",
  "/observability": "/observability-and-evidence/telemetry-and-metrics/observability",
  "/monitoring": "/observability-and-evidence/telemetry-and-metrics/monitoring",
  "/analytics": "/observability-and-evidence/telemetry-and-metrics/analytics",
  "/systems/network": "/operations-and-infrastructure/infrastructure-and-topology/network",
  "/future/core_os": "/vision-and-meta-stack/core-os-engines/core_os",
  "/future/core_os/matrix": "/vision-and-meta-stack/core-os-engines/matrix",
  "/future/super": "/vision-and-meta-stack/super-capabilities/super",
  "/future/super/matrix": "/vision-and-meta-stack/super-capabilities/matrix",
  "/future/advanced/matrix": "/vision-and-meta-stack/advanced-horizons/matrix",
  "/future/meta": "/vision-and-meta-stack/meta-envelope/meta",
  "/future/meta/matrix": "/vision-and-meta-stack/meta-envelope/matrix",
  "/future/hyper/matrix": "/vision-and-meta-stack/hyper-network/matrix",
  "/vision": "/vision-and-meta-stack/vision-deck-hub/vision",
  "/future/ultra/matrix": "/vision-and-meta-stack/ultra-scale/matrix",
  "/vision/vision-deck-hub": "/vision-and-meta-stack/vision-deck-hub/vision-deck-hub",
  "/vision/vision-deck-hub/vision": "/vision-and-meta-stack/vision-deck-hub/vision",
  "/vision/roadmap": "/vision-and-meta-stack/vision-deck-hub/roadmap",
  "/vision/glossary": "/vision-and-meta-stack/vision-deck-hub/glossary",
  "/vision/hub/overview": "/vision-and-meta-stack/vision-deck-hub/overview",
  "/vision/hub/layering": "/vision-and-meta-stack/vision-deck-hub/layering",
  "/vision/hub/capabilities": "/vision-and-meta-stack/vision-deck-hub/capabilities",
  "/vision/hub/phasing": "/vision-and-meta-stack/vision-deck-hub/phasing",
  "/vision/hub/todos": "/vision-and-meta-stack/vision-deck-hub/todos",
  "/vision/core-os-engines": "/vision-and-meta-stack/core-os-engines/core-os-engines",
  "/vision/core-os": "/vision-and-meta-stack/core-os-engines/core-os",
  "/vision/core-os-engines/matrix": "/vision-and-meta-stack/core-os-engines/matrix",
  "/vision/core/overview": "/vision-and-meta-stack/core-os-engines/overview",
  "/vision/core/baselines": "/vision-and-meta-stack/core-os-engines/baselines",
  "/vision/core/profession-os": "/vision-and-meta-stack/core-os-engines/profession-os",
  "/vision/core/todos": "/vision-and-meta-stack/core-os-engines/todos",
  "/vision/ascend": "/vision-and-meta-stack/ascend/ascend",
  "/vision/ascend/matrix": "/vision-and-meta-stack/ascend/matrix",
  "/future/ascend": "/vision-and-meta-stack/ascend/ascend",
  "/future/ascend/matrix": "/vision-and-meta-stack/ascend/matrix",
  "/vision/ascend/overview": "/vision-and-meta-stack/ascend/overview",
  "/vision/ascend/obligation": "/vision-and-meta-stack/ascend/obligation",
  "/vision/ascend/governance-shell": "/vision-and-meta-stack/ascend/governance-shell",
  "/vision/ascend/todos": "/vision-and-meta-stack/ascend/todos",
  "/vision/supreme": "/vision-and-meta-stack/supreme/supreme",
  "/vision/supreme/matrix": "/vision-and-meta-stack/supreme/matrix",
  "/future/supreme": "/vision-and-meta-stack/supreme/supreme",
  "/future/supreme/matrix": "/vision-and-meta-stack/supreme/matrix",
  "/vision/supreme/overview": "/vision-and-meta-stack/supreme/overview",
  "/vision/supreme/canon": "/vision-and-meta-stack/supreme/canon",
  "/vision/supreme/contracts": "/vision-and-meta-stack/supreme/contracts",
  "/vision/supreme/todos": "/vision-and-meta-stack/supreme/todos",
  "/vision/hyper-network": "/vision-and-meta-stack/hyper-network/hyper-network",
  "/vision/hyper": "/vision-and-meta-stack/hyper-network/hyper",
  "/vision/hyper-network/matrix": "/vision-and-meta-stack/hyper-network/matrix",
  "/future/hyper": "/vision-and-meta-stack/hyper-network/hyper",
  "/vision/hyper/overview": "/vision-and-meta-stack/hyper-network/overview",
  "/vision/hyper/hypermesh": "/vision-and-meta-stack/hyper-network/hypermesh",
  "/vision/hyper/hypersymphony": "/vision-and-meta-stack/hyper-network/hypersymphony",
  "/vision/hyper/todos": "/vision-and-meta-stack/hyper-network/todos",
  "/vision/super-capabilities": "/vision-and-meta-stack/super-capabilities/super-capabilities",
  "/vision/super": "/vision-and-meta-stack/super-capabilities/super",
  "/vision/super-capabilities/matrix": "/vision-and-meta-stack/super-capabilities/matrix",
  "/vision/super/overview": "/vision-and-meta-stack/super-capabilities/overview",
  "/vision/super/arc": "/vision-and-meta-stack/super-capabilities/arc",
  "/vision/super/self-evolving": "/vision-and-meta-stack/super-capabilities/self-evolving",
  "/vision/super/enterprise-twin": "/vision-and-meta-stack/super-capabilities/enterprise-twin",
  "/vision/super/todos": "/vision-and-meta-stack/super-capabilities/todos",
  "/vision/meta-envelope": "/vision-and-meta-stack/meta-envelope/meta-envelope",
  "/vision/meta": "/vision-and-meta-stack/meta-envelope/meta",
  "/vision/meta-envelope/matrix": "/vision-and-meta-stack/meta-envelope/matrix",
  "/vision/meta/overview": "/vision-and-meta-stack/meta-envelope/overview",
  "/vision/meta/envelope": "/vision-and-meta-stack/meta-envelope/envelope",
  "/vision/meta/safety": "/vision-and-meta-stack/meta-envelope/safety",
  "/vision/meta/todos": "/vision-and-meta-stack/meta-envelope/todos",
  "/vision/ultra-scale": "/vision-and-meta-stack/ultra-scale/ultra-scale",
  "/vision/ultra": "/vision-and-meta-stack/ultra-scale/ultra",
  "/vision/ultra-scale/matrix": "/vision-and-meta-stack/ultra-scale/matrix",
  "/future/ultra": "/vision-and-meta-stack/ultra-scale/ultra",
  "/vision/ultra/overview": "/vision-and-meta-stack/ultra-scale/overview",
  "/vision/ultra/reality-twin-mesh": "/vision-and-meta-stack/ultra-scale/reality-twin-mesh",
  "/vision/ultra/temporal-backtesting": "/vision-and-meta-stack/ultra-scale/temporal-backtesting",
  "/vision/ultra/todos": "/vision-and-meta-stack/ultra-scale/todos",
  "/vision/advanced-horizons": "/vision-and-meta-stack/advanced-horizons/advanced-horizons",
  "/vision/advanced": "/vision-and-meta-stack/advanced-horizons/advanced",
  "/vision/advanced-horizons/matrix": "/vision-and-meta-stack/advanced-horizons/matrix",
  "/future/advanced": "/vision-and-meta-stack/advanced-horizons/advanced",
  "/vision/advanced/overview": "/vision-and-meta-stack/advanced-horizons/overview",
  "/vision/advanced/envelope": "/vision-and-meta-stack/advanced-horizons/envelope",
  "/vision/advanced/todos": "/vision-and-meta-stack/advanced-horizons/todos",
  "/observability/logging-tracing": "/observability-and-evidence/logging-and-tracing/logging-tracing",
  "/observability/logging": "/observability-and-evidence/logging-and-tracing/logging",
  "/observability/logging/explorer": "/observability-and-evidence/logging-and-tracing/explorer",
  "/observability/tracing": "/observability-and-evidence/logging-and-tracing/tracing",
  "/observability/tracing/explorer": "/observability-and-evidence/logging-and-tracing/explorer",
  "/observability/correlation": "/observability-and-evidence/logging-and-tracing/correlation",
  "/observability/tracing/overview": "/observability-and-evidence/logging-and-tracing/overview",
  "/observability/tracing/logging": "/observability-and-evidence/logging-and-tracing/logging",
  "/observability/tracing/tracing": "/observability-and-evidence/logging-and-tracing/tracing",
  "/observability/tracing/policies": "/observability-and-evidence/logging-and-tracing/policies",
  "/observability/tracing/todos": "/observability-and-evidence/logging-and-tracing/todos",
  "/observability/telemetry-metrics": "/observability-and-evidence/telemetry-and-metrics/telemetry-metrics",
  "/observability/telemetry-metrics/observability": "/observability-and-evidence/telemetry-and-metrics/observability",
  "/observability/monitoring": "/observability-and-evidence/telemetry-and-metrics/monitoring",
  "/observability/analytics": "/observability-and-evidence/telemetry-and-metrics/analytics",
  "/observability/metrics": "/observability-and-evidence/telemetry-and-metrics/metrics",
  "/observability/metrics/explorer": "/observability-and-evidence/telemetry-and-metrics/explorer",
  "/observability/slis": "/observability-and-evidence/telemetry-and-metrics/slis",
  "/observability/slis/burn": "/observability-and-evidence/telemetry-and-metrics/burn",
  "/observability/anomalies": "/observability-and-evidence/telemetry-and-metrics/anomalies",
  "/observability/metrics/overview": "/observability-and-evidence/telemetry-and-metrics/overview",
  "/observability/metrics/model": "/observability-and-evidence/telemetry-and-metrics/model",
  "/observability/metrics/slos": "/observability-and-evidence/telemetry-and-metrics/slos",
  "/observability/metrics/analytics": "/observability-and-evidence/telemetry-and-metrics/analytics",
  "/observability/metrics/monitoring": "/observability-and-evidence/telemetry-and-metrics/monitoring",
  "/observability/metrics/todos": "/observability-and-evidence/telemetry-and-metrics/todos",
  "/observability/evidence-audit": "/observability-and-evidence/evidence-and-audit/evidence-audit",
  "/observability/audit-logs": "/observability-and-evidence/evidence-and-audit/audit-logs",
  "/observability/evidence": "/observability-and-evidence/evidence-and-audit/evidence",
  "/observability/evidence/query": "/observability-and-evidence/evidence-and-audit/query",
  "/observability/evidence/export": "/observability-and-evidence/evidence-and-audit/export",
  "/observability/retention": "/observability-and-evidence/evidence-and-audit/retention",
  "/observability/evidence/overview": "/observability-and-evidence/evidence-and-audit/overview",
  "/observability/evidence/packs": "/observability-and-evidence/evidence-and-audit/packs",
  "/observability/evidence/audit-logs": "/observability-and-evidence/evidence-and-audit/audit-logs",
  "/observability/evidence/retention": "/observability-and-evidence/evidence-and-audit/retention",
  "/observability/evidence/generator": "/observability-and-evidence/evidence-and-audit/generator",
  "/observability/evidence/regulator": "/observability-and-evidence/evidence-and-audit/regulator",
  "/observability/evidence/todos": "/observability-and-evidence/evidence-and-audit/todos",
  "/observability/dashboards-alerting": "/observability-and-evidence/dashboards-and-alerting/dashboards-alerting",
  "/observability/dashboards": "/observability-and-evidence/dashboards-and-alerting/dashboards",
  "/observability/dashboards/builder": "/observability-and-evidence/dashboards-and-alerting/builder",
  "/observability/alerting": "/observability-and-evidence/dashboards-and-alerting/alerting",
  "/observability/alerting/rules": "/observability-and-evidence/dashboards-and-alerting/rules",
  "/observability/alerting/channels": "/observability-and-evidence/dashboards-and-alerting/channels",
  "/observability/alerting/overview": "/observability-and-evidence/dashboards-and-alerting/overview",
  "/observability/alerting/dashboards": "/observability-and-evidence/dashboards-and-alerting/dashboards",
  "/observability/alerting/alerting": "/observability-and-evidence/dashboards-and-alerting/alerting",
  "/observability/alerting/oncall": "/observability-and-evidence/dashboards-and-alerting/oncall",
  "/observability/alerting/todos": "/observability-and-evidence/dashboards-and-alerting/todos",
  "/observability/temporal-backtesting-replay": "/observability-and-evidence/temporal-backtesting-and-replay/temporal-backtesting-replay",
  "/observability/replay": "/observability-and-evidence/temporal-backtesting-and-replay/replay",
  "/observability/replay/scenarios": "/observability-and-evidence/temporal-backtesting-and-replay/scenarios",
  "/observability/replay/determinism": "/observability-and-evidence/temporal-backtesting-and-replay/determinism",
  "/observability/backtesting": "/observability-and-evidence/temporal-backtesting-and-replay/backtesting",
  "/observability/replay/overview": "/observability-and-evidence/temporal-backtesting-and-replay/overview",
  "/observability/replay/engine": "/observability-and-evidence/temporal-backtesting-and-replay/engine",
  "/observability/replay/backtesting": "/observability-and-evidence/temporal-backtesting-and-replay/backtesting",
  "/observability/replay/counterfactuals": "/observability-and-evidence/temporal-backtesting-and-replay/counterfactuals",
  "/observability/replay/todos": "/observability-and-evidence/temporal-backtesting-and-replay/todos",
  "/observability/health-self-healing": "/observability-and-evidence/health-and-self-healing/health-self-healing",
  "/observability/health": "/observability-and-evidence/health-and-self-healing/health",
  "/observability/drift": "/observability-and-evidence/health-and-self-healing/drift",
  "/observability/runbooks": "/observability-and-evidence/health-and-self-healing/runbooks",
  "/observability/self-healing": "/observability-and-evidence/health-and-self-healing/self-healing",
  "/observability/rollbacks": "/observability-and-evidence/health-and-self-healing/rollbacks",
  "/observability/health/overview": "/observability-and-evidence/health-and-self-healing/overview",
  "/observability/health/checks": "/observability-and-evidence/health-and-self-healing/checks",
  "/observability/health/self-healing": "/observability-and-evidence/health-and-self-healing/self-healing",
  "/observability/health/runbooks": "/observability-and-evidence/health-and-self-healing/runbooks",
  "/observability/health/playbooks": "/observability-and-evidence/health-and-self-healing/playbooks",
  "/observability/health/todos": "/observability-and-evidence/health-and-self-healing/todos",
  "/observability/record-auditor-logbook": "/observability-and-evidence/record-auditor-and-logbook/record-auditor-logbook",
  "/observability/record-auditor": "/observability-and-evidence/record-auditor-and-logbook/record-auditor",
  "/observability/record-auditor/timeline": "/observability-and-evidence/record-auditor-and-logbook/timeline",
  "/observability/audit": "/observability-and-evidence/record-auditor-and-logbook/audit",
  "/observability/record-auditor-logbook/builder": "/observability-and-evidence/record-auditor-and-logbook/builder",
  "/observability/auditor/overview": "/observability-and-evidence/record-auditor-and-logbook/overview",
  "/observability/auditor/record-auditor": "/observability-and-evidence/record-auditor-and-logbook/record-auditor",
  "/observability/auditor/audit": "/observability-and-evidence/record-auditor-and-logbook/audit",
  "/observability/auditor/queries": "/observability-and-evidence/record-auditor-and-logbook/queries",
  "/observability/auditor/todos": "/observability-and-evidence/record-auditor-and-logbook/todos",
  "/observability/postmortems/overview": "/observability-and-evidence/postmortems-and-incident-analytics/overview",
  "/observability/postmortems/timeline": "/observability-and-evidence/postmortems-and-incident-analytics/timeline",
  "/observability/postmortems/root-cause": "/observability-and-evidence/postmortems-and-incident-analytics/root-cause",
  "/observability/postmortems/action-items": "/observability-and-evidence/postmortems-and-incident-analytics/action-items",
  "/observability/postmortems/todos": "/observability-and-evidence/postmortems-and-incident-analytics/todos",
  "/operations/infrastructure-topology": "/operations-and-infrastructure/infrastructure-and-topology/infrastructure-topology",
  "/operations/config": "/operations-and-infrastructure/infrastructure-and-topology/config",
  "/operations/secrets": "/operations-and-infrastructure/infrastructure-and-topology/secrets",
  "/operations/cluster": "/operations-and-infrastructure/infrastructure-and-topology/cluster",
  "/operations/topology": "/operations-and-infrastructure/infrastructure-and-topology/topology",
  "/operations/infrastructure-topology/network": "/operations-and-infrastructure/infrastructure-and-topology/network",
  "/operations/storage": "/operations-and-infrastructure/infrastructure-and-topology/storage",
  "/operations/queues": "/operations-and-infrastructure/infrastructure-and-topology/queues",
  "/operations/dependencies": "/operations-and-infrastructure/infrastructure-and-topology/dependencies",
  "/operations/multi-region": "/operations-and-infrastructure/infrastructure-and-topology/multi-region",
  "/operations/hpc": "/operations-and-infrastructure/infrastructure-and-topology/hpc",
  "/operations/topology/overview": "/operations-and-infrastructure/infrastructure-and-topology/overview",
  "/operations/topology/network": "/operations-and-infrastructure/infrastructure-and-topology/network",
  "/operations/topology/storage": "/operations-and-infrastructure/infrastructure-and-topology/storage",
  "/operations/topology/queues-search": "/operations-and-infrastructure/infrastructure-and-topology/queues-search",
  "/operations/topology/hpc": "/operations-and-infrastructure/infrastructure-and-topology/hpc",
  "/operations/topology/config": "/operations-and-infrastructure/infrastructure-and-topology/config",
  "/operations/topology/zero-trust": "/operations-and-infrastructure/infrastructure-and-topology/zero-trust",
  "/operations/topology/todos": "/operations-and-infrastructure/infrastructure-and-topology/todos",
  "/operations/failure-modes-resilience": "/operations-and-infrastructure/failure-modes-and-resilience/failure-modes-resilience",
  "/operations/failure": "/operations-and-infrastructure/failure-modes-and-resilience/failure",
  "/operations/detection": "/operations-and-infrastructure/failure-modes-and-resilience/detection",
  "/operations/recovery": "/operations-and-infrastructure/failure-modes-and-resilience/recovery",
  "/operations/data-protection": "/operations-and-infrastructure/failure-modes-and-resilience/data-protection",
  "/operations/bc-dr": "/operations-and-infrastructure/failure-modes-and-resilience/bc-dr",
  "/operations/bc-dr/drills": "/operations-and-infrastructure/failure-modes-and-resilience/drills",
  "/operations/security-incidents": "/operations-and-infrastructure/failure-modes-and-resilience/security-incidents",
  "/operations/chaos": "/operations-and-infrastructure/failure-modes-and-resilience/chaos",
  "/operations/postmortems": "/operations-and-infrastructure/failure-modes-and-resilience/postmortems",
  "/operations/resilience/overview": "/operations-and-infrastructure/failure-modes-and-resilience/overview",
  "/operations/resilience/failure": "/operations-and-infrastructure/failure-modes-and-resilience/failure",
  "/operations/resilience/detection": "/operations-and-infrastructure/failure-modes-and-resilience/detection",
  "/operations/resilience/recovery": "/operations-and-infrastructure/failure-modes-and-resilience/recovery",
  "/operations/resilience/data-protection": "/operations-and-infrastructure/failure-modes-and-resilience/data-protection",
  "/operations/resilience/security-incidents": "/operations-and-infrastructure/failure-modes-and-resilience/security-incidents",
  "/operations/resilience/bc-dr": "/operations-and-infrastructure/failure-modes-and-resilience/bc-dr",
  "/operations/resilience/todos": "/operations-and-infrastructure/failure-modes-and-resilience/todos",
  "/operations/performance-scalability": "/operations-and-infrastructure/performance-and-scalability/performance-scalability",
  "/operations/performance": "/operations-and-infrastructure/performance-and-scalability/performance",
  "/operations/scaling": "/operations-and-infrastructure/performance-and-scalability/scaling",
  "/operations/capacity": "/operations-and-infrastructure/performance-and-scalability/capacity",
  "/operations/load-testing": "/operations-and-infrastructure/performance-and-scalability/load-testing",
  "/operations/backpressure": "/operations-and-infrastructure/performance-and-scalability/backpressure",
  "/operations/reliability": "/operations-and-infrastructure/performance-and-scalability/reliability",
  "/operations/driver-performance": "/operations-and-infrastructure/performance-and-scalability/driver-performance",
  "/operations/cost-performance": "/operations-and-infrastructure/performance-and-scalability/cost-performance",
  "/operations/performance/overview": "/operations-and-infrastructure/performance-and-scalability/overview",
  "/operations/performance/nfr": "/operations-and-infrastructure/performance-and-scalability/nfr",
  "/operations/performance/sizing": "/operations-and-infrastructure/performance-and-scalability/sizing",
  "/operations/performance/scaling": "/operations-and-infrastructure/performance-and-scalability/scaling",
  "/operations/performance/driver-performance": "/operations-and-infrastructure/performance-and-scalability/driver-performance",
  "/operations/performance/backpressure": "/operations-and-infrastructure/performance-and-scalability/backpressure",
  "/operations/performance/reliability": "/operations-and-infrastructure/performance-and-scalability/reliability",
  "/operations/performance/benchmarks": "/operations-and-infrastructure/performance-and-scalability/benchmarks",
  "/operations/performance/todos": "/operations-and-infrastructure/performance-and-scalability/todos",
  "/operations/deployment-models": "/operations-and-infrastructure/deployment-models/deployment-models",
  "/operations/deployment": "/operations-and-infrastructure/deployment-models/deployment",
  "/operations/deployment/local": "/operations-and-infrastructure/deployment-models/local",
  "/operations/deployment/cloud": "/operations-and-infrastructure/deployment-models/cloud",
  "/operations/deployment/hybrid": "/operations-and-infrastructure/deployment-models/hybrid",
  "/operations/deployment/k8s": "/operations-and-infrastructure/deployment-models/k8s",
  "/operations/deployment/airgap": "/operations-and-infrastructure/deployment-models/airgap",
  "/operations/deployment/channels": "/operations-and-infrastructure/deployment-models/channels",
  "/operations/deployment/overview": "/operations-and-infrastructure/deployment-models/overview",
  "/operations/deployment/multi-region": "/operations-and-infrastructure/deployment-models/multi-region",
  "/operations/deployment/rollback": "/operations-and-infrastructure/deployment-models/rollback",
  "/operations/deployment/todos": "/operations-and-infrastructure/deployment-models/todos",
  "/operations/upgrades-migration": "/operations-and-infrastructure/upgrades-and-migration/upgrades-migration",
  "/operations/upgrades": "/operations-and-infrastructure/upgrades-and-migration/upgrades",
  "/operations/releases": "/operations-and-infrastructure/upgrades-and-migration/releases",
  "/operations/compatibility": "/operations-and-infrastructure/upgrades-and-migration/compatibility",
  "/operations/migration": "/operations-and-infrastructure/upgrades-and-migration/migration",
  "/operations/rollback": "/operations-and-infrastructure/upgrades-and-migration/rollback",
  "/operations/deployment/canary": "/operations-and-infrastructure/upgrades-and-migration/canary",
  "/operations/migration/overview": "/operations-and-infrastructure/upgrades-and-migration/overview",
  "/operations/migration/upgrades": "/operations-and-infrastructure/upgrades-and-migration/upgrades",
  "/operations/migration/migration": "/operations-and-infrastructure/upgrades-and-migration/migration",
  "/operations/migration/rollback": "/operations-and-infrastructure/upgrades-and-migration/rollback",
  "/operations/migration/todos": "/operations-and-infrastructure/upgrades-and-migration/todos",
  "/workspaces-enterprise-extensions/digital-twin-enterprise-twin-workspace/overview": "/workspaces-(enterprise-extensions)/digital-twin-and-enterprise-twin-workspace/overview",
  "/workspaces-enterprise-extensions/digital-twin-enterprise-twin-workspace/builder": "/workspaces-(enterprise-extensions)/digital-twin-and-enterprise-twin-workspace/builder",
  "/workspaces-enterprise-extensions/digital-twin-enterprise-twin-workspace/catalog": "/workspaces-(enterprise-extensions)/digital-twin-and-enterprise-twin-workspace/catalog",
  "/workspaces-enterprise-extensions/digital-twin-enterprise-twin-workspace/runtime": "/workspaces-(enterprise-extensions)/digital-twin-and-enterprise-twin-workspace/runtime",
  "/workspaces-enterprise-extensions/digital-twin-enterprise-twin-workspace/enterprise": "/workspaces-(enterprise-extensions)/digital-twin-and-enterprise-twin-workspace/enterprise",
  "/workspaces-enterprise-extensions/digital-twin-enterprise-twin-workspace/reality-mesh": "/workspaces-(enterprise-extensions)/digital-twin-and-enterprise-twin-workspace/reality-mesh",
  "/workspaces-enterprise-extensions/digital-twin-enterprise-twin-workspace/dependencies": "/workspaces-(enterprise-extensions)/digital-twin-and-enterprise-twin-workspace/dependencies",
  "/workspaces-enterprise-extensions/digital-twin-enterprise-twin-workspace/strategy": "/workspaces-(enterprise-extensions)/digital-twin-and-enterprise-twin-workspace/strategy",
  "/workspaces-enterprise-extensions/digital-twin-enterprise-twin-workspace/todos": "/workspaces-(enterprise-extensions)/digital-twin-and-enterprise-twin-workspace/todos",
  "/workspaces/record-auditor-logbook-workspace": "/workspaces-(enterprise-extensions)/record-auditor-and-logbook-workspace/record-auditor-logbook-workspace",
  "/workspaces/auditor": "/workspaces-(enterprise-extensions)/record-auditor-and-logbook-workspace/auditor",
  "/workspaces-enterprise-extensions/record-auditor-logbook-workspace/evidence": "/workspaces-(enterprise-extensions)/record-auditor-and-logbook-workspace/evidence",
  "/workspaces/auditor/controls": "/workspaces-(enterprise-extensions)/record-auditor-and-logbook-workspace/controls",
  "/workspaces-enterprise-extensions/record-auditor-logbook-workspace/requests": "/workspaces-(enterprise-extensions)/record-auditor-and-logbook-workspace/requests",
  "/workspaces/auditor/reports": "/workspaces-(enterprise-extensions)/record-auditor-and-logbook-workspace/reports",
  "/workspaces/auditor/logbook": "/workspaces-(enterprise-extensions)/record-auditor-and-logbook-workspace/logbook",
  "/workspaces-enterprise-extensions/record-auditor-logbook-workspace/regulator": "/workspaces-(enterprise-extensions)/record-auditor-and-logbook-workspace/regulator",
  "/workspaces-enterprise-extensions/record-auditor-logbook-workspace/overview": "/workspaces-(enterprise-extensions)/record-auditor-and-logbook-workspace/overview",
  "/workspaces-enterprise-extensions/record-auditor-logbook-workspace/trails": "/workspaces-(enterprise-extensions)/record-auditor-and-logbook-workspace/trails",
  "/workspaces-enterprise-extensions/record-auditor-logbook-workspace/audit-logs": "/workspaces-(enterprise-extensions)/record-auditor-and-logbook-workspace/audit-logs",
  "/workspaces-enterprise-extensions/record-auditor-logbook-workspace/replay": "/workspaces-(enterprise-extensions)/record-auditor-and-logbook-workspace/replay",
  "/workspaces-enterprise-extensions/record-auditor-logbook-workspace/todos": "/workspaces-(enterprise-extensions)/record-auditor-and-logbook-workspace/todos",
  "/workspaces-enterprise-extensions/writer-workspace/overview": "/workspaces-(enterprise-extensions)/writer-workspace/overview",
  "/workspaces-enterprise-extensions/writer-workspace/workstation": "/workspaces-(enterprise-extensions)/writer-workspace/workstation",
  "/workspaces-enterprise-extensions/writer-workspace/templates": "/workspaces-(enterprise-extensions)/writer-workspace/templates",
  "/workspaces-enterprise-extensions/writer-workspace/canon": "/workspaces-(enterprise-extensions)/writer-workspace/canon",
  "/workspaces-enterprise-extensions/writer-workspace/narrative": "/workspaces-(enterprise-extensions)/writer-workspace/narrative",
  "/workspaces-enterprise-extensions/writer-workspace/drafting": "/workspaces-(enterprise-extensions)/writer-workspace/drafting",
  "/workspaces-enterprise-extensions/writer-workspace/qa": "/workspaces-(enterprise-extensions)/writer-workspace/qa",
  "/workspaces-enterprise-extensions/writer-workspace/collaboration": "/workspaces-(enterprise-extensions)/writer-workspace/collaboration",
  "/workspaces-enterprise-extensions/writer-workspace/publishing": "/workspaces-(enterprise-extensions)/writer-workspace/publishing",
  "/workspaces-enterprise-extensions/writer-workspace/production": "/workspaces-(enterprise-extensions)/writer-workspace/production",
  "/workspaces-enterprise-extensions/writer-workspace/rights": "/workspaces-(enterprise-extensions)/writer-workspace/rights",
  "/workspaces-enterprise-extensions/writer-workspace/todos": "/workspaces-(enterprise-extensions)/writer-workspace/todos",
  "/workspaces-enterprise-extensions/operator-sre-workspace/overview": "/workspaces-(enterprise-extensions)/operator-and-sre-workspace/overview",
  "/workspaces-enterprise-extensions/operator-sre-workspace/health": "/workspaces-(enterprise-extensions)/operator-and-sre-workspace/health",
  "/workspaces-enterprise-extensions/operator-sre-workspace/reliability": "/workspaces-(enterprise-extensions)/operator-and-sre-workspace/reliability",
  "/workspaces-enterprise-extensions/operator-sre-workspace/oncall": "/workspaces-(enterprise-extensions)/operator-and-sre-workspace/oncall",
  "/workspaces-enterprise-extensions/operator-sre-workspace/runbooks": "/workspaces-(enterprise-extensions)/operator-and-sre-workspace/runbooks",
  "/workspaces-enterprise-extensions/operator-sre-workspace/sandbox": "/workspaces-(enterprise-extensions)/operator-and-sre-workspace/sandbox",
  "/workspaces-enterprise-extensions/operator-sre-workspace/capacity": "/workspaces-(enterprise-extensions)/operator-and-sre-workspace/capacity",
  "/workspaces-enterprise-extensions/operator-sre-workspace/incidents": "/workspaces-(enterprise-extensions)/operator-and-sre-workspace/incidents",
  "/workspaces-enterprise-extensions/operator-sre-workspace/todos": "/workspaces-(enterprise-extensions)/operator-and-sre-workspace/todos",
  "/workspaces-enterprise-extensions/archive-continuity-workspace/overview": "/workspaces-(enterprise-extensions)/archive-and-continuity-workspace/overview",
  "/workspaces-enterprise-extensions/archive-continuity-workspace/engine": "/workspaces-(enterprise-extensions)/archive-and-continuity-workspace/engine",
  "/workspaces-enterprise-extensions/archive-continuity-workspace/search": "/workspaces-(enterprise-extensions)/archive-and-continuity-workspace/search",
  "/workspaces-enterprise-extensions/archive-continuity-workspace/time-travel": "/workspaces-(enterprise-extensions)/archive-and-continuity-workspace/time-travel",
  "/workspaces-enterprise-extensions/archive-continuity-workspace/drift": "/workspaces-(enterprise-extensions)/archive-and-continuity-workspace/drift",
  "/workspaces-enterprise-extensions/archive-continuity-workspace/resonance": "/workspaces-(enterprise-extensions)/archive-and-continuity-workspace/resonance",
  "/workspaces-enterprise-extensions/archive-continuity-workspace/todos": "/workspaces-(enterprise-extensions)/archive-and-continuity-workspace/todos",
  "/workspaces-enterprise-extensions/research-simulation-workspace/overview": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/overview",
  "/workspaces-enterprise-extensions/research-simulation-workspace/lab": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/lab",
  "/workspaces-enterprise-extensions/research-simulation-workspace/data-sources": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/data-sources",
  "/workspaces-enterprise-extensions/research-simulation-workspace/experiments": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/experiments",
  "/workspaces-enterprise-extensions/research-simulation-workspace/sweeps": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/sweeps",
  "/workspaces-enterprise-extensions/research-simulation-workspace/simulation": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/simulation",
  "/workspaces-enterprise-extensions/research-simulation-workspace/cad-multiphysics": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/cad-multiphysics",
  "/workspaces-enterprise-extensions/research-simulation-workspace/validation": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/validation",
  "/workspaces-enterprise-extensions/research-simulation-workspace/optimization": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/optimization",
  "/workspaces-enterprise-extensions/research-simulation-workspace/calibration": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/calibration",
  "/workspaces-enterprise-extensions/research-simulation-workspace/digital-twins": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/digital-twins",
  "/workspaces-enterprise-extensions/research-simulation-workspace/composer": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/composer",
  "/workspaces-enterprise-extensions/research-simulation-workspace/knowledge-graph": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/knowledge-graph",
  "/workspaces-enterprise-extensions/research-simulation-workspace/ip-assistant": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/ip-assistant",
  "/workspaces-enterprise-extensions/research-simulation-workspace/hpc": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/hpc",
  "/workspaces-enterprise-extensions/research-simulation-workspace/training": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/training",
  "/workspaces-enterprise-extensions/research-simulation-workspace/cross-tool": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/cross-tool",
  "/workspaces-enterprise-extensions/research-simulation-workspace/knowledge-atlas": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/knowledge-atlas",
  "/workspaces-enterprise-extensions/research-simulation-workspace/todos": "/workspaces-(enterprise-extensions)/research-and-simulation-workspace/todos",
  "/workspaces-enterprise-extensions/business-finance-workspace/overview": "/workspaces-(enterprise-extensions)/business-and-finance-workspace/overview",
  "/workspaces-enterprise-extensions/business-finance-workspace/accounting": "/workspaces-(enterprise-extensions)/business-and-finance-workspace/accounting",
  "/workspaces-enterprise-extensions/business-finance-workspace/budgets": "/workspaces-(enterprise-extensions)/business-and-finance-workspace/budgets",
  "/workspaces-enterprise-extensions/business-finance-workspace/scenarios": "/workspaces-(enterprise-extensions)/business-and-finance-workspace/scenarios",
  "/workspaces-enterprise-extensions/business-finance-workspace/studio": "/workspaces-(enterprise-extensions)/business-and-finance-workspace/studio",
  "/workspaces-enterprise-extensions/business-finance-workspace/cost-governance": "/workspaces-(enterprise-extensions)/business-and-finance-workspace/cost-governance",
  "/workspaces-enterprise-extensions/business-finance-workspace/billing-insights": "/workspaces-(enterprise-extensions)/business-and-finance-workspace/billing-insights",
  "/workspaces-enterprise-extensions/business-finance-workspace/todos": "/workspaces-(enterprise-extensions)/business-and-finance-workspace/todos",
  "/workspaces-enterprise-extensions/cybersecurity-workspace/overview": "/workspaces-(enterprise-extensions)/cybersecurity-workspace/overview",
  "/workspaces-enterprise-extensions/cybersecurity-workspace/guardian": "/workspaces-(enterprise-extensions)/cybersecurity-workspace/guardian",
  "/workspaces-enterprise-extensions/cybersecurity-workspace/assets": "/workspaces-(enterprise-extensions)/cybersecurity-workspace/assets",
  "/workspaces-enterprise-extensions/cybersecurity-workspace/threat-modeling": "/workspaces-(enterprise-extensions)/cybersecurity-workspace/threat-modeling",
  "/workspaces-enterprise-extensions/cybersecurity-workspace/hardening": "/workspaces-(enterprise-extensions)/cybersecurity-workspace/hardening",
  "/workspaces-enterprise-extensions/cybersecurity-workspace/findings": "/workspaces-(enterprise-extensions)/cybersecurity-workspace/findings",
  "/workspaces-enterprise-extensions/cybersecurity-workspace/auto-remediation": "/workspaces-(enterprise-extensions)/cybersecurity-workspace/auto-remediation",
  "/workspaces-enterprise-extensions/cybersecurity-workspace/incidents": "/workspaces-(enterprise-extensions)/cybersecurity-workspace/incidents",
  "/workspaces-enterprise-extensions/cybersecurity-workspace/forensics": "/workspaces-(enterprise-extensions)/cybersecurity-workspace/forensics",
  "/workspaces-enterprise-extensions/cybersecurity-workspace/compliance": "/workspaces-(enterprise-extensions)/cybersecurity-workspace/compliance",
  "/workspaces-enterprise-extensions/cybersecurity-workspace/todos": "/workspaces-(enterprise-extensions)/cybersecurity-workspace/todos",
  "/workspaces-enterprise-extensions/dev-devops-workspace/overview": "/workspaces-(enterprise-extensions)/dev-and-devops-workspace/overview",
  "/workspaces-enterprise-extensions/dev-devops-workspace/repo": "/workspaces-(enterprise-extensions)/dev-and-devops-workspace/repo",
  "/workspaces-enterprise-extensions/dev-devops-workspace/environment": "/workspaces-(enterprise-extensions)/dev-and-devops-workspace/environment",
  "/workspaces-enterprise-extensions/dev-devops-workspace/commit-tasks": "/workspaces-(enterprise-extensions)/dev-and-devops-workspace/commit-tasks",
  "/workspaces-enterprise-extensions/dev-devops-workspace/merge-advisor": "/workspaces-(enterprise-extensions)/dev-and-devops-workspace/merge-advisor",
  "/workspaces-enterprise-extensions/dev-devops-workspace/reviews": "/workspaces-(enterprise-extensions)/dev-and-devops-workspace/reviews",
  "/workspaces-enterprise-extensions/dev-devops-workspace/cicd": "/workspaces-(enterprise-extensions)/dev-and-devops-workspace/cicd",
  "/workspaces-enterprise-extensions/dev-devops-workspace/release-evidence": "/workspaces-(enterprise-extensions)/dev-and-devops-workspace/release-evidence",
  "/workspaces-enterprise-extensions/dev-devops-workspace/tools": "/workspaces-(enterprise-extensions)/dev-and-devops-workspace/tools",
  "/workspaces-enterprise-extensions/dev-devops-workspace/sbom": "/workspaces-(enterprise-extensions)/dev-and-devops-workspace/sbom",
  "/workspaces-enterprise-extensions/dev-devops-workspace/runbooks": "/workspaces-(enterprise-extensions)/dev-and-devops-workspace/runbooks",
  "/workspaces-enterprise-extensions/dev-devops-workspace/todos": "/workspaces-(enterprise-extensions)/dev-and-devops-workspace/todos",
  "/settings-admin-enterprise-extensions/billing-usage/overview": "/settings-and-admin-(enterprise-extensions)/billing-and-usage/overview",
  "/settings-admin-enterprise-extensions/billing-usage/plan": "/settings-and-admin-(enterprise-extensions)/billing-and-usage/plan",
  "/settings-admin-enterprise-extensions/billing-usage/usage": "/settings-and-admin-(enterprise-extensions)/billing-and-usage/usage",
  "/settings-admin-enterprise-extensions/billing-usage/budgets": "/settings-and-admin-(enterprise-extensions)/billing-and-usage/budgets",
  "/settings-admin-enterprise-extensions/billing-usage/payment": "/settings-and-admin-(enterprise-extensions)/billing-and-usage/payment",
  "/settings-admin-enterprise-extensions/workspace-settings/overview": "/settings-and-admin-(enterprise-extensions)/workspace-settings/overview",
  "/settings-admin-enterprise-extensions/workspace-settings/manage": "/settings-and-admin-(enterprise-extensions)/workspace-settings/manage",
  "/settings-admin-enterprise-extensions/workspace-settings/defaults": "/settings-and-admin-(enterprise-extensions)/workspace-settings/defaults",
  "/settings-admin-enterprise-extensions/workspace-settings/environment-profiles": "/settings-and-admin-(enterprise-extensions)/workspace-settings/environment-profiles",
  "/settings-admin-enterprise-extensions/system-diagnostics/overview": "/settings-and-admin-(enterprise-extensions)/system-diagnostics/overview",
  "/settings-admin-enterprise-extensions/system-diagnostics/health": "/settings-and-admin-(enterprise-extensions)/system-diagnostics/health",
  "/settings-admin-enterprise-extensions/system-diagnostics/support-bundle": "/settings-and-admin-(enterprise-extensions)/system-diagnostics/support-bundle",
  "/settings-admin-enterprise-extensions/system-diagnostics/version": "/settings-and-admin-(enterprise-extensions)/system-diagnostics/version",
  "/settings/enterprise/user-tenant": "/settings-and-admin-(enterprise-extensions)/user-and-tenant-settings/user-tenant",
  "/settings/team": "/settings-and-admin-(enterprise-extensions)/user-and-tenant-settings/team",
  "/settings/tenant": "/settings-and-admin-(enterprise-extensions)/user-and-tenant-settings/tenant",
  "/settings/audit": "/settings-and-admin-(enterprise-extensions)/user-and-tenant-settings/audit",
  "/settings-admin-enterprise-extensions/feature-flags-labs/overview": "/settings-and-admin-(enterprise-extensions)/feature-flags-and-labs/overview",
  "/settings-admin-enterprise-extensions/feature-flags-labs/feature-flags": "/settings-and-admin-(enterprise-extensions)/feature-flags-and-labs/feature-flags",
  "/settings-admin-enterprise-extensions/feature-flags-labs/model-providers": "/settings-and-admin-(enterprise-extensions)/feature-flags-and-labs/model-providers",
  "/settings-admin-enterprise-extensions/user-profile-preferences/overview": "/settings-and-admin-(enterprise-extensions)/user-profile-and-preferences/overview",
  "/settings-admin-enterprise-extensions/user-profile-preferences/profile": "/settings-and-admin-(enterprise-extensions)/user-profile-and-preferences/profile",
  "/settings-admin-enterprise-extensions/user-profile-preferences/personas": "/settings-and-admin-(enterprise-extensions)/user-profile-and-preferences/personas",
  "/settings-admin-enterprise-extensions/user-profile-preferences/notifications": "/settings-and-admin-(enterprise-extensions)/user-profile-and-preferences/notifications",
  "/settings-admin-enterprise-extensions/user-profile-preferences/ui": "/settings-and-admin-(enterprise-extensions)/user-profile-and-preferences/ui",
  "/settings-admin-enterprise-extensions/user-profile-preferences/export": "/settings-and-admin-(enterprise-extensions)/user-profile-and-preferences/export",
  "/settings-admin-enterprise-extensions/security-privacy/overview": "/settings-and-admin-(enterprise-extensions)/security-and-privacy/overview",
  "/settings-admin-enterprise-extensions/security-privacy/auth": "/settings-and-admin-(enterprise-extensions)/security-and-privacy/auth",
  "/settings-admin-enterprise-extensions/security-privacy/devices": "/settings-and-admin-(enterprise-extensions)/security-and-privacy/devices",
  "/settings-admin-enterprise-extensions/security-privacy/privacy": "/settings-and-admin-(enterprise-extensions)/security-and-privacy/privacy",
  "/settings-admin-enterprise-extensions/security-privacy/keys": "/settings-and-admin-(enterprise-extensions)/security-and-privacy/keys",
  "/settings-admin-enterprise-extensions/tenant-org-admin/overview": "/settings-and-admin-(enterprise-extensions)/tenant-and-org-admin/overview",
  "/settings-admin-enterprise-extensions/tenant-org-admin/sso": "/settings-and-admin-(enterprise-extensions)/tenant-and-org-admin/sso",
  "/settings-admin-enterprise-extensions/tenant-org-admin/rbac": "/settings-and-admin-(enterprise-extensions)/tenant-and-org-admin/rbac",
  "/settings-admin-enterprise-extensions/tenant-org-admin/compliance": "/settings-and-admin-(enterprise-extensions)/tenant-and-org-admin/compliance",
  "/settings-admin-enterprise-extensions/tenant-org-admin/residency": "/settings-and-admin-(enterprise-extensions)/tenant-and-org-admin/residency",
  "/settings-admin-enterprise-extensions/tenant-org-admin/billing": "/settings-and-admin-(enterprise-extensions)/tenant-and-org-admin/billing",
  "/settings-admin-enterprise-extensions/integrations-credentials/overview": "/settings-and-admin-(enterprise-extensions)/integrations-and-credentials/overview",
  "/settings-admin-enterprise-extensions/integrations-credentials/connected-apps": "/settings-and-admin-(enterprise-extensions)/integrations-and-credentials/connected-apps",
  "/settings-admin-enterprise-extensions/integrations-credentials/credentials": "/settings-and-admin-(enterprise-extensions)/integrations-and-credentials/credentials",
  "/settings-admin-enterprise-extensions/integrations-credentials/permissions": "/settings-and-admin-(enterprise-extensions)/integrations-and-credentials/permissions",
  "/settings-admin-enterprise-extensions/integrations-credentials/rotation": "/settings-and-admin-(enterprise-extensions)/integrations-and-credentials/rotation",
  "/mission/architecture-principles": "/mission-and-architecture/architecture-and-principles/architecture-principles",
  "/mission/architecture": "/mission-and-architecture/architecture-and-principles/architecture",
  "/mission/principles": "/mission-and-architecture/architecture-and-principles/principles",
  "/mission/components": "/mission-and-architecture/architecture-and-principles/components",
  "/mission/orchestrator": "/mission-and-architecture/architecture-and-principles/orchestrator",
  "/mission/mapping": "/mission-and-architecture/architecture-and-principles/mapping",
  "/mission/contracts": "/mission-and-architecture/architecture-and-principles/contracts",
  "/mission/extensibility": "/mission-and-architecture/architecture-and-principles/extensibility",
  "/mission/threat-model": "/mission-and-architecture/architecture-and-principles/threat-model",
  "/mission/performance-targets": "/mission-and-architecture/architecture-and-principles/performance-targets",
  "/mission/architecture/overview": "/mission-and-architecture/architecture-and-principles/overview",
  "/mission/architecture/components": "/mission-and-architecture/architecture-and-principles/components",
  "/mission/architecture/principles": "/mission-and-architecture/architecture-and-principles/principles",
  "/mission/architecture/mapping": "/mission-and-architecture/architecture-and-principles/mapping",
  "/mission/architecture/deploy-mapping": "/mission-and-architecture/architecture-and-principles/deploy-mapping",
  "/mission/architecture/platform-envelope": "/mission-and-architecture/architecture-and-principles/platform-envelope",
  "/mission/architecture/orchestrator": "/mission-and-architecture/architecture-and-principles/orchestrator",
  "/mission/architecture/modalities": "/mission-and-architecture/architecture-and-principles/modalities",
  "/mission/architecture/hitl": "/mission-and-architecture/architecture-and-principles/hitl",
  "/mission/architecture/errors": "/mission-and-architecture/architecture-and-principles/errors",
  "/mission/architecture/guardrails": "/mission-and-architecture/architecture-and-principles/guardrails",
  "/mission/architecture/todos": "/mission-and-architecture/architecture-and-principles/todos",
  "/mission/domain/overview": "/mission-and-architecture/domain-and-knowledge-model/overview",
  "/mission/domain/identity": "/mission-and-architecture/domain-and-knowledge-model/identity",
  "/mission/domain/projects": "/mission-and-architecture/domain-and-knowledge-model/projects",
  "/mission/domain/tasks": "/mission-and-architecture/domain-and-knowledge-model/tasks",
  "/mission/domain/cir": "/mission-and-architecture/domain-and-knowledge-model/cir",
  "/mission/domain/ledger": "/mission-and-architecture/domain-and-knowledge-model/ledger",
  "/mission/domain/capsules": "/mission-and-architecture/domain-and-knowledge-model/capsules",
  "/mission/domain/environments": "/mission-and-architecture/domain-and-knowledge-model/environments",
  "/mission/domain/policies": "/mission-and-architecture/domain-and-knowledge-model/policies",
  "/mission/domain/billing": "/mission-and-architecture/domain-and-knowledge-model/billing",
  "/mission/domain/time": "/mission-and-architecture/domain-and-knowledge-model/time",
  "/mission/domain/todos": "/mission-and-architecture/domain-and-knowledge-model/todos",
  "/mission/mission-identity": "/mission-and-architecture/mission-and-identity/mission-identity",
  "/mission/overview": "/mission-and-architecture/mission-and-identity/overview",
  "/mission/use-cases": "/mission-and-architecture/mission-and-identity/use-cases",
  "/mission/non-goals": "/mission-and-architecture/mission-and-identity/non-goals",
  "/mission/glossary": "/mission-and-architecture/mission-and-identity/glossary",
  "/mission/modes": "/mission-and-architecture/mission-and-identity/modes",
  "/mission/reference-architectures": "/mission-and-architecture/mission-and-identity/reference-architectures",
  "/mission/identity": "/mission-and-architecture/mission-and-identity/identity",
  "/mission/ai-stack": "/mission-and-architecture/mission-and-identity/ai-stack",
  "/mission/models": "/mission-and-architecture/mission-and-identity/models",
  "/mission/daemons": "/mission-and-architecture/mission-and-identity/daemons",
  "/mission-architecture/mission-identity/personas": "/mission-and-architecture/mission-and-identity/personas",
  "/mission/identity/overview": "/mission-and-architecture/mission-and-identity/overview",
  "/mission/identity/principles": "/mission-and-architecture/mission-and-identity/principles",
  "/mission/identity/modes": "/mission-and-architecture/mission-and-identity/modes",
  "/mission/identity/actors": "/mission-and-architecture/mission-and-identity/actors",
  "/mission/identity/roles": "/mission-and-architecture/mission-and-identity/roles",
  "/mission/identity/personas": "/mission-and-architecture/mission-and-identity/personas",
  "/mission/identity/daemons": "/mission-and-architecture/mission-and-identity/daemons",
  "/mission/identity/ai-driver-stack": "/mission-and-architecture/mission-and-identity/ai-driver-stack",
  "/mission/identity/model-layer": "/mission-and-architecture/mission-and-identity/model-layer",
  "/mission/identity/glossary": "/mission-and-architecture/mission-and-identity/glossary",
  "/mission/identity/todos": "/mission-and-architecture/mission-and-identity/todos",
  "/mission/planes-architecture": "/mission-and-architecture/planes-architecture/planes-architecture",
  "/mission/planes": "/mission-and-architecture/planes-architecture/planes",
  "/mission/planes/data": "/mission-and-architecture/planes-architecture/data",
  "/mission/planes/control": "/mission-and-architecture/planes-architecture/control",
  "/mission/planes/governance": "/mission-and-architecture/planes-architecture/governance",
  "/mission/planes/cross-plane": "/mission-and-architecture/planes-architecture/cross-plane",
  "/mission/planes/contracts": "/mission-and-architecture/planes-architecture/contracts",
  "/mission/planes/failure-domains": "/mission-and-architecture/planes-architecture/failure-domains",
  "/mission/planes/overview": "/mission-and-architecture/planes-architecture/overview",
  "/mission/planes/slos": "/mission-and-architecture/planes-architecture/slos",
  "/mission/planes/todos": "/mission-and-architecture/planes-architecture/todos",
  "/roadmap/roadmap-planning": "/roadmap-and-risks/roadmap-and-planning/roadmap-planning",
  "/roadmap/overview": "/roadmap-and-risks/roadmap-and-planning/overview",
  "/roadmap/phases": "/roadmap-and-risks/roadmap-and-planning/phases",
  "/roadmap/milestones": "/roadmap-and-risks/roadmap-and-planning/milestones",
  "/roadmap/future": "/roadmap-and-risks/roadmap-and-planning/future",
  "/roadmap/planning/overview": "/roadmap-and-risks/roadmap-and-planning/overview",
  "/roadmap/planning/phases": "/roadmap-and-risks/roadmap-and-planning/phases",
  "/roadmap/planning/milestones": "/roadmap-and-risks/roadmap-and-planning/milestones",
  "/roadmap/planning/dependencies": "/roadmap-and-risks/roadmap-and-planning/dependencies",
  "/roadmap/planning/future": "/roadmap-and-risks/roadmap-and-planning/future",
  "/roadmap/planning/todos": "/roadmap-and-risks/roadmap-and-planning/todos",
  "/roadmap/spec-maintenance": "/roadmap-and-risks/spec-maintenance/spec-maintenance",
  "/roadmap/spec": "/roadmap-and-risks/spec-maintenance/spec",
  "/roadmap/deprecations": "/roadmap-and-risks/spec-maintenance/deprecations",
  "/roadmap/compatibility": "/roadmap-and-risks/spec-maintenance/compatibility",
  "/roadmap/future-capabilities": "/roadmap-and-risks/spec-maintenance/future-capabilities",
  "/roadmap/spec/overview": "/roadmap-and-risks/spec-maintenance/overview",
  "/roadmap/spec/versioning": "/roadmap-and-risks/spec-maintenance/versioning",
  "/roadmap/spec/proposals": "/roadmap-and-risks/spec-maintenance/proposals",
  "/roadmap/spec/future-capabilities": "/roadmap-and-risks/spec-maintenance/future-capabilities",
  "/roadmap/risks-decisions": "/roadmap-and-risks/risks-and-decisions/risks-decisions",
  "/roadmap/risks": "/roadmap-and-risks/risks-and-decisions/risks",
  "/roadmap/decisions": "/roadmap-and-risks/risks-and-decisions/decisions",
  "/roadmap/gaps": "/roadmap-and-risks/risks-and-decisions/gaps",
  "/roadmap/questions": "/roadmap-and-risks/risks-and-decisions/questions",
  "/roadmap/risk/overview": "/roadmap-and-risks/risks-and-decisions/overview",
  "/roadmap/risk/risks": "/roadmap-and-risks/risks-and-decisions/risks",
  "/roadmap/risk/decisions": "/roadmap-and-risks/risks-and-decisions/decisions",
  "/roadmap/risk/gaps": "/roadmap-and-risks/risks-and-decisions/gaps",
  "/roadmap/risk/questions": "/roadmap-and-risks/risks-and-decisions/questions",
  "/roadmap/risk/derisk": "/roadmap-and-risks/risks-and-decisions/derisk",
  "/roadmap/risk/todos": "/roadmap-and-risks/risks-and-decisions/todos",
  "/governance/data-protection-classification": "/governance-and-security/data-protection-and-classification/data-protection-classification",
  "/governance/data-protection": "/governance-and-security/data-protection-and-classification/data-protection",
  "/governance/data-protection/classification": "/governance-and-security/data-protection-and-classification/classification",
  "/governance/data-protection/masking": "/governance-and-security/data-protection-and-classification/masking",
  "/governance/data-protection/tokenization": "/governance-and-security/data-protection-and-classification/tokenization",
  "/governance/data-protection/dlp": "/governance-and-security/data-protection-and-classification/dlp",
  "/governance/data-protection/residency": "/governance-and-security/data-protection-and-classification/residency",
  "/governance/data/overview": "/governance-and-security/data-protection-and-classification/overview",
  "/governance/data/protection": "/governance-and-security/data-protection-and-classification/protection",
  "/governance/data/classification": "/governance-and-security/data-protection-and-classification/classification",
  "/governance/data/residency": "/governance-and-security/data-protection-and-classification/residency",
  "/governance/data/masking": "/governance-and-security/data-protection-and-classification/masking",
  "/governance/data/kms": "/governance-and-security/data-protection-and-classification/kms",
  "/governance/data/todos": "/governance-and-security/data-protection-and-classification/todos",
  "/governance/ai-billing-cost-governance": "/governance-and-security/ai-billing-and-cost-governance/ai-billing-cost-governance",
  "/governance/billing": "/governance-and-security/ai-billing-and-cost-governance/billing",
  "/governance/billing/usage": "/governance-and-security/ai-billing-and-cost-governance/usage",
  "/governance/billing/budgets": "/governance-and-security/ai-billing-and-cost-governance/budgets",
  "/governance/billing/guardrails": "/governance-and-security/ai-billing-and-cost-governance/guardrails",
  "/governance/billing/optimizer": "/governance-and-security/ai-billing-and-cost-governance/optimizer",
  "/governance/billing/chargeback": "/governance-and-security/ai-billing-and-cost-governance/chargeback",
  "/governance/billing/forecasting": "/governance-and-security/ai-billing-and-cost-governance/forecasting",
  "/governance/billing/rates": "/governance-and-security/ai-billing-and-cost-governance/rates",
  "/governance/billing/multi-tenant": "/governance-and-security/ai-billing-and-cost-governance/multi-tenant",
  "/governance/billing/overview": "/governance-and-security/ai-billing-and-cost-governance/overview",
  "/governance/billing/invoicing": "/governance-and-security/ai-billing-and-cost-governance/invoicing",
  "/governance/billing/todos": "/governance-and-security/ai-billing-and-cost-governance/todos",
  "/governance/security-monitoring-response": "/governance-and-security/security-monitoring-and-response/security-monitoring-response",
  "/governance/security/monitoring": "/governance-and-security/security-monitoring-and-response/monitoring",
  "/governance/security/alerts": "/governance-and-security/security-monitoring-and-response/alerts",
  "/governance/security/detection": "/governance-and-security/security-monitoring-and-response/detection",
  "/governance/security/risk": "/governance-and-security/security-monitoring-and-response/risk",
  "/governance/security/alignment": "/governance-and-security/security-monitoring-and-response/alignment",
  "/governance/security/incidents": "/governance-and-security/security-monitoring-and-response/incidents",
  "/governance/security/forensics": "/governance-and-security/security-monitoring-and-response/forensics",
  "/governance/security/vuln": "/governance-and-security/security-monitoring-and-response/vuln",
  "/governance/security/overview": "/governance-and-security/security-monitoring-and-response/overview",
  "/governance/security/abuse": "/governance-and-security/security-monitoring-and-response/abuse",
  "/governance/security/todos": "/governance-and-security/security-monitoring-and-response/todos",
  "/governance/sdlc/overview": "/governance-and-security/secure-development-and-supply-chain/overview",
  "/governance/sdlc/review": "/governance-and-security/secure-development-and-supply-chain/review",
  "/governance/sdlc/sbom": "/governance-and-security/secure-development-and-supply-chain/sbom",
  "/governance/sdlc/env-security": "/governance-and-security/secure-development-and-supply-chain/env-security",
  "/governance/sdlc/provenance": "/governance-and-security/secure-development-and-supply-chain/provenance",
  "/governance/sdlc/todos": "/governance-and-security/secure-development-and-supply-chain/todos",
  "/governance/identity-access": "/governance-and-security/identity-and-access/identity-access",
  "/governance/identity": "/governance-and-security/identity-and-access/identity",
  "/governance/identity/auth": "/governance-and-security/identity-and-access/auth",
  "/governance/identity/sso": "/governance-and-security/identity-and-access/sso",
  "/governance/identity/scim": "/governance-and-security/identity-and-access/scim",
  "/governance/identity/rbac": "/governance-and-security/identity-and-access/rbac",
  "/governance/identity/api-keys": "/governance-and-security/identity-and-access/api-keys",
  "/governance/identity/sessions": "/governance-and-security/identity-and-access/sessions",
  "/governance/identity/reviews": "/governance-and-security/identity-and-access/reviews",
  "/governance/identity/overview": "/governance-and-security/identity-and-access/overview",
  "/governance/identity/roles": "/governance-and-security/identity-and-access/roles",
  "/governance/identity/zero-trust": "/governance-and-security/identity-and-access/zero-trust",
  "/governance/identity/partners": "/governance-and-security/identity-and-access/partners",
  "/governance/identity/todos": "/governance-and-security/identity-and-access/todos",
  "/governance/policy-governance-engine": "/governance-and-security/policy-and-governance-engine/policy-governance-engine",
  "/governance/policy": "/governance-and-security/policy-and-governance-engine/policy",
  "/governance/policy/library": "/governance-and-security/policy-and-governance-engine/library",
  "/governance/policy/dsl": "/governance-and-security/policy-and-governance-engine/dsl",
  "/governance/policy/safety": "/governance-and-security/policy-and-governance-engine/safety",
  "/governance/policy/simulator": "/governance-and-security/policy-and-governance-engine/simulator",
  "/governance/policy/versioning": "/governance-and-security/policy-and-governance-engine/versioning",
  "/governance/policy/enforcement": "/governance-and-security/policy-and-governance-engine/enforcement",
  "/governance/policy/exceptions": "/governance-and-security/policy-and-governance-engine/exceptions",
  "/governance/policy/overview": "/governance-and-security/policy-and-governance-engine/overview",
  "/governance/policy/evaluation": "/governance-and-security/policy-and-governance-engine/evaluation",
  "/governance/policy/packs": "/governance-and-security/policy-and-governance-engine/packs",
  "/governance/policy/workflows": "/governance-and-security/policy-and-governance-engine/workflows",
  "/governance/policy/todos": "/governance-and-security/policy-and-governance-engine/todos",
  "/governance/compliance-regulator-fabric": "/governance-and-security/compliance-and-regulator-fabric/compliance-regulator-fabric",
  "/governance/compliance": "/governance-and-security/compliance-and-regulator-fabric/compliance",
  "/governance/compliance/controls": "/governance-and-security/compliance-and-regulator-fabric/controls",
  "/governance/compliance/readiness": "/governance-and-security/compliance-and-regulator-fabric/readiness",
  "/governance/regulator": "/governance-and-security/compliance-and-regulator-fabric/regulator",
  "/governance/regulator/tenancy": "/governance-and-security/compliance-and-regulator-fabric/tenancy",
  "/governance/regulator/evidence": "/governance-and-security/compliance-and-regulator-fabric/evidence",
  "/governance/regulator/requests": "/governance-and-security/compliance-and-regulator-fabric/requests",
  "/governance/compliance/overview": "/governance-and-security/compliance-and-regulator-fabric/overview",
  "/governance/compliance/packs": "/governance-and-security/compliance-and-regulator-fabric/packs",
  "/governance/compliance/builder": "/governance-and-security/compliance-and-regulator-fabric/builder",
  "/governance/compliance/regulator": "/governance-and-security/compliance-and-regulator-fabric/regulator",
  "/governance/compliance/regulator/tenancy": "/governance-and-security/compliance-and-regulator-fabric/tenancy",
  "/governance/compliance/regulator/evidence": "/governance-and-security/compliance-and-regulator-fabric/evidence",
  "/governance/compliance/reproducibility": "/governance-and-security/compliance-and-regulator-fabric/reproducibility",
  "/governance/compliance/todos": "/governance-and-security/compliance-and-regulator-fabric/todos",
  "/governance/law/overview": "/governance-and-security/law-of-the-os-and-adjudication/overview",
  "/governance/law/policy-vm": "/governance-and-security/law-of-the-os-and-adjudication/policy-vm",
  "/governance/law/court": "/governance-and-security/law-of-the-os-and-adjudication/court",
  "/governance/law/decision-proof-ledger": "/governance-and-security/law-of-the-os-and-adjudication/decision-proof-ledger",
  "/governance/law/treaty": "/governance-and-security/law-of-the-os-and-adjudication/treaty",
  "/governance/law/todos": "/governance-and-security/law-of-the-os-and-adjudication/todos",
  "/drivers/driver-registry-management": "/drivers-and-integrations/driver-registry-and-management/driver-registry-management",
  "/drivers/driver-registry-management/drivers": "/drivers-and-integrations/driver-registry-and-management/drivers",
  "/drivers/registry": "/drivers-and-integrations/driver-registry-and-management/registry",
  "/drivers/sdk": "/drivers-and-integrations/driver-registry-and-management/sdk",
  "/drivers/testing": "/drivers-and-integrations/driver-registry-and-management/testing",
  "/drivers/permissions": "/drivers-and-integrations/driver-registry-and-management/permissions",
  "/drivers/versioning": "/drivers-and-integrations/driver-registry-and-management/versioning",
  "/drivers/analytics": "/drivers-and-integrations/driver-registry-and-management/analytics",
  "/drivers/publishing": "/drivers-and-integrations/driver-registry-and-management/publishing",
  "/drivers/registry/overview": "/drivers-and-integrations/driver-registry-and-management/overview",
  "/drivers/registry/taxonomy": "/drivers-and-integrations/driver-registry-and-management/taxonomy",
  "/drivers/registry/catalog": "/drivers-and-integrations/driver-registry-and-management/catalog",
  "/drivers/registry/details": "/drivers-and-integrations/driver-registry-and-management/details",
  "/drivers/registry/config": "/drivers-and-integrations/driver-registry-and-management/config",
  "/drivers/registry/health": "/drivers-and-integrations/driver-registry-and-management/health",
  "/drivers/registry/sdk": "/drivers-and-integrations/driver-registry-and-management/sdk",
  "/drivers/registry/publishing": "/drivers-and-integrations/driver-registry-and-management/publishing",
  "/drivers/registry/versioning": "/drivers-and-integrations/driver-registry-and-management/versioning",
  "/drivers/registry/todos": "/drivers-and-integrations/driver-registry-and-management/todos",
  "/drivers/connectors-integrations": "/drivers-and-integrations/connectors-and-integrations/connectors-integrations",
  "/drivers/connectors-integrations/connectors": "/drivers-and-integrations/connectors-and-integrations/connectors",
  "/drivers/connectors-integrations/credentials": "/drivers-and-integrations/connectors-and-integrations/credentials",
  "/drivers/connectors-integrations/api-connectors": "/drivers-and-integrations/connectors-and-integrations/api-connectors",
  "/drivers/integrations/productivity": "/drivers-and-integrations/connectors-and-integrations/productivity",
  "/drivers/integrations/code": "/drivers-and-integrations/connectors-and-integrations/code",
  "/drivers/integrations/cloud": "/drivers-and-integrations/connectors-and-integrations/cloud",
  "/drivers/connectors-integrations/office": "/drivers-and-integrations/connectors-and-integrations/office",
  "/drivers/integrations/finance": "/drivers-and-integrations/connectors-and-integrations/finance",
  "/drivers/integrations/research": "/drivers-and-integrations/connectors-and-integrations/research",
  "/drivers/integrations/legacy": "/drivers-and-integrations/connectors-and-integrations/legacy",
  "/drivers/connectors-integrations/webhooks": "/drivers-and-integrations/connectors-and-integrations/webhooks",
  "/drivers/connectors-integrations/mappings": "/drivers-and-integrations/connectors-and-integrations/mappings",
  "/drivers/connectors-integrations/health": "/drivers-and-integrations/connectors-and-integrations/health",
  "/drivers/connectors-integrations/rate-limits": "/drivers-and-integrations/connectors-and-integrations/rate-limits",
  "/drivers/integrations/overview": "/drivers-and-integrations/connectors-and-integrations/overview",
  "/drivers/integrations/api": "/drivers-and-integrations/connectors-and-integrations/api",
  "/drivers/integrations/office": "/drivers-and-integrations/connectors-and-integrations/office",
  "/drivers/integrations/contract-testing": "/drivers-and-integrations/connectors-and-integrations/contract-testing",
  "/drivers/integrations/todos": "/drivers-and-integrations/connectors-and-integrations/todos",
  "/drivers/risk-governance": "/drivers-and-integrations/risk-and-governance/risk-governance",
  "/drivers/risk": "/drivers-and-integrations/risk-and-governance/risk",
  "/drivers/risk/vendors": "/drivers-and-integrations/risk-and-governance/vendors",
  "/drivers/risk/assessments": "/drivers-and-integrations/risk-and-governance/assessments",
  "/drivers/risk/remediation": "/drivers-and-integrations/risk-and-governance/remediation",
  "/drivers/risk/exceptions": "/drivers-and-integrations/risk-and-governance/exceptions",
  "/drivers/risk/overview": "/drivers-and-integrations/risk-and-governance/overview",
  "/drivers/risk/permissions": "/drivers-and-integrations/risk-and-governance/permissions",
  "/drivers/risk/residency": "/drivers-and-integrations/risk-and-governance/residency",
  "/drivers/risk/sandbox": "/drivers-and-integrations/risk-and-governance/sandbox",
  "/drivers/risk/monitoring": "/drivers-and-integrations/risk-and-governance/monitoring",
  "/drivers/risk/todos": "/drivers-and-integrations/risk-and-governance/todos",
  "/drivers/driver-packs-marketplace": "/drivers-and-integrations/driver-packs-and-marketplace/driver-packs-marketplace",
  "/drivers/marketplace": "/drivers-and-integrations/driver-packs-and-marketplace/marketplace",
  "/drivers/marketplace/reviews": "/drivers-and-integrations/driver-packs-and-marketplace/reviews",
  "/drivers/marketplace/security-review": "/drivers-and-integrations/driver-packs-and-marketplace/security-review",
  "/drivers/packs": "/drivers-and-integrations/driver-packs-and-marketplace/packs",
  "/drivers/packs/builder": "/drivers-and-integrations/driver-packs-and-marketplace/builder",
  "/drivers/vertical-editions": "/drivers-and-integrations/driver-packs-and-marketplace/vertical-editions",
  "/drivers/enterprise-store": "/drivers-and-integrations/driver-packs-and-marketplace/enterprise-store",
  "/drivers/licensing": "/drivers-and-integrations/driver-packs-and-marketplace/licensing",
  "/drivers/marketplace/overview": "/drivers-and-integrations/driver-packs-and-marketplace/overview",
  "/drivers/marketplace/packs": "/drivers-and-integrations/driver-packs-and-marketplace/packs",
  "/drivers/marketplace/vertical-editions": "/drivers-and-integrations/driver-packs-and-marketplace/vertical-editions",
  "/drivers/marketplace/enterprise-store": "/drivers-and-integrations/driver-packs-and-marketplace/enterprise-store",
  "/drivers/marketplace/curation": "/drivers-and-integrations/driver-packs-and-marketplace/curation",
  "/drivers/marketplace/certification": "/drivers-and-integrations/driver-packs-and-marketplace/certification",
  "/drivers/marketplace/economics": "/drivers-and-integrations/driver-packs-and-marketplace/economics",
  "/drivers/marketplace/todos": "/drivers-and-integrations/driver-packs-and-marketplace/todos",
  "/dashboard/collaboration/overview": "/mission-control/collaboration-and-federation/overview",
  "/dashboard/collaboration/membership": "/mission-control/collaboration-and-federation/membership",
  "/dashboard/collaboration/shared-views": "/mission-control/collaboration-and-federation/shared-views",
  "/dashboard/collaboration/comments": "/mission-control/collaboration-and-federation/comments",
  "/dashboard/collaboration/pipelines": "/mission-control/collaboration-and-federation/pipelines",
  "/dashboard/collaboration/realtime": "/mission-control/collaboration-and-federation/realtime",
  "/dashboard/collaboration/audit": "/mission-control/collaboration-and-federation/audit",
  "/dashboard/collaboration/run-here": "/mission-control/collaboration-and-federation/run-here",
  "/dashboard/collaboration/my-stack-sharing": "/mission-control/collaboration-and-federation/my-stack-sharing",
  "/dashboard/collaboration/federation": "/mission-control/collaboration-and-federation/federation",
  "/dashboard/collaboration/todos": "/mission-control/collaboration-and-federation/todos",
  "/dashboard/engagement-persona-surfaces": "/mission-control/engagement-and-persona-surfaces/engagement-persona-surfaces",
  "/dashboard/engagement/chat": "/mission-control/engagement-and-persona-surfaces/chat",
  "/dashboard/engagement-persona-surfaces/library": "/mission-control/engagement-and-persona-surfaces/library",
  "/dashboard/engagement/search": "/mission-control/engagement-and-persona-surfaces/search",
  "/dashboard/engagement-persona-surfaces/saved": "/mission-control/engagement-and-persona-surfaces/saved",
  "/dashboard/engagement/collaboration": "/mission-control/engagement-and-persona-surfaces/collaboration",
  "/dashboard/engagement-persona-surfaces/channels": "/mission-control/engagement-and-persona-surfaces/channels",
  "/dashboard/engagement-persona-surfaces/presence": "/mission-control/engagement-and-persona-surfaces/presence",
  "/dashboard/engagement/personalization": "/mission-control/engagement-and-persona-surfaces/personalization",
  "/dashboard/engagement-persona-surfaces/macros": "/mission-control/engagement-and-persona-surfaces/macros",
  "/dashboard/engagement-persona-surfaces/profiles": "/mission-control/engagement-and-persona-surfaces/profiles",
  "/dashboard/engagement/overview": "/mission-control/engagement-and-persona-surfaces/overview",
  "/dashboard/engagement/voice": "/mission-control/engagement-and-persona-surfaces/voice",
  "/dashboard/engagement/cli": "/mission-control/engagement-and-persona-surfaces/cli",
  "/dashboard/engagement/explanations": "/mission-control/engagement-and-persona-surfaces/explanations",
  "/dashboard/engagement/feedback": "/mission-control/engagement-and-persona-surfaces/feedback",
  "/dashboard/core-flight-deck": "/mission-control/core-flight-deck/core-flight-deck",
  "/dashboard/flight-deck": "/mission-control/core-flight-deck/flight-deck",
  "/dashboard/flight-deck/projects": "/mission-control/core-flight-deck/projects",
  "/dashboard/core-flight-deck/templates": "/mission-control/core-flight-deck/templates",
  "/dashboard/core-flight-deck/members": "/mission-control/core-flight-deck/members",
  "/dashboard/core-flight-deck/settings": "/mission-control/core-flight-deck/settings",
  "/dashboard/flight-deck/tasks": "/mission-control/core-flight-deck/tasks",
  "/dashboard/core-flight-deck/board": "/mission-control/core-flight-deck/board",
  "/dashboard/core-flight-deck/automation": "/mission-control/core-flight-deck/automation",
  "/dashboard/core-flight-deck/analytics": "/mission-control/core-flight-deck/analytics",
  "/dashboard/core-flight-deck/activity": "/mission-control/core-flight-deck/activity",
  "/dashboard/core-flight-deck/notifications": "/mission-control/core-flight-deck/notifications",
  "/dashboard/core-flight-deck/inbox": "/mission-control/core-flight-deck/inbox",
  "/dashboard/core-flight-deck/timeline": "/mission-control/core-flight-deck/timeline",
  "/dashboard/flight-deck/overview": "/mission-control/core-flight-deck/overview",
  "/dashboard/flight-deck/dashboard": "/mission-control/core-flight-deck/dashboard",
  "/dashboard/flight-deck/master-stack": "/mission-control/core-flight-deck/master-stack",
  "/dashboard/flight-deck/approvals": "/mission-control/core-flight-deck/approvals",
  "/dashboard/flight-deck/timeline": "/mission-control/core-flight-deck/timeline",
  "/dashboard/flight-deck/quick-actions": "/mission-control/core-flight-deck/quick-actions",
  "/dashboard/flight-deck/status": "/mission-control/core-flight-deck/status",
  "/ai/cognitive-agents-reasoning": "/ai-fabric/cognitive-agents-and-reasoning/cognitive-agents-reasoning",
  "/ai/copilot": "/ai-fabric/cognitive-agents-and-reasoning/copilot",
  "/ai-fabric/cognitive-agents-reasoning/personas": "/ai-fabric/cognitive-agents-and-reasoning/personas",
  "/ai/prompts": "/ai-fabric/cognitive-agents-and-reasoning/prompts",
  "/ai/project-intelligence": "/ai-fabric/cognitive-agents-and-reasoning/project-intelligence",
  "/ai/evals": "/ai-fabric/cognitive-agents-and-reasoning/evals",
  "/ai/routing": "/ai-fabric/cognitive-agents-and-reasoning/routing",
  "/ai/advanced": "/ai-fabric/cognitive-agents-and-reasoning/advanced",
  "/ai/daemons": "/ai-fabric/cognitive-agents-and-reasoning/daemons",
  "/ai/trf": "/ai-fabric/cognitive-agents-and-reasoning/trf",
  "/ai/safety": "/ai-fabric/cognitive-agents-and-reasoning/safety",
  "/ai/agents/registry": "/ai-fabric/cognitive-agents-and-reasoning/registry",
  "/ai/agents/overview": "/ai-fabric/cognitive-agents-and-reasoning/overview",
  "/ai/agents/copilot": "/ai-fabric/cognitive-agents-and-reasoning/copilot",
  "/ai/agents/advanced": "/ai-fabric/cognitive-agents-and-reasoning/advanced",
  "/ai/agents/personas": "/ai-fabric/cognitive-agents-and-reasoning/personas",
  "/ai/agents/daemons": "/ai-fabric/cognitive-agents-and-reasoning/daemons",
  "/ai/agents/project-intelligence": "/ai-fabric/cognitive-agents-and-reasoning/project-intelligence",
  "/ai/agents/trf": "/ai-fabric/cognitive-agents-and-reasoning/trf",
  "/ai/agents/traces": "/ai-fabric/cognitive-agents-and-reasoning/traces",
  "/ai/agents/safety": "/ai-fabric/cognitive-agents-and-reasoning/safety",
  "/ai/agents/time": "/ai-fabric/cognitive-agents-and-reasoning/time",
  "/ai/agents/todos": "/ai-fabric/cognitive-agents-and-reasoning/todos",
  "/ai/driver-fabric-system-execution": "/ai-fabric/driver-fabric-and-system-execution/driver-fabric-system-execution",
  "/ai/os": "/ai-fabric/driver-fabric-and-system-execution/os",
  "/ai/operations": "/ai-fabric/driver-fabric-and-system-execution/operations",
  "/ai/drivers": "/ai-fabric/driver-fabric-and-system-execution/drivers",
  "/ai/drivers/testing": "/ai-fabric/driver-fabric-and-system-execution/testing",
  "/ai/drivers/health": "/ai-fabric/driver-fabric-and-system-execution/health",
  "/ai/drivers/permissions": "/ai-fabric/driver-fabric-and-system-execution/permissions",
  "/ai/drivers/versioning": "/ai-fabric/driver-fabric-and-system-execution/versioning",
  "/ai/drivers/os": "/ai-fabric/driver-fabric-and-system-execution/os",
  "/ai/drivers/package": "/ai-fabric/driver-fabric-and-system-execution/package",
  "/ai/drivers/hardware": "/ai-fabric/driver-fabric-and-system-execution/hardware",
  "/ai/drivers/software": "/ai-fabric/driver-fabric-and-system-execution/software",
  "/ai/drivers/data": "/ai-fabric/driver-fabric-and-system-execution/data",
  "/ai/drivers/research": "/ai-fabric/driver-fabric-and-system-execution/research",
  "/ai/drivers/sandbox": "/ai-fabric/driver-fabric-and-system-execution/sandbox",
  "/ai/execution/overview": "/ai-fabric/driver-fabric-and-system-execution/overview",
  "/ai/execution/operations": "/ai-fabric/driver-fabric-and-system-execution/operations",
  "/ai/execution/os-control": "/ai-fabric/driver-fabric-and-system-execution/os-control",
  "/ai/execution/driver-registry": "/ai-fabric/driver-fabric-and-system-execution/driver-registry",
  "/ai/execution/drivers/os": "/ai-fabric/driver-fabric-and-system-execution/os",
  "/ai/execution/drivers/package": "/ai-fabric/driver-fabric-and-system-execution/package",
  "/ai/execution/drivers/hardware": "/ai-fabric/driver-fabric-and-system-execution/hardware",
  "/ai/execution/drivers/software": "/ai-fabric/driver-fabric-and-system-execution/software",
  "/ai/execution/drivers/data": "/ai-fabric/driver-fabric-and-system-execution/data",
  "/ai/execution/drivers/workflow": "/ai-fabric/driver-fabric-and-system-execution/workflow",
  "/ai/execution/drivers/governance": "/ai-fabric/driver-fabric-and-system-execution/governance",
  "/ai/execution/drivers/research": "/ai-fabric/driver-fabric-and-system-execution/research",
  "/ai/execution/sandbox": "/ai-fabric/driver-fabric-and-system-execution/sandbox",
  "/ai/execution/scheduling": "/ai-fabric/driver-fabric-and-system-execution/scheduling",
  "/ai/execution/failures": "/ai-fabric/driver-fabric-and-system-execution/failures",
  "/ai/execution/todos": "/ai-fabric/driver-fabric-and-system-execution/todos",
  "/ai/edge-vision": "/ai-fabric/edge-and-vision/edge-vision",
  "/ai/edge": "/ai-fabric/edge-and-vision/edge",
  "/ai/edge/devices": "/ai-fabric/edge-and-vision/devices",
  "/ai/edge/deploy": "/ai-fabric/edge-and-vision/deploy",
  "/ai/vision": "/ai-fabric/edge-and-vision/vision",
  "/ai/vision/streams": "/ai-fabric/edge-and-vision/streams",
  "/ai/vision/pipelines": "/ai-fabric/edge-and-vision/pipelines",
  "/ai/vision/labeling": "/ai-fabric/edge-and-vision/labeling",
  "/ai/edge/overview": "/ai-fabric/edge-and-vision/overview",
  "/ai/edge/compute": "/ai-fabric/edge-and-vision/compute",
  "/ai/edge/vision": "/ai-fabric/edge-and-vision/vision",
  "/ai/edge/deployment": "/ai-fabric/edge-and-vision/deployment",
  "/ai/edge/observability": "/ai-fabric/edge-and-vision/observability",
  "/ai/edge/todos": "/ai-fabric/edge-and-vision/todos",
  "/ai/capsules-workflow-automation": "/ai-fabric/capsules-and-workflow-automation/capsules-workflow-automation",
  "/ai/workflows": "/ai-fabric/capsules-and-workflow-automation/workflows",
  "/ai/workflows/triggers": "/ai-fabric/capsules-and-workflow-automation/triggers",
  "/ai/workflows/observability": "/ai-fabric/capsules-and-workflow-automation/observability",
  "/ai/capsules/builder": "/ai-fabric/capsules-and-workflow-automation/builder",
  "/ai/capsules/templates": "/ai-fabric/capsules-and-workflow-automation/templates",
  "/ai/capsules/my-stack": "/ai-fabric/capsules-and-workflow-automation/my-stack",
  "/ai/capsules/runtime": "/ai-fabric/capsules-and-workflow-automation/runtime",
  "/ai/capsules/secrets": "/ai-fabric/capsules-and-workflow-automation/secrets",
  "/ai/capsules": "/ai-fabric/capsules-and-workflow-automation/capsules",
  "/ai/capsules/publishing": "/ai-fabric/capsules-and-workflow-automation/publishing",
  "/ai/capsules/operator-studio": "/ai-fabric/capsules-and-workflow-automation/operator-studio",
  "/ai/autofix": "/ai-fabric/capsules-and-workflow-automation/autofix",
  "/ai/capsules/ledger": "/ai-fabric/capsules-and-workflow-automation/ledger",
  "/ai/capsules/lineage": "/ai-fabric/capsules-and-workflow-automation/lineage",
  "/ai/capsules/overview": "/ai-fabric/capsules-and-workflow-automation/overview",
  "/ai/capsules/taxonomy": "/ai-fabric/capsules-and-workflow-automation/taxonomy",
  "/ai/capsules/manifests": "/ai-fabric/capsules-and-workflow-automation/manifests",
  "/ai/capsules/lifecycle": "/ai-fabric/capsules-and-workflow-automation/lifecycle",
  "/ai/capsules/dependencies": "/ai-fabric/capsules-and-workflow-automation/dependencies",
  "/ai/capsules/workflows": "/ai-fabric/capsules-and-workflow-automation/workflows",
  "/ai/capsules/library": "/ai-fabric/capsules-and-workflow-automation/library",
  "/ai/capsules/evidence-packs": "/ai-fabric/capsules-and-workflow-automation/evidence-packs",
  "/ai/capsules/autofix": "/ai-fabric/capsules-and-workflow-automation/autofix",
  "/ai/capsules/marketplace": "/ai-fabric/capsules-and-workflow-automation/marketplace",
  "/ai/capsules/governance": "/ai-fabric/capsules-and-workflow-automation/governance",
  "/ai/capsules/collaboration": "/ai-fabric/capsules-and-workflow-automation/collaboration",
  "/ai/capsules/self-evolving": "/ai-fabric/capsules-and-workflow-automation/self-evolving",
  "/ai/capsules/todos": "/ai-fabric/capsules-and-workflow-automation/todos",
  "/ai/mlops-neural-architecture": "/ai-fabric/mlops-and-neural-architecture/mlops-neural-architecture",
  "/ai/mlops": "/ai-fabric/mlops-and-neural-architecture/mlops",
  "/ai/mlops/models": "/ai-fabric/mlops-and-neural-architecture/models",
  "/ai/mlops/data": "/ai-fabric/mlops-and-neural-architecture/data",
  "/ai/mlops/pipelines": "/ai-fabric/mlops-and-neural-architecture/pipelines",
  "/ai/mlops/serving": "/ai-fabric/mlops-and-neural-architecture/serving",
  "/ai/mlops/drift": "/ai-fabric/mlops-and-neural-architecture/drift",
  "/ai/mlops/approvals": "/ai-fabric/mlops-and-neural-architecture/approvals",
  "/ai/nas": "/ai-fabric/mlops-and-neural-architecture/nas",
  "/ai/nas/experiments": "/ai-fabric/mlops-and-neural-architecture/experiments",
  "/ai/nas/simulator": "/ai-fabric/mlops-and-neural-architecture/simulator",
  "/ai/mlops/overview": "/ai-fabric/mlops-and-neural-architecture/overview",
  "/ai/mlops/experiments": "/ai-fabric/mlops-and-neural-architecture/experiments",
  "/ai/mlops/training": "/ai-fabric/mlops-and-neural-architecture/training",
  "/ai/mlops/evaluation": "/ai-fabric/mlops-and-neural-architecture/evaluation",
  "/ai/mlops/nas": "/ai-fabric/mlops-and-neural-architecture/nas",
  "/ai/mlops/nas/experiments": "/ai-fabric/mlops-and-neural-architecture/experiments",
  "/ai/mlops/nas/simulator": "/ai-fabric/mlops-and-neural-architecture/simulator",
  "/ai/mlops/todos": "/ai-fabric/mlops-and-neural-architecture/todos",
  "/ai/intent-processing": "/ai-fabric/intent-processing/intent-processing",
  "/ai/intents": "/ai-fabric/intent-processing/intents",
  "/ai/intents/taxonomy": "/ai-fabric/intent-processing/taxonomy",
  "/ai/intents/logs": "/ai-fabric/intent-processing/logs",
  "/ai/systems": "/ai-fabric/intent-processing/systems",
  "/ai/systems/graph": "/ai-fabric/intent-processing/graph",
  "/ai/capabilities": "/ai-fabric/intent-processing/capabilities",
  "/ai/intent/overview": "/ai-fabric/intent-processing/overview",
  "/ai/intent/processor": "/ai-fabric/intent-processing/processor",
  "/ai/intent/context": "/ai-fabric/intent-processing/context",
  "/ai/intent/planning-loop": "/ai-fabric/intent-processing/planning-loop",
  "/ai/intent/approvals": "/ai-fabric/intent-processing/approvals",
  "/ai/intent/systems-map": "/ai-fabric/intent-processing/systems-map",
  "/ai/intent/errors": "/ai-fabric/intent-processing/errors",
  "/ai/intent/todos": "/ai-fabric/intent-processing/todos",
  "/docs/api-reference": "/docs-and-spec/api-reference/api-reference",
  "/docs/api": "/docs-and-spec/api-reference/api",
  "/docs/api/sdks": "/docs-and-spec/api-reference/sdks",
  "/docs/api/auth": "/docs-and-spec/api-reference/auth",
  "/docs/api/webhooks": "/docs-and-spec/api-reference/webhooks",
  "/docs/api/overview": "/docs-and-spec/api-reference/overview",
  "/docs/api/model-provider": "/docs-and-spec/api-reference/model-provider",
  "/docs/api/drivers": "/docs-and-spec/api-reference/drivers",
  "/docs/api/capsules": "/docs-and-spec/api-reference/capsules",
  "/docs/api/governance": "/docs-and-spec/api-reference/governance",
  "/docs/api/billing": "/docs-and-spec/api-reference/billing",
  "/docs/api/federation": "/docs-and-spec/api-reference/federation",
  "/docs/reference-artifacts": "/docs-and-spec/reference-artifacts/reference-artifacts",
  "/docs/reference/capsules": "/docs-and-spec/reference-artifacts/capsules",
  "/docs/reference/drivers": "/docs-and-spec/reference-artifacts/drivers",
  "/docs/reference/policies": "/docs-and-spec/reference-artifacts/policies",
  "/docs/reference/evidence": "/docs-and-spec/reference-artifacts/evidence",
  "/docs/reference/data": "/docs-and-spec/reference-artifacts/data",
  "/docs/reference/ui": "/docs-and-spec/reference-artifacts/ui",
  "/docs/reference/overview": "/docs-and-spec/reference-artifacts/overview",
  "/docs/reference/diagrams": "/docs-and-spec/reference-artifacts/diagrams",
  "/docs/reference/conformance": "/docs-and-spec/reference-artifacts/conformance",
  "/docs/glossary/overview": "/docs-and-spec/glossary-and-definitions/overview",
  "/docs/glossary/terms": "/docs-and-spec/glossary-and-definitions/terms",
  "/docs/glossary/notation": "/docs-and-spec/glossary-and-definitions/notation",
  "/docs/changelog/overview": "/docs-and-spec/changelog-and-versioning/overview",
  "/docs/changelog/spec-timeline": "/docs-and-spec/changelog-and-versioning/spec-timeline",
  "/docs/changelog/design-shifts": "/docs-and-spec/changelog-and-versioning/design-shifts",
  "/docs/changelog/deprecations": "/docs-and-spec/changelog-and-versioning/deprecations",
  "/docs/documentation-hub": "/docs-and-spec/documentation-hub/documentation-hub",
  "/docs/documentation-hub/docs": "/docs-and-spec/documentation-hub/docs",
  "/docs/getting-started": "/docs-and-spec/documentation-hub/getting-started",
  "/docs/tutorials": "/docs-and-spec/documentation-hub/tutorials",
  "/docs/glossary": "/docs-and-spec/documentation-hub/glossary",
  "/docs/spec-sheet": "/docs-and-spec/documentation-hub/spec-sheet",
  "/docs/release-notes": "/docs-and-spec/documentation-hub/release-notes",
  "/docs/hub/overview": "/docs-and-spec/documentation-hub/overview",
  "/docs/hub/spec-sheet": "/docs-and-spec/documentation-hub/spec-sheet",
  "/docs/hub/canon-mapping": "/docs-and-spec/documentation-hub/canon-mapping",
  "/docs/hub/open-questions": "/docs-and-spec/documentation-hub/open-questions",
  "/docs/hub/todos": "/docs-and-spec/documentation-hub/todos",
  "/docs/migration-integration": "/docs-and-spec/migration-and-integration/migration-integration",
  "/docs/migration_continued.md": "/docs-and-spec/migration-and-integration/migration_continued.md",
  "/docs/migration": "/docs-and-spec/migration-and-integration/migration",
  "/docs/integrations": "/docs-and-spec/migration-and-integration/integrations",
  "/docs/deployment": "/docs-and-spec/migration-and-integration/deployment",
  "/docs/migration/overview": "/docs-and-spec/migration-and-integration/overview",
  "/docs/migration/saas-to-drivers": "/docs-and-spec/migration-and-integration/saas-to-drivers",
  "/docs/migration/research-unification": "/docs-and-spec/migration-and-integration/research-unification",
  "/docs/migration/security-adoption": "/docs-and-spec/migration-and-integration/security-adoption",
  "/docs/migration/legacy-bridge": "/docs-and-spec/migration-and-integration/legacy-bridge",
  "/docs/migration/continued": "/docs-and-spec/migration-and-integration/continued",
  "/docs/migration/todos": "/docs-and-spec/migration-and-integration/todos",
  "/settings-admin/billing-usage/overview": "/settings-and-admin/billing-and-usage/overview",
  "/settings-admin/billing-usage/plan": "/settings-and-admin/billing-and-usage/plan",
  "/settings-admin/billing-usage/usage": "/settings-and-admin/billing-and-usage/usage",
  "/settings-admin/billing-usage/budgets": "/settings-and-admin/billing-and-usage/budgets",
  "/settings-admin/billing-usage/payment": "/settings-and-admin/billing-and-usage/payment",
  "/settings-admin/workspace-settings/overview": "/settings-and-admin/workspace-settings/overview",
  "/settings-admin/workspace-settings/manage": "/settings-and-admin/workspace-settings/manage",
  "/settings-admin/workspace-settings/defaults": "/settings-and-admin/workspace-settings/defaults",
  "/settings-admin/workspace-settings/environment-profiles": "/settings-and-admin/workspace-settings/environment-profiles",
  "/settings-admin/system-diagnostics/overview": "/settings-and-admin/system-diagnostics/overview",
  "/settings-admin/system-diagnostics/health": "/settings-and-admin/system-diagnostics/health",
  "/settings-admin/system-diagnostics/support-bundle": "/settings-and-admin/system-diagnostics/support-bundle",
  "/settings-admin/system-diagnostics/version": "/settings-and-admin/system-diagnostics/version",
  "/settings/user-tenant-settings": "/settings-and-admin/user-and-tenant-settings/user-tenant-settings",
  "/settings/user-tenant-settings/settings": "/settings-and-admin/user-and-tenant-settings/settings",
  "/settings/profile": "/settings-and-admin/user-and-tenant-settings/profile",
  "/settings/preferences": "/settings-and-admin/user-and-tenant-settings/preferences",
  "/settings/notifications": "/settings-and-admin/user-and-tenant-settings/notifications",
  "/settings/credentials": "/settings-and-admin/user-and-tenant-settings/credentials",
  "/settings/api-keys": "/settings-and-admin/user-and-tenant-settings/api-keys",
  "/settings-admin/feature-flags-labs/overview": "/settings-and-admin/feature-flags-and-labs/overview",
  "/settings-admin/feature-flags-labs/feature-flags": "/settings-and-admin/feature-flags-and-labs/feature-flags",
  "/settings-admin/feature-flags-labs/model-providers": "/settings-and-admin/feature-flags-and-labs/model-providers",
  "/settings-admin/user-profile-preferences/overview": "/settings-and-admin/user-profile-and-preferences/overview",
  "/settings-admin/user-profile-preferences/profile": "/settings-and-admin/user-profile-and-preferences/profile",
  "/settings-admin/user-profile-preferences/personas": "/settings-and-admin/user-profile-and-preferences/personas",
  "/settings-admin/user-profile-preferences/notifications": "/settings-and-admin/user-profile-and-preferences/notifications",
  "/settings-admin/user-profile-preferences/ui": "/settings-and-admin/user-profile-and-preferences/ui",
  "/settings-admin/user-profile-preferences/export": "/settings-and-admin/user-profile-and-preferences/export",
  "/settings-admin/security-privacy/overview": "/settings-and-admin/security-and-privacy/overview",
  "/settings-admin/security-privacy/auth": "/settings-and-admin/security-and-privacy/auth",
  "/settings-admin/security-privacy/devices": "/settings-and-admin/security-and-privacy/devices",
  "/settings-admin/security-privacy/privacy": "/settings-and-admin/security-and-privacy/privacy",
  "/settings-admin/security-privacy/keys": "/settings-and-admin/security-and-privacy/keys",
  "/settings-admin/tenant-org-admin/overview": "/settings-and-admin/tenant-and-org-admin/overview",
  "/settings-admin/tenant-org-admin/sso": "/settings-and-admin/tenant-and-org-admin/sso",
  "/settings-admin/tenant-org-admin/rbac": "/settings-and-admin/tenant-and-org-admin/rbac",
  "/settings-admin/tenant-org-admin/compliance": "/settings-and-admin/tenant-and-org-admin/compliance",
  "/settings-admin/tenant-org-admin/residency": "/settings-and-admin/tenant-and-org-admin/residency",
  "/settings-admin/tenant-org-admin/billing": "/settings-and-admin/tenant-and-org-admin/billing",
  "/settings-admin/integrations-credentials/overview": "/settings-and-admin/integrations-and-credentials/overview",
  "/settings-admin/integrations-credentials/connected-apps": "/settings-and-admin/integrations-and-credentials/connected-apps",
  "/settings-admin/integrations-credentials/credentials": "/settings-and-admin/integrations-and-credentials/credentials",
  "/settings-admin/integrations-credentials/permissions": "/settings-and-admin/integrations-and-credentials/permissions",
  "/settings-admin/integrations-credentials/rotation": "/settings-and-admin/integrations-and-credentials/rotation",
  "/data/indices-search": "/data-and-knowledge/indices-and-search/indices-search",
  "/data/indices": "/data-and-knowledge/indices-and-search/indices",
  "/data/indices/manage": "/data-and-knowledge/indices-and-search/manage",
  "/data/indices/fulltext": "/data-and-knowledge/indices-and-search/fulltext",
  "/data/indices/semantic": "/data-and-knowledge/indices-and-search/semantic",
  "/data/indices/embeddings": "/data-and-knowledge/indices-and-search/embeddings",
  "/data/indices/graph": "/data-and-knowledge/indices-and-search/graph",
  "/data/indices/tuning": "/data-and-knowledge/indices-and-search/tuning",
  "/data/query": "/data-and-knowledge/indices-and-search/query",
  "/data/indices/overview": "/data-and-knowledge/indices-and-search/overview",
  "/data/indices/ranking": "/data-and-knowledge/indices-and-search/ranking",
  "/data/indices/maintenance": "/data-and-knowledge/indices-and-search/maintenance",
  "/data/indices/todos": "/data-and-knowledge/indices-and-search/todos",
  "/data/data-protection": "/data-and-knowledge/data-protection/data-protection",
  "/data/encryption": "/data-and-knowledge/data-protection/encryption",
  "/data/encryption/rotation": "/data-and-knowledge/data-protection/rotation",
  "/data/integrity": "/data-and-knowledge/data-protection/integrity",
  "/data/protection/overview": "/data-and-knowledge/data-protection/overview",
  "/data/protection/encryption": "/data-and-knowledge/data-protection/encryption",
  "/data/protection/integrity": "/data-and-knowledge/data-protection/integrity",
  "/data/protection/secrets": "/data-and-knowledge/data-protection/secrets",
  "/data/protection/classification": "/data-and-knowledge/data-protection/classification",
  "/data/protection/todos": "/data-and-knowledge/data-protection/todos",
  "/data/replication-dr": "/data-and-knowledge/replication-and-dr/replication-dr",
  "/data/replication": "/data-and-knowledge/replication-and-dr/replication",
  "/data/consistency": "/data-and-knowledge/replication-and-dr/consistency",
  "/data/dr/failover": "/data-and-knowledge/replication-and-dr/failover",
  "/data/dr/drills": "/data-and-knowledge/replication-and-dr/drills",
  "/data/dr/overview": "/data-and-knowledge/replication-and-dr/overview",
  "/data/dr/replication": "/data-and-knowledge/replication-and-dr/replication",
  "/data/dr/consistency": "/data-and-knowledge/replication-and-dr/consistency",
  "/data/dr/todos": "/data-and-knowledge/replication-and-dr/todos",
  "/data/archive-retention": "/data-and-knowledge/archive-and-retention/archive-retention",
  "/data/archive": "/data-and-knowledge/archive-and-retention/archive",
  "/data/backup": "/data-and-knowledge/archive-and-retention/backup",
  "/data/retention/policies": "/data-and-knowledge/archive-and-retention/policies",
  "/data/legal-hold": "/data-and-knowledge/archive-and-retention/legal-hold",
  "/data/restore-testing": "/data-and-knowledge/archive-and-retention/restore-testing",
  "/data/archive/overview": "/data-and-knowledge/archive-and-retention/overview",
  "/data/archive/archive": "/data-and-knowledge/archive-and-retention/archive",
  "/data/archive/backup": "/data-and-knowledge/archive-and-retention/backup",
  "/data/archive/legal-hold": "/data-and-knowledge/archive-and-retention/legal-hold",
  "/data/archive/time-travel": "/data-and-knowledge/archive-and-retention/time-travel",
  "/data/archive/todos": "/data-and-knowledge/archive-and-retention/todos",
  "/data/observability-stores": "/data-and-knowledge/observability-stores/observability-stores",
  "/data/observability": "/data-and-knowledge/observability-stores/observability",
  "/data/metrics": "/data-and-knowledge/observability-stores/metrics",
  "/data/logs": "/data-and-knowledge/observability-stores/logs",
  "/data/traces": "/data-and-knowledge/observability-stores/traces",
  "/data/observability/tiering": "/data-and-knowledge/observability-stores/tiering",
  "/data/observability/export": "/data-and-knowledge/observability-stores/export",
  "/data/telemetry-stores/overview": "/data-and-knowledge/observability-stores/overview",
  "/data/telemetry-stores/metrics": "/data-and-knowledge/observability-stores/metrics",
  "/data/telemetry-stores/logs": "/data-and-knowledge/observability-stores/logs",
  "/data/telemetry-stores/traces": "/data-and-knowledge/observability-stores/traces",
  "/data/telemetry-stores/policies": "/data-and-knowledge/observability-stores/policies",
  "/data/telemetry-stores/todos": "/data-and-knowledge/observability-stores/todos",
  "/data/core-data-stores": "/data-and-knowledge/core-data-stores/core-data-stores",
  "/data/core-data-stores/data": "/data-and-knowledge/core-data-stores/data",
  "/data/cir": "/data-and-knowledge/core-data-stores/cir",
  "/data/capsules": "/data-and-knowledge/core-data-stores/capsules",
  "/data/ledger": "/data-and-knowledge/core-data-stores/ledger",
  "/data/artifacts": "/data-and-knowledge/core-data-stores/artifacts",
  "/data/schema": "/data-and-knowledge/core-data-stores/schema",
  "/data/ingestion": "/data-and-knowledge/core-data-stores/ingestion",
  "/data/lineage": "/data-and-knowledge/core-data-stores/lineage",
  "/data/quality": "/data-and-knowledge/core-data-stores/quality",
  "/data/stores/overview": "/data-and-knowledge/core-data-stores/overview",
  "/data/stores/cir": "/data-and-knowledge/core-data-stores/cir",
  "/data/stores/ledger": "/data-and-knowledge/core-data-stores/ledger",
  "/data/stores/capsules": "/data-and-knowledge/core-data-stores/capsules",
  "/data/stores/artifacts": "/data-and-knowledge/core-data-stores/artifacts",
  "/data/stores/knowledge-capsules": "/data-and-knowledge/core-data-stores/knowledge-capsules",
  "/data/stores/todos": "/data-and-knowledge/core-data-stores/todos"
}

const allowsActorScope = (itemScope: ActorScope | undefined, actorScope: ActorScope) => {
  if (!itemScope) return true
  if (itemScope === 'both' || itemScope === actorScope) return true
  if (actorScope === 'enterprise' && itemScope === 'personal') return true
  return false
}

export function getPlatforms(actorScope: ActorScope): IAPlatform[] {
  return iaManifest.filter(p => allowsActorScope(p.actorScope, actorScope))
}

export function getCategories(platformId: string, actorScope: ActorScope): IACategory[] {
  const platform = iaManifest.find(p => p.id === platformId)
  if (!platform) return []
  if (!allowsActorScope(platform.actorScope, actorScope)) return []
  return platform.categories.filter(c => allowsActorScope(c.actorScope, actorScope))
}

export function getFeatures(platformId: string, categoryId: string, actorScope: ActorScope): IAFeature[] {
  const platform = iaManifest.find(p => p.id === platformId)
  if (!platform) return []
  const category = platform.categories.find(c => c.id === categoryId)
  if (!category) return []
  if (!allowsActorScope(category.actorScope, actorScope)) return []
  return category.features.filter(f => allowsActorScope(f.actorScope, actorScope))
}

export function findRouteContext(route: string): {
  platform?: IAPlatform
  category?: IACategory
  feature?: IAFeature
  isCategoryHome: boolean
  isPlatformLanding: boolean
} {
  const normalized = route === '/' ? '/' : route.replace(/\/+$/, '')
  for (const platform of iaManifest) {
    if (normalized === platform.path) {
      return {
        platform,
        isCategoryHome: false,
        isPlatformLanding: true,
      }
    }
  }
  for (const platform of iaManifest) {
    for (const category of platform.categories) {
      if (normalized === category.homeRoute) {
        return {
          platform,
          category,
          isCategoryHome: true,
          isPlatformLanding: false,
        }
      }

      for (const feature of category.features) {
        if (normalized === feature.route || normalized.startsWith(feature.route + '/')) {
          return {
            platform,
            category,
            feature,
            isCategoryHome: false,
            isPlatformLanding: false,
          }
        }
      }
    }
  }

  return { isCategoryHome: false, isPlatformLanding: false }
}
