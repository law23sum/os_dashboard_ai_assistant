import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, ArrowUpRight, ExternalLink } from 'lucide-react'
import { getDocEntry, parityMeta, sourceLabel } from '../data/docManifest'

interface DocumentationPageProps {
  page?: string
}

const resolveHtmlHref = (slug: string, explicit?: string) => {
  if (explicit) return explicit
  if (slug.includes('.')) return `/docs/${slug}`
  return `/docs/${slug}.html`
}

export default function Documentation({ page: propPage }: DocumentationPageProps) {
  const { page: paramPage } = useParams<{ page?: string }>()
  const pageName = propPage || paramPage || 'index'
  const entry = getDocEntry(pageName)
  const htmlHref = resolveHtmlHref(pageName, entry?.href)

  const [content, setContent] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadPage = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await fetch(htmlHref)
        if (!response.ok) {
          throw new Error(`Failed to load ${htmlHref}`)
        }
        const text = await response.text()
        setContent(text)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load documentation')
      } finally {
        setLoading(false)
      }
    }
    loadPage()
  }, [htmlHref])

  const parity = entry ? parityMeta[entry.parity] : null

  return (
    <div className="space-y-6">
      <div className="glass-card p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="eyebrow-text">Documentation</p>
            <h1 className="text-3xl font-semibold text-white">{entry?.title ?? pageName}</h1>
            <p className="mt-2 text-sm text-slate-300">
              {entry?.description ?? 'Legacy HTML preserved from the Tkinter era.'}
            </p>
          </div>
          <div className="flex flex-wrap gap-2 text-xs">
            {entry && (
              <span className="rounded-full border border-white/20 px-3 py-1 text-slate-200">
                {sourceLabel[entry.source]}
              </span>
            )}
            {parity && (
              <span className={`rounded-full border px-3 py-1 text-slate-100 ${parity.chipClass}`}>
                {parity.label}
              </span>
            )}
          </div>
        </div>
        <div className="mt-4 flex flex-wrap gap-3 text-sm">
          <Link
            to="/docs"
            className="inline-flex items-center rounded-xl border border-white/10 px-4 py-2 text-white hover:border-white/30"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to list
          </Link>
          <a
            href={htmlHref}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center rounded-xl border border-white/10 px-4 py-2 text-white hover:border-white/30"
          >
            <ExternalLink className="mr-2 h-4 w-4" />
            Open HTML
          </a>
          {entry?.reactRoute && (
            <Link
              to={entry.reactRoute}
              className="inline-flex items-center rounded-xl bg-gradient-to-r from-blue-500 to-indigo-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-blue-500/20"
            >
              <ArrowUpRight className="mr-2 h-4 w-4" />
              {entry.reactLabel || 'Open React Surface'}
            </Link>
          )}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-white">Legacy HTML</h2>
          <p className="text-sm text-slate-300">Direct render of {htmlHref}.</p>
          <div className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-4">
            {loading && <p className="text-sm text-slate-400">Loading legacy HTML…</p>}
            {error && (
              <p className="text-sm text-rose-300">
                {error}. Confirm the file exists under <code>/docs/</code>.
              </p>
            )}
            {!loading && !error && (
              <div className="prose prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: content }} />
            )}
          </div>
        </div>

        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-white">React Equivalent</h2>
          <p className="text-sm text-slate-300">Embeds the modern route so you can confirm parity at a glance.</p>
          <div className="mt-4 rounded-2xl border border-white/10 bg-black/30">
            {entry?.reactRoute ? (
              <iframe src={entry.reactRoute} title="React Preview" className="h-[600px] w-full rounded-2xl border-0" />
            ) : (
              <div className="p-6 text-sm text-slate-300">
                No React route wired yet. Track this item in <Link className="text-blue-300 underline" to="/docs/tk_to_react_mapping.md">Tk → React Mapping</Link>.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
