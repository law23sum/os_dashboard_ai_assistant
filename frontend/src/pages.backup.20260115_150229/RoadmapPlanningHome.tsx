import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Roadmap - Category Home Page
 * Route: /roadmap
 */
export default function Roadmap() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Roadmap"
      description="Category home dashboard for Roadmap"
      features={features.map(f => ({ title: f.label, path: f.route }))}
    />
  )
}
