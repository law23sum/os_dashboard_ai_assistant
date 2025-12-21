/**
 * Complete IA Manifest - Generated from gui_nav.latest.json
 * Single Source of Truth for all 507 pages
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
    "path": "/",
    "actorScope": "both",
    "order": 1,
    "categories": [
      {
        "id": "core-flight-deck",
        "label": "Core Flight Deck",
        "homeRoute": "/",
        "homeComponentPath": "frontend/src/pages/CoreFlightDeckHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "dashboard",
            "label": "Dashboard",
            "route": "/",
            "componentPath": "frontend/src/pages/Dashboard.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "projects",
            "label": "Projects",
            "route": "/projects",
            "componentPath": "frontend/src/pages/Projects.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "project-templates",
            "label": "Project Templates",
            "route": "/projects/templates",
            "componentPath": "frontend/src/pages/ProjectTemplates.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "project-members--roles",
            "label": "Project Members & Roles",
            "route": "/projects/members",
            "componentPath": "frontend/src/pages/ProjectMembersRoles.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "project-settings",
            "label": "Project Settings",
            "route": "/projects/settings",
            "componentPath": "frontend/src/pages/ProjectSettings.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "tasks",
            "label": "Tasks",
            "route": "/tasks",
            "componentPath": "frontend/src/pages/Tasks.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "task-board-(kanban)",
            "label": "Task Board (Kanban)",
            "route": "/tasks/board",
            "componentPath": "frontend/src/pages/TaskBoard(Kanban).tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          },
          {
            "id": "task-automation--rules",
            "label": "Task Automation & Rules",
            "route": "/tasks/automation",
            "componentPath": "frontend/src/pages/TaskAutomationRules.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8
          },
          {
            "id": "task-analytics",
            "label": "Task Analytics",
            "route": "/tasks/analytics",
            "componentPath": "frontend/src/pages/TaskAnalytics.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9
          },
          {
            "id": "activity-feed",
            "label": "Activity Feed",
            "route": "/activity",
            "componentPath": "frontend/src/pages/ActivityFeed.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10
          },
          {
            "id": "notifications-center",
            "label": "Notifications Center",
            "route": "/notifications",
            "componentPath": "frontend/src/pages/NotificationsCenter.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11
          },
          {
            "id": "work-queue---inbox",
            "label": "Work Queue / Inbox",
            "route": "/inbox",
            "componentPath": "frontend/src/pages/WorkQueueInbox.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 12
          },
          {
            "id": "calendar---timeline",
            "label": "Calendar / Timeline",
            "route": "/timeline",
            "componentPath": "frontend/src/pages/CalendarTimeline.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 13
          }
        ]
      },
      {
        "id": "engagement--persona-surfaces",
        "label": "Engagement & Persona Surfaces",
        "homeRoute": "/chat",
        "homeComponentPath": "frontend/src/pages/EngagementPersonaSurfacesHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "chat",
            "label": "Chat",
            "route": "/chat",
            "componentPath": "frontend/src/pages/Chat.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "conversation-library",
            "label": "Conversation Library",
            "route": "/chat/library",
            "componentPath": "frontend/src/pages/ConversationLibrary.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "search--discovery",
            "label": "Search & Discovery",
            "route": "/search",
            "componentPath": "frontend/src/pages/SearchDiscovery.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "saved-searches--alerts",
            "label": "Saved Searches & Alerts",
            "route": "/search/saved",
            "componentPath": "frontend/src/pages/SavedSearchesAlerts.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "collaboration",
            "label": "Collaboration",
            "route": "/collaboration",
            "componentPath": "frontend/src/pages/Collaboration.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "shared-spaces---channels",
            "label": "Shared Spaces / Channels",
            "route": "/collaboration/channels",
            "componentPath": "frontend/src/pages/SharedSpacesChannels.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "mentions--presence",
            "label": "Mentions & Presence",
            "route": "/collaboration/presence",
            "componentPath": "frontend/src/pages/MentionsPresence.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          },
          {
            "id": "personalization",
            "label": "Personalization",
            "route": "/personalization",
            "componentPath": "frontend/src/pages/Personalization.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8
          },
          {
            "id": "prompt---macro-library",
            "label": "Prompt / Macro Library",
            "route": "/personalization/macros",
            "componentPath": "frontend/src/pages/PromptMacroLibrary.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9
          },
          {
            "id": "preference-profiles",
            "label": "Preference Profiles",
            "route": "/personalization/profiles",
            "componentPath": "frontend/src/pages/PreferenceProfiles.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10
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
        "id": "dev--devops-workspace",
        "label": "Dev & DevOps Workspace",
        "homeRoute": "/workspaces",
        "homeComponentPath": "frontend/src/pages/DevDevOpsWorkspaceHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "dev-workspace",
            "label": "Dev Workspace",
            "route": "/workspaces/dev",
            "componentPath": "frontend/src/pages/DevWorkspace.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "developer-tools",
            "label": "Developer Tools",
            "route": "/work/tools",
            "componentPath": "frontend/src/pages/DeveloperTools.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "repo--branch-browser",
            "label": "Repo & Branch Browser",
            "route": "/workspaces/dev/repos",
            "componentPath": "frontend/src/pages/RepoBranchBrowser.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "ci-cd-integration",
            "label": "CI/CD Integration",
            "route": "/workspaces/dev/cicd",
            "componentPath": "frontend/src/pages/CICDIntegration.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "build-test-insights",
            "label": "Build/Test Insights",
            "route": "/workspaces/dev/build-insights",
            "componentPath": "frontend/src/pages/BuildTestInsights.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "commit-task-generator",
            "label": "Commit → Task Generator",
            "route": "/workspaces/dev/commit-tasks",
            "componentPath": "frontend/src/pages/workspaces/Dev/CommitTaskGenerator.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "code-review-queue",
            "label": "Code Review Queue",
            "route": "/workspaces/dev/reviews",
            "componentPath": "frontend/src/pages/CodeReviewQueue.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          },
          {
            "id": "code-merge-advisor",
            "label": "Code Merge Advisor",
            "route": "/workspaces/dev/merge-advisor",
            "componentPath": "frontend/src/pages/CodeMergeAdvisor.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8
          },
          {
            "id": "dependency-updates",
            "label": "Dependency Updates",
            "route": "/workspaces/dev/deps",
            "componentPath": "frontend/src/pages/DependencyUpdates.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9
          },
          {
            "id": "release-notes-generator",
            "label": "Release Notes Generator",
            "route": "/workspaces/dev/release-notes",
            "componentPath": "frontend/src/pages/ReleaseNotesGenerator.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10
          },
          {
            "id": "local-environment-health",
            "label": "Local Environment Health",
            "route": "/workspaces/dev/env-health",
            "componentPath": "frontend/src/pages/LocalEnvironmentHealth.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11
          }
        ]
      },
      {
        "id": "research--simulation-workspace",
        "label": "Research & Simulation Workspace",
        "homeRoute": "/research",
        "homeComponentPath": "frontend/src/pages/ResearchSimulationWorkspaceHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "research-hub",
            "label": "Research Hub",
            "route": "/research",
            "componentPath": "frontend/src/pages/ResearchHub.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "unified-research-lab",
            "label": "Unified Research Lab",
            "route": "/workspaces/research/lab",
            "componentPath": "frontend/src/pages/UnifiedResearchLab.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "dataset-registry",
            "label": "Dataset Registry",
            "route": "/workspaces/research/datasets",
            "componentPath": "frontend/src/pages/DatasetRegistry.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "notebook---lab-notes",
            "label": "Notebook / Lab Notes",
            "route": "/workspaces/research/notes",
            "componentPath": "frontend/src/pages/NotebookLabNotes.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "experiment-design",
            "label": "Experiment Design",
            "route": "/workspaces/research/experiments",
            "componentPath": "frontend/src/pages/ExperimentDesign.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "experiment-tracking",
            "label": "Experiment Tracking",
            "route": "/workspaces/research/tracking",
            "componentPath": "frontend/src/pages/ExperimentTracking.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "simulation-workbench",
            "label": "Simulation Workbench",
            "route": "/workspaces/research/simulation",
            "componentPath": "frontend/src/pages/SimulationWorkbench.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          },
          {
            "id": "hpc-orchestrator",
            "label": "HPC Orchestrator",
            "route": "/workspaces/research/hpc",
            "componentPath": "frontend/src/pages/HPCOrchestrator.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8
          },
          {
            "id": "model-validation",
            "label": "Model Validation",
            "route": "/workspaces/research/validation",
            "componentPath": "frontend/src/pages/ModelValidation.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9
          },
          {
            "id": "reproducibility-packs",
            "label": "Reproducibility Packs",
            "route": "/workspaces/research/reproducibility",
            "componentPath": "frontend/src/pages/ReproducibilityPacks.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10
          },
          {
            "id": "results-publishing",
            "label": "Results Publishing",
            "route": "/workspaces/research/publishing",
            "componentPath": "frontend/src/pages/ResultsPublishing.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11
          },
          {
            "id": "digital-twin-builder",
            "label": "Digital Twin Builder",
            "route": "/workspaces/research/digital-twins",
            "componentPath": "frontend/src/pages/DigitalTwinBuilder.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 12
          }
        ]
      },
      {
        "id": "writer-workspace",
        "label": "Writer Workspace",
        "homeRoute": "/work",
        "homeComponentPath": "frontend/src/pages/WriterWorkspaceHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 3,
        "features": [
          {
            "id": "writer-workstation",
            "label": "Writer Workstation",
            "route": "/work/writer",
            "componentPath": "frontend/src/pages/WriterWorkstation.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "templates",
            "label": "Templates",
            "route": "/work/templates",
            "componentPath": "frontend/src/pages/Templates.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "style-guide-manager",
            "label": "Style Guide Manager",
            "route": "/workspaces/writer/style-guide",
            "componentPath": "frontend/src/pages/StyleGuideManager.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "canon--lore",
            "label": "Canon & Lore",
            "route": "/workspaces/writer/canon",
            "componentPath": "frontend/src/pages/CanonLore.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "narrative-guidance",
            "label": "Narrative Guidance",
            "route": "/workspaces/writer/narrative",
            "componentPath": "frontend/src/pages/NarrativeGuidance.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "story-qa--continuity",
            "label": "Story QA & Continuity",
            "route": "/workspaces/writer/qa",
            "componentPath": "frontend/src/pages/StoryQAContinuity.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "versioning--change-log",
            "label": "Versioning & Change Log",
            "route": "/workspaces/writer/versioning",
            "componentPath": "frontend/src/pages/VersioningChangeLog.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          },
          {
            "id": "citations--references",
            "label": "Citations & References",
            "route": "/workspaces/writer/citations",
            "componentPath": "frontend/src/pages/CitationsReferences.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8
          },
          {
            "id": "originality-check",
            "label": "Originality Check",
            "route": "/workspaces/writer/originality",
            "componentPath": "frontend/src/pages/OriginalityCheck.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9
          },
          {
            "id": "export--publishing",
            "label": "Export & Publishing",
            "route": "/workspaces/writer/publishing",
            "componentPath": "frontend/src/pages/ExportPublishing.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10
          }
        ]
      },
      {
        "id": "cybersecurity-workspace",
        "label": "Cybersecurity Workspace",
        "homeRoute": "/ai",
        "homeComponentPath": "frontend/src/pages/CybersecurityWorkspaceHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 4,
        "features": [
          {
            "id": "security-guardian",
            "label": "Security Guardian",
            "route": "/ai/security",
            "componentPath": "frontend/src/pages/SecurityGuardian.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "findings--triage",
            "label": "Findings & Triage",
            "route": "/workspaces/cyber/findings",
            "componentPath": "frontend/src/pages/FindingsTriage.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "threat-modeling",
            "label": "Threat Modeling",
            "route": "/workspaces/cyber/threat-modeling",
            "componentPath": "frontend/src/pages/ThreatModeling.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "policy-as-code-checks",
            "label": "Policy-as-Code Checks",
            "route": "/workspaces/cyber/policy-checks",
            "componentPath": "frontend/src/pages/Policy-as-CodeChecks.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "vulnerability-scan-integrations",
            "label": "Vulnerability Scan Integrations",
            "route": "/workspaces/cyber/scanners",
            "componentPath": "frontend/src/pages/VulnerabilityScanIntegrations.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "threat-intel-feeds",
            "label": "Threat Intel Feeds",
            "route": "/workspaces/cyber/intel",
            "componentPath": "frontend/src/pages/ThreatIntelFeeds.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "playbooks--runbooks",
            "label": "Playbooks & Runbooks",
            "route": "/workspaces/cyber/playbooks",
            "componentPath": "frontend/src/pages/PlaybooksRunbooks.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          },
          {
            "id": "incident-commander",
            "label": "Incident Commander",
            "route": "/workspaces/cyber/incidents",
            "componentPath": "frontend/src/pages/IncidentCommander.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8
          },
          {
            "id": "auto-remediation",
            "label": "Auto-Remediation",
            "route": "/workspaces/cyber/auto-remediation",
            "componentPath": "frontend/src/pages/Auto-Remediation.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9
          }
        ]
      },
      {
        "id": "business--finance-workspace",
        "label": "Business & Finance Workspace",
        "homeRoute": "/workspaces",
        "homeComponentPath": "frontend/src/pages/BusinessFinanceWorkspaceHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 5,
        "features": [
          {
            "id": "business-console",
            "label": "Business Console",
            "route": "/workspaces/finance",
            "componentPath": "frontend/src/pages/BusinessConsole.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "kpi-dashboard",
            "label": "KPI Dashboard",
            "route": "/workspaces/finance/kpis",
            "componentPath": "frontend/src/pages/KPIDashboard.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "budget-planner",
            "label": "Budget Planner",
            "route": "/workspaces/finance/budgets",
            "componentPath": "frontend/src/pages/BudgetPlanner.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "forecasting-lab",
            "label": "Forecasting Lab",
            "route": "/workspaces/finance/forecasting",
            "componentPath": "frontend/src/pages/ForecastingLab.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "strategy-simulation",
            "label": "Strategy Simulation",
            "route": "/workspaces/finance/scenarios",
            "componentPath": "frontend/src/pages/StrategySimulation.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "risk-register",
            "label": "Risk Register",
            "route": "/workspaces/finance/risk",
            "componentPath": "frontend/src/pages/RiskRegister.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "report-generator",
            "label": "Report Generator",
            "route": "/workspaces/finance/reports",
            "componentPath": "frontend/src/pages/ReportGenerator.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          }
        ]
      },
      {
        "id": "operator--sre-workspace",
        "label": "Operator & SRE Workspace",
        "homeRoute": "/workspaces",
        "homeComponentPath": "frontend/src/pages/OperatorSREWorkspaceHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 6,
        "features": [
          {
            "id": "sre-workspace",
            "label": "SRE Workspace",
            "route": "/workspaces/sre",
            "componentPath": "frontend/src/pages/SREWorkspace.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "reliability-dashboard",
            "label": "Reliability Dashboard",
            "route": "/workspaces/sre/reliability",
            "componentPath": "frontend/src/pages/ReliabilityDashboard.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "health--drift-monitors",
            "label": "Health & Drift Monitors",
            "route": "/workspaces/sre/health",
            "componentPath": "frontend/src/pages/HealthDriftMonitors.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "runbook-library",
            "label": "Runbook Library",
            "route": "/workspaces/sre/runbooks",
            "componentPath": "frontend/src/pages/RunbookLibrary.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "incident-timeline",
            "label": "Incident Timeline",
            "route": "/workspaces/sre/incidents",
            "componentPath": "frontend/src/pages/IncidentTimeline.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "change-management",
            "label": "Change Management",
            "route": "/workspaces/sre/changes",
            "componentPath": "frontend/src/pages/ChangeManagement.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "capacity--cost-insights",
            "label": "Capacity & Cost Insights",
            "route": "/workspaces/sre/capacity-cost",
            "componentPath": "frontend/src/pages/CapacityCostInsights.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          },
          {
            "id": "maintenance-windows",
            "label": "Maintenance Windows",
            "route": "/workspaces/sre/maintenance",
            "componentPath": "frontend/src/pages/MaintenanceWindows.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8
          },
          {
            "id": "sandbox-management",
            "label": "Sandbox Management",
            "route": "/workspaces/sre/sandbox",
            "componentPath": "frontend/src/pages/SandboxManagement.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9
          }
        ]
      },
      {
        "id": "archive--continuity-workspace",
        "label": "Archive & Continuity Workspace",
        "homeRoute": "/workspaces",
        "homeComponentPath": "frontend/src/pages/ArchiveContinuityWorkspaceHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 7,
        "features": [
          {
            "id": "archive-workspace",
            "label": "Archive Workspace",
            "route": "/workspaces/archive",
            "componentPath": "frontend/src/pages/ArchiveWorkspace.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "snapshot-manager",
            "label": "Snapshot Manager",
            "route": "/workspaces/archive/snapshots",
            "componentPath": "frontend/src/pages/SnapshotManager.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "retention-policies",
            "label": "Retention Policies",
            "route": "/workspaces/archive/retention",
            "componentPath": "frontend/src/pages/RetentionPolicies.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "temporal-reconstruction",
            "label": "Temporal Reconstruction",
            "route": "/workspaces/archive/time-travel",
            "componentPath": "frontend/src/pages/TemporalReconstruction.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "restore--export",
            "label": "Restore & Export",
            "route": "/workspaces/archive/restore",
            "componentPath": "frontend/src/pages/RestoreExport.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          }
        ]
      },
      {
        "id": "digital-twin--enterprise-twin-workspace",
        "label": "Digital Twin & Enterprise Twin Workspace",
        "homeRoute": "/workspaces",
        "homeComponentPath": "frontend/src/pages/DigitalTwinEnterpriseTwinWorkspaceHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 8,
        "features": [
          {
            "id": "digital-twin-builder",
            "label": "Digital Twin Builder",
            "route": "/workspaces/twins",
            "componentPath": "frontend/src/pages/DigitalTwinBuilder.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "twin-templates",
            "label": "Twin Templates",
            "route": "/workspaces/twins/templates",
            "componentPath": "frontend/src/pages/TwinTemplates.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "data-feeds--sync",
            "label": "Data Feeds & Sync",
            "route": "/workspaces/twins/feeds",
            "componentPath": "frontend/src/pages/DataFeedsSync.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "scenario-runner",
            "label": "Scenario Runner",
            "route": "/workspaces/twins/scenarios",
            "componentPath": "frontend/src/pages/ScenarioRunner.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "reality-twin-mesh",
            "label": "Reality Twin Mesh",
            "route": "/workspaces/twins/reality-mesh",
            "componentPath": "frontend/src/pages/RealityTwinMesh.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "twin-governance",
            "label": "Twin Governance",
            "route": "/workspaces/twins/governance",
            "componentPath": "frontend/src/pages/TwinGovernance.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "enterprise-twin",
            "label": "Enterprise Twin",
            "route": "/workspaces/twins/enterprise",
            "componentPath": "frontend/src/pages/EnterpriseTwin.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          }
        ]
      },
      {
        "id": "record-auditor--logbook-workspace",
        "label": "Record Auditor & Logbook Workspace",
        "homeRoute": "/workspaces",
        "homeComponentPath": "frontend/src/pages/RecordAuditorLogbookWorkspaceHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 9,
        "features": [
          {
            "id": "record-auditor",
            "label": "Record Auditor",
            "route": "/workspaces/auditor",
            "componentPath": "frontend/src/pages/RecordAuditor.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "evidence-trails",
            "label": "Evidence Trails",
            "route": "/workspaces/auditor/evidence",
            "componentPath": "frontend/src/pages/EvidenceTrails.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "controls-mapping",
            "label": "Controls Mapping",
            "route": "/workspaces/auditor/controls",
            "componentPath": "frontend/src/pages/ControlsMapping.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "evidence-requests",
            "label": "Evidence Requests",
            "route": "/workspaces/auditor/requests",
            "componentPath": "frontend/src/pages/EvidenceRequests.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "audit-reports",
            "label": "Audit Reports",
            "route": "/workspaces/auditor/reports",
            "componentPath": "frontend/src/pages/AuditReports.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "immutable-logbook-viewer",
            "label": "Immutable Logbook Viewer",
            "route": "/workspaces/auditor/logbook",
            "componentPath": "frontend/src/pages/ImmutableLogbookViewer.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "regulator-views",
            "label": "Regulator Views",
            "route": "/workspaces/auditor/regulator",
            "componentPath": "frontend/src/pages/RegulatorViews.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          }
        ]
      }
    ]
  },
  {
    "id": "ai-fabric",
    "label": "AI Fabric",
    "path": "/ai",
    "actorScope": "both",
    "order": 3,
    "categories": [
      {
        "id": "cognitive-agents--reasoning",
        "label": "Cognitive Agents & Reasoning",
        "homeRoute": "/ai",
        "homeComponentPath": "frontend/src/pages/CognitiveAgentsReasoningHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "ai-copilot",
            "label": "AI Copilot",
            "route": "/ai/copilot",
            "componentPath": "frontend/src/pages/AICopilot.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "personas--agents",
            "label": "Personas & Agents",
            "route": "/ai/personas",
            "componentPath": "frontend/src/pages/PersonasAgents.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "prompt-instruction-library",
            "label": "Prompt/Instruction Library",
            "route": "/ai/prompts",
            "componentPath": "frontend/src/pages/PromptInstructionLibrary.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "project-intelligence",
            "label": "Project Intelligence",
            "route": "/ai/project-intelligence",
            "componentPath": "frontend/src/pages/ProjectIntelligence.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "evaluation--benchmarks",
            "label": "Evaluation & Benchmarks",
            "route": "/ai/evals",
            "componentPath": "frontend/src/pages/EvaluationBenchmarks.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "model-router---policy",
            "label": "Model Router / Policy",
            "route": "/ai/routing",
            "componentPath": "frontend/src/pages/ModelRouterPolicy.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "advanced-ai-engine",
            "label": "Advanced AI Engine",
            "route": "/ai/advanced",
            "componentPath": "frontend/src/pages/AdvancedAIEngine.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          },
          {
            "id": "daemon-framework",
            "label": "Daemon Framework",
            "route": "/ai/daemons",
            "componentPath": "frontend/src/pages/DaemonFramework.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8
          },
          {
            "id": "theoretical-reasoning-framework",
            "label": "Theoretical Reasoning Framework",
            "route": "/ai/trf",
            "componentPath": "frontend/src/pages/TheoreticalReasoningFramework.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9
          },
          {
            "id": "safety--alignment-overview",
            "label": "Safety & Alignment Overview",
            "route": "/ai/safety",
            "componentPath": "frontend/src/pages/SafetyAlignmentOverview.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10
          },
          {
            "id": "agent-registry--lifecycle",
            "label": "Agent Registry & Lifecycle",
            "route": "/ai/agents/registry",
            "componentPath": "frontend/src/pages/AgentRegistryLifecycle.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11
          }
        ]
      },
      {
        "id": "driver-fabric--system-execution",
        "label": "Driver Fabric & System Execution",
        "homeRoute": "/ai",
        "homeComponentPath": "frontend/src/pages/DriverFabricSystemExecutionHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "ai-os-control",
            "label": "AI OS Control",
            "route": "/ai/os",
            "componentPath": "frontend/src/pages/AIOSControl.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "ai-operations",
            "label": "AI Operations",
            "route": "/ai/operations",
            "componentPath": "frontend/src/pages/AIOperations.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "driver-registry",
            "label": "Driver Registry",
            "route": "/ai/drivers",
            "componentPath": "frontend/src/pages/DriverRegistry.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "driver-test-harness",
            "label": "Driver Test Harness",
            "route": "/ai/drivers/testing",
            "componentPath": "frontend/src/pages/DriverTestHarness.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "driver-health--telemetry",
            "label": "Driver Health & Telemetry",
            "route": "/ai/drivers/health",
            "componentPath": "frontend/src/pages/DriverHealthTelemetry.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "driver-permissions--sandboxing",
            "label": "Driver Permissions & Sandboxing",
            "route": "/ai/drivers/permissions",
            "componentPath": "frontend/src/pages/DriverPermissionsSandboxing.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "driver-versioning--deprecation",
            "label": "Driver Versioning & Deprecation",
            "route": "/ai/drivers/versioning",
            "componentPath": "frontend/src/pages/DriverVersioningDeprecation.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          },
          {
            "id": "os-drivers",
            "label": "OS Drivers",
            "route": "/ai/drivers/os",
            "componentPath": "frontend/src/pages/OSDrivers.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8
          },
          {
            "id": "package--env-drivers",
            "label": "Package & Env Drivers",
            "route": "/ai/drivers/package",
            "componentPath": "frontend/src/pages/PackageEnvDrivers.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9
          },
          {
            "id": "hardware-drivers",
            "label": "Hardware Drivers",
            "route": "/ai/drivers/hardware",
            "componentPath": "frontend/src/pages/HardwareDrivers.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10
          },
          {
            "id": "software--saas-drivers",
            "label": "Software & SaaS Drivers",
            "route": "/ai/drivers/software",
            "componentPath": "frontend/src/pages/SoftwareSaaSDrivers.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11
          },
          {
            "id": "data-drivers",
            "label": "Data Drivers",
            "route": "/ai/drivers/data",
            "componentPath": "frontend/src/pages/DataDrivers.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 12
          },
          {
            "id": "research--simulation-drivers",
            "label": "Research & Simulation Drivers",
            "route": "/ai/drivers/research",
            "componentPath": "frontend/src/pages/ResearchSimulationDrivers.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 13
          },
          {
            "id": "sandbox--testbed",
            "label": "Sandbox & Testbed",
            "route": "/ai/drivers/sandbox",
            "componentPath": "frontend/src/pages/SandboxTestbed.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 14
          }
        ]
      },
      {
        "id": "capsules--workflow-automation",
        "label": "Capsules & Workflow Automation",
        "homeRoute": "/ai",
        "homeComponentPath": "frontend/src/pages/CapsulesWorkflowAutomationHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 3,
        "features": [
          {
            "id": "workflow-orchestrator",
            "label": "Workflow Orchestrator",
            "route": "/ai/workflows",
            "componentPath": "frontend/src/pages/WorkflowOrchestrator.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "scheduling--triggers",
            "label": "Scheduling & Triggers",
            "route": "/ai/workflows/triggers",
            "componentPath": "frontend/src/pages/SchedulingTriggers.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "workflow-observability",
            "label": "Workflow Observability",
            "route": "/ai/workflows/observability",
            "componentPath": "frontend/src/pages/WorkflowObservability.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "capsule-builder",
            "label": "Capsule Builder",
            "route": "/ai/capsules/builder",
            "componentPath": "frontend/src/pages/CapsuleBuilder.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "capsule-templates",
            "label": "Capsule Templates",
            "route": "/ai/capsules/templates",
            "componentPath": "frontend/src/pages/CapsuleTemplates.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "my-stack-capsules",
            "label": "My Stack Capsules",
            "route": "/ai/capsules/my-stack",
            "componentPath": "frontend/src/pages/MyStackCapsules.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "capsule-runtime-settings",
            "label": "Capsule Runtime Settings",
            "route": "/ai/capsules/runtime",
            "componentPath": "frontend/src/pages/CapsuleRuntimeSettings.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          },
          {
            "id": "secrets--inputs",
            "label": "Secrets & Inputs",
            "route": "/ai/capsules/secrets",
            "componentPath": "frontend/src/pages/SecretsInputs.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8
          },
          {
            "id": "capsule-marketplace",
            "label": "Capsule Marketplace",
            "route": "/ai/capsules",
            "componentPath": "frontend/src/pages/CapsuleMarketplace.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9
          },
          {
            "id": "approval--publishing",
            "label": "Approval & Publishing",
            "route": "/ai/capsules/publishing",
            "componentPath": "frontend/src/pages/ApprovalPublishing.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10
          },
          {
            "id": "operator-studio",
            "label": "Operator Studio",
            "route": "/ai/capsules/operator-studio",
            "componentPath": "frontend/src/pages/OperatorStudio.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11
          },
          {
            "id": "auto-fix-console",
            "label": "Auto-Fix Console",
            "route": "/ai/autofix",
            "componentPath": "frontend/src/pages/Auto-FixConsole.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 12
          },
          {
            "id": "project-ledger",
            "label": "Project Ledger",
            "route": "/ai/capsules/ledger",
            "componentPath": "frontend/src/pages/ProjectLedger.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 13
          },
          {
            "id": "lineage--replay",
            "label": "Lineage & Replay",
            "route": "/ai/capsules/lineage",
            "componentPath": "frontend/src/pages/LineageReplay.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 14
          }
        ]
      },
      {
        "id": "mlops--neural-architecture",
        "label": "MLOps & Neural Architecture",
        "homeRoute": "/ai",
        "homeComponentPath": "frontend/src/pages/MLOpsNeuralArchitectureHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 4,
        "features": [
          {
            "id": "mlops",
            "label": "MLOps",
            "route": "/ai/mlops",
            "componentPath": "frontend/src/pages/MLOps.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "model-registry",
            "label": "Model Registry",
            "route": "/ai/mlops/models",
            "componentPath": "frontend/src/pages/ModelRegistry.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "dataset--feature-store",
            "label": "Dataset & Feature Store",
            "route": "/ai/mlops/data",
            "componentPath": "frontend/src/pages/DatasetFeatureStore.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "training-pipelines",
            "label": "Training Pipelines",
            "route": "/ai/mlops/pipelines",
            "componentPath": "frontend/src/pages/TrainingPipelines.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "deployment--serving",
            "label": "Deployment & Serving",
            "route": "/ai/mlops/serving",
            "componentPath": "frontend/src/pages/DeploymentServing.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "drift-monitoring",
            "label": "Drift Monitoring",
            "route": "/ai/mlops/drift",
            "componentPath": "frontend/src/pages/DriftMonitoring.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "governance-gates",
            "label": "Governance Gates",
            "route": "/ai/mlops/approvals",
            "componentPath": "frontend/src/pages/GovernanceGates.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          },
          {
            "id": "nas-console",
            "label": "NAS Console",
            "route": "/ai/nas",
            "componentPath": "frontend/src/pages/NASConsole.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8
          },
          {
            "id": "experiment-console",
            "label": "Experiment Console",
            "route": "/ai/nas/experiments",
            "componentPath": "frontend/src/pages/ExperimentConsole.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9
          },
          {
            "id": "nas-simulator",
            "label": "NAS Simulator",
            "route": "/ai/nas/simulator",
            "componentPath": "frontend/src/pages/NASSimulator.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10
          }
        ]
      },
      {
        "id": "edge--vision",
        "label": "Edge & Vision",
        "homeRoute": "/ai",
        "homeComponentPath": "frontend/src/pages/EdgeVisionHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 5,
        "features": [
          {
            "id": "edge-computing",
            "label": "Edge Computing",
            "route": "/ai/edge",
            "componentPath": "frontend/src/pages/EdgeComputing.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "device-registry",
            "label": "Device Registry",
            "route": "/ai/edge/devices",
            "componentPath": "frontend/src/pages/DeviceRegistry.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "model-packaging--deployment",
            "label": "Model Packaging & Deployment",
            "route": "/ai/edge/deploy",
            "componentPath": "frontend/src/pages/ModelPackagingDeployment.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "computer-vision",
            "label": "Computer Vision",
            "route": "/ai/vision",
            "componentPath": "frontend/src/pages/ComputerVision.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "camera-stream-integrations",
            "label": "Camera/Stream Integrations",
            "route": "/ai/vision/streams",
            "componentPath": "frontend/src/pages/CameraStreamIntegrations.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "vision-pipelines",
            "label": "Vision Pipelines",
            "route": "/ai/vision/pipelines",
            "componentPath": "frontend/src/pages/VisionPipelines.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "annotation--labeling",
            "label": "Annotation & Labeling",
            "route": "/ai/vision/labeling",
            "componentPath": "frontend/src/pages/AnnotationLabeling.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          }
        ]
      },
      {
        "id": "intent-processing",
        "label": "Intent Processing",
        "homeRoute": "/ai",
        "homeComponentPath": "frontend/src/pages/IntentProcessingHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 6,
        "features": [
          {
            "id": "intent-processor",
            "label": "Intent Processor",
            "route": "/ai/intents",
            "componentPath": "frontend/src/pages/IntentProcessor.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "intent-taxonomy--routing-rules",
            "label": "Intent Taxonomy & Routing Rules",
            "route": "/ai/intents/taxonomy",
            "componentPath": "frontend/src/pages/IntentTaxonomyRoutingRules.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "intent-logs--replay",
            "label": "Intent Logs & Replay",
            "route": "/ai/intents/logs",
            "componentPath": "frontend/src/pages/IntentLogsReplay.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "systems-map",
            "label": "Systems Map",
            "route": "/ai/systems",
            "componentPath": "frontend/src/pages/SystemsMap.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "system-dependency-graph",
            "label": "System Dependency Graph",
            "route": "/ai/systems/graph",
            "componentPath": "frontend/src/pages/SystemDependencyGraph.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "capability-registry",
            "label": "Capability Registry",
            "route": "/ai/capabilities",
            "componentPath": "frontend/src/pages/CapabilityRegistry.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          }
        ]
      }
    ]
  },
  {
    "id": "drivers-integrations",
    "label": "Drivers & Integrations",
    "path": "/drivers",
    "actorScope": "both",
    "order": 4,
    "categories": [
      {
        "id": "driver-registry--management",
        "label": "Driver Registry & Management",
        "homeRoute": "/integrations",
        "homeComponentPath": "frontend/src/pages/DriverRegistryManagementHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "overview",
            "label": "Overview",
            "route": "/integrations",
            "componentPath": "frontend/src/pages/Overview.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "driver-registry",
            "label": "Driver Registry",
            "route": "/drivers/registry",
            "componentPath": "frontend/src/pages/DriverRegistry.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "driver-sdk",
            "label": "Driver SDK",
            "route": "/drivers/sdk",
            "componentPath": "frontend/src/pages/DriverSDK.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "driver-testing--validation",
            "label": "Driver Testing & Validation",
            "route": "/drivers/testing",
            "componentPath": "frontend/src/pages/DriverTestingValidation.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "runtime-permissions",
            "label": "Runtime Permissions",
            "route": "/drivers/permissions",
            "componentPath": "frontend/src/pages/RuntimePermissions.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "versioning--deprecation",
            "label": "Versioning & Deprecation",
            "route": "/drivers/versioning",
            "componentPath": "frontend/src/pages/VersioningDeprecation.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "driver-analytics",
            "label": "Driver Analytics",
            "route": "/drivers/analytics",
            "componentPath": "frontend/src/pages/DriverAnalytics.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          },
          {
            "id": "publishing-flow",
            "label": "Publishing Flow",
            "route": "/drivers/publishing",
            "componentPath": "frontend/src/pages/PublishingFlow.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8
          }
        ]
      },
      {
        "id": "connectors--integrations",
        "label": "Connectors & Integrations",
        "homeRoute": "/integrations",
        "homeComponentPath": "frontend/src/pages/ConnectorsIntegrationsHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "connectors-overview",
            "label": "Connectors Overview",
            "route": "/integrations/connectors",
            "componentPath": "frontend/src/pages/ConnectorsOverview.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "credential-vault",
            "label": "Credential Vault",
            "route": "/integrations/credentials",
            "componentPath": "frontend/src/pages/CredentialVault.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "api-connectors",
            "label": "API Connectors",
            "route": "/integrations/api-connectors",
            "componentPath": "frontend/src/pages/APIConnectors.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "productivity-suites",
            "label": "Productivity Suites",
            "route": "/drivers/integrations/productivity",
            "componentPath": "frontend/src/pages/ProductivitySuites.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "code-hosts--ci-cd",
            "label": "Code Hosts & CI/CD",
            "route": "/drivers/integrations/code",
            "componentPath": "frontend/src/pages/CodeHostsCICD.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "cloud-providers",
            "label": "Cloud Providers",
            "route": "/drivers/integrations/cloud",
            "componentPath": "frontend/src/pages/CloudProviders.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "office-realtime",
            "label": "Office Realtime",
            "route": "/integrations/office",
            "componentPath": "frontend/src/pages/OfficeRealtime.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          },
          {
            "id": "finance--banking",
            "label": "Finance & Banking",
            "route": "/drivers/integrations/finance",
            "componentPath": "frontend/src/pages/FinanceBanking.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8
          },
          {
            "id": "research-data-sources",
            "label": "Research Data Sources",
            "route": "/drivers/integrations/research",
            "componentPath": "frontend/src/pages/ResearchDataSources.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9
          },
          {
            "id": "legacy--mainframe",
            "label": "Legacy & Mainframe",
            "route": "/drivers/integrations/legacy",
            "componentPath": "frontend/src/pages/LegacyMainframe.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 10
          },
          {
            "id": "webhooks--events",
            "label": "Webhooks & Events",
            "route": "/integrations/webhooks",
            "componentPath": "frontend/src/pages/WebhooksEvents.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 11
          },
          {
            "id": "data-mapping--transformations",
            "label": "Data Mapping & Transformations",
            "route": "/integrations/mappings",
            "componentPath": "frontend/src/pages/DataMappingTransformations.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 12
          },
          {
            "id": "connector-health",
            "label": "Connector Health",
            "route": "/integrations/health",
            "componentPath": "frontend/src/pages/ConnectorHealth.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 13
          },
          {
            "id": "rate-limits--quotas",
            "label": "Rate Limits & Quotas",
            "route": "/integrations/rate-limits",
            "componentPath": "frontend/src/pages/RateLimitsQuotas.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 14
          }
        ]
      },
      {
        "id": "driver-packs--marketplace",
        "label": "Driver Packs & Marketplace",
        "homeRoute": "/drivers",
        "homeComponentPath": "frontend/src/pages/DriverPacksMarketplaceHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 3,
        "features": [
          {
            "id": "marketplace",
            "label": "Marketplace",
            "route": "/drivers/marketplace",
            "componentPath": "frontend/src/pages/Marketplace.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "reviews--ratings",
            "label": "Reviews & Ratings",
            "route": "/drivers/marketplace/reviews",
            "componentPath": "frontend/src/pages/ReviewsRatings.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "security-review-pipeline",
            "label": "Security Review Pipeline",
            "route": "/drivers/marketplace/security-review",
            "componentPath": "frontend/src/pages/SecurityReviewPipeline.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "driver-packs",
            "label": "Driver Packs",
            "route": "/drivers/packs",
            "componentPath": "frontend/src/pages/DriverPacks.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "pack-builder",
            "label": "Pack Builder",
            "route": "/drivers/packs/builder",
            "componentPath": "frontend/src/pages/PackBuilder.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "vertical-editions",
            "label": "Vertical Editions",
            "route": "/drivers/vertical-editions",
            "componentPath": "frontend/src/pages/VerticalEditions.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "enterprise-app-store",
            "label": "Enterprise App Store",
            "route": "/drivers/enterprise-store",
            "componentPath": "frontend/src/pages/EnterpriseAppStore.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          },
          {
            "id": "licensing--entitlements",
            "label": "Licensing & Entitlements",
            "route": "/drivers/licensing",
            "componentPath": "frontend/src/pages/LicensingEntitlements.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8
          }
        ]
      },
      {
        "id": "risk--governance",
        "label": "Risk & Governance",
        "homeRoute": "/drivers",
        "homeComponentPath": "frontend/src/pages/RiskGovernanceHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 4,
        "features": [
          {
            "id": "third-party-risk",
            "label": "Third-Party Risk",
            "route": "/drivers/risk",
            "componentPath": "frontend/src/pages/Third-PartyRisk.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "vendor-inventory",
            "label": "Vendor Inventory",
            "route": "/drivers/risk/vendors",
            "componentPath": "frontend/src/pages/VendorInventory.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "risk-assessments",
            "label": "Risk Assessments",
            "route": "/drivers/risk/assessments",
            "componentPath": "frontend/src/pages/RiskAssessments.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "remediation-tracker",
            "label": "Remediation Tracker",
            "route": "/drivers/risk/remediation",
            "componentPath": "frontend/src/pages/RemediationTracker.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "exceptions--approvals",
            "label": "Exceptions & Approvals",
            "route": "/drivers/risk/exceptions",
            "componentPath": "frontend/src/pages/ExceptionsApprovals.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          }
        ]
      }
    ]
  },
  {
    "id": "data-knowledge",
    "label": "Data & Knowledge",
    "path": "/data",
    "actorScope": "both",
    "order": 5,
    "categories": [
      {
        "id": "core-data-stores",
        "label": "Core Data Stores",
        "homeRoute": "/data",
        "homeComponentPath": "frontend/src/pages/CoreDataStoresHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "data-overview",
            "label": "Data Overview",
            "route": "/data",
            "componentPath": "frontend/src/pages/DataOverview.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "cir-store",
            "label": "CIR Store",
            "route": "/data/cir",
            "componentPath": "frontend/src/pages/CIRStore.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "capsule-store",
            "label": "Capsule Store",
            "route": "/data/capsules",
            "componentPath": "frontend/src/pages/CapsuleStore.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "project-ledger",
            "label": "Project Ledger",
            "route": "/data/ledger",
            "componentPath": "frontend/src/pages/ProjectLedger.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "binary-artifacts",
            "label": "Binary Artifacts",
            "route": "/data/artifacts",
            "componentPath": "frontend/src/pages/BinaryArtifacts.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "schema--ontology",
            "label": "Schema & Ontology",
            "route": "/data/schema",
            "componentPath": "frontend/src/pages/SchemaOntology.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "ingestion-pipelines",
            "label": "Ingestion Pipelines",
            "route": "/data/ingestion",
            "componentPath": "frontend/src/pages/IngestionPipelines.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          },
          {
            "id": "data-lineage",
            "label": "Data Lineage",
            "route": "/data/lineage",
            "componentPath": "frontend/src/pages/DataLineage.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8
          },
          {
            "id": "data-quality-checks",
            "label": "Data Quality Checks",
            "route": "/data/quality",
            "componentPath": "frontend/src/pages/DataQualityChecks.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 9
          }
        ]
      },
      {
        "id": "indices--search",
        "label": "Indices & Search",
        "homeRoute": "/data",
        "homeComponentPath": "frontend/src/pages/IndicesSearchHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "indices-overview",
            "label": "Indices Overview",
            "route": "/data/indices",
            "componentPath": "frontend/src/pages/IndicesOverview.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "index-management",
            "label": "Index Management",
            "route": "/data/indices/manage",
            "componentPath": "frontend/src/pages/IndexManagement.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "full-text-search",
            "label": "Full-Text Search",
            "route": "/data/indices/fulltext",
            "componentPath": "frontend/src/pages/Full-TextSearch.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "semantic-vector-search",
            "label": "Semantic/Vector Search",
            "route": "/data/indices/semantic",
            "componentPath": "frontend/src/pages/SemanticVectorSearch.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "embeddings-management",
            "label": "Embeddings Management",
            "route": "/data/indices/embeddings",
            "componentPath": "frontend/src/pages/EmbeddingsManagement.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "graph-index",
            "label": "Graph Index",
            "route": "/data/indices/graph",
            "componentPath": "frontend/src/pages/GraphIndex.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          },
          {
            "id": "relevance-tuning",
            "label": "Relevance Tuning",
            "route": "/data/indices/tuning",
            "componentPath": "frontend/src/pages/RelevanceTuning.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 7
          },
          {
            "id": "query-console",
            "label": "Query Console",
            "route": "/data/query",
            "componentPath": "frontend/src/pages/QueryConsole.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 8
          }
        ]
      },
      {
        "id": "observability-stores",
        "label": "Observability Stores",
        "homeRoute": "/data",
        "homeComponentPath": "frontend/src/pages/ObservabilityStoresHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 3,
        "features": [
          {
            "id": "observability-stores-overview",
            "label": "Observability Stores Overview",
            "route": "/data/observability",
            "componentPath": "frontend/src/pages/ObservabilityStoresOverview.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "metrics-store",
            "label": "Metrics Store",
            "route": "/data/metrics",
            "componentPath": "frontend/src/pages/MetricsStore.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "logs-store",
            "label": "Logs Store",
            "route": "/data/logs",
            "componentPath": "frontend/src/pages/LogsStore.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "traces-store",
            "label": "Traces Store",
            "route": "/data/traces",
            "componentPath": "frontend/src/pages/TracesStore.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "retention--tiering",
            "label": "Retention & Tiering",
            "route": "/data/observability/tiering",
            "componentPath": "frontend/src/pages/RetentionTiering.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "export--integrations",
            "label": "Export & Integrations",
            "route": "/data/observability/export",
            "componentPath": "frontend/src/pages/ExportIntegrations.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          }
        ]
      },
      {
        "id": "archive--retention",
        "label": "Archive & Retention",
        "homeRoute": "/data",
        "homeComponentPath": "frontend/src/pages/ArchiveRetentionHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 4,
        "features": [
          {
            "id": "archive",
            "label": "Archive",
            "route": "/data/archive",
            "componentPath": "frontend/src/pages/Archive.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "backup--retention",
            "label": "Backup & Retention",
            "route": "/data/backup",
            "componentPath": "frontend/src/pages/BackupRetention.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "retention-policy-builder",
            "label": "Retention Policy Builder",
            "route": "/data/retention/policies",
            "componentPath": "frontend/src/pages/RetentionPolicyBuilder.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "legal-hold",
            "label": "Legal Hold",
            "route": "/data/legal-hold",
            "componentPath": "frontend/src/pages/LegalHold.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "restore-testing",
            "label": "Restore Testing",
            "route": "/data/restore-testing",
            "componentPath": "frontend/src/pages/RestoreTesting.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          }
        ]
      },
      {
        "id": "data-protection",
        "label": "Data Protection",
        "homeRoute": "/data",
        "homeComponentPath": "frontend/src/pages/DataProtectionHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 5,
        "features": [
          {
            "id": "encryption--keys",
            "label": "Encryption & Keys",
            "route": "/data/encryption",
            "componentPath": "frontend/src/pages/EncryptionKeys.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "key-rotation--kms-integrations",
            "label": "Key Rotation & KMS Integrations",
            "route": "/data/encryption/rotation",
            "componentPath": "frontend/src/pages/KeyRotationKMSIntegrations.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "integrity-protections",
            "label": "Integrity Protections",
            "route": "/data/integrity",
            "componentPath": "frontend/src/pages/IntegrityProtections.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          }
        ]
      },
      {
        "id": "replication--dr",
        "label": "Replication & DR",
        "homeRoute": "/data",
        "homeComponentPath": "frontend/src/pages/ReplicationDRHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 6,
        "features": [
          {
            "id": "multi-region-replication",
            "label": "Multi-Region Replication",
            "route": "/data/replication",
            "componentPath": "frontend/src/pages/Multi-RegionReplication.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "consistency-models",
            "label": "Consistency Models",
            "route": "/data/consistency",
            "componentPath": "frontend/src/pages/ConsistencyModels.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "failover-controls",
            "label": "Failover Controls",
            "route": "/data/dr/failover",
            "componentPath": "frontend/src/pages/FailoverControls.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "dr-drill-planner",
            "label": "DR Drill Planner",
            "route": "/data/dr/drills",
            "componentPath": "frontend/src/pages/DRDrillPlanner.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          }
        ]
      }
    ]
  },
  {
    "id": "docs-spec",
    "label": "Docs & Spec",
    "path": "/docs",
    "actorScope": "both",
    "order": 6,
    "categories": [
      {
        "id": "documentation-hub",
        "label": "Documentation Hub",
        "homeRoute": "/docs",
        "homeComponentPath": "frontend/src/pages/DocumentationHubHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "docs-hub",
            "label": "Docs Hub",
            "route": "/docs",
            "componentPath": "frontend/src/pages/DocsHub.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "getting-started",
            "label": "Getting Started",
            "route": "/docs/getting-started",
            "componentPath": "frontend/src/pages/GettingStarted.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "tutorials",
            "label": "Tutorials",
            "route": "/docs/tutorials",
            "componentPath": "frontend/src/pages/Tutorials.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "glossary",
            "label": "Glossary",
            "route": "/docs/glossary",
            "componentPath": "frontend/src/pages/Glossary.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "technical-spec-sheet",
            "label": "Technical Spec Sheet",
            "route": "/docs/spec-sheet",
            "componentPath": "frontend/src/pages/TechnicalSpecSheet.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "release-notes",
            "label": "Release Notes",
            "route": "/docs/release-notes",
            "componentPath": "frontend/src/pages/ReleaseNotes.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          }
        ]
      },
      {
        "id": "reference-artifacts",
        "label": "Reference Artifacts",
        "homeRoute": "/docs",
        "homeComponentPath": "frontend/src/pages/ReferenceArtifactsHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "capsule-manifests",
            "label": "Capsule Manifests",
            "route": "/docs/reference/capsules",
            "componentPath": "frontend/src/pages/CapsuleManifests.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "driver-manifests",
            "label": "Driver Manifests",
            "route": "/docs/reference/drivers",
            "componentPath": "frontend/src/pages/DriverManifests.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "policy-examples",
            "label": "Policy Examples",
            "route": "/docs/reference/policies",
            "componentPath": "frontend/src/pages/PolicyExamples.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "evidence-pack-templates",
            "label": "Evidence Pack Templates",
            "route": "/docs/reference/evidence",
            "componentPath": "frontend/src/pages/EvidencePackTemplates.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "data-schemas",
            "label": "Data Schemas",
            "route": "/docs/reference/data",
            "componentPath": "frontend/src/pages/DataSchemas.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "ui-component-library",
            "label": "UI Component Library",
            "route": "/docs/reference/ui",
            "componentPath": "frontend/src/pages/UIComponentLibrary.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          }
        ]
      },
      {
        "id": "api-reference",
        "label": "API Reference",
        "homeRoute": "/docs",
        "homeComponentPath": "frontend/src/pages/APIReferenceHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 3,
        "features": [
          {
            "id": "api-reference",
            "label": "API Reference",
            "route": "/docs/api",
            "componentPath": "frontend/src/pages/APIReference.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "sdks",
            "label": "SDKs",
            "route": "/docs/api/sdks",
            "componentPath": "frontend/src/pages/SDKs.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "auth--rate-limits",
            "label": "Auth & Rate Limits",
            "route": "/docs/api/auth",
            "componentPath": "frontend/src/pages/AuthRateLimits.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "webhooks",
            "label": "Webhooks",
            "route": "/docs/api/webhooks",
            "componentPath": "frontend/src/pages/Webhooks.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          }
        ]
      },
      {
        "id": "migration--integration",
        "label": "Migration & Integration",
        "homeRoute": "/docs",
        "homeComponentPath": "frontend/src/pages/MigrationIntegrationHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 4,
        "features": [
          {
            "id": "migration-continued",
            "label": "Migration Continued",
            "route": "/docs/migration_continued.md",
            "componentPath": "frontend/src/pages/MigrationContinued.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "migration-guides",
            "label": "Migration Guides",
            "route": "/docs/migration",
            "componentPath": "frontend/src/pages/MigrationGuides.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "integration-guides",
            "label": "Integration Guides",
            "route": "/docs/integrations",
            "componentPath": "frontend/src/pages/IntegrationGuides.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "deployment-guides",
            "label": "Deployment Guides",
            "route": "/docs/deployment",
            "componentPath": "frontend/src/pages/DeploymentGuides.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
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
        "id": "user--tenant-settings",
        "label": "User & Tenant Settings",
        "homeRoute": "/settings",
        "homeComponentPath": "frontend/src/pages/UserTenantSettingsHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 1,
        "features": [
          {
            "id": "settings",
            "label": "Settings",
            "route": "/settings",
            "componentPath": "frontend/src/pages/Settings.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "user-profile",
            "label": "User Profile",
            "route": "/settings/profile",
            "componentPath": "frontend/src/pages/UserProfile.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "preferences",
            "label": "Preferences",
            "route": "/settings/preferences",
            "componentPath": "frontend/src/pages/Preferences.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
          },
          {
            "id": "notifications",
            "label": "Notifications",
            "route": "/settings/notifications",
            "componentPath": "frontend/src/pages/Notifications.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 4
          },
          {
            "id": "integrations-credentials",
            "label": "Integrations Credentials",
            "route": "/settings/credentials",
            "componentPath": "frontend/src/pages/IntegrationsCredentials.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 5
          },
          {
            "id": "api-keys",
            "label": "API Keys",
            "route": "/settings/api-keys",
            "componentPath": "frontend/src/pages/APIKeys.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 6
          }
        ]
      },
      {
        "id": "user--tenant-settings",
        "label": "User & Tenant Settings",
        "homeRoute": "/settings",
        "homeComponentPath": "frontend/src/pages/UserTenantSettingsHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "both",
        "order": 2,
        "features": [
          {
            "id": "team--members",
            "label": "Team & Members",
            "route": "/settings/team",
            "componentPath": "frontend/src/pages/TeamMembers.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 1
          },
          {
            "id": "tenancy--org-settings",
            "label": "Tenancy & Org Settings",
            "route": "/settings/tenant",
            "componentPath": "frontend/src/pages/TenancyOrgSettings.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 2
          },
          {
            "id": "audit-settings",
            "label": "Audit Settings",
            "route": "/settings/audit",
            "componentPath": "frontend/src/pages/AuditSettings.tsx",
            "bestCommit": "stable",
            "actorScope": "both",
            "order": 3
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
        "id": "mission--identity",
        "label": "Mission & Identity",
        "homeRoute": "/mission",
        "homeComponentPath": "frontend/src/pages/MissionIdentityHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 1,
        "features": [
          {
            "id": "mission--scope",
            "label": "Mission & Scope",
            "route": "/mission/overview",
            "componentPath": "frontend/src/pages/MissionScope.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "use-cases-map",
            "label": "Use Cases Map",
            "route": "/mission/use-cases",
            "componentPath": "frontend/src/pages/UseCasesMap.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "system-boundaries--non-goals",
            "label": "System Boundaries & Non-Goals",
            "route": "/mission/non-goals",
            "componentPath": "frontend/src/pages/SystemBoundariesNon-Goals.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "terminology-glossary",
            "label": "Terminology Glossary",
            "route": "/mission/glossary",
            "componentPath": "frontend/src/pages/TerminologyGlossary.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "deployment-modes",
            "label": "Deployment Modes",
            "route": "/mission/modes",
            "componentPath": "frontend/src/pages/DeploymentModes.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          },
          {
            "id": "reference-architectures-by-edition",
            "label": "Reference Architectures by Edition",
            "route": "/mission/reference-architectures",
            "componentPath": "frontend/src/pages/ReferenceArchitecturesbyEdition.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6
          },
          {
            "id": "identity--roles",
            "label": "Identity & Roles",
            "route": "/mission/identity",
            "componentPath": "frontend/src/pages/IdentityRoles.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7
          },
          {
            "id": "ai-+-driver-stack",
            "label": "AI + Driver Stack",
            "route": "/mission/ai-stack",
            "componentPath": "frontend/src/pages/AI+DriverStack.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8
          },
          {
            "id": "model-provider-layer",
            "label": "Model Provider Layer",
            "route": "/mission/models",
            "componentPath": "frontend/src/pages/ModelProviderLayer.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 9
          },
          {
            "id": "daemon-families",
            "label": "Daemon Families",
            "route": "/mission/daemons",
            "componentPath": "frontend/src/pages/DaemonFamilies.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 10
          }
        ]
      },
      {
        "id": "architecture--principles",
        "label": "Architecture & Principles",
        "homeRoute": "/mission",
        "homeComponentPath": "frontend/src/pages/ArchitecturePrinciplesHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 2,
        "features": [
          {
            "id": "architecture-overview",
            "label": "Architecture Overview",
            "route": "/mission/architecture",
            "componentPath": "frontend/src/pages/ArchitectureOverview.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "architectural-principles",
            "label": "Architectural Principles",
            "route": "/mission/principles",
            "componentPath": "frontend/src/pages/ArchitecturalPrinciples.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "major-components",
            "label": "Major Components",
            "route": "/mission/components",
            "componentPath": "frontend/src/pages/MajorComponents.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "driver-aware-orchestrator",
            "label": "Driver-Aware Orchestrator",
            "route": "/mission/orchestrator",
            "componentPath": "frontend/src/pages/Driver-AwareOrchestrator.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "component-mapping",
            "label": "Component Mapping",
            "route": "/mission/mapping",
            "componentPath": "frontend/src/pages/ComponentMapping.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          },
          {
            "id": "data-model--contracts",
            "label": "Data Model & Contracts",
            "route": "/mission/contracts",
            "componentPath": "frontend/src/pages/DataModelContracts.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6
          },
          {
            "id": "extensibility-points",
            "label": "Extensibility Points",
            "route": "/mission/extensibility",
            "componentPath": "frontend/src/pages/ExtensibilityPoints.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7
          },
          {
            "id": "threat-model-summary",
            "label": "Threat Model Summary",
            "route": "/mission/threat-model",
            "componentPath": "frontend/src/pages/ThreatModelSummary.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8
          },
          {
            "id": "performance-targets",
            "label": "Performance Targets",
            "route": "/mission/performance-targets",
            "componentPath": "frontend/src/pages/PerformanceTargets.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 9
          }
        ]
      },
      {
        "id": "planes-architecture",
        "label": "Planes Architecture",
        "homeRoute": "/mission",
        "homeComponentPath": "frontend/src/pages/PlanesArchitectureHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 3,
        "features": [
          {
            "id": "planes-overview",
            "label": "Planes Overview",
            "route": "/mission/planes",
            "componentPath": "frontend/src/pages/PlanesOverview.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "data-plane",
            "label": "Data Plane",
            "route": "/mission/planes/data",
            "componentPath": "frontend/src/pages/DataPlane.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "control-plane",
            "label": "Control Plane",
            "route": "/mission/planes/control",
            "componentPath": "frontend/src/pages/ControlPlane.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "governance-plane",
            "label": "Governance Plane",
            "route": "/mission/planes/governance",
            "componentPath": "frontend/src/pages/GovernancePlane.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "cross-plane-flows",
            "label": "Cross-Plane Flows",
            "route": "/mission/planes/cross-plane",
            "componentPath": "frontend/src/pages/Cross-PlaneFlows.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          },
          {
            "id": "plane-apis--event-contracts",
            "label": "Plane APIs & Event Contracts",
            "route": "/mission/planes/contracts",
            "componentPath": "frontend/src/pages/PlaneAPIsEventContracts.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6
          },
          {
            "id": "failure-domains-by-plane",
            "label": "Failure Domains by Plane",
            "route": "/mission/planes/failure-domains",
            "componentPath": "frontend/src/pages/FailureDomainsbyPlane.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7
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
        "id": "policy--governance-engine",
        "label": "Policy & Governance Engine",
        "homeRoute": "/governance",
        "homeComponentPath": "frontend/src/pages/PolicyGovernanceEngineHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 1,
        "features": [
          {
            "id": "policy-engine",
            "label": "Policy Engine",
            "route": "/governance/policy",
            "componentPath": "frontend/src/pages/PolicyEngine.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "policy-library--templates",
            "label": "Policy Library & Templates",
            "route": "/governance/policy/library",
            "componentPath": "frontend/src/pages/PolicyLibraryTemplates.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "policy-dsl",
            "label": "Policy DSL",
            "route": "/governance/policy/dsl",
            "componentPath": "frontend/src/pages/PolicyDSL.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "safety-harnesses",
            "label": "Safety Harnesses",
            "route": "/governance/policy/safety",
            "componentPath": "frontend/src/pages/SafetyHarnesses.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "policy-simulator",
            "label": "Policy Simulator",
            "route": "/governance/policy/simulator",
            "componentPath": "frontend/src/pages/PolicySimulator.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          },
          {
            "id": "policy-versioning--approvals",
            "label": "Policy Versioning & Approvals",
            "route": "/governance/policy/versioning",
            "componentPath": "frontend/src/pages/PolicyVersioningApprovals.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6
          },
          {
            "id": "enforcement-points-map",
            "label": "Enforcement Points Map",
            "route": "/governance/policy/enforcement",
            "componentPath": "frontend/src/pages/EnforcementPointsMap.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7
          },
          {
            "id": "exceptions--waivers",
            "label": "Exceptions & Waivers",
            "route": "/governance/policy/exceptions",
            "componentPath": "frontend/src/pages/ExceptionsWaivers.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8
          }
        ]
      },
      {
        "id": "compliance--regulator-fabric",
        "label": "Compliance & Regulator Fabric",
        "homeRoute": "/governance",
        "homeComponentPath": "frontend/src/pages/ComplianceRegulatorFabricHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 2,
        "features": [
          {
            "id": "compliance-packs",
            "label": "Compliance Packs",
            "route": "/governance/compliance",
            "componentPath": "frontend/src/pages/CompliancePacks.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "control-framework-mapping",
            "label": "Control Framework Mapping",
            "route": "/governance/compliance/controls",
            "componentPath": "frontend/src/pages/ControlFrameworkMapping.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "audit-readiness-dashboard",
            "label": "Audit Readiness Dashboard",
            "route": "/governance/compliance/readiness",
            "componentPath": "frontend/src/pages/AuditReadinessDashboard.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "regulator-fabric",
            "label": "Regulator Fabric",
            "route": "/governance/regulator",
            "componentPath": "frontend/src/pages/RegulatorFabric.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "regulator-tenancy",
            "label": "Regulator Tenancy",
            "route": "/governance/regulator/tenancy",
            "componentPath": "frontend/src/pages/RegulatorTenancy.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          },
          {
            "id": "evidence-access",
            "label": "Evidence Access",
            "route": "/governance/regulator/evidence",
            "componentPath": "frontend/src/pages/EvidenceAccess.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6
          },
          {
            "id": "evidence-request-workflow",
            "label": "Evidence Request Workflow",
            "route": "/governance/regulator/requests",
            "componentPath": "frontend/src/pages/EvidenceRequestWorkflow.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7
          }
        ]
      },
      {
        "id": "identity--access",
        "label": "Identity & Access",
        "homeRoute": "/governance",
        "homeComponentPath": "frontend/src/pages/IdentityAccessHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 3,
        "features": [
          {
            "id": "identity--roles",
            "label": "Identity & Roles",
            "route": "/governance/identity",
            "componentPath": "frontend/src/pages/IdentityRoles.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "authentication",
            "label": "Authentication",
            "route": "/governance/identity/auth",
            "componentPath": "frontend/src/pages/Authentication.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "sso-saml-oidc-settings",
            "label": "SSO/SAML/OIDC Settings",
            "route": "/governance/identity/sso",
            "componentPath": "frontend/src/pages/SSOSAMLOIDCSettings.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "scim-provisioning",
            "label": "SCIM Provisioning",
            "route": "/governance/identity/scim",
            "componentPath": "frontend/src/pages/SCIMProvisioning.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "rbac-abac",
            "label": "RBAC/ABAC",
            "route": "/governance/identity/rbac",
            "componentPath": "frontend/src/pages/RBACABAC.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          },
          {
            "id": "api-keys--tokens",
            "label": "API Keys & Tokens",
            "route": "/governance/identity/api-keys",
            "componentPath": "frontend/src/pages/APIKeysTokens.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6
          },
          {
            "id": "session-management",
            "label": "Session Management",
            "route": "/governance/identity/sessions",
            "componentPath": "frontend/src/pages/SessionManagement.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7
          },
          {
            "id": "access-reviews",
            "label": "Access Reviews",
            "route": "/governance/identity/reviews",
            "componentPath": "frontend/src/pages/AccessReviews.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8
          }
        ]
      },
      {
        "id": "data-protection--classification",
        "label": "Data Protection & Classification",
        "homeRoute": "/governance",
        "homeComponentPath": "frontend/src/pages/DataProtectionClassificationHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 4,
        "features": [
          {
            "id": "data-protection",
            "label": "Data Protection",
            "route": "/governance/data-protection",
            "componentPath": "frontend/src/pages/DataProtection.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "data-classification",
            "label": "Data Classification",
            "route": "/governance/data-protection/classification",
            "componentPath": "frontend/src/pages/DataClassification.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "data-masking",
            "label": "Data Masking",
            "route": "/governance/data-protection/masking",
            "componentPath": "frontend/src/pages/DataMasking.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "tokenization",
            "label": "Tokenization",
            "route": "/governance/data-protection/tokenization",
            "componentPath": "frontend/src/pages/Tokenization.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "dlp-rules",
            "label": "DLP Rules",
            "route": "/governance/data-protection/dlp",
            "componentPath": "frontend/src/pages/DLPRules.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          },
          {
            "id": "data-residency",
            "label": "Data Residency",
            "route": "/governance/data-protection/residency",
            "componentPath": "frontend/src/pages/DataResidency.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6
          }
        ]
      },
      {
        "id": "security-monitoring--response",
        "label": "Security Monitoring & Response",
        "homeRoute": "/governance",
        "homeComponentPath": "frontend/src/pages/SecurityMonitoringResponseHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 5,
        "features": [
          {
            "id": "security-monitoring",
            "label": "Security Monitoring",
            "route": "/governance/security/monitoring",
            "componentPath": "frontend/src/pages/SecurityMonitoring.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "alerts--rules",
            "label": "Alerts & Rules",
            "route": "/governance/security/alerts",
            "componentPath": "frontend/src/pages/AlertsRules.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "threat-detection",
            "label": "Threat Detection",
            "route": "/governance/security/detection",
            "componentPath": "frontend/src/pages/ThreatDetection.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "risk-scoring",
            "label": "Risk Scoring",
            "route": "/governance/security/risk",
            "componentPath": "frontend/src/pages/RiskScoring.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "alignment-monitor",
            "label": "Alignment Monitor",
            "route": "/governance/security/alignment",
            "componentPath": "frontend/src/pages/AlignmentMonitor.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          },
          {
            "id": "incident-response",
            "label": "Incident Response",
            "route": "/governance/security/incidents",
            "componentPath": "frontend/src/pages/IncidentResponse.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6
          },
          {
            "id": "forensics--evidence",
            "label": "Forensics & Evidence",
            "route": "/governance/security/forensics",
            "componentPath": "frontend/src/pages/ForensicsEvidence.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7
          },
          {
            "id": "vulnerability-management",
            "label": "Vulnerability Management",
            "route": "/governance/security/vuln",
            "componentPath": "frontend/src/pages/VulnerabilityManagement.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8
          }
        ]
      },
      {
        "id": "ai-billing--cost-governance",
        "label": "AI Billing & Cost Governance",
        "homeRoute": "/billing",
        "homeComponentPath": "frontend/src/pages/AIBillingCostGovernanceHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 6,
        "features": [
          {
            "id": "billing--usage",
            "label": "Billing & Usage",
            "route": "/billing",
            "componentPath": "frontend/src/pages/BillingUsage.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "usage-fabric",
            "label": "Usage Fabric",
            "route": "/governance/billing/usage",
            "componentPath": "frontend/src/pages/UsageFabric.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "budgets--quotas",
            "label": "Budgets & Quotas",
            "route": "/governance/billing/budgets",
            "componentPath": "frontend/src/pages/BudgetsQuotas.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "cost-guardrails",
            "label": "Cost Guardrails",
            "route": "/governance/billing/guardrails",
            "componentPath": "frontend/src/pages/CostGuardrails.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "billing-optimizer",
            "label": "Billing Optimizer",
            "route": "/governance/billing/optimizer",
            "componentPath": "frontend/src/pages/BillingOptimizer.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          },
          {
            "id": "chargeback-showback-reports",
            "label": "Chargeback/Showback Reports",
            "route": "/governance/billing/chargeback",
            "componentPath": "frontend/src/pages/ChargebackShowbackReports.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6
          },
          {
            "id": "forecasting",
            "label": "Forecasting",
            "route": "/governance/billing/forecasting",
            "componentPath": "frontend/src/pages/Forecasting.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7
          },
          {
            "id": "provider-rate-cards",
            "label": "Provider Rate Cards",
            "route": "/governance/billing/rates",
            "componentPath": "frontend/src/pages/ProviderRateCards.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8
          },
          {
            "id": "multi-tenant-billing",
            "label": "Multi-Tenant Billing",
            "route": "/governance/billing/multi-tenant",
            "componentPath": "frontend/src/pages/Multi-TenantBilling.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 9
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
        "id": "telemetry--metrics",
        "label": "Telemetry & Metrics",
        "homeRoute": "/observability",
        "homeComponentPath": "frontend/src/pages/TelemetryMetricsHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 1,
        "features": [
          {
            "id": "observability-overview",
            "label": "Observability Overview",
            "route": "/observability",
            "componentPath": "frontend/src/pages/ObservabilityOverview.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "monitoring",
            "label": "Monitoring",
            "route": "/monitoring",
            "componentPath": "frontend/src/pages/Monitoring.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "analytics",
            "label": "Analytics",
            "route": "/analytics",
            "componentPath": "frontend/src/pages/Analytics.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "metrics-model",
            "label": "Metrics Model",
            "route": "/observability/metrics",
            "componentPath": "frontend/src/pages/MetricsModel.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "metric-explorer",
            "label": "Metric Explorer",
            "route": "/observability/metrics/explorer",
            "componentPath": "frontend/src/pages/MetricExplorer.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          },
          {
            "id": "slis--slos",
            "label": "SLIs & SLOs",
            "route": "/observability/slis",
            "componentPath": "frontend/src/pages/SLIsSLOs.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6
          },
          {
            "id": "slo-burn-rates",
            "label": "SLO Burn Rates",
            "route": "/observability/slis/burn",
            "componentPath": "frontend/src/pages/SLOBurnRates.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7
          },
          {
            "id": "anomaly-detection",
            "label": "Anomaly Detection",
            "route": "/observability/anomalies",
            "componentPath": "frontend/src/pages/AnomalyDetection.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8
          }
        ]
      },
      {
        "id": "logging--tracing",
        "label": "Logging & Tracing",
        "homeRoute": "/observability",
        "homeComponentPath": "frontend/src/pages/LoggingTracingHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 2,
        "features": [
          {
            "id": "logging--tracing-overview",
            "label": "Logging & Tracing Overview",
            "route": "/observability/logging-tracing",
            "componentPath": "frontend/src/pages/LoggingTracingOverview.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "structured-logging",
            "label": "Structured Logging",
            "route": "/observability/logging",
            "componentPath": "frontend/src/pages/StructuredLogging.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "log-explorer",
            "label": "Log Explorer",
            "route": "/observability/logging/explorer",
            "componentPath": "frontend/src/pages/LogExplorer.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "distributed-tracing",
            "label": "Distributed Tracing",
            "route": "/observability/tracing",
            "componentPath": "frontend/src/pages/DistributedTracing.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "trace-explorer",
            "label": "Trace Explorer",
            "route": "/observability/tracing/explorer",
            "componentPath": "frontend/src/pages/TraceExplorer.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          },
          {
            "id": "correlation--context",
            "label": "Correlation & Context",
            "route": "/observability/correlation",
            "componentPath": "frontend/src/pages/CorrelationContext.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6
          }
        ]
      },
      {
        "id": "record-auditor--logbook",
        "label": "Record Auditor & Logbook",
        "homeRoute": "/observability",
        "homeComponentPath": "frontend/src/pages/RecordAuditorLogbookHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 3,
        "features": [
          {
            "id": "record-auditor",
            "label": "Record Auditor",
            "route": "/observability/record-auditor",
            "componentPath": "frontend/src/pages/RecordAuditor.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "logbook-timeline",
            "label": "Logbook Timeline",
            "route": "/observability/record-auditor/timeline",
            "componentPath": "frontend/src/pages/LogbookTimeline.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "audit-evidence",
            "label": "Audit Evidence",
            "route": "/audit",
            "componentPath": "frontend/src/pages/AuditEvidence.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "evidence-builder",
            "label": "Evidence Builder",
            "route": "/audit/builder",
            "componentPath": "frontend/src/pages/EvidenceBuilder.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          }
        ]
      },
      {
        "id": "evidence--audit",
        "label": "Evidence & Audit",
        "homeRoute": "/observability",
        "homeComponentPath": "frontend/src/pages/EvidenceAuditHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 4,
        "features": [
          {
            "id": "audit-logs",
            "label": "Audit Logs",
            "route": "/observability/audit-logs",
            "componentPath": "frontend/src/pages/AuditLogs.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "evidence-packs",
            "label": "Evidence Packs",
            "route": "/observability/evidence",
            "componentPath": "frontend/src/pages/EvidencePacks.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "evidence-queries",
            "label": "Evidence Queries",
            "route": "/observability/evidence/query",
            "componentPath": "frontend/src/pages/EvidenceQueries.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "export-for-auditors",
            "label": "Export for Auditors",
            "route": "/observability/evidence/export",
            "componentPath": "frontend/src/pages/ExportforAuditors.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "retention-policies",
            "label": "Retention Policies",
            "route": "/observability/retention",
            "componentPath": "frontend/src/pages/RetentionPolicies.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          }
        ]
      },
      {
        "id": "health--self-healing",
        "label": "Health & Self-Healing",
        "homeRoute": "/observability",
        "homeComponentPath": "frontend/src/pages/HealthSelf-HealingHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 5,
        "features": [
          {
            "id": "health-checks",
            "label": "Health Checks",
            "route": "/observability/health",
            "componentPath": "frontend/src/pages/HealthChecks.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "drift-detection",
            "label": "Drift Detection",
            "route": "/observability/drift",
            "componentPath": "frontend/src/pages/DriftDetection.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "runbooks",
            "label": "Runbooks",
            "route": "/observability/runbooks",
            "componentPath": "frontend/src/pages/Runbooks.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "self-healing",
            "label": "Self-Healing",
            "route": "/observability/self-healing",
            "componentPath": "frontend/src/pages/Self-Healing.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "automated-rollbacks",
            "label": "Automated Rollbacks",
            "route": "/observability/rollbacks",
            "componentPath": "frontend/src/pages/AutomatedRollbacks.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          }
        ]
      },
      {
        "id": "dashboards--alerting",
        "label": "Dashboards & Alerting",
        "homeRoute": "/observability",
        "homeComponentPath": "frontend/src/pages/DashboardsAlertingHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 6,
        "features": [
          {
            "id": "dashboards",
            "label": "Dashboards",
            "route": "/observability/dashboards",
            "componentPath": "frontend/src/pages/Dashboards.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "dashboard-builder",
            "label": "Dashboard Builder",
            "route": "/observability/dashboards/builder",
            "componentPath": "frontend/src/pages/DashboardBuilder.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "alerting",
            "label": "Alerting",
            "route": "/observability/alerting",
            "componentPath": "frontend/src/pages/Alerting.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "alert-rules",
            "label": "Alert Rules",
            "route": "/observability/alerting/rules",
            "componentPath": "frontend/src/pages/AlertRules.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "notification-channels",
            "label": "Notification Channels",
            "route": "/observability/alerting/channels",
            "componentPath": "frontend/src/pages/NotificationChannels.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          }
        ]
      },
      {
        "id": "temporal-backtesting--replay",
        "label": "Temporal Backtesting & Replay",
        "homeRoute": "/observability",
        "homeComponentPath": "frontend/src/pages/TemporalBacktestingReplayHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 7,
        "features": [
          {
            "id": "replay-engine",
            "label": "Replay Engine",
            "route": "/observability/replay",
            "componentPath": "frontend/src/pages/ReplayEngine.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "scenario-library",
            "label": "Scenario Library",
            "route": "/observability/replay/scenarios",
            "componentPath": "frontend/src/pages/ScenarioLibrary.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "determinism-checks",
            "label": "Determinism Checks",
            "route": "/observability/replay/determinism",
            "componentPath": "frontend/src/pages/DeterminismChecks.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "temporal-backtesting",
            "label": "Temporal Backtesting",
            "route": "/observability/backtesting",
            "componentPath": "frontend/src/pages/TemporalBacktesting.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
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
        "id": "performance--scalability",
        "label": "Performance & Scalability",
        "homeRoute": "/operations",
        "homeComponentPath": "frontend/src/pages/PerformanceScalabilityHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 1,
        "features": [
          {
            "id": "performance",
            "label": "Performance",
            "route": "/operations/performance",
            "componentPath": "frontend/src/pages/Performance.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "scaling-strategies",
            "label": "Scaling Strategies",
            "route": "/operations/scaling",
            "componentPath": "frontend/src/pages/ScalingStrategies.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "capacity-planning",
            "label": "Capacity Planning",
            "route": "/operations/capacity",
            "componentPath": "frontend/src/pages/CapacityPlanning.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "load-testing",
            "label": "Load Testing",
            "route": "/operations/load-testing",
            "componentPath": "frontend/src/pages/LoadTesting.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "backpressure--throttling",
            "label": "Backpressure & Throttling",
            "route": "/operations/backpressure",
            "componentPath": "frontend/src/pages/BackpressureThrottling.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          },
          {
            "id": "reliability-patterns",
            "label": "Reliability Patterns",
            "route": "/operations/reliability",
            "componentPath": "frontend/src/pages/ReliabilityPatterns.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6
          },
          {
            "id": "driver-performance",
            "label": "Driver Performance",
            "route": "/operations/driver-performance",
            "componentPath": "frontend/src/pages/DriverPerformance.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7
          },
          {
            "id": "cost-performance-tradeoffs",
            "label": "Cost/Performance Tradeoffs",
            "route": "/operations/cost-performance",
            "componentPath": "frontend/src/pages/CostPerformanceTradeoffs.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8
          }
        ]
      },
      {
        "id": "deployment-models",
        "label": "Deployment Models",
        "homeRoute": "/operations",
        "homeComponentPath": "frontend/src/pages/DeploymentModelsHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 2,
        "features": [
          {
            "id": "deployment-modes",
            "label": "Deployment Modes",
            "route": "/operations/deployment",
            "componentPath": "frontend/src/pages/DeploymentModes.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "local-mode",
            "label": "Local Mode",
            "route": "/operations/deployment/local",
            "componentPath": "frontend/src/pages/LocalMode.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "cloud-enterprise",
            "label": "Cloud/Enterprise",
            "route": "/operations/deployment/cloud",
            "componentPath": "frontend/src/pages/CloudEnterprise.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "hybrid--edge",
            "label": "Hybrid & Edge",
            "route": "/operations/deployment/hybrid",
            "componentPath": "frontend/src/pages/HybridEdge.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "kubernetes-deployment",
            "label": "Kubernetes Deployment",
            "route": "/operations/deployment/k8s",
            "componentPath": "frontend/src/pages/KubernetesDeployment.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          },
          {
            "id": "airgapped-deployment",
            "label": "Airgapped Deployment",
            "route": "/operations/deployment/airgap",
            "componentPath": "frontend/src/pages/AirgappedDeployment.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6
          },
          {
            "id": "upgrade-channels",
            "label": "Upgrade Channels",
            "route": "/operations/deployment/channels",
            "componentPath": "frontend/src/pages/UpgradeChannels.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7
          }
        ]
      },
      {
        "id": "infrastructure--topology",
        "label": "Infrastructure & Topology",
        "homeRoute": "/operations",
        "homeComponentPath": "frontend/src/pages/InfrastructureTopologyHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 3,
        "features": [
          {
            "id": "configuration-management",
            "label": "Configuration Management",
            "route": "/operations/config",
            "componentPath": "frontend/src/pages/ConfigurationManagement.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "secrets--configuration-vault",
            "label": "Secrets & Configuration Vault",
            "route": "/operations/secrets",
            "componentPath": "frontend/src/pages/SecretsConfigurationVault.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "compute-cluster-management",
            "label": "Compute/Cluster Management",
            "route": "/operations/cluster",
            "componentPath": "frontend/src/pages/ComputeClusterManagement.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "network-topology",
            "label": "Network Topology",
            "route": "/operations/topology",
            "componentPath": "frontend/src/pages/NetworkTopology.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "network-monitoring",
            "label": "Network Monitoring",
            "route": "/systems/network",
            "componentPath": "frontend/src/pages/NetworkMonitoring.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          },
          {
            "id": "storage-topology",
            "label": "Storage Topology",
            "route": "/operations/storage",
            "componentPath": "frontend/src/pages/StorageTopology.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6
          },
          {
            "id": "queues--search",
            "label": "Queues & Search",
            "route": "/operations/queues",
            "componentPath": "frontend/src/pages/QueuesSearch.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7
          },
          {
            "id": "service-dependencies",
            "label": "Service Dependencies",
            "route": "/operations/dependencies",
            "componentPath": "frontend/src/pages/ServiceDependencies.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8
          },
          {
            "id": "multi-region--dr",
            "label": "Multi-Region & DR",
            "route": "/operations/multi-region",
            "componentPath": "frontend/src/pages/Multi-RegionDR.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 9
          },
          {
            "id": "hpc-integration",
            "label": "HPC Integration",
            "route": "/operations/hpc",
            "componentPath": "frontend/src/pages/HPCIntegration.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 10
          }
        ]
      },
      {
        "id": "upgrades--migration",
        "label": "Upgrades & Migration",
        "homeRoute": "/operations",
        "homeComponentPath": "frontend/src/pages/UpgradesMigrationHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 4,
        "features": [
          {
            "id": "upgrades",
            "label": "Upgrades",
            "route": "/operations/upgrades",
            "componentPath": "frontend/src/pages/Upgrades.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "change-logs--release-notes",
            "label": "Change Logs & Release Notes",
            "route": "/operations/releases",
            "componentPath": "frontend/src/pages/ChangeLogsReleaseNotes.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "compatibility-matrix",
            "label": "Compatibility Matrix",
            "route": "/operations/compatibility",
            "componentPath": "frontend/src/pages/CompatibilityMatrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "migration",
            "label": "Migration",
            "route": "/operations/migration",
            "componentPath": "frontend/src/pages/Migration.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "rollback-strategy",
            "label": "Rollback Strategy",
            "route": "/operations/rollback",
            "componentPath": "frontend/src/pages/RollbackStrategy.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          },
          {
            "id": "blue-green--canary",
            "label": "Blue/Green & Canary",
            "route": "/operations/deployment/canary",
            "componentPath": "frontend/src/pages/BlueGreenCanary.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6
          }
        ]
      },
      {
        "id": "failure-modes--resilience",
        "label": "Failure Modes & Resilience",
        "homeRoute": "/operations",
        "homeComponentPath": "frontend/src/pages/FailureModesResilienceHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 5,
        "features": [
          {
            "id": "failure-modes",
            "label": "Failure Modes",
            "route": "/operations/failure",
            "componentPath": "frontend/src/pages/FailureModes.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "detection-mechanisms",
            "label": "Detection Mechanisms",
            "route": "/operations/detection",
            "componentPath": "frontend/src/pages/DetectionMechanisms.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "recovery-strategies",
            "label": "Recovery Strategies",
            "route": "/operations/recovery",
            "componentPath": "frontend/src/pages/RecoveryStrategies.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "data-loss-protection",
            "label": "Data Loss Protection",
            "route": "/operations/data-protection",
            "componentPath": "frontend/src/pages/DataLossProtection.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          },
          {
            "id": "business-continuity--dr",
            "label": "Business Continuity & DR",
            "route": "/operations/bc-dr",
            "componentPath": "frontend/src/pages/BusinessContinuityDR.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 5
          },
          {
            "id": "dr-drills",
            "label": "DR Drills",
            "route": "/operations/bc-dr/drills",
            "componentPath": "frontend/src/pages/DRDrills.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 6
          },
          {
            "id": "security-incidents",
            "label": "Security Incidents",
            "route": "/operations/security-incidents",
            "componentPath": "frontend/src/pages/SecurityIncidents.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 7
          },
          {
            "id": "chaos-engineering",
            "label": "Chaos Engineering",
            "route": "/operations/chaos",
            "componentPath": "frontend/src/pages/ChaosEngineering.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 8
          },
          {
            "id": "postmortems",
            "label": "Postmortems",
            "route": "/operations/postmortems",
            "componentPath": "frontend/src/pages/Postmortems.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 9
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
    "order": 12,
    "categories": [
      {
        "id": "roadmap--planning",
        "label": "Roadmap & Planning",
        "homeRoute": "/roadmap",
        "homeComponentPath": "frontend/src/pages/RoadmapPlanningHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 1,
        "features": [
          {
            "id": "roadmap-overview",
            "label": "Roadmap Overview",
            "route": "/roadmap/overview",
            "componentPath": "frontend/src/pages/RoadmapOverview.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "phased-delivery",
            "label": "Phased Delivery",
            "route": "/roadmap/phases",
            "componentPath": "frontend/src/pages/PhasedDelivery.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "milestones",
            "label": "Milestones",
            "route": "/roadmap/milestones",
            "componentPath": "frontend/src/pages/Milestones.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "long-term-bets",
            "label": "Long-Term Bets",
            "route": "/roadmap/future",
            "componentPath": "frontend/src/pages/Long-TermBets.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          }
        ]
      },
      {
        "id": "risks--decisions",
        "label": "Risks & Decisions",
        "homeRoute": "/roadmap",
        "homeComponentPath": "frontend/src/pages/RisksDecisionsHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 2,
        "features": [
          {
            "id": "risk-register",
            "label": "Risk Register",
            "route": "/roadmap/risks",
            "componentPath": "frontend/src/pages/RiskRegister.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "decision-log",
            "label": "Decision Log",
            "route": "/roadmap/decisions",
            "componentPath": "frontend/src/pages/DecisionLog.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "known-gaps",
            "label": "Known Gaps",
            "route": "/roadmap/gaps",
            "componentPath": "frontend/src/pages/KnownGaps.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "open-questions",
            "label": "Open Questions",
            "route": "/roadmap/questions",
            "componentPath": "frontend/src/pages/OpenQuestions.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
          }
        ]
      },
      {
        "id": "spec-maintenance",
        "label": "Spec Maintenance",
        "homeRoute": "/roadmap",
        "homeComponentPath": "frontend/src/pages/SpecMaintenanceHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 3,
        "features": [
          {
            "id": "spec-versioning",
            "label": "Spec Versioning",
            "route": "/roadmap/spec",
            "componentPath": "frontend/src/pages/SpecVersioning.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "deprecations",
            "label": "Deprecations",
            "route": "/roadmap/deprecations",
            "componentPath": "frontend/src/pages/Deprecations.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "backward-compatibility-commitments",
            "label": "Backward Compatibility Commitments",
            "route": "/roadmap/compatibility",
            "componentPath": "frontend/src/pages/BackwardCompatibilityCommitments.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          },
          {
            "id": "future-capabilities",
            "label": "Future Capabilities",
            "route": "/roadmap/future-capabilities",
            "componentPath": "frontend/src/pages/FutureCapabilities.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 4
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
    "order": 13,
    "categories": [
      {
        "id": "vision-deck-hub",
        "label": "Vision Deck Hub",
        "homeRoute": "/vision",
        "homeComponentPath": "frontend/src/pages/VisionDeckHubHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 1,
        "features": [
          {
            "id": "vision-deck-hub",
            "label": "Vision Deck Hub",
            "route": "/vision",
            "componentPath": "frontend/src/pages/VisionDeckHub.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "vision-roadmap",
            "label": "Vision Roadmap",
            "route": "/vision/roadmap",
            "componentPath": "frontend/src/pages/VisionRoadmap.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          },
          {
            "id": "vision-glossary",
            "label": "Vision Glossary",
            "route": "/vision/glossary",
            "componentPath": "frontend/src/pages/VisionGlossary.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 3
          }
        ]
      },
      {
        "id": "core-os-engines",
        "label": "Core OS Engines",
        "homeRoute": "/future",
        "homeComponentPath": "frontend/src/pages/CoreOSEnginesHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 2,
        "features": [
          {
            "id": "core-os-engines",
            "label": "Core OS Engines",
            "route": "/future/core_os",
            "componentPath": "frontend/src/pages/CoreOSEngines.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "capability-matrix",
            "label": "Capability Matrix",
            "route": "/future/core_os/matrix",
            "componentPath": "frontend/src/pages/CapabilityMatrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          }
        ]
      },
      {
        "id": "advanced-horizons",
        "label": "Advanced Horizons",
        "homeRoute": "/future",
        "homeComponentPath": "frontend/src/pages/AdvancedHorizonsHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 3,
        "features": [
          {
            "id": "advanced-horizons",
            "label": "Advanced Horizons",
            "route": "/future/advanced",
            "componentPath": "frontend/src/pages/AdvancedHorizons.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "capability-matrix",
            "label": "Capability Matrix",
            "route": "/future/advanced/matrix",
            "componentPath": "frontend/src/pages/CapabilityMatrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          }
        ]
      },
      {
        "id": "super-capabilities",
        "label": "Super Capabilities",
        "homeRoute": "/future",
        "homeComponentPath": "frontend/src/pages/SuperCapabilitiesHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 4,
        "features": [
          {
            "id": "super-capabilities",
            "label": "Super Capabilities",
            "route": "/future/super",
            "componentPath": "frontend/src/pages/SuperCapabilities.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "capability-matrix",
            "label": "Capability Matrix",
            "route": "/future/super/matrix",
            "componentPath": "frontend/src/pages/CapabilityMatrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          }
        ]
      },
      {
        "id": "hyper-network",
        "label": "Hyper Network",
        "homeRoute": "/future",
        "homeComponentPath": "frontend/src/pages/HyperNetworkHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 5,
        "features": [
          {
            "id": "hyper-network",
            "label": "Hyper Network",
            "route": "/future/hyper",
            "componentPath": "frontend/src/pages/HyperNetwork.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "capability-matrix",
            "label": "Capability Matrix",
            "route": "/future/hyper/matrix",
            "componentPath": "frontend/src/pages/CapabilityMatrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          }
        ]
      },
      {
        "id": "ultra-scale",
        "label": "Ultra Scale",
        "homeRoute": "/future",
        "homeComponentPath": "frontend/src/pages/UltraScaleHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 6,
        "features": [
          {
            "id": "ultra-scale",
            "label": "Ultra Scale",
            "route": "/future/ultra",
            "componentPath": "frontend/src/pages/UltraScale.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "capability-matrix",
            "label": "Capability Matrix",
            "route": "/future/ultra/matrix",
            "componentPath": "frontend/src/pages/CapabilityMatrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          }
        ]
      },
      {
        "id": "supreme",
        "label": "Supreme",
        "homeRoute": "/future",
        "homeComponentPath": "frontend/src/pages/SupremeHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 7,
        "features": [
          {
            "id": "supreme",
            "label": "Supreme",
            "route": "/future/supreme",
            "componentPath": "frontend/src/pages/Supreme.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "capability-matrix",
            "label": "Capability Matrix",
            "route": "/future/supreme/matrix",
            "componentPath": "frontend/src/pages/CapabilityMatrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          }
        ]
      },
      {
        "id": "ascend",
        "label": "Ascend",
        "homeRoute": "/future",
        "homeComponentPath": "frontend/src/pages/AscendHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 8,
        "features": [
          {
            "id": "ascend",
            "label": "Ascend",
            "route": "/future/ascend",
            "componentPath": "frontend/src/pages/Ascend.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "capability-matrix",
            "label": "Capability Matrix",
            "route": "/future/ascend/matrix",
            "componentPath": "frontend/src/pages/CapabilityMatrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          }
        ]
      },
      {
        "id": "meta-envelope",
        "label": "Meta Envelope",
        "homeRoute": "/future",
        "homeComponentPath": "frontend/src/pages/MetaEnvelopeHome.tsx",
        "homeBestCommit": "stable",
        "actorScope": "enterprise",
        "order": 9,
        "features": [
          {
            "id": "meta-envelope",
            "label": "Meta Envelope",
            "route": "/future/meta",
            "componentPath": "frontend/src/pages/MetaEnvelope.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 1
          },
          {
            "id": "capability-matrix",
            "label": "Capability Matrix",
            "route": "/future/meta/matrix",
            "componentPath": "frontend/src/pages/CapabilityMatrix.tsx",
            "bestCommit": "stable",
            "actorScope": "enterprise",
            "order": 2
          }
        ]
      }
    ]
  }
]

export function getPlatforms(actorScope: ActorScope): IAPlatform[] {
  return iaManifest.filter(p => 
    p.actorScope === 'both' || p.actorScope === actorScope
  )
}

export function getCategories(platformId: string, actorScope: ActorScope): IACategory[] {
  const platform = iaManifest.find(p => p.id === platformId)
  if (!platform) return []
  
  if (platform.actorScope !== 'both' && platform.actorScope !== actorScope) {
    return []
  }
  
  return platform.categories.filter(c => 
    c.actorScope === 'both' || c.actorScope === actorScope
  )
}

export function getFeatures(platformId: string, categoryId: string, actorScope: ActorScope): IAFeature[] {
  const platform = iaManifest.find(p => p.id === platformId)
  if (!platform) return []
  
  const category = platform.categories.find(c => c.id === categoryId)
  if (!category) return []
  
  if (category.actorScope !== 'both' && category.actorScope !== actorScope) {
    return []
  }
  
  return category.features.filter(f => 
    f.actorScope === 'both' || f.actorScope === actorScope
  )
}

export function findRouteContext(route: string): {
  platform?: IAPlatform
  category?: IACategory
  feature?: IAFeature
  isCategoryHome: boolean
} {
  for (const platform of iaManifest) {
    for (const category of platform.categories) {
      if (route === category.homeRoute) {
        return {
          platform,
          category,
          isCategoryHome: true,
        }
      }
      
      for (const feature of category.features) {
        if (route === feature.route || route.startsWith(feature.route + '/')) {
          return {
            platform,
            category,
            feature,
            isCategoryHome: false,
          }
        }
      }
    }
  }
  
  return { isCategoryHome: false }
}
