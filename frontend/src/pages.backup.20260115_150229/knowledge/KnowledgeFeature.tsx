import { useLocation } from 'react-router-dom'
import { FeaturePageTemplate } from '@/components/templates/FeaturePageTemplate'

const descriptionByRoute: Record<string, string> = {
  '/knowledge/perspective': 'Capture context, stakeholders, and directional framing.',
  '/knowledge/insight': 'Summarize derived insights from recent operations and signals.',
  '/knowledge/wisdom': 'Codify patterns, guardrails, and decision heuristics.',
  '/knowledge/experience': 'Log experiential learnings and post-action retrospectives.',
}

export default function KnowledgeFeature() {
  const location = useLocation()
  const description =
    descriptionByRoute[location.pathname] ?? 'Knowledge workflows and synthesis.'

  return <FeaturePageTemplate description={description} />
}
