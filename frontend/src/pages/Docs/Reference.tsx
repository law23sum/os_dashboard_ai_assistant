import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Docs Reference - Category Home Page
 * Route: /docs/reference
 */
export default function DocsReference() {{
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Docs Reference"
      description="Category home dashboard for Docs Reference"
      features={features.map((f) => ({{
        title: f.label,
        path: f.route
      }}))}
    />
  )
}}
