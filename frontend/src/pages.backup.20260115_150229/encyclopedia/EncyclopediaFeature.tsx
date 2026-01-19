import { useLocation } from 'react-router-dom'
import { FeaturePageTemplate } from '@/components/templates/FeaturePageTemplate'

const descriptionByRoute: Record<string, string> = {
  '/encyclopedia/topics': 'Curated topics and canonical references across the platform.',
  '/encyclopedia/explanations': 'Operational explanations with context, inputs, and outputs.',
  '/encyclopedia/history': 'Historical timelines, decisions, and platform milestones.',
  '/encyclopedia/glossary': 'Definitions and cross-referenced terms used across the system.',
}

export default function EncyclopediaFeature() {
  const location = useLocation()
  const description =
    descriptionByRoute[location.pathname] ?? 'Encyclopedia reference workflows.'

  return <FeaturePageTemplate description={description} />
}
