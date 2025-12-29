import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * Chat - Category Home Page
 * Route: /chat
 */
export default function Chat() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="Chat"
      description="Category home dashboard for Chat"
      features={features.map(f => ({ title: f.label, path: f.route }))}
    />
  )
}
