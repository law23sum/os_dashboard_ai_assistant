import PageHeader from '../PageHeader'
import Button from '../ui/Button'
import Card, { CardContent, CardHeader, CardTitle } from '../ui/Card'
import Input from '../ui/Input'
import { FeaturePageFrame } from './FeaturePageFrame'

type Metric = {
  label: string
  value: string
  detail?: string
}

type LegacyHomePageProps = {
  title: string
  description: string
  routeHint: string
  metrics: Metric[]
  primaryAction?: string
  secondaryAction?: string
}

export default function LegacyHomePage({
  title,
  description,
  routeHint,
  metrics,
  primaryAction = 'Execute',
  secondaryAction = 'Configure',
}: LegacyHomePageProps) {
  return (
    <FeaturePageFrame>
      <PageHeader
        title={title}
        description={description}
        actions={(
          <div className="flex flex-wrap gap-2">
            <Button variant="outline">{secondaryAction}</Button>
            <Button>{primaryAction}</Button>
          </div>
        )}
      />

      <section className="glass-card p-6 space-y-4" data-page-section="inputs">
        <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Parameters</h2>
        <div className="grid gap-4 md:grid-cols-3">
          <Input label="Scope" placeholder="workspace-id / tenant-id" />
          <Input label="Time Range" placeholder="Last 7 days" />
          <Input label="Threshold" placeholder="0.0 - 1.0" />
        </div>
      </section>

      <section className="glass-card p-6 space-y-4" data-page-section="execute">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Execute</h2>
            <p className="text-sm text-[color:var(--osd-muted)]">
              Run the latest workflows and capture outputs for {title}.
            </p>
          </div>
          <Button>{primaryAction}</Button>
        </div>
      </section>

      <section className="space-y-4" data-page-section="results">
        <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Results</h2>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {metrics.map((metric) => (
            <Card key={metric.label}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{metric.label}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-[color:var(--osd-text)]">{metric.value}</div>
                {metric.detail ? (
                  <p className="text-xs text-[color:var(--osd-muted)] mt-1">{metric.detail}</p>
                ) : null}
              </CardContent>
            </Card>
          ))}
        </div>
        <Card>
          <CardHeader>
            <CardTitle>Results & Output</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-start gap-2 text-sm text-[color:var(--osd-muted)]">
              <p>{description}</p>
              <p>Route: {routeHint}</p>
              <p>Run the workflow to populate live outputs.</p>
            </div>
          </CardContent>
        </Card>
      </section>
    </FeaturePageFrame>
  )
}
