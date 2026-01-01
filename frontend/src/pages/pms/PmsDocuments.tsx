import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FileText, Plus } from 'lucide-react'
import PageHeader from '@/components/PageHeader'
import { pmsApi } from '../../api/pms'
import { useActor } from '../../contexts/ActorContext'
import type { PmsDocument } from '@/types/pms'
import { formatDateTime, shortId } from './pmsUtils'

export default function PmsDocuments() {
  const { currentActor } = useActor()
  const queryClient = useQueryClient()
  const [selectedDoc, setSelectedDoc] = useState<PmsDocument | null>(null)
  const [newDocTitle, setNewDocTitle] = useState('')
  const [newDocProjectId, setNewDocProjectId] = useState('')
  const [filterProjectId, setFilterProjectId] = useState('all')
  const [newRevisionContent, setNewRevisionContent] = useState('')
  const [showHistory, setShowHistory] = useState(false)

  const { data: projects = [] } = useQuery({
    queryKey: ['pms-projects', currentActor],
    queryFn: () => pmsApi.listProjects(currentActor),
  })

  useEffect(() => {
    if (!newDocProjectId && projects.length > 0) {
      setNewDocProjectId(projects[0].project_id)
    }
  }, [newDocProjectId, projects])

  const { data: documents = [] } = useQuery({
    queryKey: ['pms-documents', filterProjectId, currentActor],
    queryFn: () =>
      pmsApi.listDocuments(filterProjectId === 'all' ? undefined : filterProjectId, currentActor),
  })

  const { data: documentDetail } = useQuery({
    queryKey: ['pms-document', selectedDoc?.document_id, currentActor],
    queryFn: () =>
      pmsApi.getDocument(selectedDoc?.document_id as string, 'published', currentActor),
    enabled: !!selectedDoc,
  })

  const { data: documentHistory } = useQuery({
    queryKey: ['pms-document-history', selectedDoc?.document_id, currentActor],
    queryFn: () =>
      pmsApi.getDocument(selectedDoc?.document_id as string, 'history', currentActor),
    enabled: !!selectedDoc && showHistory,
  })

  const createDocument = useMutation({
    mutationFn: () =>
      pmsApi.createDocument(
        {
          project_id: newDocProjectId,
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

  const addRevision = useMutation({
    mutationFn: () =>
      pmsApi.addRevision(
        selectedDoc?.document_id as string,
        { content: newRevisionContent },
        currentActor,
      ),
    onSuccess: () => {
      setNewRevisionContent('')
      queryClient.invalidateQueries({ queryKey: ['pms-document', selectedDoc?.document_id] })
      queryClient.invalidateQueries({ queryKey: ['pms-document-history', selectedDoc?.document_id] })
      queryClient.invalidateQueries({ queryKey: ['pms-documents'] })
    },
  })

  const publishRevision = useMutation({
    mutationFn: (revisionHash: string) =>
      pmsApi.publishRevision(selectedDoc?.document_id as string, revisionHash, currentActor),
    onSuccess: (doc) => {
      setSelectedDoc((prev) =>
        prev ? { ...prev, published_revision_hash: doc.published_revision_hash } : prev,
      )
      queryClient.invalidateQueries({ queryKey: ['pms-document', selectedDoc?.document_id] })
      queryClient.invalidateQueries({ queryKey: ['pms-document-history', selectedDoc?.document_id] })
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
        <select
          className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
          value={newDocProjectId}
          onChange={(event) => setNewDocProjectId(event.target.value)}
        >
          {projects.map((project) => (
            <option key={project.project_id} value={project.project_id}>
              {project.name}
            </option>
          ))}
        </select>
        <input
          className="flex-1 rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
          placeholder="Document title"
          value={newDocTitle}
          onChange={(event) => setNewDocTitle(event.target.value)}
        />
        <button
          type="button"
          className="btn btn-secondary"
          disabled={!newDocTitle || !newDocProjectId}
          onClick={() => createDocument.mutate()}
        >
          Create
        </button>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.3fr_1fr]">
        <div className="glass-card p-5 space-y-3">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-sm font-semibold">Documents</h2>
            <select
              className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-xs"
              value={filterProjectId}
              onChange={(event) => setFilterProjectId(event.target.value)}
            >
              <option value="all">All projects</option>
              {projects.map((project) => (
                <option key={project.project_id} value={project.project_id}>
                  {project.name}
                </option>
              ))}
            </select>
          </div>
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
          {selectedDoc && (
            <div className="pt-4 border-t border-[color:var(--osd-border)] space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold">New Revision</h3>
                <button
                  type="button"
                  className="text-xs text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]"
                  onClick={() => setShowHistory((prev) => !prev)}
                >
                  {showHistory ? 'Hide History' : 'Show History'}
                </button>
              </div>
              <textarea
                className="w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-xs min-h-[120px]"
                placeholder="Draft revision content..."
                value={newRevisionContent}
                onChange={(event) => setNewRevisionContent(event.target.value)}
              />
              <button
                type="button"
                className="btn btn-secondary"
                disabled={!newRevisionContent || addRevision.isPending}
                onClick={() => addRevision.mutate()}
              >
                Add Revision
              </button>
              {showHistory && (
                <div className="space-y-2 text-xs">
                  {(documentHistory?.history ?? []).map((revision: any) => (
                    <div
                      key={revision.revision_hash}
                      className="flex items-center justify-between rounded-lg border border-[color:var(--osd-border)] px-3 py-2"
                    >
                      <div>
                        <div className="text-[color:var(--osd-text)]">
                          {shortId(revision.revision_hash)}
                        </div>
                        <div className="text-[color:var(--osd-muted)]">{formatDateTime(revision.created_at)}</div>
                      </div>
                      {selectedDoc.published_revision_hash === revision.revision_hash ? (
                        <span className="text-[0.6rem] uppercase tracking-wider text-emerald-300">
                          Published
                        </span>
                      ) : (
                        <button
                          type="button"
                          className="btn btn-secondary"
                          onClick={() => publishRevision.mutate(revision.revision_hash)}
                        >
                          Publish
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
