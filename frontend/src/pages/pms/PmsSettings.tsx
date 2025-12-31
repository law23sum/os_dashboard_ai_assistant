import PageHeader from '../../components/PageHeader'

export default function PmsSettings() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="PMS"
        title="Settings"
        description="Global defaults for scheduler tiers, vocabularies, and templates."
      />

      <div className="glass-card p-5 space-y-4">
        <div>
          <h2 className="text-sm font-semibold text-[color:var(--osd-text)]">Scheduler defaults</h2>
          <p className="text-sm text-[color:var(--osd-muted)]">
            Set default priority tiers and lane selection policies for new projects.
          </p>
        </div>

        <div>
          <h2 className="text-sm font-semibold text-[color:var(--osd-text)]">Category & Type vocab</h2>
          <p className="text-sm text-[color:var(--osd-muted)]">
            Configure allowed categories/types or freeform normalization rules.
          </p>
        </div>
      </div>
    </div>
  )
}
