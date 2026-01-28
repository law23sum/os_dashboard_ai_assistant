import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Drivers - Category Home Page
 * Route: /drivers
 */
export default function Drivers() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Drivers"
      description="Category home dashboard for Drivers"
      features={features.map(f => ({ title: f.label, path: f.route }))}
    />
  )
}
