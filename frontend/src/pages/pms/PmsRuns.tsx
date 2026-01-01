import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { FileDown, Play } from 'lucide-react'
import PageHeader from '@/components/PageHeader'
import { pmsApi } from '../../api/pms'
import { useActor } from '../../contexts/ActorContext'
import type { PmsExecutionRun, PmsArtifact } from '@/types/pms'
import { getAccessToken } from '@/lib/apiClient'
import { formatDateTime, shortId } from './pmsUtils'

type ArtifactPreview =
  | { kind: 'image'; url: string }
  | { kind: 'text'; content: string }
  | { kind: 'empty' }

export default function PmsRuns() {
  const { currentActor } = useActor()
  const [selectedRun, setSelectedRun] = useState<PmsExecutionRun | null>(null)
  const [selectedArtifact, setSelectedArtifact] = useState<PmsArtifact | null>(null)

  const { data: runs = [] } = useQuery({
    queryKey: ['pms-runs-global', currentActor],
    queryFn: () => pmsApi.listRuns({}, currentActor),
  })

  const { data: artifacts = [] } = useQuery({
    queryKey: ['pms-artifacts', selectedRun?.run_id, currentActor],
    queryFn: () => pmsApi.listArtifacts({ run_id: selectedRun?.run_id }, currentActor),
    enabled: !!selectedRun,
  })

  const { data: artifactPreview } = useQuery({
    queryKey: ['pms-artifact-preview', selectedArtifact?.artifact_id, currentActor],
    queryFn: async (): Promise<ArtifactPreview> => {
      if (!selectedArtifact) return { kind: 'empty' }
      const url = pmsApi.downloadArtifactUrl(selectedArtifact.artifact_id, currentActor)
      if (selectedArtifact.mime_type?.startsWith('image/')) {
        return { kind: 'image', url }
      }
      if (!selectedArtifact.mime_type?.startsWith('text/') && !selectedArtifact.mime_type?.includes('json')) {
        return { kind: 'empty' }
      }
      const headers: HeadersInit = {}
      const token = getAccessToken()
      if (token) headers.Authorization = `Bearer ${token}`
      const response = await fetch(url, { headers })
      const text = await response.text()
      if (selectedArtifact.mime_type?.includes('json')) {
        try {
          const parsed = JSON.parse(text)
          return { kind: 'text', content: JSON.stringify(parsed, null, 2) }
        } catch {
          return { kind: 'text', content: text }
        }
      }
      return { kind: 'text', content: text }
    },
    enabled: !!selectedArtifact,
  })

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="PMS"
        title="Runs"
        description="Track execution runs and artifacts across projects."
        actions={
          <button type="button" className="btn btn-secondary">
            <Play className="w-4 h-4" />
            Start Run
          </button>
        }
      />

      <div className="grid gap-4 lg:grid-cols-[1.3fr_1fr]">
        <div className="glass-card p-5 space-y-3">
          <h2 className="text-sm font-semibold">Runs</h2>
          <div className="space-y-2 text-sm">
            {runs.map((run) => (
              <button
                key={run.run_id}
                type="button"
                className={`w-full text-left rounded-lg border px-3 py-2 ${
                  selectedRun?.run_id === run.run_id
                    ? 'border-[color:var(--osd-accent)] bg-[color:var(--osd-accentSoft)]'
                    : 'border-[color:var(--osd-border)]'
                }`}
                onClick={() => {
                  setSelectedRun(run)
                  setSelectedArtifact(null)
                }}
              >
                <div className="flex items-center justify-between">
                  <span>{shortId(run.run_id)}</span>
                  <span className="text-xs text-[color:var(--osd-muted)]">{run.status}</span>
                </div>
                <div className="text-xs text-[color:var(--osd-muted)]">{formatDateTime(run.started_at)}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="glass-card p-5 space-y-3">
          <h2 className="text-sm font-semibold">Artifacts</h2>
          {selectedRun ? (
            <div className="space-y-3">
              <div className="space-y-2 text-sm">
                {(artifacts as PmsArtifact[]).map((artifact) => (
                  <button
                    key={artifact.artifact_id}
                    type="button"
                    className={`w-full text-left rounded-lg border px-3 py-2 flex items-center justify-between ${
                      selectedArtifact?.artifact_id === artifact.artifact_id
                        ? 'border-[color:var(--osd-accent)] bg-[color:var(--osd-accentSoft)]'
                        : 'border-[color:var(--osd-border)]'
                    }`}
                    onClick={() => setSelectedArtifact(artifact)}
                  >
                    <span className="truncate">{artifact.filename || shortId(artifact.artifact_id)}</span>
                    <a
                      className="text-xs text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]"
                      href={pmsApi.downloadArtifactUrl(artifact.artifact_id, currentActor)}
                      onClick={(event) => event.stopPropagation()}
                    >
                      <FileDown className="w-4 h-4" />
                    </a>
                  </button>
                ))}
              </div>
              <div className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40 p-3 text-xs">
                {selectedArtifact ? (
                  artifactPreview?.kind === 'image' ? (
                    <img
                      src={artifactPreview.url}
                      alt={selectedArtifact.filename || 'artifact preview'}
                      className="max-h-56 w-full object-contain rounded"
                    />
                  ) : artifactPreview?.kind === 'text' ? (
                    <pre className="whitespace-pre-wrap break-words">{artifactPreview.content}</pre>
                  ) : (
                    <p className="text-[color:var(--osd-muted)]">Preview not available for this artifact.</p>
                  )
                ) : (
                  <p className="text-[color:var(--osd-muted)]">Select an artifact to preview.</p>
                )}
              </div>
            </div>
          ) : (
            <p className="text-sm text-[color:var(--osd-muted)]">Select a run to view artifacts.</p>
          )}
        </div>
      </div>
    </div>
  )
}
