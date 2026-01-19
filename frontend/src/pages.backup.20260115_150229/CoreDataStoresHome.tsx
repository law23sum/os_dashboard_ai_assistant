import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Data - Category Home Page
 * Route: /data
 */
export default function Data() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Data"
      description="Category home dashboard for Data"
      features={features.map(f => ({ title: f.label, path: f.route }))}
    />
  )
}
