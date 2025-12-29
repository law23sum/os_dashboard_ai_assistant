import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Docs - Category Home Page
 * Route: /docs
 */
export default function Docs() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Docs"
      description="Category home dashboard for Docs"
      features={features.map(f => ({ title: f.label, path: f.route }))}
    />
  )
}
