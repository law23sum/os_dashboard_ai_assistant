export interface DashboardTask {
  id: number;
  title: string;
  project: string;
  status: string;
  priority: string;
  due_date?: string;
  owner: string;
  notes: string;
}

export interface DashboardSnapshot {
  totals: {
    tasks: number;
    active_tasks: number;
    projects: number;
    due_today: number;
  };
  today_tasks: DashboardTask[];
  upcoming_tasks: DashboardTask[];
  top_priority_tasks: DashboardTask[];
  status_counts: Record<string, number>;
  persona_load: Record<string, number>;
  generated_at: string;
}

export async function fetchDashboardSummary(): Promise<DashboardSnapshot> {
  const resp = await fetch("/dashboard/summary");
  if (!resp.ok) {
    throw new Error(`Dashboard API error (${resp.status})`);
  }
  return resp.json();
}
