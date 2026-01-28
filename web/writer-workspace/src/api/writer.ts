import { apiRequest } from "./client";

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

export interface NarrativeGuide {
  title: string;
  status: string;
  detail: string;
  next_action: string;
}

export interface QAFinding {
  id: string;
  severity: string;
  area: string;
  summary: string;
  recommendation: string;
}

export interface QAMetrics {
  continuity: number;
  canon: number;
  voice: number;
  pacing: number;
}

export interface CollaborationParticipant {
  name: string;
  role: string;
  focus: string;
  status: string;
}

export interface ReviewCycle {
  name: string;
  owner: string;
  status: string;
  due: string;
  checklist: string[];
}

export interface CollaborationSnapshot {
  participants: CollaborationParticipant[];
  review_cycles: ReviewCycle[];
}

export interface PublishingRun {
  channel: string;
  target: string;
  stage: string;
  status: string;
  last_run: string;
  notes: string;
}

export interface OutlineEntry {
  id: string;
  stage: string;
  title: string;
  focus: string;
  status: string;
  word_target: number;
}

export interface ResearchNote {
  id: string;
  title: string;
  detail: string;
  linked_doc: string;
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
  narrative_guidance: NarrativeGuide[];
  qa_findings: QAFinding[];
  qa_metrics: QAMetrics;
  collaboration: CollaborationSnapshot;
  publishing_queue: PublishingRun[];
  outline: OutlineEntry[];
  notes: ResearchNote[];
  stats: WriterStats;
  progress: {
    days: string[];
    series: number[];
    goal: number;
  };
  timestamp: string;
}

export interface CanonEntryInput {
  category: string;
  title: string;
  description: string;
  meta?: string;
}

export interface PipelineEntryInput {
  title: string;
  summary: string;
  target: string;
  status: string;
}

const JSON_HEADERS = {
  "Content-Type": "application/json"
};

export async function fetchSnapshot(): Promise<WriterSnapshot> {
  return apiRequest<WriterSnapshot>("/writer/snapshot");
}

export async function createDocument(title: string, type: string, theme?: string) {
  return apiRequest<{ document: WriterDocument; workspace: WriterSnapshot }>("/writer/documents", {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify({ title, doc_type: type, theme })
  });
}

export async function saveDocument(documentId: string, content: string) {
  return apiRequest<{ document: WriterDocument; workspace: WriterSnapshot }>(`/writer/documents/${documentId}`, {
    method: "PUT",
    headers: JSON_HEADERS,
    body: JSON.stringify({ content })
  });
}

export async function generateNarrative(params: {
  title: string;
  type: string;
  genre: string;
  theme?: string;
}) {
  return apiRequest<{ content: string }>("/writer/generate", {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify({
      title: params.title,
      doc_type: params.type,
      genre: params.genre,
      theme: params.theme
    })
  });
}

export async function addCanonEntry(entry: CanonEntryInput) {
  return apiRequest<{ entry: WriterCanonEntry; workspace: WriterSnapshot }>("/writer/canon", {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify(entry)
  });
}

export async function queuePipelineEntry(entry: PipelineEntryInput) {
  return apiRequest<{ entry: WriterPipelineEntry; workspace: WriterSnapshot }>("/writer/pipeline", {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify(entry)
  });
}
