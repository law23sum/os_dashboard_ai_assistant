import { useMemo, useState } from "react";
import { ProjectSnapshot } from "../api/projects";
import { StatsCard } from "./StatsCard";

const PRIORITY_ORDER: Record<string, number> = {
  CRITICAL: 0,
  HIGH: 1,
  MEDIUM: 2,
  LOW: 3,
};

interface Props {
  snapshot: ProjectSnapshot | null;
  loading: boolean;
  error?: string;
  onRefresh: () => void;
}

export function ProjectsBoard({ snapshot, loading, error, onRefresh }: Props) {
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const filteredProjects = useMemo(() => {
    if (!snapshot) return [];
    const needle = query.trim().toLowerCase();
    return snapshot.projects.filter((project) => {
      const matchesTerm =
        !needle ||
        project.name.toLowerCase().includes(needle) ||
        project.description.toLowerCase().includes(needle) ||
        project.priority.toLowerCase().includes(needle);
      const matchesStatus = statusFilter === "all" || project.status === statusFilter;
      return matchesTerm && matchesStatus;
    });
  }, [snapshot, query, statusFilter]);

  const focusProjects = useMemo(() => {
    return [...filteredProjects]
      .sort((a, b) => {
        const priorityScore = (PRIORITY_ORDER[a.priority] ?? 99) - (PRIORITY_ORDER[b.priority] ?? 99);
        if (priorityScore !== 0) return priorityScore;
        return a.order_num - b.order_num;
      })
      .slice(0, 3);
  }, [filteredProjects]);

  const statusOptions = useMemo(() => (snapshot ? Object.keys(snapshot.status_counts) : []), [snapshot]);

  return (
    <div className="workspace">
      <header className="workspace-header">
        <div>
          <h1>Projects</h1>
          <p>Shared project portfolio used by both the desktop and web consoles.</p>
        </div>
        <button onClick={onRefresh} disabled={loading}>
          {loading ? "Refreshing…" : "↻ Refresh"}
        </button>
      </header>
      {error && <div className="status-text warning">{error}</div>}

      {snapshot ? (
        <>
          <section className="controls-card">
            <div className="tasks-filters">
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search name, description, or priority…" />
              <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
                <option value="all">All statuses</option>
                {statusOptions.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </div>
            <div className="stats-grid">
              <StatsCard label="Tracked Projects" value={snapshot.projects.length} />
              <StatsCard label="Filtered" value={filteredProjects.length} />
              <StatsCard label="Statuses" value={Object.keys(snapshot.status_counts).length} />
              <StatsCard label="Priorities" value={Object.keys(snapshot.priority_counts).length} />
            </div>
          </section>

          <section className="controls-card">
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-label">Projects</div>
                <div className="stat-value">{snapshot.projects.length}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Statuses Tracked</div>
                <div className="stat-value">{Object.keys(snapshot.status_counts).length}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Priorities Used</div>
                <div className="stat-value">{Object.keys(snapshot.priority_counts).length}</div>
              </div>
            </div>
            <div className="status-text">Last updated: {new Date(snapshot.generated_at).toLocaleTimeString()}</div>
          </section>

          <div className="projects-grid">
            <section className="projects-card">
              <header>
                <h3>Portfolio</h3>
              </header>
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredProjects.map((project) => (
                    <tr key={project.name}>
                      <td>{project.name}</td>
                      <td>{project.status}</td>
                      <td>{project.priority}</td>
                      <td>{project.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
            <section className="projects-card">
              <header>
                <h3>Focus Queue</h3>
              </header>
              {focusProjects.length === 0 ? (
                <p className="muted">No projects match the filters.</p>
              ) : (
                <div>
                  {focusProjects.map((project) => (
                    <div key={project.name} className="focus-entry">
                      <div>
                        <strong>{project.name}</strong>
                        <p className="muted">{project.description}</p>
                      </div>
                      <div className="focus-tags">
                        <span className="status-pill">{project.priority}</span>
                        <span className="status-pill">{project.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              <header>
                <h3>Status Summary</h3>
              </header>
              <ul className="status-list">
                {Object.entries(snapshot.status_counts).map(([status, count]) => (
                  <li key={status}>
                    <span>{status}</span>
                    <strong>{count}</strong>
                  </li>
                ))}
              </ul>
              <header>
                <h3>Priority Summary</h3>
              </header>
              <ul className="status-list">
                {Object.entries(snapshot.priority_counts).map(([priority, count]) => (
                  <li key={priority}>
                    <span>{priority}</span>
                    <strong>{count}</strong>
                  </li>
                ))}
              </ul>
            </section>
          </div>
        </>
      ) : (
        <div className="workspace loading">
          <p>{loading ? "Loading projects…" : "No projects found."}</p>
        </div>
      )}
    </div>
  );
}
