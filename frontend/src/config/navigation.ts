import {
  LayoutDashboard,
  CheckSquare,
  FolderKanban,
  MessageSquare,
  Users,
  Target,
  Search,
  BookOpen,
  LayoutTemplate,
  Terminal,
  Activity,
  Cpu,
  ServerCog,
  Bot,
  Zap,
  Brain,
  Layers,
  Workflow,
  Package,
  Wrench,
  Shield,
  Satellite,
  Eye,
  Dna,
  Plug,
  Network,
  BarChart3,
  Radio,
  CreditCard,
  ClipboardList,
  Compass,
  FileText,
  ExternalLink,
  Settings,
  Sparkles,
  Database
} from 'lucide-react';

export interface FeatureOption {
  id: string;
  label: string;
  path?: string; // If it links to a specific route or anchor
  description?: string;
  complexity?: 'simple' | 'intermediate' | 'complex';
  icon?: any;
}

export interface Platform {
  id: string;
  label: string;
  path: string;
  icon: any;
  description?: string;
  features: FeatureOption[];
}

export interface Category {
  id: string;
  label: string;
  path: string; // Base path for the category, usually the first platform's path
  platforms: Platform[];
}

export const navigationConfig: Category[] = [
  {
    id: 'mission_control',
    label: 'Mission Control',
    path: '/dashboard',
    platforms: [
      {
        id: 'dashboard',
        label: 'Dashboard',
        path: '/dashboard',
        icon: LayoutDashboard,
        features: [
          { id: 'overview', label: 'Overview', complexity: 'simple', description: 'Main system status' },
          { id: 'alerts', label: 'Alerts', complexity: 'simple', description: 'System notifications' },
          { id: 'activity', label: 'Activity Feed', complexity: 'intermediate', description: 'Recent actions' },
          { id: 'quick_actions', label: 'Quick Actions', complexity: 'intermediate', description: 'Common tasks' }
        ]
      },
      {
        id: 'projects',
        label: 'Projects',
        path: '/projects',
        icon: FolderKanban,
        features: [
          { id: 'all_projects', label: 'All Projects', complexity: 'simple' },
          { id: 'active', label: 'Active Projects', complexity: 'simple' },
          { id: 'timeline', label: 'Timeline View', complexity: 'intermediate' },
          { id: 'kanban', label: 'Kanban Board', complexity: 'intermediate' },
          { id: 'risks', label: 'Risk Analysis', complexity: 'complex' },
          { id: 'dependencies', label: 'Dependency Graph', complexity: 'complex' }
        ]
      },
      {
        id: 'tasks',
        label: 'Tasks',
        path: '/tasks',
        icon: CheckSquare,
        features: [
          { id: 'my_tasks', label: 'My Tasks', complexity: 'simple' },
          { id: 'assigned', label: 'Assigned to Me', complexity: 'simple' },
          { id: 'due_soon', label: 'Due Soon', complexity: 'intermediate' },
          { id: 'backlog', label: 'Backlog', complexity: 'intermediate' }
        ]
      },
      {
        id: 'chat',
        label: 'Chat',
        path: '/chat',
        icon: MessageSquare,
        features: [
          { id: 'recent', label: 'Recent Chats', path: '/chat', complexity: 'simple' },
          { id: 'responses', label: 'Responses API Chat', path: '/chat/responses', icon: Sparkles, complexity: 'intermediate', description: 'Modern chat with Responses API' },
          { id: 'contacts', label: 'Contacts', complexity: 'simple' },
          { id: 'archived', label: 'Archived', complexity: 'intermediate' }
        ]
      },
      {
        id: 'collaboration',
        label: 'Collaboration',
        path: '/collaboration',
        icon: Users,
        features: [
          { id: 'teams', label: 'Teams', complexity: 'simple' },
          { id: 'shared', label: 'Shared Files', complexity: 'intermediate' }
        ]
      }
    ]
  },
  {
    id: 'workspaces',
    label: 'Workspaces',
    path: '/work/writer',
    platforms: [
      {
        id: 'writer',
        label: 'Writer Workstation',
        path: '/work/writer',
        icon: BookOpen,
        features: [
          { id: 'drafts', label: 'Drafts', complexity: 'simple' },
          { id: 'canon', label: 'Canon & Lore', complexity: 'intermediate' },
          { id: 'templates', label: 'Templates', complexity: 'intermediate' },
          { id: 'publish', label: 'Publication Pipeline', complexity: 'complex' }
        ]
      },
      {
        id: 'research',
        label: 'Research Hub',
        path: '/research',
        icon: Activity,
        features: [
          { id: 'experiments', label: 'Experiments', complexity: 'intermediate' },
          { id: 'simulations', label: 'Simulations', complexity: 'complex' },
          { id: 'datasets', label: 'Datasets', complexity: 'complex' },
          { id: 'papers', label: 'Papers', complexity: 'complex' }
        ]
      },
      {
        id: 'tools',
        label: 'Tools & Terminal',
        path: '/work/tools',
        icon: Terminal,
        features: [
          { id: 'terminal', label: 'Terminal', complexity: 'intermediate' },
          { id: 'scripts', label: 'Scripts', complexity: 'complex' }
        ]
      }
    ]
  },
  {
    id: 'ai_fabric',
    label: 'AI Fabric',
    path: '/ai/operations',
    platforms: [
      {
        id: 'operations',
        label: 'AI Operations',
        path: '/ai/operations',
        icon: Cpu,
        features: [
          { id: 'status', label: 'Model Status', complexity: 'simple' },
          { id: 'metrics', label: 'Performance Metrics', complexity: 'intermediate' },
          { id: 'costs', label: 'Cost Analysis', complexity: 'complex' }
        ]
      },
      {
        id: 'copilot',
        label: 'AI Copilot',
        path: '/ai/copilot',
        icon: Bot,
        features: [
          { id: 'chat', label: 'Chat Interface', complexity: 'simple' },
          { id: 'context', label: 'Context Manager', complexity: 'intermediate' },
          { id: 'prompts', label: 'Prompt Library', complexity: 'intermediate' }
        ]
      },
      {
        id: 'workflows',
        label: 'Workflow Orchestrator',
        path: '/ai/workflows',
        icon: Workflow,
        features: [
          { id: 'active_flows', label: 'Active Flows', complexity: 'intermediate' },
          { id: 'builder', label: 'Workflow Builder', complexity: 'complex' },
          { id: 'history', label: 'Execution History', complexity: 'intermediate' }
        ]
      }
    ]
  },
  {
    id: 'systems',
    label: 'Systems & Integrations',
    path: '/integrations',
    platforms: [
      {
        id: 'integrations',
        label: 'Integrations Hub',
        path: '/integrations',
        icon: Plug,
        features: [
          { id: 'installed', label: 'Installed Drivers', complexity: 'simple' },
          { id: 'marketplace', label: 'Marketplace', complexity: 'intermediate' },
          { id: 'settings', label: 'Configuration', complexity: 'complex' }
        ]
      },
      {
        id: 'security',
        label: 'Security Operations',
        path: '/systems/security',
        icon: Shield,
        features: [
          { id: 'threat_map', label: 'Threat Map', complexity: 'simple' },
          { id: 'incidents', label: 'Incidents', complexity: 'intermediate' },
          { id: 'policies', label: 'Policy Management', complexity: 'complex' },
          { id: 'audit', label: 'Audit Log', complexity: 'complex' }
        ]
      },
      {
        id: 'network',
        label: 'Network Monitoring',
        path: '/systems/network',
        icon: Network,
        features: [
          { id: 'topology', label: 'Topology Map', complexity: 'intermediate' },
          { id: 'traffic', label: 'Traffic Analysis', complexity: 'complex' },
          { id: 'nodes', label: 'Node Status', complexity: 'intermediate' }
        ]
      }
    ]
  },
  {
    id: 'governance',
    label: 'Governance',
    path: '/analytics',
    platforms: [
      {
        id: 'analytics',
        label: 'Analytics',
        path: '/analytics',
        icon: BarChart3,
        features: [
          { id: 'dashboards', label: 'Dashboards', complexity: 'simple' },
          { id: 'reports', label: 'Reports', complexity: 'intermediate' }
        ]
      },
      {
        id: 'audit',
        label: 'Audit Evidence',
        path: '/audit',
        icon: ClipboardList,
        features: [
          { id: 'logs', label: 'Access Logs', complexity: 'intermediate' },
          { id: 'compliance', label: 'Compliance Checks', complexity: 'complex' }
        ]
      },
      {
        id: 'vector_stores',
        label: 'Vector Stores',
        path: '/vector-stores',
        icon: Database,
        description: 'Manage vector stores for file search',
        features: [
          { id: 'manage', label: 'Manage Stores', complexity: 'simple' },
          { id: 'upload', label: 'Upload Files', complexity: 'intermediate' },
          { id: 'search', label: 'Search', complexity: 'intermediate' },
          { id: 'settings', label: 'Settings', complexity: 'intermediate' }
        ]
      },
      {
        id: 'billing',
        label: 'Billing',
        path: '/billing',
        icon: CreditCard,
        features: [
          { id: 'usage', label: 'Usage', complexity: 'simple' },
          { id: 'invoices', label: 'Invoices', complexity: 'simple' },
          { id: 'budgets', label: 'Budgets', complexity: 'intermediate' }
        ]
      }
    ]
  },
  {
    id: 'settings',
    label: 'Settings',
    path: '/settings',
    platforms: [
      {
        id: 'settings',
        label: 'Global Settings',
        path: '/settings',
        icon: Settings,
        features: [
          { id: 'general', label: 'General', complexity: 'simple' },
          { id: 'appearance', label: 'Appearance', complexity: 'simple' },
          { id: 'notifications', label: 'Notifications', complexity: 'simple' },
          { id: 'account', label: 'Account', complexity: 'intermediate' }
        ]
      }
    ]
  }
];
