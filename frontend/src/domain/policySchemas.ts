import { z } from 'zod'

export const PolicySimulationRequestSchema = z.object({
  policy_pack_id: z.string().min(1),
  scenario: z.object({
    action_type: z.string().min(1),
    resource: z.string().min(1),
    actor_role: z.string().min(1),
    budget: z.number().nonnegative(),
    residency: z.string().min(1),
  }),
  environment_profile: z.enum(['local', 'enterprise', 'sandbox']),
  strict_mode: z.boolean().optional(),
  rate_limit: z.number().nonnegative().optional(),
})

export const PolicySimulationDecisionSchema = z.object({
  checkpoint: z.string().min(1),
  decision: z.string().min(1),
  risk_score: z.number(),
  cost_impact: z.number(),
})

export const PolicySimulationResponseSchema = z.object({
  id: z.string().min(1),
  status: z.enum(['queued', 'running', 'succeeded', 'failed']),
  decision: z.enum(['pass', 'fail']),
  risk_score: z.number(),
  cost_estimate: z.number(),
  decisions: z.array(PolicySimulationDecisionSchema),
  series: z.array(z.number()),
  report_json: z.record(z.unknown()),
  report_markdown: z.string(),
})

export type PolicySimulationRequest = z.infer<typeof PolicySimulationRequestSchema>
export type PolicySimulationResponse = z.infer<typeof PolicySimulationResponseSchema>
