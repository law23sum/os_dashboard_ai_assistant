import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Workspaces - Category Home Page
 * Route: /workspaces
 */
export default function Workspaces() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Workspaces"
      description="Category home dashboard for Workspaces"
      features={features.map(f => ({ title: f.label, path: f.route }))}
    />
  )
}
