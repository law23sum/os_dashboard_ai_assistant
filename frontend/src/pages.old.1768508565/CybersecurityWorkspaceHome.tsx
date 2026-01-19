import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Ai - Category Home Page
 * Route: /ai
 */
export default function Ai() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Ai"
      description="Category home dashboard for Ai"
      features={features.map(f => ({ title: f.label, path: f.route }))}
    />
  )
}
