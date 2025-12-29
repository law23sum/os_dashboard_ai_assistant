import { DashboardSnapshot, WebPageLink } from "../api/dashboard";
import { StatsCard } from "./StatsCard";

interface Props {
  snapshot: DashboardSnapshot | null;
  loading: boolean;
  error?: string;
  onRefresh: () => void;
}

export function DashboardSummary({ snapshot, loading, error, onRefresh }: Props) {
  return (
    <div className="dashboard-view">
      <header className="workspace-header">
        <div>
          <h1>Mission Control</h1>
          <p>Unified task + persona metrics shared with the desktop console.</p>
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
              <StatsCard label="Total Tasks" value={snapshot.totals.tasks} />
              <StatsCard label="Active Tasks" value={snapshot.totals.active_tasks} />
              <StatsCard label="Projects" value={snapshot.totals.projects} />
              <StatsCard label="Due Today" value={snapshot.totals.due_today} />
            </div>
            <div className="status-text">
              Last updated: {new Date(snapshot.generated_at).toLocaleTimeString()}
            </div>
          </section>

          <div className="dashboard-grid">
            <ListCard title="Due Today" tasks={snapshot.today_tasks} empty="No tasks due today." />
            <ListCard title="Upcoming Deadlines" tasks={snapshot.upcoming_tasks} empty="No upcoming deadlines." />
            <ListCard title="Top Priority" tasks={snapshot.top_priority_tasks} empty="No high-priority tasks queued." />
          </div>

          <div className="dashboard-grid">
            <StatusCard title="Status Breakdown" data={snapshot.status_counts} />
            <StatusCard title="Persona Load" data={snapshot.persona_load} />
          </div>
          {snapshot.web_pages && snapshot.web_pages.length > 0 ? (
            <section className="dashboard-card">
              <header>
                <h3>Reference Web Pages</h3>
              </header>
              <LinkList pages={snapshot.web_pages} />
            </section>
          ) : null}
        </>
      ) : (
        <div className="workspace loading">
          <p>{loading ? "Loading dashboard…" : "No dashboard data yet."}</p>
        </div>
      )}
    </div>
  );
}

function ListCard({
  title,
  tasks,
  empty,
}: {
  title: string;
  tasks: DashboardSnapshot["today_tasks"];
  empty: string;
}) {
  return (
    <section className="dashboard-card">
      <header>
        <h3>{title}</h3>
      </header>
      {tasks.length === 0 ? (
        <p className="muted">{empty}</p>
      ) : (
        <ul className="task-list">
          {tasks.map((task) => (
            <li key={task.id}>
              <div>
                <strong>
                  #{task.id} [{task.priority}] {task.title}
                </strong>
                <div className="muted">
                  {task.project} • Owner: {task.owner}
                  {task.due_date ? ` • Due ${task.due_date}` : ""}
                </div>
              </div>
              <span className={`status-pill status-${task.status.toLowerCase()}`}>{task.status}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function StatusCard({ title, data }: { title: string; data: Record<string, number> }) {
  return (
    <section className="dashboard-card">
      <header>
        <h3>{title}</h3>
      </header>
      <ul className="status-list">
        {Object.entries(data).map(([key, value]) => (
          <li key={key}>
            <span>{key}</span>
            <strong>{value}</strong>
          </li>
        ))}
      </ul>
    </section>
  );
}

function LinkList({ pages }: { pages: WebPageLink[] }) {
  return (
    <ul className="link-list">
      {pages.map((page) => (
        <li key={page.url}>
          <div>
            <strong>{page.label}</strong>
            <span className="muted">{page.kind}</span>
          </div>
          <a href={page.url} target="_blank" rel="noreferrer">
            Open
          </a>
        </li>
      ))}
    </ul>
  );
}
