import { WriterDocument, WriterSnapshot } from "../api/writer";
import { StatsCard } from "./StatsCard";
import { DocumentLibrary } from "./DocumentLibrary";

export interface WriterFormState {
  type: string;
  genre: string;
  length: string;
  assistance: string;
  title: string;
  theme: string;
}

interface WriterWorkspaceProps {
  snapshot: WriterSnapshot | null;
  form: WriterFormState;
  onFormChange: (form: WriterFormState) => void;
  editorValue: string;
  onEditorChange: (value: string) => void;
  statusMessage: string;
  onCreateDocument: () => void;
  onGenerateNarrative: () => void;
  onSaveDocument: () => void;
  onExportDocument: () => void;
  onOpenDocument: (doc: WriterDocument) => void;
  isBusy?: boolean;
}

export function WriterWorkspace({
  snapshot,
  form,
  onFormChange,
  editorValue,
  onEditorChange,
  statusMessage,
  onCreateDocument,
  onGenerateNarrative,
  onSaveDocument,
  onExportDocument,
  onOpenDocument,
  isBusy,
}: WriterWorkspaceProps) {
  const wordCount = editorValue.trim() ? editorValue.trim().split(/\s+/).length : 0;

  const handleInputChange = (field: keyof WriterFormState, value: string) => {
    onFormChange({ ...form, [field]: value });
  };

  if (!snapshot) {
    return (
      <div className="workspace loading">
        <p>Loading writer workspace…</p>
      </div>
    );
  }

  const { stats, suggestions, canon_entries, pipeline_entries, progress } = snapshot;

  return (
    <div className="workspace">
      <header className="workspace-header">
        <div>
          <h1>Writer Workspace</h1>
          <p>Content creation, canon management, and narrative generation</p>
        </div>
        <div className="header-actions">
          <button onClick={onCreateDocument} disabled={isBusy}>
            ➕ New Document
          </button>
          <button className="accent" onClick={onGenerateNarrative} disabled={isBusy}>
            ✨ Generate Story
          </button>
        </div>
      </header>

      <section className="controls-card">
        <div className="control-row">
          <div className="control">
            <label>Document Type</label>
            <select value={form.type} onChange={(e) => handleInputChange("type", e.target.value)}>
              {["Article", "Story", "Report", "Script", "Blog"].map((type) => (
                <option key={type}>{type}</option>
              ))}
            </select>
          </div>
          <div className="control">
            <label>Genre / Style</label>
            <select value={form.genre} onChange={(e) => handleInputChange("genre", e.target.value)}>
              {["Professional", "Creative", "Technical", "Academic", "Casual"].map((genre) => (
                <option key={genre}>{genre}</option>
              ))}
            </select>
          </div>
          <div className="control">
            <label>Target Length</label>
            <select value={form.length} onChange={(e) => handleInputChange("length", e.target.value)}>
              {["Short (500-1000 words)", "Medium (1000-2500 words)", "Long (2500+ words)"].map((length) => (
                <option key={length}>{length}</option>
              ))}
            </select>
          </div>
          <div className="control">
            <label>AI Assistance</label>
            <select value={form.assistance} onChange={(e) => handleInputChange("assistance", e.target.value)}>
              {["Minimal", "Moderate", "Extensive"].map((option) => (
                <option key={option}>{option}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="control-row">
          <div className="control">
            <label>Title</label>
            <input value={form.title} onChange={(e) => handleInputChange("title", e.target.value)} placeholder="Enter document title…" />
          </div>
          <div className="control">
            <label>Theme / Topic</label>
            <input value={form.theme} onChange={(e) => handleInputChange("theme", e.target.value)} placeholder="Main theme…" />
          </div>
        </div>
        <div className="status-text">{statusMessage}</div>
      </section>

      <div className="workspace-grid">
        <section className="editor-card">
          <header>
            <h3>Document Editor</h3>
            <div className="editor-actions">
              <button onClick={onSaveDocument} disabled={isBusy}>
                💾 Save
              </button>
              <button onClick={onExportDocument}>⬇️ Export</button>
            </div>
          </header>
          <textarea
            value={editorValue}
            onChange={(e) => onEditorChange(e.target.value)}
            placeholder="Start writing your masterpiece…"
          />
          <div className="word-count">{wordCount.toLocaleString()} words</div>
        </section>

        <aside className="sidebar">
          <div className="quote-card">
            <p>“The first draft of anything is shit.”</p>
            <span>— Ernest Hemingway</span>
          </div>
          <div className="stats-grid">
            <StatsCard label="Total Words" value={stats.total_words.toLocaleString()} />
            <StatsCard label="Documents" value={stats.documents} />
            <StatsCard label="Words / Day" value={stats.avg_words_per_day} />
            <StatsCard label="Day Streak" value={stats.writing_streak} />
          </div>
          <div className="suggestion-card">
            <h4>AI Suggestions</h4>
            <div className="suggestions">
              {suggestions.map((suggestion) => (
                <div key={suggestion.title} className="suggestion">
                  <strong>{suggestion.title}</strong>
                  <p>{suggestion.body}</p>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </div>

      <div className="library-row">
        <section className="library-card">
          <header>
            <h3>Document Library</h3>
          </header>
          <DocumentLibrary documents={snapshot.documents} onOpen={onOpenDocument} />
        </section>
        <section className="progress-card">
          <header>
            <h3>Writing Progress</h3>
          </header>
          <ProgressChart days={progress.days} series={progress.series} goal={progress.goal} />
        </section>
      </div>

      <div className="canon-row">
          <section className="canon-card">
            <header>
              <h3>Canon Database</h3>
            </header>
            {canon_entries.map((entry) => (
              <div key={entry.title} className="canon-entry">
                <div>
                  <strong>{entry.title}</strong> · {entry.category}
                </div>
                <p>{entry.description}</p>
                <small>{entry.meta}</small>
              </div>
            ))}
          </section>
          <section className="pipeline-card">
            <header>
              <h3>Publishing Pipeline</h3>
            </header>
            {pipeline_entries.map((entry) => (
              <div key={entry.title} className="pipeline-entry">
                <div className="pipeline-header">
                  <strong>{entry.title}</strong>
                  <span className={`status-pill status-${entry.status.toLowerCase().replace(" ", "-")}`}>
                    {entry.status}
                  </span>
                </div>
                <p>{entry.summary}</p>
                <small>{entry.meta}</small>
              </div>
            ))}
          </section>
      </div>
    </div>
  );
}

function ProgressChart({ days, series, goal }: { days: string[]; series: number[]; goal: number }) {
  if (!series.length) return null;
  const maxVal = Math.max(goal, ...series);
  const points = series
    .map((value, idx) => {
      const x = (idx / Math.max(series.length - 1, 1)) * 100;
      const y = 100 - (value / maxVal) * 100;
      return `${idx === 0 ? "M" : "L"}${x},${y}`;
    })
    .join(" ");

  const goalY = 100 - (goal / maxVal) * 100;

  return (
    <div className="progress-chart">
      <svg viewBox="0 0 100 100" preserveAspectRatio="none">
        <path d={`M0,${goalY} L100,${goalY}`} className="goal-line" />
        <path d={points} className="progress-line" fill="none" />
        {series.map((value, idx) => {
          const x = (idx / Math.max(series.length - 1, 1)) * 100;
          const y = 100 - (value / maxVal) * 100;
          return <circle key={idx} cx={x} cy={y} r={1.5} className="progress-dot" />;
        })}
      </svg>
      <div className="chart-days">
        {days.map((day) => (
          <span key={day}>{day}</span>
        ))}
      </div>
    </div>
  );
}
