import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Work - Category Home Page
 * Route: /work
 */
export default function Work() {{
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Work"
      description="Category home dashboard for Work"
      features={features.map((f) => ({{
        title: f.label,
        path: f.route
      }}))}
    />
  )
}}
