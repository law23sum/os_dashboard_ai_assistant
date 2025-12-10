export interface WriterDocument {
  id: string;
  title: string;
  type: string;
  status: string;
  words: number;
  last_edited: string;
  summary: string;
  theme?: string;
  content?: string;
}

export interface WriterSuggestion {
  title: string;
  body: string;
}

export interface WriterCanonEntry {
  category: string;
  title: string;
  description: string;
  meta: string;
}

export interface WriterPipelineEntry {
  title: string;
  summary: string;
  meta: string;
  status: string;
}

export interface WriterStats {
  total_words: number;
  documents: number;
  avg_words_per_day: number;
  writing_streak: number;
}

export interface WriterSnapshot {
  documents: WriterDocument[];
  suggestions: WriterSuggestion[];
  canon_entries: WriterCanonEntry[];
  pipeline_entries: WriterPipelineEntry[];
  stats: WriterStats;
  progress: {
    days: string[];
    series: number[];
    goal: number;
  };
  timestamp: string;
}

const JSON_HEADERS = {
  "Content-Type": "application/json"
};

async function handleResponse<T>(resp: Response): Promise<T> {
  if (!resp.ok) {
    throw new Error(`Writer API error (${resp.status})`);
  }
  return resp.json() as Promise<T>;
}

export async function fetchSnapshot(): Promise<WriterSnapshot> {
  const resp = await fetch("/writer/snapshot");
  return handleResponse<WriterSnapshot>(resp);
}

export async function createDocument(title: string, type: string, theme?: string) {
  const resp = await fetch("/writer/documents", {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify({ title, type, theme })
  });
  return handleResponse<{ document: WriterDocument; workspace: WriterSnapshot }>(resp);
}

export async function saveDocument(documentId: string, content: string) {
  const resp = await fetch(`/writer/documents/${documentId}/save`, {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify({ content })
  });
  return handleResponse<{ document: WriterDocument; workspace: WriterSnapshot }>(resp);
}

export async function generateNarrative(params: {
  title: string;
  type: string;
  genre: string;
  theme?: string;
}) {
  const resp = await fetch("/writer/narrative", {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify(params)
  });
  return handleResponse<{ content: string }>(resp);
}
