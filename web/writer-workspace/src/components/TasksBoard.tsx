import { useMemo } from "react";
import { TaskRecord } from "../api/tasks";

interface Props {
  tasks: TaskRecord[];
  loading: boolean;
  error?: string;
  onRefresh: () => void;
}

export function TasksBoard({ tasks, loading, error, onRefresh }: Props) {
  const grouped = useMemo(() => {
    const byStatus: Record<string, TaskRecord[]> = {};
    for (const task of tasks) {
      if (!byStatus[task.status]) {
        byStatus[task.status] = [];
      }
      byStatus[task.status].push(task);
    }
    return byStatus;
  }, [tasks]);

  return (
    <div className="workspace">
      <header className="workspace-header">
        <div>
          <h1>Tasks</h1>
          <p>Shared view of the execution queue from the desktop console.</p>
        </div>
        <button onClick={onRefresh} disabled={loading}>
          {loading ? "Refreshing…" : "↻ Refresh"}
        </button>
      </header>
      {error && <div className="status-text warning">{error}</div>}

      <div className="tasks-grid">
        {Object.entries(grouped).map(([status, records]) => (
          <section className="tasks-column" key={status}>
            <h3>{status}</h3>
            {records.length === 0 ? (
              <p className="muted">No tasks in this state.</p>
            ) : (
              <ul>
                {records.map((task) => (
                  <li key={task.id}>
                    <strong>
                      #{task.id} · {task.title}
                    </strong>
                    <span className="muted">
                      {task.project} • {task.priority} • Owner: {task.owner}
                      {task.due_date ? ` • Due ${task.due_date}` : ""}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        ))}
      </div>
    </div>
  );
}
