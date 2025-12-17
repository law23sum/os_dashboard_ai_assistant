import { resolveApiBase } from './lib/apiClient'

const API_BASE = resolveApiBase()

async function request<T = any>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path.startsWith("/") ? path : `/${path}`}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  const requestId = res.headers.get("x-correlation-id") || res.headers.get("x-request-id") || undefined;

  if (!res.ok) {
    const message = `Request failed: ${res.status}${requestId ? ` (request_id=${requestId})` : ""}`;
    throw new Error(message);
  }

  const data = await res.json();
  if (data && typeof data === "object" && !Array.isArray(data)) {
    (data as Record<string, unknown>)._requestId = requestId;
  }
  return data;
}

export const API = {
  // Core system endpoints
  system: () => request("/system"),
  planes: () => request("/planes/status"),
  projects: () => request("/projects"),
  billing: () => request("/billing/usage"),
  
  // Daemon management
  daemons: () => request("/daemons"),
  toggleDaemon: (name: string, enabled: boolean) =>
    request(`/daemons/${encodeURIComponent(name)}/${enabled ? "enable" : "disable"}`, {
      method: "POST",
    }),
  runDaemon: (name: string) => request(`/daemons/${encodeURIComponent(name)}/run`, { method: "POST" }),
  
  // Operations & audit
  operations: () => request("/operations?limit=50"),
  audit: (id: string) => request(`/audit/${encodeURIComponent(id)}`),
  
  // Search & AI
  search: (query: string) => request(`/search?q=${encodeURIComponent(query)}`),
  ask: (prompt: string) =>
    request("/ai/ask", {
      method: "POST",
      body: JSON.stringify({ prompt }),
    }),
  
  // Research workspace
  researchWorkspace: () => request("/research/workspace"),
  runSimulation: (payload: { type: string; modelId: string; iterations: number }) =>
    request("/research/run-simulation", {
      method: "POST",
      body: JSON.stringify({
        type: payload.type,
        model_id: payload.modelId,
        iterations: payload.iterations,
      }),
    }),
  designExperiment: (payload: { type: string; variables: string[] }) =>
    request("/research/design-experiment", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // =========================================================================
  // OBSERVABILITY & RUNTIME DIAGNOSTICS (v1000)
  // =========================================================================
  observability: {
    snapshot: () => request("/observability/snapshot"),
    events: (limit = 100, severity?: string) => {
      const params = new URLSearchParams({ limit: String(limit) });
      if (severity) params.append("severity", severity);
      return request(`/observability/events?${params}`);
    },
    suggestions: () => request("/observability/suggestions"),
    applySuggestion: (suggestionId: string) =>
      request(`/observability/suggestions/${encodeURIComponent(suggestionId)}/apply`, {
        method: "POST",
      }),
    dismissSuggestion: (suggestionId: string) =>
      request(`/observability/suggestions/${encodeURIComponent(suggestionId)}/dismiss`, {
        method: "POST",
      }),
    metrics: () => request("/observability/metrics"),
    health: () => request("/observability/health"),
  },

  // =========================================================================
  // CAPSULE MARKETPLACE (v1000)
  // =========================================================================
  capsules: {
    list: (filters?: { category?: string; status?: string; search?: string }) => {
      const params = new URLSearchParams();
      if (filters?.category) params.append("category", filters.category);
      if (filters?.status) params.append("status", filters.status);
      if (filters?.search) params.append("search", filters.search);
      const query = params.toString();
      return request(`/capsules${query ? `?${query}` : ""}`);
    },
    get: (id: string) => request(`/capsules/${encodeURIComponent(id)}`),
    create: (spec: Record<string, unknown>) =>
      request("/capsules", {
        method: "POST",
        body: JSON.stringify(spec),
      }),
    update: (id: string, spec: Record<string, unknown>) =>
      request(`/capsules/${encodeURIComponent(id)}`, {
        method: "PUT",
        body: JSON.stringify(spec),
      }),
    delete: (id: string) =>
      request(`/capsules/${encodeURIComponent(id)}`, { method: "DELETE" }),
    run: (id: string, params?: Record<string, unknown>) =>
      request(`/capsules/${encodeURIComponent(id)}/run`, {
        method: "POST",
        body: JSON.stringify(params ?? {}),
      }),
    logs: (id: string, limit = 20) =>
      request(`/capsules/${encodeURIComponent(id)}/logs?limit=${limit}`),
    featured: () => request("/capsules/featured"),
    categories: () => request("/capsules/categories"),
  },

  // =========================================================================
  // BLUEPRINTS (v1000)
  // =========================================================================
  blueprints: {
    list: () => request("/blueprints"),
    get: (id: string) => request(`/blueprints/${encodeURIComponent(id)}`),
    create: (spec: Record<string, unknown>) =>
      request("/blueprints", {
        method: "POST",
        body: JSON.stringify(spec),
      }),
    execute: (id: string, params?: Record<string, unknown>) =>
      request(`/blueprints/${encodeURIComponent(id)}/execute`, {
        method: "POST",
        body: JSON.stringify(params ?? {}),
      }),
  },

  // =========================================================================
  // AUTO-FIX & SELF-HEALING (v1000)
  // =========================================================================
  autoFix: {
    status: () => request("/autofix/status"),
    config: () => request("/autofix/config"),
    updateConfig: (config: Record<string, unknown>) =>
      request("/autofix/config", {
        method: "PUT",
        body: JSON.stringify(config),
      }),
    scan: () => request("/autofix/scan", { method: "POST" }),
    issues: (status?: string) => {
      const query = status ? `?status=${encodeURIComponent(status)}` : "";
      return request(`/autofix/issues${query}`);
    },
    applyFix: (issueId: string) =>
      request(`/autofix/issues/${encodeURIComponent(issueId)}/apply`, {
        method: "POST",
      }),
    skipIssue: (issueId: string) =>
      request(`/autofix/issues/${encodeURIComponent(issueId)}/skip`, {
        method: "POST",
      }),
    reports: (limit = 10) => request(`/autofix/reports?limit=${limit}`),
    report: (id: string) => request(`/autofix/reports/${encodeURIComponent(id)}`),
  },

  // =========================================================================
  // PLANE ORCHESTRATION (v1000)
  // =========================================================================
  planeOrchestration: {
    snapshot: () => request("/planes/orchestration"),
    dataPlane: () => request("/planes/data"),
    controlPlane: () => request("/planes/control"),
    governancePlane: () => request("/planes/governance"),
    sync: () => request("/planes/sync", { method: "POST" }),
  },

  // =========================================================================
  // DRIVER REGISTRY (v1000)
  // =========================================================================
  drivers: {
    list: () => request("/drivers"),
    get: (id: string) => request(`/drivers/${encodeURIComponent(id)}`),
    toggle: (id: string, enabled: boolean) =>
      request(`/drivers/${encodeURIComponent(id)}/${enabled ? "enable" : "disable"}`, {
        method: "POST",
      }),
    metrics: (id: string) => request(`/drivers/${encodeURIComponent(id)}/metrics`),
  },

  // =========================================================================
  // INTENT PROCESSING (v1000)
  // =========================================================================
  intents: {
    submit: (query: string, context?: Record<string, unknown>, priority?: string) =>
      request("/intents", {
        method: "POST",
        body: JSON.stringify({ query, context, priority }),
      }),
    get: (id: string) => request(`/intents/${encodeURIComponent(id)}`),
    list: (limit = 20) => request(`/intents?limit=${limit}`),
    cancel: (id: string) =>
      request(`/intents/${encodeURIComponent(id)}/cancel`, { method: "POST" }),
  },
};
