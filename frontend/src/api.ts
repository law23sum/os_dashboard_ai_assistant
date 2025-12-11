import { resolveApiBase } from './lib/apiClient'

const API_BASE = resolveApiBase()

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path.startsWith("/") ? path : `/${path}`}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return res.json();
}

export const API = {
  system: () => request("/system"),
  planes: () => request("/planes/status"),
  projects: () => request("/projects"),
  billing: () => request("/billing/usage"),
  daemons: () => request("/daemons"),
  toggleDaemon: (name: string, enabled: boolean) =>
    request(`/daemons/${encodeURIComponent(name)}/${enabled ? "enable" : "disable"}`, {
      method: "POST",
    }),
  runDaemon: (name: string) => request(`/daemons/${encodeURIComponent(name)}/run`, { method: "POST" }),
  operations: () => request("/operations?limit=50"),
  audit: (id: string) => request(`/audit/${encodeURIComponent(id)}`),
  search: (query: string) => request(`/search?q=${encodeURIComponent(query)}`),
  ask: (prompt: string) =>
    request("/ai/ask", {
      method: "POST",
      body: JSON.stringify({ prompt }),
    }),
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
};
