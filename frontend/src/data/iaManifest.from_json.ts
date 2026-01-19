/**
 * Complete IA Manifest - Generated from gui_nav.latest.json
 * Single Source of Truth for UI navigation
 */

export type ActorScope = 'personal' | 'business' | 'enterprise' | 'both'

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
    "id": "core",
    "label": "Core",
    "path": "/dashboard",
    "actorScope": "both",
    "order": 1,
    "categories": [
      {
        "id": "core-core-flight-deck",
        "label": "Core Flight Deck",
        "homeRoute": "/dashboard/core-flight-deck",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "core-core-flight-deck-projects",
            "label": "Projects",
            "route": "/dashboard/flight-deck/projects",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-tasks",
            "label": "Tasks",
            "route": "/dashboard/flight-deck/tasks",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-dashboard",
            "label": "Dashboard",
            "route": "/dashboard/flight-deck",
            "componentPath": "frontend/src/pages/Dashboard.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-core-flight-deck",
            "label": "Core Flight Deck",
            "route": "/dashboard/core-flight-deck",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-project-templates",
            "label": "Project Templates",
            "route": "/dashboard/core-flight-deck/templates",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-project-members-and-roles",
            "label": "Project Members & Roles",
            "route": "/dashboard/core-flight-deck/members",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-project-settings",
            "label": "Project Settings",
            "route": "/dashboard/core-flight-deck/settings",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-task-board-kanban",
            "label": "Task Board (Kanban)",
            "route": "/dashboard/core-flight-deck/board",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-task-automation-and-rules",
            "label": "Task Automation & Rules",
            "route": "/dashboard/core-flight-deck/automation",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-task-analytics",
            "label": "Task Analytics",
            "route": "/dashboard/core-flight-deck/analytics",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-activity-feed",
            "label": "Activity Feed",
            "route": "/dashboard/core-flight-deck/activity",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-notifications-center",
            "label": "Notifications Center",
            "route": "/dashboard/core-flight-deck/notifications",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 12,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-work-queue-inbox",
            "label": "Work Queue / Inbox",
            "route": "/dashboard/core-flight-deck/inbox",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 13,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-calendar-timeline",
            "label": "Calendar / Timeline",
            "route": "/dashboard/core-flight-deck/timeline",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 14,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-projects",
            "label": "Projects",
            "route": "/projects",
            "componentPath": "frontend/src/pages/Projects.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 15,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-project-templates",
            "label": "Project Templates",
            "route": "/projects/templates",
            "componentPath": "frontend/src/pages/projects/Templates.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 16,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-project-members-and-roles",
            "label": "Project Members & Roles",
            "route": "/projects/members",
            "componentPath": "frontend/src/pages/projects/Members.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 17,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-project-settings",
            "label": "Project Settings",
            "route": "/projects/settings",
            "componentPath": "frontend/src/pages/projects/Settings.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 18,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-tasks",
            "label": "Tasks",
            "route": "/tasks",
            "componentPath": "frontend/src/pages/Tasks.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 19,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-task-board-kanban",
            "label": "Task Board (Kanban)",
            "route": "/tasks/board",
            "componentPath": "frontend/src/pages/tasks/Board.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 20,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-task-automation-and-rules",
            "label": "Task Automation & Rules",
            "route": "/tasks/automation",
            "componentPath": "frontend/src/pages/tasks/Automation.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 21,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-task-analytics",
            "label": "Task Analytics",
            "route": "/tasks/analytics",
            "componentPath": "frontend/src/pages/tasks/Analytics.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 22,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-activity-feed",
            "label": "Activity Feed",
            "route": "/activity",
            "componentPath": "frontend/src/pages/Activity.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 23,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-notifications-center",
            "label": "Notifications Center",
            "route": "/notifications",
            "componentPath": "frontend/src/pages/Notifications.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 24,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-work-queue-inbox",
            "label": "Work Queue / Inbox",
            "route": "/inbox",
            "componentPath": "frontend/src/pages/Inbox.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 25,
            "isNew": false
          },
          {
            "id": "core-core-flight-deck-calendar-timeline",
            "label": "Calendar / Timeline",
            "route": "/timeline",
            "componentPath": "frontend/src/pages/Timeline.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 26,
            "isNew": false
          }
        ]
      },
      {
        "id": "core-engagement-and-persona-surfaces",
        "label": "Engagement & Persona Surfaces",
        "homeRoute": "/dashboard/engagement-and-persona-surfaces",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "core-engagement-and-persona-surfaces-chat",
            "label": "Chat",
            "route": "/dashboard/engagement/chat",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-collaboration",
            "label": "Collaboration",
            "route": "/dashboard/engagement/collaboration",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-personalization",
            "label": "Personalization",
            "route": "/dashboard/engagement/personalization",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-search-and-discovery",
            "label": "Search & Discovery",
            "route": "/dashboard/engagement/search",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-engagement-and-persona-surfaces",
            "label": "Engagement & Persona Surfaces",
            "route": "/dashboard/engagement-persona-surfaces",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-conversation-library",
            "label": "Conversation Library",
            "route": "/dashboard/engagement-persona-surfaces/library",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-saved-searches-and-alerts",
            "label": "Saved Searches & Alerts",
            "route": "/dashboard/engagement-persona-surfaces/saved",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-shared-spaces-channels",
            "label": "Shared Spaces / Channels",
            "route": "/dashboard/engagement-persona-surfaces/channels",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-mentions-and-presence",
            "label": "Mentions & Presence",
            "route": "/dashboard/engagement-persona-surfaces/presence",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-prompt-macro-library",
            "label": "Prompt / Macro Library",
            "route": "/dashboard/engagement-persona-surfaces/macros",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-preference-profiles",
            "label": "Preference Profiles",
            "route": "/dashboard/engagement-persona-surfaces/profiles",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-chat",
            "label": "Chat",
            "route": "/chat",
            "componentPath": "frontend/src/pages/Chat.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 12,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-conversation-library",
            "label": "Conversation Library",
            "route": "/chat/library",
            "componentPath": "frontend/src/pages/chat/Library.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 13,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-search-and-discovery",
            "label": "Search & Discovery",
            "route": "/search",
            "componentPath": "frontend/src/pages/Search.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 14,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-saved-searches-and-alerts",
            "label": "Saved Searches & Alerts",
            "route": "/search/saved",
            "componentPath": "frontend/src/pages/search/Saved.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 15,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-collaboration",
            "label": "Collaboration",
            "route": "/collaboration",
            "componentPath": "frontend/src/pages/Collaboration.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 16,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-shared-spaces-channels",
            "label": "Shared Spaces / Channels",
            "route": "/collaboration/channels",
            "componentPath": "frontend/src/pages/collaboration/Channels.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 17,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-mentions-and-presence",
            "label": "Mentions & Presence",
            "route": "/collaboration/presence",
            "componentPath": "frontend/src/pages/collaboration/Presence.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 18,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-personalization",
            "label": "Personalization",
            "route": "/personalization",
            "componentPath": "frontend/src/pages/Personalization.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 19,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-prompt-macro-library",
            "label": "Prompt / Macro Library",
            "route": "/personalization/macros",
            "componentPath": "frontend/src/pages/personalization/Macros.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 20,
            "isNew": false
          },
          {
            "id": "core-engagement-and-persona-surfaces-preference-profiles",
            "label": "Preference Profiles",
            "route": "/personalization/profiles",
            "componentPath": "frontend/src/pages/personalization/Profiles.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 21,
            "isNew": false
          }
        ]
      },
      {
        "id": "core-overview",
        "label": "Overview",
        "homeRoute": "/dashboard/overview",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 3,
        "features": [
          {
            "id": "core-overview-dashboard",
            "label": "Dashboard",
            "route": "/core/dashboard",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "core-overview-master-stack",
            "label": "Master Stack",
            "route": "/core/master-stack",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "core-overview-overview",
            "label": "Overview",
            "route": "/core/overview/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "core-overview-overview",
            "label": "Overview",
            "route": "/core/overview/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "core-overview-runbook",
            "label": "Runbook",
            "route": "/core/overview/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "core-overview-platform-overview",
            "label": "Platform Overview",
            "route": "/dashboard",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          }
        ]
      },
      {
        "id": "core-operations",
        "label": "Operations",
        "homeRoute": "/dashboard/operations",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 4,
        "features": [
          {
            "id": "core-operations-overview",
            "label": "Overview",
            "route": "/core/operations/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "core-operations-runbook",
            "label": "Runbook",
            "route": "/core/operations/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "core-operations-evidence",
            "label": "Evidence",
            "route": "/core/operations/evidence",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      }
    ]
  },
  {
    "id": "common",
    "label": "Common",
    "path": "/mission",
    "actorScope": "both",
    "order": 2,
    "categories": [
      {
        "id": "common-cookbook-lab",
        "label": "Cookbook Lab",
        "homeRoute": "/legacy/cookbook-lab",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "common-cookbook-lab-cookbook-lab",
            "label": "Cookbook Lab",
            "route": "/legacy/cookbook-lab",
            "componentPath": "frontend/src/pages/CookbookLab.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-cookbook-lab-overview",
            "label": "Overview",
            "route": "/common/cookbook-lab/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-cookbook-lab-overview",
            "label": "Overview",
            "route": "/common/cookbook-lab/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-cookbook-lab-runbook",
            "label": "Runbook",
            "route": "/common/cookbook-lab/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-cookbook-lab-runbook",
            "label": "Runbook",
            "route": "/common/cookbook-lab/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-data-knowledge-home",
        "label": "Data Knowledge Home",
        "homeRoute": "/legacy/data-knowledge-home",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "common-data-knowledge-home-data-knowledge-home",
            "label": "Data Knowledge Home",
            "route": "/legacy/data-knowledge-home",
            "componentPath": "frontend/src/pages/DataKnowledgeHome.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-data-knowledge-home-overview",
            "label": "Overview",
            "route": "/common/data-knowledge-home/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-data-knowledge-home-overview",
            "label": "Overview",
            "route": "/common/data-knowledge-home/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-data-knowledge-home-runbook",
            "label": "Runbook",
            "route": "/common/data-knowledge-home/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-data-knowledge-home-runbook",
            "label": "Runbook",
            "route": "/common/data-knowledge-home/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-docs-spec-home",
        "label": "Docs Spec Home",
        "homeRoute": "/legacy/docs-spec-home",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 3,
        "features": [
          {
            "id": "common-docs-spec-home-docs-spec-home",
            "label": "Docs Spec Home",
            "route": "/legacy/docs-spec-home",
            "componentPath": "frontend/src/pages/DocsSpecHome.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-docs-spec-home-overview",
            "label": "Overview",
            "route": "/common/docs-spec-home/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-docs-spec-home-overview",
            "label": "Overview",
            "route": "/common/docs-spec-home/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-docs-spec-home-runbook",
            "label": "Runbook",
            "route": "/common/docs-spec-home/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-docs-spec-home-runbook",
            "label": "Runbook",
            "route": "/common/docs-spec-home/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-drivers-integrations-home",
        "label": "Drivers Integrations Home",
        "homeRoute": "/legacy/drivers-integrations-home",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 4,
        "features": [
          {
            "id": "common-drivers-integrations-home-drivers-integrations-home",
            "label": "Drivers Integrations Home",
            "route": "/legacy/drivers-integrations-home",
            "componentPath": "frontend/src/pages/DriversIntegrationsHome.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-drivers-integrations-home-overview",
            "label": "Overview",
            "route": "/common/drivers-integrations-home/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-drivers-integrations-home-overview",
            "label": "Overview",
            "route": "/common/drivers-integrations-home/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-drivers-integrations-home-runbook",
            "label": "Runbook",
            "route": "/common/drivers-integrations-home/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-drivers-integrations-home-runbook",
            "label": "Runbook",
            "route": "/common/drivers-integrations-home/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-governance-security-home",
        "label": "Governance Security Home",
        "homeRoute": "/legacy/governance-security-home",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 5,
        "features": [
          {
            "id": "common-governance-security-home-governance-security-home",
            "label": "Governance Security Home",
            "route": "/legacy/governance-security-home",
            "componentPath": "frontend/src/pages/GovernanceSecurityHome.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-governance-security-home-overview",
            "label": "Overview",
            "route": "/common/governance-security-home/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-governance-security-home-overview",
            "label": "Overview",
            "route": "/common/governance-security-home/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-governance-security-home-runbook",
            "label": "Runbook",
            "route": "/common/governance-security-home/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-governance-security-home-runbook",
            "label": "Runbook",
            "route": "/common/governance-security-home/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-mission-architecture-home",
        "label": "Mission Architecture Home",
        "homeRoute": "/legacy/mission-architecture-home",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 6,
        "features": [
          {
            "id": "common-mission-architecture-home-mission-architecture-home",
            "label": "Mission Architecture Home",
            "route": "/legacy/mission-architecture-home",
            "componentPath": "frontend/src/pages/MissionArchitectureHome.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-mission-architecture-home-overview",
            "label": "Overview",
            "route": "/common/mission-architecture-home/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-mission-architecture-home-overview",
            "label": "Overview",
            "route": "/common/mission-architecture-home/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-mission-architecture-home-runbook",
            "label": "Runbook",
            "route": "/common/mission-architecture-home/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-mission-architecture-home-runbook",
            "label": "Runbook",
            "route": "/common/mission-architecture-home/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-observability-evidence-home",
        "label": "Observability Evidence Home",
        "homeRoute": "/legacy/observability-evidence-home",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 7,
        "features": [
          {
            "id": "common-observability-evidence-home-observability-evidence-home",
            "label": "Observability Evidence Home",
            "route": "/legacy/observability-evidence-home",
            "componentPath": "frontend/src/pages/ObservabilityEvidenceHome.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-observability-evidence-home-overview",
            "label": "Overview",
            "route": "/common/observability-evidence-home/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-observability-evidence-home-overview",
            "label": "Overview",
            "route": "/common/observability-evidence-home/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-observability-evidence-home-runbook",
            "label": "Runbook",
            "route": "/common/observability-evidence-home/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-observability-evidence-home-runbook",
            "label": "Runbook",
            "route": "/common/observability-evidence-home/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-operations-infrastructure-home",
        "label": "Operations Infrastructure Home",
        "homeRoute": "/legacy/operations-infrastructure-home",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 8,
        "features": [
          {
            "id": "common-operations-infrastructure-home-operations-infrastructure-home",
            "label": "Operations Infrastructure Home",
            "route": "/legacy/operations-infrastructure-home",
            "componentPath": "frontend/src/pages/OperationsInfrastructureHome.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-operations-infrastructure-home-overview",
            "label": "Overview",
            "route": "/common/operations-infrastructure-home/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-operations-infrastructure-home-overview",
            "label": "Overview",
            "route": "/common/operations-infrastructure-home/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-operations-infrastructure-home-runbook",
            "label": "Runbook",
            "route": "/common/operations-infrastructure-home/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-operations-infrastructure-home-runbook",
            "label": "Runbook",
            "route": "/common/operations-infrastructure-home/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-roadmap-risks-home",
        "label": "Roadmap Risks Home",
        "homeRoute": "/legacy/roadmap-risks-home",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 9,
        "features": [
          {
            "id": "common-roadmap-risks-home-roadmap-risks-home",
            "label": "Roadmap Risks Home",
            "route": "/legacy/roadmap-risks-home",
            "componentPath": "frontend/src/pages/RoadmapRisksHome.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-roadmap-risks-home-overview",
            "label": "Overview",
            "route": "/common/roadmap-risks-home/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-roadmap-risks-home-overview",
            "label": "Overview",
            "route": "/common/roadmap-risks-home/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-roadmap-risks-home-runbook",
            "label": "Runbook",
            "route": "/common/roadmap-risks-home/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-roadmap-risks-home-runbook",
            "label": "Runbook",
            "route": "/common/roadmap-risks-home/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-settings-admin-enterprise-extensions-home",
        "label": "Settings Admin Enterprise Extensions Home",
        "homeRoute": "/legacy/settings-admin-enterprise-extensions-home",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 10,
        "features": [
          {
            "id": "common-settings-admin-enterprise-extensions-home-settings-admin-enterprise-extensions-home",
            "label": "Settings Admin Enterprise Extensions Home",
            "route": "/legacy/settings-admin-enterprise-extensions-home",
            "componentPath": "frontend/src/pages/SettingsAdminEnterpriseExtensionsHome.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-settings-admin-enterprise-extensions-home-overview",
            "label": "Overview",
            "route": "/common/settings-admin-enterprise-extensions-home/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-settings-admin-enterprise-extensions-home-overview",
            "label": "Overview",
            "route": "/common/settings-admin-enterprise-extensions-home/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-settings-admin-enterprise-extensions-home-runbook",
            "label": "Runbook",
            "route": "/common/settings-admin-enterprise-extensions-home/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-settings-admin-enterprise-extensions-home-runbook",
            "label": "Runbook",
            "route": "/common/settings-admin-enterprise-extensions-home/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-settings-admin-home",
        "label": "Settings Admin Home",
        "homeRoute": "/legacy/settings-admin-home",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 11,
        "features": [
          {
            "id": "common-settings-admin-home-settings-admin-home",
            "label": "Settings Admin Home",
            "route": "/legacy/settings-admin-home",
            "componentPath": "frontend/src/pages/SettingsAdminHome.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-settings-admin-home-overview",
            "label": "Overview",
            "route": "/common/settings-admin-home/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-settings-admin-home-overview",
            "label": "Overview",
            "route": "/common/settings-admin-home/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-settings-admin-home-runbook",
            "label": "Runbook",
            "route": "/common/settings-admin-home/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-settings-admin-home-runbook",
            "label": "Runbook",
            "route": "/common/settings-admin-home/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-vision-meta-stack-home",
        "label": "Vision Meta Stack Home",
        "homeRoute": "/legacy/vision-meta-stack-home",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 12,
        "features": [
          {
            "id": "common-vision-meta-stack-home-vision-meta-stack-home",
            "label": "Vision Meta Stack Home",
            "route": "/legacy/vision-meta-stack-home",
            "componentPath": "frontend/src/pages/VisionMeta-StackHome.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-vision-meta-stack-home-overview",
            "label": "Overview",
            "route": "/common/vision-meta-stack-home/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-vision-meta-stack-home-overview",
            "label": "Overview",
            "route": "/common/vision-meta-stack-home/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-vision-meta-stack-home-runbook",
            "label": "Runbook",
            "route": "/common/vision-meta-stack-home/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-vision-meta-stack-home-runbook",
            "label": "Runbook",
            "route": "/common/vision-meta-stack-home/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-concept-studio",
        "label": "Concept Studio",
        "homeRoute": "/legacy/concept-studio",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 13,
        "features": [
          {
            "id": "common-concept-studio-concept-studio",
            "label": "Concept Studio",
            "route": "/legacy/concept-studio",
            "componentPath": "frontend/src/pages/concepts/ConceptStudio.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-concept-studio-overview",
            "label": "Overview",
            "route": "/common/concept-studio/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-concept-studio-overview",
            "label": "Overview",
            "route": "/common/concept-studio/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-concept-studio-runbook",
            "label": "Runbook",
            "route": "/common/concept-studio/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-concept-studio-runbook",
            "label": "Runbook",
            "route": "/common/concept-studio/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-planes-architecture",
        "label": "Planes Architecture",
        "homeRoute": "/mission/planes-architecture",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 14,
        "features": [
          {
            "id": "common-planes-architecture-planes-architecture",
            "label": "Planes Architecture",
            "route": "/legacy/planes-architecture",
            "componentPath": "frontend/src/pages/mission/PlanesArchitecture.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-planes-architecture-data-plane",
            "label": "Data Plane",
            "route": "/mission/planes/data",
            "componentPath": "frontend/src/pages/mission/planes/Data.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-planes-architecture-crossplaneflows",
            "label": "Crossplaneflows",
            "route": "/mission-architecture/planes-architecture/cross-plane-flows",
            "componentPath": "frontend/src/pages/Missionarchitecture/Planesarchitecture/Crossplaneflows.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-planes-architecture-control-plane",
            "label": "Control Plane",
            "route": "/mission/planes/control",
            "componentPath": "frontend/src/pages/mission/planes/Control.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-planes-architecture-overview",
            "label": "Overview",
            "route": "/common/planes-architecture/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-planes-architecture-governance-plane",
            "label": "Governance Plane",
            "route": "/mission/planes/governance",
            "componentPath": "frontend/src/pages/mission/planes/Governance.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-planes-architecture-cross-plane-flows",
            "label": "Cross-Plane Flows",
            "route": "/mission/planes/cross-plane",
            "componentPath": "frontend/src/pages/mission/planes/CrossPlane.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "common-planes-architecture-failure-domains-by-plane",
            "label": "Failure Domains by Plane",
            "route": "/mission/planes/failure-domains",
            "componentPath": "frontend/src/pages/mission/planes/FailureDomains.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          },
          {
            "id": "common-planes-architecture-planes-overview",
            "label": "Planes Overview",
            "route": "/mission/planes",
            "componentPath": "frontend/src/pages/mission/Planes.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6,
            "isNew": false
          },
          {
            "id": "common-planes-architecture-plane-apis-and-event-contracts",
            "label": "Plane APIs & Event Contracts",
            "route": "/mission/planes/contracts",
            "componentPath": "frontend/src/pages/mission/planes/Contracts.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7,
            "isNew": false
          },
          {
            "id": "common-planes-architecture-planes-architecture",
            "label": "Planes Architecture",
            "route": "/mission/planes-architecture",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-architecture-principles",
        "label": "Architecture Principles",
        "homeRoute": "/mission/architecture-principles-home",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 15,
        "features": [
          {
            "id": "common-architecture-principles-driverawareorchestrator",
            "label": "Driverawareorchestrator",
            "route": "/mission-architecture/architecture-principles/driver-aware-orchestrator",
            "componentPath": "frontend/src/pages/Missionarchitecture/Architectureprinciples/Driverawareorchestrator.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-architecture-principles-overview",
            "label": "Overview",
            "route": "/common/architecture-principles/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-architecture-principles-overview",
            "label": "Overview",
            "route": "/common/architecture-principles/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-architecture-principles-runbook",
            "label": "Runbook",
            "route": "/common/architecture-principles/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-architecture-principles-runbook",
            "label": "Runbook",
            "route": "/common/architecture-principles/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-mission-identity",
        "label": "Mission Identity",
        "homeRoute": "/mission/mission-identity-home",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 16,
        "features": [
          {
            "id": "common-mission-identity-identityroles",
            "label": "Identityroles",
            "route": "/mission-architecture/mission-identity/identity-roles",
            "componentPath": "frontend/src/pages/Missionarchitecture/Missionidentity/Identityroles.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-mission-identity-missionscope",
            "label": "Missionscope",
            "route": "/mission-architecture/mission-identity/mission-scope",
            "componentPath": "frontend/src/pages/Missionarchitecture/Missionidentity/Missionscope.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-mission-identity-overview",
            "label": "Overview",
            "route": "/common/mission-identity/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-mission-identity-overview",
            "label": "Overview",
            "route": "/common/mission-identity/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-telemetry-metrics",
        "label": "Telemetry Metrics",
        "homeRoute": "/observability/telemetry-metrics-home",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 17,
        "features": [
          {
            "id": "common-telemetry-metrics-slisslos",
            "label": "Slisslos",
            "route": "/observability-evidence/telemetry-metrics/slis-slos",
            "componentPath": "frontend/src/pages/Observabilityevidence/Telemetrymetrics/Slisslos.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-telemetry-metrics-overview",
            "label": "Overview",
            "route": "/common/telemetry-metrics/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-telemetry-metrics-overview",
            "label": "Overview",
            "route": "/common/telemetry-metrics/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-telemetry-metrics-runbook",
            "label": "Runbook",
            "route": "/common/telemetry-metrics/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-telemetry-metrics-runbook",
            "label": "Runbook",
            "route": "/common/telemetry-metrics/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-files-and-storage",
        "label": "Files & Storage",
        "homeRoute": "/mission/files-and-storage",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 18,
        "features": [
          {
            "id": "common-files-and-storage-file-browser",
            "label": "File Browser",
            "route": "/common/files/browser",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-files-and-storage-overview",
            "label": "Overview",
            "route": "/common/files-and-storage/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-files-and-storage-runbook",
            "label": "Runbook",
            "route": "/common/files-and-storage/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-integrations",
        "label": "Integrations",
        "homeRoute": "/mission/integrations",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 19,
        "features": [
          {
            "id": "common-integrations-connector-catalog",
            "label": "Connector Catalog",
            "route": "/common/integrations/catalog",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-integrations-overview",
            "label": "Overview",
            "route": "/common/integrations/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-integrations-runbook",
            "label": "Runbook",
            "route": "/common/integrations/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-mission-control",
        "label": "Mission Control",
        "homeRoute": "/mission/mission-control",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 20,
        "features": [
          {
            "id": "common-mission-control-mission-control",
            "label": "Mission Control",
            "route": "/mission",
            "componentPath": "frontend/src/pages/Mission.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-mission-control-overview",
            "label": "Overview",
            "route": "/common/mission-control/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-mission-control-runbook",
            "label": "Runbook",
            "route": "/common/mission-control/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-mission-and-identity",
        "label": "Mission & Identity",
        "homeRoute": "/mission/mission-and-identity",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 21,
        "features": [
          {
            "id": "common-mission-and-identity-identity-and-roles",
            "label": "Identity & Roles",
            "route": "/mission/identity",
            "componentPath": "frontend/src/pages/mission/Identity.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-mission-and-identity-mission-and-identity",
            "label": "Mission & Identity",
            "route": "/mission/mission-identity",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-mission-and-identity-mission-and-scope",
            "label": "Mission & Scope",
            "route": "/mission/overview",
            "componentPath": "frontend/src/pages/mission/Overview.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-mission-and-identity-use-cases-map",
            "label": "Use Cases Map",
            "route": "/mission/use-cases",
            "componentPath": "frontend/src/pages/mission/UseCases.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "common-mission-and-identity-system-boundaries-and-non-goals",
            "label": "System Boundaries & Non-Goals",
            "route": "/mission/non-goals",
            "componentPath": "frontend/src/pages/mission/NonGoals.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          },
          {
            "id": "common-mission-and-identity-terminology-glossary",
            "label": "Terminology Glossary",
            "route": "/mission/glossary",
            "componentPath": "frontend/src/pages/mission/Glossary.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6,
            "isNew": false
          },
          {
            "id": "common-mission-and-identity-deployment-modes",
            "label": "Deployment Modes",
            "route": "/mission/modes",
            "componentPath": "frontend/src/pages/mission/Modes.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7,
            "isNew": false
          },
          {
            "id": "common-mission-and-identity-reference-architectures-by-edition",
            "label": "Reference Architectures by Edition",
            "route": "/mission/reference-architectures",
            "componentPath": "frontend/src/pages/mission/ReferenceArchitectures.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8,
            "isNew": false
          },
          {
            "id": "common-mission-and-identity-ai-driver-stack",
            "label": "AI + Driver Stack",
            "route": "/mission/ai-stack",
            "componentPath": "frontend/src/pages/mission/AiStack.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 9,
            "isNew": false
          },
          {
            "id": "common-mission-and-identity-model-provider-layer",
            "label": "Model Provider Layer",
            "route": "/mission/models",
            "componentPath": "frontend/src/pages/mission/Models.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 10,
            "isNew": false
          },
          {
            "id": "common-mission-and-identity-daemon-families",
            "label": "Daemon Families",
            "route": "/mission/daemons",
            "componentPath": "frontend/src/pages/mission/Daemons.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 11,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-architecture-and-principles",
        "label": "Architecture & Principles",
        "homeRoute": "/mission/architecture-and-principles",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 22,
        "features": [
          {
            "id": "common-architecture-and-principles-architecture-overview",
            "label": "Architecture Overview",
            "route": "/mission/architecture",
            "componentPath": "frontend/src/pages/mission/Architecture.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-architecture-and-principles-architecture-and-principles",
            "label": "Architecture & Principles",
            "route": "/mission/architecture-principles",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-architecture-and-principles-architectural-principles",
            "label": "Architectural Principles",
            "route": "/mission/principles",
            "componentPath": "frontend/src/pages/mission/Principles.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-architecture-and-principles-major-components",
            "label": "Major Components",
            "route": "/mission/components",
            "componentPath": "frontend/src/pages/mission/Components.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "common-architecture-and-principles-driver-aware-orchestrator",
            "label": "Driver-Aware Orchestrator",
            "route": "/mission/orchestrator",
            "componentPath": "frontend/src/pages/mission/Orchestrator.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          },
          {
            "id": "common-architecture-and-principles-component-mapping",
            "label": "Component Mapping",
            "route": "/mission/mapping",
            "componentPath": "frontend/src/pages/mission/Mapping.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6,
            "isNew": false
          },
          {
            "id": "common-architecture-and-principles-data-model-and-contracts",
            "label": "Data Model & Contracts",
            "route": "/mission/contracts",
            "componentPath": "frontend/src/pages/mission/Contracts.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7,
            "isNew": false
          },
          {
            "id": "common-architecture-and-principles-extensibility-points",
            "label": "Extensibility Points",
            "route": "/mission/extensibility",
            "componentPath": "frontend/src/pages/mission/Extensibility.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8,
            "isNew": false
          },
          {
            "id": "common-architecture-and-principles-threat-model-summary",
            "label": "Threat Model Summary",
            "route": "/mission/threat-model",
            "componentPath": "frontend/src/pages/mission/ThreatModel.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 9,
            "isNew": false
          },
          {
            "id": "common-architecture-and-principles-performance-targets",
            "label": "Performance Targets",
            "route": "/mission/performance-targets",
            "componentPath": "frontend/src/pages/mission/PerformanceTargets.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 10,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-evidence-packs",
        "label": "Evidence Packs",
        "homeRoute": "/observability/evidence-packs",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 23,
        "features": [
          {
            "id": "common-evidence-packs-export-for-auditors",
            "label": "Export for Auditors",
            "route": "/observability/evidence/export",
            "componentPath": "frontend/src/pages/observability/evidence/Export.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-evidence-packs-evidence-packs",
            "label": "Evidence Packs",
            "route": "/observability/evidence",
            "componentPath": "frontend/src/pages/observability/Evidence.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-evidence-packs-evidence-queries",
            "label": "Evidence Queries",
            "route": "/observability/evidence/query",
            "componentPath": "frontend/src/pages/observability/evidence/Query.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-metrics-and-telemetry",
        "label": "Metrics & Telemetry",
        "homeRoute": "/observability/metrics-and-telemetry",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 24,
        "features": [
          {
            "id": "common-metrics-and-telemetry-metrics-model",
            "label": "Metrics Model",
            "route": "/observability/metrics",
            "componentPath": "frontend/src/pages/observability/Metrics.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-metrics-and-telemetry-metric-explorer",
            "label": "Metric Explorer",
            "route": "/observability/metrics/explorer",
            "componentPath": "frontend/src/pages/observability/metrics/Explorer.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-metrics-and-telemetry-overview",
            "label": "Overview",
            "route": "/common/metrics-and-telemetry/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-health-and-monitoring",
        "label": "Health & Monitoring",
        "homeRoute": "/observability/health-and-monitoring",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 25,
        "features": [
          {
            "id": "common-health-and-monitoring-health-checks",
            "label": "Health Checks",
            "route": "/observability/health",
            "componentPath": "frontend/src/pages/observability/Health.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-health-and-monitoring-overview",
            "label": "Overview",
            "route": "/common/health-and-monitoring/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-health-and-monitoring-runbook",
            "label": "Runbook",
            "route": "/common/health-and-monitoring/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-record-auditor-and-logbook",
        "label": "Record Auditor & Logbook",
        "homeRoute": "/observability/record-auditor-and-logbook",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 26,
        "features": [
          {
            "id": "common-record-auditor-and-logbook-record-auditor-and-logbook",
            "label": "Record Auditor & Logbook",
            "route": "/observability/record-auditor-logbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-record-auditor-and-logbook-record-auditor",
            "label": "Record Auditor",
            "route": "/observability/record-auditor",
            "componentPath": "frontend/src/pages/observability/RecordAuditor.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-record-auditor-and-logbook-logbook-timeline",
            "label": "Logbook Timeline",
            "route": "/observability/record-auditor/timeline",
            "componentPath": "frontend/src/pages/observability/record-auditor/Timeline.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-record-auditor-and-logbook-audit-evidence",
            "label": "Audit Evidence",
            "route": "/observability/audit",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "common-record-auditor-and-logbook-evidence-builder",
            "label": "Evidence Builder",
            "route": "/observability/record-auditor-logbook/builder",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          },
          {
            "id": "common-record-auditor-and-logbook-audit-evidence",
            "label": "Audit Evidence",
            "route": "/audit",
            "componentPath": "frontend/src/pages/Audit.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6,
            "isNew": false
          },
          {
            "id": "common-record-auditor-and-logbook-evidence-builder",
            "label": "Evidence Builder",
            "route": "/audit/builder",
            "componentPath": "frontend/src/pages/audit/Builder.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-evidence-and-audit",
        "label": "Evidence & Audit",
        "homeRoute": "/observability/evidence-and-audit",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 27,
        "features": [
          {
            "id": "common-evidence-and-audit-evidence-and-audit",
            "label": "Evidence & Audit",
            "route": "/observability/evidence-audit",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-evidence-and-audit-audit-logs",
            "label": "Audit Logs",
            "route": "/observability/audit-logs",
            "componentPath": "frontend/src/pages/observability/AuditLogs.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-evidence-and-audit-retention-policies",
            "label": "Retention Policies",
            "route": "/observability/retention",
            "componentPath": "frontend/src/pages/observability/Retention.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-logging-and-tracing",
        "label": "Logging & Tracing",
        "homeRoute": "/observability/logging-and-tracing",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 28,
        "features": [
          {
            "id": "common-logging-and-tracing-logging-and-tracing-overview",
            "label": "Logging & Tracing Overview",
            "route": "/observability/logging-tracing",
            "componentPath": "frontend/src/pages/observability/LoggingTracing.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-logging-and-tracing-structured-logging",
            "label": "Structured Logging",
            "route": "/observability/logging",
            "componentPath": "frontend/src/pages/observability/Logging.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-logging-and-tracing-log-explorer",
            "label": "Log Explorer",
            "route": "/observability/logging/explorer",
            "componentPath": "frontend/src/pages/observability/logging/Explorer.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-logging-and-tracing-distributed-tracing",
            "label": "Distributed Tracing",
            "route": "/observability/tracing",
            "componentPath": "frontend/src/pages/observability/Tracing.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "common-logging-and-tracing-trace-explorer",
            "label": "Trace Explorer",
            "route": "/observability/tracing/explorer",
            "componentPath": "frontend/src/pages/observability/tracing/Explorer.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          },
          {
            "id": "common-logging-and-tracing-correlation-and-context",
            "label": "Correlation & Context",
            "route": "/observability/correlation",
            "componentPath": "frontend/src/pages/observability/Correlation.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-temporal-backtesting-and-replay",
        "label": "Temporal Backtesting & Replay",
        "homeRoute": "/observability/temporal-backtesting-and-replay",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 29,
        "features": [
          {
            "id": "common-temporal-backtesting-and-replay-temporal-backtesting-and-replay",
            "label": "Temporal Backtesting & Replay",
            "route": "/observability/temporal-backtesting-replay",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-temporal-backtesting-and-replay-replay-engine",
            "label": "Replay Engine",
            "route": "/observability/replay",
            "componentPath": "frontend/src/pages/observability/Replay.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-temporal-backtesting-and-replay-scenario-library",
            "label": "Scenario Library",
            "route": "/observability/replay/scenarios",
            "componentPath": "frontend/src/pages/observability/replay/Scenarios.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-temporal-backtesting-and-replay-determinism-checks",
            "label": "Determinism Checks",
            "route": "/observability/replay/determinism",
            "componentPath": "frontend/src/pages/observability/replay/Determinism.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "common-temporal-backtesting-and-replay-temporal-backtesting",
            "label": "Temporal Backtesting",
            "route": "/observability/backtesting",
            "componentPath": "frontend/src/pages/observability/Backtesting.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-health-and-self-healing",
        "label": "Health & Self-Healing",
        "homeRoute": "/observability/health-and-self-healing",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 30,
        "features": [
          {
            "id": "common-health-and-self-healing-health-and-self-healing",
            "label": "Health & Self-Healing",
            "route": "/observability/health-self-healing",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-health-and-self-healing-drift-detection",
            "label": "Drift Detection",
            "route": "/observability/drift",
            "componentPath": "frontend/src/pages/observability/Drift.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-health-and-self-healing-runbooks",
            "label": "Runbooks",
            "route": "/observability/runbooks",
            "componentPath": "frontend/src/pages/observability/Runbooks.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-health-and-self-healing-self-healing",
            "label": "Self-Healing",
            "route": "/observability/self-healing",
            "componentPath": "frontend/src/pages/observability/SelfHealing.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "common-health-and-self-healing-automated-rollbacks",
            "label": "Automated Rollbacks",
            "route": "/observability/rollbacks",
            "componentPath": "frontend/src/pages/observability/Rollbacks.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-dashboards-and-alerting",
        "label": "Dashboards & Alerting",
        "homeRoute": "/observability/dashboards-and-alerting",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 31,
        "features": [
          {
            "id": "common-dashboards-and-alerting-dashboards-and-alerting",
            "label": "Dashboards & Alerting",
            "route": "/observability/dashboards-alerting",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-dashboards-and-alerting-dashboards",
            "label": "Dashboards",
            "route": "/observability/dashboards",
            "componentPath": "frontend/src/pages/observability/Dashboards.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-dashboards-and-alerting-dashboard-builder",
            "label": "Dashboard Builder",
            "route": "/observability/dashboards/builder",
            "componentPath": "frontend/src/pages/observability/dashboards/Builder.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-dashboards-and-alerting-alerting",
            "label": "Alerting",
            "route": "/observability/alerting",
            "componentPath": "frontend/src/pages/observability/Alerting.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "common-dashboards-and-alerting-alert-rules",
            "label": "Alert Rules",
            "route": "/observability/alerting/rules",
            "componentPath": "frontend/src/pages/observability/alerting/Rules.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          },
          {
            "id": "common-dashboards-and-alerting-notification-channels",
            "label": "Notification Channels",
            "route": "/observability/alerting/channels",
            "componentPath": "frontend/src/pages/observability/alerting/Channels.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6,
            "isNew": false
          }
        ]
      },
      {
        "id": "common-telemetry-and-metrics",
        "label": "Telemetry & Metrics",
        "homeRoute": "/observability/telemetry-and-metrics",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 32,
        "features": [
          {
            "id": "common-telemetry-and-metrics-telemetry-and-metrics",
            "label": "Telemetry & Metrics",
            "route": "/observability/telemetry-metrics",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "common-telemetry-and-metrics-observability-overview",
            "label": "Observability Overview",
            "route": "/observability/telemetry-metrics/observability",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "common-telemetry-and-metrics-monitoring",
            "label": "Monitoring",
            "route": "/observability/monitoring",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "common-telemetry-and-metrics-analytics",
            "label": "Analytics",
            "route": "/observability/analytics",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "common-telemetry-and-metrics-slis-and-slos",
            "label": "SLIs & SLOs",
            "route": "/observability/slis",
            "componentPath": "frontend/src/pages/observability/Slis.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          },
          {
            "id": "common-telemetry-and-metrics-slo-burn-rates",
            "label": "SLO Burn Rates",
            "route": "/observability/slis/burn",
            "componentPath": "frontend/src/pages/observability/slis/Burn.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6,
            "isNew": false
          },
          {
            "id": "common-telemetry-and-metrics-anomaly-detection",
            "label": "Anomaly Detection",
            "route": "/observability/anomalies",
            "componentPath": "frontend/src/pages/observability/Anomalies.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7,
            "isNew": false
          },
          {
            "id": "common-telemetry-and-metrics-observability-overview",
            "label": "Observability Overview",
            "route": "/observability",
            "componentPath": "frontend/src/pages/Observability.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8,
            "isNew": false
          },
          {
            "id": "common-telemetry-and-metrics-monitoring",
            "label": "Monitoring",
            "route": "/monitoring",
            "componentPath": "frontend/src/pages/Monitoring.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 9,
            "isNew": false
          },
          {
            "id": "common-telemetry-and-metrics-analytics",
            "label": "Analytics",
            "route": "/analytics",
            "componentPath": "frontend/src/pages/Analytics.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 10,
            "isNew": false
          }
        ]
      }
    ]
  },
  {
    "id": "audit-official-records",
    "label": "Audit Official Records",
    "path": "/governance",
    "actorScope": "both",
    "order": 3,
    "categories": [
      {
        "id": "audit-official-records-record-auditor-and-logbook",
        "label": "Record Auditor & Logbook",
        "homeRoute": "/observability/record-auditor-and-logbook",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "audit-official-records-record-auditor-and-logbook-evidence-packs",
            "label": "Evidence Packs",
            "route": "/audit/evidence-packs",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "audit-official-records-record-auditor-and-logbook-policy-decisions",
            "label": "Policy Decisions",
            "route": "/audit/policy-decisions",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "audit-official-records-record-auditor-and-logbook-overview",
            "label": "Overview",
            "route": "/audit-official-records/record-auditor-and-logbook/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "audit-official-records-operations",
        "label": "Operations",
        "homeRoute": "/governance/operations",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "audit-official-records-operations-overview",
            "label": "Overview",
            "route": "/audit-official-records/operations/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "audit-official-records-operations-runbook",
            "label": "Runbook",
            "route": "/audit-official-records/operations/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "audit-official-records-operations-evidence",
            "label": "Evidence",
            "route": "/audit-official-records/operations/evidence",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "audit-official-records-governance-center",
        "label": "Governance Center",
        "homeRoute": "/governance/governance-center",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 3,
        "features": [
          {
            "id": "audit-official-records-governance-center-governance-home",
            "label": "Governance Home",
            "route": "/governance",
            "componentPath": "frontend/src/pages/Governance.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "audit-official-records-governance-center-security-posture",
            "label": "Security Posture",
            "route": "/governance/security",
            "componentPath": "frontend/src/pages/governance/Security.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "audit-official-records-governance-center-overview",
            "label": "Overview",
            "route": "/audit-official-records/governance-center/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "audit-official-records-policy-and-governance-engine",
        "label": "Policy & Governance Engine",
        "homeRoute": "/governance/policy-and-governance-engine",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 4,
        "features": [
          {
            "id": "audit-official-records-policy-and-governance-engine-policy-dsl",
            "label": "Policy DSL",
            "route": "/governance/policy/dsl",
            "componentPath": "frontend/src/pages/governance/policy/Dsl.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "audit-official-records-policy-and-governance-engine-policy-simulator",
            "label": "Policy Simulator",
            "route": "/governance/policy/simulator",
            "componentPath": "frontend/src/pages/governance/policy/Simulator.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "audit-official-records-policy-and-governance-engine-policy-engine",
            "label": "Policy Engine",
            "route": "/governance/policy",
            "componentPath": "frontend/src/pages/governance/Policy.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "audit-official-records-policy-and-governance-engine-policy-library-and-templates",
            "label": "Policy Library & Templates",
            "route": "/governance/policy/library",
            "componentPath": "frontend/src/pages/governance/policy/Library.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "audit-official-records-policy-and-governance-engine-safety-harnesses",
            "label": "Safety Harnesses",
            "route": "/governance/policy/safety",
            "componentPath": "frontend/src/pages/governance/policy/Safety.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          },
          {
            "id": "audit-official-records-policy-and-governance-engine-policy-versioning-and-approvals",
            "label": "Policy Versioning & Approvals",
            "route": "/governance/policy/versioning",
            "componentPath": "frontend/src/pages/governance/policy/Versioning.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6,
            "isNew": false
          },
          {
            "id": "audit-official-records-policy-and-governance-engine-enforcement-points-map",
            "label": "Enforcement Points Map",
            "route": "/governance/policy/enforcement",
            "componentPath": "frontend/src/pages/governance/policy/Enforcement.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7,
            "isNew": false
          },
          {
            "id": "audit-official-records-policy-and-governance-engine-exceptions-and-waivers",
            "label": "Exceptions & Waivers",
            "route": "/governance/policy/exceptions",
            "componentPath": "frontend/src/pages/governance/policy/Exceptions.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8,
            "isNew": false
          },
          {
            "id": "audit-official-records-policy-and-governance-engine-policy-and-governance-engine",
            "label": "Policy & Governance Engine",
            "route": "/governance/policy-governance-engine",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 9,
            "isNew": false
          }
        ]
      },
      {
        "id": "audit-official-records-identity-and-access",
        "label": "Identity & Access",
        "homeRoute": "/governance/identity-and-access",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 5,
        "features": [
          {
            "id": "audit-official-records-identity-and-access-sso-saml-oidc-settings",
            "label": "SSO/SAML/OIDC Settings",
            "route": "/governance/identity/sso",
            "componentPath": "frontend/src/pages/governance/identity/Sso.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "audit-official-records-identity-and-access-identity-and-roles",
            "label": "Identity & Roles",
            "route": "/governance/identity",
            "componentPath": "frontend/src/pages/governance/Identity.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "audit-official-records-identity-and-access-authentication",
            "label": "Authentication",
            "route": "/governance/identity/auth",
            "componentPath": "frontend/src/pages/governance/identity/Auth.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "audit-official-records-identity-and-access-scim-provisioning",
            "label": "SCIM Provisioning",
            "route": "/governance/identity/scim",
            "componentPath": "frontend/src/pages/governance/identity/Scim.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "audit-official-records-identity-and-access-rbac-abac",
            "label": "RBAC/ABAC",
            "route": "/governance/identity/rbac",
            "componentPath": "frontend/src/pages/governance/identity/Rbac.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          },
          {
            "id": "audit-official-records-identity-and-access-api-keys-and-tokens",
            "label": "API Keys & Tokens",
            "route": "/governance/identity/api-keys",
            "componentPath": "frontend/src/pages/governance/identity/ApiKeys.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6,
            "isNew": false
          },
          {
            "id": "audit-official-records-identity-and-access-session-management",
            "label": "Session Management",
            "route": "/governance/identity/sessions",
            "componentPath": "frontend/src/pages/governance/identity/Sessions.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7,
            "isNew": false
          },
          {
            "id": "audit-official-records-identity-and-access-access-reviews",
            "label": "Access Reviews",
            "route": "/governance/identity/reviews",
            "componentPath": "frontend/src/pages/governance/identity/Reviews.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8,
            "isNew": false
          },
          {
            "id": "audit-official-records-identity-and-access-identity-and-access",
            "label": "Identity & Access",
            "route": "/governance/identity-access",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 9,
            "isNew": false
          }
        ]
      },
      {
        "id": "audit-official-records-compliance-packs",
        "label": "Compliance Packs",
        "homeRoute": "/governance/compliance-packs",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 6,
        "features": [
          {
            "id": "audit-official-records-compliance-packs-compliance-packs",
            "label": "Compliance Packs",
            "route": "/governance/compliance",
            "componentPath": "frontend/src/pages/governance/Compliance.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "audit-official-records-compliance-packs-control-framework-mapping",
            "label": "Control Framework Mapping",
            "route": "/governance/compliance/controls",
            "componentPath": "frontend/src/pages/governance/compliance/Controls.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "audit-official-records-compliance-packs-audit-readiness-dashboard",
            "label": "Audit Readiness Dashboard",
            "route": "/governance/compliance/readiness",
            "componentPath": "frontend/src/pages/governance/compliance/Readiness.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "audit-official-records-regulator-fabric",
        "label": "Regulator Fabric",
        "homeRoute": "/governance/regulator-fabric",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 7,
        "features": [
          {
            "id": "audit-official-records-regulator-fabric-regulator-tenancy",
            "label": "Regulator Tenancy",
            "route": "/governance/regulator/tenancy",
            "componentPath": "frontend/src/pages/governance/regulator/Tenancy.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "audit-official-records-regulator-fabric-regulator-fabric",
            "label": "Regulator Fabric",
            "route": "/governance/regulator",
            "componentPath": "frontend/src/pages/governance/Regulator.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "audit-official-records-regulator-fabric-evidence-access",
            "label": "Evidence Access",
            "route": "/governance/regulator/evidence",
            "componentPath": "frontend/src/pages/governance/regulator/Evidence.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "audit-official-records-regulator-fabric-evidence-request-workflow",
            "label": "Evidence Request Workflow",
            "route": "/governance/regulator/requests",
            "componentPath": "frontend/src/pages/governance/regulator/Requests.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          }
        ]
      },
      {
        "id": "audit-official-records-security-monitoring",
        "label": "Security Monitoring",
        "homeRoute": "/governance/security-monitoring",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 8,
        "features": [
          {
            "id": "audit-official-records-security-monitoring-alignment-monitor",
            "label": "Alignment Monitor",
            "route": "/governance/security/alignment",
            "componentPath": "frontend/src/pages/governance/security/Alignment.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "audit-official-records-security-monitoring-incident-response",
            "label": "Incident Response",
            "route": "/governance/security/incidents",
            "componentPath": "frontend/src/pages/governance/security/Incidents.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "audit-official-records-security-monitoring-security-monitoring",
            "label": "Security Monitoring",
            "route": "/governance/security/monitoring",
            "componentPath": "frontend/src/pages/governance/security/Monitoring.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "audit-official-records-security-monitoring-alerts-and-rules",
            "label": "Alerts & Rules",
            "route": "/governance/security/alerts",
            "componentPath": "frontend/src/pages/governance/security/Alerts.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "audit-official-records-security-monitoring-threat-detection",
            "label": "Threat Detection",
            "route": "/governance/security/detection",
            "componentPath": "frontend/src/pages/governance/security/Detection.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          },
          {
            "id": "audit-official-records-security-monitoring-risk-scoring",
            "label": "Risk Scoring",
            "route": "/governance/security/risk",
            "componentPath": "frontend/src/pages/governance/security/Risk.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6,
            "isNew": false
          },
          {
            "id": "audit-official-records-security-monitoring-forensics-and-evidence",
            "label": "Forensics & Evidence",
            "route": "/governance/security/forensics",
            "componentPath": "frontend/src/pages/governance/security/Forensics.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7,
            "isNew": false
          },
          {
            "id": "audit-official-records-security-monitoring-vulnerability-management",
            "label": "Vulnerability Management",
            "route": "/governance/security/vuln",
            "componentPath": "frontend/src/pages/governance/security/Vuln.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8,
            "isNew": false
          }
        ]
      },
      {
        "id": "audit-official-records-ai-billing-and-cost-governance",
        "label": "AI Billing & Cost Governance",
        "homeRoute": "/governance/ai-billing-and-cost-governance",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 9,
        "features": [
          {
            "id": "audit-official-records-ai-billing-and-cost-governance-ai-billing-and-cost-governance",
            "label": "AI Billing & Cost Governance",
            "route": "/governance/ai-billing-cost-governance",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "audit-official-records-ai-billing-and-cost-governance-billing-and-usage",
            "label": "Billing & Usage",
            "route": "/governance/billing",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "audit-official-records-ai-billing-and-cost-governance-usage-fabric",
            "label": "Usage Fabric",
            "route": "/governance/billing/usage",
            "componentPath": "frontend/src/pages/governance/billing/Usage.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "audit-official-records-ai-billing-and-cost-governance-budgets-and-quotas",
            "label": "Budgets & Quotas",
            "route": "/governance/billing/budgets",
            "componentPath": "frontend/src/pages/governance/billing/Budgets.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "audit-official-records-ai-billing-and-cost-governance-cost-guardrails",
            "label": "Cost Guardrails",
            "route": "/governance/billing/guardrails",
            "componentPath": "frontend/src/pages/governance/billing/Guardrails.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          },
          {
            "id": "audit-official-records-ai-billing-and-cost-governance-billing-optimizer",
            "label": "Billing Optimizer",
            "route": "/governance/billing/optimizer",
            "componentPath": "frontend/src/pages/governance/billing/Optimizer.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6,
            "isNew": false
          },
          {
            "id": "audit-official-records-ai-billing-and-cost-governance-chargeback-showback-reports",
            "label": "Chargeback/Showback Reports",
            "route": "/governance/billing/chargeback",
            "componentPath": "frontend/src/pages/governance/billing/Chargeback.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7,
            "isNew": false
          },
          {
            "id": "audit-official-records-ai-billing-and-cost-governance-forecasting",
            "label": "Forecasting",
            "route": "/governance/billing/forecasting",
            "componentPath": "frontend/src/pages/governance/billing/Forecasting.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8,
            "isNew": false
          },
          {
            "id": "audit-official-records-ai-billing-and-cost-governance-provider-rate-cards",
            "label": "Provider Rate Cards",
            "route": "/governance/billing/rates",
            "componentPath": "frontend/src/pages/governance/billing/Rates.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 9,
            "isNew": false
          },
          {
            "id": "audit-official-records-ai-billing-and-cost-governance-multi-tenant-billing",
            "label": "Multi-Tenant Billing",
            "route": "/governance/billing/multi-tenant",
            "componentPath": "frontend/src/pages/governance/billing/MultiTenant.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 10,
            "isNew": false
          },
          {
            "id": "audit-official-records-ai-billing-and-cost-governance-billing-and-usage",
            "label": "Billing & Usage",
            "route": "/billing",
            "componentPath": "frontend/src/pages/Billing.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 11,
            "isNew": false
          }
        ]
      },
      {
        "id": "audit-official-records-compliance-and-regulator-fabric",
        "label": "Compliance & Regulator Fabric",
        "homeRoute": "/governance/compliance-and-regulator-fabric",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 10,
        "features": [
          {
            "id": "audit-official-records-compliance-and-regulator-fabric-compliance-and-regulator-fabric",
            "label": "Compliance & Regulator Fabric",
            "route": "/governance/compliance-regulator-fabric",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "audit-official-records-compliance-and-regulator-fabric-overview",
            "label": "Overview",
            "route": "/audit-official-records/compliance-and-regulator-fabric/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "audit-official-records-compliance-and-regulator-fabric-runbook",
            "label": "Runbook",
            "route": "/audit-official-records/compliance-and-regulator-fabric/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "audit-official-records-security-monitoring-and-response",
        "label": "Security Monitoring & Response",
        "homeRoute": "/governance/security-monitoring-and-response",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 11,
        "features": [
          {
            "id": "audit-official-records-security-monitoring-and-response-security-monitoring-and-response",
            "label": "Security Monitoring & Response",
            "route": "/governance/security-monitoring-response",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "audit-official-records-security-monitoring-and-response-overview",
            "label": "Overview",
            "route": "/audit-official-records/security-monitoring-and-response/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "audit-official-records-security-monitoring-and-response-runbook",
            "label": "Runbook",
            "route": "/audit-official-records/security-monitoring-and-response/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "audit-official-records-data-protection-and-classification",
        "label": "Data Protection & Classification",
        "homeRoute": "/governance/data-protection-and-classification",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 12,
        "features": [
          {
            "id": "audit-official-records-data-protection-and-classification-data-protection-and-classification",
            "label": "Data Protection & Classification",
            "route": "/governance/data-protection-classification",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "audit-official-records-data-protection-and-classification-data-protection",
            "label": "Data Protection",
            "route": "/governance/data-protection",
            "componentPath": "frontend/src/pages/governance/DataProtection.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "audit-official-records-data-protection-and-classification-data-classification",
            "label": "Data Classification",
            "route": "/governance/data-protection/classification",
            "componentPath": "frontend/src/pages/governance/data-protection/Classification.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "audit-official-records-data-protection-and-classification-data-masking",
            "label": "Data Masking",
            "route": "/governance/data-protection/masking",
            "componentPath": "frontend/src/pages/governance/data-protection/Masking.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "audit-official-records-data-protection-and-classification-tokenization",
            "label": "Tokenization",
            "route": "/governance/data-protection/tokenization",
            "componentPath": "frontend/src/pages/governance/data-protection/Tokenization.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          },
          {
            "id": "audit-official-records-data-protection-and-classification-dlp-rules",
            "label": "DLP Rules",
            "route": "/governance/data-protection/dlp",
            "componentPath": "frontend/src/pages/governance/data-protection/Dlp.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6,
            "isNew": false
          },
          {
            "id": "audit-official-records-data-protection-and-classification-data-residency",
            "label": "Data Residency",
            "route": "/governance/data-protection/residency",
            "componentPath": "frontend/src/pages/governance/data-protection/Residency.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7,
            "isNew": false
          }
        ]
      },
      {
        "id": "audit-official-records-regulator-console",
        "label": "Regulator Console",
        "homeRoute": "/governance/regulator-console",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 13,
        "features": [
          {
            "id": "audit-official-records-regulator-console-regulator-evidence-view",
            "label": "Regulator Evidence View",
            "route": "/audit/regulator/console",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "audit-official-records-regulator-console-overview",
            "label": "Overview",
            "route": "/audit-official-records/regulator-console/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "audit-official-records-regulator-console-runbook",
            "label": "Runbook",
            "route": "/audit-official-records/regulator-console/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      }
    ]
  },
  {
    "id": "automation",
    "label": "Automation",
    "path": "/ai",
    "actorScope": "both",
    "order": 4,
    "categories": [
      {
        "id": "automation-driver-fabric-and-system-execution",
        "label": "Driver Fabric & System Execution",
        "homeRoute": "/ai/driver-fabric-and-system-execution",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "automation-driver-fabric-and-system-execution-os-drivers",
            "label": "OS Drivers",
            "route": "/ai/drivers/os",
            "componentPath": "frontend/src/pages/ai/drivers/Os.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "automation-driver-fabric-and-system-execution-hardware-drivers",
            "label": "Hardware Drivers",
            "route": "/ai/drivers/hardware",
            "componentPath": "frontend/src/pages/ai/drivers/Hardware.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "automation-driver-fabric-and-system-execution-data-drivers",
            "label": "Data Drivers",
            "route": "/ai/drivers/data",
            "componentPath": "frontend/src/pages/ai/drivers/Data.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "automation-driver-fabric-and-system-execution-sandbox-and-testbed",
            "label": "Sandbox & Testbed",
            "route": "/ai/drivers/sandbox",
            "componentPath": "frontend/src/pages/ai/drivers/Sandbox.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "automation-driver-fabric-and-system-execution-driver-registry",
            "label": "Driver Registry",
            "route": "/ai/drivers",
            "componentPath": "frontend/src/pages/ai/Drivers.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "automation-driver-fabric-and-system-execution-driver-test-harness",
            "label": "Driver Test Harness",
            "route": "/ai/drivers/testing",
            "componentPath": "frontend/src/pages/ai/drivers/Testing.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "automation-driver-fabric-and-system-execution-driver-health-and-telemetry",
            "label": "Driver Health & Telemetry",
            "route": "/ai/drivers/health",
            "componentPath": "frontend/src/pages/ai/drivers/Health.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "automation-driver-fabric-and-system-execution-driver-permissions-and-sandboxing",
            "label": "Driver Permissions & Sandboxing",
            "route": "/ai/drivers/permissions",
            "componentPath": "frontend/src/pages/ai/drivers/Permissions.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          },
          {
            "id": "automation-driver-fabric-and-system-execution-driver-versioning-and-deprecation",
            "label": "Driver Versioning & Deprecation",
            "route": "/ai/drivers/versioning",
            "componentPath": "frontend/src/pages/ai/drivers/Versioning.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9,
            "isNew": false
          },
          {
            "id": "automation-driver-fabric-and-system-execution-package-and-env-drivers",
            "label": "Package & Env Drivers",
            "route": "/ai/drivers/package",
            "componentPath": "frontend/src/pages/ai/drivers/Package.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10,
            "isNew": false
          },
          {
            "id": "automation-driver-fabric-and-system-execution-software-and-saas-drivers",
            "label": "Software & SaaS Drivers",
            "route": "/ai/drivers/software",
            "componentPath": "frontend/src/pages/ai/drivers/Software.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11,
            "isNew": false
          },
          {
            "id": "automation-driver-fabric-and-system-execution-research-and-simulation-drivers",
            "label": "Research & Simulation Drivers",
            "route": "/ai/drivers/research",
            "componentPath": "frontend/src/pages/ai/drivers/Research.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 12,
            "isNew": false
          },
          {
            "id": "automation-driver-fabric-and-system-execution-driver-fabric-and-system-execution",
            "label": "Driver Fabric & System Execution",
            "route": "/ai/driver-fabric-system-execution",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 13,
            "isNew": false
          },
          {
            "id": "automation-driver-fabric-and-system-execution-ai-os-control",
            "label": "AI OS Control",
            "route": "/ai/os",
            "componentPath": "frontend/src/pages/ai/Os.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 14,
            "isNew": false
          },
          {
            "id": "automation-driver-fabric-and-system-execution-ai-operations",
            "label": "AI Operations",
            "route": "/ai/operations",
            "componentPath": "frontend/src/pages/ai/Operations.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 15,
            "isNew": false
          }
        ]
      },
      {
        "id": "automation-capsules-and-workflow-automation",
        "label": "Capsules & Workflow Automation",
        "homeRoute": "/ai/capsules-and-workflow-automation",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "automation-capsules-and-workflow-automation-project-ledger",
            "label": "Project Ledger",
            "route": "/ai/capsules/ledger",
            "componentPath": "frontend/src/pages/ai/capsules/Ledger.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "automation-capsules-and-workflow-automation-lineage-and-replay",
            "label": "Lineage & Replay",
            "route": "/ai/capsules/lineage",
            "componentPath": "frontend/src/pages/ai/capsules/Lineage.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "automation-capsules-and-workflow-automation-operator-studio",
            "label": "Operator Studio",
            "route": "/ai/capsules/operator-studio",
            "componentPath": "frontend/src/pages/ai/capsules/OperatorStudio.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "automation-capsules-and-workflow-automation-capsule-templates",
            "label": "Capsule Templates",
            "route": "/ai/capsules/templates",
            "componentPath": "frontend/src/pages/ai/capsules/Templates.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "automation-capsules-and-workflow-automation-my-stack-capsules",
            "label": "My Stack Capsules",
            "route": "/ai/capsules/my-stack",
            "componentPath": "frontend/src/pages/ai/capsules/MyStack.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "automation-capsules-and-workflow-automation-capsule-builder",
            "label": "Capsule Builder",
            "route": "/ai/capsules/builder",
            "componentPath": "frontend/src/pages/ai/capsules/Builder.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "automation-capsules-and-workflow-automation-capsule-runtime-settings",
            "label": "Capsule Runtime Settings",
            "route": "/ai/capsules/runtime",
            "componentPath": "frontend/src/pages/ai/capsules/Runtime.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "automation-capsules-and-workflow-automation-secrets-and-inputs",
            "label": "Secrets & Inputs",
            "route": "/ai/capsules/secrets",
            "componentPath": "frontend/src/pages/ai/capsules/Secrets.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          },
          {
            "id": "automation-capsules-and-workflow-automation-capsule-marketplace",
            "label": "Capsule Marketplace",
            "route": "/ai/capsules",
            "componentPath": "frontend/src/pages/ai/Capsules.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9,
            "isNew": false
          },
          {
            "id": "automation-capsules-and-workflow-automation-approval-and-publishing",
            "label": "Approval & Publishing",
            "route": "/ai/capsules/publishing",
            "componentPath": "frontend/src/pages/ai/capsules/Publishing.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10,
            "isNew": false
          },
          {
            "id": "automation-capsules-and-workflow-automation-capsules-and-workflow-automation",
            "label": "Capsules & Workflow Automation",
            "route": "/ai/capsules-workflow-automation",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11,
            "isNew": false
          },
          {
            "id": "automation-capsules-and-workflow-automation-workflow-orchestrator",
            "label": "Workflow Orchestrator",
            "route": "/ai/workflows",
            "componentPath": "frontend/src/pages/ai/Workflows.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 12,
            "isNew": false
          },
          {
            "id": "automation-capsules-and-workflow-automation-scheduling-and-triggers",
            "label": "Scheduling & Triggers",
            "route": "/ai/workflows/triggers",
            "componentPath": "frontend/src/pages/ai/workflows/Triggers.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 13,
            "isNew": false
          },
          {
            "id": "automation-capsules-and-workflow-automation-workflow-observability",
            "label": "Workflow Observability",
            "route": "/ai/workflows/observability",
            "componentPath": "frontend/src/pages/ai/workflows/Observability.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 14,
            "isNew": false
          },
          {
            "id": "automation-capsules-and-workflow-automation-auto-fix-console",
            "label": "Auto-Fix Console",
            "route": "/ai/autofix",
            "componentPath": "frontend/src/pages/ai/Autofix.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 15,
            "isNew": false
          }
        ]
      },
      {
        "id": "automation-intent-processing",
        "label": "Intent Processing",
        "homeRoute": "/ai/intent-processing",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 3,
        "features": [
          {
            "id": "automation-intent-processing-intent-processing",
            "label": "Intent Processing",
            "route": "/ai/intent-processing",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "automation-intent-processing-intentprocessor",
            "label": "Intentprocessor",
            "route": "/ai-fabric/intent-processing/intent-processor",
            "componentPath": "frontend/src/pages/Aifabric/Intentprocessing/Intentprocessor.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "automation-intent-processing-intent-processor",
            "label": "Intent Processor",
            "route": "/ai/intents",
            "componentPath": "frontend/src/pages/ai/Intents.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "automation-intent-processing-overview",
            "label": "Overview",
            "route": "/automation/intent-processing/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "automation-intent-processing-intent-taxonomy-and-routing-rules",
            "label": "Intent Taxonomy & Routing Rules",
            "route": "/ai/intents/taxonomy",
            "componentPath": "frontend/src/pages/ai/intents/Taxonomy.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "automation-intent-processing-runbook",
            "label": "Runbook",
            "route": "/automation/intent-processing/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "automation-intent-processing-intent-logs-and-replay",
            "label": "Intent Logs & Replay",
            "route": "/ai/intents/logs",
            "componentPath": "frontend/src/pages/ai/intents/Logs.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "automation-intent-processing-systems-map",
            "label": "Systems Map",
            "route": "/ai/systems",
            "componentPath": "frontend/src/pages/ai/Systems.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "automation-intent-processing-system-dependency-graph",
            "label": "System Dependency Graph",
            "route": "/ai/systems/graph",
            "componentPath": "frontend/src/pages/ai/systems/Graph.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "automation-intent-processing-capability-registry",
            "label": "Capability Registry",
            "route": "/ai/capabilities",
            "componentPath": "frontend/src/pages/ai/Capabilities.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          }
        ]
      },
      {
        "id": "automation-edge-and-vision",
        "label": "Edge & Vision",
        "homeRoute": "/ai/edge-and-vision",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 4,
        "features": [
          {
            "id": "automation-edge-and-vision-edge-and-vision",
            "label": "Edge & Vision",
            "route": "/ai/edge-vision",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "automation-edge-and-vision-edge-computing",
            "label": "Edge Computing",
            "route": "/ai/edge",
            "componentPath": "frontend/src/pages/ai/Edge.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "automation-edge-and-vision-device-registry",
            "label": "Device Registry",
            "route": "/ai/edge/devices",
            "componentPath": "frontend/src/pages/ai/edge/Devices.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "automation-edge-and-vision-model-packaging-and-deployment",
            "label": "Model Packaging & Deployment",
            "route": "/ai/edge/deploy",
            "componentPath": "frontend/src/pages/ai/edge/Deploy.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "automation-edge-and-vision-computer-vision",
            "label": "Computer Vision",
            "route": "/ai/vision",
            "componentPath": "frontend/src/pages/ai/Vision.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "automation-edge-and-vision-camera-stream-integrations",
            "label": "Camera/Stream Integrations",
            "route": "/ai/vision/streams",
            "componentPath": "frontend/src/pages/ai/vision/Streams.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "automation-edge-and-vision-vision-pipelines",
            "label": "Vision Pipelines",
            "route": "/ai/vision/pipelines",
            "componentPath": "frontend/src/pages/ai/vision/Pipelines.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "automation-edge-and-vision-annotation-and-labeling",
            "label": "Annotation & Labeling",
            "route": "/ai/vision/labeling",
            "componentPath": "frontend/src/pages/ai/vision/Labeling.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          }
        ]
      },
      {
        "id": "automation-cognitive-agents-and-reasoning",
        "label": "Cognitive Agents & Reasoning",
        "homeRoute": "/ai/cognitive-agents-and-reasoning",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 5,
        "features": [
          {
            "id": "automation-cognitive-agents-and-reasoning-cognitive-agents-and-reasoning",
            "label": "Cognitive Agents & Reasoning",
            "route": "/ai/cognitive-agents-reasoning",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "automation-cognitive-agents-and-reasoning-ai-copilot",
            "label": "AI Copilot",
            "route": "/ai/copilot",
            "componentPath": "frontend/src/pages/ai/Copilot.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "automation-cognitive-agents-and-reasoning-personas-and-agents",
            "label": "Personas & Agents",
            "route": "/ai/personas",
            "componentPath": "frontend/src/pages/ai/Personas.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "automation-cognitive-agents-and-reasoning-prompt-instruction-library",
            "label": "Prompt/Instruction Library",
            "route": "/ai/prompts",
            "componentPath": "frontend/src/pages/ai/Prompts.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "automation-cognitive-agents-and-reasoning-project-intelligence",
            "label": "Project Intelligence",
            "route": "/ai/project-intelligence",
            "componentPath": "frontend/src/pages/ai/ProjectIntelligence.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "automation-cognitive-agents-and-reasoning-evaluation-and-benchmarks",
            "label": "Evaluation & Benchmarks",
            "route": "/ai/evals",
            "componentPath": "frontend/src/pages/ai/Evals.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "automation-cognitive-agents-and-reasoning-model-router-policy",
            "label": "Model Router / Policy",
            "route": "/ai/routing",
            "componentPath": "frontend/src/pages/ai/Routing.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "automation-cognitive-agents-and-reasoning-advanced-ai-engine",
            "label": "Advanced AI Engine",
            "route": "/ai/advanced",
            "componentPath": "frontend/src/pages/ai/Advanced.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          },
          {
            "id": "automation-cognitive-agents-and-reasoning-daemon-framework",
            "label": "Daemon Framework",
            "route": "/ai/daemons",
            "componentPath": "frontend/src/pages/ai/Daemons.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9,
            "isNew": false
          },
          {
            "id": "automation-cognitive-agents-and-reasoning-theoretical-reasoning-framework",
            "label": "Theoretical Reasoning Framework",
            "route": "/ai/trf",
            "componentPath": "frontend/src/pages/ai/Trf.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10,
            "isNew": false
          },
          {
            "id": "automation-cognitive-agents-and-reasoning-safety-and-alignment-overview",
            "label": "Safety & Alignment Overview",
            "route": "/ai/safety",
            "componentPath": "frontend/src/pages/ai/Safety.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11,
            "isNew": false
          },
          {
            "id": "automation-cognitive-agents-and-reasoning-agent-registry-and-lifecycle",
            "label": "Agent Registry & Lifecycle",
            "route": "/ai/agents/registry",
            "componentPath": "frontend/src/pages/ai/agents/Registry.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 12,
            "isNew": false
          }
        ]
      },
      {
        "id": "automation-mlops-and-neural-architecture",
        "label": "MLOps & Neural Architecture",
        "homeRoute": "/ai/mlops-and-neural-architecture",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 6,
        "features": [
          {
            "id": "automation-mlops-and-neural-architecture-mlops-and-neural-architecture",
            "label": "MLOps & Neural Architecture",
            "route": "/ai/mlops-neural-architecture",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "automation-mlops-and-neural-architecture-mlops",
            "label": "MLOps",
            "route": "/ai/mlops",
            "componentPath": "frontend/src/pages/ai/Mlops.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "automation-mlops-and-neural-architecture-model-registry",
            "label": "Model Registry",
            "route": "/ai/mlops/models",
            "componentPath": "frontend/src/pages/ai/mlops/Models.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "automation-mlops-and-neural-architecture-dataset-and-feature-store",
            "label": "Dataset & Feature Store",
            "route": "/ai/mlops/data",
            "componentPath": "frontend/src/pages/ai/mlops/Data.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "automation-mlops-and-neural-architecture-training-pipelines",
            "label": "Training Pipelines",
            "route": "/ai/mlops/pipelines",
            "componentPath": "frontend/src/pages/ai/mlops/Pipelines.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "automation-mlops-and-neural-architecture-deployment-and-serving",
            "label": "Deployment & Serving",
            "route": "/ai/mlops/serving",
            "componentPath": "frontend/src/pages/ai/mlops/Serving.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "automation-mlops-and-neural-architecture-drift-monitoring",
            "label": "Drift Monitoring",
            "route": "/ai/mlops/drift",
            "componentPath": "frontend/src/pages/ai/mlops/Drift.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "automation-mlops-and-neural-architecture-governance-gates",
            "label": "Governance Gates",
            "route": "/ai/mlops/approvals",
            "componentPath": "frontend/src/pages/ai/mlops/Approvals.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          },
          {
            "id": "automation-mlops-and-neural-architecture-nas-console",
            "label": "NAS Console",
            "route": "/ai/nas",
            "componentPath": "frontend/src/pages/ai/Nas.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9,
            "isNew": false
          },
          {
            "id": "automation-mlops-and-neural-architecture-experiment-console",
            "label": "Experiment Console",
            "route": "/ai/nas/experiments",
            "componentPath": "frontend/src/pages/ai/nas/Experiments.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10,
            "isNew": false
          },
          {
            "id": "automation-mlops-and-neural-architecture-nas-simulator",
            "label": "NAS Simulator",
            "route": "/ai/nas/simulator",
            "componentPath": "frontend/src/pages/ai/nas/Simulator.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11,
            "isNew": false
          }
        ]
      },
      {
        "id": "automation-capsules-workflow",
        "label": "Capsules Workflow",
        "homeRoute": "/ai/capsules-workflow",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 7,
        "features": [
          {
            "id": "automation-capsules-workflow-autofixconsole",
            "label": "Autofixconsole",
            "route": "/ai-fabric/capsules-workflow/auto-fix-console",
            "componentPath": "frontend/src/pages/Aifabric/Capsulesworkflow/Autofixconsole.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "automation-capsules-workflow-capsulemarketplace",
            "label": "Capsulemarketplace",
            "route": "/ai-fabric/capsules-workflow/capsule-marketplace",
            "componentPath": "frontend/src/pages/Aifabric/Capsulesworkflow/Capsulemarketplace.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "automation-capsules-workflow-lineagereplay",
            "label": "Lineagereplay",
            "route": "/ai-fabric/capsules-workflow/lineage-replay",
            "componentPath": "frontend/src/pages/Aifabric/Capsulesworkflow/Lineagereplay.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "automation-cognitive-agents",
        "label": "Cognitive Agents",
        "homeRoute": "/ai/cognitive-agents",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 8,
        "features": [
          {
            "id": "automation-cognitive-agents-aicopilot",
            "label": "Aicopilot",
            "route": "/ai-fabric/cognitive-agents/ai-copilot",
            "componentPath": "frontend/src/pages/Aifabric/Cognitiveagents/Aicopilot.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "automation-cognitive-agents-personasagents",
            "label": "Personasagents",
            "route": "/ai-fabric/cognitive-agents/personas-agents",
            "componentPath": "frontend/src/pages/Aifabric/Cognitiveagents/Personasagents.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "automation-cognitive-agents-overview",
            "label": "Overview",
            "route": "/automation/cognitive-agents/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "automation-cognitive-agents-overview",
            "label": "Overview",
            "route": "/automation/cognitive-agents/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "automation-edge-vision",
        "label": "Edge Vision",
        "homeRoute": "/ai/edge-vision-home",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 9,
        "features": [
          {
            "id": "automation-edge-vision-computervision",
            "label": "Computervision",
            "route": "/ai-fabric/edge-vision/computer-vision",
            "componentPath": "frontend/src/pages/Aifabric/Edgevision/Computervision.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "automation-edge-vision-edgecomputing",
            "label": "Edgecomputing",
            "route": "/ai-fabric/edge-vision/edge-computing",
            "componentPath": "frontend/src/pages/Aifabric/Edgevision/Edgecomputing.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "automation-edge-vision-overview",
            "label": "Overview",
            "route": "/automation/edge-vision/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "automation-edge-vision-overview",
            "label": "Overview",
            "route": "/automation/edge-vision/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "automation-mlops-neural-arch",
        "label": "Mlops Neural Arch",
        "homeRoute": "/ai/mlops-neural-arch",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 10,
        "features": [
          {
            "id": "automation-mlops-neural-arch-mlops",
            "label": "Mlops",
            "route": "/ai-fabric/mlops-neural-arch/mlops",
            "componentPath": "frontend/src/pages/Aifabric/Mlopsneuralarch/Mlops.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "automation-mlops-neural-arch-overview",
            "label": "Overview",
            "route": "/automation/mlops-neural-arch/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "automation-mlops-neural-arch-overview",
            "label": "Overview",
            "route": "/automation/mlops-neural-arch/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "automation-mlops-neural-arch-runbook",
            "label": "Runbook",
            "route": "/automation/mlops-neural-arch/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "automation-mlops-neural-arch-runbook",
            "label": "Runbook",
            "route": "/automation/mlops-neural-arch/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "automation-workflows-and-capsules",
        "label": "Workflows & Capsules",
        "homeRoute": "/ai/workflows-and-capsules",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 11,
        "features": [
          {
            "id": "automation-workflows-and-capsules-workflow-builder",
            "label": "Workflow Builder",
            "route": "/automation/workflows/builder",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "automation-workflows-and-capsules-overview",
            "label": "Overview",
            "route": "/automation/workflows-and-capsules/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "automation-workflows-and-capsules-runbook",
            "label": "Runbook",
            "route": "/automation/workflows-and-capsules/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "automation-automation-hub",
        "label": "Automation Hub",
        "homeRoute": "/ai/automation-hub",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 12,
        "features": [
          {
            "id": "automation-automation-hub-automation-home",
            "label": "Automation Home",
            "route": "/ai",
            "componentPath": "frontend/src/pages/Ai.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "automation-automation-hub-tooling-lab",
            "label": "Tooling Lab",
            "route": "/ai/tooling-lab",
            "componentPath": "frontend/src/pages/ToolingLab.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "automation-automation-hub-overview",
            "label": "Overview",
            "route": "/automation/automation-hub/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      }
    ]
  },
  {
    "id": "settings",
    "label": "Settings",
    "path": "/settings",
    "actorScope": "both",
    "order": 5,
    "categories": [
      {
        "id": "settings-user-and-tenant-settings",
        "label": "User & Tenant Settings",
        "homeRoute": "/settings/user-and-tenant-settings",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "settings-user-and-tenant-settings-user-and-tenant-settings",
            "label": "User & Tenant Settings",
            "route": "/settings/user-tenant-settings",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "settings-user-and-tenant-settings-enterprise-user-and-tenant-settings",
            "label": "Enterprise User & Tenant Settings",
            "route": "/settings/enterprise/user-tenant",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "settings-user-and-tenant-settings-settings",
            "label": "Settings",
            "route": "/settings/user-tenant-settings/settings",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "settings-user-and-tenant-settings-team-and-members",
            "label": "Team & Members",
            "route": "/settings/team",
            "componentPath": "frontend/src/pages/settings/Team.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "settings-user-and-tenant-settings-user-profile",
            "label": "User Profile",
            "route": "/settings/profile",
            "componentPath": "frontend/src/pages/settings/Profile.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "settings-user-and-tenant-settings-tenancy-and-org-settings",
            "label": "Tenancy & Org Settings",
            "route": "/settings/tenant",
            "componentPath": "frontend/src/pages/settings/Tenant.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "settings-user-and-tenant-settings-preferences",
            "label": "Preferences",
            "route": "/settings/preferences",
            "componentPath": "frontend/src/pages/settings/Preferences.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "settings-user-and-tenant-settings-audit-settings",
            "label": "Audit Settings",
            "route": "/settings/audit",
            "componentPath": "frontend/src/pages/settings/Audit.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "settings-user-and-tenant-settings-notifications",
            "label": "Notifications",
            "route": "/settings/notifications",
            "componentPath": "frontend/src/pages/settings/Notifications.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "settings-user-and-tenant-settings-integrations-credentials",
            "label": "Integrations Credentials",
            "route": "/settings/credentials",
            "componentPath": "frontend/src/pages/settings/Credentials.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "settings-user-and-tenant-settings-api-keys",
            "label": "API Keys",
            "route": "/settings/api-keys",
            "componentPath": "frontend/src/pages/settings/ApiKeys.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "settings-user-and-tenant-settings-settings",
            "label": "Settings",
            "route": "/settings",
            "componentPath": "frontend/src/pages/Settings.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          }
        ]
      },
      {
        "id": "settings-profile-and-preferences",
        "label": "Profile & Preferences",
        "homeRoute": "/settings/profile-and-preferences",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "settings-profile-and-preferences-preferences",
            "label": "Preferences",
            "route": "/settings/preferences",
            "componentPath": "frontend/src/pages/settings/Preferences.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "settings-profile-and-preferences-overview",
            "label": "Overview",
            "route": "/settings/profile-and-preferences/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "settings-profile-and-preferences-runbook",
            "label": "Runbook",
            "route": "/settings/profile-and-preferences/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "settings-operations",
        "label": "Operations",
        "homeRoute": "/settings/operations",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 3,
        "features": [
          {
            "id": "settings-operations-overview",
            "label": "Overview",
            "route": "/settings/operations/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "settings-operations-runbook",
            "label": "Runbook",
            "route": "/settings/operations/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "settings-operations-evidence",
            "label": "Evidence",
            "route": "/settings/operations/evidence",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      }
    ]
  },
  {
    "id": "admin",
    "label": "Admin",
    "path": "/admin",
    "actorScope": "both",
    "order": 6,
    "categories": [
      {
        "id": "admin-users-and-roles",
        "label": "Users & Roles",
        "homeRoute": "/admin/users-and-roles",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "admin-users-and-roles-rbac-abac",
            "label": "RBAC/ABAC",
            "route": "/admin/access/rbac",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "admin-users-and-roles-overview",
            "label": "Overview",
            "route": "/admin/users-and-roles/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "admin-users-and-roles-runbook",
            "label": "Runbook",
            "route": "/admin/users-and-roles/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "admin-operations",
        "label": "Operations",
        "homeRoute": "/admin/operations",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "admin-operations-overview",
            "label": "Overview",
            "route": "/admin/operations/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "admin-operations-runbook",
            "label": "Runbook",
            "route": "/admin/operations/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "admin-operations-evidence",
            "label": "Evidence",
            "route": "/admin/operations/evidence",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "admin-admin-console",
        "label": "Admin Console",
        "homeRoute": "/admin/admin-console",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 3,
        "features": [
          {
            "id": "admin-admin-console-admin-console",
            "label": "Admin Console",
            "route": "/admin",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "admin-admin-console-overview",
            "label": "Overview",
            "route": "/admin/admin-console/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "admin-admin-console-runbook",
            "label": "Runbook",
            "route": "/admin/admin-console/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "admin-tenants",
        "label": "Tenants",
        "homeRoute": "/admin/tenants",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 4,
        "features": [
          {
            "id": "admin-tenants-tenant-registry",
            "label": "Tenant Registry",
            "route": "/admin/tenants/registry",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "admin-tenants-overview",
            "label": "Overview",
            "route": "/admin/tenants/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "admin-tenants-runbook",
            "label": "Runbook",
            "route": "/admin/tenants/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "admin-billing-and-usage",
        "label": "Billing & Usage",
        "homeRoute": "/admin/billing-and-usage",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 5,
        "features": [
          {
            "id": "admin-billing-and-usage-usage-ledger",
            "label": "Usage Ledger",
            "route": "/admin/billing/usage",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "admin-billing-and-usage-overview",
            "label": "Overview",
            "route": "/admin/billing-and-usage/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "admin-billing-and-usage-runbook",
            "label": "Runbook",
            "route": "/admin/billing-and-usage/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "admin-approvals",
        "label": "Approvals",
        "homeRoute": "/admin/approvals",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 6,
        "features": [
          {
            "id": "admin-approvals-approval-console",
            "label": "Approval Console",
            "route": "/admin/approvals/console",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "admin-approvals-overview",
            "label": "Overview",
            "route": "/admin/approvals/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "admin-approvals-runbook",
            "label": "Runbook",
            "route": "/admin/approvals/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      }
    ]
  },
  {
    "id": "workstation",
    "label": "Workstation",
    "path": "/workspaces",
    "actorScope": "both",
    "order": 7,
    "categories": [
      {
        "id": "workstation-dev-and-devops-workspace",
        "label": "Dev & DevOps Workspace",
        "homeRoute": "/workspaces/dev-and-devops-workspace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "workstation-dev-and-devops-workspace-commit-task-generator",
            "label": "Commit → Task Generator",
            "route": "/workspaces/dev/commit-tasks",
            "componentPath": "frontend/src/pages/workspaces/dev/CommitTasks.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workstation-dev-and-devops-workspace-code-merge-advisor",
            "label": "Code Merge Advisor",
            "route": "/workspaces/dev/merge-advisor",
            "componentPath": "frontend/src/pages/workspaces/dev/MergeAdvisor.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "workstation-dev-and-devops-workspace-code-review-queue",
            "label": "Code Review Queue",
            "route": "/workspaces/dev/reviews",
            "componentPath": "frontend/src/pages/workspaces/dev/Reviews.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "workstation-dev-and-devops-workspace-ci-cd-integration",
            "label": "CI/CD Integration",
            "route": "/workspaces/dev/cicd",
            "componentPath": "frontend/src/pages/workspaces/dev/Cicd.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "workstation-dev-and-devops-workspace-developer-tools",
            "label": "Developer Tools",
            "route": "/workspaces/dev/tools",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "workstation-dev-and-devops-workspace-dev-workspace",
            "label": "Dev Workspace",
            "route": "/workspaces/dev",
            "componentPath": "frontend/src/pages/workspaces/Dev.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "workstation-dev-and-devops-workspace-repo-and-branch-browser",
            "label": "Repo & Branch Browser",
            "route": "/workspaces/dev/repos",
            "componentPath": "frontend/src/pages/workspaces/dev/Repos.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "workstation-dev-and-devops-workspace-build-test-insights",
            "label": "Build/Test Insights",
            "route": "/workspaces/dev/build-insights",
            "componentPath": "frontend/src/pages/workspaces/dev/BuildInsights.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          },
          {
            "id": "workstation-dev-and-devops-workspace-dependency-updates",
            "label": "Dependency Updates",
            "route": "/workspaces/dev/deps",
            "componentPath": "frontend/src/pages/workspaces/dev/Deps.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9,
            "isNew": false
          },
          {
            "id": "workstation-dev-and-devops-workspace-release-notes-generator",
            "label": "Release Notes Generator",
            "route": "/workspaces/dev/release-notes",
            "componentPath": "frontend/src/pages/workspaces/dev/ReleaseNotes.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10,
            "isNew": false
          },
          {
            "id": "workstation-dev-and-devops-workspace-local-environment-health",
            "label": "Local Environment Health",
            "route": "/workspaces/dev/env-health",
            "componentPath": "frontend/src/pages/workspaces/dev/EnvHealth.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11,
            "isNew": false
          },
          {
            "id": "workstation-dev-and-devops-workspace-dev-and-devops-workspace",
            "label": "Dev & DevOps Workspace",
            "route": "/workspaces/dev-devops-workspace",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 12,
            "isNew": false
          },
          {
            "id": "workstation-dev-and-devops-workspace-developer-tools",
            "label": "Developer Tools",
            "route": "/work/tools",
            "componentPath": "frontend/src/pages/work/Tools.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 13,
            "isNew": false
          }
        ]
      },
      {
        "id": "workstation-writer-workspace",
        "label": "Writer Workspace",
        "homeRoute": "/workspaces/writer-workspace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "workstation-writer-workspace-templates",
            "label": "Templates",
            "route": "/workspaces/writer/templates",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workstation-writer-workspace-canon-and-lore",
            "label": "Canon & Lore",
            "route": "/workspaces/writer/canon",
            "componentPath": "frontend/src/pages/workspaces/writer/Canon.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "workstation-writer-workspace-narrative-guidance",
            "label": "Narrative Guidance",
            "route": "/workspaces/writer/narrative",
            "componentPath": "frontend/src/pages/workspaces/writer/Narrative.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "workstation-writer-workspace-story-qa-and-continuity",
            "label": "Story QA & Continuity",
            "route": "/workspaces/writer/qa",
            "componentPath": "frontend/src/pages/workspaces/writer/Qa.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "workstation-writer-workspace-export-and-publishing",
            "label": "Export & Publishing",
            "route": "/workspaces/writer/publishing",
            "componentPath": "frontend/src/pages/workspaces/writer/Publishing.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "workstation-writer-workspace-writer-workstation",
            "label": "Writer Workstation",
            "route": "/workspaces/writer",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "workstation-writer-workspace-style-guide-manager",
            "label": "Style Guide Manager",
            "route": "/workspaces/writer/style-guide",
            "componentPath": "frontend/src/pages/workspaces/writer/StyleGuide.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "workstation-writer-workspace-versioning-and-change-log",
            "label": "Versioning & Change Log",
            "route": "/workspaces/writer/versioning",
            "componentPath": "frontend/src/pages/workspaces/writer/Versioning.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          },
          {
            "id": "workstation-writer-workspace-citations-and-references",
            "label": "Citations & References",
            "route": "/workspaces/writer/citations",
            "componentPath": "frontend/src/pages/workspaces/writer/Citations.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9,
            "isNew": false
          },
          {
            "id": "workstation-writer-workspace-originality-check",
            "label": "Originality Check",
            "route": "/workspaces/writer/originality",
            "componentPath": "frontend/src/pages/workspaces/writer/Originality.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10,
            "isNew": false
          },
          {
            "id": "workstation-writer-workspace-writer-workspace",
            "label": "Writer Workspace",
            "route": "/workspaces/writer-workspace",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11,
            "isNew": false
          },
          {
            "id": "workstation-writer-workspace-writer-workstation",
            "label": "Writer Workstation",
            "route": "/work/writer",
            "componentPath": "frontend/src/pages/work/Writer.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 12,
            "isNew": false
          },
          {
            "id": "workstation-writer-workspace-templates",
            "label": "Templates",
            "route": "/work/templates",
            "componentPath": "frontend/src/pages/work/Templates.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 13,
            "isNew": false
          }
        ]
      },
      {
        "id": "workstation-cybersecurity-workspace",
        "label": "Cybersecurity Workspace",
        "homeRoute": "/workspaces/cybersecurity-workspace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 3,
        "features": [
          {
            "id": "workstation-cybersecurity-workspace-threat-modeling",
            "label": "Threat Modeling",
            "route": "/workspaces/cyber/threat-modeling",
            "componentPath": "frontend/src/pages/workspaces/cyber/ThreatModeling.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workstation-cybersecurity-workspace-findings-and-triage",
            "label": "Findings & Triage",
            "route": "/workspaces/cyber/findings",
            "componentPath": "frontend/src/pages/workspaces/cyber/Findings.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "workstation-cybersecurity-workspace-auto-remediation",
            "label": "Auto-Remediation",
            "route": "/workspaces/cyber/auto-remediation",
            "componentPath": "frontend/src/pages/workspaces/cyber/AutoRemediation.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "workstation-cybersecurity-workspace-incident-commander",
            "label": "Incident Commander",
            "route": "/workspaces/cyber/incidents",
            "componentPath": "frontend/src/pages/workspaces/cyber/Incidents.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "workstation-cybersecurity-workspace-security-guardian",
            "label": "Security Guardian",
            "route": "/workspaces/cyber",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "workstation-cybersecurity-workspace-policy-as-code-checks",
            "label": "Policy-as-Code Checks",
            "route": "/workspaces/cyber/policy-checks",
            "componentPath": "frontend/src/pages/workspaces/cyber/PolicyChecks.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "workstation-cybersecurity-workspace-vulnerability-scan-integrations",
            "label": "Vulnerability Scan Integrations",
            "route": "/workspaces/cyber/scanners",
            "componentPath": "frontend/src/pages/workspaces/cyber/Scanners.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "workstation-cybersecurity-workspace-threat-intel-feeds",
            "label": "Threat Intel Feeds",
            "route": "/workspaces/cyber/intel",
            "componentPath": "frontend/src/pages/workspaces/cyber/Intel.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          },
          {
            "id": "workstation-cybersecurity-workspace-playbooks-and-runbooks",
            "label": "Playbooks & Runbooks",
            "route": "/workspaces/cyber/playbooks",
            "componentPath": "frontend/src/pages/workspaces/cyber/Playbooks.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9,
            "isNew": false
          },
          {
            "id": "workstation-cybersecurity-workspace-cybersecurity-workspace",
            "label": "Cybersecurity Workspace",
            "route": "/workspaces/cybersecurity-workspace",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10,
            "isNew": false
          },
          {
            "id": "workstation-cybersecurity-workspace-security-guardian",
            "label": "Security Guardian",
            "route": "/ai/security",
            "componentPath": "frontend/src/pages/ai/Security.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11,
            "isNew": false
          }
        ]
      },
      {
        "id": "workstation-business-and-finance-workspace",
        "label": "Business & Finance Workspace",
        "homeRoute": "/workspaces/business-and-finance-workspace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 4,
        "features": [
          {
            "id": "workstation-business-and-finance-workspace-budget-planner",
            "label": "Budget Planner",
            "route": "/workspaces/finance/budgets",
            "componentPath": "frontend/src/pages/workspaces/finance/Budgets.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workstation-business-and-finance-workspace-strategy-simulation",
            "label": "Strategy Simulation",
            "route": "/workspaces/finance/scenarios",
            "componentPath": "frontend/src/pages/workspaces/finance/Scenarios.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "workstation-business-and-finance-workspace-business-console",
            "label": "Business Console",
            "route": "/workspaces/finance",
            "componentPath": "frontend/src/pages/workspaces/Finance.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "workstation-business-and-finance-workspace-kpi-dashboard",
            "label": "KPI Dashboard",
            "route": "/workspaces/finance/kpis",
            "componentPath": "frontend/src/pages/workspaces/finance/Kpis.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "workstation-business-and-finance-workspace-forecasting-lab",
            "label": "Forecasting Lab",
            "route": "/workspaces/finance/forecasting",
            "componentPath": "frontend/src/pages/workspaces/finance/Forecasting.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "workstation-business-and-finance-workspace-risk-register",
            "label": "Risk Register",
            "route": "/workspaces/finance/risk",
            "componentPath": "frontend/src/pages/workspaces/finance/Risk.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "workstation-business-and-finance-workspace-report-generator",
            "label": "Report Generator",
            "route": "/workspaces/finance/reports",
            "componentPath": "frontend/src/pages/workspaces/finance/Reports.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "workstation-business-and-finance-workspace-business-and-finance-workspace",
            "label": "Business & Finance Workspace",
            "route": "/workspaces/business-finance-workspace",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          }
        ]
      },
      {
        "id": "workstation-operator-and-sre-workspace",
        "label": "Operator & SRE Workspace",
        "homeRoute": "/workspaces/operator-and-sre-workspace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 5,
        "features": [
          {
            "id": "workstation-operator-and-sre-workspace-health-and-drift-monitors",
            "label": "Health & Drift Monitors",
            "route": "/workspaces/sre/health",
            "componentPath": "frontend/src/pages/workspaces/sre/Health.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workstation-operator-and-sre-workspace-reliability-dashboard",
            "label": "Reliability Dashboard",
            "route": "/workspaces/sre/reliability",
            "componentPath": "frontend/src/pages/workspaces/sre/Reliability.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "workstation-operator-and-sre-workspace-runbook-library",
            "label": "Runbook Library",
            "route": "/workspaces/sre/runbooks",
            "componentPath": "frontend/src/pages/workspaces/sre/Runbooks.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "workstation-operator-and-sre-workspace-sandbox-management",
            "label": "Sandbox Management",
            "route": "/workspaces/sre/sandbox",
            "componentPath": "frontend/src/pages/workspaces/sre/Sandbox.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "workstation-operator-and-sre-workspace-incident-timeline",
            "label": "Incident Timeline",
            "route": "/workspaces/sre/incidents",
            "componentPath": "frontend/src/pages/workspaces/sre/Incidents.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "workstation-operator-and-sre-workspace-sre-workspace",
            "label": "SRE Workspace",
            "route": "/workspaces/sre",
            "componentPath": "frontend/src/pages/workspaces/Sre.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "workstation-operator-and-sre-workspace-change-management",
            "label": "Change Management",
            "route": "/workspaces/sre/changes",
            "componentPath": "frontend/src/pages/workspaces/sre/Changes.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "workstation-operator-and-sre-workspace-capacity-and-cost-insights",
            "label": "Capacity & Cost Insights",
            "route": "/workspaces/sre/capacity-cost",
            "componentPath": "frontend/src/pages/workspaces/sre/CapacityCost.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          },
          {
            "id": "workstation-operator-and-sre-workspace-maintenance-windows",
            "label": "Maintenance Windows",
            "route": "/workspaces/sre/maintenance",
            "componentPath": "frontend/src/pages/workspaces/sre/Maintenance.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9,
            "isNew": false
          },
          {
            "id": "workstation-operator-and-sre-workspace-operator-and-sre-workspace",
            "label": "Operator & SRE Workspace",
            "route": "/workspaces/operator-sre-workspace",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10,
            "isNew": false
          }
        ]
      },
      {
        "id": "workstation-archive-and-continuity-workspace",
        "label": "Archive & Continuity Workspace",
        "homeRoute": "/workspaces/archive-and-continuity-workspace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 6,
        "features": [
          {
            "id": "workstation-archive-and-continuity-workspace-snapshot-manager",
            "label": "Snapshot Manager",
            "route": "/workspaces/archive/snapshots",
            "componentPath": "frontend/src/pages/workspaces/archive/Snapshots.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workstation-archive-and-continuity-workspace-restore-and-export",
            "label": "Restore & Export",
            "route": "/workspaces/archive/restore",
            "componentPath": "frontend/src/pages/workspaces/archive/Restore.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "workstation-archive-and-continuity-workspace-archive-workspace",
            "label": "Archive Workspace",
            "route": "/workspaces/archive",
            "componentPath": "frontend/src/pages/workspaces/Archive.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "workstation-archive-and-continuity-workspace-retention-policies",
            "label": "Retention Policies",
            "route": "/workspaces/archive/retention",
            "componentPath": "frontend/src/pages/workspaces/archive/Retention.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "workstation-archive-and-continuity-workspace-temporal-reconstruction",
            "label": "Temporal Reconstruction",
            "route": "/workspaces/archive/time-travel",
            "componentPath": "frontend/src/pages/workspaces/archive/TimeTravel.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "workstation-archive-and-continuity-workspace-archive-and-continuity-workspace",
            "label": "Archive & Continuity Workspace",
            "route": "/workspaces/archive-continuity-workspace",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          }
        ]
      },
      {
        "id": "workstation-master-stack-and-project-management-engine",
        "label": "Master Stack & Intelligence Project Management Engine",
        "homeRoute": "/workspaces/master-stack-and-project-management-engine",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 7,
        "features": [
          {
            "id": "workstation-master-stack-and-project-management-engine-project-management-system",
            "label": "Intelligence Project Management",
            "route": "/ipm",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workstation-master-stack-and-project-management-engine-projects",
            "label": "Projects",
            "route": "/ipm/projects",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "workstation-master-stack-and-project-management-engine-runs",
            "label": "Runs",
            "route": "/ipm/runs",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "workstation-master-stack-and-project-management-engine-documents",
            "label": "Documents",
            "route": "/ipm/documents",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "workstation-master-stack-and-project-management-engine-journal",
            "label": "Journal",
            "route": "/ipm/journal",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "workstation-master-stack-and-project-management-engine-finance",
            "label": "Finance",
            "route": "/ipm/finance",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "workstation-master-stack-and-project-management-engine-audit",
            "label": "Audit",
            "route": "/ipm/audit",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "workstation-master-stack-and-project-management-engine-settings",
            "label": "Settings",
            "route": "/ipm/settings",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          }
        ]
      },
      {
        "id": "workstation-dev-devops",
        "label": "Dev Devops",
        "homeRoute": "/workspaces/dev-devops",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 8,
        "features": [
          {
            "id": "workstation-dev-devops-cicd",
            "label": "Cicd",
            "route": "/workspaces/dev-devops/ci-cd",
            "componentPath": "frontend/src/pages/Workspaces/Devdevops/Cicd.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workstation-dev-devops-committasks",
            "label": "Committasks",
            "route": "/workspaces/dev-devops/commit-tasks",
            "componentPath": "frontend/src/pages/Workspaces/Devdevops/Committasks.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "workstation-dev-devops-mergeadvisor",
            "label": "Mergeadvisor",
            "route": "/workspaces/dev-devops/merge-advisor",
            "componentPath": "frontend/src/pages/Workspaces/Devdevops/Mergeadvisor.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "workstation-writer-workstation",
        "label": "Writer Workstation",
        "homeRoute": "/workspaces/writer-workstation",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 9,
        "features": [
          {
            "id": "workstation-writer-workstation-draft-editor",
            "label": "Draft Editor",
            "route": "/workstation/writer/editor",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workstation-writer-workstation-overview",
            "label": "Overview",
            "route": "/workstation/writer-workstation/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "workstation-writer-workstation-runbook",
            "label": "Runbook",
            "route": "/workstation/writer-workstation/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "workstation-dev-workstation",
        "label": "Dev Workstation",
        "homeRoute": "/workspaces/dev-workstation",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 10,
        "features": [
          {
            "id": "workstation-dev-workstation-commands-runner",
            "label": "Commands Runner",
            "route": "/workstation/dev/commands",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workstation-dev-workstation-overview",
            "label": "Overview",
            "route": "/workstation/dev-workstation/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "workstation-dev-workstation-runbook",
            "label": "Runbook",
            "route": "/workstation/dev-workstation/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "workstation-workstation-hub",
        "label": "Workstation Hub",
        "homeRoute": "/workspaces/workstation-hub",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 11,
        "features": [
          {
            "id": "workstation-workstation-hub-workspace-hub",
            "label": "Workspace Hub",
            "route": "/workspaces",
            "componentPath": "frontend/src/pages/Workspaces.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workstation-workstation-hub-overview",
            "label": "Overview",
            "route": "/workstation/workstation-hub/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "workstation-workstation-hub-runbook",
            "label": "Runbook",
            "route": "/workstation/workstation-hub/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "workstation-record-auditor-and-logbook-workspace",
        "label": "Record Auditor & Logbook Workspace",
        "homeRoute": "/workspaces/record-auditor-and-logbook-workspace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 12,
        "features": [
          {
            "id": "workstation-record-auditor-and-logbook-workspace-immutable-logbook-viewer",
            "label": "Immutable Logbook Viewer",
            "route": "/workspaces/auditor/logbook",
            "componentPath": "frontend/src/pages/workspaces/auditor/Logbook.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "workstation-record-auditor-and-logbook-workspace-evidence-trails",
            "label": "Evidence Trails",
            "route": "/workspaces/auditor/evidence",
            "componentPath": "frontend/src/pages/workspaces/auditor/Evidence.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "workstation-record-auditor-and-logbook-workspace-regulator-views",
            "label": "Regulator Views",
            "route": "/workspaces/auditor/regulator",
            "componentPath": "frontend/src/pages/workspaces/auditor/Regulator.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "workstation-record-auditor-and-logbook-workspace-evidence-requests",
            "label": "Evidence Requests",
            "route": "/workspaces/auditor/requests",
            "componentPath": "frontend/src/pages/workspaces/auditor/Requests.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "workstation-record-auditor-and-logbook-workspace-audit-reports",
            "label": "Audit Reports",
            "route": "/workspaces/auditor/reports",
            "componentPath": "frontend/src/pages/workspaces/auditor/Reports.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          },
          {
            "id": "workstation-record-auditor-and-logbook-workspace-record-auditor",
            "label": "Record Auditor",
            "route": "/workspaces/auditor",
            "componentPath": "frontend/src/pages/workspaces/Auditor.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6,
            "isNew": false
          },
          {
            "id": "workstation-record-auditor-and-logbook-workspace-record-auditor-and-logbook-workspace",
            "label": "Record Auditor & Logbook Workspace",
            "route": "/workspaces/record-auditor-logbook-workspace",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7,
            "isNew": false
          },
          {
            "id": "workstation-record-auditor-and-logbook-workspace-controls-mapping",
            "label": "Controls Mapping",
            "route": "/workspaces/auditor/controls",
            "componentPath": "frontend/src/pages/workspaces/auditor/Controls.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8,
            "isNew": false
          }
        ]
      }
    ]
  },
  {
    "id": "systems",
    "label": "Systems",
    "path": "/drivers",
    "actorScope": "both",
    "order": 8,
    "categories": [
      {
        "id": "systems-driver-registry",
        "label": "Driver Registry",
        "homeRoute": "/drivers/driver-registry",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "systems-driver-registry-driver-registry",
            "label": "Driver Registry",
            "route": "/drivers/registry",
            "componentPath": "frontend/src/pages/drivers/Registry.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "systems-driver-registry-overview",
            "label": "Overview",
            "route": "/systems/driver-registry/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "systems-driver-registry-runbook",
            "label": "Runbook",
            "route": "/systems/driver-registry/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "systems-software-and-saas-drivers",
        "label": "Software & SaaS Drivers",
        "homeRoute": "/drivers/software-and-saas-drivers",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "systems-software-and-saas-drivers-productivity-suites",
            "label": "Productivity Suites",
            "route": "/drivers/integrations/productivity",
            "componentPath": "frontend/src/pages/drivers/integrations/Productivity.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "systems-software-and-saas-drivers-code-hosts-and-ci-cd",
            "label": "Code Hosts & CI/CD",
            "route": "/drivers/integrations/code",
            "componentPath": "frontend/src/pages/drivers/integrations/Code.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "systems-software-and-saas-drivers-finance-and-banking",
            "label": "Finance & Banking",
            "route": "/drivers/integrations/finance",
            "componentPath": "frontend/src/pages/drivers/integrations/Finance.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "systems-software-and-saas-drivers-research-data-sources",
            "label": "Research Data Sources",
            "route": "/drivers/integrations/research",
            "componentPath": "frontend/src/pages/drivers/integrations/Research.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "systems-software-and-saas-drivers-legacy-and-mainframe",
            "label": "Legacy & Mainframe",
            "route": "/drivers/integrations/legacy",
            "componentPath": "frontend/src/pages/drivers/integrations/Legacy.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "systems-software-and-saas-drivers-cloud-providers",
            "label": "Cloud Providers",
            "route": "/drivers/integrations/cloud",
            "componentPath": "frontend/src/pages/drivers/integrations/Cloud.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          }
        ]
      },
      {
        "id": "systems-marketplace",
        "label": "Marketplace",
        "homeRoute": "/drivers/marketplace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 3,
        "features": [
          {
            "id": "systems-marketplace-reviews-and-ratings",
            "label": "Reviews & Ratings",
            "route": "/drivers/marketplace/reviews",
            "componentPath": "frontend/src/pages/drivers/marketplace/Reviews.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "systems-marketplace-security-review-pipeline",
            "label": "Security Review Pipeline",
            "route": "/drivers/marketplace/security-review",
            "componentPath": "frontend/src/pages/drivers/marketplace/SecurityReview.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "systems-marketplace-marketplace",
            "label": "Marketplace",
            "route": "/drivers/marketplace",
            "componentPath": "frontend/src/pages/drivers/Marketplace.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "systems-driver-registry-and-management",
        "label": "Driver Registry & Management",
        "homeRoute": "/drivers/driver-registry-and-management",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 4,
        "features": [
          {
            "id": "systems-driver-registry-and-management-driver-registry-and-management",
            "label": "Driver Registry & Management",
            "route": "/drivers/driver-registry-management",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "systems-driver-registry-and-management-overview",
            "label": "Overview",
            "route": "/drivers/driver-registry-management/drivers",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "systems-driver-registry-and-management-driver-sdk",
            "label": "Driver SDK",
            "route": "/drivers/sdk",
            "componentPath": "frontend/src/pages/drivers/Sdk.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "systems-driver-registry-and-management-driver-testing-and-validation",
            "label": "Driver Testing & Validation",
            "route": "/drivers/testing",
            "componentPath": "frontend/src/pages/drivers/Testing.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "systems-driver-registry-and-management-runtime-permissions",
            "label": "Runtime Permissions",
            "route": "/drivers/permissions",
            "componentPath": "frontend/src/pages/drivers/Permissions.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "systems-driver-registry-and-management-versioning-and-deprecation",
            "label": "Versioning & Deprecation",
            "route": "/drivers/versioning",
            "componentPath": "frontend/src/pages/drivers/Versioning.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "systems-driver-registry-and-management-driver-analytics",
            "label": "Driver Analytics",
            "route": "/drivers/analytics",
            "componentPath": "frontend/src/pages/drivers/Analytics.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "systems-driver-registry-and-management-publishing-flow",
            "label": "Publishing Flow",
            "route": "/drivers/publishing",
            "componentPath": "frontend/src/pages/drivers/Publishing.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          },
          {
            "id": "systems-driver-registry-and-management-overview",
            "label": "Overview",
            "route": "/integrations",
            "componentPath": "frontend/src/pages/Integrations.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9,
            "isNew": false
          }
        ]
      },
      {
        "id": "systems-driver-packs-and-marketplace",
        "label": "Driver Packs & Marketplace",
        "homeRoute": "/drivers/driver-packs-and-marketplace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 5,
        "features": [
          {
            "id": "systems-driver-packs-and-marketplace-driver-packs-and-marketplace",
            "label": "Driver Packs & Marketplace",
            "route": "/drivers/driver-packs-marketplace",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "systems-driver-packs-and-marketplace-driver-packs",
            "label": "Driver Packs",
            "route": "/drivers/packs",
            "componentPath": "frontend/src/pages/drivers/Packs.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "systems-driver-packs-and-marketplace-pack-builder",
            "label": "Pack Builder",
            "route": "/drivers/packs/builder",
            "componentPath": "frontend/src/pages/drivers/packs/Builder.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "systems-driver-packs-and-marketplace-vertical-editions",
            "label": "Vertical Editions",
            "route": "/drivers/vertical-editions",
            "componentPath": "frontend/src/pages/drivers/VerticalEditions.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "systems-driver-packs-and-marketplace-enterprise-app-store",
            "label": "Enterprise App Store",
            "route": "/drivers/enterprise-store",
            "componentPath": "frontend/src/pages/drivers/EnterpriseStore.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "systems-driver-packs-and-marketplace-licensing-and-entitlements",
            "label": "Licensing & Entitlements",
            "route": "/drivers/licensing",
            "componentPath": "frontend/src/pages/drivers/Licensing.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          }
        ]
      },
      {
        "id": "systems-risk-and-governance",
        "label": "Risk & Governance",
        "homeRoute": "/drivers/risk-and-governance",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 6,
        "features": [
          {
            "id": "systems-risk-and-governance-risk-and-governance",
            "label": "Risk & Governance",
            "route": "/drivers/risk-governance",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "systems-risk-and-governance-third-party-risk",
            "label": "Third-Party Risk",
            "route": "/drivers/risk",
            "componentPath": "frontend/src/pages/drivers/Risk.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "systems-risk-and-governance-vendor-inventory",
            "label": "Vendor Inventory",
            "route": "/drivers/risk/vendors",
            "componentPath": "frontend/src/pages/drivers/risk/Vendors.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "systems-risk-and-governance-risk-assessments",
            "label": "Risk Assessments",
            "route": "/drivers/risk/assessments",
            "componentPath": "frontend/src/pages/drivers/risk/Assessments.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "systems-risk-and-governance-remediation-tracker",
            "label": "Remediation Tracker",
            "route": "/drivers/risk/remediation",
            "componentPath": "frontend/src/pages/drivers/risk/Remediation.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "systems-risk-and-governance-exceptions-and-approvals",
            "label": "Exceptions & Approvals",
            "route": "/drivers/risk/exceptions",
            "componentPath": "frontend/src/pages/drivers/risk/Exceptions.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          }
        ]
      },
      {
        "id": "systems-connectors-and-integrations",
        "label": "Connectors & Integrations",
        "homeRoute": "/drivers/connectors-and-integrations",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 7,
        "features": [
          {
            "id": "systems-connectors-and-integrations-connectors-and-integrations",
            "label": "Connectors & Integrations",
            "route": "/drivers/connectors-integrations",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "systems-connectors-and-integrations-connectors-overview",
            "label": "Connectors Overview",
            "route": "/drivers/connectors-integrations/connectors",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "systems-connectors-and-integrations-credential-vault",
            "label": "Credential Vault",
            "route": "/drivers/connectors-integrations/credentials",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "systems-connectors-and-integrations-api-connectors",
            "label": "API Connectors",
            "route": "/drivers/connectors-integrations/api-connectors",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "systems-connectors-and-integrations-mcp-gateway",
            "label": "MCP Gateway",
            "route": "/drivers/connectors-integrations/mcp-gateway",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "systems-connectors-and-integrations-office-realtime",
            "label": "Office Realtime",
            "route": "/drivers/connectors-integrations/office",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "systems-connectors-and-integrations-webhooks-and-events",
            "label": "Webhooks & Events",
            "route": "/drivers/connectors-integrations/webhooks",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "systems-connectors-and-integrations-data-mapping-and-transformations",
            "label": "Data Mapping & Transformations",
            "route": "/drivers/connectors-integrations/mappings",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          },
          {
            "id": "systems-connectors-and-integrations-connector-health",
            "label": "Connector Health",
            "route": "/drivers/connectors-integrations/health",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9,
            "isNew": false
          },
          {
            "id": "systems-connectors-and-integrations-rate-limits-and-quotas",
            "label": "Rate Limits & Quotas",
            "route": "/drivers/connectors-integrations/rate-limits",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10,
            "isNew": false
          },
          {
            "id": "systems-connectors-and-integrations-connectors-overview",
            "label": "Connectors Overview",
            "route": "/integrations/connectors",
            "componentPath": "frontend/src/pages/integrations/Connectors.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11,
            "isNew": false
          },
          {
            "id": "systems-connectors-and-integrations-credential-vault",
            "label": "Credential Vault",
            "route": "/integrations/credentials",
            "componentPath": "frontend/src/pages/integrations/Credentials.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 12,
            "isNew": false
          },
          {
            "id": "systems-connectors-and-integrations-api-connectors",
            "label": "API Connectors",
            "route": "/integrations/api-connectors",
            "componentPath": "frontend/src/pages/integrations/ApiConnectors.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 13,
            "isNew": false
          },
          {
            "id": "systems-connectors-and-integrations-mcp-gateway",
            "label": "MCP Gateway",
            "route": "/integrations/mcp-gateway",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 14,
            "isNew": false
          },
          {
            "id": "systems-connectors-and-integrations-office-realtime",
            "label": "Office Realtime",
            "route": "/integrations/office",
            "componentPath": "frontend/src/pages/integrations/Office.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 15,
            "isNew": false
          },
          {
            "id": "systems-connectors-and-integrations-webhooks-and-events",
            "label": "Webhooks & Events",
            "route": "/integrations/webhooks",
            "componentPath": "frontend/src/pages/integrations/Webhooks.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 16,
            "isNew": false
          },
          {
            "id": "systems-connectors-and-integrations-data-mapping-and-transformations",
            "label": "Data Mapping & Transformations",
            "route": "/integrations/mappings",
            "componentPath": "frontend/src/pages/integrations/Mappings.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 17,
            "isNew": false
          },
          {
            "id": "systems-connectors-and-integrations-connector-health",
            "label": "Connector Health",
            "route": "/integrations/health",
            "componentPath": "frontend/src/pages/integrations/Health.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 18,
            "isNew": false
          },
          {
            "id": "systems-connectors-and-integrations-rate-limits-and-quotas",
            "label": "Rate Limits & Quotas",
            "route": "/integrations/rate-limits",
            "componentPath": "frontend/src/pages/integrations/RateLimits.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 19,
            "isNew": false
          }
        ]
      },
      {
        "id": "systems-deployment-models",
        "label": "Deployment Models",
        "homeRoute": "/operations/deployment-models",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 8,
        "features": [
          {
            "id": "systems-deployment-models-deploymentmodes",
            "label": "Deploymentmodes",
            "route": "/operations-infrastructure/deployment-models/deployment-modes",
            "componentPath": "frontend/src/pages/Operationsinfrastructure/Deploymentmodels/Deploymentmodes.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "systems-deployment-models-local-mode",
            "label": "Local Mode",
            "route": "/operations/deployment/local",
            "componentPath": "frontend/src/pages/operations/deployment/Local.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "systems-deployment-models-hybridedge",
            "label": "Hybridedge",
            "route": "/operations-infrastructure/deployment-models/hybrid-edge",
            "componentPath": "frontend/src/pages/Operationsinfrastructure/Deploymentmodels/Hybridedge.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "systems-deployment-models-cloud-enterprise",
            "label": "Cloud/Enterprise",
            "route": "/operations/deployment/cloud",
            "componentPath": "frontend/src/pages/operations/deployment/Cloud.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "systems-deployment-models-overview",
            "label": "Overview",
            "route": "/systems/deployment-models/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "systems-deployment-models-hybrid-and-edge",
            "label": "Hybrid & Edge",
            "route": "/operations/deployment/hybrid",
            "componentPath": "frontend/src/pages/operations/deployment/Hybrid.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "systems-deployment-models-blue-green-and-canary",
            "label": "Blue/Green & Canary",
            "route": "/operations/deployment/canary",
            "componentPath": "frontend/src/pages/operations/deployment/Canary.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "systems-deployment-models-deployment-modes",
            "label": "Deployment Modes",
            "route": "/operations/deployment",
            "componentPath": "frontend/src/pages/operations/Deployment.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          },
          {
            "id": "systems-deployment-models-kubernetes-deployment",
            "label": "Kubernetes Deployment",
            "route": "/operations/deployment/k8s",
            "componentPath": "frontend/src/pages/operations/deployment/K8s.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6,
            "isNew": false
          },
          {
            "id": "systems-deployment-models-airgapped-deployment",
            "label": "Airgapped Deployment",
            "route": "/operations/deployment/airgap",
            "componentPath": "frontend/src/pages/operations/deployment/Airgap.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7,
            "isNew": false
          },
          {
            "id": "systems-deployment-models-upgrade-channels",
            "label": "Upgrade Channels",
            "route": "/operations/deployment/channels",
            "componentPath": "frontend/src/pages/operations/deployment/Channels.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8,
            "isNew": false
          },
          {
            "id": "systems-deployment-models-deployment-models",
            "label": "Deployment Models",
            "route": "/operations/deployment-models",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 9,
            "isNew": false
          }
        ]
      },
      {
        "id": "systems-observability",
        "label": "Observability",
        "homeRoute": "/drivers/observability",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 9,
        "features": [
          {
            "id": "systems-observability-logs-and-traces",
            "label": "Logs & Traces",
            "route": "/systems/observability/logs-traces",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "systems-observability-overview",
            "label": "Overview",
            "route": "/systems/observability/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "systems-observability-runbook",
            "label": "Runbook",
            "route": "/systems/observability/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "systems-drivers-hub",
        "label": "Drivers Hub",
        "homeRoute": "/drivers/drivers-hub",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 10,
        "features": [
          {
            "id": "systems-drivers-hub-drivers-home",
            "label": "Drivers Home",
            "route": "/drivers",
            "componentPath": "frontend/src/pages/Drivers.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "systems-drivers-hub-operations-center",
            "label": "Operations Center",
            "route": "/operations",
            "componentPath": "frontend/src/pages/Operations.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "systems-drivers-hub-overview",
            "label": "Overview",
            "route": "/systems/drivers-hub/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "systems-performance-and-scalability",
        "label": "Performance & Scalability",
        "homeRoute": "/operations/performance-and-scalability",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 11,
        "features": [
          {
            "id": "systems-performance-and-scalability-performance",
            "label": "Performance",
            "route": "/operations/performance",
            "componentPath": "frontend/src/pages/operations/Performance.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "systems-performance-and-scalability-performance-and-scalability",
            "label": "Performance & Scalability",
            "route": "/operations/performance-scalability",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "systems-performance-and-scalability-scaling-strategies",
            "label": "Scaling Strategies",
            "route": "/operations/scaling",
            "componentPath": "frontend/src/pages/operations/Scaling.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "systems-performance-and-scalability-capacity-planning",
            "label": "Capacity Planning",
            "route": "/operations/capacity",
            "componentPath": "frontend/src/pages/operations/Capacity.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "systems-performance-and-scalability-load-testing",
            "label": "Load Testing",
            "route": "/operations/load-testing",
            "componentPath": "frontend/src/pages/operations/LoadTesting.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          },
          {
            "id": "systems-performance-and-scalability-backpressure-and-throttling",
            "label": "Backpressure & Throttling",
            "route": "/operations/backpressure",
            "componentPath": "frontend/src/pages/operations/Backpressure.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6,
            "isNew": false
          },
          {
            "id": "systems-performance-and-scalability-reliability-patterns",
            "label": "Reliability Patterns",
            "route": "/operations/reliability",
            "componentPath": "frontend/src/pages/operations/Reliability.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7,
            "isNew": false
          },
          {
            "id": "systems-performance-and-scalability-driver-performance",
            "label": "Driver Performance",
            "route": "/operations/driver-performance",
            "componentPath": "frontend/src/pages/operations/DriverPerformance.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8,
            "isNew": false
          },
          {
            "id": "systems-performance-and-scalability-cost-performance-tradeoffs",
            "label": "Cost/Performance Tradeoffs",
            "route": "/operations/cost-performance",
            "componentPath": "frontend/src/pages/operations/CostPerformance.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 9,
            "isNew": false
          }
        ]
      },
      {
        "id": "systems-upgrades-and-migration",
        "label": "Upgrades & Migration",
        "homeRoute": "/operations/upgrades-and-migration",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 12,
        "features": [
          {
            "id": "systems-upgrades-and-migration-upgrades-and-migration",
            "label": "Upgrades & Migration",
            "route": "/operations/upgrades-migration",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "systems-upgrades-and-migration-upgrades",
            "label": "Upgrades",
            "route": "/operations/upgrades",
            "componentPath": "frontend/src/pages/operations/Upgrades.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "systems-upgrades-and-migration-change-logs-and-release-notes",
            "label": "Change Logs & Release Notes",
            "route": "/operations/releases",
            "componentPath": "frontend/src/pages/operations/Releases.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "systems-upgrades-and-migration-compatibility-matrix",
            "label": "Compatibility Matrix",
            "route": "/operations/compatibility",
            "componentPath": "frontend/src/pages/operations/Compatibility.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "systems-upgrades-and-migration-migration",
            "label": "Migration",
            "route": "/operations/migration",
            "componentPath": "frontend/src/pages/operations/Migration.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          },
          {
            "id": "systems-upgrades-and-migration-rollback-strategy",
            "label": "Rollback Strategy",
            "route": "/operations/rollback",
            "componentPath": "frontend/src/pages/operations/Rollback.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6,
            "isNew": false
          }
        ]
      },
      {
        "id": "systems-failure-modes-and-resilience",
        "label": "Failure Modes & Resilience",
        "homeRoute": "/operations/failure-modes-and-resilience",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 13,
        "features": [
          {
            "id": "systems-failure-modes-and-resilience-failure-modes-and-resilience",
            "label": "Failure Modes & Resilience",
            "route": "/operations/failure-modes-resilience",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "systems-failure-modes-and-resilience-failure-modes",
            "label": "Failure Modes",
            "route": "/operations/failure",
            "componentPath": "frontend/src/pages/operations/Failure.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "systems-failure-modes-and-resilience-detection-mechanisms",
            "label": "Detection Mechanisms",
            "route": "/operations/detection",
            "componentPath": "frontend/src/pages/operations/Detection.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "systems-failure-modes-and-resilience-recovery-strategies",
            "label": "Recovery Strategies",
            "route": "/operations/recovery",
            "componentPath": "frontend/src/pages/operations/Recovery.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "systems-failure-modes-and-resilience-data-loss-protection",
            "label": "Data Loss Protection",
            "route": "/operations/data-protection",
            "componentPath": "frontend/src/pages/operations/DataProtection.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          },
          {
            "id": "systems-failure-modes-and-resilience-business-continuity-and-dr",
            "label": "Business Continuity & DR",
            "route": "/operations/bc-dr",
            "componentPath": "frontend/src/pages/operations/BcDr.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6,
            "isNew": false
          },
          {
            "id": "systems-failure-modes-and-resilience-dr-drills",
            "label": "DR Drills",
            "route": "/operations/bc-dr/drills",
            "componentPath": "frontend/src/pages/operations/bc-dr/Drills.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7,
            "isNew": false
          },
          {
            "id": "systems-failure-modes-and-resilience-security-incidents",
            "label": "Security Incidents",
            "route": "/operations/security-incidents",
            "componentPath": "frontend/src/pages/operations/SecurityIncidents.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8,
            "isNew": false
          },
          {
            "id": "systems-failure-modes-and-resilience-chaos-engineering",
            "label": "Chaos Engineering",
            "route": "/operations/chaos",
            "componentPath": "frontend/src/pages/operations/Chaos.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 9,
            "isNew": false
          },
          {
            "id": "systems-failure-modes-and-resilience-postmortems",
            "label": "Postmortems",
            "route": "/operations/postmortems",
            "componentPath": "frontend/src/pages/operations/Postmortems.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 10,
            "isNew": false
          }
        ]
      },
      {
        "id": "systems-infrastructure-and-topology",
        "label": "Infrastructure & Topology",
        "homeRoute": "/operations/infrastructure-and-topology",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 14,
        "features": [
          {
            "id": "systems-infrastructure-and-topology-infrastructure-and-topology",
            "label": "Infrastructure & Topology",
            "route": "/operations/infrastructure-topology",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "systems-infrastructure-and-topology-configuration-management",
            "label": "Configuration Management",
            "route": "/operations/config",
            "componentPath": "frontend/src/pages/operations/Config.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "systems-infrastructure-and-topology-secrets-and-configuration-vault",
            "label": "Secrets & Configuration Vault",
            "route": "/operations/secrets",
            "componentPath": "frontend/src/pages/operations/Secrets.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "systems-infrastructure-and-topology-compute-cluster-management",
            "label": "Compute/Cluster Management",
            "route": "/operations/cluster",
            "componentPath": "frontend/src/pages/operations/Cluster.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "systems-infrastructure-and-topology-network-topology",
            "label": "Network Topology",
            "route": "/operations/topology",
            "componentPath": "frontend/src/pages/operations/Topology.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          },
          {
            "id": "systems-infrastructure-and-topology-network-monitoring",
            "label": "Network Monitoring",
            "route": "/operations/infrastructure-topology/network",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6,
            "isNew": false
          },
          {
            "id": "systems-infrastructure-and-topology-storage-topology",
            "label": "Storage Topology",
            "route": "/operations/storage",
            "componentPath": "frontend/src/pages/operations/Storage.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7,
            "isNew": false
          },
          {
            "id": "systems-infrastructure-and-topology-queues-and-search",
            "label": "Queues & Search",
            "route": "/operations/queues",
            "componentPath": "frontend/src/pages/operations/Queues.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8,
            "isNew": false
          },
          {
            "id": "systems-infrastructure-and-topology-service-dependencies",
            "label": "Service Dependencies",
            "route": "/operations/dependencies",
            "componentPath": "frontend/src/pages/operations/Dependencies.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 9,
            "isNew": false
          },
          {
            "id": "systems-infrastructure-and-topology-multi-region-and-dr",
            "label": "Multi-Region & DR",
            "route": "/operations/multi-region",
            "componentPath": "frontend/src/pages/operations/MultiRegion.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 10,
            "isNew": false
          },
          {
            "id": "systems-infrastructure-and-topology-hpc-integration",
            "label": "HPC Integration",
            "route": "/operations/hpc",
            "componentPath": "frontend/src/pages/operations/Hpc.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 11,
            "isNew": false
          },
          {
            "id": "systems-infrastructure-and-topology-network-monitoring",
            "label": "Network Monitoring",
            "route": "/systems/network",
            "componentPath": "frontend/src/pages/systems/Network.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 12,
            "isNew": false
          }
        ]
      }
    ]
  },
  {
    "id": "simulations",
    "label": "Simulations",
    "path": "/simulations",
    "actorScope": "both",
    "order": 9,
    "categories": [
      {
        "id": "simulations-digital-twin-and-enterprise-twin-workspace",
        "label": "Digital Twin & Enterprise Twin Workspace",
        "homeRoute": "/workspaces/digital-twin-and-enterprise-twin-workspace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "simulations-digital-twin-and-enterprise-twin-workspace-enterprise-twin",
            "label": "Enterprise Twin",
            "route": "/workspaces/twins/enterprise",
            "componentPath": "frontend/src/pages/workspaces/twins/Enterprise.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "simulations-digital-twin-and-enterprise-twin-workspace-reality-twin-mesh",
            "label": "Reality Twin Mesh",
            "route": "/workspaces/twins/reality-mesh",
            "componentPath": "frontend/src/pages/workspaces/twins/RealityMesh.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "simulations-digital-twin-and-enterprise-twin-workspace-scenario-runner",
            "label": "Scenario Runner",
            "route": "/workspaces/twins/scenarios",
            "componentPath": "frontend/src/pages/workspaces/twins/Scenarios.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "simulations-digital-twin-and-enterprise-twin-workspace-twin-templates",
            "label": "Twin Templates",
            "route": "/workspaces/twins/templates",
            "componentPath": "frontend/src/pages/workspaces/twins/Templates.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "simulations-digital-twin-and-enterprise-twin-workspace-twin-governance",
            "label": "Twin Governance",
            "route": "/workspaces/twins/governance",
            "componentPath": "frontend/src/pages/workspaces/twins/Governance.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "simulations-digital-twin-and-enterprise-twin-workspace-data-feeds-and-sync",
            "label": "Data Feeds & Sync",
            "route": "/workspaces/twins/feeds",
            "componentPath": "frontend/src/pages/workspaces/twins/Feeds.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "simulations-digital-twin-and-enterprise-twin-workspace-digital-twin-builder",
            "label": "Digital Twin Builder",
            "route": "/workspaces/twins",
            "componentPath": "frontend/src/pages/workspaces/Twins.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "simulations-digital-twin-and-enterprise-twin-workspace-digital-twin-and-enterprise-twin-workspace",
            "label": "Digital Twin & Enterprise Twin Workspace",
            "route": "/workspaces/digital-twin-enterprise-twin-workspace",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          }
        ]
      },
      {
        "id": "simulations-simulation-hub",
        "label": "Simulation Hub",
        "homeRoute": "/simulations/simulation-hub",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "simulations-simulation-hub-run-simulations",
            "label": "Run Simulations",
            "route": "/simulations/hub/run",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "simulations-simulation-hub-overview",
            "label": "Overview",
            "route": "/simulations/simulation-hub/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "simulations-simulation-hub-runbook",
            "label": "Runbook",
            "route": "/simulations/simulation-hub/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "simulations-simulation-home",
        "label": "Simulation Home",
        "homeRoute": "/simulations/simulation-home",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 3,
        "features": [
          {
            "id": "simulations-simulation-home-simulation-home",
            "label": "Simulation Home",
            "route": "/simulations",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "simulations-simulation-home-overview",
            "label": "Overview",
            "route": "/simulations/simulation-home/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "simulations-simulation-home-runbook",
            "label": "Runbook",
            "route": "/simulations/simulation-home/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "simulations-operations",
        "label": "Operations",
        "homeRoute": "/simulations/operations",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 4,
        "features": [
          {
            "id": "simulations-operations-overview",
            "label": "Overview",
            "route": "/simulations/operations/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "simulations-operations-runbook",
            "label": "Runbook",
            "route": "/simulations/operations/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "simulations-operations-evidence",
            "label": "Evidence",
            "route": "/simulations/operations/evidence",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "simulations-controls",
        "label": "Controls",
        "homeRoute": "/simulations/controls",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 5,
        "features": [
          {
            "id": "simulations-controls-overview",
            "label": "Overview",
            "route": "/simulations/controls/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "simulations-controls-runbook",
            "label": "Runbook",
            "route": "/simulations/controls/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "simulations-controls-evidence",
            "label": "Evidence",
            "route": "/simulations/controls/evidence",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      }
    ]
  },
  {
    "id": "research",
    "label": "Research",
    "path": "/roadmap",
    "actorScope": "both",
    "order": 10,
    "categories": [
      {
        "id": "research-research-and-simulation-workspace",
        "label": "Research & Simulation Workspace",
        "homeRoute": "/workspaces/research-and-simulation-workspace",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "research-research-and-simulation-workspace-unified-research-lab",
            "label": "Unified Research Lab",
            "route": "/workspaces/research/lab",
            "componentPath": "frontend/src/pages/workspaces/research/Lab.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "research-research-and-simulation-workspace-experiment-design",
            "label": "Experiment Design",
            "route": "/workspaces/research/experiments",
            "componentPath": "frontend/src/pages/workspaces/research/Experiments.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "research-research-and-simulation-workspace-simulation-workbench",
            "label": "Simulation Workbench",
            "route": "/workspaces/research/simulation",
            "componentPath": "frontend/src/pages/workspaces/research/Simulation.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "research-research-and-simulation-workspace-model-validation",
            "label": "Model Validation",
            "route": "/workspaces/research/validation",
            "componentPath": "frontend/src/pages/workspaces/research/Validation.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "research-research-and-simulation-workspace-digital-twin-builder",
            "label": "Digital Twin Builder",
            "route": "/workspaces/research/digital-twins",
            "componentPath": "frontend/src/pages/workspaces/research/DigitalTwins.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "research-research-and-simulation-workspace-hpc-orchestrator",
            "label": "HPC Orchestrator",
            "route": "/workspaces/research/hpc",
            "componentPath": "frontend/src/pages/workspaces/research/Hpc.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "research-research-and-simulation-workspace-research-hub",
            "label": "Research Hub",
            "route": "/workspaces/research",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "research-research-and-simulation-workspace-dataset-registry",
            "label": "Dataset Registry",
            "route": "/workspaces/research/datasets",
            "componentPath": "frontend/src/pages/workspaces/research/Datasets.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          },
          {
            "id": "research-research-and-simulation-workspace-notebook-lab-notes",
            "label": "Notebook / Lab Notes",
            "route": "/workspaces/research/notes",
            "componentPath": "frontend/src/pages/workspaces/research/Notes.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9,
            "isNew": false
          },
          {
            "id": "research-research-and-simulation-workspace-experiment-tracking",
            "label": "Experiment Tracking",
            "route": "/workspaces/research/tracking",
            "componentPath": "frontend/src/pages/workspaces/research/Tracking.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10,
            "isNew": false
          },
          {
            "id": "research-research-and-simulation-workspace-reproducibility-packs",
            "label": "Reproducibility Packs",
            "route": "/workspaces/research/reproducibility",
            "componentPath": "frontend/src/pages/workspaces/research/Reproducibility.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11,
            "isNew": false
          },
          {
            "id": "research-research-and-simulation-workspace-results-publishing",
            "label": "Results Publishing",
            "route": "/workspaces/research/publishing",
            "componentPath": "frontend/src/pages/workspaces/research/Publishing.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 12,
            "isNew": false
          },
          {
            "id": "research-research-and-simulation-workspace-research-and-simulation-workspace",
            "label": "Research & Simulation Workspace",
            "route": "/workspaces/research-simulation-workspace",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 13,
            "isNew": false
          },
          {
            "id": "research-research-and-simulation-workspace-research-hub",
            "label": "Research Hub",
            "route": "/research",
            "componentPath": "frontend/src/pages/Research.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 14,
            "isNew": false
          }
        ]
      },
      {
        "id": "research-research-simulation",
        "label": "Research Simulation",
        "homeRoute": "/workspaces/research-simulation",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "research-research-simulation-digitaltwins",
            "label": "Digitaltwins",
            "route": "/workspaces/research-simulation/digital-twins",
            "componentPath": "frontend/src/pages/Workspaces/Researchsimulation/Digitaltwins.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "research-research-simulation-overview",
            "label": "Overview",
            "route": "/research/research-simulation/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "research-research-simulation-overview",
            "label": "Overview",
            "route": "/research/research-simulation/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "research-research-simulation-runbook",
            "label": "Runbook",
            "route": "/research/research-simulation/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "research-research-simulation-runbook",
            "label": "Runbook",
            "route": "/research/research-simulation/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "research-projects-and-experiments",
        "label": "Projects & Experiments",
        "homeRoute": "/roadmap/projects-and-experiments",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 3,
        "features": [
          {
            "id": "research-projects-and-experiments-registry",
            "label": "Registry",
            "route": "/research/registry",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "research-projects-and-experiments-overview",
            "label": "Overview",
            "route": "/research/projects-and-experiments/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "research-projects-and-experiments-runbook",
            "label": "Runbook",
            "route": "/research/projects-and-experiments/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "research-roadmap-and-future",
        "label": "Roadmap & Future",
        "homeRoute": "/roadmap/roadmap-and-future",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 4,
        "features": [
          {
            "id": "research-roadmap-and-future-roadmap-hub",
            "label": "Roadmap Hub",
            "route": "/roadmap",
            "componentPath": "frontend/src/pages/Roadmap.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "research-roadmap-and-future-future-capabilities",
            "label": "Future Capabilities",
            "route": "/roadmap/future-capabilities",
            "componentPath": "frontend/src/pages/roadmap/FutureCapabilities.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "research-roadmap-and-future-future-deck",
            "label": "Future Deck",
            "route": "/future",
            "componentPath": "frontend/src/pages/Future.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "research-future-capabilities",
        "label": "Future Capabilities",
        "homeRoute": "/roadmap/future-capabilities",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 5,
        "features": [
          {
            "id": "research-future-capabilities-long-term-bets",
            "label": "Long-Term Bets",
            "route": "/roadmap/future",
            "componentPath": "frontend/src/pages/roadmap/Future.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "research-future-capabilities-overview",
            "label": "Overview",
            "route": "/research/future-capabilities/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "research-future-capabilities-runbook",
            "label": "Runbook",
            "route": "/research/future-capabilities/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "research-risk-register",
        "label": "Risk Register",
        "homeRoute": "/roadmap/risk-register",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 6,
        "features": [
          {
            "id": "research-risk-register-risk-register",
            "label": "Risk Register",
            "route": "/roadmap/risks",
            "componentPath": "frontend/src/pages/roadmap/Risks.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "research-risk-register-overview",
            "label": "Overview",
            "route": "/research/risk-register/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "research-risk-register-runbook",
            "label": "Runbook",
            "route": "/research/risk-register/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "research-open-questions",
        "label": "Open Questions",
        "homeRoute": "/roadmap/open-questions",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 7,
        "features": [
          {
            "id": "research-open-questions-open-questions",
            "label": "Open Questions",
            "route": "/roadmap/questions",
            "componentPath": "frontend/src/pages/roadmap/Questions.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "research-open-questions-overview",
            "label": "Overview",
            "route": "/research/open-questions/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "research-open-questions-runbook",
            "label": "Runbook",
            "route": "/research/open-questions/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "research-roadmap-and-planning",
        "label": "Roadmap & Planning",
        "homeRoute": "/roadmap/roadmap-and-planning",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 8,
        "features": [
          {
            "id": "research-roadmap-and-planning-roadmap-and-planning",
            "label": "Roadmap & Planning",
            "route": "/roadmap/roadmap-planning",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "research-roadmap-and-planning-roadmap-overview",
            "label": "Roadmap Overview",
            "route": "/roadmap/overview",
            "componentPath": "frontend/src/pages/roadmap/Overview.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "research-roadmap-and-planning-phased-delivery",
            "label": "Phased Delivery",
            "route": "/roadmap/phases",
            "componentPath": "frontend/src/pages/roadmap/Phases.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "research-roadmap-and-planning-milestones",
            "label": "Milestones",
            "route": "/roadmap/milestones",
            "componentPath": "frontend/src/pages/roadmap/Milestones.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          }
        ]
      },
      {
        "id": "research-spec-maintenance",
        "label": "Spec Maintenance",
        "homeRoute": "/roadmap/spec-maintenance",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 9,
        "features": [
          {
            "id": "research-spec-maintenance-spec-maintenance",
            "label": "Spec Maintenance",
            "route": "/roadmap/spec-maintenance",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "research-spec-maintenance-spec-versioning",
            "label": "Spec Versioning",
            "route": "/roadmap/spec",
            "componentPath": "frontend/src/pages/roadmap/Spec.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "research-spec-maintenance-deprecations",
            "label": "Deprecations",
            "route": "/roadmap/deprecations",
            "componentPath": "frontend/src/pages/roadmap/Deprecations.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "research-spec-maintenance-backward-compatibility-commitments",
            "label": "Backward Compatibility Commitments",
            "route": "/roadmap/compatibility",
            "componentPath": "frontend/src/pages/roadmap/Compatibility.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          }
        ]
      },
      {
        "id": "research-risks-and-decisions",
        "label": "Risks & Decisions",
        "homeRoute": "/roadmap/risks-and-decisions",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 10,
        "features": [
          {
            "id": "research-risks-and-decisions-risks-and-decisions",
            "label": "Risks & Decisions",
            "route": "/roadmap/risks-decisions",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "research-risks-and-decisions-decision-log",
            "label": "Decision Log",
            "route": "/roadmap/decisions",
            "componentPath": "frontend/src/pages/roadmap/Decisions.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "research-risks-and-decisions-known-gaps",
            "label": "Known Gaps",
            "route": "/roadmap/gaps",
            "componentPath": "frontend/src/pages/roadmap/Gaps.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      }
    ]
  },
  {
    "id": "encyclopedia",
    "label": "Encyclopedia",
    "path": "/vision",
    "actorScope": "both",
    "order": 11,
    "categories": [
      {
        "id": "encyclopedia-topics",
        "label": "Topics",
        "homeRoute": "/vision/topics",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "encyclopedia-topics-topics",
            "label": "Topics",
            "route": "/encyclopedia/topics",
            "componentPath": "frontend/src/pages/encyclopedia/EncyclopediaFeature.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "encyclopedia-topics-overview",
            "label": "Overview",
            "route": "/encyclopedia/topics/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-topics-overview",
            "label": "Overview",
            "route": "/encyclopedia/topics/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-topics-runbook",
            "label": "Runbook",
            "route": "/encyclopedia/topics/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "encyclopedia-topics-runbook",
            "label": "Runbook",
            "route": "/encyclopedia/topics/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "encyclopedia-explanations",
        "label": "Explanations",
        "homeRoute": "/vision/explanations",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "encyclopedia-explanations-explanations",
            "label": "Explanations",
            "route": "/encyclopedia/explanations",
            "componentPath": "frontend/src/pages/encyclopedia/EncyclopediaFeature.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "encyclopedia-explanations-explain-a-concept",
            "label": "Explain a Concept",
            "route": "/encyclopedia/explanations/explain",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-explanations-overview",
            "label": "Overview",
            "route": "/encyclopedia/explanations/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-explanations-overview",
            "label": "Overview",
            "route": "/encyclopedia/explanations/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "encyclopedia-explanations-runbook",
            "label": "Runbook",
            "route": "/encyclopedia/explanations/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "encyclopedia-history",
        "label": "History",
        "homeRoute": "/vision/history",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 3,
        "features": [
          {
            "id": "encyclopedia-history-history",
            "label": "History",
            "route": "/encyclopedia/history",
            "componentPath": "frontend/src/pages/encyclopedia/EncyclopediaFeature.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "encyclopedia-history-history-timeline",
            "label": "History Timeline",
            "route": "/encyclopedia/history/timeline",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-history-overview",
            "label": "Overview",
            "route": "/encyclopedia/history/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-history-overview",
            "label": "Overview",
            "route": "/encyclopedia/history/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "encyclopedia-history-runbook",
            "label": "Runbook",
            "route": "/encyclopedia/history/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "encyclopedia-glossary",
        "label": "Glossary",
        "homeRoute": "/vision/glossary",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 4,
        "features": [
          {
            "id": "encyclopedia-glossary-glossary",
            "label": "Glossary",
            "route": "/encyclopedia/glossary",
            "componentPath": "frontend/src/pages/encyclopedia/EncyclopediaFeature.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "encyclopedia-glossary-overview",
            "label": "Overview",
            "route": "/encyclopedia/glossary/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-glossary-overview",
            "label": "Overview",
            "route": "/encyclopedia/glossary/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-glossary-runbook",
            "label": "Runbook",
            "route": "/encyclopedia/glossary/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "encyclopedia-glossary-runbook",
            "label": "Runbook",
            "route": "/encyclopedia/glossary/runbook-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "encyclopedia-core-os-engines",
        "label": "Core OS Engines",
        "homeRoute": "/vision/core-os-engines",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 5,
        "features": [
          {
            "id": "encyclopedia-core-os-engines-core-os-engines",
            "label": "Core OS Engines",
            "route": "/vision/core-os",
            "componentPath": "frontend/src/pages/future/Core_os.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "encyclopedia-core-os-engines-core-os-engines",
            "label": "Core OS Engines",
            "route": "/vision/core-os-engines",
            "componentPath": "frontend/src/pages/future/Core_os.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-core-os-engines-capability-matrix",
            "label": "Capability Matrix",
            "route": "/vision/core-os-engines/matrix",
            "componentPath": "frontend/src/pages/future/core_os/Matrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "encyclopedia-core-os-engines-core-os-engines",
            "label": "Core OS Engines",
            "route": "/future/core_os",
            "componentPath": "frontend/src/pages/future/Core_os.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "encyclopedia-core-os-engines-capability-matrix",
            "label": "Capability Matrix",
            "route": "/future/core_os/matrix",
            "componentPath": "frontend/src/pages/future/core_os/Matrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          }
        ]
      },
      {
        "id": "encyclopedia-advanced-capabilities",
        "label": "Advanced Capabilities",
        "homeRoute": "/vision/advanced-capabilities",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 6,
        "features": [
          {
            "id": "encyclopedia-advanced-capabilities-advanced-horizons",
            "label": "Advanced Horizons",
            "route": "/vision/advanced",
            "componentPath": "frontend/src/pages/future/Advanced.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "encyclopedia-advanced-capabilities-overview",
            "label": "Overview",
            "route": "/encyclopedia/advanced-capabilities/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-advanced-capabilities-runbook",
            "label": "Runbook",
            "route": "/encyclopedia/advanced-capabilities/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "encyclopedia-super-capabilities",
        "label": "Super Capabilities",
        "homeRoute": "/vision/super-capabilities",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 7,
        "features": [
          {
            "id": "encyclopedia-super-capabilities-super-capabilities",
            "label": "Super Capabilities",
            "route": "/vision/super",
            "componentPath": "frontend/src/pages/future/Super.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "encyclopedia-super-capabilities-super-capabilities",
            "label": "Super Capabilities",
            "route": "/vision/super-capabilities",
            "componentPath": "frontend/src/pages/future/Super.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-super-capabilities-capability-matrix",
            "label": "Capability Matrix",
            "route": "/vision/super-capabilities/matrix",
            "componentPath": "frontend/src/pages/future/super/Matrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "encyclopedia-super-capabilities-super-capabilities",
            "label": "Super Capabilities",
            "route": "/future/super",
            "componentPath": "frontend/src/pages/future/Super.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "encyclopedia-super-capabilities-capability-matrix",
            "label": "Capability Matrix",
            "route": "/future/super/matrix",
            "componentPath": "frontend/src/pages/future/super/Matrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          }
        ]
      },
      {
        "id": "encyclopedia-hyper-capabilities",
        "label": "Hyper Capabilities",
        "homeRoute": "/vision/hyper-capabilities",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 8,
        "features": [
          {
            "id": "encyclopedia-hyper-capabilities-hyper-network",
            "label": "Hyper Network",
            "route": "/vision/hyper",
            "componentPath": "frontend/src/pages/future/Hyper.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "encyclopedia-hyper-capabilities-overview",
            "label": "Overview",
            "route": "/encyclopedia/hyper-capabilities/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-hyper-capabilities-runbook",
            "label": "Runbook",
            "route": "/encyclopedia/hyper-capabilities/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "encyclopedia-ultra-capabilities",
        "label": "Ultra Capabilities",
        "homeRoute": "/vision/ultra-capabilities",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 9,
        "features": [
          {
            "id": "encyclopedia-ultra-capabilities-ultra-scale",
            "label": "Ultra Scale",
            "route": "/vision/ultra",
            "componentPath": "frontend/src/pages/future/Ultra.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "encyclopedia-ultra-capabilities-overview",
            "label": "Overview",
            "route": "/encyclopedia/ultra-capabilities/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-ultra-capabilities-runbook",
            "label": "Runbook",
            "route": "/encyclopedia/ultra-capabilities/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "encyclopedia-supreme-capabilities",
        "label": "Supreme Capabilities",
        "homeRoute": "/vision/supreme-capabilities",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 10,
        "features": [
          {
            "id": "encyclopedia-supreme-capabilities-supreme",
            "label": "Supreme",
            "route": "/vision/supreme",
            "componentPath": "frontend/src/pages/future/Supreme.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "encyclopedia-supreme-capabilities-supreme",
            "label": "Supreme",
            "route": "/future/supreme",
            "componentPath": "frontend/src/pages/future/Supreme.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-supreme-capabilities-capability-matrix",
            "label": "Capability Matrix",
            "route": "/vision/supreme/matrix",
            "componentPath": "frontend/src/pages/future/supreme/Matrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "encyclopedia-supreme-capabilities-capability-matrix",
            "label": "Capability Matrix",
            "route": "/future/supreme/matrix",
            "componentPath": "frontend/src/pages/future/supreme/Matrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          }
        ]
      },
      {
        "id": "encyclopedia-ascend-capabilities",
        "label": "Ascend Capabilities",
        "homeRoute": "/vision/ascend-capabilities",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 11,
        "features": [
          {
            "id": "encyclopedia-ascend-capabilities-ascend",
            "label": "Ascend",
            "route": "/vision/ascend",
            "componentPath": "frontend/src/pages/future/Ascend.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "encyclopedia-ascend-capabilities-ascend",
            "label": "Ascend",
            "route": "/future/ascend",
            "componentPath": "frontend/src/pages/future/Ascend.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-ascend-capabilities-capability-matrix",
            "label": "Capability Matrix",
            "route": "/vision/ascend/matrix",
            "componentPath": "frontend/src/pages/future/ascend/Matrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "encyclopedia-ascend-capabilities-capability-matrix",
            "label": "Capability Matrix",
            "route": "/future/ascend/matrix",
            "componentPath": "frontend/src/pages/future/ascend/Matrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          }
        ]
      },
      {
        "id": "encyclopedia-advanced-horizons",
        "label": "Advanced Horizons",
        "homeRoute": "/vision/advanced-horizons",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 12,
        "features": [
          {
            "id": "encyclopedia-advanced-horizons-advanced-horizons",
            "label": "Advanced Horizons",
            "route": "/vision/advanced-horizons",
            "componentPath": "frontend/src/pages/future/Advanced.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "encyclopedia-advanced-horizons-capability-matrix",
            "label": "Capability Matrix",
            "route": "/vision/advanced-horizons/matrix",
            "componentPath": "frontend/src/pages/future/advanced/Matrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-advanced-horizons-advanced-horizons",
            "label": "Advanced Horizons",
            "route": "/future/advanced",
            "componentPath": "frontend/src/pages/future/Advanced.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "encyclopedia-advanced-horizons-capability-matrix",
            "label": "Capability Matrix",
            "route": "/future/advanced/matrix",
            "componentPath": "frontend/src/pages/future/advanced/Matrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          }
        ]
      },
      {
        "id": "encyclopedia-meta-envelope",
        "label": "Meta Envelope",
        "homeRoute": "/vision/meta-envelope",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 13,
        "features": [
          {
            "id": "encyclopedia-meta-envelope-meta-envelope",
            "label": "Meta Envelope",
            "route": "/vision/meta-envelope",
            "componentPath": "frontend/src/pages/future/Meta.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "encyclopedia-meta-envelope-meta-envelope",
            "label": "Meta Envelope",
            "route": "/vision/meta",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-meta-envelope-capability-matrix",
            "label": "Capability Matrix",
            "route": "/vision/meta-envelope/matrix",
            "componentPath": "frontend/src/pages/future/meta/Matrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "encyclopedia-meta-envelope-meta-envelope",
            "label": "Meta Envelope",
            "route": "/future/meta",
            "componentPath": "frontend/src/pages/future/Meta.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "encyclopedia-meta-envelope-capability-matrix",
            "label": "Capability Matrix",
            "route": "/future/meta/matrix",
            "componentPath": "frontend/src/pages/future/meta/Matrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          }
        ]
      },
      {
        "id": "encyclopedia-hyper-network",
        "label": "Hyper Network",
        "homeRoute": "/vision/hyper-network",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 14,
        "features": [
          {
            "id": "encyclopedia-hyper-network-hyper-network",
            "label": "Hyper Network",
            "route": "/vision/hyper-network",
            "componentPath": "frontend/src/pages/future/Hyper.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "encyclopedia-hyper-network-capability-matrix",
            "label": "Capability Matrix",
            "route": "/vision/hyper-network/matrix",
            "componentPath": "frontend/src/pages/future/hyper/Matrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-hyper-network-hyper-network",
            "label": "Hyper Network",
            "route": "/future/hyper",
            "componentPath": "frontend/src/pages/future/Hyper.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "encyclopedia-hyper-network-capability-matrix",
            "label": "Capability Matrix",
            "route": "/future/hyper/matrix",
            "componentPath": "frontend/src/pages/future/hyper/Matrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          }
        ]
      },
      {
        "id": "encyclopedia-vision-deck-hub",
        "label": "Vision Deck Hub",
        "homeRoute": "/vision/vision-deck-hub",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 15,
        "features": [
          {
            "id": "encyclopedia-vision-deck-hub-vision-deck-hub",
            "label": "Vision Deck Hub",
            "route": "/vision/vision-deck-hub",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "encyclopedia-vision-deck-hub-vision-deck-hub",
            "label": "Vision Deck Hub",
            "route": "/vision/vision-deck-hub/vision",
            "componentPath": "frontend/src/pages/Vision.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-vision-deck-hub-vision-roadmap",
            "label": "Vision Roadmap",
            "route": "/vision/roadmap",
            "componentPath": "frontend/src/pages/vision/Roadmap.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "encyclopedia-vision-deck-hub-vision-glossary",
            "label": "Vision Glossary",
            "route": "/vision/glossary",
            "componentPath": "frontend/src/pages/vision/Glossary.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          },
          {
            "id": "encyclopedia-vision-deck-hub-vision-deck-hub",
            "label": "Vision Deck Hub",
            "route": "/vision",
            "componentPath": "frontend/src/pages/Vision.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5,
            "isNew": false
          }
        ]
      },
      {
        "id": "encyclopedia-ultra-scale",
        "label": "Ultra Scale",
        "homeRoute": "/vision/ultra-scale",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 16,
        "features": [
          {
            "id": "encyclopedia-ultra-scale-ultra-scale",
            "label": "Ultra Scale",
            "route": "/vision/ultra-scale",
            "componentPath": "frontend/src/pages/future/Ultra.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "encyclopedia-ultra-scale-capability-matrix",
            "label": "Capability Matrix",
            "route": "/vision/ultra-scale/matrix",
            "componentPath": "frontend/src/pages/future/ultra/Matrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "encyclopedia-ultra-scale-ultra-scale",
            "label": "Ultra Scale",
            "route": "/future/ultra",
            "componentPath": "frontend/src/pages/future/Ultra.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          },
          {
            "id": "encyclopedia-ultra-scale-capability-matrix",
            "label": "Capability Matrix",
            "route": "/future/ultra/matrix",
            "componentPath": "frontend/src/pages/future/ultra/Matrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4,
            "isNew": false
          }
        ]
      }
    ]
  },
  {
    "id": "libraries",
    "label": "Libraries",
    "path": "/docs",
    "actorScope": "both",
    "order": 12,
    "categories": [
      {
        "id": "libraries-getting-started",
        "label": "Getting Started",
        "homeRoute": "/docs/getting-started",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "libraries-getting-started-getting-started",
            "label": "Getting Started",
            "route": "/docs/getting-started",
            "componentPath": "frontend/src/pages/docs/GettingStarted.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "libraries-getting-started-overview",
            "label": "Overview",
            "route": "/libraries/getting-started/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "libraries-getting-started-runbook",
            "label": "Runbook",
            "route": "/libraries/getting-started/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "libraries-api-reference",
        "label": "API Reference",
        "homeRoute": "/docs/api-reference",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "libraries-api-reference-api-reference",
            "label": "API Reference",
            "route": "/docs/api",
            "componentPath": "frontend/src/pages/docs/Api.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "libraries-api-reference-sdks",
            "label": "SDKs",
            "route": "/docs/api/sdks",
            "componentPath": "frontend/src/pages/docs/api/Sdks.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "libraries-api-reference-auth-and-rate-limits",
            "label": "Auth & Rate Limits",
            "route": "/docs/api/auth",
            "componentPath": "frontend/src/pages/docs/api/Auth.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "libraries-api-reference-webhooks",
            "label": "Webhooks",
            "route": "/docs/api/webhooks",
            "componentPath": "frontend/src/pages/docs/api/Webhooks.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "libraries-api-reference-api-reference",
            "label": "API Reference",
            "route": "/docs/api-reference",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          }
        ]
      },
      {
        "id": "libraries-reference-artifacts",
        "label": "Reference Artifacts",
        "homeRoute": "/docs/reference-artifacts",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 3,
        "features": [
          {
            "id": "libraries-reference-artifacts-capsule-manifests",
            "label": "Capsule Manifests",
            "route": "/docs/reference/capsules",
            "componentPath": "frontend/src/pages/docs/reference/Capsules.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "libraries-reference-artifacts-driver-manifests",
            "label": "Driver Manifests",
            "route": "/docs/reference/drivers",
            "componentPath": "frontend/src/pages/docs/reference/Drivers.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "libraries-reference-artifacts-policy-examples",
            "label": "Policy Examples",
            "route": "/docs/reference/policies",
            "componentPath": "frontend/src/pages/docs/reference/Policies.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "libraries-reference-artifacts-evidence-pack-templates",
            "label": "Evidence Pack Templates",
            "route": "/docs/reference/evidence",
            "componentPath": "frontend/src/pages/docs/reference/Evidence.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "libraries-reference-artifacts-data-schemas",
            "label": "Data Schemas",
            "route": "/docs/reference/data",
            "componentPath": "frontend/src/pages/docs/reference/Data.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "libraries-reference-artifacts-ui-component-library",
            "label": "UI Component Library",
            "route": "/docs/reference/ui",
            "componentPath": "frontend/src/pages/docs/reference/Ui.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "libraries-reference-artifacts-reference-artifacts",
            "label": "Reference Artifacts",
            "route": "/docs/reference-artifacts",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "libraries-reference-artifacts-reference-hub",
            "label": "Reference Hub",
            "route": "/docs/reference",
            "componentPath": "frontend/src/pages/docs/Reference.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          }
        ]
      },
      {
        "id": "libraries-documentation-hub",
        "label": "Documentation Hub",
        "homeRoute": "/docs/documentation-hub",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 4,
        "features": [
          {
            "id": "libraries-documentation-hub-documentation-hub",
            "label": "Documentation Hub",
            "route": "/docs/documentation-hub",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "libraries-documentation-hub-docs-hub",
            "label": "Docs Hub",
            "route": "/docs/documentation-hub/docs",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "libraries-documentation-hub-tutorials",
            "label": "Tutorials",
            "route": "/docs/tutorials",
            "componentPath": "frontend/src/pages/docs/Tutorials.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "libraries-documentation-hub-glossary",
            "label": "Glossary",
            "route": "/docs/glossary",
            "componentPath": "frontend/src/pages/docs/Glossary.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "libraries-documentation-hub-technical-spec-sheet",
            "label": "Technical Spec Sheet",
            "route": "/docs/spec-sheet",
            "componentPath": "frontend/src/pages/docs/SpecSheet.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "libraries-documentation-hub-ssot-technical-docs",
            "label": "SSOT Technical Docs",
            "route": "/docs/documentation-hub/ssot-technical-docs",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "libraries-documentation-hub-release-notes",
            "label": "Release Notes",
            "route": "/docs/release-notes",
            "componentPath": "frontend/src/pages/docs/ReleaseNotes.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "libraries-documentation-hub-docs-hub",
            "label": "Docs Hub",
            "route": "/docs",
            "componentPath": "frontend/src/pages/Docs.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          }
        ]
      },
      {
        "id": "libraries-migration-and-integration",
        "label": "Migration & Integration",
        "homeRoute": "/docs/migration-and-integration",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 5,
        "features": [
          {
            "id": "libraries-migration-and-integration-migration-and-integration",
            "label": "Migration & Integration",
            "route": "/docs/migration-integration",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "libraries-migration-and-integration-migration-continued",
            "label": "Migration Continued",
            "route": "/docs/migration_continued.md",
            "componentPath": "frontend/src/pages/docs/Migration_continued.md.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "libraries-migration-and-integration-migration-guides",
            "label": "Migration Guides",
            "route": "/docs/migration",
            "componentPath": "frontend/src/pages/docs/Migration.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "libraries-migration-and-integration-integration-guides",
            "label": "Integration Guides",
            "route": "/docs/integrations",
            "componentPath": "frontend/src/pages/docs/Integrations.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "libraries-migration-and-integration-deployment-guides",
            "label": "Deployment Guides",
            "route": "/docs/deployment",
            "componentPath": "frontend/src/pages/docs/Deployment.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          }
        ]
      },
      {
        "id": "libraries-capsule-library",
        "label": "Capsule Library",
        "homeRoute": "/docs/capsule-library",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 6,
        "features": [
          {
            "id": "libraries-capsule-library-catalog",
            "label": "Catalog",
            "route": "/libraries/capsules/catalog",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "libraries-capsule-library-overview",
            "label": "Overview",
            "route": "/libraries/capsule-library/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "libraries-capsule-library-runbook",
            "label": "Runbook",
            "route": "/libraries/capsule-library/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "libraries-operations",
        "label": "Operations",
        "homeRoute": "/docs/operations",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 7,
        "features": [
          {
            "id": "libraries-operations-overview",
            "label": "Overview",
            "route": "/libraries/operations/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "libraries-operations-runbook",
            "label": "Runbook",
            "route": "/libraries/operations/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "libraries-operations-evidence",
            "label": "Evidence",
            "route": "/libraries/operations/evidence",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "libraries-controls",
        "label": "Controls",
        "homeRoute": "/docs/controls",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 8,
        "features": [
          {
            "id": "libraries-controls-overview",
            "label": "Overview",
            "route": "/libraries/controls/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1,
            "isNew": false
          },
          {
            "id": "libraries-controls-runbook",
            "label": "Runbook",
            "route": "/libraries/controls/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "libraries-controls-evidence",
            "label": "Evidence",
            "route": "/libraries/controls/evidence",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      }
    ]
  },
  {
    "id": "knowledge",
    "label": "Knowledge",
    "path": "/data",
    "actorScope": "both",
    "order": 13,
    "categories": [
      {
        "id": "knowledge-observability-stores",
        "label": "Observability Stores",
        "homeRoute": "/data/observability-stores",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "knowledge-observability-stores-observability-stores-overview",
            "label": "Observability Stores Overview",
            "route": "/data/observability",
            "componentPath": "frontend/src/pages/data/Observability.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "knowledge-observability-stores-retention-and-tiering",
            "label": "Retention & Tiering",
            "route": "/data/observability/tiering",
            "componentPath": "frontend/src/pages/data/observability/Tiering.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "knowledge-observability-stores-export-and-integrations",
            "label": "Export & Integrations",
            "route": "/data/observability/export",
            "componentPath": "frontend/src/pages/data/observability/Export.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "knowledge-observability-stores-observability-stores",
            "label": "Observability Stores",
            "route": "/data/observability-stores",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "knowledge-observability-stores-metrics-store",
            "label": "Metrics Store",
            "route": "/data/metrics",
            "componentPath": "frontend/src/pages/data/Metrics.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "knowledge-observability-stores-logs-store",
            "label": "Logs Store",
            "route": "/data/logs",
            "componentPath": "frontend/src/pages/data/Logs.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "knowledge-observability-stores-traces-store",
            "label": "Traces Store",
            "route": "/data/traces",
            "componentPath": "frontend/src/pages/data/Traces.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          }
        ]
      },
      {
        "id": "knowledge-archive-and-backup",
        "label": "Archive & Backup",
        "homeRoute": "/data/archive-and-backup",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "knowledge-archive-and-backup-archive",
            "label": "Archive",
            "route": "/data/archive",
            "componentPath": "frontend/src/pages/data/Archive.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "knowledge-archive-and-backup-overview",
            "label": "Overview",
            "route": "/knowledge/archive-and-backup/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "knowledge-archive-and-backup-runbook",
            "label": "Runbook",
            "route": "/knowledge/archive-and-backup/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "knowledge-multi-region-and-replication",
        "label": "Multi-Region & Replication",
        "homeRoute": "/data/multi-region-and-replication",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 3,
        "features": [
          {
            "id": "knowledge-multi-region-and-replication-multi-region-replication",
            "label": "Multi-Region Replication",
            "route": "/data/replication",
            "componentPath": "frontend/src/pages/data/Replication.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "knowledge-multi-region-and-replication-overview",
            "label": "Overview",
            "route": "/knowledge/multi-region-and-replication/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "knowledge-multi-region-and-replication-runbook",
            "label": "Runbook",
            "route": "/knowledge/multi-region-and-replication/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "knowledge-core-data-stores",
        "label": "Core Data Stores",
        "homeRoute": "/data/core-data-stores",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 4,
        "features": [
          {
            "id": "knowledge-core-data-stores-core-data-stores",
            "label": "Core Data Stores",
            "route": "/data/core-data-stores",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "knowledge-core-data-stores-data-overview",
            "label": "Data Overview",
            "route": "/data/core-data-stores/data",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "knowledge-core-data-stores-cir-store",
            "label": "CIR Store",
            "route": "/data/cir",
            "componentPath": "frontend/src/pages/data/Cir.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "knowledge-core-data-stores-capsule-store",
            "label": "Capsule Store",
            "route": "/data/capsules",
            "componentPath": "frontend/src/pages/data/Capsules.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "knowledge-core-data-stores-project-ledger",
            "label": "Project Ledger",
            "route": "/data/ledger",
            "componentPath": "frontend/src/pages/data/Ledger.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "knowledge-core-data-stores-binary-artifacts",
            "label": "Binary Artifacts",
            "route": "/data/artifacts",
            "componentPath": "frontend/src/pages/data/Artifacts.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "knowledge-core-data-stores-schema-and-ontology",
            "label": "Schema & Ontology",
            "route": "/data/schema",
            "componentPath": "frontend/src/pages/data/Schema.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "knowledge-core-data-stores-ingestion-pipelines",
            "label": "Ingestion Pipelines",
            "route": "/data/ingestion",
            "componentPath": "frontend/src/pages/data/Ingestion.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          },
          {
            "id": "knowledge-core-data-stores-data-lineage",
            "label": "Data Lineage",
            "route": "/data/lineage",
            "componentPath": "frontend/src/pages/data/Lineage.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9,
            "isNew": false
          },
          {
            "id": "knowledge-core-data-stores-data-quality-checks",
            "label": "Data Quality Checks",
            "route": "/data/quality",
            "componentPath": "frontend/src/pages/data/Quality.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10,
            "isNew": false
          },
          {
            "id": "knowledge-core-data-stores-data-overview",
            "label": "Data Overview",
            "route": "/data",
            "componentPath": "frontend/src/pages/Data.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11,
            "isNew": false
          }
        ]
      },
      {
        "id": "knowledge-data-protection",
        "label": "Data Protection",
        "homeRoute": "/data/data-protection",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 5,
        "features": [
          {
            "id": "knowledge-data-protection-data-protection",
            "label": "Data Protection",
            "route": "/data/data-protection",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "knowledge-data-protection-encryption-and-keys",
            "label": "Encryption & Keys",
            "route": "/data/encryption",
            "componentPath": "frontend/src/pages/data/Encryption.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "knowledge-data-protection-key-rotation-and-kms-integrations",
            "label": "Key Rotation & KMS Integrations",
            "route": "/data/encryption/rotation",
            "componentPath": "frontend/src/pages/data/encryption/Rotation.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "knowledge-data-protection-integrity-protections",
            "label": "Integrity Protections",
            "route": "/data/integrity",
            "componentPath": "frontend/src/pages/data/Integrity.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          }
        ]
      },
      {
        "id": "knowledge-replication-and-dr",
        "label": "Replication & DR",
        "homeRoute": "/data/replication-and-dr",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 6,
        "features": [
          {
            "id": "knowledge-replication-and-dr-replication-and-dr",
            "label": "Replication & DR",
            "route": "/data/replication-dr",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "knowledge-replication-and-dr-consistency-models",
            "label": "Consistency Models",
            "route": "/data/consistency",
            "componentPath": "frontend/src/pages/data/Consistency.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "knowledge-replication-and-dr-failover-controls",
            "label": "Failover Controls",
            "route": "/data/dr/failover",
            "componentPath": "frontend/src/pages/data/dr/Failover.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "knowledge-replication-and-dr-dr-drill-planner",
            "label": "DR Drill Planner",
            "route": "/data/dr/drills",
            "componentPath": "frontend/src/pages/data/dr/Drills.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          }
        ]
      },
      {
        "id": "knowledge-indices-and-search",
        "label": "Indices & Search",
        "homeRoute": "/data/indices-and-search",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 7,
        "features": [
          {
            "id": "knowledge-indices-and-search-indices-and-search",
            "label": "Indices & Search",
            "route": "/data/indices-search",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "knowledge-indices-and-search-indices-overview",
            "label": "Indices Overview",
            "route": "/data/indices",
            "componentPath": "frontend/src/pages/data/Indices.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "knowledge-indices-and-search-index-management",
            "label": "Index Management",
            "route": "/data/indices/manage",
            "componentPath": "frontend/src/pages/data/indices/Manage.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "knowledge-indices-and-search-full-text-search",
            "label": "Full-Text Search",
            "route": "/data/indices/fulltext",
            "componentPath": "frontend/src/pages/data/indices/Fulltext.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "knowledge-indices-and-search-semantic-vector-search",
            "label": "Semantic/Vector Search",
            "route": "/data/indices/semantic",
            "componentPath": "frontend/src/pages/data/indices/Semantic.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          },
          {
            "id": "knowledge-indices-and-search-embeddings-management",
            "label": "Embeddings Management",
            "route": "/data/indices/embeddings",
            "componentPath": "frontend/src/pages/data/indices/Embeddings.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6,
            "isNew": false
          },
          {
            "id": "knowledge-indices-and-search-graph-index",
            "label": "Graph Index",
            "route": "/data/indices/graph",
            "componentPath": "frontend/src/pages/data/indices/Graph.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7,
            "isNew": false
          },
          {
            "id": "knowledge-indices-and-search-relevance-tuning",
            "label": "Relevance Tuning",
            "route": "/data/indices/tuning",
            "componentPath": "frontend/src/pages/data/indices/Tuning.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8,
            "isNew": false
          },
          {
            "id": "knowledge-indices-and-search-query-console",
            "label": "Query Console",
            "route": "/data/query",
            "componentPath": "frontend/src/pages/data/Query.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9,
            "isNew": false
          }
        ]
      },
      {
        "id": "knowledge-archive-and-retention",
        "label": "Archive & Retention",
        "homeRoute": "/data/archive-and-retention",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 8,
        "features": [
          {
            "id": "knowledge-archive-and-retention-archive-and-retention",
            "label": "Archive & Retention",
            "route": "/data/archive-retention",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "knowledge-archive-and-retention-backup-and-retention",
            "label": "Backup & Retention",
            "route": "/data/backup",
            "componentPath": "frontend/src/pages/data/Backup.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "knowledge-archive-and-retention-retention-policy-builder",
            "label": "Retention Policy Builder",
            "route": "/data/retention/policies",
            "componentPath": "frontend/src/pages/data/retention/Policies.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "knowledge-archive-and-retention-legal-hold",
            "label": "Legal Hold",
            "route": "/data/legal-hold",
            "componentPath": "frontend/src/pages/data/LegalHold.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4,
            "isNew": false
          },
          {
            "id": "knowledge-archive-and-retention-restore-testing",
            "label": "Restore Testing",
            "route": "/data/restore-testing",
            "componentPath": "frontend/src/pages/data/RestoreTesting.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5,
            "isNew": false
          }
        ]
      },
      {
        "id": "knowledge-perspective",
        "label": "Perspective",
        "homeRoute": "/data/perspective",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 9,
        "features": [
          {
            "id": "knowledge-perspective-perspective",
            "label": "Perspective",
            "route": "/knowledge/perspective",
            "componentPath": "frontend/src/pages/knowledge/KnowledgeFeature.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "knowledge-perspective-world-model",
            "label": "World Model",
            "route": "/knowledge/perspective/world-model",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "knowledge-perspective-overview",
            "label": "Overview",
            "route": "/knowledge/perspective/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "knowledge-perspective-overview",
            "label": "Overview",
            "route": "/knowledge/perspective/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "knowledge-perspective-runbook",
            "label": "Runbook",
            "route": "/knowledge/perspective/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "knowledge-insight",
        "label": "Insight",
        "homeRoute": "/data/insight",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 10,
        "features": [
          {
            "id": "knowledge-insight-insight",
            "label": "Insight",
            "route": "/knowledge/insight",
            "componentPath": "frontend/src/pages/knowledge/KnowledgeFeature.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "knowledge-insight-insight-journal",
            "label": "Insight Journal",
            "route": "/knowledge/insight/journal",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "knowledge-insight-overview",
            "label": "Overview",
            "route": "/knowledge/insight/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "knowledge-insight-overview",
            "label": "Overview",
            "route": "/knowledge/insight/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "knowledge-insight-runbook",
            "label": "Runbook",
            "route": "/knowledge/insight/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "knowledge-wisdom",
        "label": "Wisdom",
        "homeRoute": "/data/wisdom",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 11,
        "features": [
          {
            "id": "knowledge-wisdom-wisdom",
            "label": "Wisdom",
            "route": "/knowledge/wisdom",
            "componentPath": "frontend/src/pages/knowledge/KnowledgeFeature.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "knowledge-wisdom-principles",
            "label": "Principles",
            "route": "/knowledge/wisdom/principles",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "knowledge-wisdom-overview",
            "label": "Overview",
            "route": "/knowledge/wisdom/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "knowledge-wisdom-overview",
            "label": "Overview",
            "route": "/knowledge/wisdom/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "knowledge-wisdom-runbook",
            "label": "Runbook",
            "route": "/knowledge/wisdom/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      },
      {
        "id": "knowledge-experience",
        "label": "Experience",
        "homeRoute": "/data/experience",
        "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 12,
        "features": [
          {
            "id": "knowledge-experience-experience",
            "label": "Experience",
            "route": "/knowledge/experience",
            "componentPath": "frontend/src/pages/knowledge/KnowledgeFeature.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1,
            "isNew": false
          },
          {
            "id": "knowledge-experience-experience-log",
            "label": "Experience Log",
            "route": "/knowledge/experience/log",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2,
            "isNew": false
          },
          {
            "id": "knowledge-experience-overview",
            "label": "Overview",
            "route": "/knowledge/experience/overview-1",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2,
            "isNew": false
          },
          {
            "id": "knowledge-experience-overview",
            "label": "Overview",
            "route": "/knowledge/experience/overview",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3,
            "isNew": false
          },
          {
            "id": "knowledge-experience-runbook",
            "label": "Runbook",
            "route": "/knowledge/experience/runbook",
            "componentPath": "frontend/src/components/templates/FeaturePageTemplate.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3,
            "isNew": false
          }
        ]
      }
    ]
  }
]

export const legacyRedirects: Record<string, string> = {
  "/projects": "/dashboard/flight-deck/projects",
  "/tasks": "/dashboard/flight-deck/tasks",
  "/projects/templates": "/dashboard/core-flight-deck/templates",
  "/projects/members": "/dashboard/core-flight-deck/members",
  "/projects/settings": "/dashboard/core-flight-deck/settings",
  "/tasks/board": "/dashboard/core-flight-deck/board",
  "/tasks/automation": "/dashboard/core-flight-deck/automation",
  "/tasks/analytics": "/dashboard/core-flight-deck/analytics",
  "/activity": "/dashboard/core-flight-deck/activity",
  "/notifications": "/dashboard/core-flight-deck/notifications",
  "/inbox": "/dashboard/core-flight-deck/inbox",
  "/timeline": "/dashboard/core-flight-deck/timeline",
  "/chat": "/dashboard/engagement/chat",
  "/collaboration": "/dashboard/engagement/collaboration",
  "/personalization": "/dashboard/engagement/personalization",
  "/search": "/dashboard/engagement/search",
  "/chat/library": "/dashboard/engagement-persona-surfaces/library",
  "/search/saved": "/dashboard/engagement-persona-surfaces/saved",
  "/collaboration/channels": "/dashboard/engagement-persona-surfaces/channels",
  "/collaboration/presence": "/dashboard/engagement-persona-surfaces/presence",
  "/personalization/macros": "/dashboard/engagement-persona-surfaces/macros",
  "/personalization/profiles": "/dashboard/engagement-persona-surfaces/profiles",
  "/pms": "/ipm",
  "/pms/projects": "/ipm/projects",
  "/pms/runs": "/ipm/runs",
  "/pms/documents": "/ipm/documents",
  "/pms/journal": "/ipm/journal",
  "/pms/finance": "/ipm/finance",
  "/pms/audit": "/ipm/audit",
  "/pms/settings": "/ipm/settings",
  "/work/tools": "/workspaces/dev/tools",
  "/research": "/workspaces/research",
  "/work/templates": "/workspaces/writer/templates",
  "/work/writer": "/workspaces/writer",
  "/ai/security": "/workspaces/cyber",
  "/data": "/data/core-data-stores/data",
  "/integrations": "/drivers/driver-registry-management/drivers",
  "/integrations/connectors": "/drivers/connectors-integrations/connectors",
  "/integrations/credentials": "/drivers/connectors-integrations/credentials",
  "/integrations/api-connectors": "/drivers/connectors-integrations/api-connectors",
  "/integrations/mcp-gateway": "/drivers/connectors-integrations/mcp-gateway",
  "/integrations/office": "/drivers/connectors-integrations/office",
  "/integrations/webhooks": "/drivers/connectors-integrations/webhooks",
  "/integrations/mappings": "/drivers/connectors-integrations/mappings",
  "/integrations/health": "/drivers/connectors-integrations/health",
  "/integrations/rate-limits": "/drivers/connectors-integrations/rate-limits",
  "/docs": "/docs/documentation-hub/docs",
  "/settings": "/settings/user-tenant-settings/settings",
  "/mission-architecture/planes-architecture/cross-plane-flows": "/mission-architecture/planes-architecture/cross-plane-flows",
  "/mission-architecture/architecture-principles/driver-aware-orchestrator": "/mission-architecture/architecture-principles/driver-aware-orchestrator",
  "/mission-architecture/mission-identity/identity-roles": "/mission-architecture/mission-identity/identity-roles",
  "/mission-architecture/mission-identity/mission-scope": "/mission-architecture/mission-identity/mission-scope",
  "/workspaces/dev-devops/ci-cd": "/workspaces/dev-devops/ci-cd",
  "/workspaces/dev-devops/commit-tasks": "/workspaces/dev-devops/commit-tasks",
  "/workspaces/dev-devops/merge-advisor": "/workspaces/dev-devops/merge-advisor",
  "/workspaces/research-simulation/digital-twins": "/workspaces/research-simulation/digital-twins",
  "/billing": "/governance/billing",
  "/audit": "/observability/audit",
  "/audit/builder": "/observability/record-auditor-logbook/builder",
  "/observability": "/observability/telemetry-metrics/observability",
  "/monitoring": "/observability/monitoring",
  "/analytics": "/observability/analytics",
  "/observability-evidence/telemetry-metrics/slis-slos": "/observability-evidence/telemetry-metrics/slis-slos",
  "/operations-infrastructure/deployment-models/deployment-modes": "/operations-infrastructure/deployment-models/deployment-modes",
  "/operations-infrastructure/deployment-models/hybrid-edge": "/operations-infrastructure/deployment-models/hybrid-edge",
  "/systems/network": "/operations/infrastructure-topology/network",
  "/future/core_os": "/vision/core-os",
  "/future/core_os/matrix": "/vision/core-os-engines/matrix",
  "/future/super": "/vision/super",
  "/future/super/matrix": "/vision/super-capabilities/matrix",
  "/future/supreme": "/vision/supreme",
  "/future/supreme/matrix": "/vision/supreme/matrix",
  "/future/ascend": "/vision/ascend",
  "/future/ascend/matrix": "/vision/ascend/matrix",
  "/future/advanced/matrix": "/vision/advanced-horizons/matrix",
  "/future/meta": "/vision/meta",
  "/future/meta/matrix": "/vision/meta-envelope/matrix",
  "/future/hyper/matrix": "/vision/hyper-network/matrix",
  "/vision": "/vision/vision-deck-hub/vision",
  "/future/ultra/matrix": "/vision/ultra-scale/matrix",
  "/ai-fabric/capsules-workflow/auto-fix-console": "/ai-fabric/capsules-workflow/auto-fix-console",
  "/ai-fabric/capsules-workflow/capsule-marketplace": "/ai-fabric/capsules-workflow/capsule-marketplace",
  "/ai-fabric/capsules-workflow/lineage-replay": "/ai-fabric/capsules-workflow/lineage-replay",
  "/ai-fabric/cognitive-agents/ai-copilot": "/ai-fabric/cognitive-agents/ai-copilot",
  "/ai-fabric/cognitive-agents/personas-agents": "/ai-fabric/cognitive-agents/personas-agents",
  "/ai-fabric/edge-vision/computer-vision": "/ai-fabric/edge-vision/computer-vision",
  "/ai-fabric/edge-vision/edge-computing": "/ai-fabric/edge-vision/edge-computing",
  "/ai-fabric/intent-processing/intent-processor": "/ai-fabric/intent-processing/intent-processor",
  "/ai-fabric/mlops-neural-arch/mlops": "/ai-fabric/mlops-neural-arch/mlops",
  "/vision-and-meta-stack/vision-deck-hub/vision-deck-hub": "/vision/vision-deck-hub",
  "/vision-and-meta-stack/vision-deck-hub/vision": "/vision",
  "/vision-and-meta-stack/vision-deck-hub/roadmap": "/vision/roadmap",
  "/vision-and-meta-stack/vision-deck-hub/glossary": "/vision/glossary",
  "/vision-and-meta-stack/core-os-engines/core-os-engines": "/vision/core-os-engines",
  "/vision-and-meta-stack/core-os-engines/core-os": "/vision/core-os",
  "/vision-and-meta-stack/core-os-engines/matrix": "/vision/core-os-engines/matrix",
  "/vision-and-meta-stack/ascend/ascend": "/vision/ascend",
  "/vision-and-meta-stack/ascend/matrix": "/vision/ascend/matrix",
  "/vision-and-meta-stack/supreme/supreme": "/vision/supreme",
  "/vision-and-meta-stack/supreme/matrix": "/vision/supreme/matrix",
  "/vision-and-meta-stack/hyper-network/hyper-network": "/vision/hyper-network",
  "/vision-and-meta-stack/hyper-network/hyper": "/future/hyper",
  "/vision-and-meta-stack/hyper-network/matrix": "/vision/hyper-network/matrix",
  "/vision-and-meta-stack/super-capabilities/super-capabilities": "/vision/super-capabilities",
  "/vision-and-meta-stack/super-capabilities/super": "/vision/super",
  "/vision-and-meta-stack/super-capabilities/matrix": "/vision/super-capabilities/matrix",
  "/vision-and-meta-stack/meta-envelope/meta-envelope": "/vision/meta-envelope",
  "/vision-and-meta-stack/meta-envelope/meta": "/vision/meta",
  "/vision-and-meta-stack/meta-envelope/matrix": "/vision/meta-envelope/matrix",
  "/vision-and-meta-stack/ultra-scale/ultra-scale": "/vision/ultra-scale",
  "/vision-and-meta-stack/ultra-scale/ultra": "/future/ultra",
  "/vision-and-meta-stack/ultra-scale/matrix": "/vision/ultra-scale/matrix",
  "/vision-and-meta-stack/advanced-horizons/advanced-horizons": "/vision/advanced-horizons",
  "/vision-and-meta-stack/advanced-horizons/advanced": "/future/advanced",
  "/vision-and-meta-stack/advanced-horizons/matrix": "/vision/advanced-horizons/matrix",
  "/observability-and-evidence/logging-and-tracing/logging-tracing": "/observability/logging-tracing",
  "/observability-and-evidence/logging-and-tracing/logging": "/observability/logging",
  "/observability-and-evidence/logging-and-tracing/explorer": "/observability/tracing/explorer",
  "/observability-and-evidence/logging-and-tracing/tracing": "/observability/tracing",
  "/observability-and-evidence/logging-and-tracing/correlation": "/observability/correlation",
  "/observability-and-evidence/telemetry-and-metrics/telemetry-metrics": "/observability/telemetry-metrics",
  "/observability-and-evidence/telemetry-and-metrics/observability": "/observability",
  "/observability-and-evidence/telemetry-and-metrics/monitoring": "/observability/monitoring",
  "/observability-and-evidence/telemetry-and-metrics/analytics": "/observability/analytics",
  "/observability-and-evidence/telemetry-and-metrics/metrics": "/observability/metrics",
  "/observability-and-evidence/telemetry-and-metrics/explorer": "/observability/metrics/explorer",
  "/observability-and-evidence/telemetry-and-metrics/slis": "/observability/slis",
  "/observability-and-evidence/telemetry-and-metrics/burn": "/observability/slis/burn",
  "/observability-and-evidence/telemetry-and-metrics/anomalies": "/observability/anomalies",
  "/observability-and-evidence/evidence-and-audit/evidence-audit": "/observability/evidence-audit",
  "/observability-and-evidence/evidence-and-audit/audit-logs": "/observability/audit-logs",
  "/observability-and-evidence/evidence-and-audit/evidence": "/observability/evidence",
  "/observability-and-evidence/evidence-and-audit/query": "/observability/evidence/query",
  "/observability-and-evidence/evidence-and-audit/export": "/observability/evidence/export",
  "/observability-and-evidence/evidence-and-audit/retention": "/observability/retention",
  "/observability-and-evidence/dashboards-and-alerting/dashboards-alerting": "/observability/dashboards-alerting",
  "/observability-and-evidence/dashboards-and-alerting/dashboards": "/observability/dashboards",
  "/observability-and-evidence/dashboards-and-alerting/builder": "/observability/dashboards/builder",
  "/observability-and-evidence/dashboards-and-alerting/alerting": "/observability/alerting",
  "/observability-and-evidence/dashboards-and-alerting/rules": "/observability/alerting/rules",
  "/observability-and-evidence/dashboards-and-alerting/channels": "/observability/alerting/channels",
  "/observability-and-evidence/temporal-backtesting-and-replay/temporal-backtesting-replay": "/observability/temporal-backtesting-replay",
  "/observability-and-evidence/temporal-backtesting-and-replay/replay": "/observability/replay",
  "/observability-and-evidence/temporal-backtesting-and-replay/scenarios": "/observability/replay/scenarios",
  "/observability-and-evidence/temporal-backtesting-and-replay/determinism": "/observability/replay/determinism",
  "/observability-and-evidence/temporal-backtesting-and-replay/backtesting": "/observability/backtesting",
  "/observability-and-evidence/health-and-self-healing/health-self-healing": "/observability/health-self-healing",
  "/observability-and-evidence/health-and-self-healing/health": "/observability/health",
  "/observability-and-evidence/health-and-self-healing/drift": "/observability/drift",
  "/observability-and-evidence/health-and-self-healing/runbooks": "/observability/runbooks",
  "/observability-and-evidence/health-and-self-healing/self-healing": "/observability/self-healing",
  "/observability-and-evidence/health-and-self-healing/rollbacks": "/observability/rollbacks",
  "/observability-and-evidence/record-auditor-and-logbook/record-auditor-logbook": "/observability/record-auditor-logbook",
  "/observability-and-evidence/record-auditor-and-logbook/record-auditor": "/observability/record-auditor",
  "/observability-and-evidence/record-auditor-and-logbook/timeline": "/observability/record-auditor/timeline",
  "/observability-and-evidence/record-auditor-and-logbook/audit": "/observability/audit",
  "/observability-and-evidence/record-auditor-and-logbook/builder": "/observability/record-auditor-logbook/builder",
  "/operations-and-infrastructure/infrastructure-and-topology/infrastructure-topology": "/operations/infrastructure-topology",
  "/operations-and-infrastructure/infrastructure-and-topology/config": "/operations/config",
  "/operations-and-infrastructure/infrastructure-and-topology/secrets": "/operations/secrets",
  "/operations-and-infrastructure/infrastructure-and-topology/cluster": "/operations/cluster",
  "/operations-and-infrastructure/infrastructure-and-topology/topology": "/operations/topology",
  "/operations-and-infrastructure/infrastructure-and-topology/network": "/operations/infrastructure-topology/network",
  "/operations-and-infrastructure/infrastructure-and-topology/storage": "/operations/storage",
  "/operations-and-infrastructure/infrastructure-and-topology/queues": "/operations/queues",
  "/operations-and-infrastructure/infrastructure-and-topology/dependencies": "/operations/dependencies",
  "/operations-and-infrastructure/infrastructure-and-topology/multi-region": "/operations/multi-region",
  "/operations-and-infrastructure/infrastructure-and-topology/hpc": "/operations/hpc",
  "/operations-and-infrastructure/failure-modes-and-resilience/failure-modes-resilience": "/operations/failure-modes-resilience",
  "/operations-and-infrastructure/failure-modes-and-resilience/failure": "/operations/failure",
  "/operations-and-infrastructure/failure-modes-and-resilience/detection": "/operations/detection",
  "/operations-and-infrastructure/failure-modes-and-resilience/recovery": "/operations/recovery",
  "/operations-and-infrastructure/failure-modes-and-resilience/data-protection": "/operations/data-protection",
  "/operations-and-infrastructure/failure-modes-and-resilience/bc-dr": "/operations/bc-dr",
  "/operations-and-infrastructure/failure-modes-and-resilience/drills": "/operations/bc-dr/drills",
  "/operations-and-infrastructure/failure-modes-and-resilience/security-incidents": "/operations/security-incidents",
  "/operations-and-infrastructure/failure-modes-and-resilience/chaos": "/operations/chaos",
  "/operations-and-infrastructure/failure-modes-and-resilience/postmortems": "/operations/postmortems",
  "/operations-and-infrastructure/performance-and-scalability/performance-scalability": "/operations/performance-scalability",
  "/operations-and-infrastructure/performance-and-scalability/performance": "/operations/performance",
  "/operations-and-infrastructure/performance-and-scalability/scaling": "/operations/scaling",
  "/operations-and-infrastructure/performance-and-scalability/capacity": "/operations/capacity",
  "/operations-and-infrastructure/performance-and-scalability/load-testing": "/operations/load-testing",
  "/operations-and-infrastructure/performance-and-scalability/backpressure": "/operations/backpressure",
  "/operations-and-infrastructure/performance-and-scalability/reliability": "/operations/reliability",
  "/operations-and-infrastructure/performance-and-scalability/driver-performance": "/operations/driver-performance",
  "/operations-and-infrastructure/performance-and-scalability/cost-performance": "/operations/cost-performance",
  "/operations-and-infrastructure/deployment-models/deployment-models": "/operations/deployment-models",
  "/operations-and-infrastructure/deployment-models/deployment": "/operations/deployment",
  "/operations-and-infrastructure/deployment-models/local": "/operations/deployment/local",
  "/operations-and-infrastructure/deployment-models/cloud": "/operations/deployment/cloud",
  "/operations-and-infrastructure/deployment-models/hybrid": "/operations/deployment/hybrid",
  "/operations-and-infrastructure/deployment-models/k8s": "/operations/deployment/k8s",
  "/operations-and-infrastructure/deployment-models/airgap": "/operations/deployment/airgap",
  "/operations-and-infrastructure/deployment-models/channels": "/operations/deployment/channels",
  "/operations-and-infrastructure/upgrades-and-migration/upgrades-migration": "/operations/upgrades-migration",
  "/operations-and-infrastructure/upgrades-and-migration/upgrades": "/operations/upgrades",
  "/operations-and-infrastructure/upgrades-and-migration/releases": "/operations/releases",
  "/operations-and-infrastructure/upgrades-and-migration/compatibility": "/operations/compatibility",
  "/operations-and-infrastructure/upgrades-and-migration/migration": "/operations/migration",
  "/operations-and-infrastructure/upgrades-and-migration/rollback": "/operations/rollback",
  "/operations-and-infrastructure/upgrades-and-migration/canary": "/operations/deployment/canary",
  "/workspaces-(enterprise-extensions)/record-auditor-and-logbook-workspace/record-auditor-logbook-workspace": "/workspaces/record-auditor-logbook-workspace",
  "/workspaces-(enterprise-extensions)/record-auditor-and-logbook-workspace/auditor": "/workspaces/auditor",
  "/workspaces-(enterprise-extensions)/record-auditor-and-logbook-workspace/controls": "/workspaces/auditor/controls",
  "/workspaces-(enterprise-extensions)/record-auditor-and-logbook-workspace/reports": "/workspaces/auditor/reports",
  "/workspaces-(enterprise-extensions)/record-auditor-and-logbook-workspace/logbook": "/workspaces/auditor/logbook",
  "/settings-and-admin-(enterprise-extensions)/user-and-tenant-settings/user-tenant": "/settings/enterprise/user-tenant",
  "/settings-and-admin-(enterprise-extensions)/user-and-tenant-settings/team": "/settings/team",
  "/settings-and-admin-(enterprise-extensions)/user-and-tenant-settings/tenant": "/settings/tenant",
  "/settings-and-admin-(enterprise-extensions)/user-and-tenant-settings/audit": "/settings/audit",
  "/mission-and-architecture/architecture-and-principles/architecture-principles": "/mission/architecture-principles",
  "/mission-and-architecture/architecture-and-principles/architecture": "/mission/architecture",
  "/mission-and-architecture/architecture-and-principles/principles": "/mission/principles",
  "/mission-and-architecture/architecture-and-principles/components": "/mission/components",
  "/mission-and-architecture/architecture-and-principles/orchestrator": "/mission/orchestrator",
  "/mission-and-architecture/architecture-and-principles/mapping": "/mission/mapping",
  "/mission-and-architecture/architecture-and-principles/contracts": "/mission/contracts",
  "/mission-and-architecture/architecture-and-principles/extensibility": "/mission/extensibility",
  "/mission-and-architecture/architecture-and-principles/threat-model": "/mission/threat-model",
  "/mission-and-architecture/architecture-and-principles/performance-targets": "/mission/performance-targets",
  "/mission-and-architecture/mission-and-identity/mission-identity": "/mission/mission-identity",
  "/mission-and-architecture/mission-and-identity/overview": "/mission/overview",
  "/mission-and-architecture/mission-and-identity/use-cases": "/mission/use-cases",
  "/mission-and-architecture/mission-and-identity/non-goals": "/mission/non-goals",
  "/mission-and-architecture/mission-and-identity/glossary": "/mission/glossary",
  "/mission-and-architecture/mission-and-identity/modes": "/mission/modes",
  "/mission-and-architecture/mission-and-identity/reference-architectures": "/mission/reference-architectures",
  "/mission-and-architecture/mission-and-identity/identity": "/mission/identity",
  "/mission-and-architecture/mission-and-identity/ai-stack": "/mission/ai-stack",
  "/mission-and-architecture/mission-and-identity/models": "/mission/models",
  "/mission-and-architecture/mission-and-identity/daemons": "/mission/daemons",
  "/mission-and-architecture/planes-architecture/planes-architecture": "/mission/planes-architecture",
  "/mission-and-architecture/planes-architecture/planes": "/mission/planes",
  "/mission-and-architecture/planes-architecture/data": "/mission/planes/data",
  "/mission-and-architecture/planes-architecture/control": "/mission/planes/control",
  "/mission-and-architecture/planes-architecture/governance": "/mission/planes/governance",
  "/mission-and-architecture/planes-architecture/cross-plane": "/mission/planes/cross-plane",
  "/mission-and-architecture/planes-architecture/contracts": "/mission/planes/contracts",
  "/mission-and-architecture/planes-architecture/failure-domains": "/mission/planes/failure-domains",
  "/roadmap-and-risks/roadmap-and-planning/roadmap-planning": "/roadmap/roadmap-planning",
  "/roadmap-and-risks/roadmap-and-planning/overview": "/roadmap/overview",
  "/roadmap-and-risks/roadmap-and-planning/phases": "/roadmap/phases",
  "/roadmap-and-risks/roadmap-and-planning/milestones": "/roadmap/milestones",
  "/roadmap-and-risks/roadmap-and-planning/future": "/roadmap/future",
  "/roadmap-and-risks/spec-maintenance/spec-maintenance": "/roadmap/spec-maintenance",
  "/roadmap-and-risks/spec-maintenance/spec": "/roadmap/spec",
  "/roadmap-and-risks/spec-maintenance/deprecations": "/roadmap/deprecations",
  "/roadmap-and-risks/spec-maintenance/compatibility": "/roadmap/compatibility",
  "/roadmap-and-risks/spec-maintenance/future-capabilities": "/roadmap/future-capabilities",
  "/roadmap-and-risks/risks-and-decisions/risks-decisions": "/roadmap/risks-decisions",
  "/roadmap-and-risks/risks-and-decisions/risks": "/roadmap/risks",
  "/roadmap-and-risks/risks-and-decisions/decisions": "/roadmap/decisions",
  "/roadmap-and-risks/risks-and-decisions/gaps": "/roadmap/gaps",
  "/roadmap-and-risks/risks-and-decisions/questions": "/roadmap/questions",
  "/governance-and-security/data-protection-and-classification/data-protection-classification": "/governance/data-protection-classification",
  "/governance-and-security/data-protection-and-classification/data-protection": "/governance/data-protection",
  "/governance-and-security/data-protection-and-classification/classification": "/governance/data-protection/classification",
  "/governance-and-security/data-protection-and-classification/masking": "/governance/data-protection/masking",
  "/governance-and-security/data-protection-and-classification/tokenization": "/governance/data-protection/tokenization",
  "/governance-and-security/data-protection-and-classification/dlp": "/governance/data-protection/dlp",
  "/governance-and-security/data-protection-and-classification/residency": "/governance/data-protection/residency",
  "/governance-and-security/ai-billing-and-cost-governance/ai-billing-cost-governance": "/governance/ai-billing-cost-governance",
  "/governance-and-security/ai-billing-and-cost-governance/billing": "/governance/billing",
  "/governance-and-security/ai-billing-and-cost-governance/usage": "/governance/billing/usage",
  "/governance-and-security/ai-billing-and-cost-governance/budgets": "/governance/billing/budgets",
  "/governance-and-security/ai-billing-and-cost-governance/guardrails": "/governance/billing/guardrails",
  "/governance-and-security/ai-billing-and-cost-governance/optimizer": "/governance/billing/optimizer",
  "/governance-and-security/ai-billing-and-cost-governance/chargeback": "/governance/billing/chargeback",
  "/governance-and-security/ai-billing-and-cost-governance/forecasting": "/governance/billing/forecasting",
  "/governance-and-security/ai-billing-and-cost-governance/rates": "/governance/billing/rates",
  "/governance-and-security/ai-billing-and-cost-governance/multi-tenant": "/governance/billing/multi-tenant",
  "/governance-and-security/security-monitoring-and-response/security-monitoring-response": "/governance/security-monitoring-response",
  "/governance-and-security/security-monitoring-and-response/monitoring": "/governance/security/monitoring",
  "/governance-and-security/security-monitoring-and-response/alerts": "/governance/security/alerts",
  "/governance-and-security/security-monitoring-and-response/detection": "/governance/security/detection",
  "/governance-and-security/security-monitoring-and-response/risk": "/governance/security/risk",
  "/governance-and-security/security-monitoring-and-response/alignment": "/governance/security/alignment",
  "/governance-and-security/security-monitoring-and-response/incidents": "/governance/security/incidents",
  "/governance-and-security/security-monitoring-and-response/forensics": "/governance/security/forensics",
  "/governance-and-security/security-monitoring-and-response/vuln": "/governance/security/vuln",
  "/governance-and-security/identity-and-access/identity-access": "/governance/identity-access",
  "/governance-and-security/identity-and-access/identity": "/governance/identity",
  "/governance-and-security/identity-and-access/auth": "/governance/identity/auth",
  "/governance-and-security/identity-and-access/sso": "/governance/identity/sso",
  "/governance-and-security/identity-and-access/scim": "/governance/identity/scim",
  "/governance-and-security/identity-and-access/rbac": "/governance/identity/rbac",
  "/governance-and-security/identity-and-access/api-keys": "/governance/identity/api-keys",
  "/governance-and-security/identity-and-access/sessions": "/governance/identity/sessions",
  "/governance-and-security/identity-and-access/reviews": "/governance/identity/reviews",
  "/governance-and-security/policy-and-governance-engine/policy-governance-engine": "/governance/policy-governance-engine",
  "/governance-and-security/policy-and-governance-engine/policy": "/governance/policy",
  "/governance-and-security/policy-and-governance-engine/library": "/governance/policy/library",
  "/governance-and-security/policy-and-governance-engine/dsl": "/governance/policy/dsl",
  "/governance-and-security/policy-and-governance-engine/safety": "/governance/policy/safety",
  "/governance-and-security/policy-and-governance-engine/simulator": "/governance/policy/simulator",
  "/governance-and-security/policy-and-governance-engine/versioning": "/governance/policy/versioning",
  "/governance-and-security/policy-and-governance-engine/enforcement": "/governance/policy/enforcement",
  "/governance-and-security/policy-and-governance-engine/exceptions": "/governance/policy/exceptions",
  "/governance-and-security/compliance-and-regulator-fabric/compliance-regulator-fabric": "/governance/compliance-regulator-fabric",
  "/governance-and-security/compliance-and-regulator-fabric/compliance": "/governance/compliance",
  "/governance-and-security/compliance-and-regulator-fabric/controls": "/governance/compliance/controls",
  "/governance-and-security/compliance-and-regulator-fabric/readiness": "/governance/compliance/readiness",
  "/governance-and-security/compliance-and-regulator-fabric/regulator": "/governance/regulator",
  "/governance-and-security/compliance-and-regulator-fabric/tenancy": "/governance/regulator/tenancy",
  "/governance-and-security/compliance-and-regulator-fabric/evidence": "/governance/regulator/evidence",
  "/governance-and-security/compliance-and-regulator-fabric/requests": "/governance/regulator/requests",
  "/drivers-and-integrations/driver-registry-and-management/driver-registry-management": "/drivers/driver-registry-management",
  "/drivers-and-integrations/driver-registry-and-management/drivers": "/drivers/driver-registry-management/drivers",
  "/drivers-and-integrations/driver-registry-and-management/registry": "/drivers/registry",
  "/drivers-and-integrations/driver-registry-and-management/sdk": "/drivers/sdk",
  "/drivers-and-integrations/driver-registry-and-management/testing": "/drivers/testing",
  "/drivers-and-integrations/driver-registry-and-management/permissions": "/drivers/permissions",
  "/drivers-and-integrations/driver-registry-and-management/versioning": "/drivers/versioning",
  "/drivers-and-integrations/driver-registry-and-management/analytics": "/drivers/analytics",
  "/drivers-and-integrations/driver-registry-and-management/publishing": "/drivers/publishing",
  "/drivers-and-integrations/connectors-and-integrations/connectors-integrations": "/drivers/connectors-integrations",
  "/drivers-and-integrations/connectors-and-integrations/connectors": "/drivers/connectors-integrations/connectors",
  "/drivers-and-integrations/connectors-and-integrations/credentials": "/drivers/connectors-integrations/credentials",
  "/drivers-and-integrations/connectors-and-integrations/api-connectors": "/drivers/connectors-integrations/api-connectors",
  "/drivers-and-integrations/connectors-and-integrations/productivity": "/drivers/integrations/productivity",
  "/drivers-and-integrations/connectors-and-integrations/code": "/drivers/integrations/code",
  "/drivers-and-integrations/connectors-and-integrations/cloud": "/drivers/integrations/cloud",
  "/drivers-and-integrations/connectors-and-integrations/office": "/drivers/connectors-integrations/office",
  "/drivers-and-integrations/connectors-and-integrations/finance": "/drivers/integrations/finance",
  "/drivers-and-integrations/connectors-and-integrations/research": "/drivers/integrations/research",
  "/drivers-and-integrations/connectors-and-integrations/legacy": "/drivers/integrations/legacy",
  "/drivers-and-integrations/connectors-and-integrations/webhooks": "/drivers/connectors-integrations/webhooks",
  "/drivers-and-integrations/connectors-and-integrations/mappings": "/drivers/connectors-integrations/mappings",
  "/drivers-and-integrations/connectors-and-integrations/health": "/drivers/connectors-integrations/health",
  "/drivers-and-integrations/connectors-and-integrations/rate-limits": "/drivers/connectors-integrations/rate-limits",
  "/drivers-and-integrations/risk-and-governance/risk-governance": "/drivers/risk-governance",
  "/drivers-and-integrations/risk-and-governance/risk": "/drivers/risk",
  "/drivers-and-integrations/risk-and-governance/vendors": "/drivers/risk/vendors",
  "/drivers-and-integrations/risk-and-governance/assessments": "/drivers/risk/assessments",
  "/drivers-and-integrations/risk-and-governance/remediation": "/drivers/risk/remediation",
  "/drivers-and-integrations/risk-and-governance/exceptions": "/drivers/risk/exceptions",
  "/drivers-and-integrations/driver-packs-and-marketplace/driver-packs-marketplace": "/drivers/driver-packs-marketplace",
  "/drivers-and-integrations/driver-packs-and-marketplace/marketplace": "/drivers/marketplace",
  "/drivers-and-integrations/driver-packs-and-marketplace/reviews": "/drivers/marketplace/reviews",
  "/drivers-and-integrations/driver-packs-and-marketplace/security-review": "/drivers/marketplace/security-review",
  "/drivers-and-integrations/driver-packs-and-marketplace/packs": "/drivers/packs",
  "/drivers-and-integrations/driver-packs-and-marketplace/builder": "/drivers/packs/builder",
  "/drivers-and-integrations/driver-packs-and-marketplace/vertical-editions": "/drivers/vertical-editions",
  "/drivers-and-integrations/driver-packs-and-marketplace/enterprise-store": "/drivers/enterprise-store",
  "/drivers-and-integrations/driver-packs-and-marketplace/licensing": "/drivers/licensing",
  "/mission-control/engagement-and-persona-surfaces/engagement-persona-surfaces": "/dashboard/engagement-persona-surfaces",
  "/mission-control/engagement-and-persona-surfaces/chat": "/dashboard/engagement/chat",
  "/mission-control/engagement-and-persona-surfaces/library": "/dashboard/engagement-persona-surfaces/library",
  "/mission-control/engagement-and-persona-surfaces/search": "/dashboard/engagement/search",
  "/mission-control/engagement-and-persona-surfaces/saved": "/dashboard/engagement-persona-surfaces/saved",
  "/mission-control/engagement-and-persona-surfaces/collaboration": "/dashboard/engagement/collaboration",
  "/mission-control/engagement-and-persona-surfaces/channels": "/dashboard/engagement-persona-surfaces/channels",
  "/mission-control/engagement-and-persona-surfaces/presence": "/dashboard/engagement-persona-surfaces/presence",
  "/mission-control/engagement-and-persona-surfaces/personalization": "/dashboard/engagement/personalization",
  "/mission-control/engagement-and-persona-surfaces/macros": "/dashboard/engagement-persona-surfaces/macros",
  "/mission-control/engagement-and-persona-surfaces/profiles": "/dashboard/engagement-persona-surfaces/profiles",
  "/mission-control/core-flight-deck/core-flight-deck": "/dashboard/core-flight-deck",
  "/mission-control/core-flight-deck/flight-deck": "/dashboard/flight-deck",
  "/mission-control/core-flight-deck/projects": "/dashboard/flight-deck/projects",
  "/mission-control/core-flight-deck/templates": "/dashboard/core-flight-deck/templates",
  "/mission-control/core-flight-deck/members": "/dashboard/core-flight-deck/members",
  "/mission-control/core-flight-deck/settings": "/dashboard/core-flight-deck/settings",
  "/mission-control/core-flight-deck/tasks": "/dashboard/flight-deck/tasks",
  "/mission-control/core-flight-deck/board": "/dashboard/core-flight-deck/board",
  "/mission-control/core-flight-deck/automation": "/dashboard/core-flight-deck/automation",
  "/mission-control/core-flight-deck/analytics": "/dashboard/core-flight-deck/analytics",
  "/mission-control/core-flight-deck/activity": "/dashboard/core-flight-deck/activity",
  "/mission-control/core-flight-deck/notifications": "/dashboard/core-flight-deck/notifications",
  "/mission-control/core-flight-deck/inbox": "/dashboard/core-flight-deck/inbox",
  "/mission-control/core-flight-deck/timeline": "/dashboard/core-flight-deck/timeline",
  "/": "/dashboard/flight-deck",
  "/ai-fabric/cognitive-agents-and-reasoning/cognitive-agents-reasoning": "/ai/cognitive-agents-reasoning",
  "/ai-fabric/cognitive-agents-and-reasoning/copilot": "/ai/copilot",
  "/ai-fabric/cognitive-agents-and-reasoning/prompts": "/ai/prompts",
  "/ai-fabric/cognitive-agents-and-reasoning/project-intelligence": "/ai/project-intelligence",
  "/ai-fabric/cognitive-agents-and-reasoning/evals": "/ai/evals",
  "/ai-fabric/cognitive-agents-and-reasoning/routing": "/ai/routing",
  "/ai-fabric/cognitive-agents-and-reasoning/advanced": "/ai/advanced",
  "/ai-fabric/cognitive-agents-and-reasoning/daemons": "/ai/daemons",
  "/ai-fabric/cognitive-agents-and-reasoning/trf": "/ai/trf",
  "/ai-fabric/cognitive-agents-and-reasoning/safety": "/ai/safety",
  "/ai-fabric/cognitive-agents-and-reasoning/registry": "/ai/agents/registry",
  "/ai-fabric/driver-fabric-and-system-execution/driver-fabric-system-execution": "/ai/driver-fabric-system-execution",
  "/ai-fabric/driver-fabric-and-system-execution/os": "/ai/drivers/os",
  "/ai-fabric/driver-fabric-and-system-execution/operations": "/ai/operations",
  "/ai-fabric/driver-fabric-and-system-execution/drivers": "/ai/drivers",
  "/ai-fabric/driver-fabric-and-system-execution/testing": "/ai/drivers/testing",
  "/ai-fabric/driver-fabric-and-system-execution/health": "/ai/drivers/health",
  "/ai-fabric/driver-fabric-and-system-execution/permissions": "/ai/drivers/permissions",
  "/ai-fabric/driver-fabric-and-system-execution/versioning": "/ai/drivers/versioning",
  "/ai-fabric/driver-fabric-and-system-execution/package": "/ai/drivers/package",
  "/ai-fabric/driver-fabric-and-system-execution/hardware": "/ai/drivers/hardware",
  "/ai-fabric/driver-fabric-and-system-execution/software": "/ai/drivers/software",
  "/ai-fabric/driver-fabric-and-system-execution/data": "/ai/drivers/data",
  "/ai-fabric/driver-fabric-and-system-execution/research": "/ai/drivers/research",
  "/ai-fabric/driver-fabric-and-system-execution/sandbox": "/ai/drivers/sandbox",
  "/ai-fabric/edge-and-vision/edge-vision": "/ai/edge-vision",
  "/ai-fabric/edge-and-vision/edge": "/ai/edge",
  "/ai-fabric/edge-and-vision/devices": "/ai/edge/devices",
  "/ai-fabric/edge-and-vision/deploy": "/ai/edge/deploy",
  "/ai-fabric/edge-and-vision/vision": "/ai/vision",
  "/ai-fabric/edge-and-vision/streams": "/ai/vision/streams",
  "/ai-fabric/edge-and-vision/pipelines": "/ai/vision/pipelines",
  "/ai-fabric/edge-and-vision/labeling": "/ai/vision/labeling",
  "/ai-fabric/capsules-and-workflow-automation/capsules-workflow-automation": "/ai/capsules-workflow-automation",
  "/ai-fabric/capsules-and-workflow-automation/workflows": "/ai/workflows",
  "/ai-fabric/capsules-and-workflow-automation/triggers": "/ai/workflows/triggers",
  "/ai-fabric/capsules-and-workflow-automation/observability": "/ai/workflows/observability",
  "/ai-fabric/capsules-and-workflow-automation/builder": "/ai/capsules/builder",
  "/ai-fabric/capsules-and-workflow-automation/templates": "/ai/capsules/templates",
  "/ai-fabric/capsules-and-workflow-automation/my-stack": "/ai/capsules/my-stack",
  "/ai-fabric/capsules-and-workflow-automation/runtime": "/ai/capsules/runtime",
  "/ai-fabric/capsules-and-workflow-automation/secrets": "/ai/capsules/secrets",
  "/ai-fabric/capsules-and-workflow-automation/capsules": "/ai/capsules",
  "/ai-fabric/capsules-and-workflow-automation/publishing": "/ai/capsules/publishing",
  "/ai-fabric/capsules-and-workflow-automation/operator-studio": "/ai/capsules/operator-studio",
  "/ai-fabric/capsules-and-workflow-automation/autofix": "/ai/autofix",
  "/ai-fabric/capsules-and-workflow-automation/ledger": "/ai/capsules/ledger",
  "/ai-fabric/capsules-and-workflow-automation/lineage": "/ai/capsules/lineage",
  "/ai-fabric/mlops-and-neural-architecture/mlops-neural-architecture": "/ai/mlops-neural-architecture",
  "/ai-fabric/mlops-and-neural-architecture/mlops": "/ai/mlops",
  "/ai-fabric/mlops-and-neural-architecture/models": "/ai/mlops/models",
  "/ai-fabric/mlops-and-neural-architecture/data": "/ai/mlops/data",
  "/ai-fabric/mlops-and-neural-architecture/pipelines": "/ai/mlops/pipelines",
  "/ai-fabric/mlops-and-neural-architecture/serving": "/ai/mlops/serving",
  "/ai-fabric/mlops-and-neural-architecture/drift": "/ai/mlops/drift",
  "/ai-fabric/mlops-and-neural-architecture/approvals": "/ai/mlops/approvals",
  "/ai-fabric/mlops-and-neural-architecture/nas": "/ai/nas",
  "/ai-fabric/mlops-and-neural-architecture/experiments": "/ai/nas/experiments",
  "/ai-fabric/mlops-and-neural-architecture/simulator": "/ai/nas/simulator",
  "/ai-fabric/intent-processing/intent-processing": "/ai/intent-processing",
  "/ai-fabric/intent-processing/intents": "/ai/intents",
  "/ai-fabric/intent-processing/taxonomy": "/ai/intents/taxonomy",
  "/ai-fabric/intent-processing/logs": "/ai/intents/logs",
  "/ai-fabric/intent-processing/systems": "/ai/systems",
  "/ai-fabric/intent-processing/graph": "/ai/systems/graph",
  "/ai-fabric/intent-processing/capabilities": "/ai/capabilities",
  "/docs-and-spec/api-reference/api-reference": "/docs/api-reference",
  "/docs-and-spec/api-reference/api": "/docs/api",
  "/docs-and-spec/api-reference/sdks": "/docs/api/sdks",
  "/docs-and-spec/api-reference/auth": "/docs/api/auth",
  "/docs-and-spec/api-reference/webhooks": "/docs/api/webhooks",
  "/docs-and-spec/reference-artifacts/reference-artifacts": "/docs/reference-artifacts",
  "/docs-and-spec/reference-artifacts/capsules": "/docs/reference/capsules",
  "/docs-and-spec/reference-artifacts/drivers": "/docs/reference/drivers",
  "/docs-and-spec/reference-artifacts/policies": "/docs/reference/policies",
  "/docs-and-spec/reference-artifacts/evidence": "/docs/reference/evidence",
  "/docs-and-spec/reference-artifacts/data": "/docs/reference/data",
  "/docs-and-spec/reference-artifacts/ui": "/docs/reference/ui",
  "/docs-and-spec/documentation-hub/documentation-hub": "/docs/documentation-hub",
  "/docs-and-spec/documentation-hub/docs": "/docs",
  "/docs-and-spec/documentation-hub/getting-started": "/docs/getting-started",
  "/docs-and-spec/documentation-hub/tutorials": "/docs/tutorials",
  "/docs-and-spec/documentation-hub/glossary": "/docs/glossary",
  "/docs-and-spec/documentation-hub/spec-sheet": "/docs/spec-sheet",
  "/docs-and-spec/documentation-hub/release-notes": "/docs/release-notes",
  "/docs-and-spec/migration-and-integration/migration-integration": "/docs/migration-integration",
  "/docs-and-spec/migration-and-integration/migration_continued.md": "/docs/migration_continued.md",
  "/docs-and-spec/migration-and-integration/migration": "/docs/migration",
  "/docs-and-spec/migration-and-integration/integrations": "/docs/integrations",
  "/docs-and-spec/migration-and-integration/deployment": "/docs/deployment",
  "/settings-and-admin/user-and-tenant-settings/user-tenant-settings": "/settings/user-tenant-settings",
  "/settings-and-admin/user-and-tenant-settings/settings": "/settings",
  "/settings-and-admin/user-and-tenant-settings/profile": "/settings/profile",
  "/settings-and-admin/user-and-tenant-settings/preferences": "/settings/preferences",
  "/settings-and-admin/user-and-tenant-settings/notifications": "/settings/notifications",
  "/settings-and-admin/user-and-tenant-settings/credentials": "/settings/credentials",
  "/settings-and-admin/user-and-tenant-settings/api-keys": "/settings/api-keys",
  "/data-and-knowledge/indices-and-search/indices-search": "/data/indices-search",
  "/data-and-knowledge/indices-and-search/indices": "/data/indices",
  "/data-and-knowledge/indices-and-search/manage": "/data/indices/manage",
  "/data-and-knowledge/indices-and-search/fulltext": "/data/indices/fulltext",
  "/data-and-knowledge/indices-and-search/semantic": "/data/indices/semantic",
  "/data-and-knowledge/indices-and-search/embeddings": "/data/indices/embeddings",
  "/data-and-knowledge/indices-and-search/graph": "/data/indices/graph",
  "/data-and-knowledge/indices-and-search/tuning": "/data/indices/tuning",
  "/data-and-knowledge/indices-and-search/query": "/data/query",
  "/data-and-knowledge/data-protection/data-protection": "/data/data-protection",
  "/data-and-knowledge/data-protection/encryption": "/data/encryption",
  "/data-and-knowledge/data-protection/rotation": "/data/encryption/rotation",
  "/data-and-knowledge/data-protection/integrity": "/data/integrity",
  "/data-and-knowledge/replication-and-dr/replication-dr": "/data/replication-dr",
  "/data-and-knowledge/replication-and-dr/replication": "/data/replication",
  "/data-and-knowledge/replication-and-dr/consistency": "/data/consistency",
  "/data-and-knowledge/replication-and-dr/failover": "/data/dr/failover",
  "/data-and-knowledge/replication-and-dr/drills": "/data/dr/drills",
  "/data-and-knowledge/archive-and-retention/archive-retention": "/data/archive-retention",
  "/data-and-knowledge/archive-and-retention/archive": "/data/archive",
  "/data-and-knowledge/archive-and-retention/backup": "/data/backup",
  "/data-and-knowledge/archive-and-retention/policies": "/data/retention/policies",
  "/data-and-knowledge/archive-and-retention/legal-hold": "/data/legal-hold",
  "/data-and-knowledge/archive-and-retention/restore-testing": "/data/restore-testing",
  "/data-and-knowledge/observability-stores/observability-stores": "/data/observability-stores",
  "/data-and-knowledge/observability-stores/observability": "/data/observability",
  "/data-and-knowledge/observability-stores/metrics": "/data/metrics",
  "/data-and-knowledge/observability-stores/logs": "/data/logs",
  "/data-and-knowledge/observability-stores/traces": "/data/traces",
  "/data-and-knowledge/observability-stores/tiering": "/data/observability/tiering",
  "/data-and-knowledge/observability-stores/export": "/data/observability/export",
  "/data-and-knowledge/core-data-stores/core-data-stores": "/data/core-data-stores",
  "/data-and-knowledge/core-data-stores/data": "/data",
  "/data-and-knowledge/core-data-stores/cir": "/data/cir",
  "/data-and-knowledge/core-data-stores/capsules": "/data/capsules",
  "/data-and-knowledge/core-data-stores/ledger": "/data/ledger",
  "/data-and-knowledge/core-data-stores/artifacts": "/data/artifacts",
  "/data-and-knowledge/core-data-stores/schema": "/data/schema",
  "/data-and-knowledge/core-data-stores/ingestion": "/data/ingestion",
  "/data-and-knowledge/core-data-stores/lineage": "/data/lineage",
  "/data-and-knowledge/core-data-stores/quality": "/data/quality",
  "/observability-evidence/telemetry-metrics/observability": "/observability"
}

const allowsActorScope = (itemScope: ActorScope | undefined, actorScope: ActorScope) => {
  if (!itemScope) return true
  if (itemScope === 'both' || itemScope === actorScope) return true
  if (actorScope === 'enterprise' && (itemScope === 'personal' || itemScope === 'business')) return true
  if (actorScope === 'business' && itemScope === 'personal') return true
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
        if (normalized === feature.route) {
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
