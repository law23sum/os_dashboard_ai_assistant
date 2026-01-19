import { useEffect, useMemo, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FileAudio, Plus } from 'lucide-react'
import PageHeader from '@/components/PageHeader'
import { ipmApi } from '../../api/ipm'
import { agentJournalApi } from '@/api/agentJournal'
import { useActor } from '../../contexts/ActorContext'
import type { PmsJournalSectionType, PmsMeetingSession } from '@/types/pms'
import { formatDateTime } from './pmsUtils'

const JOURNAL_SECTIONS: PmsJournalSectionType[] = [
  'Comments',
  'KnowledgeTransfer',
  'DisputableDebate',
  'ChallengesRisks',
  'SolutionsMitigations',
  'ProposalRaised',
  'MisunderstandingClarification',
  'TechnicalDesign',
  'CommonDiscussions',
  'Questions',
  'NextSteps',
]

const DETAIL_TABS = [
  { id: 'transcript', label: 'Transcript' },
  { id: 'journal', label: 'Structured Journal' },
  { id: 'speakers', label: 'Speaker Map' },
] as const

const AGENT_IDS = ['AIC', 'Aria', 'Sora'] as const

const AGENT_EVENT_TYPES = [
  'all',
  'thought',
  'question',
  'action',
  'modification',
  'debate',
  'dispute',
  'support',
  'rebuttal',
  'error',
  'recovery',
  'freeze_detected',
  'throttle_applied',
  'resource_update',
  'project_selection',
  'idle_handoff',
  'collaboration',
] as const

const parseTranscriptInput = (input: string) => {
  const lines = input
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)

  return lines.map((line, index) => {
    const match = line.match(/^([^:]{1,40}):\s*(.+)$/)
    const speakerLabel = match?.[1]?.trim() || 'Speaker 1'
    const textOriginal = match?.[2]?.trim() || line
    const tsStart = index * 5
    return {
      ts_start: tsStart,
      ts_end: tsStart + 5,
      speaker_label: speakerLabel,
      text_original: textOriginal,
    }
  })
}

const fileToBase64 = (file: File) =>
  new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const result = reader.result
      if (typeof result === 'string') {
        const [, base64] = result.split(',')
        resolve(base64 || '')
      } else {
        reject(new Error('Unable to read file'))
      }
    }
    reader.onerror = () => reject(reader.error || new Error('Failed to read file'))
    reader.readAsDataURL(file)
  })

export default function PmsJournal() {
  const { currentActor } = useActor()
  const queryClient = useQueryClient()
  const [journalMode, setJournalMode] = useState<'agents' | 'meetings'>('agents')
  const [agentFilter, setAgentFilter] = useState<'all' | (typeof AGENT_IDS)[number]>('all')
  const [agentEventType, setAgentEventType] = useState<(typeof AGENT_EVENT_TYPES)[number]>('all')
  const [includeSensitive, setIncludeSensitive] = useState(false)
  const [selectedMeeting, setSelectedMeeting] = useState<PmsMeetingSession | null>(null)
  const [newMeetingTitle, setNewMeetingTitle] = useState('')
  const [newMeetingProjectId, setNewMeetingProjectId] = useState('')
  const [consent, setConsent] = useState(false)
  const [recordingConsent, setRecordingConsent] = useState(false)
  const [speakerMapping, setSpeakerMapping] = useState<Record<string, string>>({})
  const [transcriptInput, setTranscriptInput] = useState('')
  const [activeTab, setActiveTab] = useState<(typeof DETAIL_TABS)[number]['id']>('transcript')
  const [sectionFilter, setSectionFilter] = useState<'all' | PmsJournalSectionType>('all')
  const audioInputRef = useRef<HTMLInputElement>(null)

  const { data: projects = [] } = useQuery({
    queryKey: ['pms-projects', currentActor],
    queryFn: () => ipmApi.listProjects(currentActor),
  })

  useEffect(() => {
    if (!newMeetingProjectId && projects.length > 0) {
      setNewMeetingProjectId(projects[0].project_id)
    }
  }, [projects, newMeetingProjectId])

  const { data: meetings = [] } = useQuery({
    queryKey: ['pms-meetings', currentActor],
    queryFn: () => ipmApi.listMeetings(undefined, currentActor),
    enabled: journalMode === 'meetings',
  })

  const { data: segments = [] } = useQuery({
    queryKey: ['pms-transcript', selectedMeeting?.meeting_id, currentActor],
    queryFn: () => ipmApi.listTranscriptSegments(selectedMeeting?.meeting_id as string, currentActor),
    enabled: !!selectedMeeting && journalMode === 'meetings',
  })

  const { data: journalBlocks = [] } = useQuery({
    queryKey: ['pms-journal', selectedMeeting?.meeting_id, sectionFilter, currentActor],
    queryFn: () =>
      ipmApi.listJournalBlocks(
        selectedMeeting?.meeting_id as string,
        currentActor,
        sectionFilter === 'all' ? undefined : sectionFilter,
      ),
    enabled: !!selectedMeeting && journalMode === 'meetings',
  })

  const { data: agentStats } = useQuery({
    queryKey: ['agent-journal-stats', includeSensitive],
    queryFn: () => agentJournalApi.getStats(includeSensitive),
    enabled: journalMode === 'agents',
  })

  const { data: agentEvents = [] } = useQuery({
    queryKey: ['agent-journal-events', agentFilter, agentEventType, includeSensitive],
    queryFn: () =>
      agentJournalApi.listEvents({
        agent_id: agentFilter === 'all' ? undefined : agentFilter,
        event_type: agentEventType === 'all' ? undefined : agentEventType,
        limit: 200,
        include_sensitive: includeSensitive,
      }),
    enabled: journalMode === 'agents',
  })

  const { data: teamEvents = [] } = useQuery({
    queryKey: ['agent-journal-team', agentEventType, includeSensitive],
    queryFn: () =>
      agentJournalApi.listTeamEvents({
        event_type: agentEventType === 'all' ? undefined : agentEventType,
        limit: 200,
        include_sensitive: includeSensitive,
      }),
    enabled: journalMode === 'agents',
  })

  const createMeeting = useMutation({
    mutationFn: () =>
      ipmApi.createMeeting(
        {
          project_id: newMeetingProjectId,
          title: newMeetingTitle,
          language: 'en',
          participants: [],
        },
        currentActor,
      ),
    onSuccess: () => {
      setNewMeetingTitle('')
      queryClient.invalidateQueries({ queryKey: ['pms-meetings'] })
    },
  })

  const transcribeMeeting = useMutation({
    mutationFn: () => {
      if (!selectedMeeting) {
        return Promise.reject(new Error('Select a meeting'))
      }
      const segmentsPayload = parseTranscriptInput(transcriptInput)
      return ipmApi.transcribeMeeting(selectedMeeting.meeting_id, { segments: segmentsPayload }, currentActor)
    },
    onSuccess: () => {
      setTranscriptInput('')
      queryClient.invalidateQueries({ queryKey: ['pms-transcript'] })
      queryClient.invalidateQueries({ queryKey: ['pms-journal'] })
      queryClient.invalidateQueries({ queryKey: ['pms-meetings'] })
    },
  })

  const uploadAudio = useMutation({
    mutationFn: async (file: File) => {
      if (!selectedMeeting) {
        throw new Error('Select a meeting')
      }
      const contentBase64 = await fileToBase64(file)
      return ipmApi.attachMeetingAudio(
        selectedMeeting.meeting_id,
        {
          filename: file.name,
          content_base64: contentBase64,
          mime_type: file.type || 'application/octet-stream',
          recording_consent: recordingConsent,
        },
        currentActor,
      )
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['pms-meetings'] }),
  })

  const updateMapping = useMutation({
    mutationFn: () =>
      ipmApi.updateSpeakerMapping(
        selectedMeeting?.meeting_id as string,
        { mapping: speakerMapping, consent },
        currentActor,
      ),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['pms-meetings'] }),
  })

  const meetingSummary = useMemo(() => {
    if (!selectedMeeting) return null
    return {
      title: selectedMeeting.title,
      participants: selectedMeeting.participants.length,
      started: selectedMeeting.started_at ? formatDateTime(selectedMeeting.started_at) : '—',
      language: selectedMeeting.language || '—',
    }
  }, [selectedMeeting])

  const agentStatsEntries = useMemo(
    () => (agentStats ? Object.entries(agentStats.agents) : []),
    [agentStats],
  )

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="IPM"
        title="Journal"
        description="Meeting transcripts, structured journals, and agent activity logs."
        actions={
          journalMode === 'meetings' ? (
            <button type="button" className="btn btn-primary" onClick={() => createMeeting.mutate()}>
              <Plus className="w-4 h-4" />
              New Meeting Record
            </button>
          ) : undefined
        }
      />

      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          className={`btn ${journalMode === 'agents' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setJournalMode('agents')}
        >
          Agent Journal
        </button>
        <button
          type="button"
          className={`btn ${journalMode === 'meetings' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setJournalMode('meetings')}
        >
          Meeting Journal
        </button>
      </div>

      {journalMode === 'agents' && (
        <>
          <div className="glass-card p-4 flex flex-wrap gap-3 items-end">
            <div className="flex-1 min-w-[180px]">
              <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Agent</label>
              <select
                className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
                value={agentFilter}
                onChange={(event) => setAgentFilter(event.target.value as typeof agentFilter)}
              >
                <option value="all">All Agents</option>
                {AGENT_IDS.map((agentId) => (
                  <option key={agentId} value={agentId}>
                    {agentId}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex-1 min-w-[180px]">
              <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Event type</label>
              <select
                className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
                value={agentEventType}
                onChange={(event) => setAgentEventType(event.target.value as typeof agentEventType)}
              >
                {AGENT_EVENT_TYPES.map((eventType) => (
                  <option key={eventType} value={eventType}>
                    {eventType === 'all' ? 'All types' : eventType}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-center gap-2">
              <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Sensitive</label>
              <input
                type="checkbox"
                className="h-4 w-4"
                checked={includeSensitive}
                onChange={(event) => setIncludeSensitive(event.target.checked)}
              />
            </div>
          </div>

          <div className="grid gap-4 lg:grid-cols-4">
            {agentStatsEntries.map(([agentId, stats]) => (
              <div key={agentId} className="glass-card p-4 space-y-2">
                <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Agent</div>
                <div className="text-lg font-semibold">{agentId}</div>
                <div className="text-sm text-[color:var(--osd-muted)]">Total events: {stats.total}</div>
                <div className="text-xs text-[color:var(--osd-muted)]">
                  Last update: {stats.last_timestamp ? formatDateTime(stats.last_timestamp) : '—'}
                </div>
              </div>
            ))}
            <div className="glass-card p-4 space-y-2">
              <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Team Journal</div>
              <div className="text-lg font-semibold">
                {agentStats?.team?.total ?? 0} events
              </div>
              <div className="text-sm text-[color:var(--osd-muted)]">
                Interactions: {agentStats?.totals?.team_interactions ?? 0}
              </div>
              <div className="text-xs text-[color:var(--osd-muted)]">
                Last update: {agentStats?.team?.last_timestamp ? formatDateTime(agentStats.team.last_timestamp) : '—'}
              </div>
            </div>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <div className="glass-card p-4 space-y-3">
              <h2 className="text-sm font-semibold">Team Collaboration Journal</h2>
              <div className="space-y-2 text-sm">
                {teamEvents.length === 0 && (
                  <div className="text-xs text-[color:var(--osd-muted)]">No team events logged yet.</div>
                )}
                {teamEvents.map((event, index) => (
                  <div key={`${event.entry_hash ?? index}`} className="flex flex-col gap-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{event.event_type}</span>
                      <span className="text-xs text-[color:var(--osd-muted)]">
                        {event.timestamp_utc ? formatDateTime(event.timestamp_utc) : '—'}
                      </span>
                    </div>
                    <div className="text-xs text-[color:var(--osd-muted)]">
                      {event.agent_id ? `${event.agent_id} · ` : ''}{event.summary}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="glass-card p-4 space-y-3">
              <h2 className="text-sm font-semibold">Agent Journal</h2>
              <div className="space-y-2 text-sm">
                {agentEvents.length === 0 && (
                  <div className="text-xs text-[color:var(--osd-muted)]">No agent events logged yet.</div>
                )}
                {agentEvents.map((event, index) => (
                  <div key={`${event.entry_hash ?? index}`} className="flex flex-col gap-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{event.event_type}</span>
                      <span className="text-xs text-[color:var(--osd-muted)]">
                        {event.timestamp_utc ? formatDateTime(event.timestamp_utc) : '—'}
                      </span>
                    </div>
                    <div className="text-xs text-[color:var(--osd-muted)]">
                      {event.agent_id ? `${event.agent_id} · ` : ''}{event.summary}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}

      {journalMode === 'meetings' && (
        <>
      <div className="glass-card p-4 flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-[220px]">
          <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Project</label>
          <select
            className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
            value={newMeetingProjectId}
            onChange={(event) => setNewMeetingProjectId(event.target.value)}
          >
            {projects.map((project) => (
              <option key={project.project_id} value={project.project_id}>
                {project.name}
              </option>
            ))}
          </select>
        </div>
        <div className="flex-[2] min-w-[220px]">
          <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Meeting title</label>
          <input
            className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
            placeholder="Meeting title"
            value={newMeetingTitle}
            onChange={(event) => setNewMeetingTitle(event.target.value)}
          />
        </div>
        <button
          type="button"
          className="btn btn-secondary"
          disabled={!newMeetingTitle || !newMeetingProjectId}
          onClick={() => createMeeting.mutate()}
        >
          Create
        </button>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.3fr_1fr]">
        <div className="glass-card p-5 space-y-3">
          <h2 className="text-sm font-semibold">Meetings</h2>
          <div className="space-y-2 text-sm">
            {meetings.map((meeting) => (
              <button
                key={meeting.meeting_id}
                type="button"
                className={`w-full text-left rounded-lg border px-3 py-2 ${
                  selectedMeeting?.meeting_id === meeting.meeting_id
                    ? 'border-[color:var(--osd-accent)] bg-[color:var(--osd-accentSoft)]'
                    : 'border-[color:var(--osd-border)]'
                }`}
                onClick={() => {
                  setSelectedMeeting(meeting)
                  setSpeakerMapping(meeting.speaker_mapping ?? {})
                  setConsent(!!meeting.speaker_mapping_consent)
                  setActiveTab('transcript')
                }}
              >
                <div className="flex items-center justify-between">
                  <span>{meeting.title}</span>
                  <span className="text-xs text-[color:var(--osd-muted)]">{meeting.participants.length} people</span>
                </div>
                <div className="text-xs text-[color:var(--osd-muted)]">{formatDateTime(meeting.started_at)}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="glass-card p-5 space-y-4">
          <div className="flex items-center gap-2">
            <FileAudio className="w-4 h-4 text-[color:var(--osd-muted)]" />
            <h2 className="text-sm font-semibold">Meeting Detail</h2>
          </div>
          {selectedMeeting ? (
            <>
              <div className="rounded-lg border border-[color:var(--osd-border)] p-3 text-xs text-[color:var(--osd-muted)] space-y-1">
                <div className="text-sm font-medium text-[color:var(--osd-text)]">{meetingSummary?.title}</div>
                <div>Participants: {meetingSummary?.participants}</div>
                <div>Started: {meetingSummary?.started}</div>
                <div>Language: {meetingSummary?.language}</div>
              </div>

              <div className="rounded-lg border border-[color:var(--osd-border)] p-3 space-y-2">
                <label className="flex items-center gap-2 text-xs text-[color:var(--osd-muted)]">
                  <input
                    type="checkbox"
                    checked={recordingConsent}
                    onChange={(event) => setRecordingConsent(event.target.checked)}
                  />
                  Recording consent granted
                </label>
                <input
                  ref={audioInputRef}
                  type="file"
                  accept="audio/*"
                  className="hidden"
                  onChange={(event) => {
                    const file = event.target.files?.[0]
                    if (!file) return
                    uploadAudio.mutate(file)
                  }}
                />
                <button
                  type="button"
                  className="btn btn-secondary"
                  disabled={!recordingConsent || uploadAudio.isPending}
                  onClick={() => audioInputRef.current?.click()}
                >
                  Upload Audio
                </button>
              </div>

              <div className="flex flex-wrap gap-2">
                {DETAIL_TABS.map((tab) => (
                  <button
                    key={tab.id}
                    type="button"
                    className={`px-3 py-1.5 rounded-full text-xs border transition-colors ${
                      activeTab === tab.id
                        ? 'border-[color:var(--osd-accent)] bg-[color:var(--osd-accentSoft)] text-[color:var(--osd-text)]'
                        : 'border-[color:var(--osd-border)] text-[color:var(--osd-muted)]'
                    }`}
                    onClick={() => setActiveTab(tab.id)}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {activeTab === 'transcript' && (
                <div className="space-y-3 text-sm">
                  <textarea
                    className="w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-xs min-h-[120px]"
                    placeholder="Paste transcript lines like: Speaker 1: We agreed on next steps..."
                    value={transcriptInput}
                    onChange={(event) => setTranscriptInput(event.target.value)}
                  />
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => transcribeMeeting.mutate()}
                    disabled={!transcriptInput || transcribeMeeting.isPending}
                  >
                    Transcribe + Generate Journal
                  </button>
                  <div className="space-y-2">
                    {segments.map((segment) => (
                      <div key={`${segment.ts_start}-${segment.speaker_label}`}>
                        <span className="text-xs text-[color:var(--osd-muted)]">{segment.speaker_label}</span>
                        <p>{segment.text_original}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'journal' && (
                <div className="space-y-3 text-sm">
                  <select
                    className="w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-xs"
                    value={sectionFilter}
                    onChange={(event) => setSectionFilter(event.target.value as typeof sectionFilter)}
                  >
                    <option value="all">All sections</option>
                    {JOURNAL_SECTIONS.map((section) => (
                      <option key={section} value={section}>
                        {section}
                      </option>
                    ))}
                  </select>
                  <div className="space-y-2">
                    {journalBlocks.map((block) => (
                      <div key={`${block.section_type}-${block.ts_start}`}>
                        <span className="text-xs text-[color:var(--osd-muted)]">{block.section_type}</span>
                        <p>{block.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'speakers' && (
                <div className="rounded-lg border border-[color:var(--osd-border)] p-3 space-y-2">
                  <label className="flex items-center gap-2 text-xs text-[color:var(--osd-muted)]">
                    <input
                      type="checkbox"
                      checked={consent}
                      onChange={(event) => setConsent(event.target.checked)}
                    />
                    Consent to map speaker labels
                  </label>
                  <textarea
                    className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-xs"
                    placeholder="Speaker 1: Alex\nSpeaker 2: Jamie"
                    value={Object.entries(speakerMapping)
                      .map(([key, value]) => `${key}: ${value}`)
                      .join('\n')}
                    onChange={(event) => {
                      const mapping: Record<string, string> = {}
                      event.target.value.split('\n').forEach((line) => {
                        const [key, ...rest] = line.split(':')
                        if (!key || rest.length === 0) return
                        mapping[key.trim()] = rest.join(':').trim()
                      })
                      setSpeakerMapping(mapping)
                    }}
                  />
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => updateMapping.mutate()}
                    disabled={updateMapping.isPending}
                  >
                    Save Mapping
                  </button>
                </div>
              )}
            </>
          ) : (
            <p className="text-sm text-[color:var(--osd-muted)]">Select a meeting to view details.</p>
          )}
        </div>
      </div>
        </>
      )}
    </div>
  )
}
