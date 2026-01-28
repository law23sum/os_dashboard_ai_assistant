import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Observability - Category Home Page
 * Route: /observability
 */
export default function Observability() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Observability"
      description="Category home dashboard for Observability"
      features={features.map(f => ({ title: f.label, path: f.route }))}
    />
  )
}
