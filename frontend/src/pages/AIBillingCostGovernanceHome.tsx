import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Billing - Category Home Page
 * Route: /billing
 */
export default function Billing() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Billing"
      description="Category home dashboard for Billing"
      features={features.map(f => ({ title: f.label, path: f.route }))}
    />
  )
}
