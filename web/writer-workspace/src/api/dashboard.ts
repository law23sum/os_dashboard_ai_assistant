import { apiRequest } from "./client";

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

export interface WebPageLink {
  label: string;
  url: string;
  kind: string;
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
  web_pages?: WebPageLink[];
}

export async function fetchDashboardSummary(): Promise<DashboardSnapshot> {
  return apiRequest<DashboardSnapshot>("/dashboard/summary");
}
