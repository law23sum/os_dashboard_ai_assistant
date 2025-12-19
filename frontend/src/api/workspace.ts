import apiClient, { apiPath } from '../lib/apiClient'

export interface WorkspaceProfile {
  name: string
  root: string
  commands: Record<string, string[][]>
  autofix_script?: string | null
  notes?: string[]
}

export interface WorkspaceResult {
  project: string
  category: string
  command: string[] | string
  status: string
  exit_code: number | null
  duration_seconds: number
  output: string
  ran_at: number
  run_id?: string
  timeout_seconds?: number
  error?: string | null
}

export interface WorkspaceReport {
  summary: {
    root: string
    generated_at: number | string
    report_path?: string
    projects: number
    checks: number
    failed: number
    passed: number
    skipped: number
    run_id?: string
    dry_run?: boolean
    status?: string
  }
  profiles: WorkspaceProfile[]
  results: WorkspaceResult[]
}

export interface HarnessProjectSummary {
  name: string
  status: string
  failed: number
  passed: number
  skipped: number
  commands: string[]
}

export interface HarnessReport {
  generated_at?: string
  status: string
  root: string
  total_projects: number
  total_checks: number
  failed_checks: number
  passed_checks: number
  skipped_checks: number
  run_id?: string
  report_path?: string
  projects: HarnessProjectSummary[]
}

export const fetchWorkspaceScan = async (params?: { root?: string; max_depth?: number }): Promise<{
  root: string
  projects: WorkspaceProfile[]
}> => {
  const { data } = await apiClient.get(apiPath('workspace/scan'), { params })
  return data
}

export const fetchWorkspaceDoctor = async (params?: { root?: string }) => {
  const { data } = await apiClient.get(apiPath('workspace/doctor'), { params })
  return data as { checks: { label: string; status: string; output?: string[] }[]; timestamp: number }
}

export const runWorkspaceChecks = async (body?: {
  root?: string
  max_depth?: number
  categories?: string[]
  autofix?: boolean
  dry_run?: boolean
}): Promise<WorkspaceReport> => {
  const { data } = await apiClient.post(apiPath('workspace/checks'), body)
  return data as WorkspaceReport
}

export const fetchHarnessReport = async (): Promise<HarnessReport> => {
  const { data } = await apiClient.get(apiPath('runtime/harness-report'))
  return data as HarnessReport
}
