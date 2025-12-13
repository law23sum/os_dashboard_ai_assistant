import { apiRequest } from "./client";

export interface ProjectRecord {
  name: string;
  description: string;
  status: string;
  priority: string;
  order_num: number;
}

export interface ProjectSnapshot {
  projects: ProjectRecord[];
  status_counts: Record<string, number>;
  priority_counts: Record<string, number>;
  generated_at: string;
}

export async function fetchProjectSnapshot(): Promise<ProjectSnapshot> {
  return apiRequest<ProjectSnapshot>("/projects/summary");
}
