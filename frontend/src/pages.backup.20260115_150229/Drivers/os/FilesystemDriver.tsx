import { useMemo, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { ArrowUp, Eye, EyeOff, FileText, Folder, Shield, RefreshCcw } from 'lucide-react'

import { toast } from '../../../utils/toast'
import {
  getFilesystemPolicy,
  updateFilesystemPolicy,
  listDirectory,
  getFileInfo,
  readFile,
  type DirectoryItem,
} from '@/api/filesystem'

function dirname(path: string): string {
  if (!path) return '/'
  if (path === '/') return '/'
  const normalized = path.replace(/\/+$/, '')
  const idx = normalized.lastIndexOf('/')
  if (idx <= 0) return '/'
  return normalized.slice(0, idx) || '/'
}

function isAdmin(): boolean {
  try {
    const raw = localStorage.getItem('user')
    if (!raw) return false
    const parsed = JSON.parse(raw)
    return Boolean(parsed?.is_admin)
  } catch {
    return false
  }
}

export default function FilesystemDriver() {
  const [path, setPath] = useState('/')
  const [showHidden, setShowHidden] = useState(false)
  const [selected, setSelected] = useState<DirectoryItem | null>(null)
  const [newRoot, setNewRoot] = useState('')

  const policyQuery = useQuery({
    queryKey: ['filesystem', 'policy'],
    queryFn: getFilesystemPolicy,
    refetchOnWindowFocus: false,
  })

  const listingQuery = useQuery({
    queryKey: ['filesystem', 'list', path, showHidden],
    queryFn: () =>
      listDirectory({
        path,
        show_hidden: showHidden,
        include_metadata: true,
        max_items: 2000,
      }),
    refetchOnWindowFocus: false,
  })

  const fileInfoQuery = useQuery({
    queryKey: ['filesystem', 'info', selected?.path],
    queryFn: () => getFileInfo(selected?.path || ''),
    enabled: Boolean(selected?.path),
    refetchOnWindowFocus: false,
  })

  const filePreviewQuery = useQuery({
    queryKey: ['filesystem', 'read', selected?.path],
    queryFn: () => readFile(selected?.path || '', 2000),
    enabled: Boolean(selected?.path && selected?.type === 'file'),
    refetchOnWindowFocus: false,
  })

  const updatePolicyMutation = useMutation({
    mutationFn: updateFilesystemPolicy,
    onSuccess: () => {
      toast.success('Filesystem policy updated')
      policyQuery.refetch()
      listingQuery.refetch()
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Failed to update policy')
    },
  })

  const allowedRoots = policyQuery.data?.allowed_roots ?? []
  const mode = policyQuery.data?.mode ?? 'read_only'

  const breadcrumbs = useMemo(() => {
    const parts = path.split('/').filter(Boolean)
    const crumbs: Array<{ label: string; value: string }> = [{ label: '/', value: '/' }]
    let acc = ''
    for (const p of parts) {
      acc += '/' + p
      crumbs.push({ label: p, value: acc })
    }
    return crumbs
  }, [path])

  const handleOpen = (item: DirectoryItem) => {
    setSelected(item)
    if (item.type === 'directory') {
      setPath(item.path)
    }
  }

  const handleGoUp = () => {
    setSelected(null)
    setPath(dirname(path))
  }

  const handleRefresh = () => {
    listingQuery.refetch()
    if (selected?.path) {
      fileInfoQuery.refetch()
      filePreviewQuery.refetch()
    }
  }

  const addAllowedRoot = () => {
    const trimmed = newRoot.trim()
    if (!trimmed) return
    const next = Array.from(new Set([...(policyQuery.data?.allowed_roots ?? []), trimmed]))
    updatePolicyMutation.mutate({ allowed_roots: next })
    setNewRoot('')
  }

  const removeAllowedRoot = (root: string) => {
    const next = (policyQuery.data?.allowed_roots ?? []).filter((r) => r !== root)
    updatePolicyMutation.mutate({ allowed_roots: next })
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[color:var(--osd-text)] flex items-center gap-2">
            <Folder className="w-6 h-6 text-[color:var(--osd-accent)]" />
            Filesystem Driver
          </h2>
          <p className="text-[color:var(--osd-muted)]">
            Permissioned file explorer (mirrors the <code className="font-mono">file:///</code> index view).
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setShowHidden((v) => !v)}
            className="inline-flex items-center gap-2 px-3 py-2 rounded-md border border-[color:var(--osd-border)] text-sm hover:bg-[color:var(--osd-surface)]/40"
          >
            {showHidden ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            {showHidden ? 'Hide hidden' : 'Show hidden'}
          </button>
          <button
            type="button"
            onClick={handleRefresh}
            className="inline-flex items-center gap-2 px-3 py-2 rounded-md border border-[color:var(--osd-border)] text-sm hover:bg-[color:var(--osd-surface)]/40"
          >
            <RefreshCcw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </header>

      <section className="glass-card p-5">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div className="flex flex-wrap items-center gap-2">
            {breadcrumbs.map((c) => (
              <button
                key={c.value}
                type="button"
                onClick={() => {
                  setSelected(null)
                  setPath(c.value)
                }}
                className="text-sm font-mono px-2 py-1 rounded-md border border-[color:var(--osd-border)] hover:bg-[color:var(--osd-surface)]/40"
              >
                {c.label}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleGoUp}
              disabled={path === '/'}
              className="inline-flex items-center gap-2 px-3 py-2 rounded-md border border-[color:var(--osd-border)] text-sm hover:bg-[color:var(--osd-surface)]/40 disabled:opacity-50"
            >
              <ArrowUp className="w-4 h-4" />
              Up
            </button>
            <input
              value={path}
              onChange={(e) => setPath(e.target.value)}
              className="w-full md:w-[36rem] rounded-lg bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] px-3 py-2 text-sm font-mono"
              placeholder="/"
            />
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <section className="glass-card p-5 xl:col-span-2">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-[color:var(--osd-text)]">Directory listing</h3>
            {listingQuery.isFetching ? (
              <span className="text-xs text-[color:var(--osd-muted)]">Loading…</span>
            ) : (
              <span className="text-xs text-[color:var(--osd-muted)]">
                {listingQuery.data?.total_items ?? 0} items
              </span>
            )}
          </div>

          {listingQuery.isError ? (
            <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-sm text-red-200">
              {(listingQuery.error as Error).message}
            </div>
          ) : listingQuery.data?.items?.length ? (
            <div className="max-h-[36rem] overflow-auto divide-y divide-[color:var(--osd-border)]">
              {listingQuery.data.items.map((item) => (
                <button
                  key={item.path}
                  type="button"
                  onClick={() => handleOpen(item)}
                  className={`w-full flex items-center justify-between gap-3 px-2 py-2 text-left hover:bg-[color:var(--osd-surface)]/40 ${
                    selected?.path === item.path ? 'bg-[color:var(--osd-surface)]/50' : ''
                  }`}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    {item.type === 'directory' ? (
                      <Folder className="w-4 h-4 text-[color:var(--osd-accent)] shrink-0" />
                    ) : (
                      <FileText className="w-4 h-4 text-[color:var(--osd-muted)] shrink-0" />
                    )}
                    <span className="truncate text-sm text-[color:var(--osd-text)]">{item.name}</span>
                    {item.is_hidden ? (
                      <span className="text-[0.65rem] px-2 py-0.5 rounded-full border border-[color:var(--osd-border)] text-[color:var(--osd-muted)]">
                        hidden
                      </span>
                    ) : null}
                  </div>
                  <div className="flex items-center gap-3 text-xs text-[color:var(--osd-muted)] shrink-0">
                    {typeof item.size === 'number' && item.type === 'file' ? <span>{item.size} B</span> : null}
                    {item.modified ? <span>{new Date(item.modified).toLocaleString()}</span> : null}
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <p className="text-sm text-[color:var(--osd-muted)]">No items.</p>
          )}
        </section>

        <aside className="space-y-6">
          <div className="glass-card p-5 space-y-3">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-[color:var(--osd-accent)]" />
              <h3 className="text-sm font-semibold text-[color:var(--osd-text)]">Filesystem Policy</h3>
            </div>
            {policyQuery.isError ? (
              <p className="text-sm text-red-200">{(policyQuery.error as Error).message}</p>
            ) : (
              <>
                <div className="text-xs text-[color:var(--osd-muted)]">
                  Mode: <span className="font-mono text-[color:var(--osd-text)]">{mode}</span>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)] mb-2">
                    Allowed roots
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {allowedRoots.length === 0 ? (
                      <span className="text-sm text-[color:var(--osd-muted)]">Using safe default (repo root only)</span>
                    ) : (
                      allowedRoots.map((root) => (
                        <span
                          key={root}
                          className="inline-flex items-center gap-2 text-xs font-mono px-2 py-1 rounded-full border border-[color:var(--osd-border)]"
                        >
                          {root}
                          {isAdmin() ? (
                            <button
                              type="button"
                              onClick={() => removeAllowedRoot(root)}
                              className="text-[color:var(--osd-muted)] hover:text-red-300"
                            >
                              ×
                            </button>
                          ) : null}
                        </span>
                      ))
                    )}
                  </div>
                </div>

                {isAdmin() ? (
                  <div className="space-y-2">
                    <div className="flex gap-2">
                      <input
                        value={newRoot}
                        onChange={(e) => setNewRoot(e.target.value)}
                        placeholder="Add allowed root (e.g. /, /Users/chris)"
                        className="flex-1 rounded-lg bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] px-3 py-2 text-xs font-mono"
                      />
                      <button
                        type="button"
                        onClick={addAllowedRoot}
                        disabled={updatePolicyMutation.isPending}
                        className="px-3 py-2 rounded-md bg-[color:var(--osd-accent)] text-white text-xs font-semibold disabled:opacity-60"
                      >
                        Add
                      </button>
                    </div>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => updatePolicyMutation.mutate({ mode: 'read_only' })}
                        disabled={updatePolicyMutation.isPending}
                        className="flex-1 px-3 py-2 rounded-md border border-[color:var(--osd-border)] text-xs hover:bg-[color:var(--osd-surface)]/40"
                      >
                        Set read_only
                      </button>
                      <button
                        type="button"
                        onClick={() => updatePolicyMutation.mutate({ mode: 'read_write' })}
                        disabled={updatePolicyMutation.isPending}
                        className="flex-1 px-3 py-2 rounded-md border border-[color:var(--osd-border)] text-xs hover:bg-[color:var(--osd-surface)]/40"
                      >
                        Set read_write
                      </button>
                    </div>
                    <p className="text-xs text-[color:var(--osd-muted)]">
                      Tip: to replicate your screenshot, add <code className="font-mono">/</code> as an allowed root.
                    </p>
                  </div>
                ) : (
                  <p className="text-xs text-[color:var(--osd-muted)]">
                    Admin required to edit policy.
                  </p>
                )}
              </>
            )}
          </div>

          <div className="glass-card p-5 space-y-3">
            <h3 className="text-sm font-semibold text-[color:var(--osd-text)]">Selection</h3>
            {!selected ? (
              <p className="text-sm text-[color:var(--osd-muted)]">Select a file or folder.</p>
            ) : (
              <>
                <div className="text-xs text-[color:var(--osd-muted)]">Path</div>
                <div className="text-xs font-mono break-all text-[color:var(--osd-text)]">{selected.path}</div>

                {fileInfoQuery.isError ? (
                  <p className="text-sm text-red-200">{(fileInfoQuery.error as Error).message}</p>
                ) : fileInfoQuery.data ? (
                  <pre className="text-xs rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40 p-3 overflow-auto max-h-60">
                    {JSON.stringify(fileInfoQuery.data, null, 2)}
                  </pre>
                ) : null}

                {selected.type === 'file' ? (
                  filePreviewQuery.isError ? (
                    <p className="text-sm text-red-200">{(filePreviewQuery.error as Error).message}</p>
                  ) : filePreviewQuery.data ? (
                    <pre className="text-xs rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40 p-3 overflow-auto max-h-80 whitespace-pre-wrap">
                      {filePreviewQuery.data.content}
                      {filePreviewQuery.data.truncated ? '\n\n[truncated]' : ''}
                    </pre>
                  ) : (
                    <p className="text-sm text-[color:var(--osd-muted)]">Loading preview…</p>
                  )
                ) : null}
              </>
            )}
          </div>
        </aside>
      </div>
    </div>
  )
}



