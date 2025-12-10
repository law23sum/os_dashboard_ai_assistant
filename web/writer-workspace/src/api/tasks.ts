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
  const resp = await fetch(`/tasks?limit=${encodeURIComponent(limit)}`);
  if (!resp.ok) {
    throw new Error(`Tasks API error (${resp.status})`);
  }
  const data = await resp.json();
  return data.tasks ?? [];
}
