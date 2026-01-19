import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Dashboard - Category Home Page
 * Route: /
 */
export default function Dashboard() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Dashboard"
      description="Category home dashboard for Dashboard"
      features={features.map(f => ({ title: f.label, path: f.route }))}
    />
  )
}
