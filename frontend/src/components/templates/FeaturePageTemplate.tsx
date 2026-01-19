import { useEffect, useMemo, useState, type ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { Download, Play, Save } from 'lucide-react'
import { z } from 'zod'
import { useActor } from '../../contexts/ActorContext'
import type { IAPlatform, IACategory, IAFeature } from '../../data/iaManifest'
import { usePageContract } from '../../domain/pageContracts'
import {
  buildProjectionKey,
  emitEvent,
  publishProjectionUpdate,
  subscribeToProjection,
} from '../../domain/projections'
import PageHeader from '../PageHeader'
import { FeaturePageFrame } from './FeaturePageFrame'

type ParameterOption = {
  label: string
  value: string
}

export type ParameterDefinition = {
  id: string
  label: string
  type: 'text' | 'number' | 'select' | 'toggle' | 'textarea'
  required?: boolean
  placeholder?: string
  options?: ParameterOption[]
  helpText?: string
}

type LegacyParameter = {
  name: string
  label?: string
  type: 'text' | 'number' | 'select' | 'toggle' | 'textarea'
  required?: boolean
  placeholder?: string
  options?: ParameterOption[]
}

type LegacyConfigSelector = {
  label: string
  options: Array<{ id: string; name: string }>
}

type SummaryMetric = {
  label: string
  value: string
  accent?: string
}

type RunResult = {
  summary: SummaryMetric[]
  rows: Array<Record<string, string | number>>
  series: number[]
  reportJson: Record<string, unknown>
  reportMarkdown: string
}

type FeaturePageTemplateProps = {
  platform?: IAPlatform
  category?: IACategory
  feature?: IAFeature
  title?: string
  description?: string
  children?: ReactNode
  parameters?: Array<ParameterDefinition | LegacyParameter>
  configSelector?: LegacyConfigSelector
  onRun?: (payload: Record<string, unknown>) => Promise<RunResult>
  onExecute?: (
    params: Record<string, unknown>,
    config?: string,
    environment?: string,
  ) => Promise<unknown>
  onSave?: (params: Record<string, unknown>, config?: string) => Promise<void> | void
  onExport?: (format: 'json' | 'markdown', data: unknown) => Promise<void> | void
}

const defaultConfigProfiles = ['Default', 'Balanced', 'Strict']

const defaultResults = (title: string): RunResult => ({
  summary: [
    { label: 'Total records', value: '128', accent: 'text-emerald-300' },
    { label: 'Risk score', value: '0.42', accent: 'text-amber-300' },
    { label: 'Run time', value: '2m 12s', accent: 'text-sky-300' },
  ],
  rows: [
    { id: 'row-001', status: 'OK', score: 0.18, detail: `${title} check A` },
    { id: 'row-002', status: 'Warn', score: 0.52, detail: `${title} check B` },
    { id: 'row-003', status: 'OK', score: 0.27, detail: `${title} check C` },
  ],
  series: [6, 9, 4, 7, 11, 8, 10],
  reportJson: { feature: title, summary: 'Generated preview', status: 'ok' },
  reportMarkdown: `# ${title} Report\n\n- Status: ok\n- Records: 128\n- Notes: Sample output`,
})

const coerceRunResult = (title: string, response: unknown): RunResult => {
  const fallback = defaultResults(title)
  if (
    response &&
    typeof response === 'object' &&
    'summary' in response &&
    'rows' in response &&
    'series' in response
  ) {
    return response as RunResult
  }
  if (response) {
    return {
      ...fallback,
      reportJson: { ...fallback.reportJson, response },
      reportMarkdown: `${fallback.reportMarkdown}\n\n## Response\n\n\`\`\`json\n${JSON.stringify(
        response,
        null,
        2,
      )}\n\`\`\``,
    }
  }
  return fallback
}

const toTitle = (value: string) =>
  value
    .replace(/[-_]+/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())

const createCorrelationId = () => {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  return `corr_${Date.now()}_${Math.random().toString(16).slice(2)}`
}

const inferParameters = (title: string): ParameterDefinition[] => {
  const lower = title.toLowerCase()
  const common: ParameterDefinition[] = [
    {
      id: 'timeRange',
      label: 'Time Range',
      type: 'select',
      required: true,
      options: [
        { label: 'Last 24 hours', value: '24h' },
        { label: 'Last 7 days', value: '7d' },
        { label: 'Last 30 days', value: '30d' },
      ],
    },
    {
      id: 'scope',
      label: 'Scope',
      type: 'text',
      required: true,
      placeholder: 'workspace-id / project-id / tenant-id',
    },
    {
      id: 'threshold',
      label: 'Threshold',
      type: 'number',
      required: true,
      placeholder: '0.0 - 1.0',
    },
  ]

  if (lower.includes('policy')) {
    return [
      {
        id: 'policyPackId',
        label: 'Policy Pack',
        type: 'select',
        required: true,
        options: [
          { label: 'Default Governance Pack', value: 'gov-default' },
          { label: 'Regulated Data Pack', value: 'gov-regulated' },
          { label: 'AI Safety Pack', value: 'gov-ai-safety' },
        ],
      },
      {
        id: 'scenario',
        label: 'Scenario',
        type: 'textarea',
        required: true,
        placeholder: 'Describe the action, resource, and guardrails...',
      },
      {
        id: 'strictMode',
        label: 'Strict Mode',
        type: 'toggle',
        helpText: 'Enable hardened policy evaluation rules.',
      },
    ]
  }

  if (lower.includes('export') || lower.includes('report')) {
    return [
      ...common,
      {
        id: 'format',
        label: 'Export Format',
        type: 'select',
        required: true,
        options: [
          { label: 'CSV', value: 'csv' },
          { label: 'JSON', value: 'json' },
          { label: 'Markdown', value: 'md' },
        ],
      },
    ]
  }

  return common
}

const normalizeParameters = (
  title: string,
  parameters?: Array<ParameterDefinition | LegacyParameter>,
): ParameterDefinition[] => {
  if (!parameters || parameters.length === 0) {
    return inferParameters(title)
  }
  const first = parameters[0] as LegacyParameter | ParameterDefinition
  if ('name' in first) {
    return (parameters as LegacyParameter[]).map((param) => ({
      id: param.name,
      label: param.label ?? toTitle(param.name),
      type: param.type,
      required: param.required,
      placeholder: param.placeholder,
      options: param.options?.map((option) => ({
        label: option.label ?? option.value,
        value: option.value,
      })),
    }))
  }
  return parameters as ParameterDefinition[]
}

const buildSchema = (parameters: ParameterDefinition[]) => {
  const shape: Record<string, z.ZodTypeAny> = {}
  parameters.forEach((param) => {
    let schema: z.ZodTypeAny
    switch (param.type) {
      case 'number':
        schema = z.preprocess(
          (value) => (value === '' || value === null ? NaN : Number(value)),
          z.number().finite(),
        )
        break
      case 'toggle':
        schema = z.boolean()
        break
      case 'select':
        schema = z.string().min(1)
        break
      default:
        schema = z.string()
    }
    if (param.required) {
      schema = schema.refine((value) => value !== '' && value !== null && value !== undefined, {
        message: `${param.label} is required`,
      })
    }
    shape[param.id] = schema
  })
  return z.object(shape)
}

const downloadBlob = (content: string, filename: string, type = 'application/json') => {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.click()
  URL.revokeObjectURL(url)
}

const statusTone = (status: string) => {
  switch (status) {
    case 'Running':
      return 'bg-amber-500/20 text-amber-200 border-amber-400/40'
    case 'Failed':
      return 'bg-red-500/20 text-red-200 border-red-400/40'
    case 'Succeeded':
      return 'bg-emerald-500/20 text-emerald-200 border-emerald-400/40'
    default:
      return 'bg-slate-500/20 text-slate-200 border-slate-400/40'
  }
}

const SimpleBarChart = ({ series }: { series: number[] }) => {
  const max = Math.max(...series, 1)
  return (
    <svg viewBox="0 0 140 60" className="w-full h-20">
      {series.map((value, index) => {
        const height = (value / max) * 48
        return (
          <rect
            key={`bar-${index}`}
            x={index * 18 + 4}
            y={56 - height}
            width={12}
            height={height}
            rx={2}
            className="fill-[color:var(--osd-accent)]/70"
          />
        )
      })}
    </svg>
  )
}

export function FeaturePageTemplate(props: FeaturePageTemplateProps) {
  const {
    platform,
    category,
    feature,
    title,
    description,
    children,
    parameters,
    configSelector,
    onRun,
    onExecute,
    onSave,
    onExport,
  } = props
  const location = useLocation()
  const { currentActor } = useActor()

  const resolvedFeature = useMemo<IAFeature>(() => {
    if (feature) return feature
    const parts = location.pathname.split('/').filter(Boolean)
    const slug = parts[parts.length - 1] ?? 'feature'
    const label = title ?? toTitle(slug)
    return {
      id: slug,
      label,
      route: location.pathname,
      componentPath: 'frontend/src/components/templates/FeaturePageTemplate.tsx',
      bestCommit: 'stable',
      actorScope: 'both',
      order: 1,
    }
  }, [feature, location.pathname, title])

  const contract = usePageContract(resolvedFeature.route)

  const resolvedParameters = useMemo(
    () => normalizeParameters(resolvedFeature.label, parameters),
    [parameters, resolvedFeature.label],
  )
  const schema = useMemo(() => buildSchema(resolvedParameters), [resolvedParameters])
  const configOptions = useMemo(() => {
    if (configSelector?.options?.length) {
      return configSelector.options.map((option) => ({
        label: option.name,
        value: option.id,
      }))
    }
    return defaultConfigProfiles.map((profile) => ({ label: profile, value: profile }))
  }, [configSelector])
  const initialValues = useMemo(() => {
    const values: Record<string, unknown> = {}
    resolvedParameters.forEach((param) => {
      if (param.type === 'toggle') {
        values[param.id] = false
      } else if (param.options?.length) {
        values[param.id] = param.options[0].value
      } else {
        values[param.id] = ''
      }
    })
    return values
  }, [resolvedParameters])

  const valuesStorageKey = `feature-values:${resolvedFeature.route}`
  const [values, setValues] = useState<Record<string, unknown>>(() => {
    if (typeof window === 'undefined') return initialValues
    try {
      const stored = window.localStorage.getItem(valuesStorageKey)
      if (stored) {
        const parsed = JSON.parse(stored)
        if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
          return { ...initialValues, ...parsed }
        }
      }
    } catch {
      // ignore
    }
    return initialValues
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [status, setStatus] = useState('Idle')
  const [environment, setEnvironment] = useState<'local' | 'enterprise' | 'sandbox'>('local')
  const configStorageKey = `config-profile:${resolvedFeature.route}`
  const [configProfile, setConfigProfile] = useState(() => {
    const fallback = configOptions[0]?.value ?? defaultConfigProfiles[0]
    if (typeof window === 'undefined') return fallback
    try {
      return window.localStorage.getItem(configStorageKey) ?? fallback
    } catch {
      return fallback
    }
  })
  const [result, setResult] = useState<RunResult>(() => defaultResults(resolvedFeature.label))
  const [logs, setLogs] = useState<string[]>([
    'Awaiting execution plan...',
    'No tasks queued yet.',
  ])

  const environmentOptions =
    currentActor === 'enterprise' ? ['local', 'enterprise', 'sandbox'] : ['local', 'sandbox']
  const resolvedDescription =
    description ?? contract?.summary ?? `Configure and execute ${resolvedFeature.label}.`

  useEffect(() => {
    const projectionKey = buildProjectionKey(currentActor, resolvedFeature.id, 'latest')
    return subscribeToProjection(projectionKey, (data) => {
      setResult(coerceRunResult(resolvedFeature.label, data))
      setLogs((prev) => [...prev, 'Projection update received.'])
    })
  }, [currentActor, resolvedFeature.id, resolvedFeature.label])

  const handleValueChange = (id: string, value: unknown) => {
    setValues((prev) => ({ ...prev, [id]: value }))
  }

  useEffect(() => {
    if (typeof window === 'undefined') return
    try {
      window.localStorage.setItem(configStorageKey, configProfile)
    } catch {
      // ignore
    }
  }, [configProfile, configStorageKey])

  const handleRun = async () => {
    const parsed = schema.safeParse(values)
    if (!parsed.success) {
      const fieldErrors: Record<string, string> = {}
      parsed.error.errors.forEach((issue) => {
        const key = issue.path[0]
        if (typeof key === 'string') {
          fieldErrors[key] = issue.message
        }
      })
      setErrors(fieldErrors)
      return
    }

    setErrors({})
    setStatus('Running')
    const correlationId = createCorrelationId()
    emitEvent(
      'feature_action_started',
      {
        featureId: resolvedFeature.id,
        route: resolvedFeature.route,
        params: parsed.data,
        configProfile,
        environment,
      },
      correlationId,
    )
    setLogs([
      'Execution plan locked.',
      'Inputs validated.',
      'Dispatching workflow...',
    ])

    try {
      const payload = {
        params: parsed.data,
        configProfile,
        environment,
        computeClass: contract?.compute_class ?? 'standard',
      }
      const handler =
        onRun ??
        (onExecute
          ? async (runPayload: typeof payload) => {
              const response = await onExecute(
                runPayload.params as Record<string, unknown>,
                runPayload.configProfile,
                runPayload.environment,
              )
              return coerceRunResult(resolvedFeature.label, response)
            }
          : undefined)
      const output = handler ? await handler(payload) : defaultResults(resolvedFeature.label)
      setResult(output)
      const projectionKey = buildProjectionKey(currentActor, resolvedFeature.id, correlationId)
      const projectionPayload = {
        status: 'succeeded',
        featureId: resolvedFeature.id,
        route: resolvedFeature.route,
        correlationId,
        output,
      }
      publishProjectionUpdate(projectionKey, projectionPayload)
      publishProjectionUpdate(
        buildProjectionKey(currentActor, resolvedFeature.id, 'latest'),
        projectionPayload,
      )
      setLogs((prev) => [...prev, 'Results aggregated.', 'Run completed successfully.'])
      emitEvent(
        'feature_action_completed',
        {
          featureId: resolvedFeature.id,
          route: resolvedFeature.route,
          status: 'succeeded',
        },
        correlationId,
      )
      setStatus('Succeeded')
    } catch (error) {
      setLogs((prev) => [...prev, `Run failed: ${String(error)}`])
      const projectionKey = buildProjectionKey(currentActor, resolvedFeature.id, correlationId)
      const projectionPayload = {
        status: 'failed',
        featureId: resolvedFeature.id,
        route: resolvedFeature.route,
        correlationId,
        error: String(error),
      }
      publishProjectionUpdate(projectionKey, projectionPayload)
      publishProjectionUpdate(
        buildProjectionKey(currentActor, resolvedFeature.id, 'latest'),
        projectionPayload,
      )
      emitEvent(
        'feature_action_completed',
        {
          featureId: resolvedFeature.id,
          route: resolvedFeature.route,
          status: 'failed',
          error: String(error),
        },
        correlationId,
      )
      setStatus('Failed')
    }
  }

  const handleSave = async () => {
    try {
      if (onSave) {
        await onSave(values, configProfile)
        setLogs((prev) => [...prev, 'Configuration saved.'])
        return
      }
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(valuesStorageKey, JSON.stringify(values))
        setLogs((prev) => [...prev, 'Configuration saved locally.'])
      }
    } catch (error) {
      setLogs((prev) => [...prev, `Save failed: ${String(error)}`])
    }
  }

  const handleExport = async (format: 'json' | 'markdown') => {
    const payload = format === 'json' ? result.reportJson : result.reportMarkdown
    if (onExport) {
      await onExport(format, payload)
      return
    }
    const content = format === 'json' ? JSON.stringify(payload, null, 2) : String(payload)
    const filename = `${resolvedFeature.id}-report.${format === 'json' ? 'json' : 'md'}`
    const contentType = format === 'json' ? 'application/json' : 'text/markdown'
    downloadBlob(content, filename, contentType)
  }

  const tableColumns = Object.keys(result.rows[0] ?? {})

  const auditPanel = contract ? (
    <div className="grid gap-3 text-xs text-[color:var(--osd-muted)] md:grid-cols-2">
      <div>
        <div className="uppercase tracking-wider text-[0.6rem]">Entities</div>
        <div className="mt-1 text-sm text-[color:var(--osd-text)]">
          {contract.entities.length ? contract.entities.join(', ') : 'None declared'}
        </div>
      </div>
      <div>
        <div className="uppercase tracking-wider text-[0.6rem]">Projections</div>
        <div className="mt-1 text-sm text-[color:var(--osd-text)]">
          {contract.projections.length ? contract.projections.join(', ') : 'None declared'}
        </div>
      </div>
    </div>
  ) : null

  const dependsOn = contract?.projections ?? []
  const feeds = contract?.emits_events ?? []
  const relatedPanel =
    dependsOn.length || feeds.length || children ? (
      <section className="glass-card p-6 space-y-4" data-page-section="related">
        <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Related</h2>
        <div className="grid gap-4 md:grid-cols-2 text-sm text-[color:var(--osd-muted)]">
          <div>
            <div className="uppercase tracking-wider text-[0.6rem]">This page depends on</div>
            <div className="mt-2 text-[color:var(--osd-text)]">
              {dependsOn.length ? dependsOn.join(', ') : 'No upstream dependencies declared.'}
            </div>
          </div>
          <div>
            <div className="uppercase tracking-wider text-[0.6rem]">This page feeds</div>
            <div className="mt-2 text-[color:var(--osd-text)]">
              {feeds.length ? feeds.join(', ') : 'No downstream feeds declared.'}
            </div>
          </div>
        </div>
        {children ? <div className="mt-4">{children}</div> : null}
      </section>
    ) : null

  return (
    <FeaturePageFrame auditPanel={auditPanel}>
      <section data-page-section="header">
        <PageHeader
          title={resolvedFeature.label}
          description={resolvedDescription}
          actions={(
            <div className="flex flex-wrap items-center gap-2">
              <span
                className={`px-2.5 py-1 text-xs font-semibold rounded-full border ${statusTone(status)}`}
              >
                {status}
              </span>
              <button type="button" className="btn-primary flex items-center gap-2" onClick={handleRun}>
                <Play className="w-4 h-4" />
                Run
              </button>
              <button
                type="button"
                className="btn-secondary flex items-center gap-2"
                onClick={handleSave}
              >
                <Save className="w-4 h-4" />
                Save
              </button>
              <button
                type="button"
                className="btn-secondary flex items-center gap-2"
                onClick={() => handleExport('json')}
              >
                <Download className="w-4 h-4" />
                Export
              </button>
            </div>
          )}
        />
        <div className="text-xs text-[color:var(--osd-muted)] mt-2">
          {currentActor === 'enterprise'
            ? 'Enterprise'
            : currentActor === 'business'
              ? 'Business/Team'
              : 'Personal'} /{' '}
          {platform?.label ? `${platform.label} / ` : ''}
          {category?.label ? `${category.label} / ` : ''}
          {resolvedFeature.label}
        </div>
      </section>

      <section className="glass-card p-6 space-y-4" data-page-section="inputs">
        <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Parameters</h2>
        <div className="grid gap-4 md:grid-cols-2">
          {resolvedParameters.map((param) => {
            const value = values[param.id]
            const error = errors[param.id]
            const inputId = `param-${param.id}`
            return (
              <div key={param.id} className="space-y-2">
                <label htmlFor={inputId} className="text-sm font-medium text-[color:var(--osd-text)]">
                  {param.label}
                </label>
                {param.type === 'select' ? (
                  <select
                    id={inputId}
                    className="w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40 px-3 py-2 text-sm"
                    value={String(value)}
                    onChange={(event) => handleValueChange(param.id, event.target.value)}
                  >
                    {param.options?.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                ) : param.type === 'textarea' ? (
                  <textarea
                    id={inputId}
                    className="w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40 px-3 py-2 text-sm min-h-[96px]"
                    value={String(value ?? '')}
                    placeholder={param.placeholder}
                    onChange={(event) => handleValueChange(param.id, event.target.value)}
                  />
                ) : param.type === 'toggle' ? (
                  <label className="flex items-center gap-2 text-sm">
                    <input
                      id={inputId}
                      type="checkbox"
                      checked={Boolean(value)}
                      onChange={(event) => handleValueChange(param.id, event.target.checked)}
                      className="h-4 w-4 rounded border-[color:var(--osd-border)]"
                    />
                    <span className="text-[color:var(--osd-muted)]">Enabled</span>
                  </label>
                ) : (
                  <input
                    id={inputId}
                    type={param.type === 'number' ? 'number' : 'text'}
                    className="w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40 px-3 py-2 text-sm"
                    value={String(value ?? '')}
                    placeholder={param.placeholder}
                    onChange={(event) => handleValueChange(param.id, event.target.value)}
                  />
                )}
                {param.helpText && (
                  <p className="text-xs text-[color:var(--osd-muted)]">{param.helpText}</p>
                )}
                {error && <p className="text-xs text-red-300">{error}</p>}
              </div>
            )
          })}
        </div>
      </section>

      <section className="glass-card p-6 space-y-4" data-page-section="configuration">
        <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Configuration</h2>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <label htmlFor="config-profile" className="text-sm font-medium text-[color:var(--osd-text)]">
              {configSelector?.label ?? 'Configuration Profile'}
            </label>
            <select
              id="config-profile"
              value={configProfile}
              onChange={(event) => setConfigProfile(event.target.value)}
              className="w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40 px-3 py-2 text-sm"
            >
              {configOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-2">
            <label htmlFor="driver-profile" className="text-sm font-medium text-[color:var(--osd-text)]">
              Driver Profile
            </label>
            <select
              id="driver-profile"
              className="w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40 px-3 py-2 text-sm"
            >
              <option value="default">Default Driver</option>
              <option value="hardened">Hardened Driver</option>
              <option value="experimental">Experimental Driver</option>
            </select>
          </div>
        </div>
      </section>

      <section className="glass-card p-6 space-y-4" data-page-section="environment">
        <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Environment</h2>
        <div className="flex flex-wrap gap-3">
          {environmentOptions.map((option) => (
            <label key={option} className="flex items-center gap-2 text-sm">
              <input
                type="radio"
                name="environment"
                checked={environment === option}
                onChange={() => setEnvironment(option as typeof environment)}
                className="h-4 w-4 border-[color:var(--osd-border)]"
              />
              <span className="capitalize text-[color:var(--osd-text)]">{option}</span>
            </label>
          ))}
        </div>
        <div className="text-xs text-[color:var(--osd-muted)]">
          Execution plan: {contract?.compute_class ?? 'standard'} compute, scoped to {environment}.
        </div>
        <details className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/30 p-4">
          <summary className="cursor-pointer text-sm text-[color:var(--osd-text)]">
            Advanced resource limits
          </summary>
          <div className="mt-3 grid gap-3 md:grid-cols-3">
            {['CPU', 'Memory', 'Time Budget'].map((label) => (
              <div key={label} className="space-y-2">
                <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">
                  {label}
                </label>
                <input
                  type="range"
                  min={1}
                  max={10}
                  defaultValue={5}
                  className="w-full"
                />
              </div>
            ))}
          </div>
        </details>
      </section>

      <section className="glass-card p-6 space-y-4" data-page-section="execute">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Execute</h2>
          <button type="button" className="btn-primary" onClick={handleRun}>
            Run
          </button>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border border-[color:var(--osd-border)] p-4">
            <h3 className="text-sm font-semibold text-[color:var(--osd-text)]">Progress</h3>
            <ul className="mt-3 space-y-2 text-xs text-[color:var(--osd-muted)]">
              {['Queued', 'Validating', 'Executing', 'Aggregating'].map((step) => (
                <li key={step} className="flex items-center justify-between">
                  <span>{step}</span>
                  <span>{status === 'Running' ? 'In progress' : 'Idle'}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-lg border border-[color:var(--osd-border)] p-4">
            <h3 className="text-sm font-semibold text-[color:var(--osd-text)]">Logs</h3>
            <div className="mt-3 space-y-2 text-xs text-[color:var(--osd-muted)]">
              {logs.map((entry, index) => (
                <div key={`log-${index}`}>{entry}</div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="glass-card p-6 space-y-4" data-page-section="results">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Results</h2>
          <div className="flex items-center gap-2">
            <button
              type="button"
              className="btn-secondary text-xs"
              onClick={() => handleExport('json')}
            >
              Export JSON
            </button>
            <button
              type="button"
              className="btn-secondary text-xs"
              onClick={() => handleExport('markdown')}
            >
              Export Markdown
            </button>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {result.summary.map((metric) => (
            <div
              key={metric.label}
              className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/30 p-4"
            >
              <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">
                {metric.label}
              </div>
              <div className={`mt-2 text-2xl font-semibold ${metric.accent ?? ''}`}>
                {metric.value}
              </div>
            </div>
          ))}
        </div>

        <div className="grid gap-4 lg:grid-cols-[2fr,1fr]">
          <div className="rounded-lg border border-[color:var(--osd-border)] p-4 overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">
                  {tableColumns.map((col) => (
                    <th key={col} className="pb-2 pr-4">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="text-[color:var(--osd-text)]">
                {result.rows.map((row, idx) => (
                  <tr key={`row-${idx}`} className="border-t border-[color:var(--osd-border)]/50">
                    {tableColumns.map((col) => (
                      <td key={`${idx}-${col}`} className="py-2 pr-4">
                        {String(row[col] ?? '')}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="rounded-lg border border-[color:var(--osd-border)] p-4">
            <h3 className="text-sm font-semibold text-[color:var(--osd-text)]">Trend</h3>
            <SimpleBarChart series={result.series} />
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border border-[color:var(--osd-border)] p-4">
            <h3 className="text-sm font-semibold text-[color:var(--osd-text)]">JSON Report</h3>
            <pre className="mt-2 text-xs text-[color:var(--osd-muted)] whitespace-pre-wrap">
              {JSON.stringify(result.reportJson, null, 2)}
            </pre>
          </div>
          <div className="rounded-lg border border-[color:var(--osd-border)] p-4">
            <h3 className="text-sm font-semibold text-[color:var(--osd-text)]">Markdown Preview</h3>
            <pre className="mt-2 text-xs text-[color:var(--osd-muted)] whitespace-pre-wrap">
              {result.reportMarkdown}
            </pre>
          </div>
        </div>
      </section>

      {relatedPanel}
    </FeaturePageFrame>
  )
}
