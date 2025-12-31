import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FileAudio, Plus } from 'lucide-react'
import PageHeader from '../../components/PageHeader'
import { pmsApi } from '../../api/pms'
import { useActor } from '../../contexts/ActorContext'
import type { PmsMeetingSession } from '../../types/pms'
import { formatDateTime } from './pmsUtils'

export default function PmsJournal() {
  const { currentActor } = useActor()
  const queryClient = useQueryClient()
  const [selectedMeeting, setSelectedMeeting] = useState<PmsMeetingSession | null>(null)
  const [newMeetingTitle, setNewMeetingTitle] = useState('')
  const [consent, setConsent] = useState(false)
  const [speakerMapping, setSpeakerMapping] = useState<Record<string, string>>({})

  const { data: meetings = [] } = useQuery({
    queryKey: ['pms-meetings', currentActor],
    queryFn: () => pmsApi.listMeetings(undefined, currentActor),
  })

  const { data: segments = [] } = useQuery({
    queryKey: ['pms-transcript', selectedMeeting?.meeting_id, currentActor],
    queryFn: () => pmsApi.listTranscriptSegments(selectedMeeting?.meeting_id as string, currentActor),
    enabled: !!selectedMeeting,
  })

  const { data: journalBlocks = [] } = useQuery({
    queryKey: ['pms-journal', selectedMeeting?.meeting_id, currentActor],
    queryFn: () => pmsApi.listJournalBlocks(selectedMeeting?.meeting_id as string, currentActor),
    enabled: !!selectedMeeting,
  })

  const createMeeting = useMutation({
    mutationFn: () =>
      pmsApi.createMeeting(
        {
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

  const updateMapping = useMutation({
    mutationFn: () =>
      pmsApi.updateSpeakerMapping(
        selectedMeeting?.meeting_id as string,
        { mapping: speakerMapping, consent },
        currentActor,
      ),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['pms-meetings'] }),
  })

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="PMS"
        title="Journal"
        description="Meeting transcripts and structured collaborative journals."
        actions={
          <button type="button" className="btn btn-primary" onClick={() => createMeeting.mutate()}>
            <Plus className="w-4 h-4" />
            New Meeting Record
          </button>
        }
      />

      <div className="glass-card p-4 flex gap-3 items-center">
        <input
          className="flex-1 rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
          placeholder="Meeting title"
          value={newMeetingTitle}
          onChange={(event) => setNewMeetingTitle(event.target.value)}
        />
        <button
          type="button"
          className="btn btn-secondary"
          disabled={!newMeetingTitle}
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
            <h2 className="text-sm font-semibold">Transcript & Journal</h2>
          </div>
          {selectedMeeting ? (
            <>
              <div className="space-y-2 text-sm">
                {segments.slice(0, 5).map((segment) => (
                  <div key={`${segment.ts_start}-${segment.speaker_label}`}>
                    <span className="text-xs text-[color:var(--osd-muted)]">{segment.speaker_label}</span>
                    <p>{segment.text_original}</p>
                  </div>
                ))}
              </div>
              <div className="mt-4 space-y-2 text-sm">
                {journalBlocks.slice(0, 5).map((block) => (
                  <div key={`${block.section_type}-${block.ts_start}`}>
                    <span className="text-xs text-[color:var(--osd-muted)]">{block.section_type}</span>
                    <p>{block.content}</p>
                  </div>
                ))}
              </div>
              <div className="mt-4 rounded-lg border border-[color:var(--osd-border)] p-3">
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
                  className="btn btn-secondary mt-2"
                  onClick={() => updateMapping.mutate()}
                >
                  Save Mapping
                </button>
              </div>
            </>
          ) : (
            <p className="text-sm text-[color:var(--osd-muted)]">Select a meeting to view details.</p>
          )}
        </div>
      </div>
    </div>
  )
}
