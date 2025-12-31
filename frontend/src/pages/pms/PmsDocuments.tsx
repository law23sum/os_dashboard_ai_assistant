import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FileText, Plus } from 'lucide-react'
import PageHeader from '../../components/PageHeader'
import { pmsApi } from '../../api/pms'
import { useActor } from '../../contexts/ActorContext'
import type { PmsDocument } from '../../types/pms'
import { formatDateTime, shortId } from './pmsUtils'

export default function PmsDocuments() {
  const { currentActor } = useActor()
  const queryClient = useQueryClient()
  const [selectedDoc, setSelectedDoc] = useState<PmsDocument | null>(null)
  const [newDocTitle, setNewDocTitle] = useState('')

  const { data: documents = [] } = useQuery({
    queryKey: ['pms-documents', currentActor],
    queryFn: () => pmsApi.listDocuments(undefined, currentActor),
  })

  const { data: documentDetail } = useQuery({
    queryKey: ['pms-document', selectedDoc?.document_id, currentActor],
    queryFn: () =>
      pmsApi.getDocument(selectedDoc?.document_id as string, 'published', currentActor),
    enabled: !!selectedDoc,
  })

  const createDocument = useMutation({
    mutationFn: () =>
      pmsApi.createDocument(
        {
          title: newDocTitle,
          kind: 'spec',
          visibility: 'private',
        },
        currentActor,
      ),
    onSuccess: () => {
      setNewDocTitle('')
      queryClient.invalidateQueries({ queryKey: ['pms-documents'] })
    },
  })

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="PMS"
        title="Documents"
        description="Content-addressed revisions with published pointers."
        actions={
          <button type="button" className="btn btn-primary" onClick={() => createDocument.mutate()}>
            <Plus className="w-4 h-4" />
            New Document
          </button>
        }
      />

      <div className="glass-card p-4 flex gap-3 items-center">
        <input
          className="flex-1 rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
          placeholder="Document title"
          value={newDocTitle}
          onChange={(event) => setNewDocTitle(event.target.value)}
        />
        <button
          type="button"
          className="btn btn-secondary"
          disabled={!newDocTitle}
          onClick={() => createDocument.mutate()}
        >
          Create
        </button>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.3fr_1fr]">
        <div className="glass-card p-5 space-y-3">
          <h2 className="text-sm font-semibold">Documents</h2>
          <div className="space-y-2 text-sm">
            {documents.map((doc) => (
              <button
                key={doc.document_id}
                type="button"
                className={`w-full text-left rounded-lg border px-3 py-2 ${
                  selectedDoc?.document_id === doc.document_id
                    ? 'border-[color:var(--osd-accent)] bg-[color:var(--osd-accentSoft)]'
                    : 'border-[color:var(--osd-border)]'
                }`}
                onClick={() => setSelectedDoc(doc)}
              >
                <div className="flex items-center justify-between">
                  <span>{doc.title}</span>
                  <span className="text-xs text-[color:var(--osd-muted)]">{doc.kind}</span>
                </div>
                <div className="text-xs text-[color:var(--osd-muted)]">{shortId(doc.document_id)}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="glass-card p-5 space-y-3">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-[color:var(--osd-muted)]" />
            <h2 className="text-sm font-semibold">Published View</h2>
          </div>
          {documentDetail?.revision ? (
            <>
              <div className="text-xs text-[color:var(--osd-muted)]">
                Revision {shortId(documentDetail.revision.revision_hash)} · {formatDateTime(documentDetail.revision.created_at)}
              </div>
              <pre className="text-xs rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/60 p-3 overflow-auto">
                {documentDetail.revision.content}
              </pre>
            </>
          ) : (
            <p className="text-sm text-[color:var(--osd-muted)]">Select a document to view content.</p>
          )}
        </div>
      </div>
    </div>
  )
}
