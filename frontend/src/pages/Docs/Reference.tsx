import { CategoryHomeTemplate } from '../../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../../navigation/iaContext'

export default function DocsReference() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features ?? []

  return (
    <CategoryHomeTemplate
      title="Docs Reference"
      description="Reference artifacts, schemas, and UI building blocks."
      features={features.map((feature) => ({
        title: feature.label,
        path: feature.route,
      }))}
    />
  )
}
