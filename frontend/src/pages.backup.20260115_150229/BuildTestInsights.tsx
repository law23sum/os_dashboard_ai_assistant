import { FeaturePageTemplate } from '../components/templates/FeaturePageTemplate'

/**
 * Workspaces Dev Build insights - Feature Page
 * Route: /workspaces/dev/build-insights
 */
export default function WorkspacesDevBuildinsights() {
  return (
    <FeaturePageTemplate
      title="Workspaces Dev Build insights"
      description="Feature page for Workspaces Dev Build insights"
      parameters={[
        { name: 'input1', label: 'Input Parameter 1', type: 'text', required: true },
        { name: 'input2', label: 'Input Parameter 2', type: 'number', required: false },
        { name: 'input3', label: 'Input Parameter 3', type: 'select', options: [
          { value: 'option1', label: 'Option 1' },
          { value: 'option2', label: 'Option 2' }
        ]}
      ]}
      configSelector={{
        label: 'Configuration Profile',
        options: [
          { id: 'default', name: 'Default' },
          { id: 'custom', name: 'Custom' },
          { id: 'optimized', name: 'Optimized' }
        ]
      }}
    />
  )
}
