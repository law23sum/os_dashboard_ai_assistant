import { CategoryHomeTemplate } from '@/components/templates/CategoryHomeTemplate'

const features = [
  {
    "title": "Policy Engine",
    "path": "/governance/policy"
  },
  {
    "title": "Policy Library & Templates",
    "path": "/governance/policy/library"
  },
  {
    "title": "Policy DSL",
    "path": "/governance/policy/dsl"
  },
  {
    "title": "Safety Harnesses",
    "path": "/governance/policy/safety"
  },
  {
    "title": "Policy Simulator",
    "path": "/governance/policy/simulator"
  },
  {
    "title": "Policy Versioning & Approvals",
    "path": "/governance/policy/versioning"
  },
  {
    "title": "Enforcement Points Map",
    "path": "/governance/policy/enforcement"
  },
  {
    "title": "Exceptions & Waivers",
    "path": "/governance/policy/exceptions"
  }
]

/**
 * Policy & Governance Engine Home
 * Route: /governance
 */
export default function Governance() {
  return (
    <CategoryHomeTemplate
      title="Policy & Governance Engine"
      description="Category home and dashboard for Policy & Governance Engine."
      features={features}
    />
  )
}
