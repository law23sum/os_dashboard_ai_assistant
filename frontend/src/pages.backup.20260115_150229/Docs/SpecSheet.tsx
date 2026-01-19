import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { AlertCircle, Download, RefreshCw } from 'lucide-react'
import { specRequirements, statusMeta, TECH_SPEC_ROUTE } from '../data/specRequirements'

const SPEC_ENDPOINT = '/api/docs/technical-spec-sheet'

export default function SpecSheet() {
  const [reloadKey, setReloadKey] = useState(0)
  const [canEmbed, setCanEmbed] = useState(true)

  useEffect(() => {
    const mimeSupported =
      typeof navigator !== 'undefined' &&
      navigator.mimeTypes &&
      Object.prototype.hasOwnProperty.call(navigator.mimeTypes, 'application/pdf')
    setCanEmbed(mimeSupported)
  }, [])

  const iframeSrc = useMemo(
    () => `${SPEC_ENDPOINT}?reload=${reloadKey}#toolbar=0&navpanes=0&scrollbar=0`,
    [reloadKey],
  )

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6 text-slate-100">
      <section className="glass-card flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="eyebrow-text">Engineering Reference</p>
          <h1 className="mt-2 text-3xl font-semibold text-white">Technical Spec Sheet · Version 6</h1>
          <p className="mt-3 text-sm text-slate-300 max-w-3xl">
            This PDF is stored at the repository root and now streams through FastAPI, ensuring the same
            artifact is available whether you launch the desktop executable or the browser experience.
            Use the inline viewer for quick reviews or download the file for detailed markups.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <a
            href={SPEC_ENDPOINT}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 rounded-2xl border border-white/20 bg-white/5 px-4 py-2 text-sm font-semibold text-white hover:border-white/40"
          >
            <Download className="h-4 w-4" />
            Download PDF
          </a>
          <button
            type="button"
            onClick={() => setReloadKey((value) => value + 1)}
            className="inline-flex items-center gap-2 rounded-2xl border border-white/20 bg-white/5 px-4 py-2 text-sm font-semibold text-white hover:border-white/40"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh Viewer
          </button>
        </div>
      </section>

      <section className="glass-card overflow-hidden p-0">
        {canEmbed ? (
          <iframe
            key={reloadKey}
            src={iframeSrc}
            title="Technical Spec Sheet"
            className="h-[80vh] w-full border-0"
            aria-label="Technical Spec Sheet PDF viewer"
          />
        ) : (
          <div className="flex flex-col items-center gap-4 px-6 py-16 text-center text-slate-200">
            <AlertCircle className="h-10 w-10 text-amber-300" />
            <div>
              <p className="text-lg font-semibold">Inline PDF preview is unavailable</p>
              <p className="mt-2 text-sm text-slate-300">
                Your environment does not support embedded PDFs. Use the button above to download the
                Technical Spec Sheet directly.
              </p>
            </div>
          </div>
        )}
      </section>

      <section className="glass-card p-6 space-y-6">
        <div className="flex flex-col gap-2">
          <p className="eyebrow-text">Spec Tracker</p>
          <h2 className="text-2xl font-semibold text-white">Requirements from Spec + Migration Log</h2>
          <p className="text-sm text-slate-300">
            Pulled directly from <Link className="text-blue-300 underline" to="/docs/migration_continued.md">MIGRATION_CONTINUED.md</Link> and the{' '}
            <Link className="text-blue-300 underline" to={TECH_SPEC_ROUTE}>Technical Spec Sheet</Link>. Use this tracker to keep desktop + web builds honest.
            Status chips mirror the gap log so it’s obvious which surfaces still need attention.
          </p>
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          {specRequirements.map((item) => {
            const status = statusMeta[item.status]
            return (
              <article key={item.id} className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-lg shadow-black/10">
                <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">
                      {item.specRefs.join(' · ')}
                    </p>
                    <h3 className="mt-1 text-lg font-semibold text-white">{item.title}</h3>
                  </div>
                  <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${status.chipClass}`}>
                    {status.label}
                  </span>
                </div>
                <p className="mt-3 text-sm text-slate-300">{item.description}</p>
                <div className="mt-4 space-y-1 text-sm text-slate-300">
                  <p className="font-medium text-slate-100">Next steps</p>
                  <ul className="list-disc space-y-0.5 pl-5">
                    {item.nextSteps.map((step) => (
                      <li key={step}>{step}</li>
                    ))}
                  </ul>
                </div>
                <div className="mt-4 flex flex-wrap gap-2 text-xs">
                  {item.sourceDocs.map((source) =>
                    source.href ? (
                      source.href.startsWith('http') ? (
                        <a
                          key={source.label}
                          href={source.href}
                          target="_blank"
                          rel="noreferrer"
                          className="rounded-full border border-white/15 bg-white/5 px-3 py-1 text-[0.7rem] uppercase tracking-[0.25em] text-white hover:border-white/30"
                        >
                          {source.label}
                        </a>
                      ) : (
                        <Link
                          key={source.label}
                          to={source.href}
                          className="rounded-full border border-white/15 bg-white/5 px-3 py-1 text-[0.7rem] uppercase tracking-[0.25em] text-white hover:border-white/30"
                        >
                          {source.label}
                        </Link>
                      )
                    ) : (
                      <span
                        key={source.label}
                        className="rounded-full border border-white/10 px-3 py-1 text-[0.7rem] uppercase tracking-[0.25em] text-slate-200"
                      >
                        {source.label}
                      </span>
                    ),
                  )}
                </div>
              </article>
            )
          })}
        </div>
      </section>
    </div>
  )
}