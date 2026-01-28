import { useEffect, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, X } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useActor } from '../contexts/ActorContext'
import { pmsApi } from '../api/pms'

const MIN_QUERY = 2

export default function GlobalSearch() {
  const navigate = useNavigate()
  const { currentActor } = useActor()
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  const { data, isFetching } = useQuery({
    queryKey: ['pms-search', currentActor, query],
    queryFn: () => pmsApi.search({ query, scope: currentActor }),
    enabled: query.trim().length >= MIN_QUERY,
    staleTime: 20 * 1000,
  })

  const results = data?.results ?? []

  useEffect(() => {
    const onClick = (event: MouseEvent) => {
      if (!containerRef.current?.contains(event.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', onClick)
    return () => document.removeEventListener('mousedown', onClick)
  }, [])

  return (
    <div className="relative w-full max-w-sm" ref={containerRef}>
      <div className="flex items-center gap-2 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2">
        <Search className="w-4 h-4 text-[color:var(--osd-muted)]" />
        <input
          className="w-full bg-transparent text-sm text-[color:var(--osd-text)] focus:outline-none"
          placeholder="Search projects, tasks, docs, meetings..."
          value={query}
          onChange={(event) => {
            setQuery(event.target.value)
            setOpen(true)
          }}
          onFocus={() => setOpen(true)}
        />
        {query && (
          <button
            type="button"
            className="text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]"
            onClick={() => setQuery('')}
            aria-label="Clear search"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {open && query.trim().length >= MIN_QUERY && (
        <div className="absolute z-50 mt-2 w-full rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] shadow-xl">
          <div className="max-h-72 overflow-y-auto p-2">
            {isFetching && (
              <div className="px-3 py-2 text-xs text-[color:var(--osd-muted)]">Searching...</div>
            )}
            {!isFetching && results.length === 0 && (
              <div className="px-3 py-2 text-xs text-[color:var(--osd-muted)]">No results.</div>
            )}
            {!isFetching &&
              results.map((result: any) => (
                <button
                  key={`${result.kind}-${result.entity_id ?? result.title}`}
                  type="button"
                  className="w-full text-left px-3 py-2 rounded-lg hover:bg-[color:var(--osd-surface)]/70 transition-colors"
                  onClick={() => {
                    if (result.route) {
                      navigate(result.route)
                    }
                    setOpen(false)
                  }}
                >
                  <div className="text-sm font-medium text-[color:var(--osd-text)]">{result.title}</div>
                  <div className="text-xs text-[color:var(--osd-muted)]">
                    {result.kind?.toUpperCase() || 'RESULT'} · {result.subtitle || result.project_name || '—'}
                  </div>
                </button>
              ))}
          </div>
        </div>
      )}
    </div>
  )
}
