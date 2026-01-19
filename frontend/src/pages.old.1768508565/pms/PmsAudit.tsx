import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Filter } from 'lucide-react'
import PageHeader from '@/components/PageHeader'
import { ipmApi } from '../../api/ipm'
import { useActor } from '../../contexts/ActorContext'
import { formatDateTime } from './pmsUtils'

export default function PmsAudit() {
  const { currentActor } = useActor()
  const [entityFilter, setEntityFilter] = useState('')

  const { data: events = [] } = useQuery({
    queryKey: ['pms-audit-global', currentActor],
    queryFn: () => ipmApi.listAuditEvents(undefined, currentActor),
  })

  const filtered = entityFilter
    ? events.filter((event) => event.entity_type.toLowerCase().includes(entityFilter.toLowerCase()))
    : events

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="IPM"
        title="Audit"
        description="Append-only audit events across projects."
      />

      <div className="glass-card p-4 flex items-center gap-2">
        <Filter className="w-4 h-4 text-[color:var(--osd-muted)]" />
        <input
          className="flex-1 bg-transparent text-sm text-[color:var(--osd-text)] focus:outline-none"
          placeholder="Filter by entity type"
          value={entityFilter}
          onChange={(event) => setEntityFilter(event.target.value)}
        />
      </div>

      <div className="glass-card p-5 space-y-2 text-sm">
        {filtered.map((event) => (
          <div key={event.event_id} className="flex items-center justify-between">
            <div>
              <div className="font-medium">{event.action}</div>
              <div className="text-xs text-[color:var(--osd-muted)]">
                {event.entity_type} · {event.entity_id}
              </div>
            </div>
            <div className="text-xs text-[color:var(--osd-muted)]">{formatDateTime(event.timestamp)}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
