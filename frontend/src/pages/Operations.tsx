import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Operations - Category Home Page
 * Route: /operations
 */
export default function Operations() {{
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Operations"
      description="Category home dashboard for Operations"
      features={features.map((f) => ({{
        title: f.label,
        path: f.route
      }}))}
    />
  )
}}
