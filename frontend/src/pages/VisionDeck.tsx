import { useEffect, useMemo, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { BookOpen, Compass, ExternalLink, RefreshCw } from 'lucide-react'

type VisionDoc = {
  slug: string
  title: string
  description: string
  path: string
  tags: string[]
}

const VISION_DOCS: VisionDoc[] = [
  {
    slug: 'future_meta',
    title: 'Future · Meta State',
    description: 'Speculative roadmap describing the Meta phase of the OS.',
    path: '/docs/future_meta.html',
    tags: ['meta', 'future'],
  },
  {
    slug: 'future_god',
    title: 'Future · GOD Mode',
    description: 'Ambitious blueprint for hyperscale orchestration.',
    path: '/docs/future_god.html',
    tags: ['hyperscale', 'automation'],
  },
  {
    slug: 'future_ultra',
    title: 'Future · Ultra Automation',
    description: 'Automation-first horizon lifted from the Tkinter planning docs.',
    path: '/docs/future_ultra.html',
    tags: ['automation'],
  },
  {
    slug: 'future_hyper',
    title: 'Future · Hyper Intelligence',
    description: 'Research memo that captures emergent intelligence scenarios.',
    path: '/docs/future_hyper.html',
    tags: ['research', 'intelligence'],
  },
  {
    slug: 'future_super',
    title: 'Future · Super Alignment',
    description: 'Narrative about super-aligned, multi-agent systems.',
    path: '/docs/future_super.html',
    tags: ['alignment'],
  },
  {
    slug: 'future_advanced',
    title: 'Future · Advanced Workforce',
    description: 'How the OS scales across advanced teams and domains.',
    path: '/docs/future_advanced.html',
    tags: ['workforce'],
  },
  {
    slug: 'future_core_os',
    title: 'Future · Core OS',
    description: 'The canonical Core OS plan preserved from the Tkinter days.',
    path: '/docs/future_core_os.html',
    tags: ['core', 'strategy'],
  },
]

export default function VisionDeck() {
  const [searchParams, setSearchParams] = useSearchParams()
  const slugParam = searchParams.get('doc') || VISION_DOCS[0].slug
  const activeDoc = VISION_DOCS.find((doc) => doc.slug === slugParam) ?? VISION_DOCS[0]

  const [content, setContent] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    const loadDoc = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await fetch(activeDoc.path, { signal: controller.signal })
        if (!response.ok) {
          throw new Error(`Failed to load ${activeDoc.path}`)
        }
        const html = await response.text()
        setContent(html)
      } catch (err) {
        if ((err as any).name === 'AbortError') return
        setError(err instanceof Error ? err.message : 'Failed to load document')
      } finally {
        setLoading(false)
      }
    }
    loadDoc()
    return () => controller.abort()
  }, [activeDoc.path])

  const stats = useMemo(() => {
    return {
      totalDocs: VISION_DOCS.length,
      categories: new Set(VISION_DOCS.flatMap((doc) => doc.tags)).size,
    }
  }, [])

  return (
    <div className="space-y-8 px-4 py-8">
      <section className="glass-card p-6 md:p-8">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="eyebrow-text inline-flex items-center gap-2">
              <Compass className="h-4 w-4" />
              Vision Deck
            </p>
            <h1 className="mt-2 text-3xl font-semibold text-white">Future System Narratives</h1>
            <p className="mt-3 max-w-2xl text-sm text-slate-300">
              These documents are the exact HTML exports from the Tkinter “Future” tabs. They now live inside the shared
              React codebase so browser and desktop builds stay in parity.
            </p>
          </div>
          <div className="grid gap-3 text-sm text-slate-200 sm:grid-cols-2">
            <Stat label="Decks" value={stats.totalDocs} />
            <Stat label="Tag Families" value={stats.categories} />
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[300px,1fr]">
        <aside className="glass-card p-4 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Select a deck</h2>
            <button
              className="btn-tonal text-xs"
              onClick={() => setSearchParams({ doc: activeDoc.slug })}
            >
              <RefreshCw className="mr-1 h-4 w-4" />
              Reload
            </button>
          </div>
          <div className="space-y-2 max-h-[540px] overflow-y-auto pr-1">
            {VISION_DOCS.map((doc) => (
              <button
                key={doc.slug}
                onClick={() => setSearchParams({ doc: doc.slug })}
                className={`w-full rounded-2xl border px-4 py-3 text-left text-sm transition ${
                  doc.slug === activeDoc.slug
                    ? 'border-white/20 bg-white/10 text-white'
                    : 'border-white/5 bg-white/0 text-slate-300 hover:border-white/15 hover:bg-white/5'
                }`}
              >
                <p className="font-semibold">{doc.title}</p>
                <p className="text-xs text-slate-400">{doc.description}</p>
                <div className="mt-2 flex flex-wrap gap-1 text-[0.6rem] uppercase tracking-[0.2em] text-slate-500">
                  {doc.tags.map((tag) => (
                    <span key={tag} className="rounded-full border border-white/10 px-2 py-0.5">
                      {tag}
                    </span>
                  ))}
                </div>
              </button>
            ))}
          </div>
        </aside>

        <article className="glass-card p-6 space-y-4">
          <header className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="eyebrow-text">{activeDoc.slug.replace('future_', '').toUpperCase()}</p>
              <h2 className="text-2xl font-semibold text-white">{activeDoc.title}</h2>
              <p className="text-sm text-slate-300">{activeDoc.description}</p>
            </div>
            <div className="flex flex-wrap gap-2 text-sm">
              <a
                href={activeDoc.path}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center rounded-xl border border-white/10 px-4 py-2 text-white hover:border-white/30"
              >
                <ExternalLink className="mr-2 h-4 w-4" />
                Open HTML
              </a>
              <Link to="/docs" className="inline-flex items-center rounded-xl border border-white/10 px-4 py-2 text-white hover:border-white/30">
                <BookOpen className="mr-2 h-4 w-4" />
                Docs Catalog
              </Link>
            </div>
          </header>
          <div className="rounded-2xl border border-white/10 bg-black/30 p-4 min-h-[300px] max-h-[70vh] overflow-y-auto">
            {loading && <p className="text-sm text-slate-400">Loading deck…</p>}
            {error && <p className="text-sm text-rose-300">{error}</p>}
            {!loading && !error && (
              <div className="prose prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: content }} />
            )}
          </div>
        </article>
      </section>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-white">
      <p className="text-xs uppercase tracking-[0.3em] text-slate-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </div>
  )
}
