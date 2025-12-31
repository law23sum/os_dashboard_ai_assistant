import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { FileDown, Play } from 'lucide-react'
import PageHeader from '../../components/PageHeader'
import { pmsApi } from '../../api/pms'
import { useActor } from '../../contexts/ActorContext'
import type { PmsExecutionRun, PmsArtifact } from '../../types/pms'
import { formatDateTime, shortId } from './pmsUtils'

export default function PmsRuns() {
  const { currentActor } = useActor()
  const [selectedRun, setSelectedRun] = useState<PmsExecutionRun | null>(null)

  const { data: runs = [] } = useQuery({
    queryKey: ['pms-runs-global', currentActor],
    queryFn: () => pmsApi.listRuns({}, currentActor),
  })

  const { data: artifacts = [] } = useQuery({
    queryKey: ['pms-artifacts', selectedRun?.run_id, currentActor],
    queryFn: () => pmsApi.listArtifacts({ run_id: selectedRun?.run_id }, currentActor),
    enabled: !!selectedRun,
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

      <div className="grid gap-4 lg:grid-cols-[1.5fr_1fr]">
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
                onClick={() => setSelectedRun(run)}
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
            <div className="space-y-2 text-sm">
              {(artifacts as PmsArtifact[]).map((artifact) => (
                <div key={artifact.artifact_id} className="flex items-center justify-between">
                  <span>{artifact.filename}</span>
                  <a
                    className="text-xs text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]"
                    href={pmsApi.downloadArtifactUrl(artifact.artifact_id, currentActor)}
                  >
                    <FileDown className="w-4 h-4" />
                  </a>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-[color:var(--osd-muted)]">Select a run to view artifacts.</p>
          )}
        </div>
      </div>
    </div>
  )
}
