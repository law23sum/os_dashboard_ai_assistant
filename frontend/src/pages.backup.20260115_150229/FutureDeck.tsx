import { useMemo } from 'react'
import { useParams, Link, Navigate } from 'react-router-dom'
import { Sparkles, ArrowLeft, ArrowUpRight, ExternalLink } from 'lucide-react'
import { getFutureDeck, futureDecks } from '../data/futureDecks'

export default function FutureDeck() {
  const { slug } = useParams<{ slug: string }>()
  const deck = getFutureDeck(slug)

  const suggested = useMemo(() => Object.values(futureDecks), [])

  if (!deck) {
    const first = suggested[0]
    return <Navigate to={`/future/${first.slug}`} replace />
  }

  return (
    <div className="space-y-8 px-4 py-8 text-[color:var(--osd-text)]">
      <header className="glass-card relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-r from-indigo-500/10 via-transparent to-purple-500/10" />
        <div className="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div
              className="inline-flex items-center gap-2 rounded-full px-4 py-1 text-xs font-semibold uppercase tracking-[0.3em]"
              style={{ backgroundColor: deck.badgeColor, color: '#0f172a' }}
            >
              <Sparkles className="h-4 w-4" />
              {deck.badge}
            </div>
            <h1 className="mt-4 text-3xl font-bold">{deck.heroTitle}</h1>
            <p className="mt-2 max-w-3xl text-sm text-slate-300">{deck.description}</p>
          </div>
          <Link
            to="/docs"
            className="inline-flex items-center rounded-full border border-white/10 px-5 py-3 text-sm text-white hover:border-white/30"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Docs Hub
          </Link>
        </div>
      </header>

      <section className="grid gap-6 lg:grid-cols-[1.7fr,1fr]">
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-white">Feature Backlog</h2>
          <p className="text-sm text-slate-300">Mirrors the preserved HTML backlog for this future envelope.</p>
          <div className="mt-4 space-y-4">
            {deck.backlog.map((item) => (
              <article
                key={item.code}
                className="rounded-2xl border border-white/10 bg-white/5 p-4 transition hover:border-white/30"
              >
                <p className="text-xs uppercase tracking-[0.3em] text-slate-400">{item.code}</p>
                <div className="mt-1 flex flex-wrap items-center justify-between gap-2">
                  <h3 className="text-lg font-semibold text-white">{item.title}</h3>
                  <span className="rounded-full border border-white/10 px-3 py-1 text-xs text-amber-200">
                    {item.budget}
                  </span>
                </div>
                <p className="mt-2 text-sm text-slate-300">{item.summary}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="space-y-6">
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-white">Implementation Canvas</h2>
            <p className="text-sm text-slate-300">Use these prompts before writing code.</p>
            <ul className="mt-4 space-y-3">
              {deck.checklist.map((item) => (
                <li
                  key={item}
                  className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200"
                >
                  <span className="inline-flex h-5 w-5 items-center justify-center rounded-full border border-white/20 text-xs text-slate-300">
                    □
                  </span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-white">Notes</h2>
            <p className="text-sm text-slate-300">Drop architectural sketches, launch criteria, or research references.</p>
            <ul className="mt-4 space-y-3">
              {deck.notes.map((item) => (
                <li key={item} className="rounded-2xl border border-dashed border-white/20 bg-black/20 px-4 py-3 text-sm text-slate-300">
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section className="glass-card p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="eyebrow-text">Other Envelopes</p>
            <h3 className="text-xl font-semibold text-white">Explore additional horizons</h3>
            <p className="text-sm text-slate-300">Every entry in the Tkinter docs now has a React twin.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {suggested.map((item) => (
              <Link
                key={item.slug}
                to={`/future/${item.slug}`}
                className={`rounded-full border px-3 py-1 text-xs font-semibold ${
                  item.slug === deck.slug ? 'border-white/40 bg-white/10 text-white' : 'border-white/10 text-slate-300 hover:border-white/30'
                }`}
              >
                {item.badge}
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="glass-card p-6">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h3 className="text-lg font-semibold text-white">View preserved HTML</h3>
            <p className="text-sm text-slate-300">Open the exact Tkinter-era document for audit or inspiration.</p>
          </div>
          <a
            href={`/docs/future_${deck.slug}.html`}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-500 px-4 py-2 text-sm font-semibold text-white"
          >
            <ExternalLink className="h-4 w-4" />
            Open legacy HTML
          </a>
        </div>
      </section>
    </div>
  )
}
