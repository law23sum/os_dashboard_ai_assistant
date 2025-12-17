import { FormEvent, useEffect, useRef, useState } from "react";
import { WriterDocument, WriterSnapshot, CanonEntryInput, PipelineEntryInput } from "../api/writer";
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
  onAddCanonEntry: (entry: CanonEntryInput) => Promise<void>;
  onQueuePipelineEntry: (entry: PipelineEntryInput) => Promise<void>;
  isBusy?: boolean;
  activeDocumentTitle?: string;
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
  onAddCanonEntry,
  onQueuePipelineEntry,
  isBusy,
  activeDocumentTitle,
}: WriterWorkspaceProps) {
  const wordCount = editorValue.trim() ? editorValue.trim().split(/\s+/).length : 0;
  const editorRef = useRef<HTMLTextAreaElement | null>(null);
  const [canonDraft, setCanonDraft] = useState<CanonEntryInput>({
    category: "Character",
    title: "",
    description: "",
    meta: ""
  });
  const [pipelineDraft, setPipelineDraft] = useState<PipelineEntryInput>({
    title: form.title,
    summary: "",
    target: "",
    status: "Draft"
  });
  const [pipelineTitleDirty, setPipelineTitleDirty] = useState(false);
  const [assistStatus, setAssistStatus] = useState("Select text to run Aria/AIC rewrites on a passage.");
  type AssistAction = "rewrite" | "expand" | "summarize";
  const assistActions: { id: AssistAction; label: string; helper: string }[] = [
    { id: "rewrite", label: "Rewrite", helper: "Tightens phrasing" },
    { id: "expand", label: "Expand", helper: "Adds contextual beats" },
    { id: "summarize", label: "Summarize", helper: "Generates scene notes" }
  ];

  const handleInputChange = (field: keyof WriterFormState, value: string) => {
    onFormChange({ ...form, [field]: value });
  };

  useEffect(() => {
    if (pipelineTitleDirty) {
      return;
    }
    const fallbackTitle = activeDocumentTitle || form.title || "";
    setPipelineDraft((draft) => ({ ...draft, title: fallbackTitle }));
  }, [activeDocumentTitle, form.title, pipelineTitleDirty]);

  const handleCanonSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!canonDraft.title.trim() || !canonDraft.description.trim()) {
      return;
    }
    await onAddCanonEntry({
      category: canonDraft.category,
      title: canonDraft.title.trim(),
      description: canonDraft.description.trim(),
      meta: canonDraft.meta?.trim() ? canonDraft.meta.trim() : undefined
    });
    setCanonDraft((prev) => ({ ...prev, title: "", description: "", meta: "" }));
  };

  const handlePipelineSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!pipelineDraft.title.trim() || !pipelineDraft.summary.trim() || !pipelineDraft.target.trim()) {
      return;
    }
    await onQueuePipelineEntry({
      title: pipelineDraft.title.trim(),
      summary: pipelineDraft.summary.trim(),
      target: pipelineDraft.target.trim(),
      status: pipelineDraft.status
    });
    setPipelineDraft({ title: "", summary: "", target: "", status: "Draft" });
    setPipelineTitleDirty(false);
  };

  const applyAssistAction = (mode: AssistAction) => {
    const textarea = editorRef.current;
    if (!textarea) return;
    const selectionStart = textarea.selectionStart ?? 0;
    const selectionEnd = textarea.selectionEnd ?? selectionStart;
    const hasSelection = selectionEnd > selectionStart;
    const selectedText = hasSelection ? editorValue.slice(selectionStart, selectionEnd) : editorValue;
    if (!selectedText.trim()) {
      setAssistStatus("Add a few words before invoking the assistant.");
      return;
    }

    const rewritePassage = (text: string) => {
      return text
        .replace(/\bjust\b/gi, "")
        .replace(/\breally\b/gi, "")
        .replace(/\bvery\b/gi, "exceptionally")
        .replace(/\s+/g, " ")
        .trim();
    };

    const expandPassage = (text: string) => {
      const theme = form.theme || "core theme";
      return `${text.trim()}\n\nFurther context (${form.genre}): highlight how this beat reinforces ${theme} and foreshadow canon hooks.`;
    };

    const summarizePassage = (text: string) => {
      const sentences = text.replace(/\n+/g, " ").split(/(?<=[.!?])\s+/).filter(Boolean);
      const summary = sentences.slice(0, 2).join(" ");
      return `Summary: ${summary || text.slice(0, 120)}${summary ? "" : "…"}`;
    };

    let replacement = selectedText;
    if (mode === "rewrite") {
      replacement = rewritePassage(selectedText);
    } else if (mode === "expand") {
      replacement = expandPassage(selectedText);
    } else {
      replacement = summarizePassage(selectedText);
    }

    const before = editorValue.slice(0, selectionStart);
    const after = editorValue.slice(selectionEnd);
    const nextValue = `${before}${replacement}${after}`;
    onEditorChange(nextValue);
    requestAnimationFrame(() => {
      textarea.focus();
      const nextStart = selectionStart;
      const nextEnd = selectionStart + replacement.length;
      textarea.setSelectionRange(nextStart, nextEnd);
    });

    const affectedWords = replacement.trim().split(/\s+/).filter(Boolean).length;
    const label = assistActions.find((action) => action.id === mode)?.label ?? "Assistant";
    setAssistStatus(`${label} applied to ${affectedWords.toLocaleString()} words.`);
  };

  if (!snapshot) {
    return (
      <div className="workspace loading">
        <p>Loading writer workspace…</p>
      </div>
    );
  }

  const {
    stats,
    suggestions,
    canon_entries,
    pipeline_entries,
    progress,
    narrative_guidance,
    qa_findings,
    qa_metrics,
    collaboration,
    publishing_queue,
    outline,
    notes,
  } = snapshot;
  const qaMetrics = qa_metrics ?? { continuity: 0, canon: 0, voice: 0, pacing: 0 };
  const narrativeGuidance = narrative_guidance ?? [];
  const qaFindings = qa_findings ?? [];
  const collaborationState = collaboration ?? { participants: [], review_cycles: [] };
  const publishingQueue = publishing_queue ?? [];
  const outlineEntries = outline ?? [];
  const researchNotes = notes ?? [];
  const canonGraph = canon_entries.reduce<Record<string, number>>((acc, entry) => {
    acc[entry.category] = (acc[entry.category] || 0) + 1;
    return acc;
  }, {});
  const canonGraphEntries = Object.entries(canonGraph);

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

      <div className="pane-row">
        <section className="pane-card">
          <header>
            <div>
              <p className="spec-label">Spec §7.5.1</p>
              <h3>Story Outline</h3>
            </div>
          </header>
          {outlineEntries.map((section) => (
            <div key={section.id} className="outline-entry">
              <div className="outline-header">
                <div>
                  <strong>{section.stage}</strong>
                  <p>{section.title}</p>
                </div>
                <div className="outline-meta">
                  <span className={`status-pill status-${section.status.toLowerCase()}`}>{section.status}</span>
                  <small>{section.word_target.toLocaleString()} words</small>
                </div>
              </div>
              <p>{section.focus}</p>
            </div>
          ))}
        </section>
        <section className="pane-card">
          <header>
            <div>
              <p className="spec-label">Spec §7.5.1 · §7.5.2</p>
              <h3>Research Notes & Evidence</h3>
            </div>
          </header>
          {researchNotes.map((note) => (
            <div key={note.id} className="note-entry">
              <div className="note-header">
                <strong>{note.title}</strong>
                <span className="reference-pill">{note.linked_doc}</span>
              </div>
              <p>{note.detail}</p>
            </div>
          ))}
        </section>
      </div>

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
          <div className="assist-toolbar">
            <div>
              <p className="assist-title">Contextual AI Assistance</p>
              <small>{assistStatus}</small>
            </div>
            <div className="assist-actions">
              {assistActions.map((action) => (
                <button key={action.id} type="button" onClick={() => applyAssistAction(action.id)}>
                  {action.label}
                  <span>{action.helper}</span>
                </button>
              ))}
            </div>
          </div>
          <textarea
            ref={editorRef}
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
            {!!canonGraphEntries.length && (
              <div className="canon-graph">
                {canonGraphEntries.map(([category, count], idx) => (
                  <div key={category} className="canon-node">
                    <strong>{category}</strong>
                    <span>{count} entries</span>
                    {idx < canonGraphEntries.length - 1 && <span className="canon-link" />}
                  </div>
                ))}
              </div>
            )}
            <form className="canon-form" onSubmit={handleCanonSubmit}>
              <div className="canon-form-grid">
                <div className="control">
                  <label>Category</label>
                  <select
                    value={canonDraft.category}
                    onChange={(e) => setCanonDraft({ ...canonDraft, category: e.target.value })}
                  >
                    {["Character", "Location", "Event", "Rule", "Lore"].map((category) => (
                      <option key={category}>{category}</option>
                    ))}
                  </select>
                </div>
                <div className="control">
                  <label>Title</label>
                  <input
                    value={canonDraft.title}
                    onChange={(e) => setCanonDraft({ ...canonDraft, title: e.target.value })}
                    placeholder="Entry title..."
                  />
                </div>
              </div>
              <div className="control">
                <label>Description</label>
                <textarea
                  value={canonDraft.description}
                  onChange={(e) => setCanonDraft({ ...canonDraft, description: e.target.value })}
                  placeholder="Key canon details..."
                />
              </div>
              <div className="control">
                <label>Metadata (optional)</label>
                <input
                  value={canonDraft.meta ?? ""}
                  onChange={(e) => setCanonDraft({ ...canonDraft, meta: e.target.value })}
                  placeholder="Timeline, owner, source..."
                />
              </div>
              <button
                type="submit"
                className="primary-button"
                disabled={isBusy || !canonDraft.title.trim() || !canonDraft.description.trim()}
              >
                ➕ Add Canon Entry
              </button>
            </form>
          </section>
        <section className="pipeline-card">
          <header>
            <h3>Publishing Pipeline</h3>
          </header>
          {pipeline_entries.map((entry) => (
            <div key={entry.title} className="pipeline-entry">
              <div className="pipeline-header">
                <strong>{entry.title}</strong>
                <span className={`status-pill status-${entry.status.toLowerCase().replace(" ", "-")}`}>{entry.status}</span>
              </div>
              <p>{entry.summary}</p>
              <small>{entry.meta}</small>
            </div>
          ))}
          <form className="pipeline-form" onSubmit={handlePipelineSubmit}>
            <div className="control">
              <label>Title</label>
              <input
                value={pipelineDraft.title}
                onChange={(e) => {
                  setPipelineDraft({ ...pipelineDraft, title: e.target.value });
                  setPipelineTitleDirty(true);
                }}
                placeholder="Document title..."
              />
            </div>
            <div className="control">
              <label>Summary / Intent</label>
              <textarea
                value={pipelineDraft.summary}
                onChange={(e) => setPipelineDraft({ ...pipelineDraft, summary: e.target.value })}
                placeholder="What are we shipping?"
              />
            </div>
            <div className="pipeline-form-grid">
              <div className="control">
                <label>Target Channel</label>
                <input
                  value={pipelineDraft.target}
                  onChange={(e) => setPipelineDraft({ ...pipelineDraft, target: e.target.value })}
                  placeholder="Magazine, portal, platform..."
                />
              </div>
              <div className="control">
                <label>Status</label>
                <select
                  value={pipelineDraft.status}
                  onChange={(e) => setPipelineDraft({ ...pipelineDraft, status: e.target.value })}
                >
                  {["Draft", "Review", "Under Review", "Published"].map((status) => (
                    <option key={status} value={status}>
                      {status}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <button
              type="submit"
              className="primary-button"
              disabled={
                isBusy ||
                !pipelineDraft.title.trim() ||
                !pipelineDraft.summary.trim() ||
                !pipelineDraft.target.trim()
              }
            >
              ⬆️ Publish / Queue
            </button>
          </form>
        </section>
      </div>

      <div className="narrative-row">
        <section className="narrative-card">
          <header>
            <h3>Narrative Guidance Engine</h3>
          </header>
          {narrativeGuidance.length === 0 ? (
            <p className="muted">Narrative state is steady. No open actions right now.</p>
          ) : (
            narrativeGuidance.map((guide) => (
              <div key={guide.title} className="narrative-entry">
                <div className="narrative-header">
                  <strong>{guide.title}</strong>
                  <span className="status-pill">{guide.status}</span>
                </div>
                <p>{guide.detail}</p>
                <small>Next: {guide.next_action}</small>
              </div>
            ))
          )}
        </section>
        <section className="qa-card">
          <header>
            <h3>Story QA & Continuity</h3>
          </header>
          <div className="qa-metrics">
            {Object.entries(qaMetrics).map(([label, value]) => (
              <div key={label} className="qa-metric">
                <div className="qa-metric-label">{label}</div>
                <div className="qa-metric-bar">
                  <span style={{ width: `${value}%` }} />
                </div>
                <div className="qa-metric-value">{value}%</div>
              </div>
            ))}
          </div>
          <div className="qa-issues">
            {qaFindings.length === 0 ? (
              <p className="muted">No QA issues. Continuity and canon checks are green.</p>
            ) : (
              qaFindings.map((issue) => (
                <div key={issue.id} className={`qa-issue qa-${issue.severity.toLowerCase()}`}>
                  <strong>
                    {issue.id} · {issue.area}
                  </strong>
                  <p>{issue.summary}</p>
                  <small>Recommendation: {issue.recommendation}</small>
                </div>
              ))
            )}
          </div>
        </section>
      </div>

      <div className="collaboration-row">
        <section className="collaboration-card">
          <header>
            <h3>Collaboration & Review</h3>
          </header>
          <div className="participants">
            {collaborationState.participants && collaborationState.participants.length > 0 ? (
              collaborationState.participants.map((participant) => (
                <div key={participant.name} className="participant">
                  <div>
                    <strong>{participant.name}</strong>
                    <div className="muted">{participant.role}</div>
                  </div>
                  <div>
                    <span className="role-badge">{participant.focus}</span>
                    <div className="muted">{participant.status}</div>
                  </div>
                </div>
              ))
            ) : (
              <p className="muted">No collaborators assigned.</p>
            )}
          </div>
          <div className="review-cycles">
            {collaborationState.review_cycles && collaborationState.review_cycles.length > 0 ? (
              collaborationState.review_cycles.map((cycle) => (
                <div key={cycle.name} className="review-cycle">
                  <div className="cycle-header">
                    <strong>{cycle.name}</strong>
                    <span className="status-pill">{cycle.status}</span>
                  </div>
                  <p>Owner: {cycle.owner}</p>
                  <p>Due: {cycle.due}</p>
                  <ul>
                    {cycle.checklist.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              ))
            ) : (
              <p className="muted">No review cycles scheduled.</p>
            )}
          </div>
        </section>
        <section className="publishing-card">
          <header>
            <h3>Publishing & Production Flows</h3>
          </header>
          {publishingQueue.length === 0 ? (
            <p className="muted">No publishing runs are queued.</p>
          ) : (
            publishingQueue.map((run) => (
              <div key={run.target} className="publishing-entry">
                <div className="publishing-header">
                  <div>
                    <strong>{run.channel}</strong> · {run.target}
                  </div>
                  <span className="status-pill">{run.status}</span>
                </div>
                <p>
                  Stage: {run.stage} · Last run: {run.last_run}
                </p>
                <small>{run.notes}</small>
              </div>
            ))
          )}
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
