import { CategoryHomeTemplate } from '@/components/templates/CategoryHomeTemplate'

const features = [
  {
    "title": "Security Guardian",
    "path": "/ai/security"
  },
  {
    "title": "Findings & Triage",
    "path": "/workspaces/cyber/findings"
  },
  {
    "title": "Threat Modeling",
    "path": "/workspaces/cyber/threat-modeling"
  },
  {
    "title": "Policy-as-Code Checks",
    "path": "/workspaces/cyber/policy-checks"
  },
  {
    "title": "Vulnerability Scan Integrations",
    "path": "/workspaces/cyber/scanners"
  },
  {
    "title": "Threat Intel Feeds",
    "path": "/workspaces/cyber/intel"
  },
  {
    "title": "Playbooks & Runbooks",
    "path": "/workspaces/cyber/playbooks"
  },
  {
    "title": "Incident Commander",
    "path": "/workspaces/cyber/incidents"
  }
]

/**
 * Cybersecurity Workspace Home
 * Route: /ai
 */
export default function Ai() {
  return (
    <CategoryHomeTemplate
      title="Cybersecurity Workspace"
      description="Category home and dashboard for Cybersecurity Workspace."
      features={features}
    />
  )
}
