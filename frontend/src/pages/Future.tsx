import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Future - Category Home Page
 * Route: /future
 */
export default function Future() {{
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Future"
      description="Category home dashboard for Future"
      features={features.map((f) => ({{
        title: f.label,
        path: f.route
      }}))}
    />
  )
}}
