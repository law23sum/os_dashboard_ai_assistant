import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Research - Category Home Page
 * Route: /research
 */
export default function Research() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Research"
      description="Category home dashboard for Research"
      features={features.map(f => ({ title: f.label, path: f.route }))}
    />
  )
}
