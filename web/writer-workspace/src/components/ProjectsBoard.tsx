import { ProjectSnapshot } from "../api/projects";

interface Props {
  snapshot: ProjectSnapshot | null;
  loading: boolean;
  error?: string;
  onRefresh: () => void;
}

export function ProjectsBoard({ snapshot, loading, error, onRefresh }: Props) {
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
                  {snapshot.projects.map((project) => (
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
