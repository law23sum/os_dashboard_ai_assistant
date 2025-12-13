import { apiRequest } from "./client";

export interface TaskRecord {
  id: number;
  title: string;
  project: string;
  priority: string;
  status: string;
  owner: string;
  due_date?: string;
  notes: string;
}

export async function fetchTasks(limit = 100): Promise<TaskRecord[]> {
  const data = await apiRequest<{ tasks: TaskRecord[] }>(`/tasks?limit=${encodeURIComponent(limit)}`);
  return data.tasks ?? [];
}
