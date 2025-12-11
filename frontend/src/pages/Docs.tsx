import { useMemo, useState } from 'react'
import { FileText, Search, ArrowUpRight, ExternalLink } from 'lucide-react'
import { Link } from 'react-router-dom'
import { docManifest, parityMeta, sourceLabel, type DocParity } from '../data/docManifest'
import { futureTierDocs, legacyDocGroups } from '../data/legacyMaps'

const resolveHtmlHref = (path: string, explicitHref?: string) => {
  if (explicitHref) return explicitHref
  if (path.includes('.')) {
    return `/docs/${path}`
  }
  return `/docs/${path}.html`
}

const categorySequence = [
  {
    label: 'Core System',
    complexity: 'Foundation',
    description: 'Dashboards, tasks, projects, and landing pages that ground every workflow.',
  },
  {
    label: 'Operations',
    complexity: 'Platform',
    description: 'Billing, settings, and orchestration controls shared between desktop + web.',
  },
  {
    label: 'Intelligence',
    complexity: 'AI/ML',
    description: 'Research, NAS, and AI cockpit tooling layered on top of the system surfaces.',
  },
  {
    label: 'Vision Deck',
    complexity: 'Future',
    description: 'Foresight decks arranged from advanced → meta horizons for roadmap planning.',
  },
  {
    label: 'Engineering Notes',
    complexity: 'Specs',
    description: 'Migration, deployment, and compliance specs that wire the stack together.',
  },
  {
    label: 'Legacy Views',
    complexity: 'Parity',
    description: 'Tkinter + HTML mirrors used to validate parity and cross-check regressions.',
  },
]

const categoryRank = categorySequence.reduce<Record<string, number>>((acc, stage, index) => {
  acc[stage.label] = index
  return acc
}, {})

const parityPriority: Record<DocParity, number> = {
  full: 0,
  partial: 1,
  legacy: 2,
}

export default function Docs() {
  const [query, setQuery] = useState('')

  const stats = useMemo(() => {
    const total = docManifest.length
    const categories = new Set(docManifest.map((doc) => doc.category)).size
    const futures = docManifest.filter((doc) => doc.category === 'Vision Deck').length
    const parity = docManifest.reduce(
      (acc, doc) => {
        acc[doc.parity] += 1
        return acc
      },
      { full: 0, partial: 0, legacy: 0 },
    )
    return { total, categories, futures, parity }
  }, [])

  const filteredDocs = useMemo(() => {
    const trimmed = query.trim().toLowerCase()
    if (!trimmed) return docManifest
    return docManifest.filter((doc) => {
      const haystack = [doc.title, doc.description, doc.category, ...doc.tags, sourceLabel[doc.source]]
        .join(' ')
        .toLowerCase()
      return haystack.includes(trimmed)
    })
  }, [query])

  const groupedDocs = useMemo(() => {
    const sections: Record<string, typeof docManifest> = {}
    filteredDocs.forEach((doc) => {
      if (!sections[doc.category]) {
        sections[doc.category] = []
      }
      sections[doc.category].push(doc)
    })
    const order = Object.keys(sections).sort((a, b) => {
      const rankDiff = (categoryRank[a] ?? categorySequence.length) - (categoryRank[b] ?? categorySequence.length)
      if (rankDiff !== 0) return rankDiff
      return a.localeCompare(b)
    })
    order.forEach((category) => {
      const docs = sections[category]
      docs.sort((a, b) => {
        const parityDiff = (parityPriority[a.parity] ?? 99) - (parityPriority[b.parity] ?? 99)
        if (parityDiff !== 0) return parityDiff
        return a.title.localeCompare(b.title)
      })
    })
    return { order, sections }
  }, [filteredDocs])

  return (
    <div className="px-4 py-6 sm:px-0 space-y-8 text-slate-100">
      <section className="glass-card relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-indigo-500/20 via-transparent to-purple-500/10" />
        <div className="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="eyebrow-text">Documentation Hub</p>
            <h1 className="mt-2 text-3xl font-semibold text-white">Preserved HTML + Tkinter Pages</h1>
            <p className="mt-3 text-sm text-slate-300 max-w-2xl">
              Every Tkinter-era page stays online. View the original HTML, launch the React equivalent, and
              track which surfaces still need parity polish.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-4 text-center text-sm sm:grid-cols-4">
            <Stat label="Pages" value={stats.total} />
            <Stat label="Categories" value={stats.categories} />
            <Stat label="Vision Deck" value={stats.futures} />
            <div className="rounded-2xl border border-white/15 bg-white/5 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Parity</p>
              <p className="mt-1 text-2xl font-semibold text-white">
                {stats.parity.full}/{stats.total}
              </p>
              <p className="text-[0.65rem] uppercase tracking-[0.2em] text-slate-400">
                {stats.parity.partial} partial · {stats.parity.legacy} legacy
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="glass-card space-y-4">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-white">Sequence & Complexity</h2>
            <p className="text-sm text-slate-300">
              Follow the stack from foundational surfaces down to advanced futures.
            </p>
          </div>
          <span className="pill-muted">Top-to-bottom execution order</span>
        </div>
        <div className="space-y-3">
          {categorySequence.map((stage, index) => (
            <div
              key={stage.label}
              className="flex items-start gap-4 rounded-2xl border border-white/10 bg-white/5 px-4 py-3"
            >
              <div className="text-2xl font-mono text-slate-300">{String(index + 1).padStart(2, '0')}</div>
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-slate-400">{stage.complexity}</p>
                <p className="text-lg font-semibold text-white">{stage.label}</p>
                <p className="text-sm text-slate-300">{stage.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="glass-card space-y-4">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-white">Browse the archive</h2>
            <p className="text-sm text-slate-300">
              Search titles, tags, or categories. Entries pull from `/docs`, `/ui`, or FastAPI spec feeds.
            </p>
          </div>
          <span className="pill-muted">Synced nightly from repo + FastAPI</span>
        </div>
        <div className="relative">
          <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search documentation..."
            className="w-full rounded-2xl border border-white/10 bg-white/5 py-3 pl-11 pr-4 text-sm text-white placeholder:text-slate-400 focus:border-primary-500 focus:outline-none"
          />
        </div>
      </section>

      {filteredDocs.length === 0 && (
        <div className="glass-card text-center text-sm text-slate-300">
          No documentation matched “{query}”. Try a different keyword or clear the filter.
        </div>
      )}

      {groupedDocs.order.map((category) => {
        const docs = groupedDocs.sections[category]
        const stageMeta = categorySequence.find((stage) => stage.label === category)
        return (
          <section key={category} className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="eyebrow-text">
                  {stageMeta ? `${stageMeta.complexity} · ${category}` : category}
                </p>
                <h3 className="text-xl font-semibold text-white">
                  {stageMeta?.description ?? 'Operational references'}
                </h3>
              </div>
              <span className="pill-muted">{docs.length} pages</span>
            </div>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {docs.map((doc) => {
                const htmlHref = resolveHtmlHref(doc.path, doc.href)
                const parity = parityMeta[doc.parity]
                return (
                  <article
                    key={doc.path}
                    className="glass-card group relative overflow-hidden transition hover:-translate-y-1 hover:border-white/30"
                  >
                    <div className={`pointer-events-none absolute inset-0 bg-gradient-to-br ${doc.accent}`} />
                    <div className="relative">
                      <div className="flex items-center justify-between text-xs uppercase tracking-[0.2em] text-slate-300">
                        <span>{sourceLabel[doc.source]}</span>
                        <span className={`rounded-full border px-2 py-0.5 text-[0.65rem] ${parity.chipClass}`}>
                          {parity.label}
                        </span>
                      </div>
                      <h4 className="mt-3 text-lg font-semibold text-white">{doc.title}</h4>
                      <p className="mt-2 text-sm text-slate-300">{doc.description}</p>
                      <div className="mt-4 flex flex-wrap gap-2">
                        {doc.tags.map((tag) => (
                          <span
                            key={tag}
                            className="rounded-full border border-white/10 bg-white/5 px-2 py-1 text-xs font-medium uppercase tracking-widest text-slate-200"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                      <div className="mt-5 flex flex-wrap items-center gap-2">
                        {doc.reactRoute ? (
                          <Link
                            to={doc.reactRoute}
                            className="inline-flex items-center gap-2 rounded-xl border border-white/20 bg-white/5 px-3 py-1.5 text-xs font-semibold text-white hover:border-white/40"
                          >
                            <ArrowUpRight className="h-3.5 w-3.5" />
                            {doc.reactLabel || 'React Surface'}
                          </Link>
                        ) : (
                          <span className="text-xs italic text-slate-400">React view pending</span>
                        )}
                        <a
                          href={htmlHref}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-2 rounded-xl border border-white/20 bg-white/5 px-3 py-1.5 text-xs font-semibold text-white hover:border-white/40"
                        >
                          <ExternalLink className="h-3.5 w-3.5" />
                          HTML Snapshot
                        </a>
                        <Link
                          to={`/docs/${doc.path}`}
                          className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-semibold text-white hover:border-white/30"
                        >
                          <FileText className="h-3.5 w-3.5" />
                          In-app view
                        </Link>
                      </div>
                    </div>
                  </article>
                )
              })}
            </div>
          </section>
        )
      })}

      <section className="glass-card space-y-6">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-white">AI OS page map</h2>
            <p className="text-sm text-slate-300">
              Mirrors the Tkinter dropdown that launched Markdown/PDF specs from the AI OS cockpit.
            </p>
          </div>
          <span className="pill-muted">Pulled from /documentation</span>
        </div>
        <div className="space-y-6">
          {legacyDocGroups.map((group) => (
            <div key={group.title} className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="eyebrow-text">{group.title}</p>
                  <p className="text-sm text-slate-300">{group.summary}</p>
                </div>
                <span className="pill-muted">{group.items.length} references</span>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                {group.items.map((item) => (
                  <article
                    key={item.label}
                    className="rounded-2xl border border-white/10 bg-white/5 p-4 transition hover:border-white/30"
                  >
                    <div className="flex items-center justify-between text-xs uppercase tracking-[0.3em] text-slate-400">
                      <span>{group.title}</span>
                      <span className="rounded-full border border-white/15 px-2 py-0.5 text-[0.65rem] text-slate-300">
                        {item.kind}
                      </span>
                    </div>
                    <h4 className="mt-2 text-lg font-semibold text-white">{item.label}</h4>
                    <p className="mt-1 text-sm text-slate-300">{item.description}</p>
                    <div className="mt-4 flex flex-wrap gap-2">
                      <a
                        href={item.href}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-2 rounded-xl border border-white/15 bg-white/5 px-3 py-1.5 text-xs font-semibold text-white hover:border-white/40"
                      >
                        <ExternalLink className="h-3.5 w-3.5" />
                        Open
                      </a>
                    </div>
                  </article>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="glass-card space-y-4">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-white">Future tier decks</h2>
            <p className="text-sm text-slate-300">
              Every Tkinter future horizon now links to both its React canvas and preserved HTML.
            </p>
          </div>
          <span className="pill-muted">Parity with `_build_future_feature_tier_doc_map`</span>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          {futureTierDocs.map((tier) => (
            <article key={tier.slug} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Future Tier</p>
              <h3 className="mt-2 text-xl font-semibold text-white">{tier.label}</h3>
              <p className="text-sm text-slate-300">{tier.summary}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                <Link
                  to={`/future/${tier.slug}`}
                  className="inline-flex items-center gap-2 rounded-xl border border-white/15 bg-white/5 px-3 py-1.5 text-xs font-semibold text-white hover:border-white/40"
                >
                  <ArrowUpRight className="h-3.5 w-3.5" />
                  React canvas
                </Link>
                <a
                  href={tier.htmlHref}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 rounded-xl border border-white/15 bg-white/5 px-3 py-1.5 text-xs font-semibold text-white hover:border-white/40"
                >
                  <ExternalLink className="h-3.5 w-3.5" />
                  Legacy HTML
                </a>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="glass-card flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-4">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
            <FileText className="h-6 w-6 text-slate-200" />
          </div>
          <div>
            <h4 className="text-lg font-semibold text-white">Need the raw HTML?</h4>
            <p className="text-sm text-slate-300">
              Use the shortcut buttons above or open <code className="rounded bg-white/10 px-2 py-0.5">/docs/**</code> directly.
              The React clients embed the same files to keep Tkinter + web mirrored.
            </p>
          </div>
        </div>
        <a
          href="/docs/index.html"
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-500 px-5 py-3 text-sm font-semibold shadow-lg shadow-blue-500/20"
        >
          <FileText className="h-4 w-4" />
          Open index.html
          <ArrowUpRight className="h-4 w-4" />
        </a>
      </section>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-2xl border border-white/15 bg-white/5 px-4 py-3">
      <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-white">{value}</p>
    </div>
  )
}
