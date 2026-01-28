import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Governance - Category Home Page
 * Route: /governance
 */
export default function Governance() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Governance"
      description="Category home dashboard for Governance"
      features={features.map(f => ({ title: f.label, path: f.route }))}
    />
  )
}
