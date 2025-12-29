import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Governance Security - Category Home Page
 * Route: /governance/security
 */
export default function GovernanceSecurity() {{
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Governance Security"
      description="Category home dashboard for Governance Security"
      features={features.map((f) => ({{
        title: f.label,
        path: f.route
      }}))}
    />
  )
}}
