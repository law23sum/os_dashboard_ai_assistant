import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Vision - Category Home Page
 * Route: /vision
 */
export default function Vision() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Vision"
      description="Category home dashboard for Vision"
      features={features.map(f => ({ title: f.label, path: f.route }))}
    />
  )
}
