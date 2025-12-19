import { useState, useEffect } from 'react'
import { GitBranch, GitCompare, History, Eye } from 'lucide-react'

interface VersionInfo {
  version_id: string
  document_id: string
  version_number: number
  created_at: string
  created_by?: string
  file_size: number
  checksum: string
  description?: string
}

interface DiffResult {
  version_a: VersionInfo
  version_b: VersionInfo
  diff_type: string
  changes: any
  unified_diff?: string
  html_diff?: string
}

interface VersionControlProps {
  documentId: string
  hidden?: boolean
}

export default function VersionControl({ documentId, hidden = false }: VersionControlProps) {
  const [versions, setVersions] = useState<VersionInfo[]>([])
  const [selectedVersions, setSelectedVersions] = useState<number[]>([])
  const [diffResult, setDiffResult] = useState<DiffResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [showDiff, setShowDiff] = useState(false)

  useEffect(() => {
    loadVersions()
  }, [documentId])

  const loadVersions = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`/api/versions/documents/${documentId}/versions`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setVersions(data)
      }
    } catch (error) {
      console.error('Failed to load versions:', error)
    }
  }

  const createVersion = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`/api/versions/documents/${documentId}/versions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description: 'Manual snapshot' }),
      })
      if (response.ok) {
        await loadVersions()
      }
    } catch (error) {
      console.error('Failed to create version:', error)
    } finally {
      setLoading(false)
    }
  }

  const compareVersions = async () => {
    if (selectedVersions.length !== 2) return

    setLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      const [v1, v2] = selectedVersions.sort((a, b) => a - b)
      const response = await fetch(
        `/api/versions/documents/${documentId}/versions/compare?version_a=${v1}&version_b=${v2}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )
      if (response.ok) {
        const data = await response.json()
        setDiffResult(data)
        setShowDiff(true)
      }
    } catch (error) {
      console.error('Failed to compare versions:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleVersion = (versionNumber: number) => {
    setSelectedVersions((prev) => {
      if (prev.includes(versionNumber)) {
        return prev.filter((v) => v !== versionNumber)
      } else if (prev.length < 2) {
        return [...prev, versionNumber]
      } else {
        return [versionNumber]
      }
    })
  }

  if (hidden && !showDiff) {
    return (
      <button
        onClick={() => setShowDiff(true)}
        className="fixed bottom-20 right-6 px-4 py-2 bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] rounded-lg hover:bg-[color:var(--osd-accentSoft)] flex items-center gap-2"
      >
        <GitBranch className="w-4 h-4" />
        Version Control
      </button>
    )
  }

  return (
    <div className="glass-content p-6 rounded-lg">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <GitBranch className="w-5 h-5" />
          Version Control
        </h3>
        <div className="flex gap-2">
          <button
            onClick={createVersion}
            disabled={loading}
            className="px-3 py-1 text-sm bg-[color:var(--osd-accent)] text-white rounded hover:opacity-90 disabled:opacity-50"
          >
            Create Snapshot
          </button>
          {selectedVersions.length === 2 && (
            <button
              onClick={compareVersions}
              disabled={loading}
              className="px-3 py-1 text-sm bg-[color:var(--osd-accentPurple)] text-white rounded hover:opacity-90 disabled:opacity-50 flex items-center gap-1"
            >
              <GitCompare className="w-4 h-4" />
              Compare
            </button>
          )}
        </div>
      </div>

      {versions.length === 0 ? (
        <div className="text-center py-8 text-[color:var(--osd-muted)]">
          No versions yet. Create a snapshot to start tracking changes.
        </div>
      ) : (
        <div className="space-y-2">
          {versions.map((version) => (
            <div
              key={version.version_id}
              onClick={() => toggleVersion(version.version_number)}
              className={`p-3 rounded-lg cursor-pointer transition-colors ${
                selectedVersions.includes(version.version_number)
                  ? 'bg-[color:var(--osd-accentSoft)] border-2 border-[color:var(--osd-accent)]'
                  : 'bg-[color:var(--osd-surface)] hover:bg-[color:var(--osd-accentSoft)] border border-[color:var(--osd-border)]'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <History className="w-4 h-4 text-[color:var(--osd-muted)]" />
                  <span className="font-medium">Version {version.version_number}</span>
                  {selectedVersions.includes(version.version_number) && (
                    <span className="text-xs bg-[color:var(--osd-accent)] text-white px-2 py-0.5 rounded">
                      Selected
                    </span>
                  )}
                </div>
                <span className="text-xs text-[color:var(--osd-muted)]">
                  {new Date(version.created_at).toLocaleString()}
                </span>
              </div>
              {version.description && (
                <p className="text-sm text-[color:var(--osd-muted)] mt-1">{version.description}</p>
              )}
              <div className="text-xs text-[color:var(--osd-muted)] mt-1">
                {version.created_by && `by ${version.created_by} • `}
                {(version.file_size / 1024).toFixed(2)} KB
              </div>
            </div>
          ))}
        </div>
      )}

      {showDiff && diffResult && (
        <div className="mt-6 border-t border-[color:var(--osd-border)] pt-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold flex items-center gap-2">
              <Eye className="w-4 h-4" />
              Diff: v{diffResult.version_a.version_number} → v{diffResult.version_b.version_number}
            </h4>
            <button
              onClick={() => setShowDiff(false)}
              className="text-sm text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]"
            >
              Close
            </button>
          </div>
          {diffResult.diff_type === 'text' && diffResult.html_diff && (
            <div
              className="bg-[color:var(--osd-surface)] p-4 rounded-lg overflow-auto max-h-96"
              dangerouslySetInnerHTML={{ __html: diffResult.html_diff }}
            />
          )}
          {diffResult.diff_type === 'text' && diffResult.unified_diff && (
            <pre className="bg-[color:var(--osd-surface)] p-4 rounded-lg overflow-auto max-h-96 text-xs">
              {diffResult.unified_diff}
            </pre>
          )}
          {diffResult.diff_type === 'binary' && (
            <div className="text-sm text-[color:var(--osd-muted)]">
              Binary files differ. Size: {diffResult.changes.size_a} → {diffResult.changes.size_b} bytes
            </div>
          )}
        </div>
      )}
    </div>
  )
}
