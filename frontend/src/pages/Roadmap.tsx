import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

export default function Roadmap() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features ?? []

  return (
    <CategoryHomeTemplate
      title="Roadmap"
      description="Portfolio planning, strategy alignment, and sequencing."
      features={features.map((feature) => ({
        title: feature.label,
        path: feature.route,
      }))}
    />
  )
}
