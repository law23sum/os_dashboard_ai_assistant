export type PmsMode = 'personal' | 'enterprise'
export type PmsTaskStatus = 'TODO' | 'IN_PROGRESS' | 'BLOCKED' | 'DONE' | 'ARCHIVED'
export type PmsEpicStatus = 'PLANNED' | 'ACTIVE' | 'ON_HOLD' | 'DONE' | 'ARCHIVED'
export type PmsTodoStatus = 'PENDING' | 'DONE'
export type PmsRunStatus = 'queued' | 'running' | 'succeeded' | 'failed'
export type PmsDocumentKind = 'spec' | 'notes' | 'runbook' | 'manuscript' | 'draft' | 'journal'
export type PmsVisibility = 'private' | 'shared' | 'public'
export type PmsJournalSectionType =
  | 'Comments'
  | 'KnowledgeTransfer'
  | 'DisputableDebate'
  | 'ChallengesRisks'
  | 'SolutionsMitigations'
  | 'ProposalRaised'
  | 'MisunderstandingClarification'
  | 'TechnicalDesign'
  | 'CommonDiscussions'
  | 'Questions'
  | 'NextSteps'

export interface PmsProject {
  project_id: string
  name: string
  mode: PmsMode
  scope: string
  created_at: string
  updated_at: string
  config?: Record<string, unknown>
  budget?: {
    amount: number
    currency: string
  } | null
}

export interface PmsEpic {
  epic_id: string
  project_id: string
  title: string
  description: string
  acceptance_criteria: string
  status: PmsEpicStatus
  created_at: string
  updated_at: string
  rollup?: {
    total_tasks: number
    done_tasks: number
    completion_ratio: number
  }
}

export interface PmsTodo {
  todo_id: string
  task_id: string
  text: string
  status: PmsTodoStatus
  position: number
  created_at: string
  updated_at: string
}

export interface PmsTask {
  task_id: string
  project_id: string
  epic_id?: string | null
  title: string
  deliverable_spec?: string
  acceptance_criteria?: string
  priority: string
  category: string
  task_type: string
  status: PmsTaskStatus
  created_at: string
  updated_at: string
  enqueue_time: string
  todos: PmsTodo[]
}

export interface PmsLaneQueue {
  lane_key: string
  task_ids: string[]
}

export interface PmsSchedulerTier {
  tier: string
  lanes: PmsLaneQueue[]
}

export interface PmsSchedulerIndex {
  project_id: string
  tiers: PmsSchedulerTier[]
}

export interface PmsExecutionRun {
  run_id: string
  project_id: string
  epic_id?: string | null
  task_id?: string | null
  todo_id?: string | null
  input_params: Record<string, unknown>
  status: PmsRunStatus
  started_at: string
  ended_at?: string | null
  summary?: string | null
  created_by?: string | null
}

export interface PmsArtifact {
  artifact_id: string
  run_id: string
  project_id: string
  kind: string
  filename: string
  mime_type: string
  size: number
  sha256: string
  created_at: string
}

export interface PmsDocument {
  document_id: string
  project_id: string
  epic_id?: string | null
  task_id?: string | null
  title: string
  kind: PmsDocumentKind
  visibility: PmsVisibility
  created_at: string
  updated_at: string
  published_revision_hash?: string | null
}

export interface PmsDocumentRevision {
  revision_hash: string
  document_id: string
  parent_hash?: string | null
  author?: string | null
  created_at: string
  metadata?: Record<string, unknown>
  content?: string
}

export interface PmsMeetingSession {
  meeting_id: string
  project_id: string
  epic_id?: string | null
  task_id?: string | null
  title: string
  occurred_at?: string | null
  started_at?: string | null
  ended_at?: string | null
  participants: string[]
  language: string
  created_by: string
  created_at: string
  speaker_mapping?: Record<string, string>
  speaker_mapping_consent?: boolean
}

export interface PmsTranscriptSegment {
  meeting_id: string
  ts_start: number
  ts_end: number
  speaker_label: string
  text_original: string
  text_translated?: string | null
  confidence?: number | null
}

export interface PmsJournalBlock {
  meeting_id: string
  ts_start: number
  ts_end: number
  section_type: PmsJournalSectionType
  speaker_label?: string | null
  content: string
  references?: Record<string, string>
  created_at: string
}

export interface PmsExpenseEntry {
  expense_id: string
  project_id: string
  epic_id?: string | null
  task_id?: string | null
  amount: number
  currency: string
  category: string
  vendor: string
  occurred_at: string
  created_at: string
  updated_at: string
}

export interface PmsTimeEntry {
  time_entry_id: string
  project_id: string
  epic_id?: string | null
  task_id?: string | null
  actor_id: string
  role: string
  duration_minutes: number
  hourly_rate: number
  occurred_at: string
  created_at: string
  updated_at: string
  labor_cost?: number
}

export interface PmsCostRollup {
  project_id: string
  expense_total: number
  labor_total: number
  combined_total: number
  by_epic?: Record<string, number>
  by_task?: Record<string, number>
  currency?: string
}

export interface PmsAuditEvent {
  event_id: string
  project_id: string
  actor_id: string
  entity_type: string
  entity_id: string
  action: string
  timestamp: string
  before?: Record<string, unknown> | null
  after?: Record<string, unknown> | null
  correlation_id?: string | null
}

export interface PmsSearchResult {
  kind: string
  title: string
  subtitle?: string
  project_id?: string
  project_name?: string
  entity_id?: string
  route?: string
}

export interface PmsSearchResponse {
  results: PmsSearchResult[]
}
