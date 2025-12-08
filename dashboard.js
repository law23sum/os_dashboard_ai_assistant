import React, { useEffect, useMemo, useRef, useState } from "https://esm.sh/react@18";
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

// Utility functions
const systemMeta = {
  word: { label: "Word", icon: "📄", tone: "bg-blue-100" },
  excel: { label: "Excel", icon: "📊", tone: "bg-green-100" },
  pdf: { label: "PDF", icon: "📕", tone: "bg-red-100" },
  notes: { label: "Notes", icon: "📝", tone: "bg-yellow-100" },
  git: { label: "Git", icon: "🔒", tone: "bg-gray-100" },
  filesystem: { label: "Filesystem", icon: "💾", tone: "bg-purple-100" },
  unknown: { label: "Unknown", icon: "❓", tone: "bg-gray-100" },
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
    const d = new Date(iso);
    return d.toLocaleString();
  } catch {
    return iso;
  }
}

// API client
const API = {
  async search(query) {
    try {
      const res = await fetch(`/search?q=${encodeURIComponent(query)}`);
      if (!res.ok) throw new Error("search_failed");
      return await res.json();
    } catch {
      return MOCK_SEARCH.filter(r =>
        query && `${r.node_title} ${r.text_snippet}`.toLowerCase().includes(query.toLowerCase())
      );
    }
  },

  async getAudit(opId) {
    try {
      const res = await fetch(`/audit/${encodeURIComponent(opId)}`);
      if (!res.ok) throw new Error("audit_failed");
      return await res.json();
    } catch {
      return MOCK_OPS.find(o => o.id === opId) || null;
    }
  },

  async listOperations() {
    try {
      const res = await fetch('/operations?limit=50');
      if (!res.ok) throw new Error("ops_failed");
      return await res.json();
    } catch {
      return MOCK_OPS;
    }
  },

  async listDaemons() {
    try {
      const res = await fetch('/daemons');
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
};

// UI Components
function Badge({ children, variant = "secondary", className = "" }) {
  const baseClasses = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium";
  const variants = {
    secondary: "bg-gray-100 text-gray-800",
    destructive: "bg-red-100 text-red-800",
    outline: "border border-gray-300 text-gray-700",
  };
  return (
    <span className={`${baseClasses} ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
}

function Button({ children, variant = "default", size = "default", onClick, disabled, className = "" }) {
  const baseClasses = "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2";
  const variants = {
    default: "bg-blue-600 text-white hover:bg-blue-700 focus-visible:ring-blue-500",
    secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200 focus-visible:ring-gray-500",
    outline: "border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus-visible:ring-gray-500",
    ghost: "text-gray-700 hover:bg-gray-100 focus-visible:ring-gray-500",
  };
  const sizes = {
    default: "h-10 px-4 py-2",
    sm: "h-8 px-3 text-sm",
    icon: "h-10 w-10",
  };
  return (
    <button
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

function Card({ children, className = "" }) {
  return (
    <div className={`bg-white border border-gray-200 rounded-lg shadow-sm ${className}`}>
      {children}
    </div>
  );
}

function CardHeader({ children, className = "" }) {
  return <div className={`p-6 pb-4 ${className}`}>{children}</div>;
}

function CardTitle({ children, className = "" }) {
  return <h3 className={`text-lg font-semibold ${className}`}>{children}</h3>;
}

function CardDescription({ children, className = "" }) {
  return <p className={`text-sm text-gray-600 mt-1 ${className}`}>{children}</p>;
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
      className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${className}`}
    />
  );
}

function Tabs({ defaultValue, children }) {
  const [activeTab, setActiveTab] = useState(defaultValue);
  return React.cloneElement(children, { activeTab, setActiveTab });
}

function TabsList({ children, activeTab, setActiveTab, className = "" }) {
  return (
    <div className={`flex space-x-1 bg-gray-100 p-1 rounded-lg ${className}`}>
      {React.Children.map(children, child =>
        React.cloneElement(child, { activeTab, setActiveTab })
      )}
    </div>
  );
}

function TabsTrigger({ value, children, activeTab, setActiveTab }) {
  return (
    <button
      onClick={() => setActiveTab(value)}
      className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
        activeTab === value
          ? 'bg-white text-gray-900 shadow-sm'
          : 'text-gray-600 hover:text-gray-900'
      }`}
    >
      {children}
    </button>
  );
}

function TabsContent({ value, children, activeTab }) {
  if (activeTab !== value) return null;
  return <div className="mt-4">{children}</div>;
}

// Main Dashboard Component
export default function AIOSDashboard() {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [daemons, setDaemons] = useState([]);
  const [operations, setOperations] = useState([]);
  const [selectedOp, setSelectedOp] = useState(null);

  useEffect(() => {
    // Load initial data
    loadDaemons();
    loadOperations();
  }, []);

  const loadDaemons = async () => {
    const data = await API.listDaemons();
    setDaemons(data);
  };

  const loadOperations = async () => {
    const data = await API.listOperations();
    setOperations(data);
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    const results = await API.search(searchQuery);
    setSearchResults(results);
    setLoading(false);
  };

  const toggleDaemon = async (daemon) => {
    const success = await API.setDaemonEnabled(daemon.name, !daemon.enabled);
    if (success) {
      setDaemons(daemons.map(d =>
        d.name === daemon.name ? { ...d, enabled: !d.enabled } : d
      ));
    }
  };

  const runDaemon = async (daemon) => {
    await API.runDaemon(daemon.name);
    loadOperations(); // Refresh operations list
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <Card>
          <CardContent className="p-6">
            <div className="text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                🚀 AI OS Dashboard
              </h1>
              <p className="text-gray-600">
                Governed AI OS with unified search, audit trails, and daemon control
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Tabs defaultValue="search">
          {({ activeTab, setActiveTab }) => (
            <>
              <TabsList activeTab={activeTab} setActiveTab={setActiveTab}>
                <TabsTrigger value="search">🔍 Search</TabsTrigger>
                <TabsTrigger value="daemons">🤖 Daemons</TabsTrigger>
                <TabsTrigger value="activity">📊 Activity</TabsTrigger>
              </TabsList>

              <TabsContent value="search" activeTab={activeTab}>
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <Card className="lg:col-span-1">
                    <CardHeader>
                      <CardTitle>Unified Search</CardTitle>
                      <CardDescription>Search across all document types</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <Input
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search documents..."
                        className="mb-4"
                      />
                      <Button onClick={handleSearch} disabled={loading}>
                        {loading ? "Searching..." : "Search"}
                      </Button>
                    </CardContent>
                  </Card>

                  <Card className="lg:col-span-2">
                    <CardHeader>
                      <CardTitle>Results</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {loading ? (
                        <div className="text-center py-8">Loading...</div>
                      ) : searchResults.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                          No results yet. Try searching for documents.
                        </div>
                      ) : (
                        <div className="space-y-4">
                          {searchResults.map((result, idx) => (
                            <div key={idx} className="border rounded-lg p-4">
                              <div className="flex items-center gap-2 mb-2">
                                <span>{getSystemIcon(result.system)}</span>
                                <span className="font-medium">{result.node_title}</span>
                                <Badge variant="outline">{result.system}</Badge>
                              </div>
                              <p className="text-sm text-gray-600">{result.text_snippet}</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="daemons" activeTab={activeTab}>
                <Card>
                  <CardHeader>
                    <CardTitle>Daemon Control Panel</CardTitle>
                    <CardDescription>Manage automated workflows</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {daemons.map((daemon) => (
                        <div key={daemon.name} className="border rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h3 className="font-medium">{daemon.name}</h3>
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
                            <Button size="sm" variant="outline" onClick={() => runDaemon(daemon)}>
                              Run Now
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="activity" activeTab={activeTab}>
                <Card>
                  <CardHeader>
                    <CardTitle>Activity Timeline</CardTitle>
                    <CardDescription>Recent operations and audit trail</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {operations.map((op) => (
                        <div key={op.id} className="border rounded-lg p-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <h3 className="font-medium">{op.intent}</h3>
                              <p className="text-sm text-gray-600">{op.actor} • {op.triggered_by}</p>
                            </div>
                            <Badge variant="outline">{formatWhen(op.started_at)}</Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </>
          )}
        </Tabs>
      </div>
    </div>
  );
}
