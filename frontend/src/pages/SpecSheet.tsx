import { useEffect, useMemo, useState } from 'react'
import { AlertCircle, Download, RefreshCw } from 'lucide-react'

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
    </div>
  )
}
