import { useEffect, useState } from "react";
import {
  WriterDocument,
  WriterSnapshot,
  CanonEntryInput,
  PipelineEntryInput,
  createDocument,
  fetchSnapshot,
  generateNarrative,
  saveDocument,
  addCanonEntry,
  queuePipelineEntry
} from "./api/writer";
import { fetchDashboardSummary, DashboardSnapshot } from "./api/dashboard";
import { fetchTasks, TaskRecord } from "./api/tasks";
import { fetchProjectSnapshot, ProjectSnapshot } from "./api/projects";
import { WriterWorkspace, WriterFormState } from "./components/WriterWorkspace";
import { DashboardSummary } from "./components/DashboardSummary";
import { TasksBoard } from "./components/TasksBoard";
import { ProjectsBoard } from "./components/ProjectsBoard";

const defaultForm: WriterFormState = {
  type: "Article",
  genre: "Professional",
  length: "Short (500-1000 words)",
  assistance: "Minimal",
  title: "",
  theme: ""
};

type ViewMode = "writer" | "dashboard" | "tasks" | "projects";

function App() {
  const [snapshot, setSnapshot] = useState<WriterSnapshot | null>(null);
  const [form, setForm] = useState<WriterFormState>(defaultForm);
  const [editorValue, setEditorValue] = useState("");
  const [activeDocument, setActiveDocument] = useState<WriterDocument | null>(null);
  const [statusMessage, setStatusMessage] = useState("Ready to create your next masterpiece.");
  const [busy, setBusy] = useState(false);
  const [view, setView] = useState<ViewMode>("writer");
  const [dashboardSnapshot, setDashboardSnapshot] = useState<DashboardSnapshot | null>(null);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [dashboardError, setDashboardError] = useState<string | undefined>(undefined);
  const [tasks, setTasks] = useState<TaskRecord[]>([]);
  const [tasksLoading, setTasksLoading] = useState(false);
  const [tasksError, setTasksError] = useState<string | undefined>(undefined);
  const [projectSnapshot, setProjectSnapshot] = useState<ProjectSnapshot | null>(null);
  const [projectLoading, setProjectLoading] = useState(false);
  const [projectError, setProjectError] = useState<string | undefined>(undefined);

  useEffect(() => {
    loadSnapshot();
  }, []);

  useEffect(() => {
    if (view === "dashboard" && !dashboardSnapshot && !dashboardLoading) {
      refreshDashboard();
    }
  }, [view, dashboardSnapshot, dashboardLoading]);

  useEffect(() => {
    if (view === "tasks" && tasks.length === 0 && !tasksLoading) {
      refreshTasks();
    }
  }, [view, tasks, tasksLoading]);

  useEffect(() => {
    if (view === "projects" && !projectSnapshot && !projectLoading) {
      refreshProjects();
    }
  }, [view, projectSnapshot, projectLoading]);

  async function loadSnapshot() {
    try {
      const data = await fetchSnapshot();
      setSnapshot(data);
    } catch (error) {
      console.error(error);
      setStatusMessage("Failed to load writer workspace data.");
    }
  }

  async function refreshDashboard() {
    setDashboardLoading(true);
    try {
      const data = await fetchDashboardSummary();
      setDashboardSnapshot(data);
      setDashboardError(undefined);
    } catch (error) {
      console.error(error);
      setDashboardError("Failed to load dashboard summary.");
    } finally {
      setDashboardLoading(false);
    }
  }

  async function refreshTasks() {
    setTasksLoading(true);
    try {
      const data = await fetchTasks();
      setTasks(data);
      setTasksError(undefined);
    } catch (error) {
      console.error(error);
      setTasksError("Failed to load tasks.");
    } finally {
      setTasksLoading(false);
    }
  }

  async function refreshProjects() {
    setProjectLoading(true);
    try {
      const data = await fetchProjectSnapshot();
      setProjectSnapshot(data);
      setProjectError(undefined);
    } catch (error) {
      console.error(error);
      setProjectError("Failed to load projects.");
    } finally {
      setProjectLoading(false);
    }
  }

  async function handleCreateDocument() {
    if (!form.title.trim()) {
      setStatusMessage("Add a title so the library stays organized.");
      return;
    }
    setBusy(true);
    try {
      const { document, workspace } = await createDocument(form.title || "Untitled Document", form.type, form.theme);
      setSnapshot(workspace);
      setActiveDocument(document);
      setEditorValue("");
      setStatusMessage(`Document "${document.title}" created.`);
    } catch (error) {
      console.error(error);
      setStatusMessage("Failed to create document.");
    } finally {
      setBusy(false);
    }
  }

  async function handleGenerateNarrative() {
    setBusy(true);
    try {
      const { content } = await generateNarrative({
        title: form.title || "Untitled Narrative",
        type: form.type,
        genre: form.genre,
        theme: form.theme
      });
      setEditorValue(content);
      setStatusMessage("Narrative template generated.");
    } catch (error) {
      console.error(error);
      setStatusMessage("Failed to generate narrative.");
    } finally {
      setBusy(false);
    }
  }

  async function handleSaveDocument() {
    if (!editorValue.trim()) {
      setStatusMessage("Write something before saving.");
      return;
    }
    setBusy(true);
    try {
      let documentId = activeDocument?.id;
      if (!documentId) {
        const { document, workspace } = await createDocument(form.title || "Untitled Document", form.type, form.theme);
        documentId = document.id;
        setSnapshot(workspace);
        setActiveDocument(document);
      }
      if (!documentId) return;
      const { document, workspace } = await saveDocument(documentId, editorValue);
      setSnapshot(workspace);
      setActiveDocument(document);
      setStatusMessage(`Saved ${document.words.toLocaleString()} words.`);
    } catch (error) {
      console.error(error);
      setStatusMessage("Failed to save document.");
    } finally {
      setBusy(false);
    }
  }

  async function handleAddCanonEntry(entry: CanonEntryInput) {
    setBusy(true);
    try {
      const { workspace } = await addCanonEntry(entry);
      setSnapshot(workspace);
      setStatusMessage(`Canon entry "${entry.title}" filed under ${entry.category}.`);
    } catch (error) {
      console.error(error);
      setStatusMessage("Failed to add canon entry.");
    } finally {
      setBusy(false);
    }
  }

  async function handleQueuePipelineEntry(entry: PipelineEntryInput) {
    setBusy(true);
    try {
      const { workspace } = await queuePipelineEntry(entry);
      setSnapshot(workspace);
      setStatusMessage(`Queued "${entry.title}" for ${entry.target}.`);
    } catch (error) {
      console.error(error);
      setStatusMessage("Failed to queue publishing workflow.");
    } finally {
      setBusy(false);
    }
  }

  function handleExportDocument() {
    const blob = new Blob([editorValue], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    const normalizedTitle = (form.title || "document").replace(/[^a-z0-9_-]/gi, "_").toLowerCase();
    anchor.download = `${normalizedTitle}.txt`;
    anchor.click();
    URL.revokeObjectURL(url);
    setStatusMessage("Document exported.");
  }

  function handleOpenDocument(doc: WriterDocument) {
    setActiveDocument(doc);
    setEditorValue(doc.content || "");
    setForm({ ...form, title: doc.title, type: doc.type, theme: doc.theme || "" });
    setStatusMessage(`Loaded "${doc.title}".`);
  }

  return (
    <div className="app-container">
      <nav className="app-nav">
        <button className={view === "dashboard" ? "active" : ""} onClick={() => setView("dashboard")}>
          Dashboard
        </button>
        <button className={view === "tasks" ? "active" : ""} onClick={() => setView("tasks")}>
          Tasks
        </button>
        <button className={view === "projects" ? "active" : ""} onClick={() => setView("projects")}>
          Projects
        </button>
        <button className={view === "writer" ? "active" : ""} onClick={() => setView("writer")}>
          Writer Workspace
        </button>
      </nav>
      {view === "dashboard" ? (
        <DashboardSummary
          snapshot={dashboardSnapshot}
          loading={dashboardLoading}
          error={dashboardError}
          onRefresh={refreshDashboard}
        />
      ) : view === "tasks" ? (
        <TasksBoard tasks={tasks} loading={tasksLoading} error={tasksError} onRefresh={refreshTasks} />
      ) : view === "projects" ? (
        <ProjectsBoard snapshot={projectSnapshot} loading={projectLoading} error={projectError} onRefresh={refreshProjects} />
      ) : (
        <WriterWorkspace
          snapshot={snapshot}
          form={form}
          onFormChange={setForm}
          editorValue={editorValue}
          onEditorChange={setEditorValue}
          statusMessage={statusMessage}
          onCreateDocument={handleCreateDocument}
          onGenerateNarrative={handleGenerateNarrative}
          onSaveDocument={handleSaveDocument}
          onExportDocument={handleExportDocument}
          onOpenDocument={handleOpenDocument}
          onAddCanonEntry={handleAddCanonEntry}
          onQueuePipelineEntry={handleQueuePipelineEntry}
          isBusy={busy}
          activeDocumentTitle={activeDocument?.title || form.title}
        />
      )}
    </div>
  );
}

export default App;
