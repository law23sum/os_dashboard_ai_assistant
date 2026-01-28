import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Settings - Category Home Page
 * Route: /settings
 */
export default function Settings() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Settings"
      description="Category home dashboard for Settings"
      features={features.map(f => ({ title: f.label, path: f.route }))}
    />
  )
}
