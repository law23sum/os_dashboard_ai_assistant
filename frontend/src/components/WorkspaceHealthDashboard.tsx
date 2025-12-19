/**
 * WorkspaceHealthDashboard - Visual dashboard for workspace health monitoring.
 * 
 * Per Technical Spec V6:
 * - Section 7.10: Operator & SRE Workspace
 * - Section 8.16: Health & Drift Monitoring  
 * - Section 11.9: Dashboards, Alerting & On-Call Operations
 * 
 * Features:
 * - Real-time workspace health overview
 * - Project health scores with color coding
 * - TODO aggregation and filtering
 * - Auto-fix status tracking
 * - Continuation daemon controls
 */

import React, { useState, useEffect, useCallback } from 'react';

// Types
interface TodoItem {
  id: string;
  content: string;
  source_file: string;
  line_number: number;
  priority: 'low' | 'normal' | 'high' | 'critical';
  status: 'pending' | 'in_progress' | 'completed';
  category: 'general' | 'bug' | 'feature' | 'enhancement' | 'security';
}

interface ProjectHealth {
  path: string;
  name: string;
  has_git: boolean;
  has_autofix_script: boolean;
  has_tests: boolean;
  has_manifest: boolean;
  todos: TodoItem[];
  autofix_status: 'not_run' | 'running' | 'passed' | 'failed' | 'skipped';
  test_status: 'not_run' | 'running' | 'passed' | 'failed' | 'skipped';
  lint_status: 'not_run' | 'running' | 'passed' | 'failed' | 'skipped';
  last_checked: string | null;
  errors: string[];
  warnings: string[];
  health_score: number;
}

interface WorkspaceSummary {
  total_projects: number;
  healthy_projects: number;
  warning_projects: number;
  critical_projects: number;
  total_todos: number;
  average_health: number;
}

interface WorkspaceHealth {
  root: string;
  scan_timestamp: string;
  summary: WorkspaceSummary;
  projects: ProjectHealth[];
}

interface ContinuationPayload {
  timestamp: string;
  workspace_root: string;
  continuation_required: boolean;
  priority_todos: TodoItem[];
  failed_projects: { name: string; path: string; errors: string[] }[];
  recommended_actions: { action: string; description: string }[];
  context_for_next_session: string;
}

// API functions
const API_BASE = '/api/workspace';

const fetchWorkspaceHealth = async (refresh = false): Promise<WorkspaceHealth> => {
  const response = await fetch(`${API_BASE}/health?refresh=${refresh}`);
  if (!response.ok) throw new Error('Failed to fetch workspace health');
  return response.json();
};

const fetchTodos = async (filters?: { priority?: string; status?: string }): Promise<TodoItem[]> => {
  const params = new URLSearchParams();
  if (filters?.priority) params.set('priority', filters.priority);
  if (filters?.status) params.set('status', filters.status);
  const response = await fetch(`${API_BASE}/todos?${params}`);
  if (!response.ok) throw new Error('Failed to fetch todos');
  return response.json();
};

const fetchContinuation = async (): Promise<ContinuationPayload | null> => {
  const response = await fetch(`${API_BASE}/continuation`);
  if (!response.ok) return null;
  return response.json();
};

const triggerScan = async (execute = false): Promise<void> => {
  const response = await fetch(`${API_BASE}/scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ execute }),
  });
  if (!response.ok) throw new Error('Failed to trigger scan');
};

const triggerAutofix = async (projectPath: string): Promise<void> => {
  const response = await fetch(`${API_BASE}/autofix/project`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_path: projectPath }),
  });
  if (!response.ok) throw new Error('Failed to trigger autofix');
};

const triggerContinuation = async (method = 'manual'): Promise<void> => {
  const response = await fetch(`${API_BASE}/continue`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ method }),
  });
  if (!response.ok) throw new Error('Failed to trigger continuation');
};

// Utility components
const HealthBadge: React.FC<{ score: number }> = ({ score }) => {
  const getColor = () => {
    if (score >= 70) return 'bg-green-500';
    if (score >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white ${getColor()}`}>
      {score}%
    </span>
  );
};

const StatusIcon: React.FC<{ status: string }> = ({ status }) => {
  const icons: Record<string, { icon: string; color: string }> = {
    passed: { icon: '✓', color: 'text-green-500' },
    failed: { icon: '✗', color: 'text-red-500' },
    running: { icon: '⟳', color: 'text-blue-500' },
    skipped: { icon: '○', color: 'text-gray-400' },
    not_run: { icon: '–', color: 'text-gray-400' },
  };
  const { icon, color } = icons[status] || icons.not_run;
  return <span className={color}>{icon}</span>;
};

const PriorityBadge: React.FC<{ priority: string }> = ({ priority }) => {
  const colors: Record<string, string> = {
    critical: 'bg-red-600 text-white',
    high: 'bg-orange-500 text-white',
    normal: 'bg-blue-500 text-white',
    low: 'bg-gray-400 text-white',
  };
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${colors[priority] || colors.normal}`}>
      {priority.toUpperCase()}
    </span>
  );
};

// Main components
const SummaryCards: React.FC<{ summary: WorkspaceSummary }> = ({ summary }) => {
  const cards = [
    { label: 'Total Projects', value: summary.total_projects, color: 'bg-blue-100 text-blue-800' },
    { label: 'Healthy', value: summary.healthy_projects, color: 'bg-green-100 text-green-800' },
    { label: 'Warning', value: summary.warning_projects, color: 'bg-yellow-100 text-yellow-800' },
    { label: 'Critical', value: summary.critical_projects, color: 'bg-red-100 text-red-800' },
    { label: 'Total TODOs', value: summary.total_todos, color: 'bg-purple-100 text-purple-800' },
    { label: 'Avg Health', value: `${summary.average_health}%`, color: 'bg-indigo-100 text-indigo-800' },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
      {cards.map((card) => (
        <div key={card.label} className={`p-4 rounded-lg ${card.color}`}>
          <div className="text-2xl font-bold">{card.value}</div>
          <div className="text-sm opacity-80">{card.label}</div>
        </div>
      ))}
    </div>
  );
};

const ProjectList: React.FC<{
  projects: ProjectHealth[];
  onTriggerAutofix: (path: string) => void;
}> = ({ projects, onTriggerAutofix }) => {
  const [filter, setFilter] = useState<'all' | 'healthy' | 'warning' | 'critical'>('all');

  const filteredProjects = projects.filter((p) => {
    if (filter === 'all') return true;
    if (filter === 'healthy') return p.health_score >= 70;
    if (filter === 'warning') return p.health_score >= 40 && p.health_score < 70;
    if (filter === 'critical') return p.health_score < 40;
    return true;
  });

  return (
    <div className="bg-white rounded-lg shadow mb-6">
      <div className="px-4 py-3 border-b flex justify-between items-center">
        <h2 className="text-lg font-semibold">Projects</h2>
        <div className="flex gap-2">
          {(['all', 'healthy', 'warning', 'critical'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded text-sm ${
                filter === f
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>
      <div className="divide-y max-h-96 overflow-y-auto">
        {filteredProjects.map((project) => (
          <div key={project.path} className="p-4 hover:bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <HealthBadge score={project.health_score} />
                <div>
                  <div className="font-medium">{project.name}</div>
                  <div className="text-xs text-gray-500 font-mono">{project.path}</div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-sm flex gap-4">
                  <span title="Auto-fix Status">
                    <StatusIcon status={project.autofix_status} /> Fix
                  </span>
                  <span title="Test Status">
                    <StatusIcon status={project.test_status} /> Test
                  </span>
                  <span title="TODOs">
                    📝 {project.todos.length}
                  </span>
                </div>
                {project.has_autofix_script && (
                  <button
                    onClick={() => onTriggerAutofix(project.path)}
                    className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                  >
                    Run Auto-fix
                  </button>
                )}
              </div>
            </div>
            {(project.errors.length > 0 || project.warnings.length > 0) && (
              <div className="mt-2 text-sm">
                {project.errors.map((err, i) => (
                  <div key={i} className="text-red-600">⚠️ {err}</div>
                ))}
                {project.warnings.map((warn, i) => (
                  <div key={i} className="text-yellow-600">⚡ {warn}</div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const TodoList: React.FC<{ todos: TodoItem[] }> = ({ todos }) => {
  const [priorityFilter, setPriorityFilter] = useState<string>('all');

  const filteredTodos = priorityFilter === 'all'
    ? todos
    : todos.filter((t) => t.priority === priorityFilter);

  return (
    <div className="bg-white rounded-lg shadow mb-6">
      <div className="px-4 py-3 border-b flex justify-between items-center">
        <h2 className="text-lg font-semibold">Priority TODOs</h2>
        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
          className="px-3 py-1 border rounded text-sm"
        >
          <option value="all">All Priorities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="normal">Normal</option>
          <option value="low">Low</option>
        </select>
      </div>
      <div className="divide-y max-h-80 overflow-y-auto">
        {filteredTodos.slice(0, 50).map((todo) => (
          <div key={todo.id} className="p-3 hover:bg-gray-50">
            <div className="flex items-start gap-3">
              <PriorityBadge priority={todo.priority} />
              <div className="flex-1">
                <div className="text-sm">{todo.content}</div>
                <div className="text-xs text-gray-500 font-mono mt-1">
                  {todo.source_file}:{todo.line_number}
                </div>
              </div>
              <span className="text-xs px-2 py-0.5 bg-gray-100 rounded">
                {todo.category}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const ContinuationPanel: React.FC<{
  continuation: ContinuationPayload | null;
  onTrigger: (method: string) => void;
}> = ({ continuation, onTrigger }) => {
  if (!continuation || !continuation.continuation_required) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
        <div className="flex items-center gap-2">
          <span className="text-green-600 text-xl">✓</span>
          <span className="font-medium text-green-800">No Continuation Required</span>
        </div>
        <p className="text-sm text-green-700 mt-1">
          All critical tasks are addressed. Workspace is in good health.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-amber-600 text-xl">⚠️</span>
          <span className="font-medium text-amber-800">Continuation Required</span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onTrigger('manual')}
            className="px-3 py-1 bg-amber-600 text-white rounded text-sm hover:bg-amber-700"
          >
            View Prompt
          </button>
          <button
            onClick={() => onTrigger('cursor')}
            className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
          >
            Open in Cursor
          </button>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <div className="font-medium text-amber-800">Priority TODOs</div>
          <div className="text-2xl font-bold text-amber-900">
            {continuation.priority_todos.length}
          </div>
        </div>
        <div>
          <div className="font-medium text-amber-800">Failed Projects</div>
          <div className="text-2xl font-bold text-amber-900">
            {continuation.failed_projects.length}
          </div>
        </div>
      </div>
      {continuation.recommended_actions.length > 0 && (
        <div className="mt-3 pt-3 border-t border-amber-200">
          <div className="font-medium text-amber-800 mb-2">Recommended Actions:</div>
          <ul className="text-sm text-amber-700 space-y-1">
            {continuation.recommended_actions.map((action, i) => (
              <li key={i}>• {action.description}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

// Main Dashboard Component
export const WorkspaceHealthDashboard: React.FC = () => {
  const [health, setHealth] = useState<WorkspaceHealth | null>(null);
  const [todos, setTodos] = useState<TodoItem[]>([]);
  const [continuation, setContinuation] = useState<ContinuationPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async (refresh = false) => {
    try {
      setLoading(true);
      setError(null);
      const [healthData, todoData, contData] = await Promise.all([
        fetchWorkspaceHealth(refresh),
        fetchTodos({ status: 'pending' }),
        fetchContinuation(),
      ]);
      setHealth(healthData);
      setTodos(todoData);
      setContinuation(contData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleScan = async (execute = false) => {
    try {
      setScanning(true);
      await triggerScan(execute);
      // Wait a bit for scan to start, then refresh
      setTimeout(() => loadData(true), 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Scan failed');
    } finally {
      setScanning(false);
    }
  };

  const handleAutofix = async (path: string) => {
    try {
      await triggerAutofix(path);
      loadData(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Auto-fix failed');
    }
  };

  const handleContinuation = async (method: string) => {
    try {
      await triggerContinuation(method);
      loadData(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Continuation trigger failed');
    }
  };

  if (loading && !health) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <div className="mt-4 text-gray-600">Loading workspace health...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Workspace Health Dashboard</h1>
          <p className="text-sm text-gray-500">
            {health?.root} • Last scan: {health?.scan_timestamp ? new Date(health.scan_timestamp).toLocaleString() : 'Never'}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => loadData(true)}
            disabled={loading}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 disabled:opacity-50"
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
          <button
            onClick={() => handleScan(false)}
            disabled={scanning}
            className="px-4 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 disabled:opacity-50"
          >
            {scanning ? 'Scanning...' : 'Quick Scan'}
          </button>
          <button
            onClick={() => handleScan(true)}
            disabled={scanning}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            Full Scan + Execute
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
          <strong>Error:</strong> {error}
          <button onClick={() => setError(null)} className="float-right">✕</button>
        </div>
      )}

      {/* Summary Cards */}
      {health && <SummaryCards summary={health.summary} />}

      {/* Continuation Panel */}
      <ContinuationPanel continuation={continuation} onTrigger={handleContinuation} />

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Projects */}
        {health && (
          <ProjectList projects={health.projects} onTriggerAutofix={handleAutofix} />
        )}

        {/* TODOs */}
        <TodoList todos={todos} />
      </div>
    </div>
  );
};

export default WorkspaceHealthDashboard;
