import { useMemo, useState } from "react";
import { TaskRecord } from "../api/tasks";
import { StatsCard } from "./StatsCard";

const STATUS_COLUMNS = ["TODO", "IN_PROGRESS", "BLOCKED", "DONE"];

interface Props {
  tasks: TaskRecord[];
  loading: boolean;
  error?: string;
  onRefresh: () => void;
}

export function TasksBoard({ tasks, loading, error, onRefresh }: Props) {
  const [query, setQuery] = useState("");
  const [ownerFilter, setOwnerFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");

  const owners = useMemo(() => Array.from(new Set(tasks.map((task) => task.owner))).sort(), [tasks]);
  const filteredTasks = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return tasks.filter((task) => {
      const matchesTerm = !needle || task.title.toLowerCase().includes(needle) || task.notes.toLowerCase().includes(needle);
      const matchesOwner = ownerFilter === "all" || task.owner === ownerFilter;
      const matchesPriority = priorityFilter === "all" || task.priority === priorityFilter;
      return matchesTerm && matchesOwner && matchesPriority;
    });
  }, [tasks, query, ownerFilter, priorityFilter]);

  const grouped = useMemo(() => {
    const byStatus: Record<string, TaskRecord[]> = {};
    for (const column of STATUS_COLUMNS) {
      byStatus[column] = [];
    }
    for (const task of filteredTasks) {
      const column = byStatus[task.status] ? task.status : STATUS_COLUMNS[0];
      byStatus[column].push(task);
    }
    return byStatus;
  }, [filteredTasks]);

  const personaLoad = useMemo(() => {
    const load: Record<string, number> = {};
    for (const task of filteredTasks) {
      const owner = task.owner || "Unassigned";
      load[owner] = (load[owner] || 0) + 1;
    }
    return load;
  }, [filteredTasks]);

  const criticalCount = filteredTasks.filter((task) => task.priority === "CRITICAL").length;
  const overdueCount = filteredTasks.filter((task) => {
    if (!task.due_date) return false;
    const due = new Date(task.due_date);
    if (Number.isNaN(due.getTime())) return false;
    const now = new Date();
    return due < now;
  }).length;

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

      <section className="controls-card">
        <div className="tasks-filters">
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search title, notes, or project…" />
          <select value={ownerFilter} onChange={(event) => setOwnerFilter(event.target.value)}>
            <option value="all">All owners</option>
            {owners.map((owner) => (
              <option key={owner} value={owner}>
                {owner}
              </option>
            ))}
          </select>
          <select value={priorityFilter} onChange={(event) => setPriorityFilter(event.target.value)}>
            <option value="all">All priorities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
        <div className="stats-grid">
          <StatsCard label="Visible Tasks" value={filteredTasks.length} />
          <StatsCard label="Critical" value={criticalCount} />
          <StatsCard label="Overdue" value={overdueCount} />
          <StatsCard label="Owners" value={Object.keys(personaLoad).length} />
        </div>
      </section>

      <div className="tasks-insights">
        <section className="insight-card">
          <header>
            <h3>Persona Load</h3>
          </header>
          {Object.keys(personaLoad).length === 0 ? (
            <p className="muted">No active tasks.</p>
          ) : (
            <ul className="status-list">
              {Object.entries(personaLoad).map(([persona, count]) => (
                <li key={persona}>
                  <span>{persona}</span>
                  <strong>{count}</strong>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      <div className="tasks-grid">
        {STATUS_COLUMNS.map((status) => {
          const records = grouped[status] ?? [];
          return (
            <section className="tasks-column" key={status}>
              <h3>{status.replace("_", " ")}</h3>
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
          );
        })}
      </div>
    </div>
  );
}
