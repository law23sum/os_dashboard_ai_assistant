import React, { useEffect, useMemo, useState } from "https://esm.sh/react@18";
import { createRoot } from "https://esm.sh/react-dom@18/client";

// Mock data for the dashboard
const MOCK_SEARCH = [
  {
    score: 0.91,
    system: "pdf",
    resource_id: "reg-2025-12",
    node_type: "pdf",
    node_title: "New Vendor Privacy Addendum",
    text_snippet: "Sections on data retention, breach notification, and subcontractor controls...",
  },
  {
    score: 0.86,
    system: "notes",
    resource_id: "note-7",
    node_type: "note",
    node_title: "Governed AI OS idea fragments",
    text_snippet: "Daemon safety scopes, CIR minimal schema, Git-backed approvals...",
  },
];

const MOCK_DAEMONS = [
  {
    name: "regulation_ingest",
    description: "Ingest new regulations, summarize, map to internal policies, and draft updates.",
    enabled: true,
    scopes: ["/Regulations", "Policy/Privacy"],
    triggers: ["pdf.added.regulations"],
    risk_level: "medium",
    last_run: "2024-01-15T09:00:00Z",
    success_rate: 0.93,
  },
  {
    name: "deck_refresh",
    description: "Keep executive decks aligned with underlying Excel models and latest decisions.",
    enabled: false,
    scopes: ["/Board", "/Exec"],
    triggers: ["excel.model.updated"],
    risk_level: "low",
    last_run: "2024-01-14T15:30:00Z",
    success_rate: 0.88,
  },
];

const MOCK_OPS = [
  {
    id: "op-001",
    actor: "user:admin",
    intent: "search_documents",
    triggered_by: "manual",
    started_at: "2024-01-15T10:30:00Z",
    finished_at: "2024-01-15T10:30:05Z",
    touched: [{ system: "filesystem", resource_id: "documents", action: "read" }],
    diffs: [],
    metadata: { query: "test search" },
  },
];

// Utility helpers
const systemMeta = {
  word: { label: "Word", icon: "📄" },
  excel: { label: "Excel", icon: "📊" },
  pdf: { label: "PDF", icon: "📕" },
  notes: { label: "Notes", icon: "📝" },
  git: { label: "Git", icon: "🔒" },
  filesystem: { label: "Filesystem", icon: "💾" },
  unknown: { label: "Unknown", icon: "❓" },
};

const MOCK_SYSTEM_STATS = {
  cpu_percent: 27,
  memory: { total: 16_000_000_000, used: 6_100_000_000, available: 9_900_000_000 },
  disk: { total: 500_000_000_000, used: 320_000_000_000, free: 180_000_000_000 },
};

function getSystemIcon(system) {
  return systemMeta[system]?.icon || systemMeta.unknown.icon;
}

function getSystemLabel(system) {
  return systemMeta[system]?.label || "Unknown";
}

function formatWhen(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

function formatBytes(bytes) {
  if (!Number.isFinite(bytes)) return "—";
  const thresholds = ["B", "KB", "MB", "GB", "TB"];
  let value = bytes;
  let unit = 0;
  while (value >= 1024 && unit < thresholds.length - 1) {
    value /= 1024;
    unit += 1;
  }
  return `${value.toFixed(1)} ${thresholds[unit]}`;
}

// API client wrappers fall back to mock data
const API = {
  async search(query) {
    try {
      const res = await fetch(`/search?q=${encodeURIComponent(query)}`);
      if (!res.ok) throw new Error("search_failed");
      return await res.json();
    } catch {
      if (!query) return [];
      return MOCK_SEARCH.filter((record) =>
        `${record.node_title} ${record.text_snippet}`.toLowerCase().includes((query || "").toLowerCase())
      );
    }
  },
  async listDaemons() {
    try {
      const res = await fetch("/daemons");
      if (!res.ok) throw new Error("daemons_failed");
      return await res.json();
    } catch {
      return MOCK_DAEMONS;
    }
  },
  async setDaemonEnabled(name, enabled) {
    try {
      const res = await fetch(`/daemons/${encodeURIComponent(name)}/${enabled ? "enable" : "disable"}`, {
        method: "POST",
      });
      return res.ok;
    } catch {
      return false;
    }
  },
  async runDaemon(name) {
    try {
      const res = await fetch(`/daemons/${encodeURIComponent(name)}/run`, { method: "POST" });
      return res.ok;
    } catch {
      return false;
    }
  },
  async listOperations() {
    try {
      const res = await fetch("/operations?limit=50");
      if (!res.ok) throw new Error("ops_failed");
      return await res.json();
    } catch {
      return MOCK_OPS;
    }
  },
  async getAudit(opId) {
    try {
      const res = await fetch(`/audit/${encodeURIComponent(opId)}`);
      if (!res.ok) throw new Error("audit_failed");
      return await res.json();
    } catch {
      return MOCK_OPS.find((o) => o.id === opId) || null;
    }
  },
  async getSystemStats() {
    try {
      const res = await fetch("/system");
      if (!res.ok) throw new Error("system_failed");
      return await res.json();
    } catch {
      return MOCK_SYSTEM_STATS;
    }
  },
  async askAI(prompt) {
    try {
      const res = await fetch("/ai/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      if (!res.ok) throw new Error("ai_failed");
      return await res.json();
    } catch (error) {
      return { response: error?.message || "AI unavailable" };
    }
  },
};

// Primitive UI components
function Badge({ children, variant = "secondary", className = "" }) {
  const base = "inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold tracking-wide";
  const tones = {
    default: "bg-white/15 text-white shadow-inner shadow-slate-900/40",
    secondary: "bg-slate-900/40 text-slate-100 border border-white/10",
    destructive: "bg-rose-500/20 text-rose-100 border border-rose-400/30",
    outline: "border border-white/20 text-white",
  };
  return <span className={`${base} ${tones[variant] || tones.secondary} ${className}`}>{children}</span>;
}

function Button({ children, variant = "default", size = "default", onClick, disabled, className = "" }) {
  const base =
    "inline-flex items-center justify-center rounded-xl font-semibold tracking-wide transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2";
  const variants = {
    default:
      "bg-gradient-to-r from-indigo-500 via-purple-500 to-sky-500 text-white shadow-lg shadow-indigo-900/40 hover:shadow-2xl hover:translate-y-[-1px] focus-visible:ring-indigo-400",
    secondary: "bg-white/10 text-white border border-white/10 hover:bg-white/20 focus-visible:ring-white/30",
    outline: "border border-white/20 text-white hover:bg-white/10 focus-visible:ring-white/30",
    ghost: "text-white/80 hover:bg-white/10 focus-visible:ring-white/20",
  };
  const sizes = {
    default: "h-11 px-6",
    sm: "h-9 px-4 text-sm",
    icon: "h-11 w-11",
  };
  return (
    <button
      className={`${base} ${variants[variant]} ${sizes[size]} ${disabled ? "opacity-40 cursor-not-allowed" : ""} ${className}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

function Card({ children, className = "" }) {
  return (
    <div className={`bg-white/5 border border-white/10 rounded-2xl shadow-2xl backdrop-blur-xl text-slate-100 ${className}`}>
      {children}
    </div>
  );
}

function CardHeader({ children, className = "" }) {
  return <div className={`p-6 pb-4 ${className}`}>{children}</div>;
}

function CardTitle({ children, className = "" }) {
  return <h3 className={`text-xl font-semibold text-white ${className}`}>{children}</h3>;
}

function CardDescription({ children, className = "" }) {
  return <p className={`text-sm text-slate-300 mt-1 ${className}`}>{children}</p>;
}

function CardContent({ children, className = "" }) {
  return <div className={`p-6 pt-0 ${className}`}>{children}</div>;
}

function Input({ value, onChange, placeholder, className = "" }) {
  return (
    <input
      type="text"
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className={`w-full px-4 py-3 text-sm bg-white/10 border border-white/20 rounded-xl text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent ${className}`}
    />
  );
}

const SummaryCard = ({ title, value, description, icon }) => (
  <Card className="p-5 border border-white/10 shadow-none">
    <div className="flex items-center justify-between text-sm text-slate-300">
      <span className="uppercase tracking-[0.35em] text-xs text-slate-400">{title}</span>
      <span className="text-lg">{icon}</span>
    </div>
    <p className="text-3xl font-semibold mt-4 text-white">{value}</p>
    <p className="text-sm text-slate-300 mt-2">{description}</p>
  </Card>
);

const NotificationBar = ({ notification }) => {
  if (!notification) return null;
  const tone = {
    success: "bg-emerald-500/15 border-emerald-400/40 text-emerald-100",
    warning: "bg-amber-500/15 border-amber-400/40 text-amber-100",
    error: "bg-rose-500/15 border-rose-400/40 text-rose-100",
    info: "bg-sky-500/15 border-sky-400/40 text-sky-100",
  };
  return (
    <div className={`rounded-xl border px-4 py-3 text-sm ${tone[notification.type] || tone.info}`}>
      {notification.message}
    </div>
  );
};

// Main dashboard component
export default function AIOSDashboard() {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [daemons, setDaemons] = useState([]);
  const [operations, setOperations] = useState([]);
  const [selectedOp, setSelectedOp] = useState(null);
  const [selectedOpDetail, setSelectedOpDetail] = useState(null);
  const [auditLoading, setAuditLoading] = useState(false);
  const [notification, setNotification] = useState(null);
  const [systemStats, setSystemStats] = useState(MOCK_SYSTEM_STATS);
  const [systemLoading, setSystemLoading] = useState(true);
  const [chatPrompt, setChatPrompt] = useState("");
  const [chatResponse, setChatResponse] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    loadDaemons();
    loadOperations();
    loadSystem();
    const interval = setInterval(loadSystem, 30_000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!notification) return undefined;
    const timer = setTimeout(() => setNotification(null), 4000);
    return () => clearTimeout(timer);
  }, [notification]);

  const summaryMetrics = useMemo(
    () => ({
      daemonCount: daemons.length,
      activeDaemons: daemons.filter((d) => d.enabled).length,
      recentOps: operations.length,
      searchHits: searchResults.length,
    }),
    [daemons, operations, searchResults]
  );

  const memoryUsage = useMemo(() => {
    const mem = systemStats?.memory || {};
    const used = mem.used || 0;
    const total = mem.total || 1;
    return { used, total, percent: Math.round((used / total) * 100) };
  }, [systemStats]);

  const diskUsage = useMemo(() => {
    const disk = systemStats?.disk || {};
    const used = disk.used || 0;
    const total = disk.total || 1;
    return { used, total, percent: Math.round((used / total) * 100) };
  }, [systemStats]);

  const loadDaemons = async () => {
    const data = await API.listDaemons();
    setDaemons(data);
  };

  const loadOperations = async () => {
    const data = await API.listOperations();
    setOperations(data);
  };

  const loadSystem = async () => {
    setSystemLoading(true);
    const stats = await API.getSystemStats();
    setSystemStats(stats);
    setSystemLoading(false);
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setNotification({ type: "warning", message: "Enter a query to search documents." });
      return;
    }
    setLoading(true);
    const results = await API.search(searchQuery);
    setSearchResults(results);
    setLoading(false);
    setNotification({ type: "info", message: `Found ${results.length || 0} matching documents.` });
  };

  const toggleDaemon = async (daemon) => {
    const success = await API.setDaemonEnabled(daemon.name, !daemon.enabled);
    if (success) {
      loadDaemons();
      setNotification({
        type: "success",
        message: `${daemon.name} ${daemon.enabled ? "disabled" : "enabled"}.`,
      });
    }
  };

  const runDaemon = async (daemon) => {
    const success = await API.runDaemon(daemon.name);
    if (success) {
      loadOperations();
      setNotification({ type: "success", message: `${daemon.name} run queued.` });
    }
  };

  const toggleAllDaemons = async (enable) => {
    await Promise.all(daemons.map((daemon) => API.setDaemonEnabled(daemon.name, enable)));
    loadDaemons();
    setNotification({
      type: "info",
      message: enable ? "All daemons enabled." : "All daemons disabled.",
    });
  };

  const handleSelectOperation = async (op) => {
    setSelectedOp(op);
    setAuditLoading(true);
    const detail = await API.getAudit(op.id);
    setSelectedOpDetail(detail);
    setAuditLoading(false);
  };

  const handleSendPrompt = async () => {
    if (!chatPrompt.trim()) {
      setNotification({ type: "warning", message: "Enter a prompt for the AI assistant." });
      return;
    }
    setChatLoading(true);
    const data = await API.askAI(chatPrompt.trim());
    setChatResponse(data?.response || "No response");
    setChatLoading(false);
  };

  return (
    <div className="min-h-screen bg-slate-50">
        {/* Spec references: 1.7.2 driver-aware dashboard, 5.2 OS driver telemetry, 0.5 persona co-pilot */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>System Health</CardTitle>
                <CardDescription>Realtime snapshot from the host OS.</CardDescription>
              </CardHeader>
              <CardContent>
                {systemLoading ? (
                  <p className="text-sm text-slate-400">Collecting metrics…</p>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <p className="text-xs uppercase tracking-[0.35em] text-slate-400">CPU</p>
                      <p className="text-3xl font-semibold text-white">{Math.round(systemStats.cpu_percent)}%</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.35em] text-slate-400">Memory</p>
                      <div className="flex items-center justify-between text-sm text-slate-300">
                        <span>{formatBytes(memoryUsage.used)} used</span>
                        <span>{formatBytes(memoryUsage.total)}</span>
                      </div>
                      <div className="h-2 mt-2 bg-white/10 rounded-full">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-sky-400 to-indigo-500"
                          style={{ width: `${Math.min(memoryUsage.percent, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.35em] text-slate-400">Disk</p>
                      <div className="flex items-center justify-between text-sm text-slate-300">
                        <span>{formatBytes(diskUsage.used)} used</span>
                        <span>{formatBytes(diskUsage.total)}</span>
                      </div>
                      <div className="h-2 mt-2 bg-white/10 rounded-full">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-purple-400 to-fuchsia-500"
                          style={{ width: `${Math.min(diskUsage.percent, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Quick AI Assistant</CardTitle>
                <CardDescription>Bridge prompts to OpenAI-compatible APIs.</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col gap-3">
                  <Input
                    value={chatPrompt}
                    onChange={(e) => setChatPrompt(e.target.value)}
                    placeholder="Ask about tasks, incidents, or plans"
                  />
                  <div className="flex gap-2">
                    <Button onClick={handleSendPrompt} disabled={chatLoading}>
                      {chatLoading ? "Sending…" : "Send"}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => {
                        setChatPrompt("");
                        setChatResponse("");
                      }}
                    >
                      Clear
                    </Button>
                  </div>
                  {chatResponse && (
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm text-gray-700">
                      {chatResponse}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Unified Search</CardTitle>
              <CardDescription>Surface records from Notes, PDFs, Git, and more.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-3 lg:flex-row">
                <Input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Try ‘privacy addendum’"
                  className="flex-1"
                />
                <Button onClick={handleSearch} disabled={loading}>
                  {loading ? "Searching..." : "Search"}
                </Button>
              </div>
              <div className="mt-6">
                {loading ? (
                  <div className="text-center py-8 text-gray-500">Gathering documents…</div>
                ) : searchResults.length === 0 ? (
                  <div className="text-center py-8 text-gray-400">
                    Start with a query to see semantic matches across systems.
                  </div>
                ) : (
                  <div className="space-y-3">
                    {searchResults.map((result, idx) => (
                      <div key={idx} className="border rounded-lg p-4 hover:bg-gray-50 transition">
                        <div className="flex items-center gap-2 mb-2">
                          <span>{getSystemIcon(result.system)}</span>
                          <span className="font-semibold">{result.node_title}</span>
                          <Badge variant="outline">{getSystemLabel(result.system)}</Badge>
                        </div>
                        <p className="text-sm text-gray-600">{result.text_snippet}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Daemon Control</CardTitle>
              <CardDescription>Adaptive automation per scope.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2 mb-4">
                <Button size="sm" variant="outline" onClick={loadDaemons}>Refresh</Button>
                <Button size="sm" variant="outline" onClick={() => toggleAllDaemons(false)}>
                  Disable All
                </Button>
              </div>
              <div className="space-y-4 max-h-[420px] overflow-y-auto pr-1">
                {daemons.map((daemon) => (
                  <div key={daemon.name} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-1">
                      <div>
                        <h3 className="font-semibold text-gray-900">{daemon.name}</h3>
                        <p className="text-xs text-gray-500">{daemon.scopes?.join(", ")}</p>
                      </div>
                      <Badge variant={daemon.enabled ? "default" : "secondary"}>
                        {daemon.enabled ? "Enabled" : "Disabled"}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{daemon.description}</p>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant={daemon.enabled ? "outline" : "default"}
                        onClick={() => toggleDaemon(daemon)}
                      >
                        {daemon.enabled ? "Disable" : "Enable"}
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => runDaemon(daemon)}>
                        Run Now
                      </Button>
                    </div>
                  </div>
                ))}
                {daemons.length === 0 && <p className="text-sm text-gray-500">No daemons registered yet.</p>}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Activity Timeline</CardTitle>
                  <CardDescription>Click an operation to see audit detail.</CardDescription>
                </div>
                <Button size="sm" variant="outline" onClick={loadOperations}>Refresh</Button>
              </div>
            </CardHeader>
            <CardContent>
              {operations.length === 0 ? (
                <p className="text-sm text-gray-500">No operations recorded yet.</p>
              ) : (
                <div className="space-y-3 max-h-[420px] overflow-y-auto pr-1">
                  {operations.map((op) => (
                    <button
                      key={op.id}
                      onClick={() => handleSelectOperation(op)}
                      className={`w-full text-left border rounded-lg p-4 transition ${
                        selectedOp?.id === op.id ? "bg-blue-50 border-blue-200" : "hover:border-gray-300"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-semibold text-gray-900">{op.intent}</p>
                          <p className="text-sm text-gray-600">{op.actor} • {op.triggered_by}</p>
                        </div>
                        <Badge variant="outline">{formatWhen(op.started_at)}</Badge>
                      </div>
                      {op.metadata?.query && (
                        <p className="text-xs text-gray-500 mt-1">Query: {op.metadata.query}</p>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Audit Detail</CardTitle>
              <CardDescription>Touchpoints, diffs, and metadata.</CardDescription>
            </CardHeader>
            <CardContent>
              {!selectedOp ? (
                <p className="text-sm text-gray-500">Select an operation to view audit details.</p>
              ) : auditLoading ? (
                <p className="text-sm text-gray-500">Loading audit log…</p>
              ) : !selectedOpDetail ? (
                <p className="text-sm text-gray-500">No audit data available.</p>
              ) : (
                <div className="space-y-4 text-sm">
                  <div>
                    <p className="text-gray-500 uppercase text-xs">Actor</p>
                    <p className="font-medium">{selectedOpDetail.actor || selectedOp.actor}</p>
                  </div>
                  <div>
                    <p className="text-gray-500 uppercase text-xs">Systems touched</p>
                    <ul className="list-disc list-inside">
                      {(selectedOpDetail.touched || []).map((touch, idx) => (
                        <li key={idx}>{touch.system} • {touch.action}</li>
                      ))}
                    </ul>
                  </div>
                  {selectedOpDetail.metadata && (
                    <div>
                      <p className="text-gray-500 uppercase text-xs">Metadata</p>
                      <pre className="bg-gray-50 rounded p-2 text-xs overflow-x-auto">
                        {JSON.stringify(selectedOpDetail.metadata, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

if (typeof document !== "undefined") {
  const mountNode = document.getElementById("aios-dashboard-root");
  if (mountNode && !mountNode.dataset.bootstrapped) {
    mountNode.dataset.bootstrapped = "true";
    createRoot(mountNode).render(<AIOSDashboard />);
  }
}
