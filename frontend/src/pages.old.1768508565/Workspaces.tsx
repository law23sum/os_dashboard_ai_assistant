import { CategoryHomeTemplate } from '@/components/templates/CategoryHomeTemplate'

const features = [
  {
    "title": "Dev Workspace",
    "path": "/workspaces/dev"
  },
  {
    "title": "Developer Tools",
    "path": "/work/tools"
  },
  {
    "title": "Repo & Branch Browser",
    "path": "/workspaces/dev/repos"
  },
  {
    "title": "CI/CD Integration",
    "path": "/workspaces/dev/cicd"
  },
  {
    "title": "Build/Test Insights",
    "path": "/workspaces/dev/build-insights"
  },
  {
    "title": "Commit → Task Generator",
    "path": "/workspaces/dev/commit-tasks"
  },
  {
    "title": "Code Review Queue",
    "path": "/workspaces/dev/reviews"
  },
  {
    "title": "Code Merge Advisor",
    "path": "/workspaces/dev/merge-advisor"
  }
]

/**
 * Dev & DevOps Workspace Home
 * Route: /workspaces
 */
export default function Workspaces() {
  return (
    <CategoryHomeTemplate
      title="Dev & DevOps Workspace"
      description="Category home and dashboard for Dev & DevOps Workspace."
      features={features}
    />
  )
}
