import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

export default function Work() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features ?? []

  return (
    <CategoryHomeTemplate
      title="Work"
      description="Operational dashboards and work coordination surfaces."
      features={features.map((feature) => ({
        title: feature.label,
        path: feature.route,
      }))}
    />
  )
}
