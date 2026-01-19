import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Integrations - Category Home Page
 * Route: /integrations
 */
export default function Integrations() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Integrations"
      description="Category home dashboard for Integrations"
      features={features.map(f => ({ title: f.label, path: f.route }))}
    />
  )
}
