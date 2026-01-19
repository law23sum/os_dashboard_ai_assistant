import { CategoryHomeTemplate } from '@/components/templates/CategoryHomeTemplate'

const features = [
  {
    "title": "Mission & Scope",
    "path": "/mission/overview"
  },
  {
    "title": "Use Cases Map",
    "path": "/mission/use-cases"
  },
  {
    "title": "System Boundaries & Non-Goals",
    "path": "/mission/non-goals"
  },
  {
    "title": "Terminology Glossary",
    "path": "/mission/glossary"
  },
  {
    "title": "Deployment Modes",
    "path": "/mission/modes"
  },
  {
    "title": "Reference Architectures by Edition",
    "path": "/mission/reference-architectures"
  },
  {
    "title": "Identity & Roles",
    "path": "/mission/identity"
  },
  {
    "title": "AI + Driver Stack",
    "path": "/mission/ai-stack"
  }
]

/**
 * Mission & Identity Home
 * Route: /mission
 */
export default function Mission() {
  return (
    <CategoryHomeTemplate
      title="Mission & Identity"
      description="Category home and dashboard for Mission & Identity."
      features={features}
    />
  )
}
