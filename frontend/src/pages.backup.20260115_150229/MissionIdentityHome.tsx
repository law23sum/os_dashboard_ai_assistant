import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Mission - Category Home Page
 * Route: /mission
 */
export default function Mission() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Mission"
      description="Category home dashboard for Mission"
      features={features.map(f => ({ title: f.label, path: f.route }))}
    />
  )
}
