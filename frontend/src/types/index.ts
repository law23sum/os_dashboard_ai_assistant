export interface Task {
  id: number
  title: string
  project: string
  status: string
  priority: string
  due_date: string | null
  notes: string
  owner: string
  created_at: string
  depends_on?: number | null
  recurrence_pattern?: string | null
  recurrence_end?: string | null
  time_estimated?: number | null
  time_logged?: number | null
  template_id?: string | null
}

export interface Project {
  name: string
  description: string
  status: string
  priority: string
  order_num: number
}

export interface ProjectLink {
  id: number
  project_id: string
  integration_type: string
  title: string
  description: string
  external_id: string
  created_at: string
  last_synced?: string | null
  label: string
  href?: string | null
  available: boolean
}

export interface ProjectLedgerEvent {
  id: string
  project_id: string
  event_type: string
  entity_type?: string | null
  entity_id?: string | null
  payload: Record<string, unknown>
  created_at: string
  hash_prev?: string | null
  hash_curr: string
}

export interface ProjectRiskInsight {
  risk_score: number
  severity: string
  risks: Array<{
    type: string
    severity: string
    count?: number
    completion_rate?: string
    message: string
  }>
  recommendations: string
  total_tasks: number
  completed_tasks: number
  completion_rate: number
}

export interface ProjectForecastInsight {
  predicted_date?: string | null
  confidence: string
  reasoning: string
  estimated_days?: number | null
  avg_completion_days?: number | null
  pending_task_count: number
}

export interface ProjectInsightResponse {
  project: string
  generated_at: string
  risk: ProjectRiskInsight
  forecast: ProjectForecastInsight
}

export interface ProjectIntelligence {
  project_id: string
  health_score: number
  risk_level: string
  completion_ratio: number
  total_tasks: number
  open_tasks: number
  critical_tasks: number
  ledger_ok: boolean
  last_event_at?: string | null
  last_event_type?: string | null
  summary: string
}

export interface ProjectLedgerEvent {
  id: string
  project_id: string
  event_type: string
  entity_type?: string | null
  entity_id?: string | null
  payload: Record<string, unknown>
  created_at: string
  hash_prev?: string | null
  hash_curr: string
}

export interface ChatMessage {
  id: number
  persona: string
  role: string
  kind: string
  content: string
  created_at: string
}

export type ChangePermissionMode = 'auto' | 'ask' | 'ask_when_unsure'
export type ContinuityMode = 'full' | 'automation-off' | 'read-only'
export type RiskAppetite = 'conservative' | 'balanced' | 'progressive'

export interface Settings {
  theme: string
  default_view: string
  show_system_status: boolean
  font_scale: string
  data_preferences: Record<string, boolean>
  change_permission_mode?: ChangePermissionMode
  continuity_mode?: ContinuityMode
  risk_appetite?: RiskAppetite
}

export interface IntegrationStatus {
  service: string
  connected: boolean
  username?: string
  last_sync?: string
}

export interface ConnectorAction {
  name: string
  label: string
  description?: string
  options?: Record<string, unknown>
}

export interface ConnectorStatus {
  id: string
  name: string
  category: string
  connected: boolean
  status: string
  last_sync?: string | null
  item_count: number
  error?: string | null
  pending_actions: number
  health_score: number
  actions: ConnectorAction[]
}

export interface ConnectorSummary {
  total: number
  connected: number
  degraded: number
  disconnected: number
  average_health: number
}

export interface ConnectorActivity {
  timestamp: string
  connector_id: string
  severity: string
  message: string
  details?: string
}

export interface ConnectorOverview {
  summary: ConnectorSummary
  connectors: ConnectorStatus[]
  activity: ConnectorActivity[]
  actions_catalog: Record<string, ConnectorAction[]>
}

export interface ComplianceMetric {
  framework: string
  score: number
  issues: number
  status: string
  last_checked: string
}

export interface AuditSummary {
  risk_score: number
  controls_in_place: number
  controls_healthy: number
  outstanding_actions: number
  last_check: string
  metrics: ComplianceMetric[]
}

export interface AuditLogEntry {
  id: string
  event: string
  resource: string
  user: string
  level: string
  timestamp: string
  status: string
}

export interface AuditCheckResponse {
  started_at: string
  completed_at: string
  issues_found: number
  notes: string
}

export interface DashboardStats {
  total_tasks: number
  tasks_by_status: Record<string, number>
  tasks_by_priority: Record<string, number>
  total_projects: number
  active_projects: number
  system_stats: {
    cpu_percent: number
    memory_percent: number
    disk_percent: number
  }
  security_status: {
    status: string
    message: string
    updated_at: string
    source: string
  }
}

export interface DocumentOperation {
  id: number
  title: string
  project_id: string
  integration_type: string
  external_id: string
  operation: string
  status: string
  persona: string
  version_tag: string | null
  diff_path: string | null
  external_company: string | null
  started_at: string
  completed_at: string | null
  notes: string
}

export interface DocumentOperationSummary {
  queued: number
  running: number
  succeeded: number
  failed: number
  needs_review: number
}

export interface AgentRun {
  id: number
  agent: string
  action_type: string
  input_context: string
  output_summary: string
  related_files: string
  git_commit_hash?: string | null
  created_at: string
}

export interface BillingUsage {
  estimated_cost: number
  currency: string
  records: AgentRun[]
}

export interface SearchStatus {
  documents_indexed: number
  tasks_indexed: number
  projects_indexed: number
  embeddings_ready: boolean
}

export interface SearchResult {
  id: string
  kind: string
  title: string
  snippet: string
  score: number
  tags: string[]
}

export interface SearchResponse {
  query: string
  total: number
  results: SearchResult[]
  took_ms: number
}

export interface WorkflowInstance {
  id: string
  name: string
  owner: string
  status: string
  progress: number
  priority: string
  last_event: string
  eta_minutes?: number | null
}

export interface AIOSOrchestratorStatus {
  status: string
  version: string
  last_started?: string | null
  last_stopped?: string | null
  workflows_active: number
  nodes_online: number
}

export interface StorageStatus {
  documents_indexed: number
  vector_embeddings: number
  disk_used_gb: number
  disk_total_gb: number
  last_backup?: string | null
}

export interface AIOSNode {
  id: string
  location: string
  status: string
  load_percent: number
}

export interface AIOSStatus {
  orchestrator: AIOSOrchestratorStatus
  workflows: WorkflowInstance[]
  storage: StorageStatus
  nodes: AIOSNode[]
}

export interface TaskTemplate {
  id: string
  name: string
  title: string
  project: string
  priority: string
  notes: string
  time_estimated: number | null
  created_at: string
}

export interface TaskCompletionStats {
  total: number
  done: number
  in_progress: number
  todo: number
  blocked: number
  completion_rate: number
}

export interface ProjectAnalytics {
  total: number
  done: number
  in_progress: number
  todo: number
  completion_rate: number
  priority: string
}

export interface TimeTrackingStats {
  total_estimated_minutes: number
  total_logged_minutes: number
  tasks_with_time: number
  estimated_hours: number
  logged_hours: number
}

export interface ProductivityMetrics {
  completion_rate: number
  tasks_completed: number
  tasks_in_progress: number
  total_time_logged_hours: number
  average_time_per_task_minutes: number
}

export interface RecentActivityItem {
  id: number
  title: string
  project: string
  status: string
  created_at: string
}

export interface AnalyticsSummary {
  tasks: TaskCompletionStats
  projects: Record<string, ProjectAnalytics>
  time_tracking: TimeTrackingStats
  productivity: ProductivityMetrics
  recent_activity: RecentActivityItem[]
  deadline_reminders: DeadlineReminder[]
  workload: Record<string, WorkloadPersonaMetrics>
  project_health: Record<string, ProjectHealth>
  suggestions: PrioritizationSuggestion[]
}

export interface DeadlineReminder {
  task_id: number
  title: string
  project: string
  due_date?: string | null
  priority: string
  days_until: number
  urgency: 'low' | 'medium' | 'high'
}

export interface WorkloadPersonaMetrics {
  task_count: number
  estimated_hours: number
  logged_hours: number
  high_priority_count: number
  overloaded: boolean
}

export interface ProjectHealth {
  total_tasks: number
  completed: number
  blocked: number
  overdue: number
  completion_rate: number
  health_score: number
  health_status: 'healthy' | 'warning' | 'critical'
}

export interface PrioritizationSuggestion {
  type: string
  task_id?: number
  message: string
  priority: string
}

export interface MonitoringAlert {
  metric: string
  severity: string
  value: number
  threshold: number
  timestamp: string
}

export interface MonitoringEvent {
  id: string
  action: string
  status: string
  detail: string
  timestamp: string
}

export interface MonitoringSummary {
  window_hours: number
  metrics: Record<string, number>
  thresholds: Record<string, number>
  health_score: number
  alerts: MonitoringAlert[]
  events: MonitoringEvent[]
}

export interface IntegrationConnectorDetails {
  id: string
  name: string
  category: string
  status: string
  connected: boolean
  last_sync: string
  latency_ms: number
  throughput: string
  targets: string[]
  notes: string
  health: string
}

export interface IntegrationPipeline {
  id: string
  name: string
  status: string
  throughput: string
  latency_ms: number
  last_run: string
}

export interface IntegrationIncident {
  id: string
  title: string
  severity: string
  connector: string
  detail: string
  timestamp: string
}

export interface IntegrationActivity {
  id: string
  connector: string
  action: string
  status: string
  detail: string
  timestamp: string
}

export interface IntegrationSnapshot {
  summary: {
    total: number
    connected: number
    degraded: number
    disconnected: number
  }
  connectors: IntegrationConnectorDetails[]
  pipelines: IntegrationPipeline[]
  incidents: IntegrationIncident[]
  activity: IntegrationActivity[]
}

export interface ConnectorConfiguration {
  id: string
  name: string
  connected: boolean
  username?: string
  last_sync?: string
  settings_schema: Record<
    string,
    {
      label: string
      type: string
      placeholder?: string
      min?: number
      max?: number
    }
  >
  current_settings: Record<string, any>
}

export interface NASEvolutionMetrics {
  generation: number
  population_size: number
  best_fitness: number
  average_fitness: number
  diversity_score: number
}

export interface NASExperimentStatus {
  id: string
  name: string
  status: string
  generation: number
  population_size: number
  best_fitness: number
  created_at: string
  updated_at: string
}

export interface NASArchitectureSummary {
  id: string
  layers: Record<string, any>[]
  fitness: number
  discovered_at: string
  validation_accuracy: number
}

export interface NeuralArchitectureStatus {
  active_experiments: number
  total_experiments: number
  current_experiment: NASExperimentStatus | null
  evolution_metrics: NASEvolutionMetrics
  best_architecture: NASArchitectureSummary | null
  available_strategies: string[]
}

export interface SecurityEvent {
  id: string
  type: string
  severity: string
  description: string
  timestamp: string
  source_ip: string
  status: string
}

export interface SecurityMetrics {
  scans_today: number
  threats_blocked: number
  risk_score: string
  false_positives: number
  detection_accuracy: number
}

export interface SecurityStatus {
  system_status: string
  active_scans: number
  recent_events: SecurityEvent[]
  metrics: SecurityMetrics
  last_scan: string | null
  threat_detection_enabled: boolean
}

export interface SecurityReport {
  scan_summary: Record<string, number>
  recent_scans: Record<string, any>[]
  top_threats: { type: string; count: number }[]
  recommendations: string[]
  generated_at: string
}

export interface EdgeNode {
  id: string
  location: string
  status: string
  load_percent: number
  model_count: number
  last_heartbeat: string
}

export interface EdgeMetrics {
  total_nodes: number
  active_nodes: number
  total_models: number
  average_latency: number
  total_requests: number
  success_rate: number
}

export interface EdgeDeploymentRecord {
  model_id: string
  model_name: string
  target_nodes: number
  deployed_at: string
  status: string
}

export interface EdgeModel {
  id: string
  name: string
  type: string
  accuracy: number
  latency_ms: number
  deployed_at: string
  status: string
}

export interface EdgeComputingStatus {
  system_status: string
  nodes: EdgeNode[]
  metrics: EdgeMetrics
  recent_deployments: EdgeDeploymentRecord[]
  available_strategies: string[]
}

export interface WorkflowTemplate {
  id: string
  name: string
  description: string
  category: string
  estimated_duration: number
  success_rate: number
}

export interface OrchestratorMetrics {
  active_workflows: number
  completed_today: number
  success_rate: number
  average_completion_time: number
  queue_length: number
}

export interface WorkflowInstanceDetail {
  id: string
  name: string
  status: string
  priority: string
  progress_percent: number
  started_at: string
  estimated_completion: string | null
  current_step: string
  total_steps: number
  owner: string
}

export interface WorkflowStep {
  id: string
  name: string
  status: string
  duration_seconds: number
  started_at: string | null
  completed_at: string | null
}

export interface WorkflowMonitorResponse {
  success: boolean
  workflow: WorkflowInstanceDetail
  steps: WorkflowStep[]
  performance_metrics: Record<string, string>
  logs: string[]
}

export interface WorkflowOrchestratorStatus {
  status: string
  active_workflows: WorkflowInstanceDetail[]
  metrics: OrchestratorMetrics
  available_templates: WorkflowTemplate[]
  system_health: string
}

export interface WriterDocument {
  id: string
  title: string
  type: string
  status: string
  words: number
  last_edited: string
  summary: string
  theme: string
  content?: string
}

export interface WriterSuggestion {
  title: string
  body: string
}

export interface WriterCanonEntry {
  category: string
  title: string
  description: string
  meta: string
}

export interface WriterPipelineEntry {
  title: string
  summary: string
  meta: string
  status: string
}

export interface WriterStats {
  total_words: number
  documents: number
  avg_words_per_day: number
  writing_streak: number
}

export interface WriterProgress {
  days: string[]
  series: number[]
  goal: number
}

export interface WriterSnapshot {
  documents: WriterDocument[]
  suggestions: WriterSuggestion[]
  canon_entries: WriterCanonEntry[]
  pipeline_entries: WriterPipelineEntry[]
  stats: WriterStats
  progress: WriterProgress
  timestamp: string
}

export interface AICapability {
  id: string
  label: string
  description: string
  enabled: boolean
}

export interface AdvancedAIStatusMetrics {
  requests_today: number
  insights_generated: number
  autonomy_level: string
}

export interface AdvancedAIStatus {
  available: boolean
  initialized: boolean
  last_run?: string | null
  health: string
  capabilities: AICapability[]
  metrics: AdvancedAIStatusMetrics
}

export interface AdvancedAIResultMetrics {
  latency_ms: number
  tokens_used: number
  confidence: number
}

export interface AdvancedAIResult {
  title: string
  output: string
  timestamp: string
  metrics: AdvancedAIResultMetrics
}

export interface TerminalCommandEntry {
  label: string
  command: string
  description: string
}

export interface TerminalCommandCatalog {
  spec_sheet: TerminalCommandEntry[]
  backend_cli: TerminalCommandEntry[]
  templates: TerminalCommandEntry[]
}

export interface TerminalResult {
  command: string
  stdout: string
  stderr: string
  exit_code: number
  shell: string
  cwd: string
  ok: boolean
}

export interface TerminalHistoryEntry extends TerminalResult {
  id: string
  timestamp: string
}
