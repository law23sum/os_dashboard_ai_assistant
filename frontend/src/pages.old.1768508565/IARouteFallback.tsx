import { Construction } from 'lucide-react'

export default function IARouteFallback() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] py-16 px-6">
      <div className="glass-card p-8 max-w-md text-center space-y-4">
        <div className="flex justify-center mb-4">
          <div className="p-4 rounded-2xl bg-[color:var(--osd-surface)]/40 border border-[color:var(--osd-border)]">
            <Construction className="w-12 h-12 text-[color:var(--osd-muted)]" />
          </div>
        </div>
        <h2 className="text-xl font-semibold text-[color:var(--osd-text)]">
          Page Under Construction
        </h2>
        <p className="text-sm text-[color:var(--osd-muted)]">
          This page is being developed. Check back soon for updates.
        </p>
      </div>
    </div>
  )
}
