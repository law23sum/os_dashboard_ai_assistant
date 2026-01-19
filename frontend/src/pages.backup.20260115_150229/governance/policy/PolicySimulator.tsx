import { useCallback, useMemo } from 'react'
import { useIARouteContext } from '../../../navigation/iaContext'
import { FeaturePageTemplate, type ParameterDefinition } from '../../../components/templates/FeaturePageTemplate'
import {
  PolicySimulationRequestSchema,
  PolicySimulationResponseSchema,
} from '../../../domain/policySchemas'

const buildParameters = (): ParameterDefinition[] => [
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
    id: 'actionType',
    label: 'Action Type',
    type: 'select',
    required: true,
    options: [
      { label: 'Read', value: 'read' },
      { label: 'Write', value: 'write' },
      { label: 'Delete', value: 'delete' },
      { label: 'Deploy', value: 'deploy' },
    ],
  },
  {
    id: 'resource',
    label: 'Resource',
    type: 'text',
    required: true,
    placeholder: 'dataset://finance/transactions',
  },
  {
    id: 'actorRole',
    label: 'Actor Role',
    type: 'text',
    required: true,
    placeholder: 'analyst / admin / auditor',
  },
  {
    id: 'budget',
    label: 'Budget (USD)',
    type: 'number',
    required: true,
    placeholder: '5000',
  },
  {
    id: 'residency',
    label: 'Residency',
    type: 'select',
    required: true,
    options: [
      { label: 'US', value: 'us' },
      { label: 'EU', value: 'eu' },
      { label: 'APAC', value: 'apac' },
    ],
  },
  {
    id: 'strictMode',
    label: 'Strict Mode',
    type: 'toggle',
    helpText: 'Block any operation that violates policy guardrails.',
  },
  {
    id: 'rateLimit',
    label: 'Rate Limit (req/min)',
    type: 'number',
    placeholder: '120',
  },
]

export default function PolicySimulator() {
  const routeContext = useIARouteContext()
  const parameters = useMemo(buildParameters, [])

  const feature = routeContext.feature
  if (!feature) {
    return null
  }

  const handleRun = useCallback(async (payload: Record<string, unknown>) => {
    const params = payload.params as Record<string, unknown>

    const request = PolicySimulationRequestSchema.parse({
      policy_pack_id: String(params.policyPackId ?? ''),
      scenario: {
        action_type: String(params.actionType ?? ''),
        resource: String(params.resource ?? ''),
        actor_role: String(params.actorRole ?? ''),
        budget: Number(params.budget ?? 0),
        residency: String(params.residency ?? ''),
      },
      environment_profile: payload.environment,
      strict_mode: Boolean(params.strictMode ?? false),
      rate_limit: params.rateLimit ? Number(params.rateLimit) : undefined,
    })

    const response = await fetch('/api/policy/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const text = await response.text()
      throw new Error(text || 'Policy simulation failed')
    }

    const data = PolicySimulationResponseSchema.parse(await response.json())

    return {
      summary: [
        {
          label: 'Decision',
          value: data.decision === 'pass' ? 'Pass' : 'Fail',
          accent: data.decision === 'pass' ? 'text-emerald-300' : 'text-red-300',
        },
        {
          label: 'Risk score',
          value: data.risk_score.toFixed(2),
          accent: 'text-amber-300',
        },
        {
          label: 'Cost estimate',
          value: `$${data.cost_estimate.toFixed(2)}`,
          accent: 'text-sky-300',
        },
      ],
      rows: data.decisions.map((decision) => ({
        checkpoint: decision.checkpoint,
        decision: decision.decision,
        risk_score: decision.risk_score.toFixed(2),
        cost_impact: decision.cost_impact.toFixed(2),
      })),
      series: data.series,
      reportJson: data.report_json,
      reportMarkdown: data.report_markdown,
    }
  }, [])

  return (
    <FeaturePageTemplate
      platform={routeContext.platform}
      category={routeContext.category}
      feature={feature}
      parameters={parameters}
      onRun={handleRun}
    />
  )
}






