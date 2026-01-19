import type { ReactNode } from 'react'

type FeaturePageFrameProps = {
  children: ReactNode
  auditPanel?: ReactNode
}

export function FeaturePageFrame({ children, auditPanel }: FeaturePageFrameProps) {
  return (
    <div className="space-y-6" data-page-frame="feature">
      {children}
      {auditPanel ? (
        <section className="glass-card p-6 space-y-3" data-page-section="audit">
          <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Audit & Evidence</h2>
          {auditPanel}
        </section>
      ) : null}
    </div>
  )
}
